import re
from urllib.parse import quote_plus
from playwright.async_api import async_playwright, TimeoutError
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

        doi_element = await result.query_selector('a:has-text("arXiv:")')
        if doi_element:
            article['doi_link'] = await doi_element.evaluate('(element) => element.href')
        else:
            article['doi_link'] = "No link available"
 
        articles.append(article)
    
    return articles

async def search_arxiv(search_query):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        encoded_query = quote_plus(search_query)
        search_url = f"https://arxiv.org/search/?query={encoded_query}&searchtype=all&abstracts=hide&order=&size=25"

        await stealth_async(page)
        await page.goto(search_url)

        try:
            await page.wait_for_selector('li.arxiv-result', timeout=10000)
        except TimeoutError:
            await browser.close()
            return []

        articles = await extract_article_data(page)
        
        await browser.close()
        return articles