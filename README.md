# PDF Converter

Convert PDF files to Word (DOCX), Excel (XLSX), Image (PNG), Text (TXT), and HTML.

## Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: HTML + Tailwind CSS
- **Libraries**: pdf2docx, PyMuPDF, pdfplumber, pandas, openpyxl

## Project Structure

```
pdf-converter/
├── app/
│   ├── main.py                  # FastAPI app entry point
│   ├── routes/converter.py      # API endpoints
│   ├── services/converter_service.py  # Conversion functions
│   ├── utils/
│   │   ├── file_handler.py      # File save / cleanup utilities
│   │   └── validators.py        # PDF validation helpers
│   └── models/conversion.py     # Pydantic request/response models
├── static/index.html            # Frontend UI
├── uploads/                     # Uploaded PDFs (auto-deleted after conversion)
├── outputs/                     # Converted files
├── Procfile                     # Railway start command
├── runtime.txt                  # Python version for Railway
├── requirements.txt
└── README.md
```

## Setup & Run (Local)

```bash
# 1. Create a virtual environment
python -m venv venv

# 2. Activate it (Windows)
venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start the server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open **http://localhost:8000** in your browser to use the UI, or
visit **http://localhost:8000/docs** for the interactive API documentation.

## Deploy to Railway

1. Push this repo to GitHub.
2. In Railway, click **New Project** → **Deploy from GitHub repo**.
3. Select the repo — Railway auto-detects `requirements.txt` and `Procfile`.
4. No extra config needed. The app listens on `$PORT` automatically.

### Manual deploy via Railway CLI

```bash
railway login
railway init
railway up
railway domain
```

## API Endpoints

| Method | Endpoint               | Description           |
|--------|------------------------|-----------------------|
| GET    | `/api/health`          | Health check          |
| POST   | `/api/upload`          | Upload a PDF file     |
| POST   | `/api/convert/docx`    | Convert PDF → DOCX    |
| POST   | `/api/convert/xlsx`    | Convert PDF → XLSX    |
| POST   | `/api/convert/image`   | Convert PDF → PNG     |
| POST   | `/api/convert/txt`     | Convert PDF → TXT     |
| POST   | `/api/convert/html`    | Convert PDF → HTML    |
| GET    | `/api/download/{file}` | Download a file       |
| GET    | `/api/files`           | List uploaded files   |

## Sample curl Commands

```bash
# Health check
curl http://localhost:8000/api/health

# Upload a PDF
curl -X POST http://localhost:8000/api/upload \
  -F "file=@document.pdf"

# Convert to DOCX (replace <filename> with the name returned by upload)
curl -X POST http://localhost:8000/api/convert/docx \
  -d "filename=20260529_120000_document.pdf"

# Download the converted file
curl -O http://localhost:8000/api/download/<output-filename>

# List all uploaded files
curl http://localhost:8000/api/files
```

## Features

- PDF validation (magic bytes `%PDF-` + file extension)
- 100 MB file size limit
- Auto-deletes source PDF after successful conversion
- Console logging (file logging fallback on local)
- CORS enabled (works with any frontend)
- Drag-and-drop frontend with real-time progress indicators
- Interactive Swagger docs at `/docs`
