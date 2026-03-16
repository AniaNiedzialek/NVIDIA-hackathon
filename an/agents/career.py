from utils.nvidia_client import chat, chat_stream

CAREER_PROMPT = """You are the SJSU Career Advisor AI Assistant. You help students with:
- Career exploration and planning
- Elective course selection for career goals
- Internship opportunities
- Resume and interview prep
- Job market trends
- Professional development
- Connecting majors to career paths

Provide actionable, practical advice. Current year: 2026"""

def handle_career_question(question: str, stream: bool = False):
    messages = [{"role": "user", "content": question}]
    
    if stream:
        return chat_stream(messages, system_prompt=CAREER_PROMPT)
    return chat(messages, system_prompt=CAREER_PROMPT)
