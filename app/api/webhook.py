from fastapi import APIRouter, Request, BackgroundTasks
from app.flows.manager import FlowManager
import logging
import json

logger = logging.getLogger(__name__)

router = APIRouter()
flow_manager = FlowManager()

@router.post("/megaapi")
async def webhook_megaapi(request: Request, background_tasks: BackgroundTasks):
    try:
        data = await request.json()
        
        # LOG DETALHADO: Ver o que está chegando do webhook
        logger.info("=" * 60)
        logger.info("WEBHOOK RECEBIDO DA MEGAAPI")
        logger.info("=" * 60)
        logger.info(f"Payload completo: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        # Processar em background para responder rápido ao webhook (200 OK)
        background_tasks.add_task(flow_manager.handle_message, data)
        
        return {"status": "received"}
    except Exception as e:
        logger.error(f"ERRO ao processar webhook: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}
