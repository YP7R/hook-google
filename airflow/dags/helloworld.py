from airflow import DAG
from airflow.providers.google.cloud.operators.pubsub import PubSubPullOperator
from airflow.providers.google.cloud.hooks.gcs import GCSHook
from airflow.operators.python import PythonOperator
from datetime import datetime
import os


# Define default arguments
default_args = {
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
}

SERVICE_ACCOUNT_JSON = "./dags/machledata-mlops-6636519d25a7.json"

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = SERVICE_ACCOUNT_JSON

def process_file(file_data):
    """Example function to process GCS file data."""
    print(f"Processing file: {file_data['name']}")
    # Additional logic for handling the file can be added here.


with DAG(
        dag_id='gcs_update_trigger',
        default_args=default_args,
        schedule_interval=None,  # Triggered by Pub/Sub
        catchup=False,
) as dag:
    # Task 1: Pull messages from Pub/Sub
    pull_messages = PubSubPullOperator(
        task_id='pull_messages',
        project_id="machledata-mlops",
        subscription="dvc",
        max_messages=5,
    )


    # Task 2: Process each file from the GCS bucket
    def extract_file_names(**context):
        messages = context['ti'].xcom_pull(task_ids='pull_messages')
        if not messages:
            print("No messages received.")
            return []
        return [msg['message']['data'] for msg in messages]


    process_files = PythonOperator(
        task_id='process_files',
        python_callable=process_file,
        provide_context=True,
    )

    pull_messages >> process_files
