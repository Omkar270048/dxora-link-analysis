from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl


class LinkAnalysisRequest(BaseModel):
    url: HttpUrl


class Brand(BaseModel):
    name: str = ""
    category: str = ""
    summary: str = ""


class Competitor(BaseModel):
    name: str
    comparison: Optional[str] = None
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    source: str = "AI-generated suggestion"


class CompetitorAnalysis(BaseModel):
    brand_overview: str = ""
    main_category: str = ""
    main_products_services: List[str] = Field(default_factory=list)
    competitors: List[Competitor] = Field(default_factory=list)
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    competitive_advantages: List[str] = Field(default_factory=list)
    opportunities: List[str] = Field(default_factory=list)


class SearchQuery(BaseModel):
    query: str
    platforms: List[str] = Field(default_factory=list)
    intent: str = ""
    business_relevance: str = ""
    target_audience: str = ""


class SeoImprovements(BaseModel):
    primary_keyword: str = ""
    secondary_keywords: List[str] = Field(default_factory=list)
    long_tail_keywords: List[str] = Field(default_factory=list)
    business_keywords: List[str] = Field(default_factory=list)
    recommended_title: str = ""
    improved_title_structure: str = ""
    meta_description: str = ""
    supporting_content: List[str] = Field(default_factory=list)


class Service(BaseModel):
    name: str
    description: str = ""
    target_industry: str = ""
    target_customer: str = ""
    main_benefit: str = ""
    source: str = "Extracted from website"


class TargetAudience(BaseModel):
    primary_audience: List[str] = Field(default_factory=list)
    secondary_audience: List[str] = Field(default_factory=list)
    industries: List[str] = Field(default_factory=list)
    business_types: List[str] = Field(default_factory=list)
    customer_profiles: List[str] = Field(default_factory=list)
    geographical_focus: List[str] = Field(default_factory=list)
    customer_needs: List[str] = Field(default_factory=list)
    customer_interests: List[str] = Field(default_factory=list)
    recommended_segments: List[str] = Field(default_factory=list)


class Analysis(BaseModel):
    competitor_analysis: CompetitorAnalysis = Field(default_factory=CompetitorAnalysis)
    target_search_queries: List[SearchQuery] = Field(default_factory=list)
    seo_improvements: SeoImprovements = Field(default_factory=SeoImprovements)
    top_services: List[Service] = Field(default_factory=list)
    target_audience: TargetAudience = Field(default_factory=TargetAudience)


class LinkAnalysisResponse(BaseModel):
    success: bool = True
    website: str
    brand: Brand
    analysis: Analysis


class GeneratedWebsiteAnalysis(BaseModel):
    brand: Brand
    analysis: Analysis