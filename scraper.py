import asyncio
import sys
import re
from urllib.parse import quote_plus
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async

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

        await browser.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 scraper.py \"search phrase\"")
        sys.exit(1)
        
    search_words = ' '.join(sys.argv[1:])
    asyncio.run(run(search_words))