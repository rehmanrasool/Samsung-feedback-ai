# #!/usr/bin/env python3
# """
# Samsung Feedback AI - Problem Summarization Script

# This script uses GPT-based models to summarize problems from clustered feedback.
# """

# import json
# import openai
# from collections import Counter
# import logging
# from typing import List, Dict

# # Configure logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# class ProblemSummarizer:
#     def __init__(self, api_key=None):
#         """Initialize with OpenAI API key"""
#         if api_key:
#             openai.api_key = api_key
#         else:
#             logger.warning("No OpenAI API key provided. Set OPENAI_API_KEY environment variable.")
        
#         self.clustered_reviews = None
#         self.summaries = {}
    
#     def load_clustered_data(self, filename):
#         """Load clustered reviews data"""
#         logger.info(f"Loading clustered data from {filename}")
        
#         with open(f"../data/{filename}", 'r') as f:
#             self.clustered_reviews = json.load(f)
        
#         logger.info(f"Loaded {len(self.clustered_reviews)} clustered reviews")
    
#     def extract_cluster_texts(self, cluster_id):
#         """Extract all texts from a specific cluster"""
#         cluster_texts = []
#         for review in self.clustered_reviews:
#             if review.get('cluster') == cluster_id:
#                 cluster_texts.append(review.get('cleaned_text', ''))
        
#         return cluster_texts
    
#     def generate_cluster_summary(self, cluster_id, max_reviews=50):
#         """Generate summary for a specific cluster using GPT"""
#         cluster_texts = self.extract_cluster_texts(cluster_id)
        
#         if not cluster_texts:
#             return "No reviews found for this cluster"
        
#         # Limit number of reviews to avoid token limits
#         if len(cluster_texts) > max_reviews:
#             cluster_texts = cluster_texts[:max_reviews]
        
#         # Combine texts for analysis
#         combined_text = "\n".join(cluster_texts[:20])  # Use first 20 for summary
        
#         prompt = f"""
#         Analyze the following customer feedback reviews and provide a concise summary of the main problems and issues mentioned:

#         Reviews:
#         {combined_text}

#         Please provide:
#         1. Main problem themes (2-3 key issues)
#         2. Severity level (High/Medium/Low)
#         3. Affected features or components
#         4. Brief description of the impact on users

#         Format your response as a structured summary.
#         """
        
#         try:
#             response = openai.ChatCompletion.create(
#                 model="gpt-3.5-turbo",
#                 messages=[
#                     {"role": "system", "content": "You are an expert at analyzing customer feedback and identifying key problems."},
#                     {"role": "user", "content": prompt}
#                 ],
#                 max_tokens=500,
#                 temperature=0.3
#             )
            
#             summary = response.choices[0].message.content.strip()
#             logger.info(f"Generated summary for cluster {cluster_id}")
#             return summary
            
#         except Exception as e:
#             logger.error(f"Error generating summary for cluster {cluster_id}: {str(e)}")
#             return self.generate_fallback_summary(cluster_texts)
    
#     def generate_fallback_summary(self, texts):
#         """Generate basic summary without GPT when API is unavailable"""
#         if not texts:
#             return "No reviews available"
        
#         # Simple keyword extraction
#         all_words = []
#         for text in texts:
#             words = text.lower().split()
#             all_words.extend(words)
        
#         # Get most common words (excluding common stopwords)
#         stopwords = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those'}
#         filtered_words = [word for word in all_words if word not in stopwords and len(word) > 3]
        
#         common_words = Counter(filtered_words).most_common(10)
        
#         summary = f"""
#         Cluster Summary (Fallback Analysis):
#         - Number of reviews: {len(texts)}
#         - Common themes: {', '.join([word for word, count in common_words[:5]])}
#         - This cluster requires manual review for detailed analysis
#         """
        
#         return summary
    
#     def summarize_all_clusters(self):
#         """Generate summaries for all clusters"""
#         if not self.clustered_reviews:
#             logger.error("No clustered data loaded")
#             return
        
