import re
from typing import Dict

import httpx
from bs4 import BeautifulSoup

from app.utils.validators import validate_redirect_url, validate_url


async def extract_website(url: str) -> Dict[str, str]:
    validate_url(url)
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; LinkAnalysisBot/1.0)",
        "Accept": "text/html,application/xhtml+xml",
    }

    async with httpx.AsyncClient(follow_redirects=False, timeout=15.0) as client:
        current_url = url
        for _ in range(5):
            await validate_redirect_url(current_url)
            response = await client.get(current_url, headers=headers)
            if response.status_code in (301, 302, 303, 307, 308):
                location = response.headers.get("location")
                if not location:
                    break
                current_url = str(httpx.URL(current_url).join(location))
                continue
            response.raise_for_status()
            break
        else:
            raise ValueError("Website redirected too many times.")

    content_type = response.headers.get("content-type", "")
    if "text/html" not in content_type.lower() and "application/xhtml" not in content_type.lower():
        raise ValueError("The URL does not return an HTML page.")

    soup = BeautifulSoup(response.text, "html.parser")
    for element in soup(["script", "style", "noscript", "svg", "template"]):
        element.decompose()

    title = (soup.title.string.strip() if soup.title and soup.title.string else "")
    meta_description = ""
    meta = soup.find("meta", attrs={"name": re.compile("^description$", re.I)})
    if meta and meta.get("content"):
        meta_description = meta["content"].strip()

    headings = [
        re.sub(r"\s+", " ", heading.get_text(" ", strip=True)).strip()
        for heading in soup.find_all(["h1", "h2", "h3"])
        if heading.get_text(" ", strip=True).strip()
    ]
    paragraphs = [
        re.sub(r"\s+", " ", text).strip()
        for text in soup.stripped_strings
        if len(text.strip()) > 25
    ]

    text = "\n".join(dict.fromkeys(headings + paragraphs))
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = text[:12000]
    if not text:
        raise ValueError("No readable website content could be extracted.")

    return {
        "url": current_url,
        "title": title,
        "meta_description": meta_description,
        "headings": "\n".join(dict.fromkeys(headings)),
        "text": text,
    }