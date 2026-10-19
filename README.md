# Docnexa AI

**Turn invoices, receipts and resumes into clean, verified data. Every value is traced back to your document.**

---

## Problem

Businesses, students and job seekers still copy details from invoices, receipts and resumes into spreadsheets by hand. It is slow and easy to get wrong: a mistyped total or a missed date can cause real financial and hiring mistakes.

Many "OCR plus AI" tools make this faster, but they bring a new problem. The AI can invent values that are not in the document, quietly misread numbers, and give you no way to check where a value came from.

## Solution

Docnexa AI reads a PDF, Word file or image, extracts the important fields, and then **verifies the result instead of trusting the AI**:

1. **Reads** the document (direct text extraction, or OCR for scans and photos).
2. **Extracts** fields and line items with a large language model.
3. **Verifies** every value: anything that cannot be found in the document is removed, and totals, tax and dates are recalculated and cross-checked.
4. **Lets you review** each field, see the exact source text, approve or reject it, and export to Excel, JSON or CSV.

## Features

- **Only real values:** each extracted value must appear in the document text. Empty, guessed or invented fields are removed automatically.
- **Automatic checks:** quantity × price, line items against the subtotal, subtotal + tax against the total, and date validity and order. Errors and warnings are flagged.
- **Trace every value:** click 🔍 on a field to see the exact source text. Hover a value to see its quote.
- **Review workflow:** edit, approve ✓, reject ✕ or undo any field, and approve all verified fields at once.
- **Ask your document:** a chat that answers only from the document and quotes the supporting line.
- **Privacy mask:** hides emails, phone numbers, IDs, account and card numbers from the AI, the extracted text, results, history and exports.
- **Batch and export:** process many files at once and download one Excel workbook (Documents, Fields, Line items, Checks), or export a single document as Excel, JSON or CSV.
- **Accounts and history:** sign-up and login, plus a per-user history of processed documents with a dashboard summary.
- **Supported files:** PDF, Word (`.docx`) and images (PNG, JPG, TIFF, BMP, GIF, WebP). Auto-detect accepts **invoices, receipts and resumes**; other document types are rejected with a clear message.

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, FastAPI, Uvicorn, Pydantic |
| Frontend | HTML, CSS and vanilla JavaScript (single-page app, no build step) |
| Document reading | PyMuPDF (PDF), built-in `.docx` parser, Pillow and NumPy (image preparation), PaddleOCR (optional local OCR) |
| Exports | openpyxl (Excel), JSON, CSV |
| Accounts and sessions | SQLite, scrypt password hashing, HttpOnly session cookies |
| Other | requests, python-dotenv, Docker (optional) |

## AI / API Used

- **Groq API** (OpenAI-compatible chat completions): the language model that extracts structured fields and answers questions about a document. Default model: `openai/gpt-oss-120b`.
- **Groq vision model** (`meta-llama/llama-4-scout-17b-16e-instruct`): used only as an OCR fallback for scans and photos when PaddleOCR is not installed.
- **PaddleOCR** (optional, runs locally): OCR for scanned pages and images.

Model names can be changed in `.env`. Check the current list at https://console.groq.com/docs/models.

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>
```

### 2. Install dependencies

Python 3.10 or newer is required.

**Windows (PowerShell)**
```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**macOS / Linux**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Optional local OCR (large download, can be hard to install on some Windows machines): `pip install -r requirements-ocr.txt`. Without it, set `OCR_ENGINE=vision` in your `.env` and scans are read with the Groq vision model.

### 3. Add environment variables

Copy the example file and add your own key. **Never commit your real keys:** `.env` is already listed in `.gitignore`, so keep it that way and share only `.env.example`.

```bash
cp .env.example .env        # Windows: copy .env.example .env
```

Get a free key at https://console.groq.com/keys, then edit `.env`:

| Variable | Required | Description |
|---|---|---|
| `GROQ_API_KEY` | Yes | Your Groq API key |
| `GROQ_MODEL` | No | Model for extraction and questions (default `openai/gpt-oss-120b`) |
| `GROQ_FALLBACK_MODELS` | No | Comma-separated backup models |
| `GROQ_VISION_MODEL` | No | Vision model for the OCR fallback |
| `OCR_ENGINE` | No | `auto` (default), `paddle` or `vision` |
| `MAX_FILE_MB` / `MAX_PDF_PAGES` | No | Upload limits (defaults 10 MB / 10 pages) |
| `RATE_LIMIT_PER_MIN` | No | Requests per minute per IP (default 20) |
| `DB_PATH` | No | Location of the SQLite accounts database (default: a file in the project's `data/` folder) |

### 4. Run the app

```bash
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000, create an account on the first screen, then use **Dashboard** to upload documents (or click a sample on the Home page).

**Optional, with Docker**
```bash
docker build -t docnexa-ai .
docker run -p 8000:8000 --env-file .env docnexa-ai
```
Mount a persistent volume at `data/` if you want accounts to survive redeploys.

---

*Always verify extracted data before relying on it, and do not upload sensitive documents to a public demo.*
