from typing import Dict, List


def get_brand_basics(content: Dict[str, str]) -> Dict[str, str]:
    title = content.get("title", "").strip()
    description = content.get("meta_description", "").strip()
    name = title.split("|")[0].split(" - ")[0].strip() if title else "Unknown Brand"
    return {
        "name": name or "Unknown Brand",
        "summary": description or "Website content was available but no business summary was identified.",
    }


def build_inferred_competitors(content: Dict[str, str]) -> List[dict]:
    name = get_brand_basics(content)["name"]
    text = content.get("text", "").lower()
    category = "The business category could not be identified with confidence."
    if any(word in text for word in ("software", "technology", "digital", "development")):
        category = "Technology and digital services"
    elif any(word in text for word in ("marketing", "advertising", "seo")):
        category = "Marketing and advertising"
    elif any(word in text for word in ("consult", "advis")):
        category = "Professional consulting"

    competitors = [{
        "name": "Competitors should be confirmed through market research",
        "comparison": f"Relevant competitors for {name} in {category}",
        "strengths": [],
        "weaknesses": [],
        "source": "AI-generated suggestion; verify before publication",
    }]
    return competitors