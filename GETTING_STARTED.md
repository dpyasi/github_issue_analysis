# 🚀 **Getting Started - 5 Minute Setup**

## **Quick Start for New Users**

### **📋 What You Need:**
- Databricks workspace
- Python environment
- GitHub token (optional but recommended)

### **🎯 3-Step Setup:**

## **Step 1: Database Setup** (30 seconds)
```sql
-- Run this in Databricks SQL or notebook
%run /path/to/sql/create_tables.sql
```

## **Step 2: Load Data** (5-10 minutes)
```python
# Run this in Databricks notebook
%run /path/to/etl/github_issues_etl_databricks.py
```

## **Step 3: View Dashboard** (30 seconds)
```bash
# Run this in terminal
streamlit run visualizations/github_issues_dashboard.py
```

---

## **🎯 What You'll Get:**

### **After Step 1:**
- ✅ Database table created
- ✅ Schema optimized for analytics

### **After Step 2:**
- ✅ 10,000+ GitHub issues loaded
- ✅ Complete dataset ready for analysis

### **After Step 3:**
- ✅ Interactive dashboard opens in browser
- ✅ Real-time data visualization
- ✅ Funnel charts, trends, labels analysis

---

## **🔧 Configuration (Before Running):**

### **Update ETL Script:**
```python
# In etl/github_issues_etl_databricks.py
REPO_OWNER = "your_org"           # Change to your GitHub org
REPO_NAME = "your_repo"           # Change to your repository
GITHUB_TOKEN = "your_token"       # Add your GitHub token
```

### **Update Dashboard:**
```python
# In visualizations/github_issues_dashboard.py
table_name = "your_schema.your_table"  # Change to your table
```

---

## **📊 Expected Results:**

### **ETL Pipeline Output:**
```
2024-01-15 10:30:00 - INFO - ETL Pipeline initialized
2024-01-15 10:30:01 - INFO - Fetching page 1...
2024-01-15 10:30:05 - INFO - Successfully loaded 10,847 records
2024-01-15 10:30:05 - INFO - ✅ ETL pipeline completed successfully!
```

### **Dashboard Output:**
- Interactive dashboard opens in browser
- Summary metrics display
- Charts render correctly
- Data loads without errors

---

## **🚨 Troubleshooting:**

### **Issue: "Table not found"**
**Solution**: Run Step 1 (Database Setup) first

### **Issue: "Rate limit exceeded"**
**Solution**: Add GitHub token to ETL script

### **Issue: "Dashboard won't start"**
**Solution**: Install Streamlit: `pip install streamlit`

---

## **📚 Next Steps:**

### **Optional: Generate Static Charts**
```python
# Run these for additional visualizations
%run /path/to/create_funnel_chart.py
%run /path/to/create_monthly_trends_2024.py
%run /path/to/create_simple_labels_chart.py
%run /path/to/create_long_open_issues_chart.py
```

### **Regular Updates:**
```python
# Just run the ETL pipeline to get latest data
%run /path/to/etl/github_issues_etl_databricks.py
```

---

## **🎯 Success Indicators:**

### **ETL Success:**
- ✅ "Successfully loaded X records to table"
- ✅ No error messages in logs
- ✅ Data visible in table

### **Dashboard Success:**
- ✅ Dashboard opens in browser
- ✅ Charts display correctly
- ✅ Data loads without errors

---

**That's it! You now have a complete GitHub Issues Analytics Toolkit running!** 🎯

## **📞 Need Help?**

- Check `README.md` for detailed documentation
- Review `EXECUTION_GUIDE.md` for step-by-step instructions
- See `PROJECT_FLOW.md` for understanding the data flow
- Check error logs in Databricks for troubleshooting
