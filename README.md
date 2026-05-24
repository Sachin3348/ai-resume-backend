# AI Resume Parser 🤖📄

A production-ready, low-latency FastAPI backend that extracts structured **Work Experience** and **Projects** data from PDF resumes using LLMs — with full provider agnosticism via the `instructor` library.

---

## ✨ Features

- ⚡ **Ultra-fast PDF text extraction** using PyMuPDF (`fitz`)
- 🔀 **Provider-agnostic LLM integration** — switch between Google Gemini, OpenAI, Anthropic, or Ollama by changing a single `.env` variable
- 🧱 **Strict Pydantic output schemas** that prevent hallucination
- 🔁 **Auto-retry on schema validation failures** via `instructor`
- 🏭 **Singleton LLM client** using `@lru_cache` for zero per-request overhead
- 💰 **Cost-optimized** — designed for Gemini Flash / GPT-4o-mini class models

---

## 🗂 Project Structure

```
ai-resume-backend/
├── .env.example            # Environment variable template
├── .env                    # Your local config (git-ignored)
├── requirements.txt        # Python dependencies
├── run.py                  # Uvicorn entry point
└── app/
    ├── __init__.py
    ├── config.py           # Pydantic Settings — loads .env
    ├── schemas.py          # ParsedResume, WorkExperience, Project models
    ├── pdf_extractor.py    # PyMuPDF raw text extraction
    ├── llm_client.py       # Singleton instructor.from_provider() client
    ├── parser.py           # LLM call with anti-hallucination prompt
    └── main.py             # FastAPI app + /parse-resume endpoint
```

---

## 🧩 Tech Stack

| Layer | Library |
|---|---|
| API Framework | `FastAPI` |
| PDF Extraction | `PyMuPDF` (`fitz`) |
| Output Schemas | `Pydantic v2` |
| LLM Structured Output | `instructor` (`from_provider`) |
| Config Management | `pydantic-settings` |
| Server | `uvicorn` |

---

## ⚙️ Setup

### 1. Prerequisites

- Python **3.11+**
- `pip`

### 2. Clone the repository

```bash
git clone https://github.com/your-username/ai-resume-backend.git
cd ai-resume-backend
```

### 3. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure environment variables

```bash
cp .env.example .env
```

Open `.env` and fill in your values:

```env
# Pick ONE provider string — this controls which LLM is used
LLM_PROVIDER="google/gemini-2.5-flash"

# Add the API key for your chosen provider
GOOGLE_API_KEY="your-google-api-key-here"
OPENAI_API_KEY=""
ANTHROPIC_API_KEY=""
```

---

## 🚀 Start the Server

```bash
python run.py
```

The API will be live at **`http://localhost:8000`**

Interactive docs: **`http://localhost:8000/docs`**

---

## 🔀 Switching LLM Providers

Edit the `LLM_PROVIDER` value in `.env` and restart the server. No code changes needed.

| Provider | `LLM_PROVIDER` value | Required Key |
|---|---|---|
| Google Gemini Flash | `google/gemini-2.5-flash` | `GOOGLE_API_KEY` |
| OpenAI GPT-4o-mini | `openai/gpt-4o-mini` | `OPENAI_API_KEY` |
| Anthropic Claude Haiku | `anthropic/claude-3-haiku-20240307` | `ANTHROPIC_API_KEY` |
| Ollama (local) | `ollama/llama3` | *(none — local)* |

---

## 📡 API Reference

### `POST /parse-resume`

Accepts a PDF file upload and returns structured JSON.

**Request**

```
Content-Type: multipart/form-data
Body: file=<your-resume.pdf>
```

**cURL example**

```bash
curl -X POST http://localhost:8000/parse-resume \
  -F "file=@/path/to/resume.pdf"
```

**Response** `200 OK`

```json
{
  "work_experience": [
    {
      "company": "Acme Corp",
      "role": "Senior Software Engineer",
      "start_date": "Jan 2022",
      "end_date": "Present",
      "location": "San Francisco, CA",
      "bullets": [
        "Led migration of monolith to microservices, reducing p99 latency by 40%.",
        "Mentored a team of 4 junior engineers."
      ]
    }
  ],
  "projects": [
    {
      "name": "ResumeAI",
      "description": "Open-source resume parser powered by LLMs.",
      "technologies": ["FastAPI", "PyMuPDF", "instructor", "Pydantic"],
      "url": "https://github.com/you/resumeai",
      "bullets": [
        "Achieved <300ms p95 latency using Gemini Flash."
      ]
    }
  ]
}
```

### `GET /health`

Returns server health status.

```json
{ "status": "ok" }
```

---

## 🛡 Error Handling

| Scenario | HTTP Status | Detail |
|---|---|---|
| Non-PDF file uploaded | `400` | `Only PDF files are accepted.` |
| Empty file uploaded | `400` | `Uploaded file is empty.` |
| Scanned/image-only PDF | `422` | `PDF contains no extractable text.` |
| Corrupt or invalid PDF | `422` | `Failed to open PDF: ...` |
| LLM API / validation failure | `502` | `LLM parsing failed: ...` |

---

## 📝 Notes

- **Scanned PDFs** (image-based) are not supported — the extractor requires selectable text. Add an OCR step (e.g., `pytesseract`) for scanned documents.
- Set `temperature=0.0` is enforced for deterministic, low-hallucination output.
- `instructor` automatically retries up to **2 times** if the LLM response fails Pydantic schema validation.

---

## 📄 License

MIT
