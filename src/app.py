import asyncio
from os import getenv
from flask import Flask, render_template,  redirect, request, flash, session, send_file
from services.arxiv_service import search_arxiv
from services.summarizer import summarize_pdf_from_url, save_summaries
from dotenv import load_dotenv
from datetime import datetime
from uuid import uuid4
import tempfile
import requests
import zipfile
import os
from io import BytesIO


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
    session['last_query'] = search_query
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
                    "content": summary['summary'],
                    "keywords": summary['keywords']
                })

            summary_id = str(uuid4())
            SUMMARY_STORE[summary_id] = summaries
            session['summary_id'] = summary_id
                
            return render_template("index.html",
                                   results=search_results,
                                   summarized_content=summaries)
        
        elif action == "download":
            try:
                with tempfile.TemporaryDirectory() as tmpdirname:
                    zip_buffer = BytesIO()
                    with zipfile.ZipFile(zip_buffer, 'w') as zipf:
                        for url in valid_urls:
                            article = article_map.get(url)
                            if not article:
                                continue

                            response = requests.get(url)
                            if response.status_code == 200:
                                first_author = article['authors'][0].split()[-1]
                                year = article.get('year', 'unknown')
                                title = article['title']
                                safe_title = "".join(c if c.isalnum() or c in (' ', '_') else '_' for c in title).replace(' ', '_')
                                filename = f"{first_author}_{year}_{safe_title}.pdf"
                                filepath = os.path.join(tmpdirname, filename)
                                with open(filepath, 'wb') as f:
                                    f.write(response.content)
                                zipf.write(filepath, arcname=filename)

                    zip_buffer.seek(0)
                    timestamp = datetime.now().strftime("%Y%m%d")

                    return send_file(
                        zip_buffer,
                        mimetype='application/zip',
                        as_attachment=True,
                        download_name=f'articles_{timestamp}.zip'
                    )
            except Exception as e:
                flash(f"Failed to download PDFs: {str(e)}", "danger")
                return redirect("/")

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
        query = session.get('last_query', 'N/A')
        output = save_summaries(summaries, query)
        
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