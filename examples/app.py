"""
Interactive Web Playground for Social-Humanizer.
Runs standalone with zero mandatory dependencies (pure Python http.server)
or launches Gradio UI if Gradio is installed and specified.

Usage:
    python examples/app.py
    python examples/app.py --port 7860
    python examples/app.py --gradio (if gradio is installed)
"""

import argparse
import json
import os
import sys
from http import HTTPStatus
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse

# Ensure repository root is on sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from social_humanizer.engine import HumanizerEngine, Platform
from social_humanizer.metrics import evaluate_text, audit_algorithm

HTML_UI = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Social-Humanizer 🧠✍️ | Anti-AI & Algorithm Compliance Playground</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg: #090d16;
            --surface: #101726;
            --surface-hover: #172238;
            --border: #1e293b;
            --border-highlight: #334155;
            --text: #f8fafc;
            --text-dim: #94a3b8;
            --primary: #38bdf8;
            --primary-glow: rgba(56, 189, 248, 0.15);
            --success: #10b981;
            --success-bg: rgba(16, 185, 129, 0.12);
            --warning: #f59e0b;
            --warning-bg: rgba(245, 158, 11, 0.12);
            --danger: #ef4444;
            --danger-bg: rgba(239, 68, 68, 0.12);
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.5;
            padding: 24px 16px;
            min-height: 100vh;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 28px;
            padding-bottom: 20px;
            border-bottom: 1px solid var(--border);
            flex-wrap: wrap;
            gap: 16px;
        }
        .logo-group {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .logo-icon {
            font-size: 32px;
            background: linear-gradient(135deg, #38bdf8, #818cf8);
            border-radius: 12px;
            width: 48px;
            height: 48px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        h1 { font-size: 24px; font-weight: 800; letter-spacing: -0.02em; }
        .subtitle { font-size: 13px; color: var(--text-dim); }
        .badge {
            background: var(--primary-glow);
            color: var(--primary);
            border: 1px solid rgba(56, 189, 248, 0.3);
            padding: 6px 12px;
            border-radius: 999px;
            font-size: 12px;
            font-weight: 600;
        }
        .grid {
            display: grid;
            grid-template-columns: 1.1fr 1fr;
            gap: 24px;
        }
        @media (max-width: 900px) {
            .grid { grid-template-columns: 1fr; }
        }
        .card {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 20px;
        }
        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
        }
        .card-title {
            font-size: 16px;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .platform-tabs {
            display: flex;
            background: var(--bg);
            padding: 4px;
            border-radius: 10px;
            border: 1px solid var(--border);
            margin-bottom: 16px;
            gap: 4px;
            overflow-x: auto;
        }
        .platform-btn {
            background: transparent;
            border: none;
            color: var(--text-dim);
            padding: 8px 14px;
            font-size: 13px;
            font-weight: 600;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s;
            white-space: nowrap;
        }
        .platform-btn:hover { color: var(--text); }
        .platform-btn.active {
            background: var(--surface-hover);
            color: var(--primary);
            box-shadow: 0 1px 3px rgba(0,0,0,0.2);
            border: 1px solid var(--border-highlight);
        }
        .preset-bar {
            display: flex;
            gap: 8px;
            margin-bottom: 12px;
            flex-wrap: wrap;
        }
        .preset-btn {
            background: var(--surface-hover);
            border: 1px solid var(--border);
            color: var(--text-dim);
            padding: 5px 10px;
            font-size: 11px;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.15s;
        }
        .preset-btn:hover {
            color: var(--text);
            border-color: var(--text-dim);
        }
        textarea {
            width: 100%;
            height: 220px;
            background: var(--bg);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 14px;
            color: var(--text);
            font-family: inherit;
            font-size: 14px;
            line-height: 1.6;
            resize: vertical;
            outline: none;
            transition: border 0.2s;
        }
        textarea:focus { border-color: var(--primary); }
        .actions-row {
            display: flex;
            gap: 12px;
            margin-top: 14px;
        }
        .btn {
            flex: 1;
            padding: 12px 18px;
            font-size: 14px;
            font-weight: 700;
            border-radius: 10px;
            border: none;
            cursor: pointer;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }
        .btn-primary {
            background: linear-gradient(135deg, #0284c7, #2563eb);
            color: white;
        }
        .btn-primary:hover { opacity: 0.95; transform: translateY(-1px); }
        .btn-secondary {
            background: var(--surface-hover);
            color: var(--text);
            border: 1px solid var(--border);
        }
        .btn-secondary:hover { background: var(--border); }
        
        /* Metric Scorecards */
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 12px;
            margin-bottom: 16px;
        }
        .metric-box {
            background: var(--bg);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 14px;
        }
        .metric-label {
            font-size: 12px;
            color: var(--text-dim);
            font-weight: 500;
            margin-bottom: 4px;
        }
        .metric-value {
            font-size: 22px;
            font-weight: 800;
            display: flex;
            align-items: baseline;
            gap: 6px;
        }
        .metric-sub {
            font-size: 11px;
            color: var(--text-dim);
            margin-top: 4px;
        }
        .meter-track {
            height: 6px;
            background: rgba(255,255,255,0.08);
            border-radius: 999px;
            margin-top: 8px;
            overflow: hidden;
        }
        .meter-fill {
            height: 100%;
            border-radius: 999px;
            transition: width 0.4s ease;
        }
        
        /* Warnings & Clichés */
        .warning-card {
            padding: 12px;
            border-radius: 10px;
            margin-bottom: 10px;
            font-size: 13px;
        }
        .warning-high {
            background: var(--danger-bg);
            border: 1px solid rgba(239, 68, 68, 0.3);
            color: #fca5a5;
        }
        .warning-medium {
            background: var(--warning-bg);
            border: 1px solid rgba(245, 158, 11, 0.3);
            color: #fcd34d;
        }
        .warning-fix {
            margin-top: 6px;
            font-size: 12px;
            color: var(--text);
            font-weight: 500;
        }
        .cliche-tag {
            display: inline-block;
            background: rgba(239, 68, 68, 0.2);
            color: #f87171;
            border: 1px solid rgba(239, 68, 68, 0.4);
            padding: 3px 8px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 600;
            margin: 3px 3px 3px 0;
            font-family: 'JetBrains Mono', monospace;
        }
        .recommendation-item {
            display: flex;
            align-items: flex-start;
            gap: 8px;
            margin-bottom: 8px;
            font-size: 13px;
            color: var(--text);
        }
        .output-box {
            background: var(--bg);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 14px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 13px;
            color: #e2e8f0;
            white-space: pre-wrap;
            max-height: 280px;
            overflow-y: auto;
        }
        .copy-btn {
            background: var(--surface-hover);
            border: 1px solid var(--border);
            color: var(--text-dim);
            padding: 4px 8px;
            font-size: 11px;
            border-radius: 6px;
            cursor: pointer;
        }
        .copy-btn:hover { color: var(--text); }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="logo-group">
                <div class="logo-icon">🧠</div>
                <div>
                    <h1>Social-Humanizer Playground</h1>
                    <div class="subtitle">Anti-AI Algorithm Risk Auditor & Copywriting Engine (FB, LinkedIn, X, Threads, IG)</div>
                </div>
            </div>
            <div style="display: flex; gap: 8px;">
                <span class="badge">Bilingual (EN + BN)</span>
                <span class="badge">Zero Outbound Penalties</span>
            </div>
        </header>

        <div class="grid">
            <!-- Left Column: Input & Controls -->
            <div class="card">
                <div class="card-header">
                    <div class="card-title">📝 Draft Topic or Post</div>
                    <span id="charCount" style="font-size: 12px; color: var(--text-dim);">0 chars</span>
                </div>

                <div class="platform-tabs">
                    <button class="platform-btn active" onclick="setPlatform('facebook', this)">📘 Facebook</button>
                    <button class="platform-btn" onclick="setPlatform('linkedin', this)">💼 LinkedIn</button>
                    <button class="platform-btn" onclick="setPlatform('twitter', this)">🐦 Twitter/X</button>
                    <button class="platform-btn" onclick="setPlatform('threads', this)">🧵 Threads</button>
                    <button class="platform-btn" onclick="setPlatform('instagram', this)">📸 Instagram</button>
                </div>

                <div class="preset-bar">
                    <span style="font-size: 11px; color: var(--text-dim); align-self: center;">Presets:</span>
                    <button class="preset-btn" onclick="loadPreset('robotic_en')">🤖 Robotic English</button>
                    <button class="preset-btn" onclick="loadPreset('robotic_bn')">🇧🇩 Cliché Bengali</button>
                    <button class="preset-btn" onclick="loadPreset('link_penalty')">🔗 Link Penalty</button>
                    <button class="preset-btn" onclick="loadPreset('human_authentic')">✨ Authentic Post</button>
                </div>

                <textarea id="draftInput" placeholder="Paste your social media draft or topic here to evaluate AI presence, cadence burstiness, and algorithmic reach risks..."></textarea>

                <div class="actions-row">
                    <button class="btn btn-primary" onclick="auditText()">🛡️ Audit & Score Post</button>
                    <button class="btn btn-primary" style="background: linear-gradient(135deg, #10b981, #059669);" onclick="humanizeText()">✨ Humanize Draft</button>
                    <button class="btn btn-secondary" onclick="viewSystemPrompt()">📜 View Prompt Blueprint</button>
                </div>
            </div>

            <!-- Right Column: Audit Results -->
            <div class="card">
                <div class="card-header">
                    <div class="card-title">📊 Algorithmic Audit & Scores</div>
                    <span id="overallBadge" class="badge">Awaiting text</span>
                </div>

                <div class="metrics-grid">
                    <div class="metric-box">
                        <div class="metric-label">Human Authenticity Score</div>
                        <div class="metric-value" id="humanScore">-- <span style="font-size: 13px; font-weight: 500; color: var(--text-dim);">/ 100</span></div>
                        <div class="meter-track"><div id="humanMeter" class="meter-fill" style="width: 0%; background: var(--primary);"></div></div>
                        <div class="metric-sub" id="humanStatus">Benchmark: ≥ 70.0 pts</div>
                    </div>

                    <div class="metric-box">
                        <div class="metric-label">Algorithmic Reach Penalty Risk</div>
                        <div class="metric-value" id="algoRisk">-- <span style="font-size: 13px; font-weight: 500; color: var(--text-dim);">/ 100</span></div>
                        <div class="meter-track"><div id="riskMeter" class="meter-fill" style="width: 0%; background: var(--success);"></div></div>
                        <div class="metric-sub" id="algoRiskText">Target: &lt; 25 (Safe)</div>
                    </div>

                    <div class="metric-box">
                        <div class="metric-label">Burstiness (Cadence CV)</div>
                        <div class="metric-value" id="burstCV">--</div>
                        <div class="meter-track"><div id="burstMeter" class="meter-fill" style="width: 0%; background: var(--primary);"></div></div>
                        <div class="metric-sub" id="burstStatus">Formula: σ / μ (Target ≥ 0.45)</div>
                    </div>

                    <div class="metric-box">
                        <div class="metric-label">Outbound Links & Hashtags</div>
                        <div class="metric-value" id="linksTags">--</div>
                        <div class="metric-sub" id="linksTagsDetail">Links in body trigger 50%-80% penalty</div>
                    </div>
                </div>

                <!-- Algorithmic Warnings Section -->
                <div id="warningsSection" style="margin-top: 14px;">
                    <div style="font-size: 13px; font-weight: 700; margin-bottom: 8px; color: var(--text-dim);">⚠️ ALGORITHMIC FEED WARNINGS</div>
                    <div id="warningsList" style="font-size: 13px; color: var(--text-dim);">Run an audit to check for reach suppression risks.</div>
                </div>

                <!-- Flagged Clichés Section -->
                <div id="clichesSection" style="margin-top: 14px; display: none;">
                    <div style="font-size: 13px; font-weight: 700; margin-bottom: 6px; color: var(--danger);">🚨 DETECTED AI CLICHÉS</div>
                    <div id="clichesList"></div>
                </div>

                <!-- Actionable Plan -->
                <div id="recommendationsSection" style="margin-top: 14px; display: none;">
                    <div style="font-size: 13px; font-weight: 700; margin-bottom: 8px; color: var(--primary);">💡 ACTIONABLE FIXES</div>
                    <div id="recommendationsList"></div>
                </div>

                <!-- Output Blueprint Modal / Box -->
                <div id="outputSection" style="margin-top: 16px; display: none;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <span id="outputTitle" style="font-size: 13px; font-weight: 700; color: var(--text-dim);">PROMPT BLUEPRINT FOR LLM:</span>
                        <button class="copy-btn" onclick="copyOutput()">📋 Copy</button>
                    </div>
                    <div id="outputContent" class="output-box"></div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let currentPlatform = 'facebook';

        const PRESETS = {
            robotic_en: "🚀 Elevate your productivity today! In today's fast-paced digital world, it is crucial to delve into transformative technologies. 💡 Unlock your true potential with our seamless AI platform: https://innovate-now.io/start #tech #ai #innovation #future #growth",
            robotic_bn: "আজকের দ্রুত পরিবর্তনশীল বিশ্বে প্রোগ্রামিং এবং এআই শেখার গুরুত্ব অপরিসীম। আসুন এক নজরে দেখে নেওয়া যাক সফলতার মূল চাবিকাঠি কি কি। নিচে বিস্তারিত আলোচনা করা হলো।",
            link_penalty: "We just published a comprehensive breakdown on mastering social algorithms! Read the full deep-dive article right here: https://social-humanizer.dev/blog/anti-ai-algorithm-tricks",
            human_authentic: "I noticed something strange about software yesterday.\\n\\nComputers are fundamentally dumb.\\n\\nIf you miss a single semicolon, the entire compiler completely gives up and complains. Honestly, who else here has spent half the night debugging only to find a typo?"
        };

        function setPlatform(plat, btn) {
            currentPlatform = plat;
            document.querySelectorAll('.platform-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            if (document.getElementById('draftInput').value.trim()) {
                auditText();
            }
        }

        function loadPreset(key) {
            document.getElementById('draftInput').value = PRESETS[key];
            updateCharCount();
            auditText();
        }

        function updateCharCount() {
            const len = document.getElementById('draftInput').value.length;
            document.getElementById('charCount').textContent = len + ' chars';
        }

        document.getElementById('draftInput').addEventListener('input', updateCharCount);

        async function auditText() {
            const text = document.getElementById('draftInput').value.trim();
            if (!text) {
                alert('Please enter or paste draft text first.');
                return;
            }

            try {
                const resp = await fetch('/api/evaluate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text, platform: currentPlatform })
                });
                const data = await resp.json();
                renderReport(data);
            } catch (err) {
                console.error(err);
                alert('Audit request failed: ' + err);
            }
        }

        async function humanizeText() {
            const draft = document.getElementById('draftInput').value.trim();
            if (!draft) {
                alert('Please enter or paste draft text first.');
                return;
            }
            try {
                const resp = await fetch('/api/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ draft, platform: currentPlatform })
                });
                const data = await resp.json();
                document.getElementById('outputSection').style.display = 'block';
                document.getElementById('outputTitle').textContent = '✨ HUMANIZED OUTPUT:';
                document.getElementById('outputContent').textContent = data.output;
                if (data.report) {
                    renderReport(data.report);
                }
            } catch (err) {
                console.error(err);
                alert('Humanize request failed: ' + err);
            }
        }

        async function viewSystemPrompt() {
            try {
                const resp = await fetch('/api/prompt', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ platform: currentPlatform })
                });
                const data = await resp.json();
                document.getElementById('outputSection').style.display = 'block';
                document.getElementById('outputTitle').textContent = 'PROMPT BLUEPRINT FOR LLM:';
                document.getElementById('outputContent').textContent = data.prompt;
            } catch (err) {
                console.error(err);
            }
        }

        function renderReport(rep) {
            // Overall Badge
            const badge = document.getElementById('overallBadge');
            if (rep.is_human_sounding && rep.algorithm_risk_score < 25) {
                badge.textContent = '✅ Authentic Human';
                badge.style.background = 'var(--success-bg)';
                badge.style.color = 'var(--success)';
                badge.style.borderColor = 'rgba(16, 185, 129, 0.4)';
            } else if (rep.human_score >= 50) {
                badge.textContent = '⚠️ Polish Needed';
                badge.style.background = 'var(--warning-bg)';
                badge.style.color = 'var(--warning)';
                badge.style.borderColor = 'rgba(245, 158, 11, 0.4)';
            } else {
                badge.textContent = '🚨 High AI Risk';
                badge.style.background = 'var(--danger-bg)';
                badge.style.color = 'var(--danger)';
                badge.style.borderColor = 'rgba(239, 68, 68, 0.4)';
            }

            // Human Score
            document.getElementById('humanScore').innerHTML = `${rep.human_score.toFixed(1)} <span style="font-size: 13px; font-weight: 500; color: var(--text-dim);">/ 100</span>`;
            const hMeter = document.getElementById('humanMeter');
            hMeter.style.width = Math.min(100, rep.human_score) + '%';
            hMeter.style.background = rep.human_score >= 70 ? 'var(--success)' : (rep.human_score >= 50 ? 'var(--warning)' : 'var(--danger)');

            // Algo Risk
            document.getElementById('algoRisk').innerHTML = `${rep.algorithm_risk_score.toFixed(0)} <span style="font-size: 13px; font-weight: 500; color: var(--text-dim);">/ 100</span>`;
            const rMeter = document.getElementById('riskMeter');
            rMeter.style.width = Math.min(100, rep.algorithm_risk_score) + '%';
            rMeter.style.background = rep.algorithm_risk_score < 25 ? 'var(--success)' : (rep.algorithm_risk_score < 60 ? 'var(--warning)' : 'var(--danger)');
            document.getElementById('algoRiskText').textContent = rep.algorithm_risk_level;

            // Burstiness
            document.getElementById('burstCV').textContent = rep.burstiness_score.toFixed(2);
            const bMeter = document.getElementById('burstMeter');
            const burstPct = Math.min(100, (rep.burstiness_score / 0.5) * 100);
            bMeter.style.width = burstPct + '%';
            bMeter.style.background = rep.burstiness_score >= 0.45 ? 'var(--success)' : (rep.burstiness_score >= 0.35 ? 'var(--warning)' : 'var(--danger)');
            document.getElementById('burstStatus').textContent = rep.burstiness_score >= 0.45 ? 'High dynamic cadence' : 'Monotonous sentence lengths';

            // Links & Tags
            const linkCount = rep.external_links ? rep.external_links.length : 0;
            document.getElementById('linksTags').textContent = `${linkCount} link(s) • ${rep.hashtag_count} tag(s)`;
            document.getElementById('linksTagsDetail').textContent = rep.has_external_links ? '⚠️ Outbound link: Move to 1st comment!' : 'Zero link reach suppression';

            // Warnings
            const warningsList = document.getElementById('warningsList');
            warningsList.innerHTML = '';
            if (rep.audit && rep.audit.warnings && rep.audit.warnings.length > 0) {
                rep.audit.warnings.forEach(w => {
                    const cls = w.severity === 'high' ? 'warning-high' : 'warning-medium';
                    const div = document.createElement('div');
                    div.className = `warning-card ${cls}`;
                    div.innerHTML = `<div><strong>[${w.category}]</strong> ${w.message}</div><div class="warning-fix">↳ Fix: ${w.recommendation}</div>`;
                    warningsList.appendChild(div);
                });
            } else {
                warningsList.innerHTML = '<div style="color: var(--success); font-weight: 600;">✅ Clean! No algorithmic reach suppression flags found.</div>';
            }

            // Clichés
            const clichesSec = document.getElementById('clichesSection');
            const clichesList = document.getElementById('clichesList');
            if (rep.flagged_cliches && rep.flagged_cliches.length > 0) {
                clichesSec.style.display = 'block';
                clichesList.innerHTML = rep.flagged_cliches.map(c => `<span class="cliche-tag">✖ ${c}</span>`).join(' ');
            } else {
                clichesSec.style.display = 'none';
            }

            // Recommendations
            const recSec = document.getElementById('recommendationsSection');
            const recList = document.getElementById('recommendationsList');
            if (rep.recommendations && rep.recommendations.length > 0) {
                recSec.style.display = 'block';
                recList.innerHTML = rep.recommendations.map(r => `<div class="recommendation-item"><span style="color: var(--primary);">✔</span><span>${r}</span></div>`).join('');
            } else {
                recSec.style.display = 'none';
            }
        }

        function copyOutput() {
            const text = document.getElementById('outputContent').textContent;
            navigator.clipboard.writeText(text);
            alert('Prompt copied to clipboard!');
        }
    </script>
