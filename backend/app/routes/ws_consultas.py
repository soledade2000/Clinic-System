#app/routes/ws_consultas
from fastapi import WebSocket, APIRouter, Query
from app.core.websockets import manager
from app.database import SessionLocal

router = APIRouter(prefix="/ws")

@router.websocket("/consultas")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(...)):
    db = SessionLocal()
    await manager.connect(websocket, token=token, db=db)
    try:
        while True:
            data = await websocket.receive_text()
            # processa mensagens se necessário
    except:
        manager.disconnect(websocket)
    finally:
        db.close()

