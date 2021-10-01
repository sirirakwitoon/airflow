from airflow.providers.amazon.aws.hooks.s3 import S3Hook
import logging
import csv
from airflow import DAG 
from airflow.utils import timezone
from airflow.operators.dummy import DummyOperator
from airflow.operators.python import PythonOperator

from airflow.providers.http.sensors.http import HttpSensor
import requests 

DAG_FOLDER = "/opt/airflow/dags"




def _upload_to_data_lake(ds,ti):
    my_name = ti.xcom_pull(task_ids="get_data", key="name")
    logging.info(my_name)
    filename = ti.xcom_pull(task_ids="get_data",key="return_value")

    hook = S3Hook(aws_conn_id="s3_conn")
    hook.load_file(
        filename=filename,
        key=f"covid/{ds}/{ds}-covid-cases.csv",
        bucket_name="landing",
        replace=True,
    )

def _get_data(ds, ti) -> str:
    url = "https://covid19.ddc.moph.go.th/api/Cases/timeline-cases-all"
    response = requests.get(url)
    data = response.json()
    latest_record = ""
    for each in data:
        if each["txn_date"] == ds:
            latest_record = each
            break

    
    logging.info(latest_record)

    filename = f"{DAG_FOLDER}/{ds}-covid-cases.csv"
    with open(filename, "w") as csvfile:
        fieldnames = [
            "txn_date", 
            "new_case",
            "total_case",
            "new_case_excludeabroad",
            "total_case_excludeabroad",
            "new_death",
            "total_death",
            "new_recovered",
            "total_recovered",
            "update_date",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # writer.writeheader()
        writer.writerow(latest_record)

    ti.xcom_push(key="name", value="Nutsrk")
    return filename


default_args = {
    "owner": "Nutsrk",
    "start_date": timezone.datetime(2021, 9, 27)
}
with DAG(
    "covid_case_api_processing",
    schedule_interval="@daily",
    default_args=default_args,
    catchup=False,
    tags=["saksiam"],
    max_active_runs=3,
) as dag:


    start = DummyOperator(task_id="start")
    end = DummyOperator(task_id="end")


    get_data = PythonOperator(
        task_id="get_data",
        python_callable=_get_data,
    )

    upload_to_data_lake = PythonOperator(
        task_id="upload_to_data_lake",
        python_callable=_upload_to_data_lake,
    )
    
    check_api = HttpSensor(
        task_id="check_api",
        http_conn_id="",
        endpoint="https://covid19.ddc.moph.go.th/api/Cases/timeline-cases-all",
        poke_interval=5,
        timeout=100,
    )


    start >> check_api >> get_data >> upload_to_data_lake >> end
