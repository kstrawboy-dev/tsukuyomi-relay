from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI()

# Connected clients (Android App & Dashboard)
connected_clients = set()
dashboard_clients = set()

@app.get("/")
async def root():
    return {"status": "Tsukuyomi Relay Server is Online 🚀"}

@app.websocket("/ws/app")
async def app_websocket(websocket: WebSocket):
    await websocket.accept()
    connected_clients.add(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Broadcast data from app to all connected dashboards
            for dash in dashboard_clients:
                await dash.send_text(f"[App Data]: {data}")
    except WebSocketDisconnect:
        connected_clients.remove(websocket)

@app.websocket("/ws/dashboard")
async def dashboard_websocket(websocket: WebSocket):
    await websocket.accept()
    dashboard_clients.add(websocket)
    try:
        while True:
            command = await websocket.receive_text()
            # Send command from dashboard to all connected Android apps
            for client in connected_clients:
                await client.send_text(command)
    except WebSocketDisconnect:
        dashboard_clients.remove(websocket)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=10000)