#         # Get unique cluster IDs
#         cluster_ids = set(review.get('cluster', -1) for review in self.clustered_reviews)
#         cluster_ids.discard(-1)  # Remove noise cluster
        
#         logger.info(f"Generating summaries for {len(cluster_ids)} clusters")
        
#         for cluster_id in sorted(cluster_ids):
#             cluster_size = sum(1 for review in self.clustered_reviews if review.get('cluster') == cluster_id)
#             logger.info(f"Processing cluster {cluster_id} with {cluster_size} reviews")
            
#             summary = self.generate_cluster_summary(cluster_id)
#             self.summaries[cluster_id] = {
#                 'cluster_id': cluster_id,
#                 'size': cluster_size,
#                 'summary': summary
#             }
    
#     def generate_overall_summary(self):
#         """Generate an overall summary of all problems"""
#         if not self.summaries:
#             logger.error("No cluster summaries available")
#             return
        
#         # Combine all cluster summaries
#         all_summaries = [info['summary'] for info in self.summaries.values()]
#         combined_summaries = "\n\n".join(all_summaries)
        
#         prompt = f"""
#         Based on the following cluster summaries of customer feedback, provide an executive summary of the main problems affecting Samsung products:

#         Cluster Summaries:
#         {combined_summaries}

#         Please provide:
#         1. Top 5 critical issues that need immediate attention
#         2. Overall sentiment analysis
#         3. Priority recommendations for product improvement
#         4. Estimated impact on customer satisfaction

#         Keep the summary concise and actionable.
#         """
        
#         try:
#             response = openai.ChatCompletion.create(
#                 model="gpt-3.5-turbo",
#                 messages=[
#                     {"role": "system", "content": "You are a product manager analyzing customer feedback to identify critical issues."},
#                     {"role": "user", "content": prompt}
#                 ],
#                 max_tokens=800,
#                 temperature=0.3
#             )
            
#             overall_summary = response.choices[0].message.content.strip()
#             logger.info("Generated overall summary")
#             return overall_summary
            
#         except Exception as e:
#             logger.error(f"Error generating overall summary: {str(e)}")
#             return "Overall summary generation failed. Please review individual cluster summaries."
    
#     def save_summaries(self, filename):
#         """Save all summaries to JSON file"""
#         if not self.summaries:
#             logger.error("No summaries to save")
#             return
        
#         # Add overall summary
#         overall_summary = self.generate_overall_summary()
        
#         output_data = {
#             'overall_summary': overall_summary,
#             'cluster_summaries': self.summaries,
#             'total_clusters': len(self.summaries),
#             'total_reviews': len(self.clustered_reviews) if self.clustered_reviews else 0
#         }
        
#         with open(f"../data/{filename}", 'w') as f:
#             json.dump(output_data, f, indent=2)
        
#         logger.info(f"Saved summaries to {filename}")
    
#     def print_summaries(self):
#         """Print summaries to console"""
#         if not self.summaries:
#             logger.error("No summaries available")
#             return
        
#         print("\n" + "="*80)
#         print("SAMSUNG FEEDBACK ANALYSIS - PROBLEM SUMMARIES")
#         print("="*80)
        
#         for cluster_id, info in sorted(self.summaries.items()):
#             print(f"\nCLUSTER {cluster_id} ({info['size']} reviews):")
#             print("-" * 50)
#             print(info['summary'])
        
#         print("\n" + "="*80)
#         print("OVERALL SUMMARY:")
#         print("="*80)
#         overall = self.generate_overall_summary()
#         print(overall)

# if __name__ == "__main__":
#     import os
    
#     # Initialize summarizer
#     api_key = os.getenv('OPENAI_API_KEY')
#     summarizer = ProblemSummarizer(api_key)
    
#     # Load and process data
#     summarizer.load_clustered_data("clustered_reviews.json")
#     summarizer.summarize_all_clusters()
    
