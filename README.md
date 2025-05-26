# AI-research-assistant

Flask app for scraping research articles, summarizing them with LLMs, and auto-generating blog posts.  
The main goal of this project is to build a web-based AI research assistant powered by LLMs.  
The scripts `pdf_summarizer.py` and `scraper.py` are initial tests and tools for exploring the backend functionality.

## Documents
- [Project plan](./docs/AI_Research_Assistant.md)

---

## 🚀 Flask App

The main application is a Flask app located in `src/`. To start it:

1. Activate the Poetry environment:
```bash
poetry shell
```

2. Run:
```bash
python3 src/index.py
```

This will start the app on:
http://localhost:5001

## Setup

This project uses [Poetry](https://python-poetry.org/) for dependency management and virtual environments.

Make sure Poetry is installed. If not, install by running (Linux or macOS):

```bash
curl -sSL https://install.python-poetry.org | POETRY_HOME=$HOME/.local python3 -
```

Then install all project dependencies:
```bash
poetry install
```

Download and install browser binaries:
```bash
poetry run playwright install
```

Activate the virtual environment:
```bash
poetry shell
```

Set your OpenRouter API key in a `.env` file:
```bash
OPENROUTER_API_KEY=your_api_key_here
```

Set your own SECRET_KEY in a `.env` file:
```bash
SECRET_KEY=your_key_here
```

## Usage: `pdf_summarizer.py`

The `pdf_summarizer.py` automatically summarizes all PDF files in a chosen folder using a large language model via the OpenRouter API. It extracts metadata (title and authors), splits the text into manageable chunks, and generates concise summaries.

Each summary is:
- Printed in the terminal
- Saved to a timestamped text file in the same folder

### Run the script
```bash
python3 pdf_summarizer.py
```

## Usage: `scraper.py`

The `scraper.py` searches arXiv.org for academic papers using a provided keyword or phrase, extracts metadata (title, authors, year, PDF link), and optionally downloads and summarizes the PDFs using an LLM via the OpenRouter API.

Main features:
- Performs a stealth search using Playwright on arXiv
- Lists article metadata and PDF links
- Allows summarizing a selected number of articles (if PDFs are available)
- Prints summaries directly to the terminal

### Run the script
```bash
python3 scraper.py "your search query"
```