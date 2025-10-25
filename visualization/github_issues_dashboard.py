#!/usr/bin/env python3
"""
GitHub Issues Analytics Dashboard
Interactive visualizations for GitHub issues data
Author: d.pyasi42@gmail.com
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GitHubIssuesDashboard:
    """
    Interactive dashboard for GitHub issues analytics
    """
    
    def __init__(self):
        # Use existing Spark session in Databricks
        try:
            self.spark = spark  # Databricks provides 'spark' variable
        except NameError:
            # Fallback for local development
            self.spark = SparkSession.builder \
                .appName("GitHubIssuesDashboard") \
                .config("spark.sql.adaptive.enabled", "true") \
                .getOrCreate()
        
        # Streamlit page config
        st.set_page_config(
            page_title="GitHub Issues Analytics",
            page_icon="📊",
            layout="wide"
        )
    
    def load_data(self, table_name: str = "loungebip_test.internal.huggingface_transformers_issues"):
        """
        Load data from the issues table
        """
        try:
            df = self.spark.table(table_name)
            return df
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            return None
    
    def create_issues_over_time_chart(self, df):
        """
        Create issues over time chart
        """
        try:
            # Aggregate by date
            daily_issues = df.groupBy(F.date_format("created_at", "yyyy-MM-dd").alias("date")) \
                            .agg(F.count("*").alias("issues_count")) \
                            .orderBy("date")
            
            # Convert to Pandas for plotting
            daily_pd = daily_issues.toPandas()
            
            # Create line chart
            fig = px.line(
                daily_pd, 
                x="date", 
                y="issues_count",
                title="Issues Created Over Time",
                labels={"date": "Date", "issues_count": "Number of Issues"}
            )
            
            fig.update_layout(
                xaxis_title="Date",
                yaxis_title="Number of Issues",
                hovermode="x unified"
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating issues over time chart: {e}")
            return None
    
    def create_state_distribution_chart(self, df):
        """
        Create issues state distribution pie chart
        """
        try:
            # Count by state
            state_counts = df.groupBy("state").count().orderBy("count")
            state_pd = state_counts.toPandas()
            
            # Create pie chart
            fig = px.pie(
                state_pd,
                values="count",
                names="state",
                title="Issues by State",
                color_discrete_map={"open": "#ff6b6b", "closed": "#4ecdc4"}
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating state distribution chart: {e}")
            return None
    
    def create_top_contributors_chart(self, df):
        """
        Create top contributors bar chart
        """
        try:
            # Count by user
            contributors = df.groupBy("user_login").count() \
                            .orderBy(F.desc("count")) \
                            .limit(20)
            contributors_pd = contributors.toPandas()
            
            # Create horizontal bar chart
            fig = px.bar(
                contributors_pd,
                x="count",
                y="user_login",
                orientation="h",
                title="Top 20 Contributors by Issue Count",
                labels={"count": "Number of Issues", "user_login": "Contributor"}
            )
            
            fig.update_layout(yaxis={'categoryorder': 'total ascending'})
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating top contributors chart: {e}")
            return None
    
    def create_labels_analysis(self, df):
        """
        Create labels analysis chart
        """
        try:
            # Explode labels array and count
            labels_df = df.select(F.explode("labels").alias("label")) \
                         .groupBy("label") \
                         .count() \
                         .orderBy(F.desc("count")) \
                         .limit(15)
            
            labels_pd = labels_df.toPandas()
            
            # Create bar chart
            fig = px.bar(
                labels_pd,
                x="label",
                y="count",
                title="Top 15 Labels by Usage",
                labels={"count": "Number of Issues", "label": "Label"}
            )
            
            fig.update_layout(xaxis_tickangle=-45)
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating labels analysis chart: {e}")
            return None
    
    def create_monthly_trends(self, df):
        """
        Create monthly trends analysis
        """
        try:
            # Aggregate by month
            monthly_data = df.groupBy(
                F.date_format("created_at", "yyyy-MM").alias("month"),
                "state"
            ).count().orderBy("month")
            
            monthly_pd = monthly_data.toPandas()
            
            # Create grouped bar chart
            fig = px.bar(
                monthly_pd,
                x="month",
                y="count",
                color="state",
                title="Monthly Issues Trends",
                labels={"count": "Number of Issues", "month": "Month"},
                barmode="group"
            )
            
            fig.update_layout(xaxis_tickangle=-45)
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating monthly trends chart: {e}")
            return None
    
    def create_summary_metrics(self, df):
        """
        Create summary metrics cards
        """
        try:
            # Calculate metrics
            total_issues = df.count()
            open_issues = df.filter(F.col("state") == "open").count()
            closed_issues = df.filter(F.col("state") == "closed").count()
            
            # Calculate pull requests
            pr_count = df.filter(F.col("pull_request").isNotNull()).count()
            
            # Calculate average comments
            avg_comments = df.agg(F.avg("comments")).collect()[0][0] or 0
            
            # Get date range
            date_range = df.agg(
                F.min("created_at").alias("min_date"),
                F.max("created_at").alias("max_date")
            ).collect()[0]
            
            return {
                "total_issues": total_issues,
                "open_issues": open_issues,
                "closed_issues": closed_issues,
                "pull_requests": pr_count,
                "avg_comments": round(avg_comments, 2),
                "date_range": date_range
            }
            
        except Exception as e:
            logger.error(f"Error calculating summary metrics: {e}")
            return {}
    
    def run_dashboard(self):
        """
        Run the Streamlit dashboard
        """
        st.title("📊 GitHub Issues Analytics Dashboard")
        st.markdown("---")
        
        # Load data
        with st.spinner("Loading data..."):
            df = self.load_data()
        
        if df is None:
            st.error("Failed to load data. Please check your table connection.")
            return
        
        # Summary metrics
        st.subheader("📈 Summary Metrics")
        metrics = self.create_summary_metrics(df)
        
        if metrics:
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric("Total Issues", f"{metrics['total_issues']:,}")
            
            with col2:
                st.metric("Open Issues", f"{metrics['open_issues']:,}")
            
            with col3:
                st.metric("Closed Issues", f"{metrics['closed_issues']:,}")
            
            with col4:
                st.metric("Pull Requests", f"{metrics['pull_requests']:,}")
            
            with col5:
                st.metric("Avg Comments", f"{metrics['avg_comments']}")
        
        st.markdown("---")
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Issues over time
            st.subheader("📅 Issues Created Over Time")
            time_chart = self.create_issues_over_time_chart(df)
            if time_chart:
                st.plotly_chart(time_chart, use_container_width=True)
            
            # State distribution
            st.subheader("🥧 Issues by State")
            state_chart = self.create_state_distribution_chart(df)
            if state_chart:
                st.plotly_chart(state_chart, use_container_width=True)
        
        with col2:
            # Top contributors
            st.subheader("👥 Top Contributors")
            contributors_chart = self.create_top_contributors_chart(df)
            if contributors_chart:
                st.plotly_chart(contributors_chart, use_container_width=True)
            
            # Labels analysis
            st.subheader("🏷️ Top Labels")
            labels_chart = self.create_labels_analysis(df)
            if labels_chart:
                st.plotly_chart(labels_chart, use_container_width=True)
        
        # Monthly trends (full width)
        st.subheader("📊 Monthly Trends")
        monthly_chart = self.create_monthly_trends(df)
        if monthly_chart:
            st.plotly_chart(monthly_chart, use_container_width=True)
        
        # Data table
        st.subheader("📋 Recent Issues")
        recent_issues = df.select(
            "number", "title", "state", "user_login", 
            "created_at", "comments"
        ).orderBy(F.desc("created_at")).limit(100)
        
        recent_pd = recent_issues.toPandas()
        st.dataframe(recent_pd, use_container_width=True)

def main():
    """
    Main function to run the dashboard
    """
    dashboard = GitHubIssuesDashboard()
    dashboard.run_dashboard()

if __name__ == "__main__":
    main()
