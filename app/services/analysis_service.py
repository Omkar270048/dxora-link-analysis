from typing import Dict

from app.schemas import LinkAnalysisResponse
from app.services.llm_service import analyze_content


async def analyze_website(website: str, content: Dict[str, str]) -> LinkAnalysisResponse:
    generated = await analyze_content(content)
    return LinkAnalysisResponse(
        website=website,
        brand=generated.brand,
        analysis=generated.analysis.model_copy(update={
            "target_search_queries": generated.analysis.target_search_queries[:5],
            "top_services": generated.analysis.top_services[:5],
        }),
    )