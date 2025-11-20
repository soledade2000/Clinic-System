import asyncio
import websockets

# 👉 Cole aqui o token gerado no login
TOKEN = "SEU_TOKEN_JWT_AQUI"

async def listen():
    url = f"ws://127.0.0.1:8000/consultas/ws?token={TOKEN}"
    async with websockets.connect(url) as websocket:
        print("✅ Conectado ao WebSocket!")
        try:
            while True:
                msg = await websocket.recv()
                print("📩 Recebido:", msg)
        except websockets.ConnectionClosed:
            print("❌ Conexão fechada.")

if __name__ == "__main__":
    asyncio.run(listen())
