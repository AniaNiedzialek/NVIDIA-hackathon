from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=NVIDIA_API_KEY
)

MODEL = "nvidia/nemotron-3-super-120b-a12b"

def chat(messages, temperature=0.7, max_tokens=2048, system_prompt=None):
    if system_prompt:
        messages = [{"role": "system", "content": system_prompt}] + messages
    
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        extra_body={
            "chat_template_kwargs": {"enable_thinking": True},
            "reasoning_budget": 4096
        }
    )
    return response.choices[0].message.content

def chat_stream(messages, temperature=0.7, system_prompt=None):
    if system_prompt:
        messages = [{"role": "system", "content": system_prompt}] + messages
    
    completion = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=temperature,
        max_tokens=4096,
        extra_body={
            "chat_template_kwargs": {"enable_thinking": True},
            "reasoning_budget": 4096
        },
        stream=True
    )
    
    for chunk in completion:
        if not chunk.choices:
            continue
        reasoning = getattr(chunk.choices[0].delta, "reasoning_content", None)
        if reasoning:
            yield {"type": "reasoning", "content": reasoning}
        if chunk.choices[0].delta.content is not None:
            yield {"type": "content", "content": chunk.choices[0].delta.content}
