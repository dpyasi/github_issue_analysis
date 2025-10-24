# Data Quality Checks - Standalone Python Functions

## 🎯 Overview

These are **standalone Python functions** that you can use outside of Airflow for data quality checks on your GitHub issues table.

## 📁 Files

- **`data_quality_checks.py`** - Core quality check functions
- **`run_quality_checks.py`** - Standalone script to run checks
- **`README.md`** - This documentation

## 🚀 Quick Start

### **Run Quality Checks**
```bash
# Navigate to data quality directory
cd data_quality

# Run quality checks
python run_quality_checks.py
```

### **Use in Your Code**
```python
from data_quality_checks import check_data_quality, run_comprehensive_quality_check

# Simple quality check
results = check_data_quality(
    table_name="loungebip_test.internal.huggingface_transformers_issues",
    min_records=100,
    max_null_percentage=0.05
)

# Comprehensive quality check
results = run_comprehensive_quality_check(
    table_name="loungebip_test.internal.huggingface_transformers_issues",
    min_records=100,
    max_null_percentage=0.05,
    expected_schema={
        "id": "LongType",
        "title": "StringType",
        "state": "StringType"
    },
    days_threshold=7
)
```

## 🔍 Available Functions

### **1. `check_data_quality()`**
Basic data quality checks:
- **Record count validation**
- **Null ID checks**
- **Null title checks**
- **Data freshness warnings**

### **2. `check_schema_compliance()`**
Schema validation:
- **Missing columns detection**
- **Type mismatches identification**
- **Extra columns detection**

### **3. `check_data_freshness()`**
Data freshness validation:
- **Recent data check**
- **Latest record date**
- **Freshness threshold validation**

### **4. `run_comprehensive_quality_check()`**
All-in-one quality check:
- **Combines all checks**
- **Comprehensive reporting**
- **Overall pass/fail result**

## 📊 Quality Check Results

### **Example Output:**
```
🔍 Running Data Quality Checks...
==================================================
📊 Overall Result: ✅ PASSED
📈 Checks Passed: 3
📉 Checks Failed: 0

🔍 Data Quality Check:
  Total Records: 1,250
  Null IDs: 0 (0.00%)
  Null Titles: 5 (0.40%)
  Recent Records: 45

📋 Schema Compliance Check:
  ✅ All columns present
  ✅ All types match

⏰ Data Freshness Check:
  Recent Records (7 days): 45
  Latest Date: 2024-01-15 10:30:00
  Is Fresh: ✅ Yes

🎉 All quality checks passed!
```

## 🛠️ Configuration

### **Quality Thresholds:**
```python
# Strict (Production)
min_records=500
max_null_percentage=0.01  # 1%

# Lenient (Development)
min_records=50
max_null_percentage=0.10  # 10%
```

### **Expected Schema:**
```python
EXPECTED_SCHEMA = {
    "id": "LongType",
    "number": "IntegerType",
    "title": "StringType",
    "state": "StringType",
    "created_at": "TimestampType",
    "closed_at": "TimestampType",
    "updated_at": "TimestampType",
    "user_login": "StringType",
    "assignees": "ArrayType(StringType,true)",
    "labels": "ArrayType(StringType,true)",
    "comments": "IntegerType",
    "milestone_title": "StringType",
    "pull_request": "StructType",
    "body": "StringType"
}
```

## 🔧 Usage Examples

### **Basic Quality Check:**
```python
from data_quality_checks import check_data_quality

results = check_data_quality("your_table_name")
if results["passed"]:
    print("✅ Data quality is good!")
else:
    print("❌ Data quality issues found:", results["errors"])
```

### **Schema Validation:**
```python
from data_quality_checks import check_schema_compliance

expected_schema = {"id": "LongType", "title": "StringType"}
results = check_schema_compliance("your_table_name", expected_schema)
if results["passed"]:
    print("✅ Schema is compliant!")
else:
    print("❌ Schema issues:", results["missing_columns"])
```

### **Comprehensive Check:**
```python
from data_quality_checks import run_comprehensive_quality_check

results = run_comprehensive_quality_check(
    table_name="your_table_name",
    min_records=100,
    max_null_percentage=0.05,
    expected_schema=expected_schema,
    days_threshold=7
)

print(f"Overall Result: {'PASSED' if results['overall_passed'] else 'FAILED'}")
```

## 📈 Integration

### **With ETL Pipeline:**
```python
# In your ETL script
from data_quality_checks import check_data_quality

# After loading data
quality_results = check_data_quality("your_table_name")
if not quality_results["passed"]:
    raise Exception(f"Data quality check failed: {quality_results['errors']}")
```

### **With Airflow:**
```python
# In Airflow DAG
from data_quality_checks import run_comprehensive_quality_check

def quality_check_task(**context):
    results = run_comprehensive_quality_check("your_table_name")
    if not results["overall_passed"]:
        raise Exception("Quality check failed")
    return results
```

## 🚨 Error Handling

### **Common Issues:**
1. **Table not found** - Check table name and permissions
2. **Spark session issues** - Ensure Spark is properly configured
3. **Schema mismatches** - Verify expected schema matches actual

### **Debugging:**
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Run with detailed output
results = run_comprehensive_quality_check("your_table_name")
print("Detailed results:", results)
```

## 📝 Notes

- **Standalone**: These functions work outside of Airflow
- **Reusable**: Can be imported and used in any Python script
- **Configurable**: All thresholds and parameters are adjustable
- **Comprehensive**: Covers data quality, schema, and freshness
- **Production-ready**: Includes proper error handling and logging
