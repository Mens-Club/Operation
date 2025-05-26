from airflow import DAG
from airflow.operators.python import PythonOperator
from module.validating_model import run_evaluation
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

with DAG('evaluate_model_daily',
         default_args=default_args,
         schedule_interval='0 2 * * 1', # 일주일에 한 번 
         catchup=False) as dag:
    
    evaluate_model_task = PythonOperator(
        task_id='evaluate_recommend_model',
        python_callable=run_evaluation
    )