#!/usr/bin/env python3
"""
Standalone Data Quality Checks for GitHub Issues
Python functions that can be used outside of Airflow
Author: d.pyasi42@gmail.com
"""

import logging
from typing import Dict, Any, Optional
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_data_quality(
    table_name: str,
    min_records: int = 100,
    max_null_percentage: float = 0.05,
    spark_session: Optional[SparkSession] = None
) -> Dict[str, Any]:
    """
    Standalone data quality check function
    
    Args:
        table_name: Name of the table to check
        min_records: Minimum number of records required
        max_null_percentage: Maximum percentage of nulls allowed
        spark_session: Optional Spark session (creates new if None)
    
    Returns:
        Dictionary with quality metrics and results
    """
    try:
        # Initialize Spark session if not provided
        if spark_session is None:
            spark = SparkSession.builder \
                .appName("DataQualityCheck") \
                .getOrCreate()
        else:
            spark = spark_session
        
        try:
            # Load data
            df = spark.table(table_name)
            
            # Basic quality checks
            total_records = df.count()
            null_ids = df.filter(F.col("id").isNull()).count()
            null_titles = df.filter(F.col("title").isNull()).count()
            
            # Calculate null percentages
            id_null_pct = (null_ids / total_records) if total_records > 0 else 0
            title_null_pct = (null_titles / total_records) if total_records > 0 else 0
            
            # Check for recent data
            recent_data = df.filter(
                F.col("created_at") >= F.current_date() - F.expr("INTERVAL 7 DAYS")
            ).count()
            
            # Quality metrics
            quality_metrics = {
                "total_records": total_records,
                "null_ids": null_ids,
                "null_titles": null_titles,
                "id_null_percentage": id_null_pct,
                "title_null_percentage": title_null_pct,
                "recent_records": recent_data
            }
            
            logger.info(f"Data Quality Check Results: {quality_metrics}")
            
            # Quality checks
            quality_results = {
                "passed": True,
                "errors": [],
                "warnings": [],
                "metrics": quality_metrics
            }
            
            # Check minimum records
            if total_records < min_records:
                error_msg = f"Too few records: {total_records} < {min_records}"
                quality_results["errors"].append(error_msg)
                quality_results["passed"] = False
                logger.error(error_msg)
            
            # Check null IDs
            if id_null_pct > max_null_percentage:
                error_msg = f"Too many null IDs: {id_null_pct:.2%} > {max_null_percentage:.2%}"
                quality_results["errors"].append(error_msg)
                quality_results["passed"] = False
                logger.error(error_msg)
            
            # Check null titles
            if title_null_pct > max_null_percentage:
                error_msg = f"Too many null titles: {title_null_pct:.2%} > {max_null_percentage:.2%}"
                quality_results["errors"].append(error_msg)
                quality_results["passed"] = False
                logger.error(error_msg)
            
            # Check data freshness (warning only)
            if recent_data < 10:
                warning_msg = f"Low recent data count: {recent_data} (last 7 days)"
                quality_results["warnings"].append(warning_msg)
                logger.warning(warning_msg)
            
            return quality_results
            
        finally:
            if spark_session is None:
                spark.stop()
                
    except Exception as e:
        logger.error(f"Error in data quality check: {e}")
        return {
            "passed": False,
            "errors": [f"Data quality check failed: {e}"],
            "warnings": [],
            "metrics": {}
        }

def check_schema_compliance(
    table_name: str,
    expected_schema: Dict[str, str],
    spark_session: Optional[SparkSession] = None
) -> Dict[str, Any]:
    """
    Check if table schema matches expected schema
    
    Args:
        table_name: Name of the table to check
        expected_schema: Dictionary of expected column names and types
        spark_session: Optional Spark session
    
    Returns:
        Dictionary with schema compliance results
    """
    try:
        if spark_session is None:
            spark = SparkSession.builder \
                .appName("SchemaComplianceCheck") \
                .getOrCreate()
        else:
            spark = spark_session
        
        try:
            # Get actual schema
            df = spark.table(table_name)
            actual_schema = {field.name: str(field.dataType) for field in df.schema}
            
            # Check schema compliance
            compliance_results = {
                "passed": True,
                "missing_columns": [],
                "type_mismatches": [],
                "extra_columns": [],
                "actual_schema": actual_schema,
                "expected_schema": expected_schema
            }
            
            # Check for missing columns
            for col_name, expected_type in expected_schema.items():
                if col_name not in actual_schema:
                    compliance_results["missing_columns"].append(col_name)
                    compliance_results["passed"] = False
                elif actual_schema[col_name] != expected_type:
                    compliance_results["type_mismatches"].append({
                        "column": col_name,
                        "expected": expected_type,
                        "actual": actual_schema[col_name]
                    })
                    compliance_results["passed"] = False
            
            # Check for extra columns
            for col_name in actual_schema:
                if col_name not in expected_schema:
                    compliance_results["extra_columns"].append(col_name)
            
            return compliance_results
            
        finally:
            if spark_session is None:
                spark.stop()
                
    except Exception as e:
        logger.error(f"Error in schema compliance check: {e}")
        return {
            "passed": False,
            "errors": [f"Schema compliance check failed: {e}"],
            "actual_schema": {},
            "expected_schema": expected_schema
        }

