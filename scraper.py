import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        await stealth_async(page)
        await page.goto('https://www.example.com', wait_until="domcontentloaded")

        page_title = await page.title()
        
        header = await page.query_selector('h1')
        header_text = await header.text_content() if header else "No header found"
        
        div_element = await page.query_selector('div')
        div_text = await div_element.text_content() if div_element else "No div found"
        
        print(f"\nPage Title: {page_title}")
        print(f"Main Header: {header_text}")
        print(f"Div Content: {div_text}\n")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())