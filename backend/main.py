"""FastAPI entry point for the news summarizer."""

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from summarizer import summarize
from article import fetch_article_text

load_dotenv()

app = FastAPI(title="AI News Summarizer", version="1.0.0")

# CORS — allow the deployed frontend (and localhost for dev).
_origins_env = os.environ.get("CORS_ORIGINS", "*")
origins = [o.strip() for o in _origins_env.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["*"],
)

MAX_INPUT_CHARS = 20000


class TextIn(BaseModel):
    text: str = Field(..., min_length=50, max_length=MAX_INPUT_CHARS)
    max_length: int = Field(150, ge=40, le=300)
    min_length: int = Field(40, ge=10, le=200)


class UrlIn(BaseModel):
    url: str = Field(..., min_length=8, max_length=2000)
    max_length: int = Field(150, ge=40, le=300)
    min_length: int = Field(40, ge=10, le=200)


@app.get("/")
def root():
    return {"service": "ai-news-summarizer", "status": "ok"}


@app.get("/health")
def health():
    return {"status": "ok", "has_token": bool(os.environ.get("HF_API_TOKEN"))}


@app.post("/summarize")
def summarize_text(body: TextIn):
    try:
        return summarize(body.text, body.max_length, body.min_length)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Upstream error: {e}")


@app.post("/summarize-url")
def summarize_url(body: UrlIn):
    try:
        text = fetch_article_text(body.url, max_chars=MAX_INPUT_CHARS)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not fetch article: {e}")

    if len(text) < 200:
        raise HTTPException(
            status_code=422,
            detail="Fetched page had too little readable text to summarize.",
        )

    try:
        result = summarize(text, body.max_length, body.min_length)
        result["source_url"] = body.url
        return result
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Upstream error: {e}")
