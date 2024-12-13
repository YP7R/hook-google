
**Configure git**  

```shell
git init
```

**Install dvc and init it**  

```shell
pip install dvc[gs]
dvc init
```

**Configure the remote address, in order to get this step correctly done instantiate a bucket**  

```shell
$env:GCP_BUCKET="mlops-airflow-42"
$env:GCP_LOCATION="europe-west6"
gcloud storage buckets create gs://$env:GCP_BUCKET --location=$env:GCP_LOCATION --uniform-bucket-level-access --public-access-prevention
dvc remote add -d data gs://$($env:GCP_BUCKET)/dvcstore -f
dvc remote list # list dvc remote
```

**Add the data to be tracked, and push it**  
```shell
dvc add .\data\raw\ 
dvc push
```

**Generate the pub/sub - enable notifications**  
```shell
gcloud projects list # to get the project id
$env:GCP_PROJECT_ID="machledata-mlops"
$env:TOPIC="dvc"
gcloud storage buckets notifications create gs://$env:GCP_BUCKET --topic=projects/$($env:GCP_PROJECT_ID)/topics/$($env:TOPIC) --event-types=OBJECT_FINALIZE --payload-format=json
# topic: https://www.googleapis.com/storage/v1/b/mlops-airflow-42/notificationConfigs/1

gcloud storage buckets notifications list gs://$($env:GCP_BUCKET)

```

**Manually create the "abonnement" using the Google Cloud Platform UI ***or*** use the Google cloud CLI**  
```shell
$env:GCP_SUBSCRIPTION="dvc"
gcloud pubsub subscriptions create $env:GCP_SUBSCRIPTION --topic=projects/$($env:GCP_PROJECT_ID)/topics/$($env:TOPIC)

gcloud pubsub subscriptions list
gcloud pubsub topics list
```

**Test the notification**  
```shell
gsutil cp test-file.txt gs://$env:GCP_BUCKET
gcloud pubsub subscriptions pull $env:GCP_SUBCRIPTION --auto-ack
```



**Configure the connection id under admin section**  


## Airflow python
```shell
pip install apache-airflow
pip install apache-airflow-providers-google
```






# BELOW IS NOT IMPORTANT






# **dvc**

```shell
# DVC
pip install dvc[gs]
```
```shell
# Configuration of dvc
dvc init
```


## bucket creation

```shell
# Export the bucket name
export GCP_BUCKET_NAME=<my_bucket_name>
$env:GCP_BUCKET_NAME="mlops-airflow-bckt"
```

```shell
# Export the bucket location
export GCP_BUCKET_LOCATION=<my_bucket_location>
$env:GCP_BUCKET_LOCATION="europe-west6"
```

```shell
gcloud storage buckets create gs://$env:GCP_BUCKET_NAME --location=$env:GCP_BUCKET_LOCATION --uniform-bucket-level-access --public-access-prevention
```

## DVC Configuration
```shell
git init
dvc init # Create the .dvc folder
dvc add .\data\raw # Add new data
dvc push # Push
dvc pull # Pull
```

```shell
dvc remote add -d data gs://$GCP_BUCKET_NAME/dvcstore
dvc remote add -d data gs://$env:GCP_BUCKET_NAME/dvcstore
```

## Airflow Configuration

https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html

```shell
mkdir -p ./dags ./logs ./plugins ./config
echo -e "AIRFLOW_UID=$(id -u)" > .env
```

```shell
docker compose up airflow-init
docker compose up # http://localhost:8080/ #username:airflow  pwd: airflow
```

## Pub/Sub
https://cloud.google.com/storage/docs/reporting-changes?hl=fr


```shell
gcloud storage buckets notifications create gs://YOUR_BUCKET_NAME \
    --topic=projects/YOUR_PROJECT_ID/topics/YOUR_TOPIC_NAME \
    --event-types=OBJECT_FINALIZE \
    --payload-format=json

$env:TOPIC_NAME="projects/$env:PROJECT_iD/"

gcloud storage buckets notifications create gs://$env:GCP_BUCKET_NAME --topic=projects/machledata-mlops/topics/bckt --event-types=OBJECT_FINALIZE --payload-format=json
# https://www.googleapis.com/storage/v1/b/mlops-airflow-bckt/notificationConfigs/1

gcloud storage buckets notifications list gs://mlops-airflow-bckt
```