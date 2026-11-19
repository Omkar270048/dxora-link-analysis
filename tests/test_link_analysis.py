import asyncio
import logging
from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.main import app
from app.schemas import Analysis, Brand, GeneratedWebsiteAnalysis
from app.services import llm_service
from app import main as main_module
from app.utils.validators import validate_url


client = TestClient(app)


def test_invalid_url_scheme_is_rejected():
    try:
        validate_url("ftp://example.com")
    except ValueError:
        return
    raise AssertionError("FTP URL should be rejected")


def test_private_url_is_rejected():
    try:
        validate_url("http://127.0.0.1")
    except ValueError:
        return
    raise AssertionError("Loopback URL should be rejected")


def test_link_analysis_requires_url():
    response = client.post("/link-analysis", json={})
    assert response.status_code == 422


def test_gemini_returns_structured_website_analysis(monkeypatch):
    expected = GeneratedWebsiteAnalysis(
        brand=Brand(
            name="GeeksforGeeks",
            category="Computer science education",
            summary="Programming tutorials and interview preparation.",
        ),
        analysis=Analysis(),
    )

    class FakeModels:
        async def generate_content(self, **kwargs):
            self.kwargs = kwargs
            return SimpleNamespace(parsed=expected, text=None)

    class FakeAsyncClient:
        def __init__(self):
            self.models = FakeModels()

        @property
        def aio(self):
            return self

        async def __aenter__(self):
            return self

        async def __aexit__(self, *_):
            return None

    fake_client = FakeAsyncClient()
    monkeypatch.setattr(llm_service, "GEMINI_API_KEY", "test-key")
    monkeypatch.setattr(llm_service.genai, "Client", lambda **_: fake_client)

    actual = asyncio.run(llm_service.analyze_content({
        "title": "GeeksforGeeks | Your All-in-One Learning Portal",
        "meta_description": "Programming articles and practice problems.",
        "headings": "Learn programming",
        "text": "Computer science tutorials for students and developers.",
    }))

    assert actual.brand.name == "GeeksforGeeks"
    assert fake_client.models.kwargs["model"] == llm_service.GEMINI_MODEL
    assert fake_client.models.kwargs["config"].response_mime_type == "application/json"
    assert fake_client.models.kwargs["config"].response_schema is GeneratedWebsiteAnalysis


def test_gemini_rejects_unparsed_text_instead_of_skipping_structured_output(monkeypatch):
    class FakeModels:
        async def generate_content(self, **kwargs):
            return SimpleNamespace(parsed=None, text='{"brand": {}, "analysis": {}}')

    class FakeAsyncClient:
        models = FakeModels()

        @property
        def aio(self):
            return self

        async def __aenter__(self):
            return self

        async def __aexit__(self, *_):
            return None

    monkeypatch.setattr(llm_service, "GEMINI_API_KEY", "test-key")
    monkeypatch.setattr(llm_service.genai, "Client", lambda **_: FakeAsyncClient())

    try:
        asyncio.run(llm_service.analyze_content({"title": "Example"}))
    except ValueError as exc:
        assert "response schema" in str(exc)
    else:
        raise AssertionError("Unparsed text should not be accepted as structured output")


def test_missing_gemini_key_does_not_return_generic_analysis(monkeypatch):
    monkeypatch.setattr(llm_service, "GEMINI_API_KEY", None)

    try:
        asyncio.run(llm_service.analyze_content({"title": "Example"}))
    except llm_service.GeminiConfigurationError as exc:
        assert "GEMINI_API_KEY" in str(exc)
    else:
        raise AssertionError("Missing Gemini credentials should fail explicitly")


def test_missing_gemini_key_returns_service_unavailable(monkeypatch):
    async def fake_extract_website(_):
        return {
            "url": "https://example.com",
            "title": "Example",
            "meta_description": "",
            "headings": "",
            "text": "Example website content.",
        }

    monkeypatch.setattr(main_module, "validate_url", lambda _: None)
    monkeypatch.setattr(main_module, "extract_website", fake_extract_website)
    monkeypatch.setattr(llm_service, "GEMINI_API_KEY", None)

    response = client.post("/link-analysis", json={"url": "https://example.com"})

    assert response.status_code == 503
    assert "GEMINI_API_KEY" in response.json()["detail"]


def test_gemini_failure_is_logged_and_identified(monkeypatch, caplog):
    async def fake_extract_website(_):
        return {
            "url": "https://example.com",
            "title": "Example",
            "meta_description": "",
            "headings": "",
            "text": "Example website content.",
        }

    async def fake_analyze_website(*_):
        raise RuntimeError("Gemini model request failed")

    monkeypatch.setattr(main_module, "validate_url", lambda _: None)
    monkeypatch.setattr(main_module, "extract_website", fake_extract_website)
    monkeypatch.setattr(main_module, "analyze_website", fake_analyze_website)

    with caplog.at_level(logging.ERROR, logger="app.main"):
        response = client.post("/link-analysis", json={"url": "https://example.com"})

    assert response.status_code == 502
    assert response.json()["detail"].startswith("Gemini analysis failed")
    assert "Gemini model request failed" in caplog.text