def check_data_freshness(
    table_name: str,
    days_threshold: int = 7,
    spark_session: Optional[SparkSession] = None
) -> Dict[str, Any]:
    """
    Check data freshness (how recent the data is)
    
    Args:
        table_name: Name of the table to check
        days_threshold: Number of days to check for recent data
        spark_session: Optional Spark session
    
    Returns:
        Dictionary with freshness results
    """
    try:
        if spark_session is None:
            spark = SparkSession.builder \
                .appName("DataFreshnessCheck") \
                .getOrCreate()
        else:
            spark = spark_session
        
        try:
            df = spark.table(table_name)
            
            # Check recent data
            recent_data = df.filter(
                F.col("created_at") >= F.current_date() - F.expr(f"INTERVAL {days_threshold} DAYS")
            ).count()
            
            # Check latest record date
            latest_date = df.agg(F.max("created_at")).collect()[0][0]
            
            freshness_results = {
                "passed": recent_data > 0,
                "recent_records": recent_data,
                "latest_date": latest_date,
                "days_threshold": days_threshold,
                "is_fresh": recent_data > 0
            }
            
            if recent_data == 0:
                freshness_results["warning"] = f"No data from last {days_threshold} days"
            
            return freshness_results
            
        finally:
            if spark_session is None:
                spark.stop()
                
    except Exception as e:
        logger.error(f"Error in data freshness check: {e}")
        return {
            "passed": False,
            "error": f"Data freshness check failed: {e}"
        }

def run_comprehensive_quality_check(
    table_name: str,
    min_records: int = 100,
    max_null_percentage: float = 0.05,
    expected_schema: Optional[Dict[str, str]] = None,
    days_threshold: int = 7
) -> Dict[str, Any]:
    """
    Run comprehensive data quality checks
    
    Args:
        table_name: Name of the table to check
        min_records: Minimum number of records required
        max_null_percentage: Maximum percentage of nulls allowed
        expected_schema: Expected schema (optional)
        days_threshold: Days threshold for freshness check
    
    Returns:
        Dictionary with comprehensive quality results
    """
    try:
        # Initialize Spark session
        spark = SparkSession.builder \
            .appName("ComprehensiveQualityCheck") \
            .getOrCreate()
        
        try:
            # Run all quality checks
            quality_results = check_data_quality(
                table_name, min_records, max_null_percentage, spark
            )
            
            schema_results = None
            if expected_schema:
                schema_results = check_schema_compliance(
                    table_name, expected_schema, spark
                )
            
            freshness_results = check_data_freshness(
                table_name, days_threshold, spark
            )
            
            # Combine results
            comprehensive_results = {
                "overall_passed": True,
                "quality_check": quality_results,
                "schema_check": schema_results,
                "freshness_check": freshness_results,
                "summary": {
                    "total_checks": 3 if expected_schema else 2,
                    "passed_checks": 0,
                    "failed_checks": 0
                }
            }
            
            # Count passed/failed checks
            if quality_results["passed"]:
                comprehensive_results["summary"]["passed_checks"] += 1
            else:
                comprehensive_results["summary"]["failed_checks"] += 1
                comprehensive_results["overall_passed"] = False
            
            if schema_results and schema_results["passed"]:
                comprehensive_results["summary"]["passed_checks"] += 1
            elif schema_results:
                comprehensive_results["summary"]["failed_checks"] += 1
                comprehensive_results["overall_passed"] = False
            
            if freshness_results["passed"]:
                comprehensive_results["summary"]["passed_checks"] += 1
            else:
                comprehensive_results["summary"]["failed_checks"] += 1
                comprehensive_results["overall_passed"] = False
            
            return comprehensive_results
            
        finally:
            spark.stop()
            
    except Exception as e:
        logger.error(f"Error in comprehensive quality check: {e}")
        return {
            "overall_passed": False,
            "error": f"Comprehensive quality check failed: {e}"
        }

def main():
    """
    Example usage of data quality checks
    """
    # Example usage
    table_name = "loungebip_test.internal.huggingface_transformers_issues"
    
    # Expected schema for GitHub issues
    expected_schema = {
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
    
    # Run comprehensive quality check
    results = run_comprehensive_quality_check(
        table_name=table_name,
        min_records=100,
        max_null_percentage=0.05,
        expected_schema=expected_schema,
        days_threshold=7
    )
    
    print("Comprehensive Quality Check Results:")
    print(f"Overall Passed: {results['overall_passed']}")
    print(f"Passed Checks: {results['summary']['passed_checks']}")
    print(f"Failed Checks: {results['summary']['failed_checks']}")
    
    if not results['overall_passed']:
        print("\nIssues found:")
        if not results['quality_check']['passed']:
            print("Quality Check Issues:", results['quality_check']['errors'])
        if results['schema_check'] and not results['schema_check']['passed']:
            print("Schema Issues:", results['schema_check']['missing_columns'])
        if not results['freshness_check']['passed']:
            print("Freshness Issues:", results['freshness_check'].get('warning', 'No recent data'))

if __name__ == "__main__":
    main()
