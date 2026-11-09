import http.server
import socketserver
import os
import time
import json
import urllib.request
from urllib.parse import parse_qs, urlparse

active_sessions = {}
blocked_ips = set()

# Firebase Database URL provided by you
FIREBASE_URL = "https://vipp-b3a35-default-rtdb.firebaseio.com/passwords.json"

def load_passwords():
    try:
        req = urllib.request.Request(FIREBASE_URL, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=3) as response:
            data = json.loads(response.read().decode())
            if data and isinstance(data, dict):
                return data
    except Exception as e:
        print("Firebase Load Error:", e)
    return {"vip123": "Active", "jivan99": "Active"}

def save_passwords(db):
    try:
        data = json.dumps(db).encode("utf-8")
        req = urllib.request.Request(FIREBASE_URL, data=data, method='PUT', headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=3) as response:
            pass
    except Exception as e:
        print("Firebase Save Error:", e)

user_passwords_db = load_passwords()

security_config = {
    "password_enabled": True,
    "dashboard_password": "8709"
}

import sqlite3
import math
from typing import List, Dict, Any

os.makedirs("data", exist_ok=True)
DB_PATH = "data/wingo_history.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS wingo_history (
            game_type TEXT,
            issue_number TEXT,
            number INTEGER,
            big_small TEXT,
            color TEXT,
            time_str TEXT,
            PRIMARY KEY (game_type, issue_number)
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def classify_number(num: int) -> str:
    return "Big" if num >= 5 else "Small"

HTML_LOGIN = """<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Jivan VIP Master - Secure Access</title>
    <style>
        body { background: #040814; color: #f8fafc; font-family: 'Segoe UI', sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .login-card { background: linear-gradient(145deg, rgba(15, 23, 42, 0.95), rgba(30, 41, 59, 0.9)); border: 1px solid rgba(56, 189, 248, 0.3); border-radius: 24px; padding: 40px 30px; width: 100%; max-width: 380px; text-align: center; box-shadow: 0 25px 50px rgba(0,0,0,0.9); }
        .logo-icon { font-size: 50px; margin-bottom: 15px; background: rgba(56, 189, 248, 0.1); width: 80px; height: 80px; line-height: 80px; border-radius: 50%; margin-left: auto; margin-right: auto; border: 1px solid rgba(56, 189, 248, 0.2); }
        h2 { color: #38bdf8; margin-bottom: 10px; font-size: 26px; font-weight: 900; }
        p { font-size: 13px; color: #94a3b8; margin-bottom: 25px; }
        input { width: 100%; padding: 15px; border-radius: 14px; border: 1px solid #475569; background: #0b1329; color: #fff; font-size: 16px; text-align: center; margin-bottom: 18px; outline: none; box-sizing: border-box; }
        button { width: 100%; padding: 15px; background: linear-gradient(135deg, #0284c7, #38bdf8); color: #040814; border: 0; border-radius: 14px; font-weight: 900; font-size: 16px; cursor: pointer; box-shadow: 0 5px 20px rgba(56,189,248,0.4); }
        .error-box { background: rgba(239, 68, 68, 0.15); border: 1px solid rgba(239, 68, 68, 0.4); padding: 12px; border-radius: 12px; margin-top: 18px; color: #f87171; font-size: 13px; }
    </style>
</head>
<body>
    <div class="login-card">
        <div class="logo-icon">👑</div>
        <h2>Jivan Master VIP</h2>
        <p>डैशबोर्ड एक्सेस करने के लिए अपना लॉगिन पासवर्ड दर्ज करें।</p>
        <form method="POST">
            <input type="password" name="password" placeholder="••••••••" required autofocus>
            <button type="submit">अनलॉक करें ➔</button>
        </form>
        %ERROR_MSG%
    </div>
</body>
</html>"""

