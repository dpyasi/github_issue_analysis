# Databricks Deployment Guide

This guide explains how to deploy and use the GitHub Issues ETL pipeline in Databricks.

## 📁 Files for Databricks

### **Core Files to Copy:**
```
load_table_loungebip_test_internal_huggingface_transformers_issues.py    # ETL Pipeline
query_table_loungebip_test_internal_huggingface_transformers_issues.py  # SQL Queries
sql/create_tables.sql                                                    # Schema Reference
```

### **Optional Files:**
```
data_quality/data_quality_checks.py    # Quality validation
README.md                             # Documentation
```

## 🚀 Deployment Steps

### **Step 1: Copy Files to Databricks**
1. **Upload to Databricks Workspace:**
   - Go to your Databricks workspace
   - Navigate to Workspace → Users → [your-username]
   - Create a folder: `github-issues-etl`
   - Upload the core files

### **Step 2: Create Databricks Job**
1. **Go to Jobs:**
   - Click "Jobs" in the left sidebar
   - Click "Create Job"

2. **Configure Job:**
   - **Name**: `GitHub Issues ETL`
   - **Type**: Notebook
   - **Source**: Upload `load_table_loungebip_test_internal_huggingface_transformers_issues.py`

3. **Set Schedule:**
   - **Schedule Type**: Cron
   - **Cron Expression**: `0 6 * * *` (Daily at 6:00 AM UTC)

### **Step 3: Run ETL Pipeline**

#### **Option A: Run in Notebook**
```python
# In a Databricks notebook
%run /path/to/load_table_loungebip_test_internal_huggingface_transformers_issues.py
```

#### **Option B: Run as Job**
- Go to Jobs → GitHub Issues ETL
- Click "Run Now"

### **Step 4: Query Data**

#### **Option A: Run Query Script**
```python
# In a Databricks notebook
%run /path/to/query_table_loungebip_test_internal_huggingface_transformers_issues.py
```

#### **Option B: Direct SQL**
```sql
-- Check table exists
SELECT COUNT(*) FROM loungebip_test.internal.huggingface_transformers_issues;

-- Recent issues
SELECT number, title, state, user_login, created_at
FROM loungebip_test.internal.huggingface_transformers_issues
ORDER BY created_at DESC
LIMIT 10;
```

## 🔧 Configuration

### **ETL Settings:**
```python
# In load_table_loungebip_test_internal_huggingface_transformers_issues.py
REPO_OWNER = "huggingface"           # GitHub repository owner
REPO_NAME = "transformers"            # GitHub repository name
MAX_PAGES = None                     # None = all pages, or limit for testing
```

### **Table Settings:**
```python
# Target table (already exists in your environment)
TABLE_NAME = "loungebip_test.internal.huggingface_transformers_issues"
```

## 📊 Expected Results

### **Data Volume:**
- **Total Issues**: 10,000+ (all time)
- **Open Issues**: 1,080+ (current)
- **Closed Issues**: 9,000+ (historical)
- **Pull Requests**: 2,000+ (estimated)

### **ETL Performance:**
- **Runtime**: 5-15 minutes (depending on data volume)
- **API Calls**: 100+ (GitHub API pagination)
- **Data Size**: ~50-100 MB (compressed)

## 🔍 Monitoring

### **Check ETL Status:**
```sql
-- Check recent data
SELECT 
  COUNT(*) as total_records,
  MAX(created_at) as latest_issue,
  MIN(created_at) as earliest_issue
FROM loungebip_test.internal.huggingface_transformers_issues;
```

### **Monitor Job Runs:**
- Go to Jobs → GitHub Issues ETL
- View run history and logs
- Check for errors or warnings

## 🛠️ Troubleshooting

### **Common Issues:**

1. **Table Not Found:**
   ```sql
   -- Check if table exists
   SHOW TABLES IN loungebip_test.internal;
   ```

2. **Permission Denied:**
   - Ensure you have write access to `loungebip_test.internal` schema
   - Check with your Databricks admin

3. **API Rate Limits:**
   - GitHub API has rate limits
   - ETL includes built-in rate limiting
   - Consider running during off-peak hours

4. **Memory Issues:**
   - Large datasets may require cluster scaling
   - Consider using smaller `MAX_PAGES` for testing

## 📈 Next Steps

1. **Schedule Daily Runs** - Set up automated ETL
2. **Create Dashboards** - Build visualizations
3. **Set Up Alerts** - Monitor data quality
4. **Scale Up** - Process additional repositories

## 💡 Tips

- **Test First**: Use `MAX_PAGES = 5` for initial testing
- **Monitor Logs**: Check job run logs for issues
- **Backup Data**: Consider data retention policies
- **Optimize Performance**: Use appropriate cluster sizes
