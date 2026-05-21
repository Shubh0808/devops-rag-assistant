from pydantic import BaseModel, Field


class Source(BaseModel):
    title: str
    source: str
    category: str
    snippet: str
    score: float


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=3, examples=["How do I troubleshoot CrashLoopBackOff?"])
    top_k: int = Field(4, ge=1, le=8)


class ChatResponse(BaseModel):
    answer: str
    sources: list[Source]
    model_used: str


class IngestResponse(BaseModel):
    indexed_count: int
    collection_name: str
    data_dir: str


class HealthResponse(BaseModel):
    app: str
    status: str
    indexed_count: int
    ollama: dict

