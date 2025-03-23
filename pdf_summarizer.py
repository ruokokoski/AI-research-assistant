import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()

openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
#print(openrouter_api_key)

llm = ChatOpenAI(
    openai_api_key=openrouter_api_key,
    model="deepseek/deepseek-chat",
    base_url="https://openrouter.ai/api/v1",
    default_headers={
        "HTTP-Referer": "http://localhost:3000",
        "X-Title": "AI Research Assistant"
    }
)

messages = [
    SystemMessage(content="You are a helpful assistant."),
    HumanMessage(content="Tell me about summarizing texts with LangChain.")
]

response = llm.invoke(messages)

print(response.content)

'''
from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=openrouter_api_key,
    default_headers={
        "HTTP-Referer": "http://localhost:3000",
        "X-Title": "AI Research Assistant"
    }
)

response = client.chat.completions.create(
    model="deepseek/deepseek-chat",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Tell me about LangChain."}
    ]
)

print(response.choices[0].message.content)
'''