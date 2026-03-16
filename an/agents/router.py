import json
from utils.nvidia_client import chat

ROUTER_PROMPT = """You are an SJSU AI Counselor Router. Your job is to understand student questions and route them to the appropriate specialist agent.

Available agents:
- registrar: Course enrollment, transcripts, graduation requirements, add/drop courses, degree worksheets
- career: Career advice, electives selection, internships, job opportunities, professional development
- compliance: F-1 visa status, minimum units for maintaining status, I-20 requirements, work authorization
- general: Questions that don't fit the above categories

Analyze the student's question and respond with JSON only (no other text):
{"agent": "agent_name", "reason": "brief explanation"}"""

def route_question(question: str) -> dict:
    messages = [{"role": "user", "content": question}]
    result = chat(messages, temperature=0.3, system_prompt=ROUTER_PROMPT)
    
    try:
        return json.loads(result)
    except json.JSONDecodeError:
        return {"agent": "general", "reason": "Could not parse, defaulting to general"}
