"""
Small Flask web app: Court-Data Fetcher & Judgment Downloader (proof-of-concept)
"""

from flask import Flask, request, redirect, url_for, send_file, flash
from flask import render_template_string, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from datetime import datetime
import os
import io
import uuid
import json

# --- Configuration ---
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'cases.db')
PDF_STORAGE = os.path.join(BASE_DIR, 'pdfs')
os.makedirs(PDF_STORAGE, exist_ok=True)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'dev-key-for-demo'

db = SQLAlchemy(app)

# --- Database models ---
class QueryLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    court = db.Column(db.String(80), nullable=False)
    case_type = db.Column(db.String(120), nullable=False)
    case_number = db.Column(db.String(120), nullable=False)
    year = db.Column(db.String(10), nullable=True)
    created_at = db.Column(db.DateTime, default=func.now())
    raw_response = db.Column(db.Text)
    parsed_json = db.Column(db.Text)
    pdf_path = db.Column(db.String(400))
    status = db.Column(db.String(80))

with app.app_context():
    db.create_all()

# --- Scraper architecture ---
class ScraperResult:
    def __init__(self, parties=None, filing_date=None, next_hearing=None, status=None, raw_response='', pdf_bytes=None, pdf_filename=None):
        self.parties = parties or {}
        self.filing_date = filing_date
        self.next_hearing = next_hearing
        self.status = status
        self.raw_response = raw_response
        self.pdf_bytes = pdf_bytes
        self.pdf_filename = pdf_filename

class BaseScraper:
    name = 'base'
    def fetch(self, case_type: str, case_number: str, year: str) -> ScraperResult:
        raise NotImplementedError()

# Dummy scraper
class DummyScraper(BaseScraper):
    name = 'dummy_court_example'
    def fetch(self, case_type, case_number, year):
        parties = {'petitioner': 'A. Example','respondent': 'B. Sample'}
        filing_date = '2021-06-15'
        next_hearing = '2025-10-10'
        status = 'Pending'
        raw_response = f"DUMMY: Found case {case_type}-{case_number}/{year}"
        pdf_bytes = generate_simple_pdf_bytes(f"Judgment for {case_type}-{case_number}/{year}\nParties: {parties}")
        pdf_filename = f"{case_type}_{case_number}_{year}.pdf"
        return ScraperResult(parties, filing_date, next_hearing, status, raw_response, pdf_bytes, pdf_filename)

SCRAPER_REGISTRY = {DummyScraper.name: DummyScraper()}

# --- Helpers ---
def generate_simple_pdf_bytes(text: str) -> bytes:
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        buf = io.BytesIO()
        c = canvas.Canvas(buf, pagesize=letter)
        text_object = c.beginText(40, 720)
        for line in text.split('\n'):
            text_object.textLine(line)
        c.drawText(text_object)
        c.showPage()
        c.save()
        buf.seek(0)
        return buf.read()
    except Exception:
        return text.encode('utf-8')

def save_pdf_bytes(pdf_bytes: bytes, filename: str) -> str:
    safe_name = f"{uuid.uuid4().hex}_{filename}"
    path = os.path.join(PDF_STORAGE, safe_name)
    with open(path, 'wb') as f:
        f.write(pdf_bytes)
    return path

