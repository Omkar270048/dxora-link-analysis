import json
from typing import Dict

from google import genai
from google.genai import types

from app.config import GEMINI_API_KEY, GEMINI_MODEL
from app.schemas import GeneratedWebsiteAnalysis


class GeminiConfigurationError(Exception):
    pass


async def analyze_content(content: Dict[str, str]) -> GeneratedWebsiteAnalysis:
    if not GEMINI_API_KEY:
        raise GeminiConfigurationError(
            "GEMINI_API_KEY is not configured. Add it to .env and restart the API."
        )

    prompt = (
        "Analyze the supplied website for business positioning and SEO. "
        "Use the page title and description as metadata, not as the whole business category. "
        "Infer the actual brand name, category, products, services, target audience, and customer "
        "search language from the page text and headings. Do not copy the full title into keywords "
        "or search queries. Write search queries as natural phrases customers would actually use. "
        "Return exactly five distinct, relevant queries across Google, Facebook, Instagram, LinkedIn, "
        "and X. Base recommendations on the supplied page; use empty lists or state uncertainty when "
        "information is unavailable. Competitors must be clearly marked as AI-generated suggestions "
        "unless directly supported by the supplied content. Never invent search volume or ranking data. "
        "List up to five actual services found on the page; mark any inferred service as inferred. "
        "If the site is an educational content platform, analyze its learning resources and audiences "
        "rather than treating it as a generic business.\n\n"
        f"Website data:\n{json.dumps(content, ensure_ascii=False)}"
    )

    async with genai.Client(api_key=GEMINI_API_KEY).aio as client:
        response = await client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=(
                    "You are a careful website business and SEO analyst. Ground every conclusion "
                    "in the provided website content and return complete, useful structured data."
                ),
                response_mime_type="application/json",
                response_schema=GeneratedWebsiteAnalysis,
                temperature=0.2,
            ),
        )

    if response.parsed is None:
        raise ValueError("Gemini did not return an analysis matching the requested response schema.")
    return GeneratedWebsiteAnalysis.model_validate(response.parsed)