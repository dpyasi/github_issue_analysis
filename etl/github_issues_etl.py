#!/usr/bin/env python3
"""
GitHub Issues ETL Pipeline
Daily ETL process to fetch, process, and load GitHub issues data
Author: d.pyasi42@gmail.com
"""

import requests
import pandas as pd
from pyspark.sql import SparkSession, functions as F
from pyspark.sql.types import (
    IntegerType, StringType, TimestampType, ArrayType, BooleanType, StructType, StructField
)
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime, date
import uuid
import time
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('etl/github_issues_etl.log')
    ]
)
logger = logging.getLogger(__name__)

class GitHubIssuesETL:
    """
    Production ETL pipeline for GitHub issues data
    """
    
    def __init__(self, repo_owner: str = "huggingface", repo_name: str = "transformers"):
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.full_name = f"{repo_owner}/{repo_name}"
        self.base_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/issues"
        
        # Initialize Spark session
        self.spark = SparkSession.builder \
            .appName("GitHubIssuesETL") \
            .config("spark.sql.adaptive.enabled", "true") \
            .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
            .getOrCreate()
        
        # Initialize requests session
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'GitHub-Issues-ETL/1.0'
        })
        
        # ETL metadata
        self.batch_id = str(uuid.uuid4())
        self.run_date = date.today()
        self.start_time = datetime.now()
        
        logger.info(f"ETL Pipeline initialized for {self.full_name}")
        logger.info(f"Batch ID: {self.batch_id}")
    
    def fetch_issues(self, state: str = "all", per_page: int = 100, max_pages: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Fetch issues from GitHub API with pagination and rate limiting
        """
        all_issues = []
        page = 1
        api_calls = 0
        
        while True:
            try:
                params = {
                    "state": state,
                    "per_page": min(per_page, 100),
                    "page": page,
                    "sort": "updated",
                    "direction": "desc"
                }
                
                logger.info(f"Fetching page {page}...")
                response = self.session.get(self.base_url, params=params, timeout=30)
                response.raise_for_status()
                api_calls += 1
                
                issues = response.json()
                if not issues:
                    break
                
                all_issues.extend(issues)
                logger.info(f"Fetched {len(issues)} issues from page {page}")
                
                if max_pages and page >= max_pages:
                    break
                
                page += 1
                
                # Rate limiting: 60 requests/hour for unauthenticated, 5000/hour for authenticated
                time.sleep(0.1)
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Error fetching page {page}: {e}")
                break
            except Exception as e:
                logger.error(f"Unexpected error on page {page}: {e}")
                break
        
        logger.info(f"Total issues fetched: {len(all_issues)}")
        logger.info(f"Total API calls made: {api_calls}")
        
        return all_issues, api_calls
    
    def extract_issue_data(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract and clean issue data from GitHub API response
        """
        try:
            # Handle nested data safely
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
            
            return {
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
        except Exception as e:
            logger.error(f"Error extracting issue data: {e}")
            return {}
    
    def process_issues_to_spark(self, issues: List[Dict[str, Any]]) -> 'pyspark.sql.DataFrame':
        """
        Convert issues data to Spark DataFrame with proper schema
        """
        if not issues:
            logger.warning("No issues to process")
            return None
        
        # Extract and clean data
        issues_data = [self.extract_issue_data(issue) for issue in issues]
        issues_data = [data for data in issues_data if data]
        
        if not issues_data:
            logger.warning("No valid issue data after extraction")
            return None
        
        # Convert to Spark DataFrame
        df = self.spark.createDataFrame(issues_data)
        
        # Cast columns to proper types
        df = df.withColumn("id", F.col("id").cast(IntegerType())) \
               .withColumn("number", F.col("number").cast(IntegerType())) \
               .withColumn("comments", F.col("comments").cast(IntegerType())) \
               .withColumn("created_at", F.to_timestamp(F.col("created_at"))) \
               .withColumn("closed_at", F.to_timestamp(F.col("closed_at"))) \
               .withColumn("updated_at", F.to_timestamp(F.col("updated_at")))
        
        return df
    
    def load_to_raw_table(self, df: 'pyspark.sql.DataFrame', table_name: str = "loungebip_test.internal.huggingface_transformers_issues") -> bool:
        """
        Load data to raw issues table
        """
        try:
            if df is None or df.count() == 0:
                logger.warning("No data to load to raw table")
                return False
            
            # Write to table (append mode for daily ETL)
            df.write.mode("append").saveAsTable(table_name)
            
            logger.info(f"Successfully loaded {df.count()} records to {table_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading to raw table: {e}")
            return False
    
    def load_to_history_table(self, df: 'pyspark.sql.DataFrame', table_name: str = "loungebip_test.internal.github_issues_history") -> bool:
        """
        Load data to history table for change tracking
        """
        try:
            if df is None or df.count() == 0:
                logger.warning("No data to load to history table")
                return False
            
            # Add history tracking columns
            history_df = df.withColumn("is_current", F.lit(True)) \
                          .withColumn("previous_state", F.lit(None).cast(StringType()))
            
            # Write to history table
            history_df.write.mode("append").saveAsTable(table_name)
            
            logger.info(f"Successfully loaded {history_df.count()} records to {table_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading to history table: {e}")
            return False
    
    def create_daily_summary(self, df: 'pyspark.sql.DataFrame') -> bool:
        """
        Create daily summary statistics
        """
        try:
            if df is None or df.count() == 0:
                logger.warning("No data for daily summary")
                return False
            
            # Calculate summary statistics
            summary = df.groupBy("etl_run_date").agg(
                F.count("*").alias("total_issues"),
                F.sum(F.when(F.col("state") == "open", 1).otherwise(0)).alias("open_issues"),
                F.sum(F.when(F.col("state") == "closed", 1).otherwise(0)).alias("closed_issues"),
                F.sum(F.when(F.col("is_pull_request"), 1).otherwise(0)).alias("total_pull_requests"),
                F.sum(F.when(F.col("is_pull_request") & (F.col("state") == "open"), 1).otherwise(0)).alias("open_pull_requests"),
                F.sum(F.when(F.col("is_pull_request") & (F.col("state") == "closed"), 1).otherwise(0)).alias("closed_pull_requests")
            ).withColumn("summary_date", F.col("etl_run_date")) \
             .withColumn("new_issues_today", F.col("total_issues")) \
             .withColumn("closed_issues_today", F.lit(0)) \
             .withColumn("top_contributors", F.array()) \
             .withColumn("top_labels", F.array()) \
             .withColumn("etl_timestamp", F.current_timestamp()) \
             .withColumn("etl_batch_id", F.lit(self.batch_id))
            
            # Write to summary table
            summary.write.mode("append").saveAsTable("loungebip_test.internal.github_issues_daily_summary")
            
            logger.info("Daily summary created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error creating daily summary: {e}")
            return False
    
    def log_etl_run(self, issues_fetched: int, issues_processed: int, api_calls: int, status: str, error_message: str = None):
        """
        Log ETL run details
        """
        try:
            end_time = datetime.now()
            duration = (end_time - self.start_time).total_seconds()
            
            log_data = {
                "batch_id": self.batch_id,
                "run_date": self.run_date,
                "start_time": self.start_time,
                "end_time": end_time,
                "repo_owner": self.repo_owner,
                "repo_name": self.repo_name,
                "issues_fetched": issues_fetched,
                "issues_processed": issues_processed,
                "issues_new": issues_processed,  # Simplified for now
                "issues_updated": 0,
                "issues_errors": 0,
                "api_calls_made": api_calls,
                "api_rate_limit_remaining": 0,  # Would need to parse from response headers
                "status": status,
                "error_message": error_message,
                "etl_timestamp": datetime.now()
            }
            
            # Create DataFrame and write to log table
            log_df = self.spark.createDataFrame([log_data])
            log_df.write.mode("append").saveAsTable("loungebip_test.internal.etl_run_log")
            
            logger.info(f"ETL run logged: {status} - {issues_processed} issues processed in {duration:.2f}s")
            
        except Exception as e:
            logger.error(f"Error logging ETL run: {e}")
    
    def run_etl(self, max_pages: Optional[int] = None) -> bool:
        """
        Run the complete ETL pipeline
        """
        try:
            logger.info("=" * 60)
            logger.info("Starting GitHub Issues ETL Pipeline")
            logger.info("=" * 60)
            
            # Fetch issues
            issues, api_calls = self.fetch_issues(max_pages=max_pages)
            
            if not issues:
                logger.error("No issues fetched")
                self.log_etl_run(0, 0, api_calls, "FAILED", "No issues fetched")
                return False
            
            # Process to Spark DataFrame
            df = self.process_issues_to_spark(issues)
            
            if df is None:
                logger.error("Failed to process issues")
                self.log_etl_run(len(issues), 0, api_calls, "FAILED", "Failed to process issues")
                return False
            
            # Load to tables
            raw_success = self.load_to_raw_table(df)
            history_success = self.load_to_history_table(df)
            summary_success = self.create_daily_summary(df)
            
            if raw_success and history_success and summary_success:
                logger.info("✅ ETL pipeline completed successfully!")
                self.log_etl_run(len(issues), df.count(), api_calls, "SUCCESS")
                return True
            else:
                logger.error("❌ ETL pipeline failed during data loading")
                self.log_etl_run(len(issues), df.count(), api_calls, "PARTIAL", "Data loading failed")
                return False
                
        except Exception as e:
            logger.error(f"❌ ETL pipeline failed: {e}")
            self.log_etl_run(0, 0, 0, "FAILED", str(e))
            return False
        finally:
            self.spark.stop()

def main():
    """
    Main function to run the ETL pipeline
    """
    # Configuration
    REPO_OWNER = "huggingface"
    REPO_NAME = "transformers"
    MAX_PAGES = None  # Set to None for all pages, or limit for testing
    
    # Initialize and run ETL
    etl = GitHubIssuesETL(repo_owner=REPO_OWNER, repo_name=REPO_NAME)
    success = etl.run_etl(max_pages=MAX_PAGES)
    
    if success:
        print("✅ ETL pipeline completed successfully!")
    else:
        print("❌ ETL pipeline failed!")
        exit(1)

if __name__ == "__main__":
    main()