</body>
</html>
"""


class PlaygroundHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Quiet standard HTTP access logs
        return

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path in ("/", "/index.html"):
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_UI.encode("utf-8"))
        elif parsed.path == "/health":
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status": "ok"}')
        else:
            self.send_response(HTTPStatus.NOT_FOUND)
            self.end_headers()

    def do_POST(self):
        parsed = urlparse(self.path)
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        try:
            data = json.loads(body.decode("utf-8")) if body else {}
        except Exception:
            data = {}

        if parsed.path == "/api/evaluate":
            text = data.get("text", "")
            platform = data.get("platform", "facebook")
            report = evaluate_text(text, platform=platform)

            # Build serializable payload
            response_data = {
                "word_count": report.word_count,
                "sentence_count": report.sentence_count,
                "avg_sentence_length": report.avg_sentence_length,
                "burstiness_score": report.burstiness_score,
                "human_score": report.human_score,
                "grade_level": report.grade_level,
                "reading_ease": report.reading_ease,
                "flagged_cliches": report.flagged_cliches,
                "has_emoji_spam": report.has_emoji_spam,
                "is_human_sounding": report.is_human_sounding,
                "recommendations": report.recommendations,
                "has_external_links": report.has_external_links,
                "external_links": report.external_links,
                "hashtag_count": report.hashtag_count,
                "has_excessive_hashtags": report.has_excessive_hashtags,
                "algorithm_risk_score": report.algorithm_risk_score,
                "algorithm_risk_level": report.algorithm_risk_level,
                "audit": report.audit.to_dict() if report.audit else None,
            }

            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode("utf-8"))

        elif parsed.path == "/api/prompt":
            plat_str = data.get("platform", "facebook").lower()
            try:
                platform = Platform(plat_str)
            except Exception:
                platform = Platform.FACEBOOK
            engine = HumanizerEngine()
            prompt = engine.get_system_prompt(platform)

            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"platform": platform.value, "prompt": prompt}).encode("utf-8"))

        elif parsed.path == "/api/generate":
            draft = data.get("draft", "")
            plat_str = data.get("platform", "facebook").lower()
            try:
                platform = Platform(plat_str)
            except Exception:
                platform = Platform.FACEBOOK
            engine = HumanizerEngine(
                api_base=data.get("api_base"),
                api_key=data.get("api_key"),
                model=data.get("model"),
            )
            output, report = engine.generate(draft, platform=platform)

            response_data = {
                "output": output,
                "human_score": report.human_score,
                "risk_score": report.algorithm_risk_score,
                "report": {
                    "word_count": report.word_count,
                    "sentence_count": report.sentence_count,
                    "avg_sentence_length": report.avg_sentence_length,
                    "burstiness_score": report.burstiness_score,
                    "human_score": report.human_score,
                    "grade_level": report.grade_level,
                    "reading_ease": report.reading_ease,
                    "flagged_cliches": report.flagged_cliches,
                    "has_emoji_spam": report.has_emoji_spam,
                    "is_human_sounding": report.is_human_sounding,
                    "recommendations": report.recommendations,
                    "has_external_links": report.has_external_links,
                    "external_links": report.external_links,
                    "hashtag_count": report.hashtag_count,
                    "has_excessive_hashtags": report.has_excessive_hashtags,
                    "algorithm_risk_score": report.algorithm_risk_score,
                    "algorithm_risk_level": report.algorithm_risk_level,
                    "audit": report.audit.to_dict() if report.audit else None,
                },
            }

            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode("utf-8"))
        else:
            self.send_response(HTTPStatus.NOT_FOUND)
            self.end_headers()


def launch_gradio_app(host="127.0.0.1", port=7860):
    """Launches Gradio UI if gradio is installed."""
    try:
        import gradio as gr
    except ImportError:
        print("Gradio is not installed. To use Gradio, run: pip install gradio")
        print("Falling back to built-in zero-dependency web playground...")
        return False

    engine = HumanizerEngine()

    def gradio_eval(text, platform):
        report = evaluate_text(text, platform=platform)
        audit_warnings = "\n".join(
            f"- **[{w.severity.upper()}] {w.category}**: {w.message}\n  *Fix: {w.recommendation}*"
            for w in (report.audit.warnings if report.audit else [])
        ) or "✅ Clean! Zero algorithmic penalties flagged."
        
        cliches = ", ".join(report.flagged_cliches) or "None"
        recs = "\n".join(f"- {r}" for r in report.recommendations)

        summary_md = f"""
