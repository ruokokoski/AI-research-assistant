# AI-research-assistant

## Setup

This project uses [Poetry](https://python-poetry.org/) for dependency management and virtual environments.

### Install dependencies

Make sure Poetry is installed:

```bash
pip install poetry
```

Then install all project dependencies:
```bash
poetry install
```

Activate the virtual environment:
```bash
poetry shell
```

Set your OpenRouter API key in a `.env` file:
```bash
OPENROUTER_API_KEY=your_api_key_here
```

## Documents
- [Project plan](./docs/AI_Research_Assistant.md)

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