# Setup Guide

Two pieces to set up: the Python backend and the React frontend.
Both are free. Plan: get it running locally first, then deploy.

---

## Part 1 · Get a Hugging Face API token (2 min)

1. Go to https://huggingface.co/join and sign up (or sign in)
2. Go to https://huggingface.co/settings/tokens
3. Click **+ Create new token**
4. Token type: **Read** (no write access needed)
5. Name: `news-summarizer` → **Create token**
6. **Copy the token** (starts with `hf_...`) — you see it once

---

## Part 2 · Run the backend locally (3 min)

```bash
cd /Users/sabitrazzak/ClaudeCode/news-summarizer/backend
source .venv/bin/activate
cp .env.example .env
```

Open `.env` and paste your Hugging Face token where it says `hf_your_token_here`.
Save the file.

Start the server:
```bash
uvicorn main:app --reload
```

It should print `Uvicorn running on http://127.0.0.1:8000`. Leave this running.

Quick test: open http://localhost:8000/health in a browser. You should see
`{"status":"ok","has_token":true}`.

---

## Part 3 · Run the frontend locally (1 min)

**Open a new Terminal tab** (keep the backend running in the first one).

```bash
cd /Users/sabitrazzak/ClaudeCode/news-summarizer/frontend
cp .env.example .env.local
npm run dev
```

Open http://localhost:5173. Paste some long text (500+ chars) → click **Summarize**.
The first request takes ~15–30 seconds (model cold start); later ones are 2–5 seconds.

---

## Part 4 · Deploy the backend to Render (5 min)

### 4.1 Push code to GitHub first
Follow **Part 6** below to set up the GitHub repo, then come back here.

### 4.2 Create the Render service
1. Go to https://render.com → sign up with GitHub
2. Dashboard → **New +** → **Web Service**
3. Connect your `news-summarizer` GitHub repo
4. Fill in:
   - **Name:** `news-summarizer-api` (or anything)
   - **Root Directory:** `backend`
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type:** **Free**
5. Scroll to **Environment Variables** → **Add Environment Variable**:
   - Key: `HF_API_TOKEN` · Value: your `hf_...` token
   - Key: `CORS_ORIGINS` · Value: `*` (we'll tighten this later)
6. Click **Create Web Service**

Render will build and deploy. Takes ~3–5 min. When it's done, you'll see a
URL like `https://news-summarizer-api.onrender.com`. Test it:
`https://your-url.onrender.com/health`

**Note:** Render's free tier sleeps after 15 minutes of no traffic. First
request after sleep takes ~30 seconds to wake up. This is fine for a demo.

---

## Part 5 · Deploy the frontend to Vercel (3 min)

1. Go to https://vercel.com → sign up with GitHub
2. **Add New** → **Project**
3. Import your `news-summarizer` repo
4. **Root Directory:** `frontend` (click **Edit** next to the directory field)
5. Framework preset should auto-detect **Vite**
6. Expand **Environment Variables**:
   - Key: `VITE_API_BASE` · Value: your Render URL (e.g. `https://news-summarizer-api.onrender.com`)
7. Click **Deploy**

Takes ~1 min. You get a URL like `https://news-summarizer-abc123.vercel.app`.

### Tighten CORS
Back on Render → your service → **Environment** tab → edit `CORS_ORIGINS`:
- Change from `*` to your Vercel URL (exactly, no trailing slash)
- Save → Render auto-redeploys

---

## Part 6 · Push to GitHub (first-time setup)

1. Create a new repo at https://github.com/new — name it `news-summarizer`, Public, no README
2. Copy the HTTPS URL it shows
3. In Terminal:
```bash
cd /Users/sabitrazzak/ClaudeCode/news-summarizer
git init
git add .
git commit -m "Initial commit: AI news summarizer"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/news-summarizer.git
git push -u origin main
```

Use your GitHub Personal Access Token as the password (same flow as the
reminder app — make a new one at https://github.com/settings/tokens if yours
has expired).

---

## What to put on your resume
- **Repo:** `github.com/YOUR_USERNAME/news-summarizer`
- **Live demo:** your Vercel URL
