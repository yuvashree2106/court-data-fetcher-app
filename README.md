I created a working, single-file proof-of-concept web app you can run immediately that implements the UI, storage, parsing pipeline, PDF download, and cause-list download flow. The file is in the canvas as “Ecourts-case-fetcher-flask” and contains:

What I gave you

A full app.py-style Flask single-file app (in the canvas) that:

Presents a simple UI form (Case Type, Case Number, Year, Court selection).

Stores each query and raw response in SQLite (SQLAlchemy).

Has a pluggable BaseScraper architecture and a DummyScraper that demonstrates the full flow (parsing, storing, generating a demo PDF).

Saves PDFs to a pdfs/ folder and serves them for download.

A cause-list endpoint that demonstrates storing/downloading a cause-list PDF.

An example API endpoint /api/fetch for programmatic calls.

Error handling for common failure cases and explicit comments showing where/ how to implement real scrapers.

Why a dummy scraper?

eCourts portals differ across High Courts and District Courts; many pages are JavaScript-driven or use different search endpoints. To give you a runnable end-to-end demo right away, I implemented a DummyScraper and a robust scaffold with clear, commented instructions and extension points where you plug in real scrapers (requests/BeautifulSoup for static pages or Selenium/Playwright for JS-heavy pages).

How to extend to real courts

Implement a subclass of BaseScraper for each court (or group of courts) you want to support, for example DelhiHighCourtScraper, KarnatakaHighCourtScraper, DistrictCourtXYZScraper.

Two approaches:

requests + BeautifulSoup — for pages that render server-side and return HTML/JSON.

Selenium / Playwright — for pages that require JS interaction, form tokens, or dynamic requests (fill fields, click search, wait for results).

In your fetch implementation:

Search the court portal using the fields (case_type, case_number, year).

Parse parties’ names, filing date, next hearing date, case status.

If a judgment/order PDF link is present, download the PDF bytes and return them in ScraperResult.pdf_bytes.

Return raw HTML/JSON in ScraperResult.raw_response so it’s stored in the DB.

Register the new scraper in SCRAPER_REGISTRY with a unique key and it will appear in the UI.

Security, politeness & production considerations

Respect robots.txt, terms of service, and rate limits. Add sleeps and caching; avoid hammering court servers.

Use official APIs where available — many courts provide structured services if you request access.

For production, run behind a WSGI server (gunicorn/uvicorn), add authentication and logging, and store PDFs in durable object storage (S3) rather than local disk.

Handling captchas or login-protected resources will require manual steps or partner APIs.

How to run the demo locally

Copy the code from the canvas file Ecourts-case-fetcher-flask into app.py on your machine (or download it).

Create a virtual environment and install dependencies:

python -m venv venv
source venv/bin/activate     # or `venv\\Scripts\\activate` on Windows
pip install flask flask_sqlalchemy sqlalchemy requests beautifulsoup4 reportlab


Install selenium if you’ll implement Selenium scrapers; install chromedriver / geckodriver as appropriate.

Run:

python app.py


Open http://127.0.0.1:5000 — submit a demo query and download the generated PDF from history.
I can convert the UI into a React single-file preview or split the Flask app into a backend + React frontend.

I can add rate-limiting, caching, and a simple scheduler to fetch cause lists daily and store them.
