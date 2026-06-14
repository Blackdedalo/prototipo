from fastapi import APIRouter, HTTPException
from httpx import HTTPError

from app.schemas import ChatRequest, ChatResponse
from app.services.ai_service import get_provider


router = APIRouter(prefix="/api/ai", tags=["ai"])


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    provider = get_provider(request.provider)
    context = {**request.context, "_current_step": request.current_step}
    try:
        result = await provider.chat([message.model_dump() for message in request.messages], context)
    except HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"No se pudo conectar con el proveedor IA: {exc}") from exc
    return ChatResponse(provider=provider.name, **result)
