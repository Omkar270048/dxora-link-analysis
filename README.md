# dxora-link-analysis

FastAPI service that extracts website content and produces structured competitor, search, SEO, service, and audience analysis.

## Setup

```powershell
py -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Set `GEMINI_API_KEY` and `GEMINI_MODEL` in the project-root `.env` file for Gemini-powered analysis. The application loads that file regardless of the working directory. Restart the server after changing either setting. The API returns an explicit configuration error if the key is missing rather than presenting generic fallback text as an AI analysis.

## Run

```powershell
py -m uvicorn app.main:app --host 0.0.0.0 --port 4000
```

Open `http://localhost:4000/docs` for interactive API documentation.

## Example

```powershell
$body = @{ url = "https://example.com" } | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:4000/link-analysis" -Method Post -ContentType "application/json" -Body $body
```

Private, loopback, link-local, reserved, and local-network URLs are rejected to reduce SSRF risk. HTTP redirects are revalidated before following.