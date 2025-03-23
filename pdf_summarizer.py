import os
import time
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
#from langchain_core.messages import HumanMessage, SystemMessage
#from langchain_core.prompts import PromptTemplate
from langchain.chains.summarize import load_summarize_chain
from langchain_community.document_loaders import PyMuPDFLoader

load_dotenv()

openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
current_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(current_dir, "pdfs", "Garza2023-TimeGPT.pdf")

if not os.path.exists(file_path):
    raise FileNotFoundError(
        f"The file {file_path} does not exist. Please check the path."
    )

llm = ChatOpenAI(
        openai_api_key=openrouter_api_key,
        model="deepseek/deepseek-chat",
        base_url="https://openrouter.ai/api/v1",
        default_headers={
            "HTTP-Referer": "http://localhost:3000",
            "X-Title": "AI Research Assistant"
        }
    )

def summarize_pdf(file_path):
    loader = PyMuPDFLoader(file_path)
    docs = loader.load_and_split()

    chain = load_summarize_chain(llm, chain_type="map_reduce")
    summary = chain.invoke(docs)

    return summary

if __name__ == "__main__":
    start_time = time.time()

    summary = summarize_pdf(file_path)

    end_time = time.time()

    elapsed_time = end_time - start_time
    print(f"Time taken: {elapsed_time:.2f} seconds\n")

    print('Summary:')
    print(summary['output_text'])