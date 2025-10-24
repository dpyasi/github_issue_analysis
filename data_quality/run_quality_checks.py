#!/usr/bin/env python3
"""
Standalone script to run data quality checks
Author: d.pyasi42@gmail.com
"""

import sys
import os
from data_quality_checks import run_comprehensive_quality_check

def main():
    """
    Run data quality checks on the GitHub issues table
    """
    # Configuration
    TABLE_NAME = "loungebip_test.internal.huggingface_transformers_issues"
    
    # Expected schema for GitHub issues
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
    
    print("🔍 Running Data Quality Checks...")
    print("=" * 50)
    
    try:
        # Run comprehensive quality check
        results = run_comprehensive_quality_check(
            table_name=TABLE_NAME,
            min_records=100,
            max_null_percentage=0.05,
            expected_schema=EXPECTED_SCHEMA,
            days_threshold=7
        )
        
        # Display results
        print(f"📊 Overall Result: {'✅ PASSED' if results['overall_passed'] else '❌ FAILED'}")
        print(f"📈 Checks Passed: {results['summary']['passed_checks']}")
        print(f"📉 Checks Failed: {results['summary']['failed_checks']}")
        
        # Quality check details
        quality = results['quality_check']
        print(f"\n🔍 Data Quality Check:")
        print(f"  Total Records: {quality['metrics'].get('total_records', 0):,}")
        print(f"  Null IDs: {quality['metrics'].get('null_ids', 0)} ({quality['metrics'].get('id_null_percentage', 0):.2%})")
        print(f"  Null Titles: {quality['metrics'].get('null_titles', 0)} ({quality['metrics'].get('title_null_percentage', 0):.2%})")
        print(f"  Recent Records: {quality['metrics'].get('recent_records', 0)}")
        
        if quality['errors']:
            print(f"  ❌ Errors: {', '.join(quality['errors'])}")
        if quality['warnings']:
            print(f"  ⚠️  Warnings: {', '.join(quality['warnings'])}")
        
        # Schema check details
        if results['schema_check']:
            schema = results['schema_check']
            print(f"\n📋 Schema Compliance Check:")
            if schema['missing_columns']:
                print(f"  ❌ Missing Columns: {', '.join(schema['missing_columns'])}")
            if schema['type_mismatches']:
                print(f"  ❌ Type Mismatches: {len(schema['type_mismatches'])}")
                for mismatch in schema['type_mismatches']:
                    print(f"    - {mismatch['column']}: expected {mismatch['expected']}, got {mismatch['actual']}")
            if schema['extra_columns']:
                print(f"  ℹ️  Extra Columns: {', '.join(schema['extra_columns'])}")
        
        # Freshness check details
        freshness = results['freshness_check']
        print(f"\n⏰ Data Freshness Check:")
        print(f"  Recent Records (7 days): {freshness.get('recent_records', 0)}")
        print(f"  Latest Date: {freshness.get('latest_date', 'Unknown')}")
        print(f"  Is Fresh: {'✅ Yes' if freshness.get('is_fresh', False) else '❌ No'}")
        
        if 'warning' in freshness:
            print(f"  ⚠️  Warning: {freshness['warning']}")
        
        # Summary
        if results['overall_passed']:
            print(f"\n🎉 All quality checks passed!")
            return 0
        else:
            print(f"\n💥 Quality checks failed!")
            return 1
            
    except Exception as e:
        print(f"❌ Error running quality checks: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