# --- HTML Template ---
INDEX_HTML = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Court Data Fetcher</title>
  <style>
    body {
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      background-color: #f4f7f8;
      margin: 0;
      padding: 0;
    }
    .container {
      max-width: 1000px;
      margin: 20px auto;
      padding: 30px;
    }
    h1, h2 {
      text-align: center;
      color: #333;
    }
    a {
      color: #1e88e5;
      text-decoration: none;
    }
    a:hover {
      text-decoration: underline;
    }

    /* --- Flash messages --- */
    .flash {
      background-color: #fff3cd;
      padding: 12px 15px;
      border-left: 5px solid #ffc107;
      margin-bottom: 20px;
      border-radius: 6px;
      font-weight: bold;
      color: #856404;
    }

    /* --- Forms --- */
    form {
      display: flex;
      flex-wrap: wrap;
      gap: 15px;
      justify-content: space-between;
      background: #fff;
      padding: 20px;
      border-radius: 10px;
      box-shadow: 0 4px 10px rgba(0,0,0,0.1);
      margin-bottom: 30px;
    }
    label {
      flex: 1 1 45%;
      display: flex;
      flex-direction: column;
      font-weight: bold;
      color: #555;
    }
    input, select {
      padding: 8px 10px;
      margin-top: 5px;
      border: 1px solid #ccc;
      border-radius: 6px;
      font-size: 14px;
    }
    input[type="submit"] {
      background-color: #1e88e5;
      color: white;
      font-weight: bold;
      border: none;
      cursor: pointer;
      transition: background 0.3s;
      flex: 1 1 100%;
      padding: 12px;
      font-size: 16px;
    }
    input[type="submit"]:hover {
      background-color: #1565c0;
    }

    /* --- Query History Cards --- */
    .history-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
      gap: 20px;
    }
    .card {
      background: #fff;
      border-radius: 10px;
      box-shadow: 0 4px 8px rgba(0,0,0,0.1);
      padding: 20px;
      transition: transform 0.2s;
    }
    .card:hover {
      transform: translateY(-3px);
    }
    .card h3 {
      margin-top: 0;
      color: #1e88e5;
    }
    .status-badge {
      display: inline-block;
      padding: 4px 10px;
      border-radius: 12px;
      font-size: 12px;
      font-weight: bold;
      color: white;
    }
    .status-ok { background-color: #4caf50; }
    .status-error { background-color: #f44336; }
    .status-not_found { background-color: #ff9800; }

    .pdf-btn {
      display: inline-block;
      padding: 6px 12px;
      margin-top: 10px;
      background-color: #1e88e5;
      color: white;
      border-radius: 6px;
      font-size: 13px;
      text-decoration: none;
      transition: background 0.3s;
    }
    .pdf-btn:hover {
      background-color: #1565c0;
    }

    /* --- Cause list form --- */
    .cause-list {
      margin-top: 40px;
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>Court Data Fetcher</h1>

    {% with messages = get_flashed_messages() %}
      {% if messages %}
        {% for message in messages %}
          <div class="flash">{{ message }}</div>
        {% endfor %}
      {% endif %}
    {% endwith %}

    <!-- Fetch Case Form -->
    <form method="post" action="/fetch">
      <label>
        Select Court:
        <select name="court" required>
          {% for key, scr in scrapers.items() %}
            <option value="{{key}}">{{key}}</option>
          {% endfor %}
        </select>
      </label>
      <label>
        Case Type:
        <input name="case_type" required>
      </label>
      <label>
        Case Number:
        <input name="case_number" required>
      </label>
      <label>
        Year:
        <input name="year">
      </label>
      <input type="submit" value="Fetch Case">
    </form>

    <!-- Query History -->
    <h2>Query History</h2>
    <div class="history-grid">
      {% for q in queries %}
      <div class="card">
        <h3>{{ q.case_type }}-{{ q.case_number }}/{{ q.year }}</h3>
        <p><strong>Court:</strong> {{ q.court }}</p>
        <p><strong>Time:</strong> {{ q.created_at }}</p>
        <p>
          <strong>Status:</strong> 
          <span class="status-badge status-{{ q.status|lower }}">{{ q.status }}</span>
        </p>
        {% if q.pdf_path %}
          <a class="pdf-btn" href="/download/{{q.id}}">Download PDF</a>
        {% endif %}
      </div>
      {% endfor %}
    </div>

    <!-- Cause List Form -->
    <div class="cause-list">
      <h2>Cause List</h2>
      <form method="post" action="/causelist">
        <label>
          Court ID:
          <input name="court" value="dummy_court_example">
        </label>
        <label>
          Date (YYYY-MM-DD, optional for today):
          <input name="date">
        </label>
        <input type="submit" value="Download Cause List">
      </form>
    </div>
  </div>
</body>
</html>

"""

# --- Routes ---
@app.route('/')
def index():
    queries = QueryLog.query.order_by(QueryLog.created_at.desc()).limit(50).all()
    return render_template_string(INDEX_HTML, queries=queries, scrapers=SCRAPER_REGISTRY)

@app.route('/fetch', methods=['POST'])
def fetch_case():
    court = request.form.get('court')
    case_type = request.form.get('case_type')
    case_number = request.form.get('case_number')
    year = request.form.get('year')
    if not court or not case_type or not case_number:
        flash('Missing required fields'); return redirect(url_for('index'))
    if court not in SCRAPER_REGISTRY:
        flash('Unknown court'); return redirect(url_for('index'))
    log = QueryLog(court=court, case_type=case_type, case_number=case_number, year=year)
    db.session.add(log); db.session.commit()
    try:
        result = SCRAPER_REGISTRY[court].fetch(case_type, case_number, year)
    except Exception as e:
        log.status = 'error'; log.raw_response = str(e); db.session.commit()
        flash('Error: '+str(e)); return redirect(url_for('index'))
    log.raw_response = result.raw_response
    log.parsed_json = json.dumps({'parties': result.parties,'filing_date': result.filing_date,'next_hearing': result.next_hearing,'status': result.status})
    log.status = 'ok'
    if result.pdf_bytes: log.pdf_path = save_pdf_bytes(result.pdf_bytes, result.pdf_filename or 'judgment.pdf')
    db.session.commit()
    flash('Fetched successfully!'); return redirect(url_for('index'))

@app.route('/download/<int:query_id>')
def download_pdf(query_id):
    q = QueryLog.query.get_or_404(query_id)
    if not q.pdf_path or not os.path.exists(q.pdf_path):
        flash('PDF not available'); return redirect(url_for('index'))
    return send_file(q.pdf_path, as_attachment=True)

# --- Run ---
if __name__ == '__main__':
    app.run(debug=True)
