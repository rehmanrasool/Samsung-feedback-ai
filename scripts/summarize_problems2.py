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
        response = requests.post(API_URL, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get("response", "").strip()
    except Exception as e:
        print(f"Error calling remote LLaMA API: {e}")
        return ""

# Load cluster summaries
with open('data/summarize_problems.json', 'r', encoding='utf-8') as f:
    cluster_summaries = json.load(f)

final_results = {}

for cluster_id, cluster_data in cluster_summaries.items():
    input_text = json.dumps(cluster_data, ensure_ascii=False)

    # Step 1: Get refined problem statement
    problem_prompt = f"""
Given the following JSON cluster summary containing category, module, severity score, keywords, and feedback samples, write a concise refined problem statement summarizing the main issue.

Input JSON: {input_text}

Return ONLY the refined problem statement as a single string. Do NOT include any extra words like "Here is" or "Sure,".
"""
    problem_statement = call_remote_llama(problem_prompt)
    if not problem_statement:
        problem_statement = "Failed to generate problem statement"
    else:
        problem_statement = re.sub(r"^(Sure,.*?:|Here is.*?:)\s*\n*", "", problem_statement).strip()

    # Step 2: Get solutions
    solution_prompt = f"""
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
    solution_output = call_remote_llama(solution_prompt)

    # Parse solutions JSON with fallback
    solutions = []
    try:
        if solution_output.startswith("```json"):
            solution_output = solution_output[7:].strip()
        if solution_output.endswith("```"):
            solution_output = solution_output[:-3].strip()

        parsed_json = json.loads(solution_output)
        solutions = parsed_json.get("solutions", [])
        if not isinstance(solutions, list) or len(solutions) < 3:
            raise ValueError("Invalid solutions format")
    except Exception as e:
        print(f"Warning: JSON parsing failed for cluster {cluster_id} ({e}), attempting regex fallback")
        pattern = r'"solution":\s*"([^"]+)",\s*"solvability_score":\s*(\d+)'
        matches = re.findall(pattern, solution_output)
        for sol, score in matches:
            solutions.append({"solution": sol.strip(), "solvability_score": int(score)})

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

# Save results
with open('data/refined_problem_solutions.json', 'w', encoding='utf-8') as f:
    json.dump(final_results, f, ensure_ascii=False, indent=2)

print(json.dumps(final_results, indent=2))
