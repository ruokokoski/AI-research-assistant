# AI Research Assistant Project

This outlines the development of an AI Research Assistant capable of:

- **Searching** ACM and arXiv databases based on user queries.
- **Scraping** article details such as authors, titles, publication years, citation counts, and PDF links.
- **Summarizing** each article using a Large Language Model (LLM).
- **Rating** the relevance of each article.
- **Generating** new search keywords based on retrieved articles.
- **Composing** a blog post synthesizing the retrieved articles.

## 1. Define Requirements & Tech Stack

- **Backend Framework:** Choose between Node.js (with Express) or Python (with Flask or FastAPI) for building API endpoints.
- **Web Scraping:** Utilize tools like Puppeteer, Selenium or Playwright for rendering pages and extracting article details.
- **LLM Integration:** Implement LangChain with OpenAI API (or another LLM provider) for tasks such as summarization, rating, keyword extraction, and blog post generation.
- **Database:** Use a database to cache search results and embeddings. Consider a vector store (e.g., Chroma, FAISS, Pinecone) if planning on semantic retrieval.
- **Frontend:** Develop a minimal user interface using frameworks like React, Vue, or Python Flask to collect user queries and display results.

## 2. High-Level Steps

### User Query Input

- Develop a user interface where users can input their research queries.
- Send these queries to the backend API.

### Search API Integration

- Utilize ACM and arXiv APIs (or construct search URLs) to fetch initial search results.
- If APIs are unavailable or limited, generate search URLs for both sources.

### Page Rendering & Web Scraping

- Launch a headless browser (using Puppeteer, Selenium or Playwright) to load search result pages.
- Scrape rendered pages to extract:
  - Article title
  - Authors
  - Publication year
  - Citation count
  - PDF Link
- Store these details in an intermediate data structure.

### Article Summarization & Rating

- For each article, send PDF to an LLM chain to:
  - Summarize the article.
  - Rate its quality (e.g., "High relevance", "Moderate relevance", "Low relevance").
- Cache the summary and rating.

### Keyword Extraction & Search Suggestions

- Analyze the article details (or summaries) to extract frequent keywords.
- Generate a list of new search terms using the LLM.

### Blog Post Generation

- Use the retrieved articles and their summaries to create a cohesive blog post.
- This can be achieved through an LLM chain that compiles the summaries into a structured blog post.

### Return Results to User

- Combine article details, summaries, ratings, keyword suggestions, and the blog post.
- Return these as a JSON response or render them in the user interface.

### Error Handling & Logging

- Implement error logging at each step.
- Provide fallback messages if a component fails.

### (Optional) Persistence & Caching

- Cache search results and LLM outputs in a database or vector store to avoid repeated API calls.

## 3. Project Diagram

```mermaid
graph TD
  A[User enters research query] --> B[Backend API receives query]
  B --> C[ACM/arXiv Search]
  C --> D[Form search URL or use API]
  D --> E[Headless Browser renders page]
  E --> F[Web Scraper extracts article details]
  F --> G[LLM Chain: Summarize & Rate articles]
  G --> H[LLM Chain: Extract keywords & generate suggestions]
  H --> I[LLM Chain: Generate blog post]
  I --> J[Combine results]
  J --> K[Return response to UI]

## 4. Additional Features for the AI Research Assistant

- **Interactive Q&A on Retrieved Articles::**
  Enable users to ask questions about the fetched articles. Implement vector-based semantic search on the scraped article content (titles, abstracts, or full text) by embedding the data and storing it in a vector database.

- **Search News Articles:**
  Extend the search query to also fetch recent news articles from reputable news providers. This allows the assistant to present up-to-date information and context alongside academic research.
  
- **Citation Management:**  
  Automatically format and export citations (e.g., APA, BibTex) for the retrieved articles.

- **Collaboration Tools:**  
  Enable users to save, annotate, and share research summaries and blog posts.

- **Interactive Q&A:**  
  Allow users to ask follow-up questions about specific articles, with the assistant providing deeper insights.

- **Visual Summaries:**  
  Generate infographics or visual summaries (e.g., charts of publication years, citation trends) based on the data.

- **Citation Network Analysis:**
  Visual paper connections, key influential papers
  
- **Personalized Recommendations:**
  Similar papers, related researchers
  
---

## 5. Getting Started

### Prototype the Backend

- Initiate a simple Express, FastAPI or Flask project.
- Implement an endpoint for a test query.
- Add web scraping capabilities using Puppeteer, Selenium or Playwright.
- Integrate a basic LLM chain for summarization using LangChain.

### Develop the User Interface

- Create a basic interface using React or Flask (a similar framework) for entering queries and displaying results.
- Connect the UI to the backend API.

### Iterate and Expand

- Add additional endpoints for:
  - Keyword extraction
  - Blog post generation
- Implement caching mechanisms and robust error handling.
- Refine LLM prompts to improve:
  - Summarization quality
  - Rating accuracy

### Test and Deploy

- Conduct local testing for each individual component.
- Deploy the backend (e.g., to **Fly.io**).
- Deploy the frontend (e.g., to **Vercel** or **Netlify**).

### Template for Research Analyzer Class

```python
import spacy
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

class ResearchAnalyzer:
    def __init__(self, llm, config):
       self.llm
       self.nlp 
       self.config
    
    def search_articles(self, query):
      # Construct ACM/arXiv API/search URLs
      # Launch headless browser & scrape metadata
      return articles_metadata, pdf_urls
      
    def extract_pdf_content(self, pdf_url):
        # Extract text and metadata from PDF
        response = requests.get(pdf_url, stream=True)
        return text
    
    def summarize_article(self, text):
        # LLM-powered summary
        summary = "Generated summary of the article."
        return summary

    def rate_relevance(self, text, metadata):
        # LLM for text, metadata: citation count, journal prestige, year
        relevance_score = #e.g. high, moderate, low
        return relevance_score

    def generate_keywords(self, content):
        # Hybrid NLP+LLM keyword extraction
        keywords = ["keyword1", "keyword2", "keyword3"]
        return keywords
        
    def generate_blog(self, all_articles):
        # LLM-based blog generation
        return blog_post
        
    def aggregate_keywords(self, all_articles):
        # Combine keywords from retrieved articles
        return search_suggestions
        
    def cache_results(self, articles):
        # Store results in DB/vector store
    
    def check_cache(self, query):
        # Check for existing cached results