### 📊 Scorecard
- **Human Quality Score**: {report.human_score:.1f} / 100 ({'Passed' if report.is_human_sounding else 'Needs Polish'})
- **Algorithmic Reach Penalty Risk**: {report.algorithm_risk_score:.0f} / 100 ({report.algorithm_risk_level})
- **Burstiness (Cadence CV)**: {report.burstiness_score:.2f} (Target ≥ 0.45)
- **Reading Ease**: {report.reading_ease:.1f} ({report.grade_level})
- **Outbound Links in Body**: {len(report.external_links)}
- **Hashtags**: {report.hashtag_count}

### 🚨 Detected AI Clichés
{cliches}

### 🛡️ Algorithmic Risk Warnings
{audit_warnings}

### 💡 Improvement Recommendations
{recs}
"""
        prompt = engine.get_system_prompt(Platform(platform))
        return summary_md, prompt

    def gradio_humanize(text, platform):
        output, report = engine.generate(text, platform=Platform(platform))
        audit_warnings = "\n".join(
            f"- **[{w.severity.upper()}] {w.category}**: {w.message}\n  *Fix: {w.recommendation}*"
            for w in (report.audit.warnings if report.audit else [])
        ) or "✅ Clean! Zero algorithmic penalties flagged."
        summary_md = f"""
