from airflow.operators import PythonOperator
from airflow.models import DAG
from datetime import datetime, timedelta

import time
from pprint import pprint

one_day_ago = datetime.combine(
        datetime.today() - timedelta(days=1), datetime.min.time())

args = {
    'owner': 'airflow',
    'start_date': one_day_ago
}

dag = DAG(
    dag_id='dynamic_dags', default_args=args,
    schedule_interval=None)


def my_sleeping_function(random_base):
    'This is a function that will run within the DAG execution'
    time.sleep(random_base)


def setup_jobs_fn(ds, **kwargs):
    pprint(kwargs)
    print(ds)
    time.sleep(2)
    return 'Whatever you return gets printed in the logs'


setup_jobs = PythonOperator(
    task_id='setup_jobs',
    provide_context=True,
    python_callable=setup_jobs_fn,
    dag=dag)


def collect_results_fn(ds, **kwargs):
    pprint(kwargs)
    print(ds)


collect_results = PythonOperator(
    task_id='collect_results',
    provide_context=True,
    python_callable=collect_results_fn,
    dag=dag)


for i in range(10):
    '''
    Generating 10 sleeping task, sleeping from 0 to 9 seconds
    respectively
    '''
    task = PythonOperator(
        task_id='sleep_for_'+str(i),
        python_callable=my_sleeping_function,
        op_kwargs={'random_base': float(i)/10},
        dag=dag)
    task.set_upstream(setup_jobs)
    task.set_downstream(collect_results)
