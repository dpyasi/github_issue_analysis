"""
GitHub Issues ETL Pipeline - Airflow DAG
Daily ETL pipeline for GitHub issues data with monitoring and alerting
Author: d.pyasi42@gmail.com
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.operators.dummy import DummyOperator
from airflow.operators.email import EmailOperator
from airflow.models import Variable
from airflow.utils.dates import days_ago
from airflow.utils.trigger_rule import TriggerRule
import logging

# Import custom operators
import sys
import os
sys.path.append('/opt/airflow/dags/airflow/operators')
from github_issues_operator import GitHubIssuesOperator, DataQualityCheckOperator, SparkETLOperator

# Default arguments
default_args = {
    'owner': 'dpyasi',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email': ['d.pyasi42@gmail.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'catchup': False,
    'max_active_runs': 1,
}

# DAG definition
dag = DAG(
    'github_issues_etl',
    default_args=default_args,
    description='Daily ETL pipeline for GitHub issues data',
    schedule_interval='0 6 * * *',  # Daily at 6:00 AM UTC
    max_active_runs=1,
    tags=['github', 'etl', 'issues', 'analytics'],
    doc_md="""
    # GitHub Issues ETL Pipeline
    
    This DAG runs a daily ETL pipeline for GitHub issues data:
    
    ## Tasks:
    1. **Start Pipeline** - Initialize the ETL process
    2. **Fetch GitHub Issues** - Retrieve issues from GitHub API
    3. **Process Data** - Clean and transform the data
    4. **Load to Database** - Store data in the target table
    5. **Data Quality Check** - Validate data quality
    6. **Create Summary** - Generate daily summary statistics
    7. **Send Notifications** - Notify on success/failure
    
    ## Configuration:
    - Repository: `huggingface/transformers`
    - Schedule: Daily at 6:00 AM UTC
    - Retries: 3 with 5-minute delay
    - Email notifications on failure
    """,
)

# Task definitions
start_task = DummyOperator(
    task_id='start_etl_pipeline',
    dag=dag,
)

fetch_issues_task = GitHubIssuesOperator(
    task_id='fetch_github_issues',
    repo_owner=Variable.get("github_repo_owner", default_var="huggingface"),
    repo_name=Variable.get("github_repo_name", default_var="transformers"),
    state="all",
    per_page=100,
    max_pages=Variable.get("github_max_pages", default_var=None, deserialize_json=True),
    dag=dag,
)

load_data_task = SparkETLOperator(
    task_id='load_data_to_table',
    table_name="loungebip_test.internal.huggingface_transformers_issues",
    issues_data="{{ ti.xcom_pull(task_ids='fetch_github_issues')['issues'] }}",
    dag=dag,
)

data_quality_task = DataQualityCheckOperator(
    task_id='check_data_quality',
    table_name="loungebip_test.internal.huggingface_transformers_issues",
    min_records=100,
    max_null_percentage=0.05,
    dag=dag,
)

create_summary_task = PythonOperator(
    task_id='create_daily_summary',
    python_callable=lambda **context: create_daily_summary(context),
    provide_context=True,
    dag=dag,
)

def create_daily_summary(context):
    """
    Create daily summary statistics
    """
    try:
        from pyspark.sql import SparkSession
        from pyspark.sql import functions as F
        
        # Initialize Spark
        spark = SparkSession.builder \
            .appName("DailySummary") \
            .getOrCreate()
        
        try:
            # Load data
            df = spark.table("loungebip_test.internal.huggingface_transformers_issues")
            
            # Calculate summary statistics
            summary = df.groupBy(F.current_date().alias("summary_date")).agg(
                F.count("*").alias("total_issues"),
                F.sum(F.when(F.col("state") == "open", 1).otherwise(0)).alias("open_issues"),
                F.sum(F.when(F.col("state") == "closed", 1).otherwise(0)).alias("closed_issues"),
                F.sum(F.when(F.col("pull_request").isNotNull(), 1).otherwise(0)).alias("total_pull_requests"),
                F.sum(F.when(F.col("pull_request").isNotNull() & (F.col("state") == "open"), 1).otherwise(0)).alias("open_pull_requests"),
                F.sum(F.when(F.col("pull_request").isNotNull() & (F.col("state") == "closed"), 1).otherwise(0)).alias("closed_pull_requests")
            ).withColumn("new_issues_today", F.col("total_issues")) \
             .withColumn("closed_issues_today", F.lit(0)) \
             .withColumn("top_contributors", F.array()) \
             .withColumn("top_labels", F.array()) \
             .withColumn("etl_timestamp", F.current_timestamp()) \
             .withColumn("etl_batch_id", F.lit(f"airflow_{context['ds']}"))
            
            # Write to summary table
            summary.write.mode("append").saveAsTable("loungebip_test.internal.github_issues_daily_summary")
            
            logging.info("Daily summary created successfully")
            return "Daily summary created successfully"
            
        finally:
            spark.stop()
            
    except Exception as e:
        logging.error(f"Error creating daily summary: {e}")
        raise

success_notification = EmailOperator(
    task_id='send_success_notification',
    to=['d.pyasi42@gmail.com'],
    subject='GitHub Issues ETL - SUCCESS',
    html_content="""
    <h2>GitHub Issues ETL Pipeline - SUCCESS</h2>
    <p>The ETL pipeline completed successfully.</p>
    <p><strong>Execution Date:</strong> {{ ds }}</p>
    <p><strong>Start Time:</strong> {{ ts }}</p>
    <p><strong>Duration:</strong> {{ (ts - task_instance.start_date).total_seconds() }} seconds</p>
    """,
    trigger_rule=TriggerRule.ALL_SUCCESS,
    dag=dag,
)

failure_notification = EmailOperator(
    task_id='send_failure_notification',
    to=['d.pyasi42@gmail.com'],
    subject='GitHub Issues ETL - FAILURE',
    html_content="""
    <h2>GitHub Issues ETL Pipeline - FAILURE</h2>
    <p>The ETL pipeline failed. Please check the logs for details.</p>
    <p><strong>Execution Date:</strong> {{ ds }}</p>
    <p><strong>Failed Task:</strong> {{ task_instance.task_id }}</p>
    <p><strong>Error:</strong> {{ task_instance.log_url }}</p>
    """,
    trigger_rule=TriggerRule.ONE_FAILED,
    dag=dag,
)

end_task = DummyOperator(
    task_id='end_etl_pipeline',
    trigger_rule=TriggerRule.NONE_FAILED,
    dag=dag,
)

# Task dependencies
start_task >> fetch_issues_task >> load_data_task >> data_quality_task >> create_summary_task >> success_notification >> end_task

# Failure notifications
fetch_issues_task >> failure_notification
load_data_task >> failure_notification
data_quality_task >> failure_notification
create_summary_task >> failure_notification
