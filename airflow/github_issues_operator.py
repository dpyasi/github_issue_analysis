"""
Custom Airflow Operators for GitHub Issues ETL
Author: d.pyasi42@gmail.com
"""

from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
from airflow.hooks.base import BaseHook
from airflow.exceptions import AirflowException
import logging
import requests
import json
from typing import Dict, List, Any, Optional

class GitHubIssuesOperator(BaseOperator):
    """
    Custom operator for fetching GitHub issues
    """
    
    @apply_defaults
    def __init__(
        self,
        repo_owner: str,
        repo_name: str,
        state: str = "all",
        per_page: int = 100,
        max_pages: Optional[int] = None,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.state = state
        self.per_page = per_page
        self.max_pages = max_pages
    
    def execute(self, context):
        """
        Execute the GitHub issues fetch operation
        """
        try:
            logging.info(f"Fetching GitHub issues for {self.repo_owner}/{self.repo_name}")
            
            # Initialize session
            session = requests.Session()
            session.headers.update({
                'Accept': 'application/vnd.github.v3+json',
                'User-Agent': 'GitHub-Issues-ETL/1.0'
            })
            
            # Fetch issues
            all_issues = []
            page = 1
            api_calls = 0
            
            while True:
                try:
                    params = {
                        "state": self.state,
                        "per_page": min(self.per_page, 100),
                        "page": page,
                        "sort": "updated",
                        "direction": "desc"
                    }
                    
                    url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/issues"
                    response = session.get(url, params=params, timeout=30)
                    response.raise_for_status()
                    api_calls += 1
                    
                    issues = response.json()
                    if not issues:
                        break
                    
                    all_issues.extend(issues)
                    logging.info(f"Fetched {len(issues)} issues from page {page}")
                    
                    if self.max_pages and page >= self.max_pages:
                        break
                    
                    page += 1
                    
                    # Rate limiting
                    import time
                    time.sleep(0.1)
                    
                except requests.exceptions.RequestException as e:
                    logging.error(f"Error fetching page {page}: {e}")
                    break
            
            logging.info(f"Total issues fetched: {len(all_issues)}")
            logging.info(f"Total API calls made: {api_calls}")
            
            # Store results in XCom
            return {
                "issues": all_issues,
                "api_calls": api_calls,
                "total_issues": len(all_issues)
            }
            
        except Exception as e:
            logging.error(f"Error in GitHubIssuesOperator: {e}")
            raise AirflowException(f"Failed to fetch GitHub issues: {e}")

class DataQualityCheckOperator(BaseOperator):
    """
    Custom operator for data quality checks
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
                
                # Basic quality checks
                total_records = df.count()
                null_ids = df.filter(F.col("id").isNull()).count()
                null_titles = df.filter(F.col("title").isNull()).count()
                
                # Calculate null percentages
                id_null_pct = (null_ids / total_records) if total_records > 0 else 0
                title_null_pct = (null_titles / total_records) if total_records > 0 else 0
                
                # Check for recent data
                recent_data = df.filter(
                    F.col("created_at") >= F.current_date() - F.expr("INTERVAL 7 DAYS")
                ).count()
                
                # Quality metrics
                quality_metrics = {
                    "total_records": total_records,
                    "null_ids": null_ids,
                    "null_titles": null_titles,
                    "id_null_percentage": id_null_pct,
                    "title_null_percentage": title_null_pct,
                    "recent_records": recent_data
                }
                
                logging.info(f"Data Quality Check Results: {quality_metrics}")
                
                # Quality checks
                if total_records < self.min_records:
                    raise AirflowException(f"Too few records: {total_records} < {self.min_records}")
                
                if id_null_pct > self.max_null_percentage:
                    raise AirflowException(f"Too many null IDs: {id_null_pct:.2%} > {self.max_null_percentage:.2%}")
                
                if title_null_pct > self.max_null_percentage:
                    raise AirflowException(f"Too many null titles: {title_null_pct:.2%} > {self.max_null_percentage:.2%}")
                
                return quality_metrics
                
            finally:
                spark.stop()
                
        except Exception as e:
            logging.error(f"Error in DataQualityCheckOperator: {e}")
            raise AirflowException(f"Data quality check failed: {e}")

class SparkETLOperator(BaseOperator):
    """
    Custom operator for Spark ETL operations
    """
    
    @apply_defaults
    def __init__(
        self,
        table_name: str,
        issues_data: List[Dict[str, Any]],
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.table_name = table_name
        self.issues_data = issues_data
    
    def execute(self, context):
        """
        Execute Spark ETL operation
        """
        try:
            from pyspark.sql import SparkSession
            from pyspark.sql import functions as F
            from pyspark.sql.types import IntegerType, StringType, TimestampType, ArrayType
            
            # Initialize Spark
            spark = SparkSession.builder \
                .appName("GitHubIssuesETL") \
                .config("spark.sql.adaptive.enabled", "true") \
                .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
                .getOrCreate()
            
            try:
                if not self.issues_data:
                    logging.warning("No issues data to process")
                    return {"processed_records": 0}
                
                # Process issues data
                processed_issues = []
                for issue in self.issues_data:
                    try:
                        # Extract and clean data
                        user_data = issue.get("user", {}) or {}
                        milestone_data = issue.get("milestone", {}) or {}
                        pull_request_data = issue.get("pull_request", {}) or {}
                        
                        # Clean arrays
                        labels = [l.get("name") for l in (issue.get("labels", []) or []) if l and l.get("name")]
                        assignees = [a.get("login") for a in (issue.get("assignees", []) or []) if a and a.get("login")]
                        
                        # Create pull_request struct
                        pull_request_struct = None
                        if pull_request_data:
                            pull_request_struct = {
                                "url": pull_request_data.get("url"),
                                "html_url": pull_request_data.get("html_url"),
                                "diff_url": pull_request_data.get("diff_url"),
                                "patch_url": pull_request_data.get("patch_url")
                            }
                        
                        processed_issue = {
                            "id": issue.get("id"),
                            "number": issue.get("number"),
                            "title": issue.get("title"),
                            "state": issue.get("state"),
                            "created_at": issue.get("created_at"),
                            "closed_at": issue.get("closed_at"),
                            "updated_at": issue.get("updated_at"),
                            "user_login": user_data.get("login"),
                            "assignees": assignees,
                            "labels": labels,
                            "comments": issue.get("comments", 0),
                            "milestone_title": milestone_data.get("title"),
                            "pull_request": pull_request_struct,
                            "body": issue.get("body")
                        }
                        
                        processed_issues.append(processed_issue)
                        
                    except Exception as e:
                        logging.error(f"Error processing issue {issue.get('id', 'unknown')}: {e}")
                        continue
                
                if not processed_issues:
                    logging.warning("No valid issues data after processing")
                    return {"processed_records": 0}
                
                # Convert to Spark DataFrame
                df = spark.createDataFrame(processed_issues)
                
                # Cast columns to proper types
                df = df.withColumn("id", F.col("id").cast(IntegerType())) \
                       .withColumn("number", F.col("number").cast(IntegerType())) \
                       .withColumn("comments", F.col("comments").cast(IntegerType())) \
                       .withColumn("created_at", F.to_timestamp(F.col("created_at"))) \
                       .withColumn("closed_at", F.to_timestamp(F.col("closed_at"))) \
                       .withColumn("updated_at", F.to_timestamp(F.col("updated_at")))
                
                # Write to table
                df.write.mode("append").saveAsTable(self.table_name)
                
                processed_count = df.count()
                logging.info(f"Successfully processed {processed_count} records to {self.table_name}")
                
                return {"processed_records": processed_count}
                
            finally:
                spark.stop()
                
        except Exception as e:
            logging.error(f"Error in SparkETLOperator: {e}")
            raise AirflowException(f"Spark ETL operation failed: {e}")