HTML_MASTER_CONTENT = """<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Jivan Master Dashboard VIP</title>
    <style>
        :root { --bg-color: #070b19; --card-bg: rgba(15, 23, 42, 0.9); --border-glow: rgba(56, 189, 248, 0.4); --text-main: #f8fafc; --accent-gold: #fbbf24; }
        body { background: var(--bg-color); color: var(--text-main); font-family: 'Segoe UI', sans-serif; text-align: center; margin: 0; padding: 15px; min-height: 100vh; display: flex; justify-content: center; align-items: center; }
        .vip-card { background: var(--card-bg); border: 2px solid var(--border-glow); border-radius: 22px; padding: 22px; width: 100%; max-width: 420px; box-shadow: 0 15px 35px rgba(0, 0, 0, 0.9); position: relative; }
        .admin-icon-btn { position: absolute; top: 15px; right: 15px; background: rgba(239, 68, 68, 0.2); border: 1px solid #ef4444; color: #f87171; padding: 4px 10px; border-radius: 8px; font-size: 11px; font-weight: bold; text-decoration: none; }
        .header-title { font-size: 20px; font-weight: 900; color: #38bdf8; margin-bottom: 8px; }
        .mode-selector { display: flex; gap: 8px; margin-bottom: 10px; }
        .mode-btn { flex: 1; padding: 7px; border: 0; border-radius: 8px; font-weight: bold; cursor: pointer; font-size: 13px; background: #1e1b4b; color: #94a3b8; }
        .mode-btn.active { background: #0284c7; color: #fff; box-shadow: 0 0 10px rgba(56,189,248,0.5); }
        .top-bar { display: flex; justify-content: space-between; align-items: center; background: #1e1b4b; padding: 8px 12px; border-radius: 12px; margin-bottom: 8px; }
        .tg-control { font-size: 12px; display: flex; align-items: center; gap: 6px; color: #38bdf8; font-weight: bold; }
        .info-row { display: flex; justify-content: space-between; align-items: center; background: rgba(30, 41, 59, 0.8); padding: 6px 10px; border-radius: 10px; margin-bottom: 6px; font-size: 13px; }
        .timer-badge { background: rgba(251, 191, 36, 0.2); color: var(--accent-gold); padding: 3px 8px; border-radius: 6px; font-family: monospace; font-size: 13px; font-weight: bold; }
        .pattern-box { background: #1e1b4b; border: 1px solid #475569; color: #facc15; font-weight: 800; padding: 7px; border-radius: 10px; font-size: 12px; margin-bottom: 6px; }
        .signal-box { font-size: 38px; font-weight: 900; margin: 6px 0; padding: 10px; border-radius: 14px; background: #000; letter-spacing: 2px; color: #38bdf8; }
        .level-mini-box { background: rgba(251, 191, 36, 0.15); border: 1px dashed var(--accent-gold); padding: 5px 10px; border-radius: 8px; margin-bottom: 6px; font-size: 12px; font-weight: bold; color: var(--accent-gold); display: flex; justify-content: space-between; align-items: center; }
        .stats-row { display: flex; justify-content: space-around; background: #1e293b; padding: 6px; border-radius: 10px; margin-bottom: 8px; font-size: 12px; font-weight: bold; }
        .table-container { max-height: 110px; overflow-y: auto; border-radius: 8px; border: 1px solid #475569; margin-top: 6px; }
        table { width: 100%; border-collapse: collapse; font-size: 11px; color: #fff; }
        th, td { padding: 5px; border-bottom: 1px solid #1e293b; text-align: center; }
        th { background: #0f172a; color: #38bdf8; position: sticky; top: 0; }
        .footer-panel { display: flex; justify-content: space-between; align-items: center; margin-top: 10px; font-size: 11px; background: rgba(56, 189, 248, 0.1); padding: 6px 8px; border-radius: 8px; gap: 4px; }
        .action-btn { background: #38bdf8; color: #0f172a; border: 0; padding: 5px 7px; border-radius: 6px; font-weight: bold; cursor: pointer; font-size: 10px; }
        .copy-btn { background: #22c55e; color: #fff; }
    </style>
</head>
<body>
    <div class="vip-card">
        <a href="/admin_master_jivan" class="admin-icon-btn">👑 Admin</a>
        <div class="header-title" id="dashboard-title">Jivan dashboard VIP 30S</div>
        <div class="mode-selector">
            <button class="mode-btn active" id="btn-30s" onclick="switchMode('30S')">⚡ 30 सेकंड</button>
            <button class="mode-btn" id="btn-1m" onclick="switchMode('1M')">🚀 1 मिनट</button>
        </div>
        <div class="top-bar">
            <button style="background:#0284c7; color:#fff; border:0; padding:5px 12px; border-radius:8px;" id="mode-badge">30S</button>
            <div class="tg-control"><span>Telegram Auto:</span> <input type="checkbox" id="tgToggle" onclick="verifyTelegram(event)"></div>
        </div>
        <div class="info-row"><span id="issue-text">पीरियड नंबर: --</span><span>समय: <span class="timer-badge" id="timer-text">00:30</span></span></div>
        <div class="pattern-box" id="pattern-text">VIP Master Engine Active...</div>
        <div class="signal-box" id="signal-text">--</div>
        
        <div class="level-mini-box">
            <span>📊 वर्तमान लेवल: <span id="current-level-text" style="color:#fff;">Level 1</span></span>
            <span>💰 अमाउंट: <span id="current-amount-text" style="color:#38bdf8; font-size:13px;">₹10</span></span>
        </div>

        <div class="stats-row">
            <span style="color: #22c55e;">जीत (Win): <span id="wins-count">0</span></span>
            <span style="color: #ef4444;">हार (Loss): <span id="losses-count">0</span></span>
        </div>
        <h3>लाइव मार्केट इतिहास</h3>
        <div class="table-container">
            <table>
                <thead><tr><th>पीरियड</th><th>नंबर</th><th>साइज</th><th>स्टेटस</th></tr></thead>
                <tbody id="history-rows"><tr><td colspan="4">डाटा सिंक हो रहा है...</td></tr></tbody>
            </table>
        </div>
        <div class="footer-panel">
            <span>🟢 एक्टिव: <span id="active-count">1</span></span>
            <button class="action-btn" onclick="openLevelMenu()">📋 Level</button>
            <button class="action-btn" onclick="editLevelAmounts()">⚙️ Edit</button>
            <button class="action-btn copy-btn" onclick="copyResultsList()">📋 Copy List</button>
        </div>
    </div>
    <script>
        const API_URL_30S = "https://draw.ar-lottery01.com/WinGo/WinGo_30S/GetHistoryIssuePage.json";
        const API_URL_1M = "https://draw.ar-lottery01.com/WinGo/WinGo_1M/GetHistoryIssuePage.json";

        let currentMode = "30S";
        let levelAmounts = { 1: 10, 2: 25, 3: 60, 4: 150, 5: 350, 6: 800, 7: 1800, 8: 4000 };
        let currentLevel = 1;

        let lastProcessedIssue = "";
        let historyLog = [];
        let records = [];
        let stats = { wins: 0, losses: 0 };
        let shiftToCurrent = false;
        let lockedPeriod = "";
        let lockedPrediction = null;
        let lockedPattern = "";

        function switchMode(mode) {
            currentMode = mode;
            lastProcessedIssue = "";
            historyLog = [];
            records = [];
            stats = { wins: 0, losses: 0 };
            shiftToCurrent = false;
            lockedPeriod = "";
            lockedPrediction = null;
            
            if(mode === "30S") {
                document.getElementById('btn-30s').classList.add('active');
                document.getElementById('btn-1m').classList.remove('active');
                document.getElementById('dashboard-title').innerText = "Jivan dashboard VIP 30S";
                document.getElementById('mode-badge').innerText = "30S";
            } else {
                document.getElementById('btn-1m').classList.add('active');
                document.getElementById('btn-30s').classList.remove('active');
                document.getElementById('dashboard-title').innerText = "Jivan dashboard VIP 1M";
                document.getElementById('mode-badge').innerText = "1M";
            }
            fetchAndProcess();
        }

        function copyResultsList() {
            if (historyLog.length === 0 && !lockedPrediction) {
                alert("❌ अभी कोई डेटा उपलब्ध नहीं है!");
                return;
            }
            let textToCopy = "";
            let reversedLog = [...historyLog].reverse();
            reversedLog.forEach((item, index) => {
                let numStr = index + 1;
                textToCopy += `${numStr}. Period: ${item.issue} | ${item.size} | Status: ${item.status}\n`;
            });

            if (lockedPrediction && lockedPeriod) {
                textToCopy += `👉 LIVE Target: Period ${lockedPeriod} - ${lockedPrediction}\n`;
            }
            
            navigator.clipboard.writeText(textToCopy).then(() => {
                alert("✅ लिस्ट सफलतापूर्वक कॉपी हो गई है!");
            }).catch(err => {
                prompt("कॉपी करने के लिए नीचे दिए गए टेक्स्ट को सेलेक्ट करें:", textToCopy);
            });
        }

        setInterval(() => {
            fetch('/ping').then(res => res.json()).then(data => {
                if(data.blocked) {
                    document.body.innerHTML = "<div style='background:#040814; color:#ff4444; text-align:center; padding-top:20vh; font-family:sans-serif;'><h1>🚫 आपका डिवाइस ब्लॉक कर दिया गया है!</h1><p style='color:#fff; font-size:16px;'>अनब्लॉक कराने या बात करने के लिए कृपया टेलीग्राम पर संपर्क करें:</p><a href='https://t.me/VIPGUPTAA' target='_blank' style='color:#38bdf8; font-size:22px; font-weight:bold; text-decoration:none;'>@VIPGUPTAA</a></div>";
                } else if(data.active_devices) {
                    document.getElementById('active-count').innerText = data.active_devices;
                }
            }).catch(e => {});
        }, 3000);

        function openLevelMenu() {
            let menuText = `👑 Jivan VIP (${currentMode}) - 1 से 8 लेवल अमाउंट चार्ट 👑\n\n`;
            for (let lvl = 1; lvl <= 8; lvl++) {
                let marker = (lvl === currentLevel) ? " ➔ [वर्तमान लेवल]" : "";
                menuText += `Level ${lvl} : ₹${levelAmounts[lvl]}${marker}\n`;
            }
            alert(menuText);
        }

        function editLevelAmounts() {
            let lvlChoice = prompt("किस लेवल का अमाउंट बदलना चाहते हैं? (1 से 8):");
            if (!lvlChoice) return;
            let lvlNum = parseInt(lvlChoice);
            if (isNaN(lvlNum) || lvlNum < 1 || lvlNum > 8) { alert("❌ अमान्य लेवल!"); return; }
            let newAmt = prompt(`Level ${lvlNum} के लिए नया अमाउंट दर्ज करें:`);
            if (newAmt !== null && newAmt.trim() !== "") {
                let amtNum = parseInt(newAmt);
                if (!isNaN(amtNum) && amtNum > 0) {
                    levelAmounts[lvlNum] = amtNum;
                    alert(`✅ अपडेट हो गया! Level ${lvlNum} = ₹${amtNum}`);
                }
            }
        }

        function verifyTelegram(event) {
            let toggleBox = document.getElementById('tgToggle');
            if (toggleBox.checked) {
                toggleBox.checked = false;
                let pass = prompt("🔒 सुरक्षित क्षेत्र: टेलीग्राम ऑटोमेशन ऑन करने के लिए पासवर्ड दर्ज करें:");
                if (pass === "8709") { toggleBox.checked = true; alert("✅ टेलीग्राम ऑन हो गया!"); }
                else if (pass !== null) { alert("❌ गलत पासवर्ड!"); }
            }
        }

        setInterval(() => {
            let now = new Date();
            let sec = now.getSeconds();
            let remaining = 0;
            if(currentMode === "30S") {
                remaining = 29 - (sec % 30);
            } else {
                let totalSecCurrent = (now.getMinutes() * 60) + sec;
                remaining = 59 - (totalSecCurrent % 60);
            }
            let m = String(Math.floor(remaining / 60)).padStart(2, '0');
            let s = String(remaining % 60).padStart(2, '0');
            document.getElementById('timer-text').innerText = `${m}:${s}`;
        }, 200);

        function analyzeMarketPattern(history_list) {
            if (!history_list || history_list.length < 4) return { prediction: "WAITING", pattern: "मार्केट स्कैन हो रहा है..." };
            
            let recent = history_list.slice(0, 4).map(r => r.size);
            
            if (recent[0] !== recent[1] && recent[1] !== recent[2] && recent[2] !== recent[3]) {
                let pred = (recent[0] === "BIG") ? "SMALL" : "BIG";
                return { prediction: pred, pattern: "⚡ ZIG-ZAG PATTERN (" + pred + ")" };
            }
            
            if (recent[0] === recent[1] && recent[1] !== recent[2]) {
                let pred = (recent[0] === "BIG") ? "SMALL" : "BIG";
                return { prediction: pred, pattern: "🔄 2/1 FLIP TREND (" + pred + ")" };
            }
            
            if (shiftToCurrent) { 
                return { prediction: recent[0], pattern: "🎯 LOSS-SHIFT RECOVERY (" + recent[0] + ")" }; 
            }
            
            let streakCount = 1;
            for (let i = 0; i < recent.length - 1; i++) {
                if (recent[i] === recent[i+1]) {
                    streakCount++;
                } else {
                    break;
                }
            }
            
            if (streakCount >= 3) {
                return { prediction: recent[0], pattern: "🐉 DRAGON STREAK (" + streakCount + "X " + recent[0] + ")" };
            }

            return { prediction: recent[0], pattern: "📈 TREND FOLLOW (" + recent[0] + ")" };
        }

        // --- BROWSER DIRECT FETCH USING CODETABS PROXY ---
        async function fetchWithRetry(url, retries = 2, timeout = 3000) {
            for (let i = 0; i < retries; i++) {
                try {
                    let proxyUrl = 'https://api.codetabs.com/v1/proxy?quest=' + encodeURIComponent(url + '?pageSize=50&pageNo=1');
                    let controller = new AbortController();
                    let timer = setTimeout(() => controller.abort(), timeout);
                    let res = await fetch(proxyUrl, { signal: controller.signal });
                    clearTimeout(timer);
                    if (res.ok) {
                        return await res.json();
                    }
                } catch (err) { if (i === retries - 1) throw err; }
            }
        }

        async function fetchAndProcess() {
            try {
                let activeApi = (currentMode === "30S") ? API_URL_30S : API_URL_1M;
                let json_data = await fetchWithRetry(activeApi);
                if (!json_data) return;
                let list = json_data.data?.list || json_data.list || json_data.data;
                if (!list || list.length === 0) return;

                if (lastProcessedIssue === "" && list.length >= 5) {
                    for (let i = Math.min(10, list.length) - 1; i >= 1; i--) {
                        let p_num = parseInt(list[i].number !== undefined ? list[i].number : list[i].winningNumber);
                        records.unshift({ size: p_num >= 5 ? "BIG" : "SMALL" });
                    }
                    lastProcessedIssue = String(list[0].issueNumber || list[0].period || list[0].issue);
                }

                let latest = list[0];
                let issueId = String(latest.issueNumber || latest.period || latest.issue);
                let num = parseInt(latest.number !== undefined ? latest.number : latest.winningNumber);

                if (issueId !== lastProcessedIssue) {
                    lastProcessedIssue = issueId;
                    let actual_size = num >= 5 ? "BIG" : "SMALL";
                    let result_status = "📌 PAST";

                    if (records.length > 0 && records[0].predicted) {
                        let last_pred = records[0].predicted;
                        let recent = records.slice(0, 3).map(r => r.size);
                        let was_zigzag = (recent.length >= 3 && recent[0] !== recent[1] && recent[1] !== recent[2]);
                        let was_2_1 = (recent.length >= 3 && recent[0] === recent[1] && recent[1] !== recent[2]);

                        if (last_pred === actual_size) {
                            stats.wins++; result_status = "👑 WIN ⚡"; shiftToCurrent = false; currentLevel = 1;
                        } else {
                            stats.losses++; result_status = "LOSS 🤬";
                            shiftToCurrent = (!was_zigzag && !was_2_1);
                            if (currentLevel < 8) currentLevel++;
                        }
                    }

                    records.unshift({ size: actual_size, predicted: lockedPrediction });
                    if (records.length > 30) records.pop();
                    historyLog.unshift({ issue: issueId.slice(-4), num: num, size: actual_size, status: result_status });
                    if (historyLog.length > 20) historyLog.pop();
                    lockedPrediction = null;
                }

                let next_issue = String(BigInt(issueId) + 1n);
                let short_next = next_issue.slice(-4);

                if (lockedPeriod !== short_next) {
                    let result = analyzeMarketPattern(records);
                    if (result.prediction !== "WAITING") {
                        lockedPeriod = short_next;
                        lockedPrediction = result.prediction;
                        lockedPattern = result.pattern;
                        if(records.length > 0) records[0].predicted = lockedPrediction;
                    }
                }

                document.getElementById('signal-text').innerText = lockedPrediction || "WAITING";
                document.getElementById('pattern-text').innerText = lockedPattern || "डेटा सिंक हो रहा है...";
                document.getElementById('issue-text').innerText = "पीरियड नंबर: " + short_next;
                document.getElementById('wins-count').innerText = stats.wins;
                document.getElementById('losses-count').innerText = stats.losses;
                document.getElementById('current-level-text').innerText = `Level ${currentLevel}`;
                document.getElementById('current-amount-text').innerText = `₹${levelAmounts[currentLevel]}`;

                let rows = "";
                historyLog.forEach(item => {
                    let colorStyle = item.status.includes("WIN") ? "color:#22c55e; font-weight:bold;" : (item.status.includes("LOSS") ? "color:#ef4444; font-weight:bold;" : "color:#94a3b8;");
                    rows += `<tr><td>${item.issue}</td><td>${item.num}</td><td>${item.size}</td><td style="${colorStyle}">${item.status}</td></tr>`;
                });
                document.getElementById('history-rows').innerHTML = rows || '<tr><td colspan="4">डाटा सिंक हो रहा है...</td></tr>';
            } catch (e) {}
        }

        setInterval(fetchAndProcess, 1500);
        fetchAndProcess();
    </script>
</body>
</html>"""

