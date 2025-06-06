from airflow import DAG
from airflow.operators.python import PythonOperator
from module.database_fill_chain import main
from datetime import datetime, timedelta

default_args = {
    'owner': 'airscholar',
    'depends_on_past': False,
    'start_date': datetime(2024, 4, 10),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

with DAG('recommend_data_pipeline',
         default_args=default_args,
         schedule_interval=timedelta(days=3), # 3일에 한번 null 데이터 채우기 
         catchup=False) as dag:

    fill_data_process = PythonOperator(
        task_id='recommend_fill_data',
        python_callable=main,
    )