#     # Save and display results
#     summarizer.save_summaries("problem_summaries.json")
#     summarizer.print_summaries()


# ------------- New Code Added.... 12 August 2025 2.41 PM 




# import json
# import re
# from langchain_ollama import ChatOllama
# from langchain.chains import LLMChain
# from langchain.prompts import PromptTemplate


# with open('data/summarize_problems.json', 'r', encoding='utf-8') as f:
#     cluster_summaries = json.load(f)


# problem_llm = ChatOllama(model="llama2")


# solution_llm = ChatOllama(model="llama2", format="json")

# problem_prompt = PromptTemplate(
#     input_variables=["input_text"],
#     template="""
# Given the following JSON cluster summary containing category, module, severity score, keywords, and feedback samples, write a concise refined problem statement summarizing the main issue.

# Input JSON: {input_text}

# Return only the refined problem statement as a single string.
# """,
# )

# # Define the solution prompt template with strict JSON instructions
# solution_prompt = PromptTemplate(
#     input_variables=["problem_statement"],
#     template="""
# You are an expert product support strategist using Monte Carlo Tree Search (MCTS) reasoning.
# Given the problem statement below, brainstorm at least three actionable solutions with an estimated solvability score (1-10).

# Problem: {problem_statement}

# Your response must consist solely of a valid JSON object in the following format. Do not include any introductory text, explanations, justifications, or additional content:
# {{
#   "solutions": [
#     {{"solution": "<detailed solution text>", "solvability_score": <int>}},
#     {{"solution": "<detailed solution text>", "solvability_score": <int>}},
#     {{"solution": "<detailed solution text>", "solvability_score": <int>}}
#   ]
# }}
# Ensure the JSON is well-formed and includes at least three solutions. The "solution" field should include the full description of the solution.
# """,
# )


# problem_chain = LLMChain(llm=problem_llm, prompt=problem_prompt, verbose=True)
# solution_chain = LLMChain(llm=solution_llm, prompt=solution_prompt, verbose=True)


# final_results = {}


# for cluster_id, cluster_data in cluster_summaries.items():

#     input_text = json.dumps(cluster_data, ensure_ascii=False)
    

#     try:
#         problem_statement = problem_chain.run(input_text).strip()
#     except Exception as e:
#         print(f"Error running problem_chain for cluster {cluster_id}: {e}")
#         problem_statement = "Failed to generate problem statement"
    
#     try:
#         solution_output = solution_chain.run(problem_statement)
#         print(f"Raw solution output for cluster {cluster_id}: {solution_output}")  # Debug output
        
#         solution_output = solution_output.strip()
#         if solution_output.startswith("```json"):
#             solution_output = solution_output[7:].strip()
#         if solution_output.endswith("```"):
#             solution_output = solution_output[:-3].strip()
        
#         try:
#             parsed_json = json.loads(solution_output)
#             solutions = parsed_json.get("solutions", [])
#             if not isinstance(solutions, list) or len(solutions) < 3:
#                 raise ValueError("Invalid solutions structure")
#         except (json.JSONDecodeError, ValueError) as parse_err:
#             print(f"Warning: JSON parsing failed for cluster {cluster_id} ({parse_err}), attempting regex fallback")
#             solutions = []
#             pattern = r'(\d+\.\s*.*?-\s*Solvability Score:\s*(\d+))\s*\*\s*Solution:\s*(.*?)(?=\s*\*\s*Justification:|\s*\d+\.|$)'
#             matches = re.findall(pattern, solution_output, re.DOTALL | re.MULTILINE)
#             for _, score, solution_text in matches:
#                 solutions.append({"solution": solution_text.strip(), "solvability_score": int(score)})
            
#             if not solutions:
#                 print(f"Warning: Regex fallback failed for cluster {cluster_id}, no solutions parsed")
         
