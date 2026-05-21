import httpx

from app import config


async def generate_with_ollama(prompt: str) -> str | None:
    payload = {
        "model": config.OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.2,
            "top_p": 0.9,
        },
    }

    try:
        async with httpx.AsyncClient(timeout=config.OLLAMA_TIMEOUT_SECONDS) as client:
            response = await client.post(f"{config.OLLAMA_BASE_URL}/api/generate", json=payload)
            response.raise_for_status()
    except httpx.HTTPError:
        return None

    answer = response.json().get("response", "").strip()
    return answer or None


async def ollama_status() -> dict:
    try:
        async with httpx.AsyncClient(timeout=2) as client:
            response = await client.get(f"{config.OLLAMA_BASE_URL}/api/tags")
            response.raise_for_status()
    except httpx.HTTPError:
        return {
            "available": False,
            "model": config.OLLAMA_MODEL,
        }

    models = response.json().get("models", [])
    model_names = [model.get("name") for model in models]

    return {
        "available": True,
        "model": config.OLLAMA_MODEL,
        "model_downloaded": config.OLLAMA_MODEL in model_names,
    }

