from langchain_ollama import ChatOllama
from langchain.chains import LLMChain, SimpleSequentialChain
from langchain.prompts import PromptTemplate

llm = ChatOllama(model="llama2")

# Single input combining both keywords and feedback samples as a JSON string
problem_prompt = PromptTemplate(
    input_variables=["input_text"],
    template="""
Given the following JSON input containing keywords and feedback snippets, write a concise problem statement that summarizes the main issues:

Input JSON: {input_text}

Problem Statement:
""",
)

solution_prompt = PromptTemplate(
    input_variables=["problem_statement"],
    template="""
You are an expert product support agent. Given this problem statement, provide a clear and actionable solution or recommendation:

Problem: {problem_statement}

Solution:
""",
)

problem_chain = LLMChain(llm=llm, prompt=problem_prompt)
solution_chain = LLMChain(llm=llm, prompt=solution_prompt)

full_chain = SimpleSequentialChain(chains=[problem_chain, solution_chain], verbose=True)

# Combine your inputs into one JSON string to pass as a single input
import json
cluster_summaries_example = {
    "keywords": ["battery", "performance", "slow software"],
    "feedback_samples": [
        "Battery drains quickly after heavy usage.",
        "The software interface is slow and lags often."
    ]
}
input_text = json.dumps(cluster_summaries_example)

output = full_chain.run(input_text)
print(output)
