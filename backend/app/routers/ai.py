from fastapi import APIRouter, HTTPException
from httpx import HTTPError, HTTPStatusError

from app.schemas import ChatRequest, ChatResponse
from app.services.ai_service import get_provider


router = APIRouter(prefix="/api/ai", tags=["ai"])


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    provider = get_provider(request.provider)
    context = {**request.context, "_current_step": request.current_step}
    try:
        result = await provider.chat([message.model_dump() for message in request.messages], context)
    except HTTPStatusError as exc:
        detail = exc.response.text or exc.response.reason_phrase or str(exc)
        raise HTTPException(
            status_code=502,
            detail=f"El proveedor IA respondio con error {exc.response.status_code}: {detail}",
        ) from exc
    except HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"No se pudo conectar con el proveedor IA: {exc}") from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error interno consultando la IA: {exc}") from exc
    return ChatResponse(provider=provider.name, **result)
