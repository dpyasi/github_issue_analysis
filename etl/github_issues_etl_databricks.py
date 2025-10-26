#!/usr/bin/env python3
"""
GitHub Issues ETL Pipeline for Databricks
Modified to work with Databricks environment
Author: d.pyasi42@gmail.com
"""

import requests
import pandas as pd
from pyspark.sql import SparkSession, functions as F
from pyspark.sql.types import (
    IntegerType, LongType, StringType, TimestampType, ArrayType, BooleanType, StructType, StructField
)
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime, date
import uuid
import time
import json

# Configure logging for Databricks (no file logging)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Only console output for Databricks
    ]
)
logger = logging.getLogger(__name__)

class GitHubIssuesETL:
    """
    Production ETL pipeline for GitHub issues data (Databricks version)
    """
    
    def __init__(self, repo_owner: str = "huggingface", repo_name: str = "transformers", github_token: str = None):
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.full_name = f"{repo_owner}/{repo_name}"
        self.base_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/issues"
        
        # Use existing Spark session in Databricks
        self.spark = spark  # Databricks provides 'spark' variable
        
        # Initialize requests session with authentication
        self.session = requests.Session()
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'GitHub-Issues-ETL/1.0'
        }
        
        # Add authentication if token provided
        if github_token:
            headers['Authorization'] = f'token {github_token}'
            logger.info("GitHub authentication enabled")
            
            # Test token validity and permissions
            self._test_token(github_token)
        else:
            logger.warning("No GitHub token provided - using unauthenticated requests (60/hour limit)")
        
        self.session.headers.update(headers)
    
    def _test_token(self, token: str):
        """
        Test if GitHub token is valid and has required permissions
        """
        try:
            test_headers = {
                'Authorization': f'token {token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            # Test authentication
            response = requests.get('https://api.github.com/user', headers=test_headers, timeout=10)
            
            if response.status_code == 200:
                user_info = response.json()
                logger.info(f"✅ GitHub token is valid for user: {user_info.get('login')}")
                
                # Check rate limit
                rate_response = requests.get('https://api.github.com/rate_limit', headers=test_headers)
                if rate_response.status_code == 200:
                    limits = rate_response.json()['resources']['core']
                    logger.info(f"Rate limit: {limits['remaining']} requests remaining (limit: {limits['limit']})")
                
            elif response.status_code == 401:
                logger.error("❌ GitHub token is invalid or expired")
                raise Exception("GitHub token authentication failed. Please check your token.")
            else:
                logger.warning(f"⚠️ Unexpected response when testing token: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            logger.warning(f"⚠️ Could not test GitHub token: {e}")
        
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
                
                # Check rate limit headers
                remaining = response.headers.get('X-RateLimit-Remaining', 'unknown')
                logger.info(f"Rate limit remaining: {remaining}")
                
                if response.status_code == 403:
                    logger.error(f"Rate limit exceeded or unauthorized. Status: {response.status_code}")
                    logger.error(f"Response: {response.text[:500]}")
                    raise Exception("GitHub API rate limit exceeded. Please check your token or wait.")
                
                response.raise_for_status()
                api_calls += 1
                
                issues = response.json()
                
                # Validate response format
                if not isinstance(issues, list):
                    logger.error(f"Unexpected response format. Expected list, got {type(issues)}")
                    logger.error(f"Response: {str(issues)[:500]}")
                    break
                
                if not issues:
                    break
                
                all_issues.extend(issues)
                logger.info(f"Fetched {len(issues)} issues from page {page}")
                
                if max_pages and page >= max_pages:
                    break
                
                page += 1
                
                # Rate limiting
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
            
            # Parse timestamps from ISO format to proper format
            created_at = issue.get("created_at")
            closed_at = issue.get("closed_at")
            updated_at = issue.get("updated_at")
            
            return {
                "id": issue.get("id"),
                "number": issue.get("number"),
                "title": issue.get("title"),
                "state": issue.get("state"),
                "created_at": created_at,  # Keep as string, Spark will parse
                "closed_at": closed_at,    # Keep as string, Spark will parse
                "updated_at": updated_at,  # Keep as string, Spark will parse
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
        
        # Define explicit schema to avoid type inference issues
        schema = StructType([
            StructField("id", LongType(), True),  # Changed to LongType for large GitHub IDs
            StructField("number", IntegerType(), True),
            StructField("title", StringType(), True),
            StructField("state", StringType(), True),
            StructField("created_at", StringType(), True),  # Keep as string first
            StructField("closed_at", StringType(), True),   # Keep as string first
            StructField("updated_at", StringType(), True),  # Keep as string first
            StructField("user_login", StringType(), True),
            StructField("assignees", ArrayType(StringType()), True),
            StructField("labels", ArrayType(StringType()), True),
            StructField("comments", IntegerType(), True),
            StructField("milestone_title", StringType(), True),
            StructField("pull_request", StructType([
                StructField("url", StringType(), True),
                StructField("html_url", StringType(), True),
                StructField("diff_url", StringType(), True),
                StructField("patch_url", StringType(), True)
            ]), True),
            StructField("body", StringType(), True)
        ])
        
        # Convert to Spark DataFrame with explicit schema
        df = self.spark.createDataFrame(issues_data, schema)
        
        # Convert timestamp strings to proper timestamp type
        df = df.withColumn("created_at", F.to_timestamp(F.col("created_at"), "yyyy-MM-dd'T'HH:mm:ss'Z'")) \
               .withColumn("closed_at", F.to_timestamp(F.col("closed_at"), "yyyy-MM-dd'T'HH:mm:ss'Z'")) \
               .withColumn("updated_at", F.to_timestamp(F.col("updated_at"), "yyyy-MM-dd'T'HH:mm:ss'Z'"))
        
        return df
    
    def load_to_table(self, df: 'pyspark.sql.DataFrame', table_name: str = "loungebip_test.internal.huggingface_transformers_issues") -> bool:
        """
        Load data to Delta Lake table using SCD Type 2 (keeps history with effective dates)
        Creates new row when record changes, expires old row
        
        Args:
            df: Spark DataFrame with issue data
            table_name: Target table name
        
        Returns:
            bool: Success status
        """
        try:
            if df is None or df.count() == 0:
                logger.warning("No data to load to table")
                return False
            
            return self._load_with_scd2(df, table_name)
                
        except Exception as e:
            logger.error(f"Error loading to table: {e}")
            return False
    
    def _load_with_scd2(self, df: 'pyspark.sql.DataFrame', table_name: str) -> bool:
        """
        Load data using Type 2 SCD (keeps history with effective dates)
        Creates new row when record changes, expires old row
        """
        try:
            logger.info("Starting SCD Type 2 load (keeping history with effective dates)...")
            
            from pyspark.sql.functions import col, current_timestamp, lit, when, isnan, isnull
            from datetime import datetime
            
            # Create temporary view for the new data
            temp_view = "temp_new_issues"
            df.createOrReplaceTempView(temp_view)
            
            # Step 1: Identify changed records and mark old ones as expired
            expire_old_sql = f"""
            UPDATE {table_name} AS target
            SET effective_end_date = current_timestamp()
            WHERE target.id IN (
                SELECT source.id
                FROM {temp_view} AS source
                WHERE EXISTS (
                    SELECT 1 
                    FROM {table_name} AS existing
                    WHERE existing.id = source.id
                    AND (
                        existing.state != source.state OR
                        existing.comments != source.comments OR
                        existing.updated_at != source.updated_at
                    )
                )
            )
            AND target.effective_end_date IS NULL
            """
            
            self.spark.sql(expire_old_sql)
            logger.info("Expired old records")
            
            # Step 2: Insert only changed or new records with effective_start_date
            insert_new_sql = f"""
            INSERT INTO {table_name}
            SELECT 
                source.*,
                current_timestamp() AS effective_start_date,
                NULL AS effective_end_date
            FROM {temp_view} AS source
            WHERE NOT EXISTS (
                -- Skip if already exists with same data and current
                SELECT 1
                FROM {table_name} AS existing
                WHERE existing.id = source.id
                AND existing.effective_end_date IS NULL
                AND existing.state = source.state
                AND existing.comments = source.comments
            )
            """
            
            self.spark.sql(insert_new_sql)
            
            # Clean up temp view
            self.spark.catalog.dropTempView(temp_view)
            
            records_count = df.count()
            logger.info(f"Successfully loaded {records_count} records with SCD Type 2")
            logger.info("✅ History preserved - new rows created for changes")
            return True
            
        except Exception as e:
            logger.error(f"Error in SCD2 load: {e}")
            return False
    
    def run_etl(self, max_pages: Optional[int] = None) -> bool:
        """
        Run the complete ETL pipeline using SCD Type 2 (keeps history)
        
        Args:
            max_pages: Maximum number of pages to fetch (None for all)
        """
        try:
            logger.info("=" * 60)
            logger.info("Starting GitHub Issues ETL Pipeline")
            logger.info("=" * 60)
            logger.info("Mode: SCD Type 2 (history preserved with effective dates)")
            
            # Fetch issues
            issues, api_calls = self.fetch_issues(max_pages=max_pages)
            
            if not issues:
                logger.error("No issues fetched")
                return False
            
            # Process to Spark DataFrame
            df = self.process_issues_to_spark(issues)
            
            if df is None:
                logger.error("Failed to process issues")
                return False
            
            # Load to table
            success = self.load_to_table(df)
            
            if success:
                logger.info("✅ ETL pipeline completed successfully!")
                return True
            else:
                logger.error("❌ ETL pipeline failed during data loading")
                return False
                
        except Exception as e:
            logger.error(f"❌ ETL pipeline failed: {e}")
            return False

def main():
    """
    Main function to run the ETL pipeline in Databricks
    
    Usage:
        1. Set your GitHub token as environment variable in Databricks notebook:
           import os
           os.environ['GITHUB_TOKEN'] = 'ghp_your_token_here'
        
        2. Run this script:
           %run /path/to/github_issues_etl_databricks.py
    """
    # Configuration
    REPO_OWNER = "huggingface"
    REPO_NAME = "transformers"
    MAX_PAGES = None  # Set to None for all pages, or limit for testing
    
    # Get token from environment variable
    import os
    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
    
    if not GITHUB_TOKEN:
        logger.warning("No GitHub token provided - using unauthenticated requests (60/hour limit)")
        logger.warning("To use authenticated requests:")
        logger.warning("  import os")
        logger.warning("  os.environ['GITHUB_TOKEN'] = 'ghp_your_token_here'")
    else:
        logger.info("Using GitHub token from environment variable")
    
    # Initialize and run ETL
    etl = GitHubIssuesETL(
        repo_owner=REPO_OWNER, 
        repo_name=REPO_NAME, 
        github_token=GITHUB_TOKEN
    )
    success = etl.run_etl(max_pages=MAX_PAGES)
    
    if success:
        print("✅ ETL pipeline completed successfully!")
    else:
        print("❌ ETL pipeline failed!")
        return 1

if __name__ == "__main__":
    main()
