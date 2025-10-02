A Flask-based web application to fetch Indian court case details, download judgments/orders, and generate cause lists. Supports High Courts and District Courts via their official eCourts portals and demonstrates a pluggable scraper architecture for easy extension

## Features

- Simple, responsive UI with **dropdowns** for Court, Case Type, Case Number, and Year.
- **Fetch case details** (Parties, Filing Date, Next Hearing, Status) using a modular scraper architecture.
- **Download judgments/orders as PDF**.
- **Cause List generator** (demo).
- **Query history dashboard** with cards and status indicators.
- **Interactive charts**:
  - Doughnut chart for cases by status (`OK`, `Error`, `Not Found`)
  - Bar chart for cases per court.
- SQLite database for storing **queries, raw responses, and PDF paths**.
- API endpoints for programmatic access (JSON responses).

---
## Demo Screenshot
<img width="1920" height="1080" alt="Screenshot (33)" src="https://github.com/user-attachments/assets/e36d1c56-1ab0-4de6-81f5-4179fa7171d9" />

<img width="1920" height="1080" alt="Screenshot (34)" src="https://github.com/user-attachments/assets/87642c65-b02a-4966-b3aa-f8c6886229a3" />

<img width="1920" height="1080" alt="Screenshot (35)" src="https://github.com/user-attachments/assets/c68465cf-0f8e-4037-b0a6-8822c17dba98" />

<img width="1920" height="1080" alt="Screenshot (36)" src="https://github.com/user-attachments/assets/116947db-8e21-4fea-8c88-d72327e3562d" />


## Tools & Libraries Used

- **Python 3**
- **Flask** – Web framework
- **Flask-SQLAlchemy** – Database ORM
- **SQLite** – Lightweight database for demo
- **ReportLab** – Generate PDF files
- **Chart.js** – Interactive charts for dashboard
- **Jinja2** – HTML templating
- **ChatGPT** – Assisted in improving UI/UX

  for real scrapers:  

- **Requests** – HTTP requests  
- **BeautifulSoup4** – HTML parsing  
- **Selenium** – For JS-heavy court portals

---

## Setup & Installation

1. **Clone the repository**

```bash
**git clone https://github.com/your-username/ecourts-case-fetcher.git
cd ecourts-case-fetcher**

Create a virtual environment

**python -m venv venv**

Activate the virtual environment

PowerShell:

**.\venv\Scripts\Activate.ps1**

CMD:

**venv\Scripts\activate.bat**

Install dependencies

**pip install -r requirements.txt**

If requirements.txt is not present, install manually:

**pip install flask flask_sqlalchemy sqlalchemy reportlab requests beautifulsoup4 selenium**

Run the Flask app

**python app.py**

Open in browser
Go to http://127.0.0.1:5000
git clone https://github.com/your-username/court-data-fetcher.git
cd court-data-fetcher
