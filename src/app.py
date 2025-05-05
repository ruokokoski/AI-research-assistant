import asyncio
from os import getenv
from flask import Flask, render_template,  redirect, request, flash, session, send_file
from services.arxiv_service import search_arxiv
from services.summarizer import summarize_pdf_from_url, save_summaries
from dotenv import load_dotenv
from datetime import datetime
from collections import Counter
from uuid import uuid4
#from flask import g

SUMMARY_STORE = {}

load_dotenv()

app = Flask(__name__)
app.secret_key = getenv("SECRET_KEY")

@app.route("/")
def render_home():
    results = session.get('search_results', [])
    return render_template("index.html", results=results)

@app.route("/search", methods=["POST"])
def search():
    search_query = request.form.get("query", "")

    if not search_query:
        flash("Search field can't be empty", "danger")
        return redirect("/")

    try:
        results = asyncio.run(search_arxiv(search_query))
    except ValueError as e:
        flash(str(e), "danger")
        return redirect("/")

    if results is None or len(results) == 0:
        flash("Search didn't find anything", "warning")
        return redirect("/")

    session['search_results'] = results
    return render_template("index.html", results=results)

@app.route("/process-marked", methods=["POST"])
def process_marked():
    selected_urls = request.form.getlist('selected_articles')
    action = request.form.get("action")
    search_results = session.get('search_results', [])

    article_map = {article['pdf_url']: article for article in search_results}

    if not selected_urls:
        flash("No articles selected", "danger")
        return redirect("/")

    valid_urls = [url for url in selected_urls if url != "No PDF available"]
    
    try:
        if action == "summarize":
            summaries = []
            all_keywords = []
            for url in valid_urls:
                article = article_map.get(url)
                if not article:
                    continue
                    
                summary = summarize_pdf_from_url(url)
                summaries.append({
                    "title": article['title'],
                    "authors": ", ".join(article['authors']),
                    "year": article['year'],
                    "pdf_url": article['pdf_url'],
                    "content": summary['summary'],
                    "keywords": summary['keywords']
                })
                all_keywords.extend(summary['keywords'])
            top_keywords = [kw for kw, _ in Counter(all_keywords).most_common(5)]
            summary_id = str(uuid4())
            SUMMARY_STORE[summary_id] = summaries
            session['summary_id'] = summary_id
                
            return render_template("index.html",
                                results=search_results,
                                summarized_content=summaries,
                                top_keywords=top_keywords)
            
        elif action == "blog":
            # Implement blog post generation logic here
            pass
            
    except Exception as e:
        flash(f"Error processing articles: {str(e)}", "danger")
        return redirect("/")

@app.route("/save-summaries", methods=["POST"])
def save_summaries_route():
    summary_id = session.get('summary_id')
    if not summary_id or summary_id not in SUMMARY_STORE:
        flash("No summaries available to save", "warning")
        return redirect("/")
    
    try:
        summaries = SUMMARY_STORE[summary_id]
        output = save_summaries(summaries)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        filename = f"summaries_{timestamp}.txt"
        
        return send_file(
            output,
            as_attachment=True,
            download_name=filename,
            mimetype='text/plain'
        )
    except Exception as e:
        flash(f"Failed to save summaries: {str(e)}", "danger")
        return redirect("/")