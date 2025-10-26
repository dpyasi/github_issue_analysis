"""
Simplified Airflow Operators for GitHub Issues ETL Pipeline
Only necessary operators - no duplication of ETL script functionality
Author: d.pyasi42@gmail.com
"""

from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
from airflow.exceptions import AirflowException
import logging

class DataQualityCheckOperator(BaseOperator):
    """
    Custom operator for data quality checks
    Validates data after ETL completion
    """
    
    @apply_defaults
    def __init__(
        self,
        table_name: str,
        min_records: int = 100,
        max_null_percentage: float = 0.05,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.table_name = table_name
        self.min_records = min_records
        self.max_null_percentage = max_null_percentage
    
    def execute(self, context):
        """
        Execute data quality checks
        """
        try:
            from pyspark.sql import SparkSession
            from pyspark.sql import functions as F
            
            # Initialize Spark
            spark = SparkSession.builder \
                .appName("DataQualityCheck") \
                .getOrCreate()
            
            try:
                # Load data
                df = spark.table(self.table_name)
                
                # Check record count
                record_count = df.count()
                logging.info(f"Total records in {self.table_name}: {record_count}")
                
                if record_count < self.min_records:
                    raise AirflowException(f"Data quality check failed: Only {record_count} records found, minimum required: {self.min_records}")
                
                # Check null percentages for key fields
                null_checks = {}
                key_fields = ["id", "title", "state", "created_at"]
                
                for field in key_fields:
                    null_count = df.filter(F.col(field).isNull()).count()
                    null_percentage = (null_count / record_count) * 100
                    null_checks[field] = null_percentage
                    
                    if null_percentage > (self.max_null_percentage * 100):
                        raise AirflowException(f"Data quality check failed: {field} has {null_percentage:.2f}% null values, maximum allowed: {self.max_null_percentage * 100}%")
                
                # Check data freshness (created_at should be recent)
                latest_created = df.agg(F.max("created_at")).collect()[0][0]
                logging.info(f"Latest issue created at: {latest_created}")
                
                # Quality check results
                quality_results = {
                    "record_count": record_count,
                    "null_checks": null_checks,
                    "latest_created": str(latest_created),
                    "status": "passed"
                }
                
                logging.info(f"Data quality check passed for {self.table_name}")
                return quality_results
                
            finally:
                spark.stop()
                
        except Exception as e:
            logging.error(f"Error in DataQualityCheckOperator: {e}")
            raise AirflowException(f"Data quality check failed: {e}")

class DailySummaryOperator(BaseOperator):
    """
    Custom operator for creating daily summary statistics
    Generates business intelligence summaries after ETL
    """
    
    @apply_defaults
    def __init__(
        self,
        table_name: str,
        summary_table_name: str = None,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.table_name = table_name
        self.summary_table_name = summary_table_name or f"{table_name}_daily_summary"
    
    def execute(self, context):
        """
        Execute daily summary creation
        """
        try:
            from pyspark.sql import SparkSession
            from pyspark.sql import functions as F
            from datetime import datetime
            
            # Initialize Spark
            spark = SparkSession.builder \
                .appName("DailySummary") \
                .getOrCreate()
            
            try:
                # Load data
                df = spark.table(self.table_name)
                
                # Calculate summary statistics
                summary = df.groupBy(F.current_date().alias("summary_date")).agg(
                    F.count("*").alias("total_issues"),
                    F.sum(F.when(F.col("state") == "open", 1).otherwise(0)).alias("open_issues"),
                    F.sum(F.when(F.col("state") == "closed", 1).otherwise(0)).alias("closed_issues"),
                    F.sum(F.when(F.col("pull_request").isNotNull(), 1).otherwise(0)).alias("total_pull_requests"),
                    F.sum(F.when(F.col("pull_request").isNotNull() & (F.col("state") == "open"), 1).otherwise(0)).alias("open_pull_requests"),
                    F.avg("comments").alias("avg_comments"),
                    F.sum(F.when(F.col("created_at") >= F.date_sub(F.current_date(), 7), 1).otherwise(0)).alias("issues_last_7_days"),
                    F.sum(F.when(F.col("created_at") >= F.date_sub(F.current_date(), 30), 1).otherwise(0)).alias("issues_last_30_days")
                )
                
                # Add metadata
                summary = summary.withColumn("created_at", F.current_timestamp())
                
                # Write summary to table
                summary.write.mode("append").saveAsTable(self.summary_table_name)
                
                # Get summary results
                summary_results = summary.collect()[0]
                
                logging.info(f"Daily summary created successfully:")
                logging.info(f"  Total Issues: {summary_results['total_issues']}")
                logging.info(f"  Open Issues: {summary_results['open_issues']}")
                logging.info(f"  Closed Issues: {summary_results['closed_issues']}")
                logging.info(f"  Pull Requests: {summary_results['total_pull_requests']}")
                logging.info(f"  Avg Comments: {summary_results['avg_comments']:.2f}")
                
                return {
                    "status": "success",
                    "summary_date": str(summary_results['summary_date']),
                    "total_issues": summary_results['total_issues'],
                    "open_issues": summary_results['open_issues'],
                    "closed_issues": summary_results['closed_issues'],
                    "pull_requests": summary_results['total_pull_requests'],
                    "avg_comments": summary_results['avg_comments']
                }
                
            finally:
                spark.stop()
                
        except Exception as e:
            logging.error(f"Error in DailySummaryOperator: {e}")
            raise AirflowException(f"Daily summary creation failed: {e}")
