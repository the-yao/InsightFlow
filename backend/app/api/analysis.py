import json 

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.agent.graph import stream_agent

router = APIRouter(prefix="/analysis",tags=["analysis"])

@router.get("/stream")
async def stream_analysis(question: str):
    """SSE 流式接口：边分析边把每个节点的进度推给前端"""

    async def event_generator():
        #遍历 stream_agent 的每一段节点输出，包装成 SSE 格式
        async for node,output in stream_agent(question):
            #output 形如{"messages"：[消息对象]}，取出最后一条
            msg = output["messages"][-1]
            # getattr 防御式取值：ToolMessage 没有tool_calls 属性，直接.tool_calls会AttributeError
            tool_calls = getattr(msg,"tool_calls",None) or []
            event = {
                "node":node,                                          #哪个节点产出（agent/tools）      
                "content":msg.content,                                #干净的文本内容
                "tool_calls":[tc["name"] for tc in tool_calls],       #模型想调哪些工具（只给名字）
            }
            yield f"data: {json.dumps(event,ensure_ascii=False)}\n\n"               

    return StreamingResponse(event_generator(),media_type="text/event-stream")