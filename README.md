<div align="center">
  
# Docnexa AI

**Turn invoices, receipts and resumes into clean, verified data. Every value is traced back to your document.**
</div>

---
<div align="center">
  
## Problem
</div>

Manually extracting information from documents is time-consuming and error-prone. Incorrect totals, missing dates, and inaccurate data can lead to financial and administrative mistakes. Traditional OCR tools can read text but may struggle to organize, validate, and interpret the extracted information.

<div align="center">
  
## Solution
</div>

**DocNexa AI** combines Optical Character Recognition (OCR) with AI-powered information extraction to convert supported documents into structured, verifiable data. Users can review extracted fields, check calculations, ask questions about their documents, and export results in convenient formats.

<div align="center">
  
## Features
</div>

- **AI-Powered Document Extraction** — Automatically extracts structured information from invoices, receipts, and resumes using OCR and AI.
- **Smart Validation & Review** — Detects missing or potentially incorrect values and allows users to review, edit, and approve extracted data.
- **Document Q&A & Export** — Lets users ask questions about uploaded documents and export extracted results to formats such as Excel, CSV, and JSON.

<div align="center">
  
## Tech Stack
</div>

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi&logoColor=white)
![HTML5](https://img.shields.io/badge/HTML5-Frontend-E34F26?logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-Styling-1572B6?logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-Frontend-F7DF1E?logo=javascript&logoColor=black)
![PaddleOCR](https://img.shields.io/badge/PaddleOCR-OCR-0062B8)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?logo=sqlite&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Containerization-2496ED?logo=docker&logoColor=white)

<div align="center">
  
## AI / API Used

</div>

- **Groq API (LLM Integration):** Enables AI-powered document information extraction, structured data generation, and document-based question answering.
- **PaddleOCR (Optical Character Recognition):** Extracts text from scanned PDFs and images to support automated document processing.
  
**Groq vision model** used only as an OCR fallback for scans and photos when PaddleOCR is not installed.

<div align="center">
  
## Setup Instructions
</div>

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

### 3. Run the app

```bash
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```
---

*Always verify extracted data before relying on it, and do not upload sensitive documents to a public demo.*
