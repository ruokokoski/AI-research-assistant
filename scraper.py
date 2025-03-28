import os
import asyncio
import sys
import re
import requests
import fitz
from io import BytesIO
from urllib.parse import quote_plus
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async
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

async def extract_article_data(page):
    articles = []
    results = await page.query_selector_all('li.arxiv-result')
    
    for result in results:
        article = {}
        
        title_element = await result.query_selector('p.title.is-5.mathjax')
        article['title'] = (await title_element.text_content()).strip() if title_element else "No title"
        
        authors_element = await result.query_selector('p.authors')
        if authors_element:
            author_links = await authors_element.query_selector_all('a')
            article['authors'] = [await link.text_content() for link in author_links]
        else:
            article['authors'] = []
        
        date_element = await result.query_selector('p.is-size-7')
        if date_element:
            date_text = await date_element.text_content()
            year_match = re.search(r'Submitted.*?(\d{4})', date_text)
            article['year'] = year_match.group(1) if year_match else "Unknown"
        else:
            article['year'] = "Unknown"
        
        pdf_element = await result.query_selector('a:has-text("pdf")')
        if pdf_element:
            article['pdf_url'] = await pdf_element.evaluate('(element) => element.href')
        else:
            article['pdf_url'] = "No PDF available"
        
        articles.append(article)
    
    return articles

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

async def run(search_query):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        encoded_query = quote_plus(search_query)
        search_url = f"https://arxiv.org/search/?query={encoded_query}&searchtype=all&abstracts=hide&order=&size=25"

        await stealth_async(page)
        await page.goto(search_url)

        await page.wait_for_selector('li.arxiv-result', timeout=10000)

        articles = await extract_article_data(page)
        
        print(f"\nFound {len(articles)} articles:")
        for idx, article in enumerate(articles, 1):
            print(f"\nArticle {idx}:")
            print(f"Title: {article['title']}")
            print(f"Authors: {', '.join(article['authors'])}")
            print(f"Year: {article['year']}")
            print(f"PDF: {article['pdf_url']}")

        if not articles:
            print("\n🔎 No articles found for this search query")
            await browser.close()
            return

        while True:
            choice = input("\nSummarize articles? (y/n): ").strip().lower()
            if choice in ['y', 'n']:
                break
            print("Invalid input. Please enter 'y' or 'n'")
        
        if choice == 'n':
            await browser.close()
            return

        max_articles = min(len(articles), 25)
        while True:
            try:
                num = int(input(f"How many articles to summarize? (1-{max_articles}): "))
                if 1 <= num <= max_articles:
                    break
                print(f"Please enter a number between 1 and {max_articles}")
            except ValueError:
                print("Invalid input. Please enter a number")

        successful = 0
        for i in range(num):
            article = articles[i]
            if article['pdf_url'] == "No PDF available":
                print(f"\n⚠️ Article {i+1} has no PDF available")
                continue
            
            try:
                print(f"\n📄 Processing PDF {i+1}/{num}: {article['pdf_url']}")
                summary = summarize_pdf_from_url(article['pdf_url'])
                print(f"\nTitle: {article['title']}")
                print(f"Year: {article['year']}")
                print(f"Authors: {', '.join(article['authors'])}")
                print(f"\nSummary:\n{summary}")
                print("-" * 80)
                successful += 1
            except Exception as e:
                print(f"\n❌ Error processing article {i+1}: {str(e)}")

        print(f"\n✅ Successfully summarized {successful}/{num} articles")
        await browser.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 scraper.py \"search phrase\"")
        sys.exit(1)
        
    search_words = ' '.join(sys.argv[1:])
    asyncio.run(run(search_words))