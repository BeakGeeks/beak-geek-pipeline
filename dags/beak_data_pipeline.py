#This is the master DAG file that orchestrates the entire data pipeline. 
# It is responsible for creating the tasks and defining the dependencies between them.

from os import path
from datetime import timedelta  
import airflow  
from airflow import DAG  
from airflow.providers.amazon.aws.operators.emr import EmrServerlessCreateApplicationOperator
from airflow.providers.amazon.aws.operators.emr import EmrServerlessDeleteApplicationOperator
from airflow.providers.amazon.aws.operators.emr import EmrServerlessStartJobOperator
from airflow.providers.amazon.aws.sensors.emr import EmrServerlessJobSensor
from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor
from airflow.providers.amazon.aws.sensors.emr import EmrStepSensor
from airflow.providers.amazon.aws.operators.glue import GlueJobOperator
from airflow.providers.amazon.aws.operators.glue_crawler import GlueCrawlerOperator
from airflow.providers.amazon.aws.transfers.s3_to_redshift import S3ToRedshiftOperator

S3_BUCKET_NAME = "airflow-d16a0290-dcbd-11ef-9afa-06d9d5d85d85-bucket"

GLUE_ROLE_ARN = "arn:aws:iam::751982554700:role/AWSGlueServiceRoleDefault"

EXEC_ROLE_ARN = "arn:aws:iam::751982554700:role/service-role/MwaaExecutionRole"

dag_name = 'beak_data_pipeline'
# Unique identifier for the DAG
correlation_id = "{{ run_id }}"
  
default_args = {  
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': airflow.utils.dates.days_ago(1),
    'retries': 0,
    'retry_delay': timedelta(minutes=2),
    'provide_context': True,
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False
}

dag = DAG(  
    dag_name,
    default_args=default_args,
    dagrun_timeout=timedelta(hours=2),
    schedule='0 3 * * *'
)

s3_sensor = S3KeySensor(  
  task_id='s3_sensor',  
  bucket_name=S3_BUCKET_NAME,  
  bucket_key='data/raw/green*', 
  wildcard_match=True, 
  dag=dag  
)

glue_crawler_config = {
        "Name": "airflow-workshop-raw-green-crawler",
        "Role": GLUE_ROLE_ARN,
        "DatabaseName": "default",
        "Targets": {"S3Targets": [{"Path": f"{S3_BUCKET_NAME}/data/raw/green"}]},
    }
    
glue_crawler = GlueCrawlerOperator(
    task_id="glue_crawler",
    config=glue_crawler_config,
    dag=dag
)
