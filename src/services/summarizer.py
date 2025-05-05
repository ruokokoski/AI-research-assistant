import os
import requests
import fitz
from io import BytesIO
from langchain_openai import ChatOpenAI
from langchain.chains.summarize import load_summarize_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
import tiktoken
from dotenv import load_dotenv
from datetime import datetime

from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
#from collections import Counter

load_dotenv()

llm = ChatOpenAI(
    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
    model="deepseek/deepseek-chat:free",
    base_url="https://openrouter.ai/api/v1",
    default_headers={
        "HTTP-Referer": "http://localhost:3000",
        "X-Title": "AI Research Assistant"
    }
)

def summarize_pdf_from_url(pdf_url):
    response = requests.get(pdf_url)
    response.raise_for_status()
    
    pdf_data = BytesIO(response.content)
    doc = fitz.open(stream=pdf_data, filetype="pdf")
    
    text = ""
    metadata = doc.metadata
    for page in doc:
        text += page.get_text()
        if not metadata:
            metadata.update(page.metadata)
    
    encoding = tiktoken.get_encoding("cl100k_base")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=8000,
        chunk_overlap=400,
        length_function=lambda text: len(encoding.encode(text)),
        separators=["\n\n", "\n"]
    )
    
    docs = [Document(page_content=text, metadata=metadata)]
    split_docs = text_splitter.split_documents(docs)

    summary_chain = load_summarize_chain(llm, chain_type="map_reduce")
    summary = summary_chain.invoke(split_docs)['output_text']
    doc_keywords = extract_keywords(summary)

    return {
        'summary': summary,
        'keywords': doc_keywords
    }

def extract_keywords(text):
    keyword_template = """Extract the 3-5 most important technical keywords from the text below. 
    Return ONLY a comma-separated list of keywords, nothing else.
    Avoid common words. Use lowercase for all keywords.

    TEXT: {text}

    KEYWORDS:"""
    
    keyword_prompt = PromptTemplate(
        template=keyword_template,
        input_variables=["text"]
    )
    keyword_chain = LLMChain(llm=llm, prompt=keyword_prompt)
    keywords_str = keyword_chain.run(text)
    
    return [kw.strip().lower() for kw in keywords_str.split(",") if kw.strip()]

def save_summaries(summaries):
    output = BytesIO()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    output.write(f"Research Summaries ({timestamp})\n".encode('utf-8'))
    output.write("="*50 + b"\n\n")
    
    for summary in summaries:
        output.write(f"Title: {summary['title']}\n".encode('utf-8'))
        output.write(f"Authors: {summary['authors']}\n".encode('utf-8'))
        output.write(f"Year: {summary['year']}\n".encode('utf-8'))
        output.write(f"PDF URL: {summary['pdf_url']}\n".encode('utf-8'))
        output.write("\nSummary:\n".encode('utf-8'))
        output.write(f"{summary['content']}\n".encode('utf-8'))
        output.write("\n" + "="*50 + "\n\n".encode('utf-8'))
    
    output.seek(0)
    return output