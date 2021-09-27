from airflow import DAG 
from airflow.utils import timezone
from airflow.operators.dummy import DummyOperator

default_args = {
    "owner": "Nutsrk",
    "start_date": timezone.datetime(2021, 9, 27)
}

with DAG(
    "my_homework",
    schedule_interval="*/10 * * * *",
    default_args=default_args,
    catchup=False,
    tags=["saksiam"],
) as dag:

    t1 = DummyOperator(task_id="1")
    t2 = DummyOperator(task_id="2")
    t3 = DummyOperator(task_id="3")
    t4 = DummyOperator(task_id="4")
    t5 = DummyOperator(task_id="5")
    t6 = DummyOperator(task_id="6")
    t7 = DummyOperator(task_id="7")
    t8 = DummyOperator(task_id="8")
    t9 = DummyOperator(task_id="9")
    
    # t1 >> [t2, t5]
    # t2 >> [t3, t6]
    # t3 >> t4 >> t9
    # t5 >> [t6, t7] >> t8 >> t9


    t1 >> [t2  >> [t3 >> t4 >> t9, t6], t5 >> [t6, t7] >> t8 >> t9]


