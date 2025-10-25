# GitHub Issues Analytics Toolkit

A comprehensive ETL pipeline and analytics toolkit for GitHub issues data, configurable for any repository (currently set for Hugging Face Transformers) and designed for Databricks environments.

## 🎯 **What This Project Does**

Complete solution for GitHub issues analytics:
- **ETL Pipeline**: Fetches GitHub data → Transforms → Loads to Delta Lake
- **Interactive Dashboard**: Real-time Streamlit dashboard with funnel charts
- **Static Visualizations**: 25+ professional charts for analysis
- **Automated Scheduling**: Airflow DAGs for daily ETL runs
- **Data Quality**: Automated checks and monitoring

## 📁 **Project Structure**

```
github_issues_analysis/
├── etl/                                    # ETL Pipeline
│   └── github_issues_etl_databricks.py    # Main ETL script
├── sql/                                   # Database Schema
│   └── create_tables.sql                 # Table creation
├── visualizations/                        # Interactive Dashboard
│   └── github_issues_dashboard.py         # Streamlit dashboard
├── airflow/                              # Automated Scheduling
│   ├── dags/                             # Airflow DAGs
│   ├── operators/                        # Custom operators
│   ├── docker-compose.yml               # Airflow setup
│   └── AIRFLOW_SETUP.md                 # Airflow documentation
├── data_quality/                         # Data Quality Checks
│   ├── data_quality_checks.py           # Quality functions
│   └── run_quality_checks.py          # Quality runner
├── funnel_charts/                        # Generated Charts
├── monthly_trends_2024/                  # Generated Charts
├── labels_analysis/                      # Generated Charts
├── long_open_issues_analysis/           # Generated Charts
├── create_*.py                          # Chart generation scripts
└── README.md                            # This file
```

## 🚀 **Quick Start (3 Steps)**

### **Step 1: Database Setup**
```sql
-- Run in Databricks SQL/notebook
%run /path/to/sql/create_tables.sql
```

### **Step 2: ETL Pipeline**
```python
# Run in Databricks notebook
%run /path/to/etl/github_issues_etl_databricks.py
```

### **Step 3: Interactive Dashboard**
```bash
# Run locally or in Databricks
streamlit run visualizations/github_issues_dashboard.py
```

## 🔧 **Configuration**

### **ETL Pipeline** (`etl/github_issues_etl_databricks.py`)
```python
REPO_OWNER = "huggingface"           # Change to your org
REPO_NAME = "transformers"           # Change to your repo
GITHUB_TOKEN = "your_token_here"     # Add your GitHub token
```

### **Dashboard** (`visualizations/github_issues_dashboard.py`)
```python
table_name = "loungebip_test.internal.huggingface_transformers_issues"
```

## 📊 **Components Overview**

### **1. ETL Pipeline**
- **Purpose**: Fetches GitHub issues → Transforms → Loads to Delta Lake
- **Features**: GitHub API integration, schema handling, rate limiting
- **Output**: Delta Lake table with 10,000+ issues

### **2. Interactive Dashboard**
- **Purpose**: Real-time data exploration with Streamlit
- **Features**: Funnel charts, trends, labels analysis, top contributors
- **Usage**: `streamlit run visualizations/github_issues_dashboard.py`

### **3. Airflow Scheduling** (`airflow/`)
- **Purpose**: Automated daily ETL runs
- **Features**: DAGs, custom operators, monitoring, alerts
- **Setup**: `docker-compose up` in airflow/ directory

### **4. Data Quality** (`data_quality/`)
- **Purpose**: Automated data quality checks
- **Features**: Record count, null checks, schema validation
- **Usage**: `python data_quality/run_quality_checks.py`

### **5. Chart Generation**
- **Purpose**: Static professional visualizations
- **Scripts**: `create_funnel_chart.py`, `create_monthly_trends_2024.py`, etc.
- **Output**: 25+ PNG charts in organized folders

## 🎯 **Execution Options**

### **Option A: Manual Execution**
1. Database Setup → ETL Pipeline → Dashboard
2. Generate charts as needed
3. Run quality checks

### **Option B: Automated with Airflow**
1. Set up Airflow: `cd airflow && docker-compose up`
2. ETL runs daily automatically
3. Quality checks run after ETL
4. Alerts on failures

### **Option C: Databricks Only**
1. Run ETL in Databricks notebook
2. Use Databricks SQL for queries
3. Generate charts in Databricks

## 📈 **Generated Visualizations**

- **Funnel Charts**: Data filtering process, PR vs Issues comparison
- **Monthly Trends**: Time series analysis, growth patterns
- **Labels Analysis**: Top labels, distribution, categories
- **Long Open Issues**: Heatmaps, timeframe analysis
- **Interactive Dashboard**: Real-time exploration

## 🛠️ **Troubleshooting**

### **Common Issues:**
- **Schema Errors**: Check data types (LongType for IDs)
- **Rate Limiting**: Add GitHub token
- **Timestamp Issues**: ISO 8601 format parsing
- **Airflow Issues**: Check Docker setup and logs

### **Solutions:**
- Check Databricks logs for detailed errors
- Verify GitHub token permissions
- Ensure proper schema definition
- Monitor Airflow UI for DAG status

## 📚 **Documentation**

- **`CHANGES_SUMMARY.md`**: Project evolution and features
- **`ETL_CHANGES_SUMMARY.md`**: Technical implementation details
- **`data_modeling_analysis.md`**: Database design decisions
- **`schema_comparison_analysis.md`**: Schema optimization
- **`airflow/AIRFLOW_SETUP.md`**: Airflow setup and usage

## 🚀 **Next Steps**

1. **Customize**: Update repository and table names
2. **Schedule**: Set up Airflow for automated runs
3. **Extend**: Add more chart types and insights
4. **Deploy**: Host dashboard for team access

---

**Complete GitHub issues analytics solution with ETL, visualization, scheduling, and quality monitoring!** 🎯