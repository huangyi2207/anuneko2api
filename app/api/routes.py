from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import StreamingResponse
from app.models.protocol import (
    ChatCompletionRequest, ChatCompletionResponse, 
    ChatCompletionStreamResponse, ChatCompletionStreamChoice,
    ChatCompletionResponseChoice, Message, DeltaMessage
)
from app.core.client import anuneko_client
from app.core.config import settings
import uuid
import json

router = APIRouter()
security = HTTPBearer()

async def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """验证 Bearer Token"""
    token = credentials.credentials
    
    # 如果配置包含 "*"，则允许所有
    if "*" in settings.PROXY_API_KEYS:
        return token
        
    if token not in settings.PROXY_API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token

@router.post("/chat/completions")
async def chat_completions(
    request: ChatCompletionRequest, 
    _: str = Depends(verify_api_key)
):
    if not request.messages:
        raise HTTPException(status_code=400, detail="Messages cannot be empty")
    
    try:
        # 获取会话ID和待发送的文本
        chat_id, prompt = await anuneko_client.get_session_and_prompt(
            request.messages, 
            request.model
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    req_id = f"chatcmpl-{uuid.uuid4()}"

    # --- 流式响应 ---
    if request.stream:
        async def stream_generator():
            async for chunk_text in anuneko_client.chat_stream(chat_id, prompt):
                chunk_resp = ChatCompletionStreamResponse(
                    id=req_id,
                    model=request.model,
                    choices=[ChatCompletionStreamChoice(
                        index=0, 
                        delta=DeltaMessage(content=chunk_text),
                        finish_reason=None
                    )]
                )
                yield f"data: {chunk_resp.model_dump_json()}\n\n"
            
            # 结束标记
            final_resp = ChatCompletionStreamResponse(
                id=req_id,
                model=request.model,
                choices=[ChatCompletionStreamChoice(
                    index=0, 
                    delta=DeltaMessage(),
                    finish_reason="stop"
                )]
            )
            yield f"data: {final_resp.model_dump_json()}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(stream_generator(), media_type="text/event-stream")

    # --- 非流式响应 ---
    else:
        full_content = ""
        async for chunk_text in anuneko_client.chat_stream(chat_id, prompt):
            full_content += chunk_text
        
        return ChatCompletionResponse(
            id=req_id,
            model=request.model,
            choices=[ChatCompletionResponseChoice(
                index=0,
                message=Message(role="assistant", content=full_content)
            )]
        )

@router.get("/models")
async def list_models(_: str = Depends(verify_api_key)):
    return {
        "object": "list",
        "data": [
            {"id": "orange-cat", "object": "model", "owned_by": "anuneko"},
            {"id": "black-cat", "object": "model", "owned_by": "anuneko"},
        ]
    }