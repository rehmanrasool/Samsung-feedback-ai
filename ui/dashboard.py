#!/usr/bin/env python3
"""
Samsung Feedback AI - Streamlit Dashboard

This dashboard provides an interactive interface for viewing feedback analysis results.
"""

import streamlit as st
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime
import os

# Configure Streamlit page
st.set_page_config(
    page_title="Samsung Feedback AI Dashboard",
    page_icon="��",
    layout="wide",
    initial_sidebar_state="expanded"
)

class FeedbackDashboard:
    def __init__(self):
        self.data_path = "../data/"
        self.raw_reviews = None
        self.processed_reviews = None
        self.clustered_reviews = None
        self.problem_summaries = None
        self.recommendations = None
    
    def load_data(self):
        """Load all available data files"""
        try:
            # Load raw reviews if available
            if os.path.exists(f"{self.data_path}raw_reviews.json"):
                with open(f"{self.data_path}raw_reviews.json", 'r') as f:
                    self.raw_reviews = json.load(f)
            
            # Load processed reviews if available
            if os.path.exists(f"{self.data_path}processed_reviews.json"):
                with open(f"{self.data_path}processed_reviews.json", 'r') as f:
                    self.processed_reviews = json.load(f)
            
            # Load clustered reviews if available
            if os.path.exists(f"{self.data_path}clustered_reviews.json"):
                with open(f"{self.data_path}clustered_reviews.json", 'r') as f:
                    self.clustered_reviews = json.load(f)
            
            # Load problem summaries if available
            if os.path.exists(f"{self.data_path}problem_summaries.json"):
                with open(f"{self.data_path}problem_summaries.json", 'r') as f:
                    self.problem_summaries = json.load(f)
            
            # Load recommendations if available
            if os.path.exists(f"{self.data_path}solution_recommendations.json"):
                with open(f"{self.data_path}solution_recommendations.json", 'r') as f:
                    self.recommendations = json.load(f)
                    
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
    
    def show_overview(self):
        """Display overview metrics"""
        st.header("📊 Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if self.raw_reviews:
                st.metric("Total Reviews", len(self.raw_reviews))
            else:
                st.metric("Total Reviews", "No data")
        
        with col2:
            if self.clustered_reviews:
                clusters = set(review.get('cluster', -1) for review in self.clustered_reviews)
                clusters.discard(-1)  # Remove noise cluster
                st.metric("Problem Clusters", len(clusters))
            else:
                st.metric("Problem Clusters", "No data")
        
        with col3:
            if self.recommendations:
                high_priority = self.recommendations.get('priority_summary', {}).get('high_priority', 0)
                st.metric("High Priority Issues", high_priority)
            else:
                st.metric("High Priority Issues", "No data")
        
        with col4:
            if self.processed_reviews:
                avg_rating = np.mean([r.get('rating', 0) for r in self.processed_reviews if r.get('rating', 0) > 0])
                st.metric("Average Rating", f"{avg_rating:.1f}" if not np.isnan(avg_rating) else "No data")
            else:
                st.metric("Average Rating", "No data")
    
    def show_cluster_analysis(self):
        """Display cluster analysis"""
        st.header("🎯 Cluster Analysis")
        
        if not self.clustered_reviews:
            st.warning("No clustered data available. Please run the clustering script first.")
            return
        
        # Create cluster distribution chart
        cluster_data = {}
        for review in self.clustered_reviews:
            cluster_id = review.get('cluster', -1)
            if cluster_id != -1:  # Exclude noise
                cluster_data[cluster_id] = cluster_data.get(cluster_id, 0) + 1
        
        if cluster_data:
            # Cluster size distribution
            fig = px.bar(
                x=list(cluster_data.keys()),
                y=list(cluster_data.values()),
                title="Reviews per Cluster",
                labels={'x': 'Cluster ID', 'y': 'Number of Reviews'}
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Cluster details table
            if self.problem_summaries:
                cluster_summaries = self.problem_summaries.get('cluster_summaries', {})
                
                cluster_df = []
                for cluster_id, size in cluster_data.items():
                    summary_info = cluster_summaries.get(str(cluster_id), {})
                    cluster_df.append({
                        'Cluster ID': cluster_id,
                        'Size': size,
                        'Summary': summary_info.get('summary', 'No summary available')[:100] + '...'
                    })
                
                df = pd.DataFrame(cluster_df)
                st.dataframe(df, use_container_width=True)
    
    def show_problem_summaries(self):
        """Display problem summaries"""
        st.header("📋 Problem Summaries")
        
        if not self.problem_summaries:
            st.warning("No problem summaries available. Please run the summarization script first.")
            return
        
        # Overall summary
        overall_summary = self.problem_summaries.get('overall_summary', '')
        if overall_summary:
            st.subheader("Executive Summary")
            st.write(overall_summary)
        
        # Individual cluster summaries
        cluster_summaries = self.problem_summaries.get('cluster_summaries', {})
        
        if cluster_summaries:
            st.subheader("Cluster Summaries")
            
            for cluster_id, info in cluster_summaries.items():
                with st.expander(f"Cluster {cluster_id} ({info.get('size', 0)} reviews)"):
                    st.write(info.get('summary', 'No summary available'))
    
    def show_recommendations(self):
        """Display solution recommendations"""
        st.header("💡 Solution Recommendations")
        
        if not self.recommendations:
            st.warning("No recommendations available. Please run the recommendation script first.")
            return
        
        # Executive action plan
        action_plan = self.recommendations.get('executive_action_plan', '')
        if action_plan:
            st.subheader("Executive Action Plan")
            st.write(action_plan)
        
        # Priority summary
        priority_summary = self.recommendations.get('priority_summary', {})
        if priority_summary:
            st.subheader("Priority Distribution")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("High Priority", priority_summary.get('high_priority', 0), delta_color="inverse")
            with col2:
                st.metric("Medium Priority", priority_summary.get('medium_priority', 0))
            with col3:
                st.metric("Low Priority", priority_summary.get('low_priority', 0))
        
        # Detailed recommendations by priority
        cluster_recommendations = self.recommendations.get('cluster_recommendations', {})
        
        if cluster_recommendations:
            st.subheader("Detailed Recommendations")
            
            # Group by priority
            priorities = ['HIGH', 'MEDIUM', 'LOW']
            for priority in priorities:
                priority_recs = {k: v for k, v in cluster_recommendations.items() if v.get('priority') == priority}
                
                if priority_recs:
                    st.write(f"### {priority} Priority Issues ({len(priority_recs)} clusters)")
                    
                    for cluster_id, rec in priority_recs.items():
                        with st.expander(f"Cluster {cluster_id} ({rec.get('cluster_size', 0)} reviews)"):
                            st.write("**Problem Summary:**")
                            st.write(rec.get('problem_summary', 'No summary available'))
                            
                            st.write("**Recommendations:**")
                            st.write(rec.get('recommendations', 'No recommendations available'))
    
    def show_data_explorer(self):
        """Display raw data explorer"""
        st.header("🔍 Data Explorer")
        
        # Data selection
        data_type = st.selectbox(
            "Select data to explore:",
            ["Raw Reviews", "Processed Reviews", "Clustered Reviews"]
        )
        
        if data_type == "Raw Reviews" and self.raw_reviews:
            df = pd.DataFrame(self.raw_reviews)
            st.dataframe(df, use_container_width=True)
            
        elif data_type == "Processed Reviews" and self.processed_reviews:
            # Remove embeddings for display (too large)
            display_data = []
            for review in self.processed_reviews:
                display_review = {k: v for k, v in review.items() if k != 'embedding'}
                display_data.append(display_review)
            
            df = pd.DataFrame(display_data)
            st.dataframe(df, use_container_width=True)
            
        elif data_type == "Clustered Reviews" and self.clustered_reviews:
            # Remove embeddings for display
            display_data = []
            for review in self.clustered_reviews:
                display_review = {k: v for k, v in review.items() if k != 'embedding'}
                display_data.append(display_review)
            
            df = pd.DataFrame(display_data)
            
            # Add cluster filter
            if 'cluster' in df.columns:
                clusters = sorted(df['cluster'].unique())
                selected_cluster = st.selectbox("Filter by cluster:", ['All'] + [str(c) for c in clusters])
                
                if selected_cluster != 'All':
                    df = df[df['cluster'] == int(selected_cluster)]
            
            st.dataframe(df, use_container_width=True)
        else:
            st.warning(f"No {data_type.lower()} data available.")
    
    def show_analytics(self):
        """Display advanced analytics"""
        st.header("📈 Analytics")
        
        if not self.clustered_reviews:
            st.warning("No data available for analytics.")
            return
        
        # Rating distribution
        ratings = [r.get('rating', 0) for r in self.clustered_reviews if r.get('rating', 0) > 0]
        if ratings:
            fig = px.histogram(
                x=ratings,
                nbins=5,
                title="Rating Distribution",
                labels={'x': 'Rating', 'y': 'Count'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Source distribution
        sources = [r.get('source', 'unknown') for r in self.clustered_reviews]
        source_counts = pd.Series(sources).value_counts()
        
        if len(source_counts) > 0:
            fig = px.pie(
                values=source_counts.values,
                names=source_counts.index,
                title="Reviews by Source"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Cluster vs Rating analysis
        if 'cluster' in [r.keys() for r in self.clustered_reviews][0]:
            cluster_ratings = {}
            for review in self.clustered_reviews:
                cluster_id = review.get('cluster', -1)
                rating = review.get('rating', 0)
                if cluster_id != -1 and rating > 0:
                    if cluster_id not in cluster_ratings:
                        cluster_ratings[cluster_id] = []
                    cluster_ratings[cluster_id].append(rating)
            
            if cluster_ratings:
                avg_ratings = {k: np.mean(v) for k, v in cluster_ratings.items()}
                
                fig = px.bar(
                    x=list(avg_ratings.keys()),
                    y=list(avg_ratings.values()),
                    title="Average Rating by Cluster",
                    labels={'x': 'Cluster ID', 'y': 'Average Rating'}
                )
                st.plotly_chart(fig, use_container_width=True)

def main():
    """Main dashboard function"""
    st.title("📱 Samsung Feedback AI Dashboard")
    st.markdown("---")
    
    # Initialize dashboard
    dashboard = FeedbackDashboard()
    dashboard.load_data()
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page:",
        ["Overview", "Cluster Analysis", "Problem Summaries", "Recommendations", "Analytics", "Data Explorer"]
    )
    
    # Display selected page
    if page == "Overview":
        dashboard.show_overview()
    elif page == "Cluster Analysis":
        dashboard.show_cluster_analysis()
    elif page == "Problem Summaries":
        dashboard.show_problem_summaries()
    elif page == "Recommendations":
        dashboard.show_recommendations()
    elif page == "Analytics":
        dashboard.show_analytics()
    elif page == "Data Explorer":
        dashboard.show_data_explorer()
    
    # Footer
    st.markdown("---")
    st.markdown("*Samsung Feedback AI Dashboard - Powered by Streamlit*")

if __name__ == "__main__":
    main()
