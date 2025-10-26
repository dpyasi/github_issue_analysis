"""
Simplified GitHub Issues ETL Pipeline - Airflow DAG
Uses existing ETL script instead of duplicating functionality
Author: d.pyasi42@gmail.com
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator
from airflow.operators.email import EmailOperator
from airflow.models import Variable
from airflow.utils.dates import days_ago
from airflow.utils.trigger_rule import TriggerRule
import logging

# Import only necessary custom operators
import sys
import os
sys.path.append('/opt/airflow/dags/airflow/operators')
from operators import DataQualityCheckOperator, DailySummaryOperator

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
    'simplified_github_issues_etl',
    default_args=default_args,
    description='Simplified daily ETL pipeline for GitHub issues data',
    schedule_interval='0 6 * * *',  # Daily at 6:00 AM UTC
    max_active_runs=1,
    tags=['github', 'etl', 'issues', 'analytics', 'simplified'],
    doc_md="""
    # Simplified GitHub Issues ETL Pipeline
    
    This DAG runs a daily ETL pipeline for GitHub issues data using the existing ETL script:
    
    ## Tasks:
    1. **Start Pipeline** - Initialize the ETL process
    2. **Run ETL Script** - Execute the complete ETL pipeline
    3. **Data Quality Check** - Validate data quality
    4. **Create Summary** - Generate daily summary statistics
    5. **Send Notifications** - Notify on success/failure
    
    ## Key Features:
    - Uses existing ETL script (no code duplication)
    - Simple orchestration with Airflow
    - Data quality validation
    - Daily summary generation
    - Email notifications
    
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

# Run the complete ETL pipeline using existing script
def run_etl_pipeline():
    """
    Run the complete ETL pipeline using the existing ETL script
    """
    import subprocess
    import sys
    import os
    
    # Get GitHub token from Airflow Variables or environment
    github_token = Variable.get("GITHUB_TOKEN", default_var=None)
    
    # Set environment variable for the ETL script
    if github_token:
        os.environ['GITHUB_TOKEN'] = github_token
        logging.info("GitHub token set from Airflow Variables")
    else:
        logging.warning("No GITHUB_TOKEN found in Airflow Variables - using unauthenticated requests")
    
    # Get the ETL script path
    etl_script_path = os.path.join(os.path.dirname(__file__), '..', '..', 'etl', 'github_issues_etl_databricks.py')
    
    try:
        # Run the ETL script
        result = subprocess.run([
            sys.executable, 
            etl_script_path
        ], capture_output=True, text=True, cwd=os.path.dirname(etl_script_path))
        
        if result.returncode != 0:
            raise Exception(f"ETL script failed with return code {result.returncode}: {result.stderr}")
        
        logging.info(f"ETL pipeline completed successfully: {result.stdout}")
        return {"status": "success", "output": result.stdout}
        
    except Exception as e:
        logging.error(f"Error running ETL pipeline: {e}")
        raise

etl_task = PythonOperator(
    task_id='run_etl_pipeline',
    python_callable=run_etl_pipeline,
    dag=dag,
)

# Data quality check
data_quality_task = DataQualityCheckOperator(
    task_id='check_data_quality',
    table_name="loungebip_test.internal.huggingface_transformers_issues",
    min_records=100,
    max_null_percentage=0.05,
    dag=dag,
)

# Daily summary
create_summary_task = DailySummaryOperator(
    task_id='create_daily_summary',
    table_name="loungebip_test.internal.huggingface_transformers_issues",
    summary_table_name="loungebip_test.internal.huggingface_transformers_issues_daily_summary",
    dag=dag,
)

# Success notification
success_notification = EmailOperator(
    task_id='send_success_notification',
    to=['d.pyasi42@gmail.com'],
    subject='GitHub Issues ETL - SUCCESS',
    html_content="""
    <h2>GitHub Issues ETL Pipeline - SUCCESS</h2>
    <p>The ETL pipeline completed successfully.</p>
    <p><strong>Execution Date:</strong> {{ ds }}</p>
    <p><strong>Status:</strong> All tasks completed successfully</p>
    <p><strong>Logs:</strong> {{ task_instance.log_url }}</p>
    """,
    trigger_rule=TriggerRule.ALL_SUCCESS,
    dag=dag,
)

# Failure notification
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

# End task
end_task = DummyOperator(
    task_id='end_etl_pipeline',
    trigger_rule=TriggerRule.NONE_FAILED,
    dag=dag,
)

# Task dependencies - Simplified flow
start_task >> etl_task >> data_quality_task >> create_summary_task >> success_notification >> end_task

# Failure notifications
etl_task >> failure_notification
data_quality_task >> failure_notification
create_summary_task >> failure_notification
