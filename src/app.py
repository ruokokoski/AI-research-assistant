import asyncio
from os import getenv
from flask import Flask, render_template,  redirect, request, flash, session, send_file
from services.arxiv_service import search_arxiv
from services.summarizer import summarize_pdf_from_url, save_summaries
from dotenv import load_dotenv
from datetime import datetime

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
                    "content": summary
                })
            session['summarized_content'] = summaries
                
            return render_template("index.html",
                                results=search_results,
                                summarized_content=summaries)
            
        elif action == "blog":
            # Implement blog post generation logic here
            pass
            
    except Exception as e:
        flash(f"Error processing articles: {str(e)}", "danger")
        return redirect("/")

@app.route("/save-summaries", methods=["POST"])
def save_summaries():
    if 'summarized_content' not in session:
        flash("No summaries available to save", "warning")
        return redirect("/")
    
    try:
        summaries = session['summarized_content']
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