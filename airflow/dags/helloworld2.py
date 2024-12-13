from airflow import models
from airflow.providers.google.cloud.operators.pubsub import PubSubPullOperator
from airflow.providers.google.cloud.sensors.gcs import GCSObjectExistenceSensor
from airflow.utils.dates import days_ago
from airflow.operators.dummy_operator import DummyOperator

# Define your project, bucket, and Pub/Sub topic information
PROJECT_ID = 'machledata-mlops'
BUCKET_NAME = 'mlops-airflow-42'
PUBSUB_TOPIC = 'dvc'

def pubsub_message_callback(message, **kwargs):
    """
    Callback function to handle incoming Pub/Sub messages
    """
    print(f"Received message: {message}")
    # Assuming the message contains the 'file_name' field
    file_name = message.get("file_name", "")
    # Push the file_name to XCom so it can be used by the next task
    kwargs['ti'].xcom_push(key='file_name', value=file_name)

with models.DAG(
    "gcs_update_trigger_dag",
    schedule_interval=None,  # This DAG will not run on a schedule, it's event-driven
    start_date=days_ago(1),
    catchup=False,
) as dag:

    # 1. Task to wait for a Pub/Sub message (this would be triggered by GCS event notification)
    pull_pubsub = PubSubPullOperator(
        task_id="pull_pubsub_message",
        project_id=PROJECT_ID,
        subscription="projects/{}/subscriptions/gcs-update-subscription".format(PROJECT_ID),
        ack_messages=True,
        max_messages=1,
        callback=pubsub_message_callback,
    )

    # 2. Sensor to check if the object exists in GCS (based on the Pub/Sub message)
    gcs_sensor = GCSObjectExistenceSensor(
        task_id="check_gcs_object_exists",
        bucket_name=BUCKET_NAME,
        object_name="{{ task_instance.xcom_pull(task_ids='pull_pubsub_message')['file_name'] }}",  # Retrieve the filename from Pub/Sub
        poke_interval=30,  # check every 30 seconds
        timeout=600,  # stop after 10 minutes
    )

    start_task = DummyOperator(task_id="start_task")

    # Set the task dependencies
    start_task >> pull_pubsub >> gcs_sensor
