# GitHub Issues Analytics Toolkit

A comprehensive ETL pipeline and analytics toolkit for GitHub issues data, designed for Databricks environments.

## 🎯 **What This Project Does**

This toolkit provides a complete solution for:
- **Extracting** GitHub issues data via API
- **Transforming** data with proper schema handling
- **Loading** data into Delta Lake tables
- **Visualizing** data with interactive dashboards and static charts
- **Analyzing** trends, patterns, and insights

## 📁 **Project Structure**

```
github_issues_analysis/
├── etl/                                    # ETL Pipeline
│   └── github_issues_etl_databricks.py    # Main ETL script (Databricks)
├── sql/                                   # Database Schema
│   └── create_tables.sql                 # Table creation scripts
├── visualizations/                        # Interactive Dashboard
│   └── github_issues_dashboard.py         # Streamlit dashboard
├── funnel_charts/                         # Generated Charts
├── monthly_trends_2024/                   # Generated Charts
├── labels_analysis/                       # Generated Charts
├── long_open_issues_analysis/             # Generated Charts
├── create_*.py                           # Chart generation scripts
└── README.md                             # This file
```

## 🚀 **Quick Start Guide**

### **Step 1: Prerequisites**
- Databricks workspace with Spark/Delta Lake
- Python environment with required packages
- GitHub Personal Access Token (optional, for higher rate limits)

### **Step 2: Database Setup**
```sql
-- Run this in Databricks SQL or notebook
%run /path/to/sql/create_tables.sql
```

### **Step 3: Run ETL Pipeline**
```python
# In Databricks notebook
%run /path/to/etl/github_issues_etl_databricks.py
```

### **Step 4: Generate Charts**
```python
# Run individual chart scripts
%run /path/to/create_funnel_chart.py
%run /path/to/create_monthly_trends_2024.py
%run /path/to/create_simple_labels_chart.py
%run /path/to/create_long_open_issues_chart.py
```

### **Step 5: Interactive Dashboard**
```bash
# Run Streamlit dashboard
streamlit run visualizations/github_issues_dashboard.py
```

## 📊 **What Each Component Does**

### **1. ETL Pipeline (`etl/github_issues_etl_databricks.py`)**
- **Purpose**: Fetches GitHub issues data and loads into Delta Lake
- **Features**:
  - GitHub API integration with authentication
  - Handles large datasets (10,000+ issues)
  - Proper schema definition (LongType, ArrayType, StructType)
  - Timestamp parsing for ISO 8601 format
  - Rate limiting and error handling
- **Output**: Delta Lake table with complete GitHub issues data

### **2. Database Schema (`sql/create_tables.sql`)**
- **Purpose**: Creates the target table structure
- **Features**:
  - Optimized schema for GitHub issues data
  - Array types for labels and assignees
  - Struct type for pull request data
  - ETL run logging table
  - Daily summary table for analytics

### **3. Interactive Dashboard (`visualizations/github_issues_dashboard.py`)**
- **Purpose**: Interactive Streamlit dashboard for data exploration
- **Features**:
  - Real-time data visualization
  - Funnel charts for data filtering
  - Time series analysis
  - Labels analysis
  - Top contributors
  - Monthly trends
- **Usage**: `streamlit run visualizations/github_issues_dashboard.py`

### **4. Chart Generation Scripts**
- **`create_funnel_chart.py`**: Data filtering funnel analysis
- **`create_monthly_trends_2024.py`**: Monthly trends and patterns
- **`create_simple_labels_chart.py`**: Labels distribution analysis
- **`create_long_open_issues_chart.py`**: Long-open issues analysis
- **`create_detailed_monthly_analysis.py`**: Advanced monthly analysis

## 🔧 **Configuration**

### **ETL Pipeline Configuration**
```python
# In github_issues_etl_databricks.py
REPO_OWNER = "huggingface"           # GitHub repository owner
REPO_NAME = "transformers"           # Repository name
MAX_PAGES = None                      # None for all pages, or limit for testing
GITHUB_TOKEN = "your_token_here"     # GitHub Personal Access Token
```

### **Table Configuration**
```python
# Target table name
table_name = "loungebip_test.internal.huggingface_transformers_issues"
```

## 📈 **Generated Visualizations**

### **Funnel Charts** (`funnel_charts/`)
- Data filtering process visualization
- With vs without PRs comparison
- Detailed breakdown analysis

### **Monthly Trends** (`monthly_trends_2024/`)
- Simple monthly trends
- Comprehensive dashboard
- Growth rate analysis
- Bar chart breakdowns

### **Labels Analysis** (`labels_analysis/`)
- Top labels visualization
- Pie chart distribution
- Category breakdown
- Treemap hierarchy

### **Long Open Issues** (`long_open_issues_analysis/`)
- Heatmap by label and timeframe
- Timeframe distribution
- Top long-open labels
- Cumulative analysis

## 🎯 **Execution Order**

### **For First-Time Setup:**
1. **Database Setup** → Run `sql/create_tables.sql`
2. **ETL Pipeline** → Run `etl/github_issues_etl_databricks.py`
3. **Generate Charts** → Run chart generation scripts
4. **Interactive Dashboard** → Run `visualizations/github_issues_dashboard.py`

### **For Regular Updates:**
1. **ETL Pipeline** → Run ETL to get latest data
2. **Generate Charts** → Update visualizations
3. **Dashboard** → View updated data

## 🔍 **Data Flow**

```
GitHub API → ETL Pipeline → Delta Lake Table → Charts/Dashboard
     ↓              ↓              ↓              ↓
  Raw Data    Transform    Structured Data   Visualizations
```

## 📊 **Expected Results**

### **ETL Pipeline Output:**
- **Data Volume**: 10,000+ GitHub issues
- **Table**: `loungebip_test.internal.huggingface_transformers_issues`
- **Schema**: Optimized for analytics and visualization

### **Charts Generated:**
- **25+ Professional Charts** in PNG format
- **Interactive Dashboard** with real-time data
- **Multiple Analysis Perspectives** (funnel, trends, labels, long-open)

## 🛠️ **Troubleshooting**

### **Common Issues:**
1. **Schema Errors**: Ensure proper data types (LongType for IDs)
2. **Rate Limiting**: Use GitHub token for higher limits
3. **Timestamp Issues**: ISO 8601 format parsing
4. **Memory Issues**: Process data in batches

### **Solutions:**
- Check Databricks logs for detailed error messages
- Verify GitHub token permissions
- Ensure proper schema definition
- Monitor memory usage during processing

## 📚 **Documentation**

- **`CHANGES_SUMMARY.md`**: What we built and why
- **`ETL_CHANGES_SUMMARY.md`**: Technical changes made
- **`data_modeling_analysis.md`**: Database design decisions
- **`schema_comparison_analysis.md`**: Schema optimization

## 🚀 **Next Steps**

1. **Customize Configuration**: Update repository and table names
2. **Schedule ETL**: Set up automated data updates
3. **Extend Analysis**: Add more chart types and insights
4. **Deploy Dashboard**: Host Streamlit dashboard for team access

## 📞 **Support**

For questions or issues:
- Check the documentation files
- Review error logs in Databricks
- Verify configuration settings
- Ensure proper permissions

---

**This toolkit provides a complete GitHub issues analytics solution with ETL, visualization, and interactive dashboard capabilities!** 🎯