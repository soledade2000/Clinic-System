#app/core/websockets.py
from fastapi import WebSocket, WebSocketDisconnect, HTTPException, status
from typing import List
from app.core.security import decode_token
from app.database import get_db
from sqlalchemy.orm import Session

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket, token: str, db: Session):
        payload = decode_token(token)
        if not payload or payload.get("type") != "access":
            # lançar uma exceção que será convertida em 401 pelo endpoint que chama connect
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")
        sub = payload.get("sub")
        if not isinstance(sub, str):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido (sub ausente)")

        # Use websocket.state para guardar dados arbitrários
        websocket.state.user = sub
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()
