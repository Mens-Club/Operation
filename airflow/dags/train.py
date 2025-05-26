from airflow import DAG
from airflow.operators.python import PythonOperator
from module.train_piepeline import runpod_run
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

with DAG('model_train_pipelines',
         default_args=default_args,
         schedule_interval='0 9 * * 1/2', # 2주에 한 번 격주 한 번이라는 개념
         catchup=False) as dag:
    
        fill_data_process = PythonOperator(
        task_id='runpod_model_train',
        python_callable=runpod_run,
    )

