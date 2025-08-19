# gemini_client.py
import google.generativeai as genai
import json
import re
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key from environment
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini AI
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    llm_model = genai.GenerativeModel("gemini-2.0-flash-lite")
else:
    llm_model = None
    print("Warning: GEMINI_API_KEY not found in .env file")

def categorize_task(task_description):
    """
    Simple function to categorize a task using Gemini AI
    Returns category and priority
    """
    prompt = f"""
    Categorize the following task into a category (Work, Study, Personal, Health) and
    assign a priority (High, Medium, Low). 
    Return the response as **only valid JSON**,  Strictly following this format:
    {{
        "category": "Work/Study/Personal/Health",
        "priority": "High/Medium/Low"
    }}
    Task: "{task_description}"
    """
    
    response = llm_model.generate_content(prompt)
    content = response.text.strip()
    try:
        match = re.search(r'\{.*\}', content, re.DOTALL)
        if match:
            content = match.group(0)
        else:
            print("No Valid JSON found in response, using default values.")
            return "Personal", "Medium"
        task_data = json.loads(content)
        return task_data.get("category", "Personal"), task_data.get("priority", "Medium")
    except Exception as e:
        print(f"Error parsing response: {e}")
        return "Personal", "Medium"