from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

app = FastAPI()

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>NEXUS — Control Center</title>
<style>
:root{
  --bg:#07090d; --panel:#0d1117; --panel2:#131a24; --line:rgba(255,255,255,.07);
  --txt:#e6edf7; --dim:#7d8899; --cyan:#22d3ee; --violet:#8b5cf6;
  --green:#22c55e; --red:#ef4444; --amber:#f59e0b;
}
*{margin:0;padding:0;box-sizing:border-box}
body{
  background:var(--bg); color:var(--txt); overflow:hidden;
  font-family:'Inter',system-ui,-apple-system,'Segoe UI',sans-serif;
  -webkit-font-smoothing:antialiased;
}
body::before{
  content:""; position:fixed; inset:0; pointer-events:none; z-index:0;
  background:
    radial-gradient(600px 400px at 15% 0%, rgba(34,211,238,.10), transparent 70%),
    radial-gradient(700px 500px at 90% 100%, rgba(139,92,246,.12), transparent 70%);
}
::-webkit-scrollbar{width:8px;height:8px}
::-webkit-scrollbar-thumb{background:#1c2432;border-radius:8px}
::-webkit-scrollbar-thumb:hover{background:#2a3546}

.app{display:grid;grid-template-columns:248px 1fr;height:100vh;position:relative;z-index:1}

/* ============ SIDEBAR ============ */
.sidebar{
  background:linear-gradient(180deg,#0b0f15,#080b10);
  border-right:1px solid var(--line);
  display:flex;flex-direction:column;padding:20px 14px;
}
.brand{display:flex;align-items:center;gap:12px;padding:4px 8px 22px}
.brand-mark{
  width:40px;height:40px;border-radius:12px;display:grid;place-items:center;
  font-weight:800;font-size:18px;color:#04121a;
  background:linear-gradient(135deg,var(--cyan),var(--violet));
  box-shadow:0 0 24px rgba(34,211,238,.35);
}
.brand-text b{display:block;font-size:15px;letter-spacing:.14em}
.brand-text span{font-size:10px;color:var(--dim);letter-spacing:.08em}

.nav{display:flex;flex-direction:column;gap:4px;flex:1}
.nav-item{
  display:flex;align-items:center;gap:12px;padding:11px 12px;border-radius:11px;
  background:transparent;border:1px solid transparent;color:var(--dim);
  font-size:13.5px;font-weight:500;cursor:pointer;text-align:left;
  transition:.18s; font-family:inherit;
}
.nav-item svg{width:18px;height:18px;stroke:currentColor;fill:none;stroke-width:1.7;
  stroke-linecap:round;stroke-linejoin:round;flex-shrink:0}
.nav-item:hover{background:rgba(255,255,255,.04);color:var(--txt)}
.nav-item.active{
  background:linear-gradient(90deg,rgba(34,211,238,.14),rgba(139,92,246,.10));
  border-color:rgba(34,211,238,.28); color:#fff;
  box-shadow:inset 0 0 20px rgba(34,211,238,.06);
}
.nav-item.active svg{stroke:var(--cyan)}

.side-foot{border-top:1px solid var(--line);padding-top:14px;margin-top:10px}
.demo-badge{
  font-size:9.5px;letter-spacing:.16em;text-align:center;padding:6px;border-radius:8px;
  color:var(--amber);background:rgba(245,158,11,.10);
  border:1px solid rgba(245,158,11,.25);margin-bottom:12px;font-weight:700;
}
.side-user{display:flex;align-items:center;gap:10px;padding:0 4px}
.side-user .ava{
  width:32px;height:32px;border-radius:50%;display:grid;place-items:center;
  background:linear-gradient(135deg,#1f2937,#111827);border:1px solid var(--line);
  font-size:11px;font-weight:700;color:var(--cyan);
}
.side-user small{display:block;font-size:10px;color:var(--dim)}
.side-user b{font-size:12px}

/* ============ MAIN ============ */
.main{display:flex;flex-direction:column;overflow:hidden}
.topbar{
  height:70px;flex-shrink:0;display:flex;align-items:center;justify-content:space-between;
  padding:0 28px;border-bottom:1px solid var(--line);
  background:rgba(10,13,18,.7);backdrop-filter:blur(14px);
}
.tb-left{display:flex;align-items:baseline;gap:10px}
.tb-left h1{font-size:19px;font-weight:650;letter-spacing:-.01em}
.crumb{font-size:12px;color:var(--dim)}
.tb-right{display:flex;align-items:center;gap:10px}
.chip{
  display:flex;align-items:center;gap:7px;font-size:11.5px;color:var(--dim);
  padding:7px 12px;border-radius:9px;border:1px solid var(--line);
  background:rgba(255,255,255,.02);font-variant-numeric:tabular-nums;
}
.chip.live{color:var(--green);border-color:rgba(34,197,94,.28);background:rgba(34,197,94,.08)}
.chip.live i{width:6px;height:6px;border-radius:50%;background:var(--green);
  box-shadow:0 0 8px var(--green);animation:pulse 1.6s infinite}
@keyframes pulse{50%{opacity:.25}}
.avatar-sm{
  width:34px;height:34px;border-radius:10px;display:grid;place-items:center;
  font-size:11px;font-weight:700;color:#04121a;
  background:linear-gradient(135deg,var(--cyan),var(--violet));
}

.views{flex:1;overflow-y:auto;padding:24px 28px 60px}
.view{display:none;animation:fade .28s ease}
.view.active{display:block}
@keyframes fade{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}

/* ============ CARDS / COMMON ============ */
.card{
  background:linear-gradient(180deg,rgba(255,255,255,.035),rgba(255,255,255,.012));
  border:1px solid var(--line);border-radius:16px;
  box-shadow:0 12px 30px -14px rgba(0,0,0,.8);
}
.sec-head{display:flex;align-items:center;justify-content:space-between;margin:26px 0 14px}
.sec-head h2{font-size:13px;font-weight:650;letter-spacing:.06em;text-transform:uppercase;color:#b9c4d4}
.btn{
  font-family:inherit;font-size:12px;font-weight:600;padding:8px 14px;border-radius:9px;
  border:1px solid var(--line);background:rgba(255,255,255,.04);color:var(--txt);
  cursor:pointer;transition:.18s;
}
.btn:hover{background:rgba(255,255,255,.09);border-color:rgba(34,211,238,.3)}
.btn.grad{
  background:linear-gradient(135deg,var(--cyan),var(--violet));color:#04121a;border:none;
  box-shadow:0 6px 20px -6px rgba(34,211,238,.5);
}
.btn.grad:hover{filter:brightness(1.1)}

/* ============ STATS ============ */
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:14px}
.stat{
  display:flex;align-items:center;gap:14px;padding:18px;border-radius:16px;
  border:1px solid var(--line);
  background:linear-gradient(180deg,rgba(255,255,255,.04),rgba(255,255,255,.01));
  transition:.2s;
}
.stat:hover{border-color:rgba(34,211,238,.3);transform:translateY(-2px)}
.stat-ico{
  width:42px;height:42px;border-radius:12px;display:grid;place-items:center;font-size:17px;
  background:rgba(34,211,238,.10);border:1px solid rgba(34,211,238,.2);
}
.stat-k{font-size:11px;color:var(--dim);letter-spacing:.05em;text-transform:uppercase}
.stat-v{font-size:22px;font-weight:700;letter-spacing:-.02em;margin-top:2px}
.stat-v span{font-size:13px;color:var(--dim);font-weight:500}

/* ============ DEVICE CARDS ============ */
.devices{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:14px}
.device-card{
  padding:18px;border-radius:16px;cursor:pointer;transition:.2s;position:relative;
  border:1px solid var(--line);
  background:linear-gradient(180deg,rgba(255,255,255,.04),rgba(255,255,255,.01));
}
.device-card:hover{border-color:rgba(34,211,238,.35);transform:translateY(-3px);
  box-shadow:0 18px 40px -20px rgba(34,211,238,.4)}
.device-card.selected{border-color:rgba(34,211,238,.55);
  box-shadow:0 0 0 1px rgba(34,211,238,.25),0 18px 40px -20px rgba(34,211,238,.4)}
.device-card.offline{opacity:.55}
.dc-top{display:flex;align-items:center;gap:12px;margin-bottom:16px}
.dc-ico{width:38px;height:38px;border-radius:11px;display:grid;place-items:center;font-size:16px;
  background:rgba(139,92,246,.12);border:1px solid rgba(139,92,246,.25)}
.dc-meta h3{font-size:14px;font-weight:600}
.dc-meta p{font-size:11px;color:var(--dim);margin-top:2px}
.dot{width:8px;height:8px;border-radius:50%;margin-left:auto}
.dot.online{background:var(--green);box-shadow:0 0 10px var(--green)}
.dot.offline{background:#4b5563}
.dc-bat{display:flex;align-items:center;gap:10px;margin-bottom:14px}
.bar{flex:1;height:6px;border-radius:6px;background:#1a2130;overflow:hidden}
.bar i{display:block;height:100%;border-radius:6px;transition:width .5s}
.dc-bat span{font-size:11.5px;color:var(--dim);font-variant-numeric:tabular-nums}
.dc-info{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;padding-top:12px;
  border-top:1px solid var(--line)}
.dc-info label{display:block;font-size:9.5px;color:var(--dim);letter-spacing:.08em;text-transform:uppercase;margin-bottom:3px}
.dc-info b{font-size:11.5px;font-weight:600;font-variant-numeric:tabular-nums}
.dc-info b.ok{color:var(--red)} .dc-info b.no{color:var(--green)}

/* ============ FEED ============ */
.feed{display:flex;flex-direction:column;gap:2px;padding:6px 0}
.feed-item{display:flex;align-items:center;gap:12px;padding:11px 14px;border-radius:11px;font-size:12.5px}
.feed-item:hover{background:rgba(255,255,255,.03)}
.feed-item .fi{width:28px;height:28px;border-radius:8px;display:grid;place-items:center;font-size:12px;
  background:rgba(34,211,238,.08);border:1px solid rgba(34,211,238,.16);flex-shrink:0}
.feed-item span{color:var(--dim)}
.feed-item b{font-weight:600;color:var(--txt)}
.feed-item time{margin-left:auto;font-size:11px;color:#525d6d;white-space:nowrap}

/* ============ CONTACTS ============ */
.toolbar{display:flex;gap:10px;margin-bottom:16px;flex-wrap:wrap}
.input{
  flex:1;min-width:200px;padding:11px 15px;border-radius:11px;font-family:inherit;font-size:13px;
  background:rgba(255,255,255,.03);border:1px solid var(--line);color:var(--txt);outline:none;
}
.input:focus{border-color:rgba(34,211,238,.45);box-shadow:0 0 0 3px rgba(34,211,238,.08)}
.input::placeholder{color:#4d5766}
.contacts{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:12px}
.contact{
  display:flex;align-items:center;gap:13px;padding:14px;border-radius:14px;cursor:pointer;
  border:1px solid var(--line);transition:.18s;
  background:linear-gradient(180deg,rgba(255,255,255,.035),rgba(255,255,255,.008));
}
.contact:hover{border-color:rgba(34,211,238,.32);transform:translateY(-2px)}
.c-ava{
  width:40px;height:40px;border-radius:12px;display:grid;place-items:center;flex-shrink:0;
  font-size:13px;font-weight:700;color:#04121a;
  background:linear-gradient(135deg,var(--cyan),var(--violet));
}
.c-ava.alt{background:linear-gradient(135deg,#f59e0b,#ef4444)}
.c-ava.alt2{background:linear-gradient(135deg,#22c55e,#0ea5e9)}
.c-info{min-width:0}
.c-info h4{font-size:13.5px;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.c-info p{font-size:11.5px;color:var(--dim);font-variant-numeric:tabular-nums;margin-top:2px}
.c-tag{margin-left:auto;font-size:9.5px;padding:4px 9px;border-radius:20px;letter-spacing:.06em;
  color:var(--cyan);background:rgba(34,211,238,.10);border:1px solid rgba(34,211,238,.2);
  white-space:nowrap}

/* ============ MESSAGES ============ */
.msg-wrap{display:grid;grid-template-columns:300px 1fr;gap:14px;height:calc(100vh - 190px)}
.convos{padding:8px;overflow-y:auto}
.convo{
  display:flex;gap:11px;align-items:center;padding:12px;border-radius:12px;cursor:pointer;transition:.15s;
}
.convo:hover{background:rgba(255,255,255,.04)}
.convo.active{background:linear-gradient(90deg,rgba(34,211,238,.12),rgba(139,92,246,.08));
  border:1px solid rgba(34,211,238,.25)}
.convo .c-info h4{font-size:13px}
.convo .c-info p{font-size:11.5px;color:var(--dim);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:150px}
.convo-meta{margin-left:auto;text-align:right;flex-shrink:0}
.convo-meta small{font-size:10px;color:#525d6d;display:block}
.unread{margin-top:4px;display:inline-grid;place-items:center;min-width:18px;height:18px;padding:0 5px;
  border-radius:9px;font-size:10px;font-weight:700;color:#04121a;
  background:linear-gradient(135deg,var(--cyan),var(--violet))}
.chat{display:flex;flex-direction:column;overflow:hidden}
.chat-head{padding:16px 20px;border-bottom:1px solid var(--line);display:flex;align-items:center;gap:12px}
.chat-body{flex:1;overflow-y:auto;padding:20px;display:flex;flex-direction:column;gap:10px}
.bubble{max-width:70%;padding:11px 15px;border-radius:14px;font-size:12.8px;line-height:1.5}
.bubble.them{align-self:flex-start;background:rgba(255,255,255,.055);border:1px solid var(--line);
  border-bottom-left-radius:5px}
.bubble.me{align-self:flex-end;color:#04121a;font-weight:500;
  background:linear-gradient(135deg,var(--cyan),#4dd0f0);border-bottom-right-radius:5px}
.bubble time{display:block;font-size:9.5px;opacity:.55;margin-top:4px}
.chat-input{padding:14px 16px;border-top:1px solid var(--line);display:flex;gap:10px}

/* ============ DEVICE DETAIL ============ */
.detail-grid{display:grid;grid-template-columns:1fr 340px;gap:14px}
.info-list{padding:6px 0}
.info-row{display:flex;justify-content:space-between;align-items:center;padding:13px 20px;font-size:12.5px}
.info-row:hover{background:rgba(255,255,255,.025)}
.info-row+.info-row{border-top:1px solid rgba(255,255,255,.04)}
.info-row span{color:var(--dim)}
.info-row b{font-weight:600;font-variant-numeric:tabular-nums}
.pill{font-size:10.5px;padding:3px 10px;border-radius:20px;font-weight:700;letter-spacing:.04em}
.pill.g{color:var(--green);background:rgba(34,197,94,.12);border:1px solid rgba(34,197,94,.25)}
.pill.r{color:var(--red);background:rgba(239,68,68,.12);border:1px solid rgba(239,68,68,.25)}
.pill.y{color:var(--amber);background:rgba(245,158,11,.12);border:1px solid rgba(245,158,11,.25)}

.ring-wrap{padding:22px;display:flex;flex-direction:column;align-items:center;gap:14px}
.ring{
  width:130px;height:130px;border-radius:50%;display:grid;place-items:center;position:relative;
  background:conic-gradient(var(--green) 0 82%, #182030 82% 100%);
}
.ring::after{content:"";position:absolute;inset:9px;border-radius:50%;background:#0b0f15}
.ring-in{position:relative;z-index:1;text-align:center}
.ring-in b{font-size:26px;font-weight:700;letter-spacing:-.02em}
.ring-in small{display:block;font-size:10px;color:var(--dim);letter-spacing:.1em;text-transform:uppercase}

.map{
  height:190px;border-radius:14px;position:relative;overflow:hidden;
  background:
    linear-gradient(rgba(34,211,238,.05) 1px,transparent 1px) 0 0/26px 26px,
    linear-gradient(90deg,rgba(34,211,238,.05) 1px,transparent 1px) 0 0/26px 26px,
    radial-gradient(circle at 50% 55%,#101a24,#080c11);
  border:1px solid var(--line);
}
.pin{position:absolute;top:52%;left:50%;transform:translate(-50%,-50%)}
.pin::before{content:"";position:absolute;width:52px;height:52px;border-radius:50%;
  border:2px solid rgba(34,211,238,.5);left:50%;top:50%;transform:translate(-50%,-50%);
  animation:ripple 2.2s infinite}
@keyframes ripple{0%{transform:translate(-50%,-50%) scale(.4);opacity:.9}
  100%{transform:translate(-50%,-50%) scale(1.6);opacity:0}}
.pin-dot{width:14px;height:14px;border-radius:50%;background:var(--cyan);
  box-shadow:0 0 16px var(--cyan);position:relative;z-index:1}

/* ============ GALLERY ============ */
.tabs{display:flex;gap:6px;margin-bottom:16px}
.tab{padding:8px 16px;border-radius:9px;font-size:12px;font-weight:600;cursor:pointer;
  border:1px solid var(--line);background:transparent;color:var(--dim);font-family:inherit;transition:.18s}
.tab.active{background:rgba(34,211,238,.12);border-color:rgba(34,211,238,.35);color:var(--cyan)}
.grid-media{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:10px}
.media{
  aspect-ratio:1;border-radius:13px;position:relative;overflow:hidden;cursor:pointer;
  border:1px solid var(--line);transition:.2s;display:grid;place-items:center;
}
.media:hover{transform:scale(1.03);border-color:rgba(34,211,238,.4)}
.media::after{content:"";position:absolute;inset:0;
  background:linear-gradient(180deg,transparent 45%,rgba(0,0,0,.75))}
.media .lbl{position:absolute;bottom:9px;left:11px;right:11px;font-size:10.5px;
  color:#c9d4e3;z-index:2;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.media .play{position:absolute;z-index:2;width:38px;height:38px;border-radius:50%;
  background:rgba(0,0,0,.55);backdrop-filter:blur(6px);border:1px solid rgba(255,255,255,.25);
  display:grid;place-items:center;font-size:13px;color:#fff}
.media .dur{position:absolute;top:9px;right:10px;z-index:2;font-size:9.5px;padding:2px 7px;
  border-radius:6px;background:rgba(0,0,0,.65);color:#dbe4f0}

/* ============ FILES ============ */
.file-row{
  display:grid;grid-template-columns:32px 1fr 110px 130px 40px;align-items:center;gap:14px;
  padding:13px 18px;font-size:12.5px;transition:.15s;cursor:pointer;
}
.file-row:hover{background:rgba(255,255,255,.03)}
.file-row+.file-row{border-top:1px solid rgba(255,255,255,.04)}
.file-head{font-size:10px;letter-spacing:.1em;text-transform:uppercase;color:#525d6d;
  padding:12px 18px;border-bottom:1px solid var(--line);font-weight:700}
.f-ico{width:30px;height:30px;border-radius:9px;display:grid;place-items:center;font-size:13px;
  background:rgba(34,211,238,.08);border:1px solid rgba(34,211,238,.16)}
.f-name{font-weight:500}
.f-dim{color:var(--dim);font-variant-numeric:tabular-nums;font-size:11.5px}
.f-more{color:#3d4653;text-align:center;font-size:16px}

/* ============ SCREEN MIRROR ============ */
.mirror-wrap{display:grid;grid-template-columns:1fr 300px;gap:20px;align-items:start}
.mirror-stage{display:flex;justify-content:center;padding:26px;border-radius:16px;
  border:1px solid var(--line);
  background:radial-gradient(circle at 50% 30%,rgba(34,211,238,.07),transparent 65%),#0a0e14}
.phone{
  width:250px;height:500px;border-radius:38px;padding:9px;position:relative;
  background:linear-gradient(160deg,#232b3a,#0e131b);
  border:1px solid rgba(255,255,255,.1);
  box-shadow:0 40px 80px -30px rgba(0,0,0,.9),0 0 50px -20px rgba(34,211,238,.5);
}
.phone::before{content:"";position:absolute;top:16px;left:50%;transform:translateX(-50%);
  width:74px;height:7px;border-radius:6px;background:#0a0d12;z-index:5}
.phone-screen{
  width:100%;height:100%;border-radius:30px;overflow:hidden;position:relative;
  background:linear-gradient(160deg,#152238,#0b1220 55%,#131024);
}
.ps-status{display:flex;justify-content:space-between;padding:16px 20px 0;font-size:10px;
  color:#c3cede;font-weight:600;position:relative;z-index:2}
.ps-wall{position:absolute;inset:0;
  background:
    radial-gradient(circle at 30% 20%,rgba(139,92,246,.55),transparent 55%),
    radial-gradient(circle at 75% 70%,rgba(34,211,238,.45),transparent 55%);
  filter:blur(6px)}
.ps-time{position:relative;z-index:2;text-align:center;margin-top:64px}
.ps-time b{font-size:46px;font-weight:200;letter-spacing:-.03em;color:#fff}
.ps-time span{display:block;font-size:11px;color:#a9b6c8;letter-spacing:.1em;margin-top:2px}
.ps-apps{position:absolute;bottom:26px;left:0;right:0;z-index:2;
  display:grid;grid-template-columns:repeat(4,1fr);gap:14px 8px;padding:0 22px}
.ps-app{aspect-ratio:1;border-radius:13px;background:rgba(255,255,255,.14);
  border:1px solid rgba(255,255,255,.18);backdrop-filter:blur(6px)}
.ps-app:nth-child(2){background:linear-gradient(135deg,rgba(34,211,238,.65),rgba(14,165,233,.5))}
.ps-app:nth-child(5){background:linear-gradient(135deg,rgba(139,92,246,.65),rgba(236,72,153,.5))}
.ps-app:nth-child(7){background:linear-gradient(135deg,rgba(34,197,94,.6),rgba(16,185,129,.5))}
.scan{position:absolute;left:0;right:0;height:70px;z-index:3;pointer-events:none;
  background:linear-gradient(180deg,transparent,rgba(34,211,238,.12),transparent);
  animation:scan 3.4s linear infinite}
@keyframes scan{0%{top:-70px}100%{top:100%}}
.live-badge{display:inline-flex;align-items:center;gap:7px;font-size:10.5px;font-weight:700;
  letter-spacing:.1em;color:var(--red);padding:6px 12px;border-radius:20px;
  background:rgba(239,68,68,.12);border:1px solid rgba(239,68,68,.3)}
.live-badge i{width:6px;height:6px;border-radius:50%;background:var(--red);
  box-shadow:0 0 8px var(--red);animation:pulse 1.2s infinite}
.side-panel{padding:20px}

/* ============ CONTROLS ============ */
.controls{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:14px}
.ctrl{
  padding:18px;border-radius:16px;border:1px solid var(--line);transition:.2s;
  background:linear-gradient(180deg,rgba(255,255,255,.04),rgba(255,255,255,.01));
  display:flex;align-items:center;gap:14px;
}
.ctrl:hover{border-color:rgba(34,211,238,.3);transform:translateY(-2px)}
.ctrl-ico{width:44px;height:44px;border-radius:13px;display:grid;place-items:center;font-size:19px;
  background:rgba(139,92,246,.12);border:1px solid rgba(139,92,246,.25);flex-shrink:0;transition:.2s}
.ctrl.on .ctrl-ico{background:rgba(34,211,238,.16);border-color:rgba(34,211,238,.5);
  box-shadow:0 0 20px rgba(34,211,238,.35)}
.ctrl-txt{flex:1;min-width:0}
.ctrl-txt h4{font-size:13px;font-weight:600}
.ctrl-txt p{font-size:11px;color:var(--dim);margin-top:3px}
.switch{
  width:44px;height:25px;border-radius:20px;background:#1a2130;position:relative;flex-shrink:0;
  border:1px solid var(--line);cursor:pointer;transition:.22s;
}
.switch::after{content:"";position:absolute;width:17px;height:17px;border-radius:50%;
  background:#5b6676;top:3px;left:3px;transition:.22s}
.ctrl.on .switch{background:linear-gradient(135deg,var(--cyan),var(--violet));border-color:transparent}
.ctrl.on .switch::after{left:22px;background:#fff}
.mini-btn{
  padding:7px 12px;border-radius:9px;font-size:11px;font-weight:600;cursor:pointer;
  font-family:inherit;color:var(--txt);background:rgba(255,255,255,.05);
  border:1px solid var(--line);transition:.18s;flex-shrink:0;
}
.mini-btn:hover{background:rgba(34,211,238,.15);border-color:rgba(34,211,238,.4);color:var(--cyan)}

/* ============ KEYSTROKES ============ */
.krow{display:grid;grid-template-columns:32px 1fr auto;gap:12px;padding:13px 18px;align-items:start}
.krow:hover{background:rgba(255,255,255,.03)}
.krow+.krow{border-top:1px solid rgba(255,255,255,.04)}
.k-app{width:30px;height:30px;border-radius:9px;display:grid;place-items:center;font-size:13px;
  background:rgba(34,211,238,.08);border:1px solid rgba(34,211,238,.16)}
.k-body{min-width:0}
.k-win{font-size:11px;color:var(--dim);margin-bottom:5px;white-space:nowrap;
  overflow:hidden;text-overflow:ellipsis}
.k-text{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:11.8px;
  color:#bfe6f5;background:rgba(34,211,238,.055);border:1px solid rgba(34,211,238,.14);
  border-radius:7px;padding:6px 10px;display:inline-block;max-width:100%;
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis;vertical-align:bottom}
.caret{display:inline-block;width:1px;height:11px;background:var(--cyan);margin-left:3px;
  vertical-align:-1px;animation:blink 1.1s steps(1) infinite}
@keyframes blink{50%{opacity:0}}
.k-time{font-size:10.5px;color:#525d6d;font-variant-numeric:tabular-nums;
  white-space:nowrap;padding-top:2px}
.mini-bar{height:6px;border-radius:6px;background:#1a2130;overflow:hidden;margin-top:7px}
.mini-bar i{display:block;height:100%;border-radius:6px;
  background:linear-gradient(90deg,var(--cyan),var(--violet))}
.app-stat{margin-bottom:15px}
.app-stat:last-child{margin-bottom:0}
.app-stat-top{display:flex;justify-content:space-between;font-size:11.5px}
.app-stat-top span{color:var(--dim)}

/* ============ TOAST ============ */
.toasts{position:fixed;bottom:24px;right:24px;display:flex;flex-direction:column;gap:10px;z-index:99}
.toast{
  min-width:250px;padding:13px 17px;border-radius:13px;font-size:12.5px;
  background:rgba(16,22,30,.96);border:1px solid rgba(34,211,238,.35);
  backdrop-filter:blur(14px);box-shadow:0 20px 40px -18px rgba(0,0,0,.9);
  display:flex;align-items:center;gap:11px;animation:slideIn .3s ease;
}
.toast i{width:7px;height:7px;border-radius:50%;background:var(--cyan);
  box-shadow:0 0 10px var(--cyan);flex-shrink:0}
@keyframes slideIn{from{opacity:0;transform:translateX(40px)}to{opacity:1;transform:none}}

@media(max-width:1080px){
  .app{grid-template-columns:76px 1fr}
  .brand-text,.nav-item span,.side-foot .side-user>div:last-child{display:none}
  .nav-item{justify-content:center;padding:13px}
  .detail-grid,.msg-wrap,.mirror-wrap{grid-template-columns:1fr}
}
</style>
</head>
<body>

<div class="app">
  <!-- ================= SIDEBAR ================= -->
  <aside class="sidebar">
    <div class="brand">
      <div class="brand-mark">N</div>
      <div class="brand-text"><b>NEXUS</b><span>CONTROL CENTER</span></div>
    </div>

    <nav class="nav">
      <button class="nav-item active" data-view="dashboard">
        <svg viewBox="0 0 24 24"><rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/></svg>
        <span>Dashboard</span>
      </button>
      <button class="nav-item" data-view="contacts">
        <svg viewBox="0 0 24 24"><circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 3.6-6.5 8-6.5s8 2.5 8 6.5"/></svg>
        <span>Contacts</span>
      </button>
      <button class="nav-item" data-view="messages">
        <svg viewBox="0 0 24 24"><path d="M21 11.5a8.4 8.4 0 0 1-9 8.4 9 9 0 0 1-4-.9L3 21l1.9-4.6A8.4 8.4 0 1 1 21 11.5z"/></svg>
        <span>Messages</span>
      </button>
      <button class="nav-item" data-view="device">
        <svg viewBox="0 0 24 24"><rect x="6" y="2" width="12" height="20" rx="3"/><path d="M10.5 18h3"/></svg>
        <span>Device</span>
      </button>
      <button class="nav-item" data-view="gallery">
        <svg viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="2.5"/><circle cx="8.5" cy="8.5" r="1.6"/><path d="M21 15.5l-5-5L5 21"/></svg>
        <span>Gallery</span>
      </button>
      <button class="nav-item" data-view="files">
        <svg viewBox="0 0 24 24"><path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/></svg>
        <span>Files</span>
      </button>
      <button class="nav-item" data-view="keylog">
        <svg viewBox="0 0 24 24"><rect x="2" y="6" width="20" height="12" rx="2.5"/><path d="M6 10h.01M10 10h.01M14 10h.01M18 10h.01M6 14h.01M18 14h.01M9.5 14h5"/></svg>
        <span>Keystrokes</span>
      </button>
      <button class="nav-item" data-view="screen">
        <svg viewBox="0 0 24 24"><rect x="2" y="4" width="20" height="13" rx="2.5"/><path d="M8 21h8M12 17v4"/></svg>
        <span>Screen</span>
      </button>
      <button class="nav-item" data-view="controls">
        <svg viewBox="0 0 24 24"><path d="M4 7h16M4 12h16M4 17h16"/><circle cx="9" cy="7" r="2.2" fill="#0b0f15"/><circle cx="15" cy="12" r="2.2" fill="#0b0f15"/><circle cx="7" cy="17" r="2.2" fill="#0b0f15"/></svg>
        <span>Controls</span>
      </button>
    </nav>

    <div class="side-foot">
      <div class="demo-badge">DEMO — FAKE DATA</div>
      <div class="side-user">
        <div class="ava">OP</div>
        <div><b>Operator</b><small>Admin access</small></div>
      </div>
    </div>
  </aside>

  <!-- ================= MAIN ================= -->
  <main class="main">
    <header class="topbar">
      <div class="tb-left">
        <h1 id="pageTitle">Dashboard</h1>
        <span class="crumb" id="pageCrumb">/ overview</span>
      </div>
      <div class="tb-right">
        <div class="chip live"><i></i> 3 online</div>
        <div class="chip"><span id="clock">--:--:--</span></div>
        <div class="avatar-sm">OP</div>
      </div>
    </header>

    <div class="views">

      <!-- ---------- DASHBOARD ---------- -->
      <section class="view active" id="v-dashboard">
        <div class="stats">
          <div class="stat"><div class="stat-ico">📶</div><div>
            <div class="stat-k">Devices Online</div><div class="stat-v">3<span>/4</span></div></div></div>
          <div class="stat"><div class="stat-ico">🔋</div><div>
            <div class="stat-k">Avg Battery</div><div class="stat-v">68<span>%</span></div></div></div>
          <div class="stat"><div class="stat-ico">💾</div><div>
            <div class="stat-k">Data Synced</div><div class="stat-v">1.24<span>GB</span></div></div></div>
          <div class="stat"><div class="stat-ico">🔔</div><div>
            <div class="stat-k">Alerts</div><div class="stat-v">2<span>new</span></div></div></div>
        </div>

        <div class="sec-head">
          <h2>Connected Devices</h2>
          <button class="btn ghost" onclick="toast('Device list refreshed')">Refresh</button>
        </div>
        <div class="devices" id="deviceGrid"></div>

        <div class="sec-head"><h2>Recent Activity</h2></div>
        <div class="card feed">
          <div class="feed-item"><div class="fi">🔓</div>
            <div><b>Pixel 7 Pro</b> <span>— screen unlocked</span></div><time>2m ago</time></div>
          <div class="feed-item"><div class="fi">📷</div>
            <div><b>Redmi Note 12</b> <span>— 3 new photos captured</span></div><time>14m ago</time></div>
          <div class="feed-item"><div class="fi">📡</div>
            <div><b>iPhone 13</b> <span>— location updated</span></div><time>38m ago</time></div>
          <div class="feed-item"><div class="fi">🔋</div>
            <div><b>Pixel 7 Pro</b> <span>— charging started (82%)</span></div><time>1h ago</time></div>
          <div class="feed-item"><div class="fi">💬</div>
            <div><b>Redmi Note 12</b> <span>— 2 new SMS received</span></div><time>2h ago</time></div>
        </div>
      </section>

      <!-- ---------- CONTACTS ---------- -->
      <section class="view" id="v-contacts">
        <div class="toolbar">
          <input class="input" id="contactSearch" placeholder="Search contacts by name or number...">
          <button class="btn grad" onclick="toast('Contact sync requested')">Sync Contacts</button>
        </div>
        <div class="contacts" id="contactGrid"></div>
      </section>

      <!-- ---------- MESSAGES ---------- -->
      <section class="view" id="v-messages">
        <div class="msg-wrap">
          <div class="card convos" id="convoList"></div>
          <div class="card chat">
            <div class="chat-head" id="chatHead"></div>
            <div class="chat-body" id="chatBody"></div>
            <div class="chat-input">
              <input class="input" id="msgInput" placeholder="Type a message to send from device...">
              <button class="btn grad" onclick="sendMsg()">Send</button>
            </div>
          </div>
        </div>
      </section>

      <!-- ---------- DEVICE ---------- -->
      <section class="view" id="v-device">
        <div class="detail-grid">
          <div class="card">
            <div class="sec-head" style="margin:0;padding:18px 20px 14px">
              <h2>Device Information</h2>
              <span class="pill g" id="devStatusPill">ONLINE</span>
            </div>
            <div class="info-list" id="infoList"></div>
          </div>

          <div style="display:flex;flex-direction:column;gap:14px">
            <div class="card ring-wrap">
              <div class="ring"><div class="ring-in"><b id="ringPct">82%</b><small>Battery</small></div></div>
              <div style="text-align:center;font-size:11.5px;color:var(--dim)">
                Charging · 4,850 mAh · 28°C
              </div>
            </div>
            <div class="card" style="padding:14px">
              <div style="font-size:11px;color:var(--dim);letter-spacing:.08em;text-transform:uppercase;margin-bottom:10px">
                Live Location
              </div>
              <div class="map"><div class="pin"><div class="pin-dot"></div></div></div>
              <div style="margin-top:11px;font-size:11.5px;color:var(--dim);font-variant-numeric:tabular-nums">
                📍 12.9716° N, 77.5946° E · Bengaluru
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- ---------- GALLERY ---------- -->
      <section class="view" id="v-gallery">
        <div class="tabs">
          <button class="tab active" data-tab="photos">Photos</button>
          <button class="tab" data-tab="videos">Videos</button>
        </div>
        <div class="grid-media" id="mediaGrid"></div>
      </section>

      <!-- ---------- FILES ---------- -->
      <section class="view" id="v-files">
        <div class="card" style="overflow:hidden">
          <div class="file-head" style="display:grid;grid-template-columns:32px 1fr 110px 130px 40px;gap:14px">
            <div></div><div>Name</div><div>Size</div><div>Modified</div><div></div>
          </div>
          <div id="fileList"></div>
        </div>
      </section>

      <!-- ---------- KEYSTROKES ---------- -->
      <section class="view" id="v-keylog">
        <div class="stats">
          <div class="stat"><div class="stat-ico">⌨️</div><div>
            <div class="stat-k">Captures Today</div>
            <div class="stat-v" id="keylogCount">12<span>events</span></div></div></div>
          <div class="stat"><div class="stat-ico">🪟</div><div>
            <div class="stat-k">Active Window</div><div class="stat-v" style="font-size:16px">WhatsApp</div></div></div>
          <div class="stat"><div class="stat-ico">⏱</div><div>
            <div class="stat-k">Session Length</div><div class="stat-v">2<span>h 14m</span></div></div></div>
          <div class="stat"><div class="stat-ico">📊</div><div>
            <div class="stat-k">Avg / Minute</div><div class="stat-v">38<span>keys</span></div></div></div>
        </div>

        <div class="sec-head">
          <h2>Keystroke Log</h2>
          <div style="display:flex;gap:8px">
            <button class="btn" onclick="toast('Log exported as .txt')">Export</button>
            <button class="btn" onclick="clearKeylog()">Clear</button>
          </div>
        </div>

        <div class="detail-grid">
          <div class="card" style="overflow:hidden">
            <div class="tabs" style="padding:14px 16px 12px;border-bottom:1px solid var(--line);margin:0">
              <button class="tab active" data-kf="all">All</button>
              <button class="tab" data-kf="WhatsApp">WhatsApp</button>
              <button class="tab" data-kf="Chrome">Chrome</button>
              <button class="tab" data-kf="Instagram">Instagram</button>
              <button class="tab" data-kf="Telegram">Telegram</button>
            </div>
            <div id="keylogList"></div>
          </div>

          <div style="display:flex;flex-direction:column;gap:14px">
            <div class="card side-panel">
              <div style="font-size:11px;color:var(--dim);letter-spacing:.08em;
                text-transform:uppercase;margin-bottom:14px">Top Captured Apps</div>
              <div class="app-stat"><div class="app-stat-top">
                <b>WhatsApp</b><span>42%</span></div>
                <div class="mini-bar"><i style="width:42%"></i></div></div>
              <div class="app-stat"><div class="app-stat-top">
                <b>Chrome</b><span>28%</span></div>
                <div class="mini-bar"><i style="width:28%"></i></div></div>
              <div class="app-stat"><div class="app-stat-top">
                <b>Instagram</b><span>16%</span></div>
                <div class="mini-bar"><i style="width:16%"></i></div></div>
              <div class="app-stat"><div class="app-stat-top">
                <b>Telegram</b><span>9%</span></div>
                <div class="mini-bar"><i style="width:9%"></i></div></div>
              <div class="app-stat"><div class="app-stat-top">
                <b>System</b><span>5%</span></div>
                <div class="mini-bar"><i style="width:5%"></i></div></div>
            </div>

            <div class="card side-panel">
              <div style="font-size:11px;color:var(--dim);letter-spacing:.08em;
                text-transform:uppercase;margin-bottom:12px">Capture Status</div>
              <div style="display:flex;flex-direction:column;gap:12px">
                <div class="info-row" style="padding:0"><span>Hook Status</span>
                  <span class="pill g">ACTIVE</span></div>
                <div class="info-row" style="padding:0"><span>Buffer</span><b>12 / 500</b></div>
                <div class="info-row" style="padding:0"><span>Sync</span><b>Realtime</b></div>
                <div class="info-row" style="padding:0"><span>Target</span><b>Pixel 7 Pro</b></div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- ---------- SCREEN MIRROR ---------- -->
      <section class="view" id="v-screen">
        <div class="mirror-wrap">
          <div class="mirror-stage">
            <div class="phone">
              <div class="phone-screen">
                <div class="ps-wall"></div>
                <div class="ps-status"><span>14:32</span><span>5G ▮▮▮ 82%</span></div>
                <div class="ps-time"><b>14:32</b><span>MON, 28 OCT</span></div>
                <div class="ps-apps">
                  <div class="ps-app"></div><div class="ps-app"></div>
                  <div class="ps-app"></div><div class="ps-app"></div>
                  <div class="ps-app"></div><div class="ps-app"></div>
                  <div class="ps-app"></div><div class="ps-app"></div>
                </div>
                <div class="scan"></div>
              </div>
            </div>
          </div>

          <div style="display:flex;flex-direction:column;gap:14px">
            <div class="card side-panel">
              <div class="live-badge"><i></i> LIVE STREAM</div>
              <div style="margin-top:16px;display:flex;flex-direction:column;gap:12px">
                <div class="info-row" style="padding:0"><span>Resolution</span><b>1080 × 2400</b></div>
                <div class="info-row" style="padding:0"><span>FPS</span><b>30 fps</b></div>
                <div class="info-row" style="padding:0"><span>Bitrate</span><b>2.4 Mbps</b></div>
                <div class="info-row" style="padding:0"><span>Latency</span><b class="f-dim">68 ms</b></div>
                <div class="info-row" style="padding:0"><span>Touch Control</span>
                  <span class="pill g">ENABLED</span></div>
              </div>
            </div>
            <div class="card side-panel" style="display:grid;gap:9px">
              <button class="btn" onclick="toast('Screenshot captured')">📸 Capture Screen</button>
              <button class="btn" onclick="toast('Recording started')">⏺ Record Session</button>
              <button class="btn" onclick="toast('Quality set to 720p')">⚙ Adjust Quality</button>
              <button class="btn" style="color:var(--red);border-color:rgba(239,68,68,.3)"
                onclick="toast('Stream stopped')">⏹ Stop Stream</button>
            </div>
          </div>
        </div>
      </section>

      <!-- ---------- CONTROLS ---------- -->
      <section class="view" id="v-controls">
        <div class="sec-head" style="margin-top:0"><h2>Remote Controls</h2></div>
        <div class="controls">

          <div class="ctrl" data-toggle="flashlight">
            <div class="ctrl-ico">🔦</div>
            <div class="ctrl-txt"><h4>Flashlight</h4><p>Toggle rear LED</p></div>
            <div class="switch"></div>
          </div>

          <div class="ctrl" data-toggle="vibration">
            <div class="ctrl-ico">📳</div>
            <div class="ctrl-txt"><h4>Vibration</h4><p>Trigger vibrator motor</p></div>
            <div class="switch"></div>
          </div>

          <div class="ctrl" data-toggle="alarm">
            <div class="ctrl-ico">🔔</div>
            <div class="ctrl-txt"><h4>Alarm</h4><p>Play alarm at max volume</p></div>
            <div class="switch"></div>
          </div>

          <div class="ctrl" data-toggle="mic">
            <div class="ctrl-ico">🎙</div>
            <div class="ctrl-txt"><h4>Microphone</h4><p>Live audio listen-in</p></div>
            <div class="switch"></div>
          </div>

          <div class="ctrl" data-toggle="camera">
            <div class="ctrl-ico">📷</div>
            <div class="ctrl-txt"><h4>Camera</h4><p>Front / rear capture</p></div>
            <div class="switch"></div>
          </div>

          <div class="ctrl" data-toggle="lock">
            <div class="ctrl-ico">🔒</div>
            <div class="ctrl-txt"><h4>Lock Screen</h4><p>Lock the device instantly</p></div>
            <div class="switch"></div>
          </div>

          <div class="ctrl">
            <div class="ctrl-ico">💬</div>
            <div class="ctrl-txt"><h4>Toast Message</h4><p>Show popup on device</p></div>
            <button class="mini-btn" onclick="toast('Toast sent to device')">Send</button>
          </div>

          <div class="ctrl">
            <div class="ctrl-ico">📞</div>
            <div class="ctrl-txt"><h4>Call Forward</h4><p>Route incoming calls</p></div>
            <button class="mini-btn" onclick="toast('Call forwarding enabled')">Enable</button>
          </div>

          <div class="ctrl">
            <div class="ctrl-ico">🗺</div>
            <div class="ctrl-txt"><h4>Location Ping</h4><p>Request fresh GPS fix</p></div>
            <button class="mini-btn" onclick="toast('GPS ping sent — awaiting fix')">Ping</button>
          </div>

          <div class="ctrl">
            <div class="ctrl-ico">📸</div>
            <div class="ctrl-txt"><h4>Screenshot</h4><p>Capture current screen</p></div>
            <button class="mini-btn" onclick="toast('Screenshot saved to gallery')">Capture</button>
          </div>

          <div class="ctrl">
            <div class="ctrl-ico">🔊</div>
            <div class="ctrl-txt"><h4>Volume</h4><p>Set media volume to 100%</p></div>
            <button class="mini-btn" onclick="toast('Volume set to 100%')">Max</button>
          </div>

          <div class="ctrl">
            <div class="ctrl-ico">♻</div>
            <div class="ctrl-txt"><h4>Reboot</h4><p>Restart the device</p></div>
            <button class="mini-btn" style="color:var(--red);border-color:rgba(239,68,68,.3)"
              onclick="toast('Reboot command sent')">Reboot</button>
          </div>

        </div>
      </section>

    </div>
  </main>
</div>

<div class="toasts" id="toasts"></div>

<script>
/* ================== MOCK DATA ================== */
const devices = [
  { id:'d1', name:'Pixel 7 Pro', model:'GP4BC', os:'Android 14', battery:82, charging:true,
    ip:'103.21.44.18', carrier:'Jio 5G', root:false, status:'online',
    gps:'12.9716° N, 77.5946° E', city:'Bengaluru, IN', ram:'12 GB', storage:'128 GB',
    imei:'356789012345678', androidId:'a1b2c3d4e5f6g7h8', uptime:'3d 14h 22m' },
  { id:'d2', name:'Redmi Note 12', model:'22111317I', os:'Android 13', battery:54, charging:false,
    ip:'49.207.183.92', carrier:'Airtel 4G', root:true, status:'online',
    gps:'13.0827° N, 80.2707° E', city:'Chennai, IN', ram:'6 GB', storage:'128 GB',
    imei:'359876543210987', androidId:'z9y8x7w6v5u4t3s2', uptime:'1d 06h 41m' },
  { id:'d3', name:'iPhone 13', model:'A2633', os:'iOS 17.2', battery:67, charging:true,
    ip:'157.32.88.104', carrier:'Vi 4G', root:false, status:'online',
    gps:'11.0168° N, 76.9558° E', city:'Coimbatore, IN', ram:'4 GB', storage:'128 GB',
    imei:'N/A', androidId:'N/A', uptime:'9h 12m' },
  { id:'d4', name:'Windows Laptop', model:'ThinkPad E14', os:'Windows 11', battery:31, charging:false,
    ip:'192.168.1.14', carrier:'Wi-Fi', root:false, status:'offline',
    gps:'—', city:'—', ram:'16 GB', storage:'512 GB',
    imei:'N/A', androidId:'N/A', uptime:'—' }
];

const contacts = [
  { name:'Arun Kumar',    phone:'+91 98765 43210', tag:'Family',  cls:'' },
  { name:'Divya R',       phone:'+91 91234 56789', tag:'Work',    cls:'alt' },
  { name:'Karthik S',     phone:'+91 87654 32109', tag:'Friend',  cls:'alt2' },
  { name:'Priya Lakshmi', phone:'+91 76543 21098', tag:'Family',  cls:'' },
  { name:'Vignesh M',     phone:'+91 65432 10987', tag:'College', cls:'alt' },
  { name:'Sneha Patel',   phone:'+91 54321 09876', tag:'Work',    cls:'alt2' },
  { name:'Rahul Verma',   phone:'+91 43210 98765', tag:'Friend',  cls:'' },
  { name:'Meena Kumari',  phone:'+91 32109 87654', tag:'Family',  cls:'alt' },
  { name:'Ajay Raj',      phone:'+91 21098 76543', tag:'College', cls:'alt2' },
  { name:'Nithya B',      phone:'+91 10987 65432', tag:'Work',    cls:'' },
  { name:'Suresh Babu',   phone:'+91 99887 76655', tag:'Friend',  cls:'alt' },
  { name:'Lakshmi N',     phone:'+91 88776 65544', tag:'Family',  cls:'alt2' }
];

const convos = [
  { id:1, name:'Arun Kumar', initials:'AK', time:'2m', unread:2, cls:'',
    thread:[
      { from:'them', text:'Bro call me when free', time:'14:28' },
      { from:'them', text:'Important matter da', time:'14:29' }
    ]},
  { id:2, name:'Divya R', initials:'DR', time:'26m', unread:0, cls:'alt',
    thread:[
      { from:'them', text:'Report ready ah?', time:'13:40' },
      { from:'me',   text:'Almost done, 30 min la send panren', time:'13:44' },
      { from:'them', text:'Okay 👍', time:'13:45' }
    ]},
  { id:3, name:'Karthik S', initials:'KS', time:'1h', unread:1, cls:'alt2',
    thread:[
      { from:'them', text:'Bro lab solve pannitiya?', time:'12:50' },
      { from:'them', text:'Enaku SQLi part la doubt', time:'12:51' }
    ]},
  { id:4, name:'Airtel', initials:'AT', time:'3h', unread:0, cls:'alt',
    thread:[
      { from:'them', text:'Your data balance is 2.4 GB. Recharge now to continue browsing.', time:'11:02' }
    ]},
  { id:5, name:'Sneha Patel', initials:'SP', time:'Yesterday', unread:0, cls:'alt2',
    thread:[
      { from:'them', text:'Meeting tomorrow 10 AM, don\\'t forget!', time:'18:20' },
      { from:'me',   text:'Noted 👍', time:'18:25' }
    ]}
];

const media = {
  photos: [
    { label:'IMG_20261028_1432.jpg', g:'linear-gradient(135deg,#1e3a8a,#0ea5e9)' },
    { label:'IMG_20261028_1401.jpg', g:'linear-gradient(135deg,#7c2d12,#f59e0b)' },
    { label:'Screenshot_112.png',    g:'linear-gradient(135deg,#312e81,#8b5cf6)' },
    { label:'IMG_20261027_0912.jpg', g:'linear-gradient(135deg,#064e3b,#22c55e)' },
    { label:'IMG_20261026_1830.jpg', g:'linear-gradient(135deg,#7f1d1d,#ef4444)' },
    { label:'IMG_20261025_2015.jpg', g:'linear-gradient(135deg,#164e63,#22d3ee)' },
    { label:'Download_88.jpg',       g:'linear-gradient(135deg,#3f3f46,#a1a1aa)' },
    { label:'IMG_20261024_1102.jpg', g:'linear-gradient(135deg,#4c1d95,#c026d3)' }
  ],
  videos: [
    { label:'VID_20261028_1420.mp4', g:'linear-gradient(135deg,#1e40af,#06b6d4)', dur:'0:42' },
    { label:'VID_20261027_1810.mp4', g:'linear-gradient(135deg,#831843,#f43f5e)', dur:'2:15' },
    { label:'ScreenRecord_03.mp4',   g:'linear-gradient(135deg,#14532d,#4ade80)', dur:'1:08' },
    { label:'VID_20261025_0902.mp4', g:'linear-gradient(135deg,#581c87,#a855f7)', dur:'0:19' },
    { label:'WhatsApp_Video.mp4',    g:'linear-gradient(135deg,#134e4a,#2dd4bf)', dur:'3:44' },
    { label:'VID_20261022_2215.mp4', g:'linear-gradient(135deg,#78350f,#fbbf24)', dur:'1:31' }
  ]
};

const files = [
  { name:'DCIM',               type:'📁', size:'—',       date:'28 Oct 2026' },
  { name:'WhatsApp Images',    type:'📁', size:'—',       date:'28 Oct 2026' },
  { name:'Downloads',          type:'📁', size:'—',       date:'27 Oct 2026' },
  { name:'screenshot_1432.png',type:'🖼', size:'2.4 MB',  date:'28 Oct 2026' },
  { name:'voice_note_0112.m4a',type:'🎵', size:'1.1 MB',  date:'28 Oct 2026' },
  { name:'college_notes.pdf',  type:'📄', size:'840 KB',  date:'26 Oct 2026' },
  { name:'backup_full.zip',    type:'🗜', size:'1.8 GB',  date:'25 Oct 2026' },
  { name:'IMG_20261028.jpg',   type:'🖼', size:'3.2 MB',  date:'28 Oct 2026' },
  { name:'contacts.vcf',       type:'📇', size:'96 KB',   date:'24 Oct 2026' },
  { name:'app_debug.apk',      type:'📦', size:'24.6 MB', date:'23 Oct 2026' }
];

/* ================== HELPERS ================== */
const $ = s => document.querySelector(s);
const $$ = s => document.querySelectorAll(s);

function toast(msg){
  const el = document.createElement('div');
  el.className = 'toast';
  el.innerHTML = `<i></i><span>${msg}</span>`;
  $('#toasts').appendChild(el);
  setTimeout(()=>{ el.style.opacity='0'; el.style.transform='translateX(40px)';
    el.style.transition='.3s'; setTimeout(()=>el.remove(),300); }, 2600);
}

/* ================== NAVIGATION ================== */
const titles = {
  dashboard:['Dashboard','/ overview'], contacts:['Contacts','/ device phonebook'],
  messages:['Messages','/ sms inbox'], device:['Device','/ hardware info'],
  gallery:['Gallery','/ media storage'], files:['Files','/ file manager'],
  keylog:['Keystrokes','/ input capture log'],
  screen:['Screen Mirror','/ live stream'], controls:['Controls','/ remote actions']
};
$$('.nav-item').forEach(btn=>{
  btn.addEventListener('click',()=>{
    $$('.nav-item').forEach(b=>b.classList.remove('active'));
    btn.classList.add('active');
    const v = btn.dataset.view;
    $$('.view').forEach(s=>s.classList.remove('active'));
    $('#v-'+v).classList.add('active');
    $('#pageTitle').textContent = titles[v][0];
    $('#pageCrumb').textContent = titles[v][1];
    $('.views').scrollTop = 0;
  });
});

/* ================== CLOCK ================== */
setInterval(()=>{
  const d = new Date();
  $('#clock').textContent = d.toLocaleTimeString('en-GB');
},1000);

/* ================== DASHBOARD ================== */
let activeDevice = devices[0];

function renderDevices(){
  $('#deviceGrid').innerHTML = devices.map(d=>{
    const bc = d.battery>60?'var(--green)':d.battery>25?'var(--amber)':'var(--red)';
    return `<article class="device-card ${d.status==='offline'?'offline':''} ${d.id===activeDevice.id?'selected':''}" data-id="${d.id}">
      <div class="dc-top">
        <div class="dc-ico">${d.name.includes('Laptop')?'💻':'📱'}</div>
        <div class="dc-meta"><h3>${d.name}</h3><p>${d.os} · ${d.model}</p></div>
        <span class="dot ${d.status}"></span>
      </div>
      <div class="dc-bat">
        <div class="bar"><i style="width:${d.battery}%;background:${bc}"></i></div>
        <span>${d.battery}%${d.charging?' ⚡':''}</span>
      </div>
      <div class="dc-info">
        <div><label>IP</label><b>${d.ip}</b></div>
        <div><label>Carrier</label><b>${d.carrier}</b></div>
        <div><label>Root</label><b class="${d.root?'ok':'no'}">${d.root?'YES':'NO'}</b></div>
      </div>
    </article>`;
  }).join('');

  $$('.device-card').forEach(c=>{
    c.addEventListener('click',()=>{
      activeDevice = devices.find(d=>d.id===c.dataset.id);
      renderDevices(); renderDeviceDetail();
      toast(`Selected: ${activeDevice.name}`);
    });
  });
}

/* ================== CONTACTS ================== */
function renderContacts(filter=''){
  const list = contacts.filter(c =>
    c.name.toLowerCase().includes(filter.toLowerCase()) || c.phone.includes(filter));
  $('#contactGrid').innerHTML = list.map(c=>`
    <div class="contact" onclick="toast('Opening thread with ${c.name}')">
      <div class="c-ava ${c.cls}">${c.name.split(' ').map(w=>w[0]).join('').slice(0,2)}</div>
      <div class="c-info"><h4>${c.name}</h4><p>${c.phone}</p></div>
      <span class="c-tag">${c.tag}</span>
    </div>`).join('') || `<div style="color:var(--dim);font-size:13px;padding:20px">
      No contacts found.</div>`;
}
$('#contactSearch').addEventListener('input', e=>renderContacts(e.target.value));

/* ================== MESSAGES ================== */
let activeConvo = convos[0];

function renderConvos(){
  $('#convoList').innerHTML = convos.map(c=>`
    <div class="convo ${c.id===activeConvo.id?'active':''}" data-id="${c.id}">
      <div class="c-ava ${c.cls}">${c.initials}</div>
      <div class="c-info"><h4>${c.name}</h4><p>${c.thread[c.thread.length-1].text}</p></div>
      <div class="convo-meta"><small>${c.time}</small>
        ${c.unread?`<span class="unread">${c.unread}</span>`:''}</div>
    </div>`).join('');

  $$('.convo').forEach(el=>{
    el.addEventListener('click',()=>{
      activeConvo = convos.find(c=>c.id===+el.dataset.id);
      activeConvo.unread = 0;
      renderConvos(); renderThread();
    });
  });
}

function renderThread(){
  $('#chatHead').innerHTML = `
    <div class="c-ava ${activeConvo.cls}">${activeConvo.initials}</div>
    <div><div style="font-size:13.5px;font-weight:600">${activeConvo.name}</div>
    <div style="font-size:11px;color:var(--dim)">SMS · encrypted relay</div></div>`;

  $('#chatBody').innerHTML = activeConvo.thread.map(m=>`
    <div class="bubble ${m.from}">${m.text}<time>${m.time}</time></div>`).join('');
  $('#chatBody').scrollTop = $('#chatBody').scrollHeight;
}

function sendMsg(){
  const val = $('#msgInput').value.trim();
  if(!val) return;
  const now = new Date().toLocaleTimeString('en-GB',{hour:'2-digit',minute:'2-digit'});
  activeConvo.thread.push({ from:'me', text:val, time:now });
  $('#msgInput').value = '';
  renderThread(); renderConvos();
  toast('SMS queued for delivery');
}
$('#msgInput').addEventListener('keydown', e=>{ if(e.key==='Enter') sendMsg(); });

/* ================== DEVICE DETAIL ================== */
function renderDeviceDetail(){
  const d = activeDevice;
  $('#devStatusPill').textContent = d.status.toUpperCase();
  $('#devStatusPill').className = 'pill ' + (d.status==='online'?'g':'r');
  $('#ringPct').textContent = d.battery + '%';
  $('.ring').style.background =
    `conic-gradient(${d.battery>60?'var(--green)':d.battery>25?'var(--amber)':'var(--red)'} 0 ${d.battery}%, #182030 ${d.battery}% 100%)`;

  const rows = [
    ['Device Name', d.name], ['Model', d.model], ['OS Version', d.os],
    ['IP Address', d.ip], ['Carrier / Network', d.carrier],
    ['GPS Coordinates', d.gps], ['Location', d.city],
    ['Root Status', d.root ? '<span class="pill r">ROOTED</span>'
                           : '<span class="pill g">SECURE</span>'],
    ['Battery', d.battery + '%' + (d.charging?' ⚡ Charging':'')],
    ['RAM', d.ram], ['Storage', d.storage],
    ['IMEI', d.imei], ['Android ID', d.androidId], ['Uptime', d.uptime]
  ];
  $('#infoList').innerHTML = rows.map(([k,v])=>
    `<div class="info-row"><span>${k}</span><b>${v}</b></div>`).join('');
}

/* ================== GALLERY ================== */
function renderMedia(tab='photos'){
  $('#mediaGrid').innerHTML = media[tab].map(m=>`
    <div class="media" style="background:${m.g}" onclick="toast('Opening ${m.label}')">
      ${tab==='videos'?`<div class="play">▶</div><span class="dur">${m.dur}</span>`:''}
      <span class="lbl">${m.label}</span>
    </div>`).join('');
}
$$('.tab[data-tab]').forEach(t=>{
  t.addEventListener('click',()=>{
    $$('.tab[data-tab]').forEach(x=>x.classList.remove('active'));
    t.classList.add('active');
    renderMedia(t.dataset.tab);
  });
});

/* ================== FILES ================== */
function renderFiles(){
  $('#fileList').innerHTML = files.map(f=>`
    <div class="file-row" onclick="toast('Opening ${f.name}')">
      <div class="f-ico">${f.type}</div>
      <div class="f-name">${f.name}</div>
      <div class="f-dim">${f.size}</div>
      <div class="f-dim">${f.date}</div>
      <div class="f-more">⋮</div>
    </div>`).join('');
}

/* ================== CONTROLS ================== */
$$('.ctrl[data-toggle]').forEach(c=>{
  c.addEventListener('click',()=>{
    c.classList.toggle('on');
    const on = c.classList.contains('on');
    const name = c.querySelector('h4').textContent;
    toast(`${name} ${on?'ENABLED':'DISABLED'} on ${activeDevice.name}`);
  });
});

/* ================== KEYSTROKES (MOCK ONLY) ================== */
const keyPool = [
  {app:'WhatsApp',  ico:'💬', win:'Arun Kumar — chat',    text:'bro call me when free da'},
  {app:'Chrome',    ico:'🌐', win:'Google Search',        text:'tryhackme sqli room writeup'},
  {app:'Instagram', ico:'📸', win:'Explore',              text:'cybersecurity memes tamil'},
  {app:'Chrome',    ico:'🌐', win:'PortSwigger Labs',     text:'xss reflected lab solution'},
  {app:'WhatsApp',  ico:'💬', win:'Divya R — chat',       text:'assignment submit pannitiya'},
  {app:'Telegram',  ico:'✈️', win:'HTB Group',            text:'htb machine walkthrough link'},
  {app:'Chrome',    ico:'🌐', win:'Google Search',        text:'linux privilege escalation cheat sheet'},
  {app:'Instagram', ico:'📸', win:'Search',               text:'pentest tools 2026'},
  {app:'Chrome',    ico:'🌐', win:'Terminal Docs',        text:'nmap -sV -sC scan syntax'},
  {app:'WhatsApp', ico:'💬', win:'Karthik S — chat',      text:'naalaiku lab la meet pannalama'},
  {app:'Telegram', ico:'✈️', win:'Study Group',           text:'notes share panren bro'},
  {app:'Chrome',   ico:'🌐', win:'Notes',                 text:'OSCP exam date confirm pannu'}
];

let keylog = keyPool.map((k,i)=>({
  ...k,
  t: new Date(Date.now() - i*97000).toLocaleTimeString('en-GB')
}));
let keyFilter = 'all';

function renderKeylog(){
  const list = keyFilter === 'all'
    ? keylog
    : keylog.filter(k => k.app === keyFilter);

  $('#keylogList').innerHTML = list.length ? list.map((k,idx)=>`
    <div class="krow">
      <div class="k-app">${k.ico}</div>
      <div class="k-body">
        <div class="k-win">${k.app} · ${k.win}</div>
        <div class="k-text">${k.text}${idx===0?'<span class="caret"></span>':''}</div>
      </div>
      <div class="k-time">${k.t}</div>
    </div>`).join('')
    : `<div style="padding:26px;color:var(--dim);font-size:13px">No entries for this filter.</div>`;

  $('#keylogCount').innerHTML = `${list.length}<span>events</span>`;
}

function clearKeylog(){
  keylog = [];
  renderKeylog();
  toast('Keystroke buffer cleared');
}

$$('.tab[data-kf]').forEach(t=>{
  t.addEventListener('click',()=>{
    $$('.tab[data-kf]').forEach(x=>x.classList.remove('active'));
    t.classList.add('active');
    keyFilter = t.dataset.kf;
    renderKeylog();
  });
});

/* Fake ticker — pool la irundhu mattum, real capture illa */
setInterval(()=>{
  const v = document.getElementById('v-keylog');
  if(!v || !v.classList.contains('active')) return;
  const p = keyPool[Math.floor(Math.random()*keyPool.length)];
  keylog.unshift({ ...p, t:new Date().toLocaleTimeString('en-GB') });
  if(keylog.length > 40) keylog.pop();
  renderKeylog();
}, 4200);

/* ================== INIT ================== */
renderDevices();
renderDeviceDetail();
renderContacts();
renderConvos();
renderThread();
renderMedia('photos');
renderFiles();
renderKeylog();
</script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def home():
    return HTML_TEMPLATE
