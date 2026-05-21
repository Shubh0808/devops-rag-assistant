from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app import config
from app.ollama import generate_with_ollama, ollama_status
from app.rag import DevOpsRAG
from app.schemas import ChatRequest, ChatResponse, HealthResponse, IngestResponse

rag = DevOpsRAG()

app = FastAPI(
    title=config.APP_NAME,
    description="Free RAG chatbot for DevOps runbooks and incident reports.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(
        app=config.APP_NAME,
        status="ok",
        indexed_count=rag.count(),
        ollama=await ollama_status(),
    )


@app.post("/ingest", response_model=IngestResponse)
def ingest():
    indexed_count = rag.ingest()
    return IngestResponse(
        indexed_count=indexed_count,
        collection_name=config.COLLECTION_NAME,
        data_dir=str(config.DATA_DIR),
    )


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    sources = rag.search(question=question, top_k=request.top_k)
    prompt = rag.build_prompt(question=question, sources=sources)

    answer = await generate_with_ollama(prompt)
    if answer:
        model_used = f"ollama:{config.OLLAMA_MODEL}"
    else:
        answer = rag.fallback_answer(question=question, sources=sources)
        model_used = "retrieval-fallback"

    return ChatResponse(answer=answer, sources=sources, model_used=model_used)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)