#                 solutions = []
#     except Exception as e:
#         print(f"Error running solution_chain for cluster {cluster_id}: {e}")
#         solutions = [] 
    

#     result = {
#         "Refined Problem Statement": problem_statement,
#         "Solutions": solutions,
#         "Category": cluster_data.get("category", ""),
#         "Module": cluster_data.get("module", ""),
#         "Issue": cluster_data.get("issue", "N/A"),
#         "Impact score": cluster_data.get("severity_score", 0),
#         "Solvability score": max([s["solvability_score"] for s in solutions], default=0)
#     }
    
#     final_results[cluster_id] = result


# with open('data/refined_problem_solutions.json', 'w', encoding='utf-8') as f:
#     json.dump(final_results, f, ensure_ascii=False, indent=2)


# print(json.dumps(final_results, indent=2))



# Added code to use company's inbuilt api's to run the llm

import json
import re
import requests

# Remote LLaMA API endpoint
API_URL = "http://107.108.42.41:11434/api/generate"

def call_remote_llama(prompt):
    """
    Sends a request to the remote LLaMA API and returns the 'response' field.
    """
    payload = {
        "model": "llama3.1",  # Remote model name
        "prompt": prompt,
        "stream": False
    }
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(API_URL, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data.get("response", "").strip()
    except Exception as e:
        print(f"Error calling remote LLaMA API: {e}")
        return ""

# Load cluster summaries generated by preprocess_nlp.py
with open('data/summarize_problems.json', 'r', encoding='utf-8') as f:
    cluster_summaries = json.load(f)

final_results = {}

for cluster_id, cluster_data in cluster_summaries.items():
    input_text = json.dumps(cluster_data, ensure_ascii=False)

    # Step 1 - Generate refined problem statement
    problem_statement = call_remote_llama(
        f"""
Given the following JSON cluster summary containing category, module, severity score, keywords, and feedback samples, write a concise refined problem statement summarizing the main issue.

Input JSON: {input_text}

Return only the refined problem statement as a single string.
"""
    )

    if not problem_statement:
        problem_statement = "Failed to generate problem statement"

    # Step 2 - Generate solutions in JSON format
    solution_output = call_remote_llama(
        f"""
You are an expert product support strategist.
Given the problem statement below, brainstorm at least three actionable solutions with an estimated solvability score (1-10).

Problem: {problem_statement}

Your response must consist solely of a valid JSON object in the following format:
{{
  "solutions": [
    {{"solution": "<detailed solution text>", "solvability_score": <int>}},
    {{"solution": "<detailed solution text>", "solvability_score": <int>}},
    {{"solution": "<detailed solution text>", "solvability_score": <int>}}
  ]
}}
"""
    )

    # Try to parse JSON from the model's output
    try:
        # Remove markdown formatting if present
        if solution_output.startswith("```json"):
            solution_output = solution_output[7:].strip()
        if solution_output.endswith("```"):
            solution_output = solution_output[:-3].strip()

        parsed_json = json.loads(solution_output)
        solutions = parsed_json.get("solutions", [])
        if not isinstance(solutions, list):
            raise ValueError("Solutions is not a list")
    except Exception as e:
        print(f"Warning: Failed to parse solutions for cluster {cluster_id}: {e}")
        solutions = []

    # Prepare result for this cluster
    result = {
        "Refined Problem Statement": problem_statement,
        "Solutions": solutions,
        "Category": cluster_data.get("category", ""),
        "Module": cluster_data.get("module", ""),
        "Issue": cluster_data.get("issue", "N/A"),
        "Impact score": cluster_data.get("severity_score", 0),
        "Solvability score": max([s.get("solvability_score", 0) for s in solutions], default=0)
    }

    final_results[cluster_id] = result

# Save final results to file
with open('data/refined_problem_solutions.json', 'w', encoding='utf-8') as f:
    json.dump(final_results, f, ensure_ascii=False, indent=2)

# Print results for debug
print(json.dumps(final_results, indent=2))