class DashboardServer(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query = parse_qs(parsed_path.query)
        client_ip = self.client_address[0]
        
        if client_ip in blocked_ips:
            if path == "/ping":
                self.send_response(200)
                self.send_header('Content-type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(b'{"blocked": true}')
                return
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            blocked_html = """
            <!DOCTYPE html>
            <html lang="hi">
            <head><meta charset="UTF-8"><title>Access Blocked</title></head>
            <body style="background:#040814; color:#fff; font-family:sans-serif; text-align:center; padding-top:20vh;">
                <h1 style="color:#ef4444;">🚫 आपका डिवाइस ब्लॉक कर दिया गया है!</h1>
                <p style="font-size:16px; color:#94a3b8;">अनब्लॉक कराने या बात करने के लिए कृपया टेलीग्राम पर संपर्क करें:</p>
                <a href="https://t.me/VIPGUPTAA" target="_blank" style="color:#38bdf8; font-size:22px; font-weight:bold; text-decoration:none;">@VIPGUPTAA</a>
            </body>
            </html>
            """
            self.wfile.write(blocked_html.encode('utf-8'))
            return

        if path == "/admin_master_jivan":
            cookie_header = self.headers.get('Cookie', '')
            if "admin_auth=master_verified" not in cookie_header:
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                admin_login_html = HTML_LOGIN.replace('डैशबोर्ड एक्सेस करने के लिए अपना लॉगिन पासवर्ड दर्ज करें।', 'मास्टर एडमिन पैनल खोलने के लिए मास्टर पासवर्ड दर्ज करें।')
                self.wfile.write(admin_login_html.replace('%ERROR_MSG%', '').encode('utf-8'))
                return
            
            action = query.get('action', [''])[0]
            target_ip = query.get('ip', [''])[0]
            target_upass = query.get('upass', [''])[0]
            new_upass = query.get('new_upass', [''])[0]

            if action == 'block' and target_ip:
                blocked_ips.add(target_ip)
            elif action == 'unblock' and target_ip:
                blocked_ips.discard(target_ip)
            elif action == 'toggle_sec':
                security_config["password_enabled"] = not security_config["password_enabled"]
            elif action == 'set_pass':
                new_p = query.get('new_p', [''])[0]
                if new_p: security_config["dashboard_password"] = new_p
            elif action == 'add_user' and new_upass:
                user_passwords_db[new_upass.strip()] = "Active"
                save_passwords(user_passwords_db)
            elif action == 'block_user' and target_upass:
                if target_upass in user_passwords_db: 
                    user_passwords_db[target_upass] = "Blocked"
                    save_passwords(user_passwords_db)
            elif action == 'unblock_user' and target_upass:
                if target_upass in user_passwords_db: 
                    user_passwords_db[target_upass] = "Active"
                    save_passwords(user_passwords_db)
            elif action == 'delete_user' and target_upass:
                if target_upass in user_passwords_db: 
                    del user_passwords_db[target_upass]
                    save_passwords(user_passwords_db)

            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            sec_status = "🟢 ON (सक्रिय)" if security_config["password_enabled"] else "🔴 OFF (बंद)"
            current_pass_val = security_config["dashboard_password"]
            
            html = f"""
            <html>
            <head><title>Jivan Master Admin Panel</title></head>
            <body style="background:#0f172a; color:#fff; font-family:sans-serif; text-align:center; padding:20px;">
                <h1>👑 Jivan Master Admin Panel 👑</h1>
                <div style="background:#1e293b; padding:15px; border-radius:10px; margin:15px auto; width:80%; max-width:600px; border:1px solid #38bdf8;">
                    <h3 style="color:#fbbf24; margin-top:0;">🔑 Master Password: <span style="background:#0f172a; padding:4px 12px; border-radius:6px; border:1px solid #475569; color:#38bdf8; font-family:monospace; font-size:16px;">{current_pass_val}</span></h3>
                    <hr style="border-color:#334155; margin:12px 0;">
                    <h3>🔐 Password Gate: <b style="color: {'#22c55e' if security_config['password_enabled'] else '#ef4444'};">{sec_status}</b></h3>
                    <a href="/admin_master_jivan?action=toggle_sec" style="background:#38bdf8; color:#0f172a; padding:6px 12px; text-decoration:none; border-radius:6px; font-weight:bold; font-size:12px;">चालू/बंद करें (TOGGLE)</a>
                    <br><br>
                    <form action="/admin_master_jivan" method="GET">
                        <input type="hidden" name="action" value="set_pass">
                        <input type="text" name="new_p" placeholder="नया मास्टर पासवर्ड" style="padding:6px; border-radius:4px;" required>
                        <button type="submit" style="background:#22c55e; color:#fff; border:0; padding:6px 12px; border-radius:4px; font-weight:bold; cursor:pointer;">मास्टर पासवर्ड बदलें</button>
                    </form>
                </div>

                <div style="background:#1e293b; padding:15px; border-radius:10px; margin:15px auto; width:80%; max-width:600px; border:1px solid #22c55e;">
                    <h3 style="color:#22c55e; margin-top:0;">👥 Add User Login Password</h3>
                    <form action="/admin_master_jivan" method="GET">
                        <input type="hidden" name="action" value="add_user">
                        <input type="text" name="new_upass" placeholder="नया यूजर पासवर्ड बनाएं" style="padding:8px; border-radius:6px; width:60%;" required>
                        <button type="submit" style="background:#22c55e; color:#fff; border:0; padding:8px 15px; border-radius:6px; font-weight:bold; cursor:pointer;">पासवर्ड जोड़ें</button>
                    </form>
                </div>

                <h3>Registered User Passwords & Status (Firebase Synced)</h3>
                <table border="1" style="margin:10px auto; width:80%; max-width:600px; border-collapse:collapse; text-align:center;">
                    <tr style="background:#1e293b; color:#38bdf8;"><th>User Password</th><th>Status</th><th>Actions</th></tr>
            """
            for upass, ustat in user_passwords_db.items():
                stat_html = "<span style='color:green;'>Active</span>" if ustat == "Active" else "<span style='color:red;'>Blocked</span>"
                if ustat == "Active":
                    act_btn = f"<a href='/admin_master_jivan?action=block_user&upass={upass}' style='color:red; font-weight:bold; margin-right:10px;'>BLOCK</a>"
                else:
                    act_btn = f"<a href='/admin_master_jivan?action=unblock_user&upass={upass}' style='color:green; font-weight:bold; margin-right:10px;'>UNBLOCK</a>"
                del_btn = f"<a href='/admin_master_jivan?action=delete_user&upass={upass}' style='color:#fbbf24; font-weight:bold;'>DELETE</a>"
                html += f"<tr><td><b>{upass}</b></td><td>{stat_html}</td><td>{act_btn} {del_btn}</td></tr>"

            html += """
                </table>

                <h3>Connected Devices & Block Control</h3>
                <table border="1" style="margin:10px auto; width:80%; max-width:600px; border-collapse:collapse; text-align:center;">
                    <tr style="background:#1e293b; color:#38bdf8;"><th>IP Address</th><th>Status</th><th>Action</th></tr>
            """
            for ip in list(active_sessions.keys()):
                is_blk = ip in blocked_ips
                status_txt = "<span style='color:red;'>BLOCKED</span>" if is_blk else "<span style='color:green;'>Active</span>"
                btn_txt = f"<a href='/admin_master_jivan?action=unblock&ip={ip}' style='color:#22c55e; font-weight:bold;'>UNBLOCK</a>" if is_blk else f"<a href='/admin_master_jivan?action=block&ip={ip}' style='color:red; font-weight:bold;'>BLOCK</a>"
                html += f"<tr><td>{ip}</td><td>{status_txt}</td><td>{btn_txt}</td></tr>"
            
            html += """
                </table>
                <br><a href="/" style="color:#38bdf8; font-size:16px; font-weight:bold;">⬅️ Back to Dashboard</a>
            </body>
            </html>
            """
            self.wfile.write(html.encode('utf-8'))
            return

        if security_config["password_enabled"]:
            cookie_header = self.headers.get('Cookie', '')
            if "auth_token=jivan_vip_auth" not in cookie_header:
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write(HTML_LOGIN.replace('%ERROR_MSG%', '').encode('utf-8'))
                return

        active_sessions[client_ip] = time.time()
        current_time = time.time()
        for ip, t in list(active_sessions.items()):
            if current_time - t > 20: del active_sessions[ip]

        if path == "/ping":
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(b'{"blocked": false}')
            return

        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(HTML_MASTER_CONTENT.encode('utf-8'))

    def do_POST(self):
        client_ip = self.client_address[0]
        if client_ip in blocked_ips:
            self.send_response(403)
            self.end_headers()
            return

        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode('utf-8')
        params = parse_qs(post_data)
        entered_pass = params.get('password', [''])[0]

        if self.path.startswith("/admin_master_jivan") and entered_pass == security_config["dashboard_password"]:
            self.send_response(303)
            self.send_header('Set-Cookie', 'admin_auth=master_verified; Path=/; Max-Age=3600')
            self.send_header('Location', '/admin_master_jivan')
            self.end_headers()
            return

        if entered_pass in user_passwords_db and user_passwords_db[entered_pass] == "Blocked":
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            blocked_msg_html = """
            <!DOCTYPE html>
            <html lang="hi">
            <head><meta charset="UTF-8"><title>Password Blocked</title></head>
            <body style="background:#040814; color:#fff; font-family:sans-serif; text-align:center; padding-top:20vh;">
                <h1 style="color:#ef4444;">🚫 आपका यह पासवर्ड ब्लॉक कर दिया गया है!</h1>
                <p style="font-size:16px; color:#94a3b8;">अनब्लॉक कराने या बात करने के लिए कृपया मास्टर एडमिन से टेलीग्राम पर संपर्क करें:</p>
                <a href="https://t.me/VIPGUPTAA" target="_blank" style="color:#38bdf8; font-size:22px; font-weight:bold; text-decoration:none;">@VIPGUPTAA</a>
            </body>
            </html>
            """
            self.wfile.write(blocked_msg_html.encode('utf-8'))
            return

        if entered_pass == security_config["dashboard_password"] or (entered_pass in user_passwords_db and user_passwords_db[entered_pass] == "Active"):
            self.send_response(303)
            self.send_header('Set-Cookie', 'auth_token=jivan_vip_auth; Path=/; Max-Age=31536000')
            self.send_header('Location', '/')
            self.end_headers()
        else:
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            err_html = HTML_LOGIN.replace('%ERROR_MSG%', '<div class="error-box">❌ गलत पासवर्ड! कृपया सही पासवर्ड दर्ज करें।</div>')
            self.wfile.write(err_html.encode('utf-8'))

    def log_message(self, format, *args): pass

def run_server():
    PORT = int(os.environ.get("PORT", 8000))
    with socketserver.TCPServer(("", PORT), DashboardServer) as httpd:
        print(f"🌐 Master Bot Server Live on port {PORT}")
        httpd.serve_forever()

if __name__ == "__main__":
    run_server()
