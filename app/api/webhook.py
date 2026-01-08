from fastapi import APIRouter, Request, BackgroundTasks
from app.flows.manager import FlowManager

router = APIRouter()
flow_manager = FlowManager()

@router.post("/megaapi")
async def webhook_megaapi(request: Request, background_tasks: BackgroundTasks):
    data = await request.json()
    
    # Processar em background para responder rápido ao webhook (200 OK)
    background_tasks.add_task(flow_manager.handle_message, data)
    
    return {"status": "received"}
