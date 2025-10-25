# 🚀 **Execution Guide - What to Run When**

## **📋 For New Users**

### **Quick Start (3 Steps)**
1. **Database Setup** → `sql/create_tables.sql`
2. **ETL Pipeline** → `etl/github_issues_etl_databricks.py`
3. **Dashboard** → `streamlit run visualizations/github_issues_dashboard.py`

### **Optional: Generate Charts**
```python
python create_funnel_chart.py
python create_monthly_trends_2024.py
python create_simple_labels_chart.py
python create_long_open_issues_chart.py
```

## **🔄 For Automated Operations**

### **Airflow Setup (Production)**
```bash
cd airflow
docker-compose up -d
# Access: http://localhost:8080 (airflow/airflow)
```

### **Data Quality Checks**
```python
python data_quality/run_quality_checks.py
```

## **🎯 Execution Order**

### **First Time Setup:**
1. Database → ETL → Dashboard
2. Generate charts (optional)
3. Set up Airflow (optional)

### **Regular Updates:**
1. ETL Pipeline (gets latest data)
2. Dashboard (views updated data)
3. Airflow (automated daily runs)

## **⚙️ Configuration Required**

### **Before Running ETL:**
- Update repository name in `etl/github_issues_etl_databricks.py`
- Add GitHub token for higher rate limits
- Update table name if needed

### **Before Running Dashboard:**
- Update table name in `visualizations/github_issues_dashboard.py`
- Ensure data is loaded in the table

### **Before Running Airflow:**
- Set up Docker environment
- Configure Airflow variables
- Set up email notifications

## **📊 Expected Results**

### **ETL Success:**
- ✅ "Successfully loaded X records to table"
- ✅ No error messages
- ✅ Data visible in table

### **Dashboard Success:**
- ✅ Opens in browser
- ✅ Charts display correctly
- ✅ Data loads without errors

### **Airflow Success:**
- ✅ DAG appears in Airflow UI
- ✅ Tasks execute successfully
- ✅ Email notifications work

## **🚨 Common Issues**

### **ETL Issues:**
- **Rate limiting**: Add GitHub token
- **Schema errors**: Check data types
- **Memory issues**: Process in batches

### **Dashboard Issues:**
- **Table not found**: Run ETL first
- **Charts not loading**: Check data quality
- **Performance issues**: Optimize queries

### **Airflow Issues:**
- **DAG not appearing**: Check file permissions
- **Task failures**: Review logs
- **Docker issues**: Check Docker setup

## **📞 Support**

- Check logs in Databricks/Airflow
- Review error messages
- Verify configuration settings
- Ensure proper permissions

---

**This guide covers all execution scenarios without repetition!** 🎯
