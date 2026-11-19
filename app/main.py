import logging

from fastapi import FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from google.genai.errors import APIError

from app.config import APP_NAME
from app.schemas import LinkAnalysisRequest, LinkAnalysisResponse
from app.services.analysis_service import analyze_website
from app.services.llm_service import GeminiConfigurationError
from app.services.website_extractor import extract_website
from app.utils.validators import validate_url

app = FastAPI(title=APP_NAME)
logger = logging.getLogger(__name__)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": jsonable_encoder(exc.errors())},
    )


@app.post("/link-analysis", response_model=LinkAnalysisResponse)
async def link_analysis(payload: LinkAnalysisRequest):
    url = str(payload.url)
    stage = "URL validation"
    try:
        validate_url(url)
        stage = "website fetch"
        content = await extract_website(url)
        stage = "Gemini analysis"
        return await analyze_website(content["url"], content)
    except ValueError as exc:
        if stage != "Gemini analysis":
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        logger.exception("Link analysis failed during %s", stage)
        raise HTTPException(
            status_code=502,
            detail="Gemini did not return valid structured analysis. See the server log for details.",
        ) from exc
    except GeminiConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except APIError as exc:
        logger.exception("Gemini API request failed")
        raise HTTPException(
            status_code=502,
            detail=(
                f"Gemini API request failed (HTTP {exc.code}, {exc.status}). "
                "Check GEMINI_API_KEY and GEMINI_MODEL; see the server log for details."
            ),
        ) from exc
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Link analysis failed during %s", stage)
        if "timed out" in str(exc).lower():
            detail = f"The {stage} request timed out. See the server log for details."
        elif stage == "website fetch":
            detail = "The website could not be fetched. See the server log for details."
        else:
            detail = "Gemini analysis failed. Check Gemini configuration and see the server log for details."
        raise HTTPException(status_code=502, detail=detail) from exc


