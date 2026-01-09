from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from metagpt.api.orchestrator import orchestrator

router = APIRouter()

@router.websocket("/log")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    orchestrator.add_websocket(websocket)
    try:
        while True:
            # Keep connection alive, listen for client messages (optional)
            # We just need it open to push messages
            await websocket.receive_text()
    except WebSocketDisconnect:
        orchestrator.remove_websocket(websocket)
    except Exception:
        orchestrator.remove_websocket(websocket)
