import asyncio
from os import getenv
from flask import Flask, render_template,  redirect, request, flash, session
from services.arxiv_service import search_arxiv
from dotenv import load_dotenv

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
