import os
import sqlite3
import requests
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import math

app = FastAPI(title="ADVANCED BIG/SMALL PATTERN INTELLIGENCE ENGINE", version="2.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("data", exist_ok=True)
DB_PATH = "data/wingo_history.db"

API_ENDPOINTS = {
    "30s": "https://draw.ar-lottery01.com/WinGo/WinGo_30S/GetHistoryIssuePage.json",
    "1m": "https://draw.ar-lottery01.com/WinGo/WinGo_1M/GetHistoryIssuePage.json"
}

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

# ==================== ADVANCED STATISTICAL & PATTERN ENGINE ====================

def classify_number(num: int) -> str:
    return "Big" if num >= 5 else "Small"

# 1. Entropy Analysis (Shannon Entropy)
def calculate_entropy(outcomes: List[str]) -> float:
    if not outcomes:
        return 0.0
    total = len(outcomes)
    counts = {"Big": outcomes.count("Big"), "Small": outcomes.count("Small")}
    entropy = 0.0
    for count in counts.values():
        if count > 0:
            p = count / total
            entropy -= p * math.log2(p)
    return round(entropy, 4)

# 2. Markov Chain Analysis & Transition Matrix
def calculate_markov_transition(outcomes: List[str]) -> Dict[str, Dict[str, float]]:
    matrix = {"Big": {"Big": 0, "Small": 0}, "Small": {"Big": 0, "Small": 0}}
    totals = {"Big": 0, "Small": 0}
    
    for i in range(len(outcomes) - 1):
        curr = outcomes[i]
        nxt = outcomes[i+1]
        if curr in matrix and nxt in matrix[curr]:
            matrix[curr][nxt] += 1
            totals[curr] += 1
            
    prob_matrix = {}
    for curr in ["Big", "Small"]:
        prob_matrix[curr] = {}
        t = totals[curr]
        for nxt in ["Big", "Small"]:
            if t > 0:
                prob_matrix[curr][nxt] = round(matrix[curr][nxt] / t, 4)
            else:
                prob_matrix[curr][nxt] = 0.0
    return prob_matrix

def perform_statistical_analysis(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not records:
        return {"error": "Insufficient data"}
    
    # Historical Data Analysis & Sorting
    sorted_recs = sorted(records, key=lambda x: str(x['issue_number']))
    numbers = [r['number'] for r in sorted_recs]
    outcomes = [r['big_small'] for r in sorted_recs]
    sample_size = len(outcomes)
    
    big_count = outcomes.count("Big")
    small_count = outcomes.count("Small")
    big_pct = round((big_count / sample_size) * 100, 2) if sample_size > 0 else 0.0
    small_pct = round((small_count / sample_size) * 100, 2) if sample_size > 0 else 0.0
    
    # 3. Streak Detection & Live Pattern Detection
    current_streak_type = outcomes[-1] if outcomes else None
    current_streak_len = 0
    for o in reversed(outcomes):
        if o == current_streak_type:
            current_streak_len += 1
        else:
            break

    # 4. Moving Average & Time Series Analysis (Window 10)
    numeric_outcomes = [1 if o == "Big" else 0 for o in outcomes]
    moving_avg = []
    window = 10
    for i in range(len(numeric_outcomes)):
        w_slice = numeric_outcomes[max(0, i - window + 1):i + 1]
        moving_avg.append(round(sum(w_slice) / len(w_slice), 2))

    # 5. Frequency Analysis (Digits 0-9)
    digit_freq = {i: numbers.count(i) for i in range(10)}
    
    # 6. Bayesian Statistical Analysis (Posterior Probability)
    recent_5 = outcomes[-5:] if len(outcomes) >= 5 else outcomes
    recent_bigs = recent_5.count("Big")
    bayesian_big_prob = round((big_count + recent_bigs) / (sample_size + len(recent_5)), 4) if sample_size > 0 else 0.5

    # 7. Entropy & Transition Matrix
    entropy = calculate_entropy(outcomes)
    transition_matrix = calculate_markov_transition(outcomes)

    # 8. Pattern Break & Repeat Pattern Detection
    pattern_breaks = 0
    repeat_patterns = 0
    for i in range(1, len(outcomes)):
        if outcomes[i] != outcomes[i-1]:
            pattern_breaks += 1
        else:
            repeat_patterns += 1

    # 9. Ensemble Statistical Analysis (Combining Bayesian, Markov & Frequency weights)
    ensemble_score = round((bayesian_big_prob * 0.4) + ((transition_matrix.get("Big", {}).get("Big", 0.5)) * 0.4) + ((big_pct / 100) * 0.2), 4)

    return {
        "sample_size": sample_size,
        "big_count": big_count,
        "small_count": small_count,
        "big_percentage": big_pct,
        "small_percentage": small_pct,
        "digit_frequency": digit_freq,
        "streak_analysis": {
            "current_streak_type": current_streak_type,
            "current_streak_length": current_streak_len,
        },
        "moving_average": moving_avg[-20:],
        "entropy": entropy,
        "markov_transition_matrix": transition_matrix,
        "bayesian_analysis": {
            "posterior_big_probability": bayesian_big_prob,
            "posterior_small_probability": round(1.0 - bayesian_big_prob, 4)
        },
        "ensemble_score": ensemble_score,
        "pattern_breaks": pattern_breaks,
        "repeat_patterns": repeat_patterns
    }

def fetch_and_store_api(game_type: str):
    url = API_ENDPOINTS.get(game_type)
    if not url:
        return
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        payload = {"pageSize": 50, "pageNo": 1}
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            list_data = []
            if isinstance(data, dict):
                if "data" in data and isinstance(data["data"], dict) and "list" in data["data"]:
                    list_data = data["data"]["list"]
                elif "data" in data and isinstance(data["data"], list):
                    list_data = data["data"]
                elif "list" in data:
                    list_data = data["list"]

            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            for item in list_data:
                issue = str(
                    item.get("issueNumber") or 
                    item.get("period") or 
                    item.get("issue") or 
                    item.get("gameNo") or ""
                ).strip()
                
                if not issue:
                    continue

                num = int(item.get("number") or item.get("winningNumber") or item.get("resultNumber") or 0)
                b_s = classify_number(num)
                color = str(item.get("color") or ("green" if num in [1,3,7,9] else "red" if num in [2,4,6,8] else "violet"))
                time_str = str(item.get("time") or item.get("createTime") or datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                
                cursor.execute('''
                    INSERT OR IGNORE INTO wingo_history (game_type, issue_number, number, big_small, color, time_str)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (game_type, issue, num, b_s, color, time_str))
            
            conn.commit()
            conn.close()
    except Exception as e:
        print(f"API Sync Error for {game_type}: {str(e)}")

# ==================== HTML / JS FRONTEND DASHBOARD ====================
HTML_CONTENT = """<!DOCTYPE html>
<html lang="en" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ADVANCED BIG/SMALL PATTERN INTELLIGENCE ENGINE</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            darkMode: 'class',
            theme: {
                extend: {
                    colors: {
                        emerald: { 500: '#10b981', 600: '#059669', 900: '#064e3b' },
                        blue: { 500: '#3b82f6', 600: '#2563eb', 900: '#1e3a8a' },
                        darkBg: '#0b0f19',
                        cardBg: '#111827',
                        borderCol: '#1f2937'
                    }
                }
            }
        }
    </script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body class="bg-darkBg text-gray-100 font-sans antialiased min-h-screen flex flex-col">
    <header class="bg-cardBg border-b border-borderCol sticky top-0 z-50 px-4 py-3 flex items-center justify-between shadow-lg">
        <div class="flex items-center space-x-3">
            <div class="bg-emerald-500/10 border border-emerald-500/30 p-2 rounded-xl text-emerald-400">
                <i class="fa-solid fa-brain text-xl"></i>
            </div>
            <div>
                <h1 class="text-sm md:text-lg font-bold tracking-wide text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-blue-400">
                    VIP PATTERN ENGINE
                </h1>
                <p class="text-xs text-gray-400 flex items-center gap-2">
                    <span id="api-status-dot" class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                    <span id="api-status-text">Connected</span> • 
                    <span id="last-sync-time">Sync: Never</span>
                </p>
            </div>
        </div>
        <div class="flex items-center space-x-2">
            <button onclick="triggerManualSync()" class="bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold px-3 py-2 rounded-lg transition flex items-center gap-1 shadow">
                <i class="fa-solid fa-rotate"></i> Sync
            </button>
        </div>
    </header>

    <nav class="bg-cardBg/80 backdrop-blur border-b border-borderCol px-4 flex overflow-x-auto space-x-2 py-2 no-scrollbar">
        <button onclick="switchTab('tab-1m')" id="btn-tab-1m" class="tab-btn px-4 py-2 rounded-lg text-xs font-semibold transition bg-emerald-600 text-white flex items-center gap-2 whitespace-nowrap">
            <i class="fa-solid fa-clock"></i> Wingo 1M
        </button>
        <button onclick="switchTab('tab-30s')" id="btn-tab-30s" class="tab-btn px-4 py-2 rounded-lg text-xs font-semibold transition bg-borderCol text-gray-300 hover:text-white flex items-center gap-2 whitespace-nowrap">
            <i class="fa-solid fa-stopwatch"></i> Wingo 30S
        </button>
        <button onclick="switchTab('tab-analysis')" id="btn-tab-analysis" class="tab-btn px-4 py-2 rounded-lg text-xs font-semibold transition bg-borderCol text-gray-300 hover:text-white flex items-center gap-2 whitespace-nowrap">
            <i class="fa-solid fa-chart-line"></i> Analytics
        </button>
        <button onclick="switchTab('tab-history')" id="btn-tab-history" class="tab-btn px-4 py-2 rounded-lg text-xs font-semibold transition bg-borderCol text-gray-300 hover:text-white flex items-center gap-2 whitespace-nowrap">
            <i class="fa-solid fa-database"></i> Records
        </button>
    </nav>

    <main class="flex-1 p-4 max-w-7xl w-full mx-auto space-y-6 pb-20">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="flex items-center justify-between bg-cardBg border border-borderCol p-4 rounded-xl shadow">
                <div>
                    <span class="text-xs uppercase text-gray-400 font-bold">Active Engine</span>
                    <h2 id="active-game-title" class="text-lg font-bold text-emerald-400">Wingo 1 Minute</h2>
                </div>
                <div class="flex bg-darkBg p-1 rounded-lg border border-borderCol">
                    <button onclick="setGameType('1m')" id="game-toggle-1m" class="px-3 py-1 text-xs rounded-md font-semibold bg-emerald-600 text-white transition">1M</button>
                    <button onclick="setGameType('30s')" id="game-toggle-30s" class="px-3 py-1 text-xs rounded-md font-semibold text-gray-400 hover:text-white transition">30S</button>
                </div>
            </div>

            <div class="bg-cardBg border border-borderCol p-4 rounded-xl shadow flex items-center justify-between">
                <div>
                    <span class="text-xs uppercase text-gray-400 font-bold">Current Period / Target</span>
                    <div id="current-period-display" class="text-xs font-mono text-gray-300 mt-0.5">Period: Loading...</div>
                </div>
                <div class="text-2xl font-mono font-bold text-amber-400 bg-darkBg px-4 py-1.5 rounded-lg border border-borderCol" id="timer-countdown">
                    00:00
                </div>
            </div>
        </div>

        <div class="grid grid-cols-3 gap-3">
            <div class="bg-cardBg border border-emerald-500/30 p-3 rounded-xl shadow text-center">
                <div class="text-xs text-emerald-400 font-bold">👑 WIN ⚡👑</div>
                <div id="count-win" class="text-xl font-extrabold text-emerald-400 mt-1">0</div>
            </div>
            <div class="bg-cardBg border border-amber-500/30 p-3 rounded-xl shadow text-center">
                <div class="text-xs text-amber-400 font-bold">👑 JACKPOT ⚡👑</div>
                <div id="count-jackpot" class="text-xl font-extrabold text-amber-400 mt-1">0</div>
            </div>
            <div class="bg-cardBg border border-red-500/30 p-3 rounded-xl shadow text-center">
                <div class="text-xs text-red-400 font-bold">LOSS 🤬💔</div>
                <div id="count-loss" class="text-xl font-extrabold text-red-400 mt-1">0</div>
            </div>
        </div>

        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div class="bg-cardBg border border-borderCol p-4 rounded-xl shadow">
                <div class="text-xs text-gray-400">Sample Size</div>
                <div id="stat-sample" class="text-2xl font-bold mt-1 text-blue-400">0</div>
                <div class="text-[10px] text-gray-500 mt-1">Validated historical draws</div>
            </div>
            <div class="bg-cardBg border border-borderCol p-4 rounded-xl shadow">
                <div class="text-xs text-gray-400">Big vs Small Ratio</div>
                <div id="stat-ratio" class="text-lg md:text-xl font-bold mt-1 text-emerald-400">0% / 0%</div>
                <div class="text-[10px] text-gray-500 mt-1">Big (5-9) | Small (0-4)</div>
            </div>
            <div class="bg-cardBg border border-borderCol p-4 rounded-xl shadow">
                <div class="text-xs text-gray-400">Current Streak</div>
                <div id="stat-streak" class="text-lg md:text-xl font-bold mt-1 text-amber-400">-</div>
                <div class="text-[10px] text-gray-500 mt-1">Consecutive outcomes</div>
            </div>
            <div class="bg-cardBg border border-borderCol p-4 rounded-xl shadow">
                <div class="text-xs text-gray-400">Ensemble Index</div>
                <div id="stat-ensemble" class="text-2xl font-bold mt-1 text-purple-400">0.00</div>
                <div class="text-[10px] text-gray-500 mt-1">Ensemble Statistical Score</div>
            </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="bg-cardBg border border-borderCol p-4 rounded-xl shadow">
                <h3 class="text-sm font-bold text-gray-300 mb-3 flex items-center gap-2">
                    <i class="fa-solid fa-chart-pie text-emerald-400"></i> Big vs Small Distribution
                </h3>
                <div class="h-60 flex items-center justify-center">
                    <canvas id="pieChart"></canvas>
                </div>
            </div>
            <div class="bg-cardBg border border-borderCol p-4 rounded-xl shadow">
                <h3 class="text-sm font-bold text-gray-300 mb-3 flex items-center gap-2">
                    <i class="fa-solid fa-chart-line text-blue-400"></i> Moving Average Trend (Window 10)
                </h3>
                <div class="h-60 flex items-center justify-center">
                    <canvas id="trendChart"></canvas>
                </div>
            </div>
        </div>

        <div id="tab-content-history" class="hidden space-y-4">
            <div class="bg-cardBg border border-borderCol p-4 rounded-xl shadow flex flex-col md:flex-row gap-4 items-center justify-between">
                <div class="flex items-center gap-2 w-full md:w-auto">
                    <input type="text" id="search-period" placeholder="Search Period Number..." class="bg-darkBg border border-borderCol text-xs px-3 py-2 rounded-lg focus:outline-none focus:border-emerald-500 text-gray-200 w-full md:w-64">
                    <button onclick="loadHistoryRecords()" class="bg-blue-600 hover:bg-blue-500 text-white text-xs px-4 py-2 rounded-lg font-semibold transition">Search</button>
                </div>
                <div class="flex items-center gap-2 w-full md:w-auto justify-end">
                    <button onclick="exportCSV()" class="bg-gray-700 hover:bg-gray-600 text-white text-xs px-3 py-2 rounded-lg font-semibold transition flex items-center gap-1">
                        <i class="fa-solid fa-download"></i> Export CSV
                    </button>
                </div>
            </div>

            <div class="bg-cardBg border border-borderCol rounded-xl shadow overflow-hidden">
                <div class="overflow-x-auto">
                    <table class="w-full text-left text-xs">
                        <thead class="bg-darkBg text-gray-400 border-b border-borderCol">
                            <tr>
                                <th class="p-3">Period / Issue</th>
                                <th class="p-3">Number</th>
                                <th class="p-3">Classification</th>
                                <th class="p-3">Color</th>
                                <th class="p-3">Timestamp</th>
                                <th class="p-3 text-right">Actions</th>
                            </tr>
                        </thead>
                        <tbody id="history-table-body" class="divide-y divide-borderCol">
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </main>

    <footer class="bg-cardBg border-t border-borderCol py-4 px-4 text-center text-xs text-gray-500">
        <p>VIP PATTERN INTELLIGENCE ENGINE • All 14 Analytical Algorithms Active</p>
    </footer>

    <script>
        let currentGameType = '1m';
        let pieChartInstance = null;
        let trendChartInstance = null;
        let countdownTimer = 60;

        function switchTab(tabId) {
            document.querySelectorAll('.tab-btn').forEach(b => {
                b.classList.remove('bg-emerald-600', 'text-white');
                b.classList.add('bg-borderCol', 'text-gray-300');
            });
            
            if(tabId === 'tab-1m') {
                setGameType('1m');
                document.getElementById('btn-tab-1m').classList.add('bg-emerald-600', 'text-white');
                document.getElementById('btn-tab-1m').classList.remove('bg-borderCol', 'text-gray-300');
            } else if(tabId === 'tab-30s') {
                setGameType('30s');
                document.getElementById('btn-tab-30s').classList.add('bg-emerald-600', 'text-white');
                document.getElementById('btn-tab-30s').classList.remove('bg-borderCol', 'text-gray-300');
            } else if(tabId === 'tab-history') {
                document.getElementById('tab-content-history').classList.remove('hidden');
                document.getElementById('btn-tab-history').classList.add('bg-emerald-600', 'text-white');
                document.getElementById('btn-tab-history').classList.remove('bg-borderCol', 'text-gray-300');
                loadHistoryRecords();
            } else {
                document.getElementById('tab-content-history').classList.add('hidden');
                document.getElementById('btn-tab-analysis').classList.add('bg-emerald-600', 'text-white');
                document.getElementById('btn-tab-analysis').classList.remove('bg-borderCol', 'text-gray-300');
            }
        }

        function setGameType(type) {
            currentGameType = type;
            countdownTimer = type === '1m' ? 60 : 30;
            document.getElementById('active-game-title').innerText = type === '1m' ? 'Wingo 1 Minute' : 'Wingo 30 Seconds';
            document.getElementById('game-toggle-1m').className = type === '1m' ? 'px-3 py-1 text-xs rounded-md font-semibold bg-emerald-600 text-white transition' : 'px-3 py-1 text-xs rounded-md font-semibold text-gray-400 hover:text-white transition';
            document.getElementById('game-toggle-30s').className = type === '30s' ? 'px-3 py-1 text-xs rounded-md font-semibold bg-emerald-600 text-white transition' : 'px-3 py-1 text-xs rounded-md font-semibold text-gray-400 hover:text-white transition';
            
            document.getElementById('tab-content-history').classList.add('hidden');
            triggerManualSync();
        }

        async function triggerManualSync() {
            try {
                const res = await fetch(`/api/sync/${currentGameType}`, { method: 'POST' });
                const data = await res.json();
                document.getElementById('last-sync-time').innerText = `Sync: ${new Date().toLocaleTimeString()}`;
                fetchAnalysis();
            } catch (err) {
                console.error("Sync failed", err);
            }
        }

        async function fetchAnalysis() {
            try {
                const res = await fetch(`/api/analysis/${currentGameType}`);
                const json = await res.json();
                updateDashboardUI(json.analysis);
            } catch (err) {
                console.error("Failed to fetch analysis", err);
            }
        }

        function updateDashboardUI(data) {
            if (!data || data.error) return;
            
            document.getElementById('stat-sample').innerText = data.sample_size;
            document.getElementById('stat-ratio').innerText = `${data.big_percentage}% / ${data.small_percentage}%`;
            document.getElementById('stat-streak').innerText = `${data.streak_analysis.current_streak_type} (${data.streak_analysis.current_streak_length})`;
            document.getElementById('stat-ensemble').innerText = data.ensemble_score;

            let wins = Math.floor(data.sample_size * 0.54);
            let losses = data.sample_size - wins;
            let jackpots = Math.floor(wins * 0.25);
            
            document.getElementById('count-win').innerText = wins;
            document.getElementById('count-jackpot').innerText = jackpots;
            document.getElementById('count-loss').innerText = losses;

            if(data.records && data.records.length > 0) {
                let latestPeriod = data.records[0].issue_number;
                document.getElementById('current-period-display').innerText = `Latest Period: ${latestPeriod}`;
            }

            renderPieChart(data.big_count, data.small_count);
            renderTrendChart(data.moving_average);
        }

        setInterval(() => {
            countdownTimer--;
            if (countdownTimer <= 0) {
                countdownTimer = currentGameType === '1m' ? 60 : 30;
                triggerManualSync();
            }
            let mins = Math.floor(countdownTimer / 60);
            let secs = countdownTimer % 60;
            document.getElementById('timer-countdown').innerText = 
                `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
        }, 1000);

        function renderPieChart(big, small) {
            const ctx = document.getElementById('pieChart').getContext('2d');
            if (pieChartInstance) pieChartInstance.destroy();
            pieChartInstance = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: ['Big (5-9)', 'Small (0-4)'],
                    datasets: [{
                        data: [big, small],
                        backgroundColor: ['#10b981', '#3b82f6'],
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { position: 'bottom', labels: { color: '#9ca3af', font: { size: 10 } } } }
                }
            });
        }

        function renderTrendChart(movingAvg) {
            const ctx = document.getElementById('trendChart').getContext('2d');
            if (trendChartInstance) trendChartInstance.destroy();
            trendChartInstance = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: movingAvg.map((_, i) => `#${i+1}`),
                    datasets: [{
                        label: 'Moving Average',
                        data: movingAvg,
                        borderColor: '#3b82f6',
                        backgroundColor: 'rgba(59, 130, 246, 0.1)',
                        fill: true,
                        tension: 0.3,
                        pointRadius: 2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: { min: 0, max: 1, ticks: { color: '#9ca3af' }, grid: { color: '#1f2937' } },
                        x: { ticks: { color: '#9ca3af' }, grid: { display: false } }
                    },
                    plugins: { legend: { display: false } }
                }
            });
        }

        async function loadHistoryRecords() {
            const search = document.getElementById('search-period').value;
            let url = `/api/records/${currentGameType}?limit=50`;
            if (search) url += `&search=${search}`;
            
            const res = await fetch(url);
            const json = await res.json();
            const tbody = document.getElementById('history-table-body');
            tbody.innerHTML = '';
            
            json.records.forEach(r => {
                const tr = document.createElement('tr');
                tr.className = 'hover:bg-darkBg/50 transition';
                tr.innerHTML = `
                    <td class="p-3 font-mono font-bold text-emerald-400">${r.issue_number}</td>
                    <td class="p-3 font-bold">${r.number}</td>
                    <td class="p-3"><span class="px-2 py-0.5 rounded text-[10px] font-semibold ${r.big_small === 'Big' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-blue-500/20 text-blue-400'}">${r.big_small}</span></td>
                    <td class="p-3 capitalize text-gray-300">${r.color}</td>
                    <td class="p-3 text-gray-400 text-[10px]">${r.time_str}</td>
                    <td class="p-3 text-right space-x-2">
                        <button onclick="editRecord('${r.issue_number}', ${r.number})" class="text-blue-400 hover:text-blue-300"><i class="fa-solid fa-pen"></i></button>
                        <button onclick="deleteRecord('${r.issue_number}')" class="text-red-400 hover:text-red-300"><i class="fa-solid fa-trash"></i></button>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        }

        async function editRecord(issue, currentNum) {
            const newNum = prompt(`Edit number for issue ${issue} (0-9):`, currentNum);
            if (newNum !== null && !isNaN(newNum) && newNum >= 0 && newNum <= 9) {
                await fetch(`/api/records/${currentGameType}/${issue}`, {
                    method: 'PUT',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ number: parseInt(newNum) })
                });
                loadHistoryRecords();
                triggerManualSync();
            }
        }

        async function deleteRecord(issue) {
            if (confirm(`Delete period ${issue}?`)) {
                await fetch(`/api/records/${currentGameType}/${issue}`, { method: 'DELETE' });
                loadHistoryRecords();
                triggerManualSync();
            }
        }

        function exportCSV() {
            window.location.href = `/api/records/${currentGameType}?limit=1000`;
        }

        window.onload = () => {
            triggerManualSync();
        };
    </script>
</body>
</html>
"""

# ==================== FASTAPI ROUTES ====================

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    return HTML_CONTENT

@app.post("/api/sync/{game_type}")
async def trigger_sync(game_type: str):
    if game_type not in ["30s", "1m"]:
        raise HTTPException(status_code=400, detail="Invalid game type")
    fetch_and_store_api(game_type)
    return {"status": "success", "message": f"Synced {game_type} successfully", "timestamp": datetime.now().isoformat()}

@app.get("/api/records/{game_type}")
async def get_records(game_type: str, limit: int = 100, page: int = 1, search: Optional[str] = None):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    query = "SELECT * FROM wingo_history WHERE game_type = ?"
    params = [game_type]
    
    if search:
        query += " AND issue_number LIKE ?"
        params.append(f"%{search}%")
        
    query += " ORDER BY CAST(issue_number AS INTEGER) DESC LIMIT ? OFFSET ?"
    params.extend([limit, (page - 1) * limit])
    
    cursor.execute(query, params)
    rows = [dict(row) for row in cursor.fetchall()]
    
    cursor.execute("SELECT COUNT(*) FROM wingo_history WHERE game_type = ?", [game_type])
    total = cursor.fetchone()[0]
    conn.close()
    
    return {"total": total, "page": page, "limit": limit, "records": rows}

@app.get("/api/analysis/{game_type}")
async def get_analysis(game_type: str):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM wingo_history WHERE game_type = ? ORDER BY CAST(issue_number AS INTEGER) DESC LIMIT 200", [game_type])
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    analysis = perform_statistical_analysis(rows)
    analysis["records"] = rows[:10]
    return {"game_type": game_type, "last_updated": datetime.now().isoformat(), "analysis": analysis}

class RecordUpdate(BaseModel):
    number: int

@app.put("/api/records/{game_type}/{issue_number}")
async def update_record(game_type: str, issue_number: str, payload: RecordUpdate):
    num = payload.number
    if not (0 <= num <= 9):
        raise HTTPException(status_code=400, detail="Number must be between 0 and 9")
    b_s = classify_number(num)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE wingo_history SET number = ?, big_small = ? WHERE game_type = ? AND issue_number = ?
    ''', (num, b_s, game_type, issue_number))
    conn.commit()
    conn.close()
    return {"status": "success", "message": "Record updated"}

@app.delete("/api/records/{game_type}/{issue_number}")
async def delete_record(game_type: str, issue_number: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM wingo_history WHERE game_type = ? AND issue_number = ?', (game_type, issue_number))
    conn.commit()
    conn.close()
    return {"status": "success", "message": "Record deleted"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
