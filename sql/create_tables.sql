-- GitHub Issues ETL Pipeline - Table Creation Script
-- Database: BigQuery/Spark SQL
-- Author: d.pyasi42@gmail.com

-- Main issues table matching your exact schema
CREATE OR REPLACE TABLE loungebip_test.internal.huggingface_transformers_issues(
  id BIGINT,
  number INT,
  title STRING,
  state STRING,
  created_at TIMESTAMP,
  closed_at TIMESTAMP,
  updated_at TIMESTAMP,
  user_login STRING,
  assignees ARRAY<STRING>,
  labels ARRAY<STRING>,
  comments INT,
  milestone_title STRING,
  pull_request STRUCT<
    url: STRING,
    html_url: STRING,
    diff_url: STRING,
    patch_url: STRING
  >,
  body STRING
)
COMMENT 'Table for GitHub issues from huggingface/transformers repo';

-- ETL run log table for tracking daily runs
CREATE OR REPLACE TABLE loungebip_test.internal.etl_run_log (
  batch_id STRING,
  run_date DATE,
  start_time TIMESTAMP,
  end_time TIMESTAMP,
  repo_owner STRING,
  repo_name STRING,
  issues_fetched INT,
  issues_processed INT,
  issues_new INT,
  issues_updated INT,
  issues_errors INT,
  api_calls_made INT,
  api_rate_limit_remaining INT,
  status STRING,
  error_message STRING,
  etl_timestamp TIMESTAMP
)
COMMENT 'ETL run log for tracking daily pipeline execution';

-- Daily summary table for analytics
CREATE OR REPLACE TABLE loungebip_test.internal.github_issues_daily_summary (
  summary_date DATE,
  total_issues INT,
  open_issues INT,
  closed_issues INT,
  new_issues_today INT,
  closed_issues_today INT,
  total_pull_requests INT,
  open_pull_requests INT,
  closed_pull_requests INT,
  top_contributors ARRAY<STRUCT<user_login STRING, issue_count INT>>,
  top_labels ARRAY<STRUCT<label STRING, count INT>>,
  etl_timestamp TIMESTAMP,
  etl_batch_id STRING
)
COMMENT 'Daily summary statistics for GitHub issues analytics';
