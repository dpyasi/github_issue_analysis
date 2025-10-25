# 🚀 **Execution Guide - Step by Step**

## **For New Users Opening Your GitHub Repository**

### **📋 Prerequisites Checklist**
- [ ] Databricks workspace access
- [ ] Python environment with required packages
- [ ] GitHub Personal Access Token (optional but recommended)
- [ ] Basic understanding of Spark/Delta Lake

### **🎯 Execution Order (What to Run First)**

## **Step 1: Database Setup** 
```sql
-- Run this FIRST in Databricks SQL or notebook
%run /path/to/sql/create_tables.sql
```
**What it does**: Creates the target table structure for your data
**Expected result**: Table `loungebip_test.internal.huggingface_transformers_issues` created

---

## **Step 2: ETL Pipeline (Main Data Loading)**
```python
# Run this SECOND in Databricks notebook
%run /path/to/etl/github_issues_etl_databricks.py
```
**What it does**: 
- Fetches GitHub issues data via API
- Transforms data with proper schema
- Loads data into Delta Lake table
- Handles 10,000+ issues with authentication

**Expected result**: 
- 10,000+ records loaded into your table
- Logs showing successful data loading
- Data ready for analysis

---

## **Step 3: Generate Static Charts (Optional)**
```python
# Run these THIRD for static visualizations
%run /path/to/create_funnel_chart.py
%run /path/to/create_monthly_trends_2024.py
%run /path/to/create_simple_labels_chart.py
%run /path/to/create_long_open_issues_chart.py
```
**What it does**: Creates 25+ professional charts in PNG format
**Expected result**: Charts saved in respective folders

---

## **Step 4: Interactive Dashboard (Recommended)**
```bash
# Run this FOURTH for interactive analysis
streamlit run visualizations/github_issues_dashboard.py
```
**What it does**: 
- Launches interactive Streamlit dashboard
- Real-time data visualization
- Funnel charts, trends, labels analysis
- Interactive exploration of your data

**Expected result**: 
- Dashboard opens in browser
- Interactive charts and metrics
- Real-time data exploration

---

## **🔄 Regular Updates (After Initial Setup)**

### **Daily/Weekly Updates:**
```python
# Just run the ETL pipeline to get latest data
%run /path/to/etl/github_issues_etl_databricks.py
```

### **Generate Updated Charts:**
```python
# Run chart scripts to update visualizations
%run /path/to/create_*.py
```

---

## **📊 What Each Step Produces**

### **Step 1 Output:**
- ✅ Database table structure created
- ✅ Schema optimized for analytics
- ✅ ETL logging table ready

### **Step 2 Output:**
- ✅ 10,000+ GitHub issues loaded
- ✅ Complete dataset with all fields
- ✅ Data ready for analysis
- ✅ Logs showing success/failure

### **Step 3 Output:**
- ✅ 25+ professional charts
- ✅ Funnel analysis
- ✅ Monthly trends
- ✅ Labels analysis
- ✅ Long-open issues analysis

### **Step 4 Output:**
- ✅ Interactive dashboard
- ✅ Real-time data exploration
- ✅ Interactive charts
- ✅ Summary metrics
- ✅ Data filtering capabilities

---

## **🎯 Quick Start (5 Minutes)**

### **Minimum Viable Setup:**
1. **Database**: Run `sql/create_tables.sql`
2. **ETL**: Run `etl/github_issues_etl_databricks.py`
3. **Dashboard**: Run `streamlit run visualizations/github_issues_dashboard.py`

### **Expected Timeline:**
- **Database Setup**: 30 seconds
- **ETL Pipeline**: 5-10 minutes (depending on data volume)
- **Dashboard**: 30 seconds to launch

---

## **🔧 Configuration Required**

### **Before Running ETL:**
```python
# Update these in github_issues_etl_databricks.py
REPO_OWNER = "your_org"           # Change to your GitHub org
REPO_NAME = "your_repo"           # Change to your repository
GITHUB_TOKEN = "your_token"       # Add your GitHub token
```

### **Before Running Dashboard:**
```python
# Update table name in github_issues_dashboard.py
table_name = "your_schema.your_table"  # Change to your table
```

---

## **📈 Success Indicators**

### **ETL Success:**
- ✅ "Successfully loaded X records to table"
- ✅ No error messages in logs
- ✅ Data visible in table

### **Dashboard Success:**
- ✅ Dashboard opens in browser
- ✅ Charts display correctly
- ✅ Data loads without errors

### **Charts Success:**
- ✅ PNG files generated in folders
- ✅ No error messages during generation
- ✅ Charts display properly

---

## **🚨 Common Issues & Solutions**

### **Issue: "Table not found"**
**Solution**: Run Step 1 (Database Setup) first

### **Issue: "Rate limit exceeded"**
**Solution**: Add GitHub token to ETL script

### **Issue: "Schema errors"**
**Solution**: Check data types in ETL script

### **Issue: "Dashboard won't start"**
**Solution**: Install Streamlit: `pip install streamlit`

---

## **🎯 Final Result**

After completing all steps, you'll have:
- ✅ **Complete GitHub issues dataset** in Delta Lake
- ✅ **Interactive dashboard** for data exploration
- ✅ **25+ professional charts** for analysis
- ✅ **ETL pipeline** for regular updates
- ✅ **Full documentation** for team use

**Your GitHub repository will be a complete, professional analytics toolkit!** 🚀
