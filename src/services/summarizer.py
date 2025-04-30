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
    
    chain = load_summarize_chain(llm, chain_type="map_reduce")
    return chain.invoke(split_docs)['output_text']