from utils.nvidia_client import chat, chat_stream

REGISTRAR_PROMPT = """You are the SJSU Registrar AI Assistant. You help students with:
- Course enrollment and registration
- Transcript requests
- Graduation requirements and deadlines
- Add/drop courses
- Degree worksheets and requirements
- Prerequisites and course equivalencies

Always be helpful, accurate, and direct. If you don't know something, say so.
Current academic year: 2025-2026"""

def handle_registrar_question(question: str, stream: bool = False):
    messages = [{"role": "user", "content": question}]
    
    if stream:
        return chat_stream(messages, system_prompt=REGISTRAR_PROMPT)
    return chat(messages, system_prompt=REGISTRAR_PROMPT)
