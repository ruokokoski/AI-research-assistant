import warnings
warnings.filterwarnings("ignore", message="Unexpected type for token usage")

import os
import time
from datetime import datetime
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.chains.summarize import load_summarize_chain
from langchain_community.document_loaders import PyMuPDFLoader

load_dotenv()

def get_folder():
    while True:
        folder_path = input("Enter path to PDF folder: ").strip()
        if os.path.isdir(folder_path):
            return os.path.abspath(folder_path)
        print(f"Error: '{folder_path}' is not a valid directory. Try again.")

def process_folder(folder_path):
    pdf_files = [file for file in os.listdir(folder_path) 
                if file.lower().endswith('.pdf')]
    
    summaries = []
    for idx, pdf_file in enumerate(pdf_files, 1):
        file_path = os.path.join(folder_path, pdf_file)
        try:
            print(f"\nProcessing {idx}/{len(pdf_files)}: {pdf_file}")
            authors, title, summary = summarize_pdf(file_path)
            summaries.append({
                "title": title,
                "authors": authors,
                "content": summary['output_text'],
                "source": pdf_file
            })
        except Exception as e:
            print(f"Failed to process {pdf_file}: {str(e)}")
    
    return summaries

def summarize_pdf(file_path):
    loader = PyMuPDFLoader(file_path)
    docs = loader.load_and_split()
    metadata = docs[0].metadata
    authors = metadata.get("author") or "-"
    title = metadata.get("title") or "-"

    chain = load_summarize_chain(llm, chain_type="map_reduce")
    summary = chain.invoke(docs)

    return authors, title, summary

def print_summaries(summaries):
    print("\n" + "="*80)
    print("GENERATED SUMMARIES".center(80))
    print("="*80 + "\n")
    
    for idx, summary in enumerate(summaries, 1):
        print(f"Summary {idx}: {summary['source']}")
        print("-"*80)
        print(f"Title: {summary['title']}")
        print(f"Authors: {summary['authors']}")
        print("\nSummary Content:")
        print(summary['content'])
        print("\n" + "="*80 + "\n")

def save_summaries(summaries, folder_path):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    output_file = os.path.join(folder_path, f"summaries_{timestamp}.txt")
    
    with open(output_file, 'w', encoding='utf-8') as file:
        for summary in summaries:
            file.write(f"Title: {summary['title']}\n")
            file.write(f"Authors: {summary['authors']}\n")
            file.write(f"Source: {summary['source']}\n")
            file.write("Summary:\n" + summary['content'] + "\n")
            file.write("\n" + "="*80 + "\n")
    
    print(f"\nSaved {len(summaries)} summaries to {output_file}")

def print_summaries():
    pdf_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.pdf')]
    print("\nSummary statistics:")
    print(f"- Total PDFs found: {len(pdf_files)}")
    print(f"- Successfully processed: {len(summaries)}")
    print(f"- Failed: {len(pdf_files) - len(summaries)}")

if __name__ == "__main__":
    llm = ChatOpenAI(
        openai_api_key=os.getenv("OPENROUTER_API_KEY"),
        model="deepseek/deepseek-chat",
        base_url="https://openrouter.ai/api/v1",
        default_headers={
            "HTTP-Referrer": "http://localhost:3000",
            "X-Title": "AI Research Assistant"
        }
    )
    start_time = time.time()

    folder_path = get_folder()
    summaries = process_folder(folder_path)

    if summaries:
        print_summaries(summaries)
        save_summaries(summaries, folder_path)
        print_summaries()
    else:
        print("No valid PDFs processed.")
    
    print(f"\nProcessing time: {time.time() - start_time:.2f} seconds")