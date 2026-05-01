from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
import httpx
import json
from app.config import get_settings
from app.models.schemas import ChatRequest
from app.services.auth_service import require_admin

router = APIRouter(prefix="/chat", tags=["chat"])


def _provider_config(provider: str) -> tuple[str, str, str]:
    settings = get_settings()
    if provider.lower() == "b":
        return settings.ai_b_base_url, settings.ai_b_api_key, settings.ai_b_model
    return settings.ai_a_base_url, settings.ai_a_api_key, settings.ai_a_model


@router.post("", dependencies=[Depends(require_admin)])
async def chat(payload: ChatRequest):
    base_url, api_key, model = _provider_config(payload.provider)
    if not base_url or not api_key or not model:
        # 开发占位，避免无配置时报 500。
        text = "AI 端点尚未配置。请在 .env 中配置 AI_A_* 或 AI_B_*。"
        if payload.stream:
            async def fake_stream():
                yield f"data: {json.dumps({'content': text}, ensure_ascii=False)}\n\n"
                yield "data: [DONE]\n\n"
            return StreamingResponse(fake_stream(), media_type="text/event-stream")
        return {"content": text}

    url = base_url.rstrip("/") + "/chat/completions"
    body = {
        "model": model,
        "messages": [m.model_dump() for m in payload.messages],
        "stream": payload.stream,
    }
    headers = {"Authorization": f"Bearer {api_key}"}

    if payload.stream:
        async def proxy():
            async with httpx.AsyncClient(timeout=None) as client:
                async with client.stream("POST", url, json=body, headers=headers) as response:
                    async for chunk in response.aiter_text():
                        yield chunk
        return StreamingResponse(proxy(), media_type="text/event-stream")

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(url, json=body, headers=headers)
        if response.status_code >= 400:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        return response.json()
