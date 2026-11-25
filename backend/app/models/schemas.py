from pydantic import BaseModel, HttpUrl, Field
from typing import Any

class AnalyzeRequest(BaseModel):
    url: HttpUrl
    force_refresh: bool = False

class Evidence(BaseModel):
    id: str
    source: str
    title: str
    detail: str
    url: str | None = None
    kind: str = "documental"

class AnalysisReport(BaseModel):
    id: int | None = None
    url: str
    resource_type: str
    identity: dict[str, Any]
    summary: str
    functionality: list[str] = []
    technical: dict[str, Any] = {}
    strengths: list[str] = []
    weaknesses: list[str] = []
    use_cases: list[str] = []
    categories: list[dict[str, Any]] = []
    requirements: list[str] = []
    security: list[str] = []
    conclusion: str
    evidence: list[Evidence] = []
    confidence: str = "limitada"
    provider: str = "none"
    created_at: str | None = None
    raw_data: dict[str, Any] = {}

class ProviderStatus(BaseModel):
    provider: str
    available: bool
    model: str | None = None
    detail: str
