"""Fetch and extract readable article text from a URL."""

import requests
from bs4 import BeautifulSoup

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0 Safari/537.36"
)


def fetch_article_text(url: str, max_chars: int = 20000) -> str:
    """Download a URL and return the main readable text.

    This isn't a full Readability port — a naive concatenation of <p> tags
    is good enough for most news sites and avoids heavy dependencies.
    """
    resp = requests.get(
        url,
        headers={"User-Agent": USER_AGENT},
        timeout=15,
        allow_redirects=True,
    )
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    # Drop non-content elements.
    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form"]):
        tag.decompose()

    paragraphs = [p.get_text(" ", strip=True) for p in soup.find_all("p")]
    text = "\n\n".join(p for p in paragraphs if len(p) > 30)

    if not text.strip():
        # Fallback: all visible body text.
        text = soup.get_text("\n", strip=True)

    return text[:max_chars]