### ✨ Humanized Output
```text
{output}
```

### 📊 Humanized Post Scorecard
- **Human Quality Score**: {report.human_score:.1f} / 100 ({'Passed' if report.is_human_sounding else 'Needs Polish'})
- **Algorithmic Reach Penalty Risk**: {report.algorithm_risk_score:.0f} / 100 ({report.algorithm_risk_level})
- **Burstiness (Cadence CV)**: {report.burstiness_score:.2f} (Target ≥ 0.45)
- **Reading Ease**: {report.reading_ease:.1f} ({report.grade_level})
- **Outbound Links in Body**: {len(report.external_links)}
- **Hashtags**: {report.hashtag_count}

### 🛡️ Algorithmic Risk Warnings
{audit_warnings}
"""
        return summary_md, output

    with gr.Blocks(title="Social-Humanizer Playground") as demo:
        gr.Markdown("# 🧠 Social-Humanizer Playground\nUniversal Anti-AI Algorithm Risk Auditor & Copywriting Engine")
        with gr.Row():
            with gr.Column():
                input_text = gr.Textbox(
                    lines=8,
                    label="Draft Text or Topic",
                    placeholder="Enter social post draft to audit or humanize...",
                )
                platform_choice = gr.Dropdown(
                    choices=["facebook", "linkedin", "twitter", "threads", "instagram"],
                    value="facebook",
                    label="Target Platform",
                )
                with gr.Row():
                    audit_btn = gr.Button("🛡️ Audit Draft", variant="primary")
                    humanize_btn = gr.Button("✨ Humanize Draft", variant="secondary")
            with gr.Column():
                results_md = gr.Markdown("### Awaiting input...")
                prompt_output = gr.Code(label="Platform Blueprint Prompt / Output", language="markdown")

        audit_btn.click(
            gradio_eval,
            inputs=[input_text, platform_choice],
            outputs=[results_md, prompt_output],
        )
        humanize_btn.click(
            gradio_humanize,
            inputs=[input_text, platform_choice],
            outputs=[results_md, prompt_output],
        )

    demo.launch(server_name=host, server_port=port)
    return True


def run_server(host="127.0.0.1", port=7860, use_gradio=False):
    if use_gradio:
        if launch_gradio_app(host=host, port=port):
            return

    server_address = (host, port)
    httpd = HTTPServer(server_address, PlaygroundHandler)
    print(f"===============================================================")
    print(f"🚀 Social-Humanizer Web Playground running at: http://{host}:{port}")
    print(f"   - Anti-AI Cadence & Cliché Auditor")
    print(f"   - Reach Suppression Link Checker (50%-80% Demotion Warning)")
    print(f"   - Multi-Platform Support: FB, LinkedIn, Twitter, Threads, IG")
    print(f"   - Press Ctrl+C to stop the server.")
    print(f"===============================================================")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down playground server.")
        httpd.server_close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Social-Humanizer Web Playground")
    parser.add_argument("--host", default="127.0.0.1", help="Host address (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=7860, help="Port (default: 7860)")
    parser.add_argument("--gradio", action="store_true", help="Launch Gradio UI if installed")
    args = parser.parse_args()

    run_server(host=args.host, port=args.port, use_gradio=args.gradio)
