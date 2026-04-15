# AI News Summarizer

Transformer-based summarizer for articles, essays, or any long-form text.
Accepts pasted text, `.txt` uploads, or a URL.

**Stack:** Python (FastAPI) · Hugging Face `facebook/bart-large-cnn` · React (Vite)

## Architecture
```
React frontend  ──fetch──►  FastAPI backend  ──HF Inference API──►  BART
  (Vercel)                    (Render)                                (hosted)
```

## How it handles long inputs
- **Chunking:** articles up to 20,000 chars are split into ~3,200-char chunks
  on sentence boundaries.
- **Batched inference:** all chunks are sent in one HTTP request to Hugging
  Face (`inputs: [chunk1, chunk2, ...]`) instead of N round-trips.
- **Bounded output:** `max_length` is explicitly passed to the model so it
  can't wander into hallucinated content beyond the configured budget.

## Layout
```
backend/    FastAPI app
frontend/   Vite + React app
```

## Local development

### Backend
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env and set HF_API_TOKEN to your Hugging Face token.
uvicorn main:app --reload
```
Runs at http://localhost:8000. Check `http://localhost:8000/health` for status.

### Frontend
```bash
cd frontend
npm install
cp .env.example .env.local   # already points at localhost:8000
npm run dev
```
Runs at http://localhost:5173.

## Deployment
- **Backend →** Render Web Service (free tier). Root = `backend/`, build: `pip install -r requirements.txt`, start: `uvicorn main:app --host 0.0.0.0 --port $PORT`. Env vars: `HF_API_TOKEN`, `CORS_ORIGINS`.
- **Frontend →** Vercel. Root = `frontend/`. Env var: `VITE_API_BASE` = your Render URL.

See `SETUP.md` for step-by-step deployment.
