import os
import google.generativeai as genai
from typing import List, Dict

# Assumes GEMINI_API_KEY is set in the environment
def init_gemini():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Warning: GEMINI_API_KEY not set. LLM features will not work.")
        return None
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-1.5-flash')

def generate_prose(beat: str, memory_context: List[Dict], stats: Dict) -> str:
    """Agentic Workflow Phase 3: Strategic Planning -> Prose Execution"""
    model = init_gemini()
    if not model:
        return "Error: LLM not configured."

    context_str = "Story Context:\n"
    for item in memory_context:
        context_str += f"- {item['content']}\n"

    prompt = f"""
You are an expert fiction writer. You are writing a chapter for a story.
Here is the memory context retrieved from the Codex:
{context_str}

Story Stats (for reference):
{stats}

Now, write a compelling prose execution for the following narrative beat:
BEAT: {beat}

Write only the prose.
"""
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating prose: {str(e)}"
