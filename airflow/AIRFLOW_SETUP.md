# Airflow Setup Guide for GitHub Issues ETL Pipeline

## 🚀 Quick Start with Docker

### **Step 1: Prerequisites**
```bash
# Install Docker and Docker Compose
# Ensure you have at least 4GB RAM and 2 CPUs available
```

### **Step 2: Setup Airflow**
```bash
# Navigate to the airflow directory
cd airflow

# Create necessary directories
mkdir -p dags logs plugins operators

# Set Airflow user ID
export AIRFLOW_UID=50000

# Initialize Airflow
docker-compose up airflow-init

# Start all services
docker-compose up -d
```

### **Step 3: Access Airflow UI**
- **URL**: http://localhost:8080
- **Username**: `airflow`
- **Password**: `airflow`

## 📊 DAG Available

### **GitHub Issues ETL DAG** (`github_issues_etl`)
- **Schedule**: Daily at 6:00 AM UTC
- **Tasks**: Fetch → Load → Quality Check → Summary → Notifications
- **Features**: Custom operators, error handling, email notifications, data quality checks

## 🔧 Configuration

### **Airflow Variables**
Set these in the Airflow UI (Admin → Variables):

```bash
# Repository configuration
github_repo_owner: huggingface
github_repo_name: transformers
github_max_pages: null  # or set a limit like 100

# Email configuration
email_on_failure: true
email_on_retry: false
```

### **Connection Configuration**
Set these in the Airflow UI (Admin → Connections):

```bash
# GitHub API connection (optional)
conn_id: github_api
conn_type: HTTP
host: https://api.github.com
```

## 📈 Monitoring and Alerting

### **Email Notifications**
- **Success**: Sent to configured email on successful completion
- **Failure**: Sent to configured email on task failure
- **Retry**: Configurable retry attempts with delays

### **Logs and Monitoring**
- **Task Logs**: Available in Airflow UI
- **DAG Runs**: Track execution history
- **Task Instances**: Monitor individual task status
- **XCom**: Data exchange between tasks

## 🛠️ Custom Operators

### **GitHubIssuesOperator**
- Fetches issues from GitHub API
- Handles pagination and rate limiting
- Returns structured data for processing

### **DataQualityCheckOperator**
- Validates data quality
- Configurable thresholds
- Detailed quality metrics

### **SparkETLOperator**
- Processes data with Spark
- Handles schema validation
- Loads data to target table

## 📊 Dashboard Integration

### **Streamlit Dashboard**
```bash
# Run the dashboard
streamlit run visualizations/github_issues_dashboard.py
```

### **Airflow UI Features**
- **DAG View**: Visual representation of the pipeline
- **Task Logs**: Detailed execution logs
- **Metrics**: Performance and execution statistics
- **Variables**: Configuration management

## 🔄 Daily Operations

### **Manual Trigger**
```bash
# Trigger DAG manually
curl -X POST "http://localhost:8080/api/v1/dags/github_issues_etl/dagRuns" \
  -H "Content-Type: application/json" \
  -d '{"conf": {}}'
```

### **Monitoring**
- **DAG Status**: Check in Airflow UI
- **Task Status**: Monitor individual tasks
- **Logs**: Review execution logs
- **Alerts**: Email notifications

## 🚨 Troubleshooting

### **Common Issues**

1. **DAG not appearing**
   - Check file permissions
   - Verify DAG syntax
   - Check Airflow logs

2. **Task failures**
   - Review task logs
   - Check dependencies
   - Verify configuration

3. **Data quality issues**
   - Review quality check logs
   - Adjust thresholds
   - Check data source

### **Logs Location**
```bash
# Airflow logs
./logs/

# Application logs
./logs/dags/github_issues_etl/
```

## 📝 Best Practices

### **Development**
- Test DAGs in development environment
- Use local executor for testing
- Validate custom operators

### **Production**
- Use Celery executor for scalability
- Set up proper monitoring
- Configure alerting
- Regular maintenance

### **Security**
- Secure Airflow UI access
- Use environment variables for secrets
- Regular security updates

## 🎯 Next Steps

1. **Setup Airflow**: Follow the Docker setup guide
2. **Configure Variables**: Set repository and email settings
3. **Test DAGs**: Run test executions
4. **Monitor**: Set up monitoring and alerting
5. **Scale**: Configure for production use

## 📚 Additional Resources

- [Airflow Documentation](https://airflow.apache.org/docs/)
- [Docker Compose Guide](https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html)
- [Custom Operators](https://airflow.apache.org/docs/apache-airflow/stable/howto/custom-operator.html)
- [Monitoring and Logging](https://airflow.apache.org/docs/apache-airflow/stable/logging-monitoring/index.html)
