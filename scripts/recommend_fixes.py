#!/usr/bin/env python3
"""
Samsung Feedback AI - Solution Recommendation Script

This script uses GPT-based models to suggest fixes and improvements based on problem summaries.
"""

import json
import openai
import logging
from typing import List, Dict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SolutionRecommender:
    def __init__(self, api_key=None):
        """Initialize with OpenAI API key"""
        if api_key:
            openai.api_key = api_key
        else:
            logger.warning("No OpenAI API key provided. Set OPENAI_API_KEY environment variable.")
        
        self.problem_summaries = None
        self.recommendations = {}
    
    def load_problem_summaries(self, filename):
        """Load problem summaries data"""
        logger.info(f"Loading problem summaries from {filename}")
        
        with open(f"../data/{filename}", 'r') as f:
            self.problem_summaries = json.load(f)
        
        logger.info(f"Loaded summaries for {self.problem_summaries.get('total_clusters', 0)} clusters")
    
    def generate_cluster_recommendations(self, cluster_id, problem_summary):
        """Generate solution recommendations for a specific cluster"""
        
        prompt = f"""
        As a product manager and technical expert, analyze the following customer feedback problem summary and provide actionable solution recommendations:

        Problem Summary:
        {problem_summary}

        Please provide detailed recommendations including:

        1. IMMEDIATE ACTIONS (0-30 days):
           - Quick fixes that can be implemented immediately
           - Workarounds for users
           - Communication strategies

        2. SHORT-TERM SOLUTIONS (1-3 months):
           - Feature improvements
           - Bug fixes
           - Process changes

        3. LONG-TERM STRATEGIC CHANGES (3-12 months):
           - Major feature overhauls
           - System redesigns
           - Infrastructure improvements

        4. RESOURCE REQUIREMENTS:
           - Estimated development effort
           - Required team expertise
           - Budget considerations

        5. SUCCESS METRICS:
           - How to measure improvement
           - Key performance indicators
           - User satisfaction targets

        6. RISK ASSESSMENT:
           - Implementation risks
           - Potential side effects
           - Mitigation strategies

        Format your response as a structured action plan with clear priorities and timelines.
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",  # Using GPT-4 for better reasoning
                messages=[
                    {"role": "system", "content": "You are a senior product manager with expertise in mobile technology, user experience, and software development. Provide practical, actionable recommendations."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1200,
                temperature=0.2
            )
            
            recommendations = response.choices[0].message.content.strip()
            logger.info(f"Generated recommendations for cluster {cluster_id}")
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations for cluster {cluster_id}: {str(e)}")
            return self.generate_fallback_recommendations(problem_summary)
    
    def generate_fallback_recommendations(self, problem_summary):
        """Generate basic recommendations when GPT is unavailable"""
        
        fallback_recommendations = f"""
        FALLBACK RECOMMENDATIONS (Generated without AI assistance):
        
        Based on the problem summary, here are general recommendations:
        
        1. IMMEDIATE ACTIONS:
           - Acknowledge the issues publicly
           - Provide temporary workarounds to affected users
           - Set up dedicated support channels
        
        2. SHORT-TERM SOLUTIONS:
           - Conduct detailed technical analysis of reported issues
           - Prioritize fixes based on user impact
           - Implement quick wins and bug fixes
        
        3. LONG-TERM STRATEGIC CHANGES:
           - Review and improve quality assurance processes
           - Enhance user testing procedures
           - Consider architectural improvements
        
        4. RESOURCE REQUIREMENTS:
           - Assign dedicated development team
           - Allocate QA resources for thorough testing
           - Budget for potential infrastructure changes
        
        5. SUCCESS METRICS:
           - Monitor user satisfaction scores
           - Track issue resolution time
           - Measure feature adoption rates
        
        6. RISK ASSESSMENT:
           - Test all changes thoroughly before release
           - Have rollback plans ready
           - Monitor system performance post-deployment
        
        Note: This is a generic template. Manual analysis required for specific recommendations.
        
        Original Problem Summary:
        {problem_summary}
        """
        
        return fallback_recommendations
    
    def generate_all_recommendations(self):
        """Generate recommendations for all problem clusters"""
        if not self.problem_summaries:
            logger.error("No problem summaries loaded")
            return
        
        cluster_summaries = self.problem_summaries.get('cluster_summaries', {})
        
        logger.info(f"Generating recommendations for {len(cluster_summaries)} clusters")
        
        for cluster_id, cluster_info in cluster_summaries.items():
            problem_summary = cluster_info.get('summary', '')
            cluster_size = cluster_info.get('size', 0)
            
            logger.info(f"Processing cluster {cluster_id} with {cluster_size} reviews")
            
            recommendations = self.generate_cluster_recommendations(cluster_id, problem_summary)
            
            self.recommendations[cluster_id] = {
                'cluster_id': cluster_id,
                'cluster_size': cluster_size,
                'problem_summary': problem_summary,
                'recommendations': recommendations,
                'priority': self.calculate_priority(cluster_size, problem_summary)
            }
    
    def calculate_priority(self, cluster_size, problem_summary):
        """Calculate priority based on cluster size and problem severity"""
        # Simple priority calculation
        if cluster_size > 100:
            size_score = 3  # High
        elif cluster_size > 50:
            size_score = 2  # Medium
        else:
            size_score = 1  # Low
        
        # Check for severity indicators in summary
        severity_keywords = ['critical', 'severe', 'major', 'urgent', 'crash', 'failure', 'broken']
        severity_score = 1
        
        summary_lower = problem_summary.lower()
        for keyword in severity_keywords:
            if keyword in summary_lower:
                severity_score = 3
                break
        
        # Combined priority
        total_score = size_score + severity_score
        
        if total_score >= 5:
            return "HIGH"
        elif total_score >= 3:
            return "MEDIUM"
        else:
            return "LOW"
    
    def generate_executive_action_plan(self):
        """Generate overall executive action plan"""
        if not self.recommendations:
            logger.error("No recommendations available")
            return
        
        # Sort recommendations by priority
        high_priority = [r for r in self.recommendations.values() if r['priority'] == 'HIGH']
        medium_priority = [r for r in self.recommendations.values() if r['priority'] == 'MEDIUM']
        low_priority = [r for r in self.recommendations.values() if r['priority'] == 'LOW']
        
        # Create summary of all recommendations
        all_recommendations = []
        for rec in self.recommendations.values():
            all_recommendations.append(f"Cluster {rec['cluster_id']} ({rec['cluster_size']} reviews, {rec['priority']} priority):\n{rec['recommendations']}")
        
        combined_recommendations = "\n\n".join(all_recommendations)
        
        prompt = f"""
        As a Chief Product Officer, create an executive action plan based on the following detailed recommendations from customer feedback analysis:

        DETAILED RECOMMENDATIONS:
        {combined_recommendations}

        Create a comprehensive executive action plan that includes:

        1. EXECUTIVE SUMMARY
           - Key findings and critical issues
           - Overall impact on business

        2. STRATEGIC PRIORITIES
           - Top 3 initiatives that will have maximum impact
           - Resource allocation recommendations

        3. IMPLEMENTATION ROADMAP
           - 30-60-90 day action plan
           - Key milestones and deliverables

        4. BUDGET AND RESOURCES
           - Estimated investment required
           - Team structure recommendations

        5. RISK MITIGATION
           - Major risks and mitigation strategies
           - Contingency plans

        6. SUCCESS METRICS AND KPIs
           - How to measure success
           - Reporting and monitoring framework

        7. STAKEHOLDER COMMUNICATION
           - Internal communication plan
           - Customer communication strategy

        Keep the plan concise, actionable, and focused on business impact.
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a Chief Product Officer with extensive experience in product strategy, customer satisfaction, and business transformation."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.2
            )
            
            action_plan = response.choices[0].message.content.strip()
            logger.info("Generated executive action plan")
            return action_plan
            
        except Exception as e:
            logger.error(f"Error generating executive action plan: {str(e)}")
            return self.generate_fallback_action_plan()
    
    def generate_fallback_action_plan(self):
        """Generate basic action plan when GPT is unavailable"""
        high_priority_count = sum(1 for r in self.recommendations.values() if r['priority'] == 'HIGH')
        medium_priority_count = sum(1 for r in self.recommendations.values() if r['priority'] == 'MEDIUM')
        low_priority_count = sum(1 for r in self.recommendations.values() if r['priority'] == 'LOW')
        
        return f"""
        EXECUTIVE ACTION PLAN (Fallback Analysis)
        
        1. EXECUTIVE SUMMARY
           - {len(self.recommendations)} problem clusters identified
           - {high_priority_count} high priority issues requiring immediate attention
           - {medium_priority_count} medium priority issues for short-term planning
           - {low_priority_count} low priority issues for long-term consideration
        
        2. IMMEDIATE ACTIONS (Next 30 days)
           - Address all high priority issues
           - Establish crisis response team
           - Communicate with affected customers
        
        3. SHORT-TERM PLAN (30-90 days)
           - Implement fixes for medium priority issues
           - Enhance quality assurance processes
           - Improve customer feedback collection
        
        4. LONG-TERM STRATEGY (3-12 months)
           - Address systemic issues
           - Invest in preventive measures
           - Build better customer experience
        
        Note: This is a generic template. Detailed analysis with AI assistance recommended.
        """
    
    def save_recommendations(self, filename):
        """Save all recommendations to JSON file"""
        if not self.recommendations:
            logger.error("No recommendations to save")
            return
        
        # Generate executive action plan
        action_plan = self.generate_executive_action_plan()
        
        output_data = {
            'executive_action_plan': action_plan,
            'cluster_recommendations': self.recommendations,
            'priority_summary': {
                'high_priority': len([r for r in self.recommendations.values() if r['priority'] == 'HIGH']),
                'medium_priority': len([r for r in self.recommendations.values() if r['priority'] == 'MEDIUM']),
                'low_priority': len([r for r in self.recommendations.values() if r['priority'] == 'LOW'])
            },
            'total_clusters': len(self.recommendations)
        }
        
        with open(f"../data/{filename}", 'w') as f:
            json.dump(output_data, f, indent=2)
        
        logger.info(f"Saved recommendations to {filename}")
    
    def print_recommendations(self):
        """Print recommendations to console"""
        if not self.recommendations:
            logger.error("No recommendations available")
            return
        
        print("\n" + "="*100)
        print("SAMSUNG FEEDBACK AI - SOLUTION RECOMMENDATIONS")
        print("="*100)
        
        # Print by priority
        for priority in ['HIGH', 'MEDIUM', 'LOW']:
            priority_recs = [r for r in self.recommendations.values() if r['priority'] == priority]
            if priority_recs:
                print(f"\n{priority} PRIORITY ISSUES ({len(priority_recs)} clusters):")
                print("="*80)
                
                for rec in sorted(priority_recs, key=lambda x: x['cluster_size'], reverse=True):
                    print(f"\nCLUSTER {rec['cluster_id']} ({rec['cluster_size']} reviews):")
                    print("-" * 60)
                    print("PROBLEM:")
                    print(rec['problem_summary'][:200] + "..." if len(rec['problem_summary']) > 200 else rec['problem_summary'])
                    print("\nRECOMMENDATIONS:")
                    print(rec['recommendations'])
                    print("\n" + "="*60)
        
        # Print executive action plan
        print("\n" + "="*100)
        print("EXECUTIVE ACTION PLAN:")
        print("="*100)
        action_plan = self.generate_executive_action_plan()
        print(action_plan)

if __name__ == "__main__":
    import os
    
    # Initialize recommender
    api_key = os.getenv('OPENAI_API_KEY')
    recommender = SolutionRecommender(api_key)
    
    # Load and process data
    recommender.load_problem_summaries("problem_summaries.json")
    recommender.generate_all_recommendations()
    
    # Save and display results
    recommender.save_recommendations("solution_recommendations.json")
    recommender.print_recommendations()
