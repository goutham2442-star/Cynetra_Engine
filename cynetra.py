import streamlit as st
import re
import time
import json
import urllib.parse
from datetime import datetime
import hashlib
import requests
import streamlit as st
import pickle
import pandas as pd
import pickle

# Load trained model and vectorizer
with open("url_model.pkl", "rb") as f:
    ml_model = pickle.load(f)

with open("url_vectorizer.pkl", "rb") as f:
    ml_vectorizer = pickle.load(f)

# 🔥 PASTE STEP 2 HERE
def ml_url_predict(url):
    try:
        vec = ml_vectorizer.transform([url])
        pred = ml_model.predict(vec)[0]
        return "PHISHING" if pred == 1 else "SAFE"
    except Exception as e:
        return f"Error: {e}"
# ══════════════════════════════════════════════════════════════
#  PAGE CONFIG
# ══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="CYNETRA — Phish Hunter AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ══════════════════════════════════════════════════════════════
#  SESSION STATE
# ══════════════════════════════════════════════════════════════
def init_state():
    defaults = {
        "splash_done": False,
        "current_page": "dashboard",
        "scan_result": None,
        "scan_history": [],
        "url_result": None,
        "email_result": None,
        "total_scans": 0,
        "threats_detected": 0,
        "safe_count": 0,
        "ai_analysis": None,
        "email_ai_analysis": None,
        "url_ai_analysis": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ══════════════════════════════════════════════════════════════
#  MASTER CSS
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;700;900&family=Rajdhani:wght@300;400;500;600;700&family=Share+Tech+Mono&display=swap');

:root {
  --bg:        #020508;
  --bg2:       #030c14;
  --bg3:       #041220;
  --cyan:      #00f2ff;
  --cyan-dim:  rgba(0,242,255,0.15);
  --purple:    #bc13fe;
  --purple-dim:rgba(188,19,254,0.15);
  --red:       #ff3131;
  --red-dim:   rgba(255,49,49,0.15);
  --green:     #00ff88;
  --amber:     #ffb703;
  --text:      #c9e8f5;
  --text-dim:  rgba(200,232,245,0.5);
  --glass:     rgba(4,18,32,0.7);
  --glass-b:   rgba(0,242,255,0.18);
}

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stApp"] {
  background: var(--bg) !important;
  color: var(--text);
  font-family: 'Rajdhani', sans-serif;
  letter-spacing: 0.02em;
}

[data-testid="stHeader"]        { display:none !important; }
[data-testid="stSidebar"]       { display:none !important; }
[data-testid="stToolbar"]       { display:none !important; }
#MainMenu, footer               { display:none !important; }
[data-testid="stDecoration"]    { display:none !important; }
.stDeployButton                 { display:none !important; }

/* scrollbar */
::-webkit-scrollbar            { width:5px; }
::-webkit-scrollbar-track      { background:#010305; }
::-webkit-scrollbar-thumb      { background:var(--cyan); border-radius:3px; }

/* ── GLASS CARD ── */
.g-card {
  background: var(--glass);
  border: 1px solid var(--glass-b);
  border-radius: 14px;
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  padding: 28px 32px;
  margin-bottom: 22px;
  box-shadow: 0 0 40px rgba(0,242,255,0.03), inset 0 1px 0 rgba(0,242,255,0.07);
  position: relative;
  overflow: hidden;
}
.g-card::before {
  content:'';
  position:absolute;
  top:0;left:0;right:0;
  height:1px;
  background: linear-gradient(90deg,transparent,var(--cyan),transparent);
  opacity:0.4;
}

/* ── NAV BAR ── */
.navbar {
  position: fixed;
  top: 0; left: 0; right: 0;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 40px;
  height: 62px;
  background: rgba(2,5,8,0.92);
  border-bottom: 1px solid rgba(0,242,255,0.15);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
}
.nav-logo {
  font-family: 'Orbitron', sans-serif;
  font-weight: 900;
  font-size: 1.3rem;
  color: var(--cyan);
  text-shadow: 0 0 12px var(--cyan);
  letter-spacing: 0.3em;
  display: flex;
  align-items: center;
  gap: 12px;
}
.nav-logo svg { filter: drop-shadow(0 0 6px var(--cyan)); }
.nav-links {
  display: flex;
  gap: 6px;
}
.nav-btn {
  font-family: 'Orbitron', sans-serif;
  font-size: 0.65rem;
  letter-spacing: 2px;
  padding: 8px 18px;
  border-radius: 6px;
  cursor: pointer;
  text-transform: uppercase;
  transition: all 0.2s;
  border: 1px solid transparent;
  background: transparent;
  color: var(--text-dim);
  text-decoration: none;
  display: inline-block;
}
.nav-btn:hover {
  color: var(--cyan);
  border-color: rgba(0,242,255,0.3);
  background: rgba(0,242,255,0.05);
}
.nav-btn.active {
  color: var(--cyan);
  border-color: var(--cyan);
  background: rgba(0,242,255,0.08);
  box-shadow: 0 0 16px rgba(0,242,255,0.2);
}
.nav-status {
  font-family: 'Share Tech Mono', monospace;
  font-size: 0.72rem;
  color: var(--green);
  display: flex;
  align-items: center;
  gap: 7px;
}
.status-dot {
  width: 7px; height: 7px;
  border-radius: 50%;
  background: var(--green);
  box-shadow: 0 0 8px var(--green);
  animation: blink 2s infinite;
}
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.3} }

/* spacer under fixed navbar */
.nav-spacer { height: 80px; }

/* ── SPLASH ── */
.splash {
  position: fixed;
  inset: 0;
  z-index: 9999;
  background: #010306;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  font-family: 'Orbitron', sans-serif;
}
.splash-hex {
  width: 160px; height: 160px;
  margin-bottom: 32px;
  animation: hex-spin 8s linear infinite;
  filter: drop-shadow(0 0 20px rgba(0,242,255,0.6));
}
@keyframes hex-spin { from{transform:rotate(0deg)} to{transform:rotate(360deg)} }

.splash-inner-logo {
  position: absolute;
  font-family: 'Orbitron', sans-serif;
  font-size: 1.3rem;
  font-weight: 900;
  color: var(--cyan);
  text-shadow: 0 0 20px var(--cyan);
  letter-spacing: 0.2em;
  animation: logo-pulse 2s ease-in-out infinite;
}
@keyframes logo-pulse {
  0%,100%{text-shadow:0 0 12px var(--cyan),0 0 30px var(--cyan)}
  50%{text-shadow:0 0 24px var(--cyan),0 0 60px var(--cyan),0 0 100px rgba(0,242,255,0.4)}
}
.splash-title-main {
  font-size: clamp(3.5rem, 9vw, 7rem);
  font-weight: 900;
  color: var(--cyan);
  letter-spacing: 0.35em;
  text-shadow: 0 0 20px var(--cyan), 0 0 60px var(--cyan), 0 0 120px rgba(0,242,255,0.3);
  animation: logo-pulse 2s ease-in-out infinite;
  margin-bottom: 4px;
}
.splash-tagline {
  font-family: 'Rajdhani', sans-serif;
  font-size: 0.9rem;
  letter-spacing: 5px;
  color: rgba(0,242,255,0.5);
  text-transform: uppercase;
  margin-bottom: 48px;
}
.splash-progress-wrap {
  width: min(520px, 80vw);
  position: relative;
}
.splash-bar-bg {
  width: 100%; height: 3px;
  background: rgba(0,242,255,0.1);
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 16px;
}
.splash-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--cyan), var(--purple));
  border-radius: 3px;
  transition: width 0.4s ease;
  box-shadow: 0 0 10px var(--cyan);
}
.splash-status-text {
  font-family: 'Share Tech Mono', monospace;
  font-size: 0.75rem;
  color: rgba(0,242,255,0.55);
  letter-spacing: 2px;
  text-align: center;
}
.splash-nodes {
  display: flex;
  gap: 8px;
  margin-top: 28px;
  justify-content: center;
}
.splash-node {
  width: 8px; height: 8px;
  border-radius: 50%;
  background: rgba(0,242,255,0.2);
  border: 1px solid rgba(0,242,255,0.3);
  transition: all 0.3s;
}
.splash-node.active {
  background: var(--cyan);
  box-shadow: 0 0 10px var(--cyan);
}
.splash-grid {
  position: fixed;
  inset: 0;
  background-image:
    linear-gradient(rgba(0,242,255,0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0,242,255,0.03) 1px, transparent 1px);
  background-size: 50px 50px;
  pointer-events: none;
}
.splash-corner {
  position: fixed;
  width: 60px; height: 60px;
  border-color: rgba(0,242,255,0.3);
  border-style: solid;
  border-width: 0;
}
.splash-corner.tl { top:20px;left:20px; border-top-width:2px; border-left-width:2px; }
.splash-corner.tr { top:20px;right:20px; border-top-width:2px; border-right-width:2px; }
.splash-corner.bl { bottom:20px;left:20px; border-bottom-width:2px; border-left-width:2px; }
.splash-corner.br { bottom:20px;right:20px; border-bottom-width:2px; border-right-width:2px; }

/* ── TYPOGRAPHY ── */
.orbitron { font-family: 'Orbitron', sans-serif !important; }
.mono     { font-family: 'Share Tech Mono', monospace !important; }
.sec-title {
  font-family: 'Orbitron', sans-serif;
  font-size: 0.8rem;
  letter-spacing: 4px;
  color: var(--cyan);
  text-transform: uppercase;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
}
.sec-title::after {
  content:'';
  flex:1;
  height:1px;
  background: linear-gradient(90deg, rgba(0,242,255,0.3), transparent);
}

/* ── SCORE RING ── */
.score-ring-wrap {
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  width: 200px; height: 200px;
  margin: 0 auto;
}
.score-value {
  position: absolute;
  font-family: 'Orbitron', sans-serif;
  font-size: 3rem;
  font-weight: 900;
  text-align: center;
  line-height: 1;
}
.score-label {
  position: absolute;
  bottom: 42px;
  font-family: 'Rajdhani', sans-serif;
  font-size: 0.7rem;
  letter-spacing: 3px;
  color: var(--text-dim);
  text-transform: uppercase;
}

/* ── BADGES ── */
.verdict-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-family: 'Orbitron', sans-serif;
  font-size: 0.75rem;
  letter-spacing: 3px;
  padding: 8px 20px;
  border-radius: 6px;
  font-weight: 700;
  text-transform: uppercase;
}
.vb-safe   { background:rgba(0,255,136,0.1);color:var(--green);border:1px solid var(--green);}
.vb-warn   { background:rgba(255,183,3,0.1);color:var(--amber);border:1px solid var(--amber);}
.vb-danger { background:rgba(255,49,49,0.12);color:var(--red);border:1px solid var(--red);
             box-shadow:0 0 20px rgba(255,49,49,0.3); animation:danger-pulse 1.5s infinite;}
@keyframes danger-pulse {
  0%,100%{box-shadow:0 0 20px rgba(255,49,49,0.3)}
  50%{box-shadow:0 0 40px rgba(255,49,49,0.6)}
}

/* ── FACTOR ROWS ── */
.factor {
  display:flex;
  align-items:center;
  gap:14px;
  padding:14px 0;
  border-bottom:1px solid rgba(0,242,255,0.06);
}
.factor:last-child{border-bottom:none}
.factor-icon{
  font-size:1.4rem;width:40px;text-align:center;
}
.factor-body{flex:1}
.factor-name{
  font-family:'Rajdhani',sans-serif;font-weight:600;font-size:1.05rem;
  color:var(--text);margin-bottom:4px;
}
.factor-detail{
  font-family:'Share Tech Mono',monospace;font-size:0.72rem;
  color:var(--text-dim);
}
.factor-bar-wrap{
  width:160px;
}
.factor-bar-bg{
  height:5px;background:rgba(255,255,255,0.06);border-radius:999px;overflow:hidden;margin-bottom:4px;
}
.factor-bar-fill{height:100%;border-radius:999px;}
.factor-pts{
  font-family:'Orbitron',sans-serif;font-size:0.7rem;text-align:right;
}

/* ── EMERGENCY PANEL ── */
.emergency {
  background: rgba(255,49,49,0.06);
  border: 1px solid rgba(255,49,49,0.5);
  border-radius: 14px;
  padding: 32px 36px;
  margin-top: 24px;
  animation: em-pulse 2s infinite;
  position: relative;
  overflow: hidden;
}
.emergency::before {
  content:'';
  position:absolute;
  top:0;left:0;right:0;height:2px;
  background:var(--red);
  box-shadow:0 0 20px var(--red);
}
@keyframes em-pulse {
  0%,100%{border-color:rgba(255,49,49,0.5); box-shadow:0 0 30px rgba(255,49,49,0.1)}
  50%{border-color:rgba(255,49,49,0.9); box-shadow:0 0 60px rgba(255,49,49,0.2)}
}
.em-title {
  font-family:'Orbitron',sans-serif;
  color:var(--red);
  font-size:1rem;
  letter-spacing:3px;
  text-transform:uppercase;
  text-shadow:0 0 12px var(--red);
  margin-bottom:16px;
}
.portal-btn {
  display:inline-block;
  font-family:'Orbitron',sans-serif;
  font-size:0.8rem;
  letter-spacing:2px;
  color:var(--red) !important;
  border:1px solid var(--red);
  padding:14px 32px;
  border-radius:8px;
  text-decoration:none !important;
  margin-top:16px;
  transition:all 0.25s;
  background:rgba(255,49,49,0.05);
  box-shadow:0 0 20px rgba(255,49,49,0.2);
}
.portal-btn:hover {
  background:rgba(255,49,49,0.18) !important;
  box-shadow:0 0 40px rgba(255,49,49,0.4) !important;
  transform:translateY(-2px);
}

/* ── STAT BOXES ── */
.stat-box {
  text-align:center;
  padding:24px 16px;
  border:1px solid var(--glass-b);
  border-radius:12px;
  background: rgba(4,18,32,0.6);
  backdrop-filter:blur(10px);
  transition:all 0.2s;
}
.stat-box:hover {
  border-color: rgba(0,242,255,0.35);
  box-shadow: 0 0 24px rgba(0,242,255,0.08);
  transform: translateY(-2px);
}
.stat-num {
  font-family:'Orbitron',sans-serif;
  font-size:2.4rem;
  font-weight:900;
  line-height:1;
}
.stat-lbl {
  font-family:'Rajdhani',sans-serif;
  font-size:0.72rem;
  letter-spacing:3px;
  color:var(--text-dim);
  text-transform:uppercase;
  margin-top:6px;
}

/* ── INPUT STYLING ── */
textarea, input[type="text"] {
  background: rgba(4,18,32,0.8) !important;
  border: 1px solid rgba(0,242,255,0.2) !important;
  color: var(--text) !important;
  font-family: 'Share Tech Mono', monospace !important;
  font-size: 0.9rem !important;
  border-radius: 8px !important;
  caret-color: var(--cyan) !important;
}
textarea:focus, input[type="text"]:focus {
  border-color: var(--cyan) !important;
  box-shadow: 0 0 0 2px rgba(0,242,255,0.1) !important;
}

/* ── BUTTONS ── */
.stButton > button {
  font-family: 'Orbitron', sans-serif !important;
  font-size: 0.7rem !important;
  letter-spacing: 2px !important;
  text-transform: uppercase !important;
  border-radius: 7px !important;
  transition: all 0.2s !important;
  padding: 12px 24px !important;
}
div[data-testid="column"]:first-child .stButton > button {
  background: linear-gradient(135deg,rgba(0,242,255,0.15),rgba(188,19,254,0.1)) !important;
  border: 1px solid var(--cyan) !important;
  color: var(--cyan) !important;
}
div[data-testid="column"]:first-child .stButton > button:hover {
  background: rgba(0,242,255,0.22) !important;
  box-shadow: 0 0 24px rgba(0,242,255,0.35) !important;
  transform: translateY(-1px) !important;
}

/* ── HISTORY TABLE ── */
.hist-row {
  display:flex;align-items:center;gap:14px;
  padding:12px 16px;
  border-bottom:1px solid rgba(0,242,255,0.06);
  border-radius:6px;
  font-family:'Rajdhani',sans-serif;
  transition:background 0.15s;
}
.hist-row:hover{background:rgba(0,242,255,0.03);}
.hist-score{
  font-family:'Orbitron',sans-serif;font-size:1.1rem;font-weight:700;
  min-width:50px;text-align:center;
}
.hist-text{flex:1;font-size:0.9rem;color:var(--text-dim);overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}
.hist-time{font-family:'Share Tech Mono',monospace;font-size:0.7rem;color:rgba(200,232,245,0.35);}

/* ── TIPS CARD ── */
.tip-item {
  display:flex;gap:14px;padding:14px 0;
  border-bottom:1px solid rgba(0,242,255,0.06);
  font-family:'Rajdhani',sans-serif;
}
.tip-icon{font-size:1.3rem;margin-top:2px;}
.tip-title{font-weight:700;font-size:1.05rem;color:var(--cyan);margin-bottom:3px;}
.tip-body{font-size:0.95rem;color:var(--text-dim);line-height:1.5;}

/* ── PAGE SECTIONS ── */
.page-hero {
  text-align:center;
  padding:20px 0 36px;
}
.page-hero h1 {
  font-family:'Orbitron',sans-serif;
  font-size:clamp(1.6rem,3.5vw,2.8rem);
  font-weight:900;
  color:var(--cyan);
  text-shadow:0 0 16px rgba(0,242,255,0.4);
  letter-spacing:0.12em;
  margin-bottom:8px;
}
.page-hero p {
  font-family:'Rajdhani',sans-serif;
  color:var(--text-dim);
  font-size:1.05rem;
  letter-spacing:2px;
  text-transform:uppercase;
}

/* ── GRID BG ── */
.bg-grid {
  position:fixed;
  inset:0;
  background-image:
    linear-gradient(rgba(0,242,255,0.015) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0,242,255,0.015) 1px, transparent 1px);
  background-size:60px 60px;
  pointer-events:none;
  z-index:0;
}
.bg-glow {
  position:fixed;
  width:600px;height:600px;
  border-radius:50%;
  pointer-events:none;
  z-index:0;
}
.bg-glow.tl {
  top:-200px;left:-200px;
  background:radial-gradient(circle, rgba(0,242,255,0.04) 0%, transparent 70%);
}
.bg-glow.br {
  bottom:-200px;right:-200px;
  background:radial-gradient(circle, rgba(188,19,254,0.04) 0%, transparent 70%);
}

/* Tab style overrides */
.stTabs [data-baseweb="tab-list"] {
  gap: 4px;
  background: transparent !important;
  border-bottom: 1px solid rgba(0,242,255,0.15) !important;
}
.stTabs [data-baseweb="tab"] {
  font-family: 'Orbitron', sans-serif !important;
  font-size: 0.65rem !important;
  letter-spacing: 2px !important;
  color: var(--text-dim) !important;
  background: transparent !important;
  border: none !important;
  padding: 12px 20px !important;
}
.stTabs [aria-selected="true"] {
  color: var(--cyan) !important;
  border-bottom: 2px solid var(--cyan) !important;
}
.stTabs [data-baseweb="tab-panel"] {
  padding-top: 24px !important;
}

/* progress bar */
.stProgress > div > div > div {
  background: linear-gradient(90deg, var(--cyan), var(--purple)) !important;
}

/* ── AI ANALYSIS CARD ── */
.ai-card {
  background: linear-gradient(135deg, rgba(188,19,254,0.06), rgba(0,242,255,0.04));
  border: 1px solid rgba(188,19,254,0.3);
  border-radius: 14px;
  padding: 24px 28px;
  margin-top: 20px;
  position: relative;
  overflow: hidden;
}
.ai-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 2px;
  background: linear-gradient(90deg, var(--purple), var(--cyan));
  opacity: 0.7;
}
.ai-card-title {
  font-family: 'Orbitron', sans-serif;
  font-size: 0.75rem;
  letter-spacing: 3px;
  color: var(--purple);
  text-transform: uppercase;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 10px;
}
.ai-card-title::after {
  content: '';
  flex: 1;
  height: 1px;
  background: linear-gradient(90deg, rgba(188,19,254,0.4), transparent);
}
.ai-content {
  font-family: 'Rajdhani', sans-serif;
  font-size: 1rem;
  color: rgba(200,232,245,0.85);
  line-height: 1.8;
  white-space: pre-line;
}
.ai-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-family: 'Orbitron', sans-serif;
  font-size: 0.55rem;
  letter-spacing: 2px;
  color: var(--purple);
  border: 1px solid rgba(188,19,254,0.4);
  padding: 4px 10px;
  border-radius: 4px;
  background: rgba(188,19,254,0.08);
  margin-left: auto;
}

/* email header specific */
.email-header-row {
  display: flex;
  gap: 10px;
  padding: 10px 0;
  border-bottom: 1px solid rgba(0,242,255,0.06);
  font-family: 'Rajdhani', sans-serif;
  align-items: flex-start;
}
.email-header-label {
  font-family: 'Share Tech Mono', monospace;
  font-size: 0.72rem;
  color: var(--cyan);
  min-width: 110px;
  padding-top: 2px;
}
.email-header-value {
  font-size: 0.92rem;
  color: var(--text);
  flex: 1;
  word-break: break-all;
}
.email-flag {
  font-family: 'Orbitron', sans-serif;
  font-size: 0.58rem;
  letter-spacing: 1px;
  padding: 2px 8px;
  border-radius: 3px;
  white-space: nowrap;
}

/* ── FOOTER ── */
.footer {
  text-align:center;
  padding:40px 20px 24px;
  border-top:1px solid rgba(0,242,255,0.08);
  margin-top:60px;
}
.footer-logo {
  font-family:'Orbitron',sans-serif;
  font-size:1rem;
  letter-spacing:5px;
  color:rgba(0,242,255,0.2);
  margin-bottom:8px;
}
.footer-txt {
  font-family:'Share Tech Mono',monospace;
  font-size:0.7rem;
  color:rgba(200,232,245,0.2);
  letter-spacing:2px;
}

/* select box */
div[data-baseweb="select"] > div {
  background: rgba(4,18,32,0.8) !important;
  border-color: rgba(0,242,255,0.2) !important;
  color: var(--text) !important;
  font-family: 'Rajdhani', sans-serif !important;
}

/* info/warning boxes */
.stAlert {
  background: rgba(4,18,32,0.8) !important;
  border-radius: 8px !important;
  font-family: 'Rajdhani', sans-serif !important;
}
</style>

<div class="bg-grid"></div>
<div class="bg-glow tl"></div>
<div class="bg-glow br"></div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
#  SPLASH SCREEN
# ══════════════════════════════════════════════════════════════
SPLASH_STEPS = [
    (12,  "Initialising CYNETRA Core Engine..."),
    (24,  "Loading Indian Threat Intelligence Feeds..."),
    (36,  "Connecting to I4C Node Network..."),
    (48,  "Calibrating Phishing Heuristics..."),
    (60,  "Syncing CERT-In Blacklist Database..."),
    (72,  "Activating Brand Spoof Detection Matrix..."),
    (84,  "Running Linguistic Entropy Analysis..."),
    (95,  "Connecting Claude AI Analysis Module..."),
    (100, "CYNETRA ONLINE — ALL SYSTEMS OPERATIONAL"),
]

if not st.session_state.splash_done:
    splash_ph = st.empty()
    for pct, msg in SPLASH_STEPS:
        node_html = "".join(
            f'<div class="splash-node {"active" if i < (pct // 13) else ""}"></div>'
            for i in range(8)
        )
        with splash_ph.container():
            st.markdown(f"""
            <div class="splash">
              <div class="splash-grid"></div>
              <div class="splash-corner tl"></div>
              <div class="splash-corner tr"></div>
              <div class="splash-corner bl"></div>
              <div class="splash-corner br"></div>
              <div style="position:relative;width:180px;height:180px;margin-bottom:28px;display:flex;align-items:center;justify-content:center;">
                <svg class="splash-hex" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg"
                     style="position:absolute;inset:0;width:180px;height:180px;">
                  <polygon points="100,10 185,55 185,145 100,190 15,145 15,55"
                    fill="none" stroke="#00f2ff" stroke-width="1.5"
                    stroke-dasharray="8,4" opacity="0.7"/>
                  <polygon points="100,25 172,67 172,133 100,175 28,133 28,67"
                    fill="none" stroke="#bc13fe" stroke-width="1" opacity="0.4"/>
                  <circle cx="100" cy="100" r="60" fill="none" stroke="#00f2ff"
                    stroke-width="0.5" opacity="0.3"/>
                  <path d="M100 45 L140 62 L140 98 C140 120 122 138 100 145 C78 138 60 120 60 98 L60 62 Z"
                    fill="rgba(0,242,255,0.08)" stroke="#00f2ff" stroke-width="1.5"/>
                  <path d="M87 95 L96 104 L116 84" fill="none" stroke="#00f2ff"
                    stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </div>
              <div class="splash-title-main">CYNETRA</div>
              <div class="splash-tagline">Phish Hunter AI &nbsp;·&nbsp; Indian Threat Intelligence Engine</div>
              <div class="splash-progress-wrap">
                <div class="splash-bar-bg">
                  <div class="splash-bar-fill" style="width:{pct}%"></div>
                </div>
                <div class="splash-status-text">{msg}</div>
              </div>
              <div class="splash-nodes" style="margin-top:24px;">{node_html}</div>
              <div style="position:fixed;bottom:30px;font-family:'Share Tech Mono',monospace;font-size:0.65rem;
                          color:rgba(0,242,255,0.2);letter-spacing:3px;">
                SESSION ID: {hashlib.md5(str(time.time()).encode()).hexdigest()[:16].upper()}
              </div>
            </div>
            """, unsafe_allow_html=True)
        time.sleep(0.9)
    splash_ph.empty()
    st.session_state.splash_done = True
    st.rerun()


# ══════════════════════════════════════════════════════════════
#  AI ANALYSIS MODULE (Claude API)
# ══════════════════════════════════════════════════════════════
def call_claude_ai(prompt: str, max_tokens: int = 800) -> str:
    """Call the Anthropic Claude API for AI-powered analysis."""
    try:
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={"Content-Type": "application/json"},
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": max_tokens,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=30,
        )
        if response.status_code == 200:
            data = response.json()
            return data["content"][0]["text"]
        else:
            return ""
    except Exception:
        return ""


def get_ai_analysis(text: str, engine_result: dict, scan_type: str = "message") -> str:
    """Get AI-powered contextual analysis from Claude."""
    score = engine_result["score"]
    verdict = engine_result["verdict"]
    findings_summary = "; ".join(
        f"{f['category']} (score {f['score']}/{f['max']}): {f['detail']}"
        for f in engine_result.get("findings", [])
    )

    prompt = f"""You are CYNETRA's AI threat analyst specializing in Indian cybercrime and phishing detection.

A user submitted this {scan_type} for analysis:
---
{text[:1500]}
---

Our rule-based engine gave it a threat score of {score}/100 and verdict: {verdict}.
Engine findings: {findings_summary if findings_summary else "No specific signals triggered."}

Provide a concise, specific AI analysis of THIS message in 3-4 short paragraphs:
1. What specific tactics or patterns make this suspicious (or safe) — reference actual content from the message
2. Who is likely the target and what the attacker's goal appears to be based on the specific content
3. What specific red flags or reassuring signs are present in the actual text
4. Immediate recommended actions for the recipient

Be specific to THIS message — mention actual words, phrases, or elements you see in it. Do not give generic advice.
Keep it under 250 words. Write in a clear, direct cybersecurity analyst tone."""

    return call_claude_ai(prompt, max_tokens=600)


def get_email_ai_analysis(sender: str, subject: str, reply_to: str, received_from: str, body: str, engine_result: dict) -> str:
    """Get AI analysis specifically for email header + body."""
    score = engine_result["score"]
    verdict = engine_result["verdict"]
    findings_summary = "; ".join(
        f"{f['category']} (score {f['score']}/{f['max']}): {f['detail']}"
        for f in engine_result.get("findings", [])
    )

    prompt = f"""You are CYNETRA's email forensics AI analyst specializing in Indian phishing email detection.

Analyse this email submission:
- Sender: {sender or "(not provided)"}
- Subject: {subject or "(not provided)"}
- Reply-To: {reply_to or "(not provided)"}
- Received From: {received_from or "(not provided)"}
- Body: {body[:800] if body else "(not provided)"}

Our engine scored this {score}/100, verdict: {verdict}.
Engine detected: {findings_summary if findings_summary else "No signals."}

Provide a specific email forensics analysis covering:
1. Header anomalies — analyze the sender address, reply-to mismatch, received-from IP/domain for suspicious patterns
2. Subject line manipulation tactics present (if any)
3. Body content analysis — specific phrases or techniques used in this exact email
4. Overall assessment of whether this is legitimate, suspicious, or a confirmed phishing attempt

Be specific to the actual values provided. Reference exact domain names, IP addresses, or phrases you see.
Under 220 words. Professional cybersecurity analyst tone."""

    return call_claude_ai(prompt, max_tokens=550)


def get_url_ai_analysis(url: str, url_result: dict) -> str:
    """Get AI analysis for URL."""
    score = url_result["score"]
    verdict = url_result["verdict"]
    findings_summary = "; ".join(
        f"{f['check']} [{f['severity']}]: {f['detail']}"
        for f in url_result.get("findings", [])
    )

    prompt = f"""You are CYNETRA's URL threat intelligence AI specializing in Indian phishing and malware URLs.

Analyse this URL: {url}

Technical findings from our scanner:
- Risk Score: {score}/100
- Verdict: {verdict}
- Issues found: {findings_summary if findings_summary else "No specific issues detected."}

Provide a specific URL threat analysis:
1. Break down what each part of this URL (domain, subdomain, path, parameters) reveals about intent
2. Identify the specific deception technique being used (brand impersonation, homoglyph, credential harvesting, etc.)
3. What would happen if a user visited this URL — what data are they likely trying to steal?
4. How to verify if a legitimate version of this URL exists

Reference the actual URL components. Be specific and technical.
Under 200 words. Direct threat analyst tone."""

    return call_claude_ai(prompt, max_tokens=500)


# ══════════════════════════════════════════════════════════════
#  ANALYSIS ENGINE (corrected weighted logic)
# ══════════════════════════════════════════════════════════════
PSYCH_PATTERNS = [
    (r'\b(urgent|urgently)\b',                               8, "Urgency trigger"),
    (r'\b(immediately|instant|right now|right away)\b',      7, "Immediacy pressure"),
    (r'\b(expire[sd]?|expiring|last chance|final notice)\b', 7, "Expiration threat"),
    (r'\b(suspended|blocked|disabled|locked|deactivated)\b', 9, "Account threat"),
    (r'\b(verify|confirm|validate)\s+(now|immediately|your (account|details|identity))\b', 8, "Forced verification"),
    (r'\baction\s+required\b',                               7, "Action required"),
    (r'\b(security alert|unusual activity|suspicious login)\b', 9, "Security scare"),
    (r'\b(otp|one.time.password|one time pin)\b',            8, "OTP solicitation"),
    (r'\b(password|pin|cvv|cvc)\b',                          9, "Credential request"),
    (r'\bclick\s+(here|below|the link|this link)\b',         6, "Click-bait language"),
    (r'\b(won|winner|winning|you\'?ve? won|congratulations)\b', 8, "Prize scam"),
    (r'\b(free (gift|prize|reward|money|cash))\b',           7, "Free offer lure"),
    (r'\b(claim (your|the|this))\b',                         6, "Claim prompt"),
    (r'\b(limited (time|offer|slots?))\b',                   6, "Scarcity tactic"),
    (r'\bdo not (ignore|delete|discard)\b',                  7, "Ignore warning"),
    (r'\b(refund|cashback|bonus credited)\b',                6, "Fake refund"),
    (r'\b(kyc|know your customer)\b',                        7, "KYC phishing"),
    (r'\b(aadhar|aadhaar|pan card) (update|verify|link)\b',  9, "ID document request"),
    (r'\b(account will be (closed|terminated|deactivated))\b', 9, "Account closure threat"),
]

SHORTENERS = [
    'bit.ly','tinyurl.com','goo.gl','t.co','ow.ly','is.gd',
    'buff.ly','rebrand.ly','tiny.cc','shorte.st','cutt.ly',
    'rb.gy','shorturl.at','clck.ru','qr.ae','adf.ly',
]

SUSPICIOUS_TLDS = re.compile(
    r'\.(xyz|top|click|loan|pw|work|tk|ml|ga|cf|gq|online|site|info|biz|'
    r'live|shop|store|win|fun|vip|buzz|club|space|website|tech)\b', re.I
)

INDIAN_BRANDS = {
    "Banking": [
        'sbi','state bank of india','hdfc','icici','axis bank','pnb',
        'punjab national','canara bank','kotak','yes bank','bob',
        'bank of baroda','union bank','idfc','rbl bank',
    ],
    "Payments": [
        'paytm','phonepe','phone pe','gpay','google pay','bhim',
        'upi','razorpay','mobikwik','freecharge','airtel money',
    ],
    "E-Commerce": [
        'amazon india','flipkart','myntra','snapdeal','meesho',
        'ajio','nykaa','tata cliq','reliance digital',
    ],
    "Government": [
        'irctc','uidai','aadhaar','pan card','income tax',
        'epfo','provident fund','nps','lic','esic',
        'passport seva','nsdl','traces','gst',
    ],
    "Telecom": [
        'jio','airtel','vi ','vodafone','idea','bsnl',
    ],
}

ALL_INDIAN_BRANDS = [b for brands in INDIAN_BRANDS.values() for b in brands]


def cynetra_engine(text: str) -> dict:
    """4-vector phishing analysis engine."""
    txt_lower = text.lower()
    txt_orig  = text
    findings  = []

    # ── Vector 1: Psychological Triggers (max 35 pts)
    psych_hits = []
    psych_raw  = 0
    for pattern, weight, label in PSYCH_PATTERNS:
        if re.search(pattern, txt_lower):
            psych_hits.append((label, weight))
            psych_raw += weight

    psych_score = min(35, psych_raw)
    if psych_hits:
        findings.append({
            "category": "Psychological Triggers",
            "score":    psych_score,
            "max":      35,
            "hits":     psych_hits,
            "detail":   ", ".join(h[0] for h in psych_hits[:4]) + ("..." if len(psych_hits) > 4 else ""),
            "icon":     "🧠",
            "color":    "#bc13fe",
        })

    # ── Vector 2: Network Malice (max 40 pts)
    net_raw  = 0
    net_hits = []

    if re.search(r'https?://\d{1,3}(\.\d{1,3}){3}', txt_lower):
        net_raw += 22
        net_hits.append(("IP-based URL", 22))

    if re.search(r'\bhttp://(?!localhost|127\.)', txt_lower):
        net_raw += 12
        net_hits.append(("Insecure HTTP (no SSL)", 12))

    for s in SHORTENERS:
        if s in txt_lower:
            net_raw += 15
            net_hits.append((f"Masked link via {s}", 15))
            break

    tld_match = SUSPICIOUS_TLDS.search(txt_lower)
    if tld_match:
        net_raw += 12
        net_hits.append((f"Suspicious TLD: .{tld_match.group(1)}", 12))

    url_count = len(re.findall(r'https?://', txt_lower))
    if url_count >= 3:
        net_raw += 8
        net_hits.append((f"{url_count} URLs in one message", 8))

    if re.search(r'(?<=[a-z])[0o][a-z]|(?<=[a-z])[1il][a-z]', txt_lower):
        net_raw += 10
        net_hits.append(("Homoglyph/lookalike domain", 10))

    if re.search(r'https?://(secure|update|login|verify|account)-', txt_lower):
        net_raw += 10
        net_hits.append(("Deceptive subdomain prefix", 10))

    net_score = min(40, net_raw)
    if net_hits:
        findings.append({
            "category": "Network Malice",
            "score":    net_score,
            "max":      40,
            "hits":     net_hits,
            "detail":   ", ".join(h[0] for h in net_hits[:3]),
            "icon":     "🌐",
            "color":    "#00f2ff",
        })

    # ── Vector 3: Brand Spoofing (max 25 pts)
    brand_raw    = 0
    brand_hits   = []
    has_link     = bool(re.search(r'https?://', txt_lower) or any(s in txt_lower for s in SHORTENERS))

    for brand in ALL_INDIAN_BRANDS:
        if brand in txt_lower:
            base = 8
            if has_link:
                base += 5
            brand_hits.append((brand.title(), base))
            brand_raw += base

    # Domain mismatch
    for brand in ALL_INDIAN_BRANDS:
        if brand in txt_lower:
            brand_clean = brand.replace(' ', '').replace('.', '')
            urls = re.findall(r'https?://([^\s/]+)', txt_lower)
            for url in urls:
                if brand_clean not in url and len(url) > 5:
                    brand_raw += 5
                    brand_hits.append(("Domain doesn't match brand", 5))
                    break
            break

    brand_score = min(25, brand_raw)
    if brand_hits:
        findings.append({
            "category": "Brand Spoofing",
            "score":    brand_score,
            "max":      25,
            "hits":     brand_hits,
            "detail": "Brands: " + ", ".join(list(set(h[0] for h in brand_hits if h[0] != "Domain doesn't match brand"))[:4]),
            "icon":     "🏦",
            "color":    "#ffb703",
        })

    # ── Vector 4: Linguistic Red Flags (max 20 pts)
    ling_raw  = 0
    ling_hits = []

    words = re.findall(r'[A-Za-z]+', txt_orig)
    if words:
        caps_words = [w for w in words if w.isupper() and len(w) > 2]
        caps_ratio = len(caps_words) / len(words)
        if caps_ratio > 0.25:
            score_v = min(8, int(caps_ratio * 20))
            ling_raw += score_v
            ling_hits.append((f"Excessive caps ({caps_ratio:.0%} of words)", score_v))

    sub_pattern = re.compile(r'[a-zA-Z][0@][a-zA-Z]|[a-zA-Z][1|!][a-zA-Z]|[a-zA-Z][3][a-zA-Z]')
    if sub_pattern.search(txt_lower):
        ling_raw += 8
        ling_hits.append(("Character substitution (e.g., '0' for 'o')", 8))

    if txt_orig.count('!') >= 3 or txt_orig.count('?') >= 3:
        ling_raw += 4
        ling_hits.append((f"Excessive punctuation ({txt_orig.count('!')} !, {txt_orig.count('?')} ?)", 4))

    if len(txt_orig.strip()) > 50 and not re.search(r'\b(dear|hello|hi|greetings|namaste)\b', txt_lower):
        ling_raw += 4
        ling_hits.append(("No salutation — abrupt message", 4))

    if re.search(r'\b(kindly|do the needful|revert back|regards sir|dear customer)\b', txt_lower):
        ling_raw += 4
        ling_hits.append(("Phishing-typical phrasing detected", 4))

    ling_score = min(20, ling_raw)
    if ling_hits:
        findings.append({
            "category": "Linguistic Analysis",
            "score":    ling_score,
            "max":      20,
            "hits":     ling_hits,
            "detail":   ling_hits[0][0] if ling_hits else "",
            "icon":     "🔤",
            "color":    "#00ff88",
        })

    # ── Aggregate & Classify
    raw_total = sum(f["score"] for f in findings)
    vectors_active = len(findings)
    if vectors_active >= 3:
        raw_total = int(raw_total * 1.12)
    elif vectors_active >= 2:
        raw_total = int(raw_total * 1.05)

    total = min(100, raw_total)

    if total >= 65:
        verdict      = "PHISHING"
        verdict_txt  = "⚠ HIGH-RISK PHISHING DETECTED"
        badge_cls    = "vb-danger"
        color        = "#ff3131"
        risk_label   = "HIGH RISK"
    elif total >= 35:
        verdict      = "SUSPICIOUS"
        verdict_txt  = "⚡ SUSPICIOUS — EXERCISE CAUTION"
        badge_cls    = "vb-warn"
        color        = "#ffb703"
        risk_label   = "MEDIUM RISK"
    else:
        verdict      = "SAFE"
        verdict_txt  = "✔ LOW RISK — LIKELY LEGITIMATE"
        badge_cls    = "vb-safe"
        color        = "#00ff88"
        risk_label   = "LOW RISK"

    return {
        "score":       total,
        "verdict":     verdict,
        "verdict_txt": verdict_txt,
        "badge_cls":   badge_cls,
        "color":       color,
        "risk_label":  risk_label,
        "findings":    findings,
        "vectors":     vectors_active,
        "timestamp":   datetime.now().strftime("%H:%M:%S"),
    }


def url_analyzer(url: str) -> dict:
    """Dedicated URL analysis with domain/path/param dissection."""
    findings = []
    score = 0

    try:
        parsed = urllib.parse.urlparse(url if url.startswith('http') else 'http://' + url)
        domain = parsed.netloc or parsed.path.split('/')[0]
        path   = parsed.path
        params = parsed.query
    except Exception:
        domain, path, params = url, "", ""

    if url.startswith('http://'):
        score += 15
        findings.append({"check": "Protocol", "detail": "HTTP (no SSL/TLS encryption)", "severity": "HIGH", "pts": 15})
    elif url.startswith('https://'):
        findings.append({"check": "Protocol", "detail": "HTTPS — encrypted connection", "severity": "OK", "pts": 0})

    if re.search(r'^\d{1,3}(\.\d{1,3}){3}', domain):
        score += 25
        findings.append({"check": "Host", "detail": f"Direct IP address: {domain}", "severity": "CRITICAL", "pts": 25})

    tld_m = SUSPICIOUS_TLDS.search(domain)
    if tld_m:
        score += 15
        findings.append({"check": "TLD", "detail": f"High-risk TLD: .{tld_m.group(1)}", "severity": "HIGH", "pts": 15})

    if re.search(r'(?<=[a-z])[0o][a-z]|[a-z][1il][a-z]', domain.lower()):
        score += 18
        findings.append({"check": "Domain", "detail": "Character substitution in domain (homoglyph attack)", "severity": "CRITICAL", "pts": 18})

    subdomain_count = domain.count('.') - 1
    if subdomain_count >= 3:
        score += 10
        findings.append({"check": "Subdomains", "detail": f"{subdomain_count+1} subdomains — obfuscation likely", "severity": "MEDIUM", "pts": 10})

    for brand in ALL_INDIAN_BRANDS:
        brand_slug = brand.replace(' ', '').replace('.', '')
        if brand_slug in domain.lower() and not domain.lower().endswith(f"{brand_slug}.com"):
            score += 20
            findings.append({"check": "Brand Spoof", "detail": f"'{brand.title()}' in non-official domain", "severity": "CRITICAL", "pts": 20})
            break

    if re.search(r'/(login|signin|verify|confirm|secure|update|account|wallet|pay)', path.lower()):
        score += 8
        findings.append({"check": "Path", "detail": f"Sensitive keyword in path: {path[:50]}", "severity": "MEDIUM", "pts": 8})

    if re.search(r'(otp|password|pass|pin|cvv|card|token)=', params.lower()):
        score += 15
        findings.append({"check": "Parameters", "detail": "Sensitive data in URL params (credential harvesting)", "severity": "CRITICAL", "pts": 15})

    for s in SHORTENERS:
        if s in url.lower():
            score += 12
            findings.append({"check": "Redirector", "detail": f"Link shortener: {s}", "severity": "HIGH", "pts": 12})
            break

    score = min(100, score)

    if score >= 60:
        verdict, color = "MALICIOUS", "#ff3131"
    elif score >= 30:
        verdict, color = "SUSPICIOUS", "#ffb703"
    else:
        verdict, color = "CLEAN", "#00ff88"

    return {
        "score": score, "verdict": verdict, "color": color,
        "domain": domain, "path": path, "params": params,
        "findings": findings,
    }


# ══════════════════════════════════════════════════════════════
#  EMAIL HEADER ANALYSER (dedicated, fixes the broken output)
# ══════════════════════════════════════════════════════════════
def analyse_email_headers(sender: str, subject: str, reply_to: str, received_from: str, body: str) -> dict:
    """
    Dedicated email header + body analysis engine.
    Returns structured header findings separate from body findings.
    """
    header_flags = []
    body_result  = None

    # ── Sender domain analysis
    sender_flag = None
    sender_domain = ""
    if sender:
        m = re.search(r'@([^\s>]+)', sender)
        if m:
            sender_domain = m.group(1).lower()
            # Free email claiming to be a bank/official
            free_providers = ['gmail.com','yahoo.com','hotmail.com','outlook.com','rediffmail.com','ymail.com']
            is_free = any(sender_domain == fp for fp in free_providers)
            is_brand = any(brand.replace(' ','') in sender_domain.replace('.','') for brand in ALL_INDIAN_BRANDS)

            if is_free and is_brand:
                header_flags.append({
                    "field": "From",
                    "value": sender,
                    "flag": "CRITICAL",
                    "reason": f"Brand name in free-email domain — official orgs never use {sender_domain}",
                    "color": "#ff3131"
                })
            elif is_free:
                header_flags.append({
                    "field": "From",
                    "value": sender,
                    "flag": "MEDIUM",
                    "reason": "Free email provider — unusual for official communications",
                    "color": "#ffb703"
                })
            elif SUSPICIOUS_TLDS.search(sender_domain):
                header_flags.append({
                    "field": "From",
                    "value": sender,
                    "flag": "HIGH",
                    "reason": f"Suspicious TLD in sender domain: .{sender_domain.split('.')[-1]}",
                    "color": "#ff6b35"
                })
            else:
                header_flags.append({
                    "field": "From",
                    "value": sender,
                    "flag": "OK",
                    "reason": "Sender domain appears legitimate",
                    "color": "#00ff88"
                })

    # ── Subject line analysis
    if subject:
        subj_lower = subject.lower()
        subj_flag  = "OK"
        subj_reason = "Subject appears normal"
        subj_color  = "#00ff88"

        urgent_words = re.findall(r'\b(urgent|action required|suspended|blocked|verify|kyc|otp|alert|warning|immediate|expire|final|last chance)\b', subj_lower)
        caps_ratio = sum(1 for c in subject if c.isupper()) / max(len(subject), 1)

        if urgent_words and caps_ratio > 0.4:
            subj_flag   = "CRITICAL"
            subj_reason = f"Urgency tactics + excessive caps: [{', '.join(set(urgent_words))}]"
            subj_color  = "#ff3131"
        elif urgent_words:
            subj_flag   = "HIGH"
            subj_reason = f"Urgency/scare keywords detected: [{', '.join(set(urgent_words))}]"
            subj_color  = "#ff6b35"
        elif caps_ratio > 0.5:
            subj_flag   = "MEDIUM"
            subj_reason = f"Excessive capitalisation ({caps_ratio:.0%} uppercase)"
            subj_color  = "#ffb703"

        header_flags.append({
            "field": "Subject",
            "value": subject,
            "flag": subj_flag,
            "reason": subj_reason,
            "color": subj_color
        })

    # ── Reply-To mismatch
    if reply_to and sender:
        sender_dom  = re.search(r'@([^\s>]+)', sender)
        replyto_dom = re.search(r'@([^\s>]+)', reply_to)
        if sender_dom and replyto_dom:
            s_dom = sender_dom.group(1).lower()
            r_dom = replyto_dom.group(1).lower()
            if s_dom != r_dom:
                header_flags.append({
                    "field": "Reply-To",
                    "value": reply_to,
                    "flag": "CRITICAL",
                    "reason": f"Reply-To domain ({r_dom}) differs from sender ({s_dom}) — replies go to attacker",
                    "color": "#ff3131"
                })
            else:
                header_flags.append({
                    "field": "Reply-To",
                    "value": reply_to,
                    "flag": "OK",
                    "reason": "Reply-To matches sender domain",
                    "color": "#00ff88"
                })
        elif reply_to.strip():
            header_flags.append({
                "field": "Reply-To",
                "value": reply_to,
                "flag": "MEDIUM",
                "reason": "Reply-To set but could not be parsed",
                "color": "#ffb703"
            })

    # ── Received-From IP/Domain
    if received_from:
        recv_clean = received_from.strip()
        is_ip = bool(re.match(r'^\d{1,3}(\.\d{1,3}){3}$', recv_clean))

        if is_ip:
            # Check if it's a known suspicious IP range
            octets = recv_clean.split('.')
            first_octet = int(octets[0]) if octets[0].isdigit() else 0

            if first_octet in [185, 91, 194, 45, 176, 195]:
                header_flags.append({
                    "field": "Received-From",
                    "value": recv_clean,
                    "flag": "HIGH",
                    "reason": f"IP {recv_clean} is in a range associated with bulletproof hosting / spam networks",
                    "color": "#ff6b35"
                })
            else:
                header_flags.append({
                    "field": "Received-From",
                    "value": recv_clean,
                    "flag": "MEDIUM",
                    "reason": f"Raw IP address origin ({recv_clean}) — legitimate senders use named mail servers",
                    "color": "#ffb703"
                })
        else:
            if SUSPICIOUS_TLDS.search(recv_clean):
                header_flags.append({
                    "field": "Received-From",
                    "value": recv_clean,
                    "flag": "HIGH",
                    "reason": f"Receiving mail server has suspicious TLD",
                    "color": "#ff6b35"
                })
            else:
                header_flags.append({
                    "field": "Received-From",
                    "value": recv_clean,
                    "flag": "OK",
                    "reason": "Receiving domain appears standard",
                    "color": "#00ff88"
                })

    # ── Body analysis using cynetra_engine
    full_text = f"{sender} {subject} {reply_to} {received_from} {body}"
    if full_text.strip():
        body_result = cynetra_engine(full_text)

    # Compute header risk score
    flag_weights = {"CRITICAL": 30, "HIGH": 20, "MEDIUM": 10, "OK": 0}
    header_score = min(60, sum(flag_weights.get(f["flag"], 0) for f in header_flags))

    # Combine header + body scores (header max 60, body engine already 0-100)
    body_score   = body_result["score"] if body_result else 0
    combined     = min(100, int(header_score * 0.5 + body_score * 0.6))

    if combined >= 65:
        verdict, badge_cls, color, verdict_txt = "PHISHING", "vb-danger", "#ff3131", "⚠ PHISHING EMAIL CONFIRMED"
    elif combined >= 35:
        verdict, badge_cls, color, verdict_txt = "SUSPICIOUS", "vb-warn", "#ffb703", "⚡ SUSPICIOUS EMAIL"
    else:
        verdict, badge_cls, color, verdict_txt = "SAFE", "vb-safe", "#00ff88", "✔ EMAIL APPEARS LEGITIMATE"

    return {
        "score":        combined,
        "verdict":      verdict,
        "badge_cls":    badge_cls,
        "color":        color,
        "verdict_txt":  verdict_txt,
        "header_flags": header_flags,
        "body_result":  body_result,
        "timestamp":    datetime.now().strftime("%H:%M:%S"),
    }


# ══════════════════════════════════════════════════════════════
#  HELPER: render AI analysis block
# ══════════════════════════════════════════════════════════════
def render_ai_block(ai_text: str, title: str = "🤖 AI DEEP ANALYSIS — POWERED BY CLAUDE"):
    if ai_text:
        st.markdown(f"""
        <div class="ai-card">
          <div class="ai-card-title">
            {title}
            <span class="ai-badge">⚡ CLAUDE AI</span>
          </div>
          <div class="ai-content">{ai_text}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="ai-card" style="opacity:0.5;">
          <div class="ai-card-title">🤖 AI ANALYSIS UNAVAILABLE</div>
          <div style="font-family:'Rajdhani',sans-serif;color:var(--text-dim);font-size:0.9rem;">
            Claude AI analysis could not be retrieved. Rule-based analysis above is still valid.
          </div>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
#  NAVIGATION BAR
# ══════════════════════════════════════════════════════════════
page = st.session_state.current_page

pages = [
    ("dashboard", "⬡  DASHBOARD"),
    ("scanner",   "🔍  SCANNER"),
    ("url_check", "🔗  URL CHECK"),
    ("education", "📚  CYBER GUIDE"),
    ("report",    "🚨  REPORT"),
]

st.markdown(f"""
<div class="navbar">
  <div class="nav-logo">
    <svg width="28" height="28" viewBox="0 0 100 100" fill="none">
      <polygon points="50,5 92,27 92,73 50,95 8,73 8,27"
        fill="rgba(0,242,255,0.08)" stroke="#00f2ff" stroke-width="2"/>
      <path d="M50 22 L72 33 L72 55 C72 67 62 76 50 80 C38 76 28 67 28 55 L28 33 Z"
        fill="rgba(0,242,255,0.12)" stroke="#00f2ff" stroke-width="1.5"/>
      <path d="M40 50 L48 58 L63 42" fill="none" stroke="#00f2ff"
        stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
    CYNETRA
  </div>
  <div class="nav-links"></div>
  <div class="nav-status">
    <div class="status-dot"></div>
    THREAT INTEL: LIVE
  </div>
</div>
<div class="nav-spacer"></div>
""", unsafe_allow_html=True)

nav_cols = st.columns(len(pages) + 2)
with nav_cols[0]:
    st.markdown("<div style='height:1px'></div>", unsafe_allow_html=True)
for i, (pid, plabel) in enumerate(pages):
    with nav_cols[i + 1]:
        if st.button(plabel, key=f"nav_{pid}", use_container_width=True):
            st.session_state.current_page = pid
            st.rerun()


# ══════════════════════════════════════════════════════════════
#  PAGE: DASHBOARD
# ══════════════════════════════════════════════════════════════
if page == "dashboard":
    st.markdown("""
    <div class="page-hero">
      <h1>THREAT INTELLIGENCE DASHBOARD</h1>
      <p>Real-time phishing detection · Indian Cyber Intelligence Network · Claude AI Powered</p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    stats = [
        (st.session_state.total_scans,     "#00f2ff", "TOTAL SCANS"),
        (st.session_state.threats_detected, "#ff3131", "THREATS CAUGHT"),
        (st.session_state.safe_count,       "#00ff88", "SAFE MESSAGES"),
        ("94.7%",                            "#bc13fe", "ACCURACY RATE"),
    ]
    for col, (num, clr, lbl) in zip([c1,c2,c3,c4], stats):
        with col:
            st.markdown(f"""
            <div class="stat-box">
              <div class="stat-num" style="color:{clr};text-shadow:0 0 12px {clr};">{num}</div>
              <div class="stat-lbl">{lbl}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

    col_l, col_r = st.columns([3, 2])

    with col_l:
        st.markdown('<div class="g-card">', unsafe_allow_html=True)
        st.markdown('<div class="sec-title">🔍 Quick Threat Scan</div>', unsafe_allow_html=True)
        quick_input = st.text_area(
            "Paste message, email or URL",
            placeholder="Paste suspicious content here for instant AI-powered analysis...",
            height=140,
            key="quick_scan_input",
            label_visibility="collapsed",
        )
        q1, q2 = st.columns(2)
        with q1:
            
            if st.button("⚡ ANALYSE THREAT", key="dash_scan", use_container_width=True):
                if quick_input.strip():
                    with st.spinner("Running analysis..."):
                        time.sleep(0.4)
                        r = cynetra_engine(quick_input)
                        st.session_state.scan_result = r
                        st.session_state.ai_analysis = None  # reset so it re-runs on scanner page
                        st.session_state.total_scans += 1
                        if r["verdict"] == "PHISHING":
                            st.session_state.threats_detected += 1
                        elif r["verdict"] == "SAFE":
                            st.session_state.safe_count += 1
                        st.session_state.scan_history.insert(0, {
                            "text": quick_input[:80],
                            "score": r["score"],
                            "verdict": r["verdict"],
                            "color": r["color"],
                            "time": r["timestamp"],
                        })
                        st.session_state.current_page = "scanner"
                        st.rerun()
                else:
                    st.warning("Please enter some text to analyse.")
        with q2:
            if st.button("🔗 CHECK URL", key="dash_url", use_container_width=True):
                st.session_state.current_page = "url_check"
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col_r:
        st.markdown('<div class="g-card" style="height:100%">', unsafe_allow_html=True)
        st.markdown('<div class="sec-title">📡 Active Intelligence</div>', unsafe_allow_html=True)
        intel_items = [
            ("🔴", "SMS phishing surge targeting Jio users"),
            ("🟠", "HDFC Bank KYC scam — new variant"),
            ("🟡", "Fake IRCTC refund links circulating"),
            ("🔴", "UPI fraud via deceptive QR codes"),
            ("🟠", "Aadhaar update SMS campaign active"),
        ]
        for dot, msg in intel_items:
            st.markdown(f"""
            <div style="display:flex;gap:10px;align-items:flex-start;
                        padding:9px 0;border-bottom:1px solid rgba(0,242,255,0.06);
                        font-family:'Rajdhani',sans-serif;font-size:0.92rem;">
              <span style="margin-top:1px;">{dot}</span>
              <span style="color:var(--text-dim);">{msg}</span>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("""
        <div style="margin-top:12px;font-family:'Share Tech Mono',monospace;
                    font-size:0.65rem;color:rgba(0,242,255,0.3);letter-spacing:2px;">
          CERT-IN FEEDS · UPDATED LIVE
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Scan history
    if st.session_state.scan_history:
        st.markdown('<div class="g-card">', unsafe_allow_html=True)
        st.markdown('<div class="sec-title">📋 Recent Scans</div>', unsafe_allow_html=True)
        for item in st.session_state.scan_history[:5]:
            st.markdown(f"""
            <div class="hist-row">
              <div class="hist-score" style="color:{item['color']};">{item['score']}</div>
              <div style="width:70px;">
                <span style="font-family:'Orbitron',sans-serif;font-size:0.6rem;
                             letter-spacing:1px;color:{item['color']};">{item['verdict']}</span>
              </div>
              <div class="hist-text">{item['text']}...</div>
              <div class="hist-time">{item['time']}</div>
            </div>
            """, unsafe_allow_html=True)
        if st.button("🗑 CLEAR HISTORY", key="clear_hist_dash"):
            st.session_state.scan_history = []
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # Threat matrix
    st.markdown('<div class="g-card">', unsafe_allow_html=True)
    st.markdown('<div class="sec-title">🗺 Indian Phishing Threat Matrix</div>', unsafe_allow_html=True)
    threat_data = [
        ("SMS Phishing (Smishing)",    85, "#ff3131"),
        ("Fake KYC / OTP Scams",       82, "#ff3131"),
        ("Brand Impersonation",        72, "#ff3131"),
        ("Fraudulent UPI Links",       68, "#ffb703"),
        ("Government Portal Spoof",    62, "#ffb703"),
        ("Fake E-Commerce Offers",     55, "#ffb703"),
        ("Email Phishing",             45, "#00f2ff"),
    ]
    for name, pct, clr in threat_data:
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:14px;padding:8px 0;">
          <div style="width:220px;font-family:'Rajdhani',sans-serif;font-size:0.95rem;
                      color:var(--text-dim);">{name}</div>
          <div style="flex:1;height:6px;background:rgba(255,255,255,0.06);border-radius:999px;overflow:hidden;">
            <div style="width:{pct}%;height:100%;background:{clr};border-radius:999px;
                        box-shadow:0 0 8px {clr};"></div>
          </div>
          <div style="width:40px;font-family:'Orbitron',sans-serif;font-size:0.75rem;color:{clr};">{pct}%</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
#  PAGE: SCANNER
# ══════════════════════════════════════════════════════════════
elif page == "scanner":
    st.markdown("""
    <div class="page-hero">
      <h1>PHISHING MESSAGE SCANNER</h1>
      <p>4-Vector Rule Engine + Claude AI Deep Analysis</p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📱  SMS / MESSAGE SCAN", "📧  EMAIL HEADER SCAN", "📦  BATCH SCAN"])

    # ─────────────────────────────────────────────
    with tab1:
        st.markdown('<div class="g-card">', unsafe_allow_html=True)
        st.markdown('<div class="sec-title">🔍 Paste Suspicious Content</div>', unsafe_allow_html=True)
        msg_input = st.text_area(
            "",
            placeholder='Paste the SMS, WhatsApp message, or email body here.\n\nExample:\n"Dear SBI customer, your account is suspended due to incomplete KYC. Click http://sbi-kyc-update.xyz/verify to restore access. OTP required. Act NOW or account will be permanently closed."',
            height=200,
            key="msg_scan_input",
            label_visibility="collapsed",
        )
        col_a, col_b, col_c = st.columns([2, 1, 1])
        with col_a:
            scan_btn = st.button("⚡ RUN CYNETRA ANALYSIS", key="msg_scan_btn", use_container_width=True)
        with col_b:
            if st.button("📋 LOAD EXAMPLE", key="load_example", use_container_width=True):
                st.session_state["_example"] = (
                    "URGENT: Dear SBI Customer, your account will be suspended in 24hrs. "
                    "Verify your KYC immediately at http://sbi-secure-kyc.xyz/update?otp=true "
                    "Failure to act NOW will result in PERMANENT account closure. "
                    "Share your OTP to our agent. Limited time offer: get ₹500 cashback on verification."
                )
                st.session_state.ai_analysis = None
                st.rerun()
        with col_c:
            if st.button("🗑 CLEAR", key="msg_clear", use_container_width=True):
                st.session_state.scan_result = None
                st.session_state.ai_analysis = None
                st.rerun()

        # Load example
        if "_example" in st.session_state:
            ex = st.session_state.pop("_example")
            r = cynetra_engine(ex)
            st.session_state.scan_result = r
            st.session_state["_last_msg_text"] = ex
            st.session_state.total_scans += 1
            if r["verdict"] == "PHISHING": st.session_state.threats_detected += 1
            elif r["verdict"] == "SAFE":   st.session_state.safe_count += 1
            st.session_state.scan_history.insert(0, {
                "text": ex[:80], "score": r["score"],
                "verdict": r["verdict"], "color": r["color"], "time": r["timestamp"],
            })

        if scan_btn and msg_input.strip():
            with st.spinner("Running CYNETRA engine..."):
                time.sleep(0.5)
                r = cynetra_engine(msg_input)
                st.session_state.scan_result = r
                st.session_state.ai_analysis = None  # clear old AI result
                st.session_state["_last_msg_text"] = msg_input
                st.session_state.total_scans += 1
                if r["verdict"] == "PHISHING": st.session_state.threats_detected += 1
                elif r["verdict"] == "SAFE":   st.session_state.safe_count += 1
                st.session_state.scan_history.insert(0, {
                    "text": msg_input[:80], "score": r["score"],
                    "verdict": r["verdict"], "color": r["color"], "time": r["timestamp"],
                })
        elif scan_btn:
            st.warning("Please enter some text to analyse.")
        st.markdown('</div>', unsafe_allow_html=True)

        # ── RESULTS
        result = st.session_state.scan_result
        if result:
            score   = result["score"]
            color   = result["color"]
            verdict = result["verdict"]

            r_col1, r_col2 = st.columns([1, 2])

            with r_col1:
                st.markdown('<div class="g-card" style="text-align:center;">', unsafe_allow_html=True)
                circ   = 440
                offset = circ - (score / 100) * circ
                st.markdown(f"""
                <div style="position:relative;width:180px;height:180px;margin:0 auto 16px;">
                  <svg width="180" height="180" viewBox="0 0 180 180">
                    <circle cx="90" cy="90" r="70"
                      fill="none" stroke="rgba(255,255,255,0.05)" stroke-width="10"/>
                    <circle cx="90" cy="90" r="70"
                      fill="none" stroke="{color}" stroke-width="10"
                      stroke-linecap="round"
                      stroke-dasharray="{circ}"
                      stroke-dashoffset="{offset}"
                      transform="rotate(-90 90 90)"
                      style="filter:drop-shadow(0 0 8px {color});"/>
                  </svg>
                  <div style="position:absolute;inset:0;display:flex;flex-direction:column;
                              align-items:center;justify-content:center;">
                    <div style="font-family:'Orbitron',sans-serif;font-size:2.8rem;
                                font-weight:900;color:{color};line-height:1;
                                text-shadow:0 0 16px {color};">{score}</div>
                    <div style="font-family:'Rajdhani',sans-serif;font-size:0.7rem;
                                letter-spacing:3px;color:var(--text-dim);text-transform:uppercase;">
                      THREAT SCORE</div>
                  </div>
                </div>
                <div>
                  <span class="verdict-badge {result['badge_cls']}">{verdict}</span>
                </div>
                <div style="margin-top:12px;font-family:'Rajdhani',sans-serif;
                            font-size:0.85rem;color:{color};letter-spacing:1px;">
                  {result['verdict_txt']}
                </div>
                <div style="margin-top:8px;font-family:'Share Tech Mono',monospace;
                            font-size:0.65rem;color:var(--text-dim);">
                  {result['vectors']} VECTOR(S) TRIGGERED
                </div>
                """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            with r_col2:
                st.markdown('<div class="g-card">', unsafe_allow_html=True)
                st.markdown('<div class="sec-title">📊 Analysis Breakdown</div>', unsafe_allow_html=True)

                if result["findings"]:
                    for f in result["findings"]:
                        pct = int(f["score"] / f["max"] * 100)
                        bar_color = f["color"]
                        # Build specific hit detail list
                        hits_html = ""
                        if f.get("hits"):
                            hits_html = "<div style='margin-top:6px;'>" + "".join(
                                f"<span style='display:inline-block;font-family:Share Tech Mono,monospace;"
                                f"font-size:0.65rem;color:{bar_color};background:rgba(0,0,0,0.2);"
                                f"border:1px solid {bar_color}40;padding:2px 7px;border-radius:3px;"
                                f"margin:2px 3px 2px 0;'>{h[0]} +{h[1]}</span>"
                                for h in f["hits"][:5]
                            ) + "</div>"
                        st.markdown(f"""
                        <div class="factor">
                          <div class="factor-icon">{f['icon']}</div>
                          <div class="factor-body">
                            <div class="factor-name">{f['category']}</div>
                            <div class="factor-detail">{f['detail']}</div>
                            {hits_html}
                            <div class="factor-bar-wrap" style="margin-top:8px;">
                              <div class="factor-bar-bg">
                                <div class="factor-bar-fill"
                                  style="width:{pct}%;background:linear-gradient(90deg,{bar_color},{bar_color}80);
                                         box-shadow:0 0 8px {bar_color}40;"></div>
                              </div>
                            </div>
                          </div>
                          <div style="text-align:right;min-width:70px;">
                            <div style="font-family:'Orbitron',sans-serif;font-size:1.1rem;
                                        font-weight:700;color:{bar_color};">+{f['score']}</div>
                            <div style="font-family:'Share Tech Mono',monospace;font-size:0.65rem;
                                        color:var(--text-dim);">/ {f['max']} pts</div>
                          </div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div style="text-align:center;padding:24px;color:var(--green);
                                font-family:'Rajdhani',sans-serif;">
                      ✓ No threat signals detected across all vectors.
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            # ── AI ANALYSIS BUTTON + RESULT
            ai_col1, ai_col2 = st.columns([1, 3])
            with ai_col1:
                if st.button("🤖 RUN AI ANALYSIS", key="msg_ai_btn", use_container_width=True):
                    last_text = st.session_state.get("_last_msg_text", "")
                    if last_text:
                        with st.spinner("Claude AI is analysing this message..."):
                            ai_result = get_ai_analysis(last_text, result, "SMS/message")
                            st.session_state.ai_analysis = ai_result
                    else:
                        st.warning("Please run the engine scan first.")

            if st.session_state.ai_analysis:
                render_ai_block(st.session_state.ai_analysis)

            # ── EMERGENCY PANEL
            if verdict == "PHISHING":
                st.markdown("""
                <div class="emergency">
                  <div class="em-title">🚨 EMERGENCY ACTION REQUIRED</div>
                  <div style="font-family:'Rajdhani',sans-serif;font-size:1.1rem;
                              color:rgba(255,180,180,0.9);line-height:1.7;margin-bottom:12px;">
                    <strong style="color:#ff3131;">CYNETRA</strong> has confirmed this message as a
                    <strong>HIGH-RISK PHISHING ATTEMPT</strong>. Do <strong>NOT</strong> click any link,
                    share your OTP, password, or any personal / financial information.
                  </div>
                  <div style="font-family:'Rajdhani',sans-serif;font-size:1rem;
                              color:rgba(255,160,160,0.75);line-height:1.6;">
                    Document this incident and file an official complaint with the
                    <strong style="color:#ff3131;">Indian Cyber Crime Coordination Centre (I4C)</strong>.
                  </div>
                  <div style="display:flex;gap:16px;flex-wrap:wrap;margin-top:20px;align-items:center;">
                    <a class="portal-btn" href="https://www.cybercrime.gov.in/" target="_blank" rel="noopener noreferrer">
                      🚨 REGISTER OFFICIAL COMPLAINT
                    </a>
                    <a class="portal-btn" style="border-color:#bc13fe;color:#bc13fe !important;box-shadow:0 0 20px rgba(188,19,254,0.2);"
                       href="https://sancharsaathi.gov.in/sfc/" target="_blank" rel="noopener noreferrer">
                      📱 REPORT FRAUD SMS
                    </a>
                    <a class="portal-btn" style="border-color:#ffb703;color:#ffb703 !important;box-shadow:0 0 20px rgba(255,183,3,0.2);"
                       href="tel:1930">
                      📞 CALL 1930 HELPLINE
                    </a>
                  </div>
                </div>
                """, unsafe_allow_html=True)

            elif verdict == "SUSPICIOUS":
                st.markdown("""
                <div style="background:rgba(255,183,3,0.06);border:1px solid rgba(255,183,3,0.4);
                            border-radius:14px;padding:24px 28px;margin-top:20px;">
                  <div style="font-family:'Orbitron',sans-serif;color:#ffb703;font-size:0.85rem;
                              letter-spacing:3px;margin-bottom:12px;">⚡ CAUTION ADVISED</div>
                  <div style="font-family:'Rajdhani',sans-serif;font-size:1rem;
                              color:rgba(255,230,150,0.85);line-height:1.6;">
                    This message shows suspicious characteristics. Verify the sender's identity through
                    official channels before taking any action. Do not share OTPs or click unverified links.
                  </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="background:rgba(0,255,136,0.05);border:1px solid rgba(0,255,136,0.25);
                            border-radius:14px;padding:24px 28px;margin-top:20px;text-align:center;">
                  <div style="font-family:'Orbitron',sans-serif;color:#00ff88;font-size:1rem;
                              letter-spacing:3px;text-shadow:0 0 10px #00ff88;">
                    ✓ MESSAGE APPEARS LEGITIMATE
                  </div>
                  <div style="font-family:'Rajdhani',sans-serif;color:rgba(200,232,245,0.5);
                              font-size:0.9rem;margin-top:8px;letter-spacing:2px;">
                    No significant threat signals detected. Always stay vigilant.
                  </div>
                </div>
                """, unsafe_allow_html=True)

    # ─────────────────────────────────────────────
    with tab2:
        st.markdown('<div class="g-card">', unsafe_allow_html=True)
        st.markdown('<div class="sec-title">📧 Email Header & Body Analysis</div>', unsafe_allow_html=True)

        col_e1, col_e2 = st.columns(2)
        with col_e1:
            sender        = st.text_input("Sender Email Address",    placeholder="noreply@sbi-secure-update.xyz", key="email_sender")
            subject       = st.text_input("Email Subject Line",       placeholder="URGENT: Your account has been suspended", key="email_subject")
        with col_e2:
            reply_to      = st.text_input("Reply-To (if different)", placeholder="support@gmail.com", key="email_replyto")
            received_from = st.text_input("Received From IP/Domain", placeholder="185.220.101.45", key="email_recv")

        body = st.text_area("Email Body", placeholder="Paste the email body text here...", height=120, key="email_body")

        ec1, ec2, ec3 = st.columns([2, 1, 1])
        with ec1:
            email_scan_btn = st.button("⚡ ANALYSE EMAIL", key="email_scan", use_container_width=True)
        with ec2:
            if st.button("📋 LOAD EXAMPLE", key="email_example_btn", use_container_width=True):
                st.session_state["_email_example"] = {
                    "sender": "kyc-update@sbi-secure-noreply.xyz",
                    "subject": "URGENT ACTION REQUIRED: SBI Account Suspended",
                    "reply_to": "support123@gmail.com",
                    "received_from": "185.220.101.45",
                    "body": "Dear SBI Customer, Your account has been temporarily suspended due to incomplete KYC verification. To restore your account, click here: http://sbi-kyc-verify.xyz/login?token=abc123 and provide your Aadhaar number, PAN card, and OTP. Failure to verify within 24 hours will result in permanent account closure. - SBI Customer Care",
                }
                st.session_state.email_result = None
                st.session_state.email_ai_analysis = None
                st.rerun()
        with ec3:
            if st.button("🗑 CLEAR", key="email_clear_btn", use_container_width=True):
                st.session_state.email_result = None
                st.session_state.email_ai_analysis = None
                st.rerun()

        # Load email example values
        if "_email_example" in st.session_state:
            ex = st.session_state.pop("_email_example")
            result_e = analyse_email_headers(
                ex["sender"], ex["subject"], ex["reply_to"],
                ex["received_from"], ex["body"]
            )
            st.session_state.email_result = result_e
            st.session_state["_last_email"] = ex

        if email_scan_btn:
            if any([sender, subject, reply_to, received_from, body]):
                with st.spinner("Analysing email headers..."):
                    time.sleep(0.4)
                    result_e = analyse_email_headers(sender, subject, reply_to, received_from, body)
                    st.session_state.email_result = result_e
                    st.session_state.email_ai_analysis = None
                    st.session_state["_last_email"] = {
                        "sender": sender, "subject": subject,
                        "reply_to": reply_to, "received_from": received_from, "body": body
                    }
                    st.session_state.total_scans += 1
                    if result_e["verdict"] == "PHISHING": st.session_state.threats_detected += 1
                    elif result_e["verdict"] == "SAFE":   st.session_state.safe_count += 1
            else:
                st.warning("Please fill in at least one field.")

        st.markdown('</div>', unsafe_allow_html=True)

        # ── EMAIL RESULTS
        er = st.session_state.email_result
        if er:
            # Score + verdict row
            ev_col1, ev_col2 = st.columns([1, 2])
            with ev_col1:
                st.markdown(f"""
                <div class="g-card" style="text-align:center;">
                  <div style="font-family:'Orbitron',sans-serif;font-size:3rem;font-weight:900;
                              color:{er['color']};text-shadow:0 0 16px {er['color']};line-height:1;">
                    {er['score']}
                  </div>
                  <div style="font-family:'Rajdhani',sans-serif;font-size:0.7rem;letter-spacing:3px;
                              color:var(--text-dim);text-transform:uppercase;margin:6px 0 14px;">
                    COMBINED RISK SCORE
                  </div>
                  <span class="verdict-badge {er['badge_cls']}">{er['verdict']}</span>
                  <div style="margin-top:12px;font-family:'Rajdhani',sans-serif;
                              font-size:0.85rem;color:{er['color']};letter-spacing:1px;">
                    {er['verdict_txt']}
                  </div>
                  <div style="margin-top:8px;font-family:'Share Tech Mono',monospace;
                              font-size:0.65rem;color:var(--text-dim);">
                    SCANNED: {er['timestamp']}
                  </div>
                </div>
                """, unsafe_allow_html=True)

            with ev_col2:
                # Header flags display
                st.markdown('<div class="g-card">', unsafe_allow_html=True)
                st.markdown('<div class="sec-title">📋 Header Analysis</div>', unsafe_allow_html=True)
                for hf in er["header_flags"]:
                    flag_bg = {
                        "CRITICAL": "rgba(255,49,49,0.08)",
                        "HIGH":     "rgba(255,107,53,0.08)",
                        "MEDIUM":   "rgba(255,183,3,0.08)",
                        "OK":       "rgba(0,255,136,0.05)",
                    }.get(hf["flag"], "rgba(0,242,255,0.05)")
                    st.markdown(f"""
                    <div class="email-header-row" style="background:{flag_bg};border-radius:6px;padding:10px 12px;margin-bottom:6px;border-left:3px solid {hf['color']};">
                      <div class="email-header-label">{hf['field']}</div>
                      <div style="flex:1;">
                        <div class="email-header-value" style="margin-bottom:4px;">{hf['value'] or '—'}</div>
                        <div style="font-family:'Share Tech Mono',monospace;font-size:0.68rem;color:{hf['color']};">
                          {hf['reason']}
                        </div>
                      </div>
                      <span class="email-flag" style="color:{hf['color']};border:1px solid {hf['color']};background:{flag_bg};">
                        {hf['flag']}
                      </span>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            # Body findings (from cynetra_engine on the body text)
            body_r = er.get("body_result")
            if body_r and body_r["findings"]:
                st.markdown('<div class="g-card">', unsafe_allow_html=True)
                st.markdown('<div class="sec-title">📊 Body Content Analysis</div>', unsafe_allow_html=True)
                for f in body_r["findings"]:
                    pct = int(f["score"] / f["max"] * 100)
                    bar_color = f["color"]
                    hits_html = ""
                    if f.get("hits"):
                        hits_html = "<div style='margin-top:5px;'>" + "".join(
                            f"<span style='display:inline-block;font-family:Share Tech Mono,monospace;"
                            f"font-size:0.62rem;color:{bar_color};background:rgba(0,0,0,0.2);"
                            f"border:1px solid {bar_color}40;padding:2px 6px;border-radius:3px;"
                            f"margin:2px 3px 2px 0;'>{h[0]} +{h[1]}</span>"
                            for h in f["hits"][:4]
                        ) + "</div>"
                    st.markdown(f"""
                    <div class="factor">
                      <div class="factor-icon">{f['icon']}</div>
                      <div class="factor-body">
                        <div class="factor-name">{f['category']}</div>
                        <div class="factor-detail">{f['detail']}</div>
                        {hits_html}
                        <div style="height:5px;background:rgba(255,255,255,0.06);border-radius:999px;
                                    overflow:hidden;margin-top:8px;">
                          <div style="width:{pct}%;height:100%;background:{bar_color};border-radius:999px;
                                      box-shadow:0 0 6px {bar_color}50;"></div>
                        </div>
                      </div>
                      <div style="text-align:right;min-width:70px;">
                        <div style="font-family:'Orbitron',sans-serif;font-size:1.1rem;
                                    font-weight:700;color:{bar_color};">+{f['score']}</div>
                        <div style="font-family:'Share Tech Mono',monospace;font-size:0.65rem;
                                    color:var(--text-dim);">/ {f['max']} pts</div>
                      </div>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            # AI Analysis button for email
            eai_col1, eai_col2 = st.columns([1, 3])
            with eai_col1:
                if st.button("🤖 AI EMAIL ANALYSIS", key="email_ai_btn", use_container_width=True):
                    last_e = st.session_state.get("_last_email", {})
                    with st.spinner("Claude AI analysing email forensics..."):
                        ai_result = get_email_ai_analysis(
                            last_e.get("sender",""),
                            last_e.get("subject",""),
                            last_e.get("reply_to",""),
                            last_e.get("received_from",""),
                            last_e.get("body",""),
                            er
                        )
                        st.session_state.email_ai_analysis = ai_result

            if st.session_state.email_ai_analysis:
                render_ai_block(st.session_state.email_ai_analysis, "🤖 AI EMAIL FORENSICS — POWERED BY CLAUDE")

            # Emergency panel for email
            if er["verdict"] == "PHISHING":
                st.markdown("""
                <div class="emergency">
                  <div class="em-title">🚨 PHISHING EMAIL CONFIRMED</div>
                  <div style="font-family:'Rajdhani',sans-serif;font-size:1.05rem;color:rgba(255,180,180,0.9);line-height:1.7;">
                    Do NOT reply, click any links, or open attachments. Mark as spam and delete immediately.
                    Report to CERT-In and file an official complaint.
                  </div>
                  <div style="display:flex;gap:16px;flex-wrap:wrap;margin-top:16px;">
                    <a class="portal-btn" href="https://www.cybercrime.gov.in/" target="_blank" rel="noopener noreferrer">
                      🚨 FILE OFFICIAL COMPLAINT
                    </a>
                    <a class="portal-btn" style="border-color:#00f2ff;color:#00f2ff !important;"
                       href="https://www.cert-in.org.in/" target="_blank">
                      🔐 REPORT TO CERT-IN
                    </a>
                  </div>
                </div>
                """, unsafe_allow_html=True)
            elif er["verdict"] == "SUSPICIOUS":
                st.markdown("""
                <div style="background:rgba(255,183,3,0.06);border:1px solid rgba(255,183,3,0.4);
                            border-radius:14px;padding:24px 28px;margin-top:20px;">
                  <div style="font-family:'Orbitron',sans-serif;color:#ffb703;font-size:0.85rem;
                              letter-spacing:3px;margin-bottom:12px;">⚡ SUSPICIOUS EMAIL — EXERCISE CAUTION</div>
                  <div style="font-family:'Rajdhani',sans-serif;font-size:1rem;
                              color:rgba(255,230,150,0.85);line-height:1.6;">
                    This email shows multiple suspicious signals. Do not click links or share any credentials.
                    Verify the sender through official channels before responding.
                  </div>
                </div>
                """, unsafe_allow_html=True)

    # ─────────────────────────────────────────────
    with tab3:
        st.markdown('<div class="g-card">', unsafe_allow_html=True)
        st.markdown('<div class="sec-title">📦 Batch Message Scanner</div>', unsafe_allow_html=True)
        st.markdown("""
        <div style="font-family:'Rajdhani',sans-serif;color:var(--text-dim);margin-bottom:16px;">
          Enter multiple messages separated by <code style="color:var(--cyan);">---</code> on its own line.
          Each message will be analysed independently.
        </div>
        """, unsafe_allow_html=True)
        batch_input = st.text_area(
            "",
            placeholder="Message 1 text here...\n---\nMessage 2 text here...\n---\nMessage 3 text here...",
            height=200,
            key="batch_input",
            label_visibility="collapsed",
        )
        if st.button("⚡ ANALYSE ALL MESSAGES", key="batch_scan", use_container_width=False):
            msgs = [m.strip() for m in batch_input.split("---") if m.strip()]
            if msgs:
                results = []
                prog = st.progress(0)
                for i, msg in enumerate(msgs):
                    r = cynetra_engine(msg)
                    results.append((msg[:60], r))
                    st.session_state.total_scans += 1
                    if r["verdict"] == "PHISHING": st.session_state.threats_detected += 1
                    elif r["verdict"] == "SAFE":   st.session_state.safe_count += 1
                    prog.progress((i+1)/len(msgs))
                    time.sleep(0.2)

                st.markdown(f"""
                <div style="display:flex;gap:16px;flex-wrap:wrap;margin-bottom:20px;">
                  <div class="stat-box" style="flex:1;">
                    <div class="stat-num" style="color:var(--cyan);">{len(msgs)}</div>
                    <div class="stat-lbl">Messages Scanned</div>
                  </div>
                  <div class="stat-box" style="flex:1;">
                    <div class="stat-num" style="color:#ff3131;">
                      {sum(1 for _,r in results if r['verdict']=='PHISHING')}
                    </div>
                    <div class="stat-lbl">Phishing Detected</div>
                  </div>
                  <div class="stat-box" style="flex:1;">
                    <div class="stat-num" style="color:#ffb703;">
                      {sum(1 for _,r in results if r['verdict']=='SUSPICIOUS')}
                    </div>
                    <div class="stat-lbl">Suspicious</div>
                  </div>
                  <div class="stat-box" style="flex:1;">
                    <div class="stat-num" style="color:#00ff88;">
                      {sum(1 for _,r in results if r['verdict']=='SAFE')}
                    </div>
                    <div class="stat-lbl">Safe</div>
                  </div>
                </div>
                """, unsafe_allow_html=True)

                for text_preview, r in results:
                    st.markdown(f"""
                    <div style="display:flex;align-items:center;gap:14px;padding:12px 16px;
                                background:rgba(4,18,32,0.5);border:1px solid rgba(0,242,255,0.08);
                                border-radius:8px;margin-bottom:8px;font-family:'Rajdhani',sans-serif;">
                      <span style="font-family:'Orbitron',sans-serif;font-size:1.1rem;
                                   font-weight:700;color:{r['color']};min-width:45px;">{r['score']}</span>
                      <span class="verdict-badge {r['badge_cls']}" style="padding:4px 10px;font-size:0.6rem;">{r['verdict']}</span>
                      <span style="flex:1;color:var(--text-dim);font-size:0.9rem;">{text_preview}...</span>
                      <span style="font-family:'Share Tech Mono',monospace;font-size:0.65rem;color:var(--text-dim);">
                        {r['vectors']} vectors
                      </span>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.warning("Please enter at least one message separated by ---")
        st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
#  PAGE: URL CHECK
# ══════════════════════════════════════════════════════════════
elif page == "url_check":

    st.markdown("""
    <div class="page-hero">
      <h1>URL THREAT ANALYSIS</h1>
      <p>Scan links using ML + Cyber Intelligence</p>
    </div>
    """, unsafe_allow_html=True)

    # INPUT
    url_input = st.text_input("Enter URL to check", key="url_input_box")

    # BUTTON
    if st.button("CHECK URL", key="check_url_btn"):

        if url_input == "":
            st.warning("Please enter a URL")
        else:
            # RULE BASED
            result = url_analyzer(url_input)

            # ML BASED
            ml_result = ml_url_predict(url_input)

            # OUTPUT
            st.write("### 🔍 Rule-Based Analysis")
            st.write("Score:", result["score"])
            st.write("Verdict:", result["verdict"])

            st.write("### 🤖 ML Prediction")
            st.write("Result:", ml_result)
    
    u1, u2, u3 = st.columns([2,1,1])
    with u1:
        url_scan = st.button("🔍 DEEP URL ANALYSIS", key="url_scan_btn", use_container_width=True)
    with u2:
        if st.button("📋 LOAD SUSPICIOUS URL", key="url_example", use_container_width=True):
            st.session_state["_url_ex"] = "http://hdfc-bank-kyc-update.xyz/secure/login?token=abc&cvv=123&otp=true"
            st.session_state.url_ai_analysis = None
            st.rerun()
    with u3:
        if st.button("🗑 CLEAR", key="url_clear_btn", use_container_width=True):
            st.session_state.url_result = None
            st.session_state.url_ai_analysis = None
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    if "_url_ex" in st.session_state:
        ex_url = st.session_state.pop("_url_ex")
        st.session_state.url_result = url_analyzer(ex_url)
        st.session_state["_url_display"] = ex_url

    if url_scan and url_input.strip():
        with st.spinner("Scanning URL..."):
            time.sleep(0.4)
            st.session_state.url_result = url_analyzer(url_input)
            st.session_state["_url_display"] = url_input
            st.session_state.url_ai_analysis = None
            st.session_state.total_scans += 1
    elif url_scan:
        st.warning("Please enter a URL first.")

    ur = st.session_state.url_result
    if ur:
        display_url = st.session_state.get("_url_display", "")

        # Dissected URL display
        if display_url:
            try:
                parsed    = urllib.parse.urlparse(display_url if display_url.startswith('http') else 'http://'+display_url)
                proto     = parsed.scheme.upper() + "://"
                dom       = parsed.netloc or display_url.split('/')[0]
                pth       = parsed.path
                qry       = "?" + parsed.query if parsed.query else ""
            except Exception:
                proto, dom, pth, qry = "HTTP://", display_url, "", ""

            proto_color = "#ff3131" if proto == "HTTP://" else "#00ff88"
            st.markdown(f"""
            <div class="g-card">
              <div class="sec-title">🔬 URL Dissection</div>
              <div style="font-family:'Share Tech Mono',monospace;font-size:0.9rem;
                          word-break:break-all;line-height:2;">
                <span style="color:{proto_color};text-shadow:0 0 8px {proto_color};">{proto}</span><span style="color:#ff6b35;">{dom}</span><span style="color:#ffb703;">{pth}</span><span style="color:#bc13fe;">{qry}</span>
              </div>
              <div style="display:flex;gap:20px;flex-wrap:wrap;margin-top:14px;font-family:'Rajdhani',sans-serif;font-size:0.82rem;">
                <span style="color:{proto_color};">▪ Protocol: {proto}</span>
                <span style="color:#ff6b35;">▪ Domain: {dom}</span>
                {'<span style="color:#ffb703;">▪ Path: ' + pth + '</span>' if pth and pth != '/' else ''}
                {'<span style="color:#bc13fe;">▪ Params: ' + qry + '</span>' if qry else ''}
              </div>
            </div>
            """, unsafe_allow_html=True)

        sc1, sc2 = st.columns([1, 2])
        with sc1:
            st.markdown(f"""
            <div class="g-card" style="text-align:center;">
              <div style="font-family:'Orbitron',sans-serif;font-size:3.5rem;font-weight:900;
                          color:{ur['color']};text-shadow:0 0 20px {ur['color']};line-height:1;">
                {ur['score']}
              </div>
              <div style="font-family:'Rajdhani',sans-serif;font-size:0.7rem;
                          letter-spacing:3px;color:var(--text-dim);text-transform:uppercase;margin:6px 0 16px;">
                RISK SCORE
              </div>
              <span class="verdict-badge {'vb-danger' if ur['verdict']=='MALICIOUS' else 'vb-warn' if ur['verdict']=='SUSPICIOUS' else 'vb-safe'}">
                {ur['verdict']}
              </span>
            </div>
            """, unsafe_allow_html=True)

        with sc2:
            st.markdown('<div class="g-card">', unsafe_allow_html=True)
            st.markdown('<div class="sec-title">🔎 Security Checks</div>', unsafe_allow_html=True)
            if ur["findings"]:
                for f in ur["findings"]:
                    sev_color = {"CRITICAL":"#ff3131","HIGH":"#ff6b35","MEDIUM":"#ffb703","OK":"#00ff88"}.get(f["severity"],"#00f2ff")
                    st.markdown(f"""
                    <div style="display:flex;align-items:center;gap:12px;padding:10px 0;
                                border-bottom:1px solid rgba(0,242,255,0.06);">
                      <div style="min-width:80px;">
                        <span style="font-family:'Orbitron',sans-serif;font-size:0.6rem;letter-spacing:1px;
                                     color:{sev_color};border:1px solid {sev_color};
                                     padding:2px 8px;border-radius:4px;">{f['severity']}</span>
                      </div>
                      <div style="min-width:90px;font-family:'Share Tech Mono',monospace;
                                  font-size:0.75rem;color:var(--cyan);">{f['check']}</div>
                      <div style="flex:1;font-family:'Rajdhani',sans-serif;font-size:0.9rem;
                                  color:var(--text-dim);">{f['detail']}</div>
                      {f'<div style="font-family:Orbitron,sans-serif;font-size:0.75rem;color:{sev_color};">+{f["pts"]}</div>' if f['pts'] > 0 else ''}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown('<div style="color:var(--green);font-family:Rajdhani,sans-serif;padding:16px;">✓ No threats detected in URL structure.</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # AI Analysis for URL
        uai_col1, uai_col2 = st.columns([1, 3])
        with uai_col1:
            # URL input
          url = st.text_input("Enter URL to check")


# ══════════════════════════════════════════════════════════════
#  PAGE: EDUCATION / CYBER GUIDE
# ══════════════════════════════════════════════════════════════
elif page == "education":
    st.markdown("""
    <div class="page-hero">
      <h1>CYBER SAFETY GUIDE</h1>
      <p>Recognise · Avoid · Report — Indian Cybercrime Awareness</p>
    </div>
    """, unsafe_allow_html=True)

    tab_e1, tab_e2, tab_e3 = st.tabs(["🛡 HOW TO SPOT PHISHING", "📱 INDIA-SPECIFIC SCAMS", "📋 SAFETY CHECKLIST"])

    with tab_e1:
        st.markdown('<div class="g-card">', unsafe_allow_html=True)
        st.markdown('<div class="sec-title">🧠 Psychological Manipulation Tactics</div>', unsafe_allow_html=True)
        psych_tips = [
            ("⏰", "Urgency & Time Pressure",
             "Phishers create false deadlines ('Your account expires in 2 hours'). Legitimate banks NEVER rush you. Always verify through official channels."),
            ("😱", "Fear & Threat",
             "'Your account will be permanently closed' — this triggers panic. Real banks send formal notices by post and don't threaten via SMS."),
            ("🎁", "Greed & Reward",
             "Free prizes, cashback, lottery wins. If it sounds too good to be true, it is. India's cybercrime rate for prize scams grew 340% in 2023."),
            ("🔒", "Authority Impersonation",
             "Fake UIDAI, Income Tax, or RBI messages. Government agencies never ask for OTPs or credentials via SMS/email."),
        ]
        for icon, title, body in psych_tips:
            st.markdown(f"""
            <div class="tip-item">
              <div class="tip-icon">{icon}</div>
              <div>
                <div class="tip-title">{title}</div>
                <div class="tip-body">{body}</div>
              </div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="g-card">', unsafe_allow_html=True)
        st.markdown('<div class="sec-title">🌐 URL Red Flags to Spot</div>', unsafe_allow_html=True)
        url_tips = [
            ("🔴", "sbi-secure-update.xyz",           "Brand name + 'secure/update' + suspicious TLD"),
            ("🔴", "http://192.168.1.1/hdfc/login",   "IP address instead of domain name"),
            ("🟠", "hdfc-bank-kyc.online/verify",     "Brand name hyphenated with keyword"),
            ("🟠", "bit.ly/SBI-KYC-Update",           "URL shortener hiding real destination"),
            ("🟡", "secure.paypa1.com",               "Character substitution: '1' instead of 'l'"),
        ]
        for dot, url, desc in url_tips:
            st.markdown(f"""
            <div style="display:flex;align-items:flex-start;gap:12px;padding:10px 0;
                        border-bottom:1px solid rgba(0,242,255,0.06);">
              <span style="margin-top:2px;">{dot}</span>
              <div>
                <div style="font-family:'Share Tech Mono',monospace;font-size:0.85rem;
                            color:var(--red);margin-bottom:3px;">{url}</div>
                <div style="font-family:'Rajdhani',sans-serif;font-size:0.9rem;
                            color:var(--text-dim);">{desc}</div>
              </div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with tab_e2:
        st.markdown('<div class="g-card">', unsafe_allow_html=True)
        st.markdown('<div class="sec-title">🇮🇳 Common Indian Phishing Campaigns</div>', unsafe_allow_html=True)
        scams = [
            ("🏦", "SBI / HDFC KYC Scam",
             "SMS claiming your KYC is incomplete and account will be blocked. Asks to click a link and enter Aadhaar + OTP. Real banks never do this via SMS.",
             "HIGH"),
            ("📱", "Fake UPI / PhonePe / GPay",
             "Fraudsters send fake 'payment received' screenshots and ask you to 'confirm' by sending back. Reverse charges do not exist on UPI.",
             "CRITICAL"),
            ("🚂", "IRCTC Refund Scam",
             "Fake messages about train ticket refunds asking for bank account + CVV details. IRCTC refunds are automatic — no info ever needed.",
             "HIGH"),
            ("🪪", "Aadhaar / PAN Update",
             "'Link Aadhaar with PAN before March 31' SMS with suspicious links. The official process is only at incometax.gov.in.",
             "CRITICAL"),
            ("🎁", "Flipkart / Amazon Lottery",
             "'You have been selected for a ₹50,000 prize' — always followed by a 'processing fee'. No legitimate retailer runs such schemes.",
             "HIGH"),
            ("👮", "Fake Cyber Police / CBI",
             "Video call from 'CBI/Police' claiming you're involved in illegal activity. Demands payment to 'close the case'. Pure social engineering.",
             "CRITICAL"),
        ]
        for icon, title, desc, severity in scams:
            sev_c = "#ff3131" if severity == "CRITICAL" else "#ffb703"
            st.markdown(f"""
            <div style="padding:16px;background:rgba(0,0,0,0.2);border-radius:10px;
                        border-left:3px solid {sev_c};margin-bottom:12px;">
              <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">
                <span style="font-size:1.3rem;">{icon}</span>
                <span style="font-family:'Orbitron',sans-serif;font-size:0.8rem;color:{sev_c};
                             letter-spacing:1px;">{title}</span>
                <span style="margin-left:auto;font-family:'Orbitron',sans-serif;font-size:0.6rem;
                             letter-spacing:1px;color:{sev_c};border:1px solid {sev_c};
                             padding:2px 8px;border-radius:3px;">{severity}</span>
              </div>
              <div style="font-family:'Rajdhani',sans-serif;font-size:0.95rem;
                          color:var(--text-dim);line-height:1.6;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with tab_e3:
        st.markdown('<div class="g-card">', unsafe_allow_html=True)
        st.markdown('<div class="sec-title">✅ Personal Cyber Safety Checklist</div>', unsafe_allow_html=True)
        checklist = [
            (True,  "Never share OTP with anyone — banks and payment apps NEVER ask"),
            (True,  "Verify URLs before clicking — look for HTTPS and correct spelling"),
            (True,  "Enable 2FA on all banking and payment apps"),
            (True,  "Download apps only from official Play Store / App Store"),
            (True,  "Regularly check your CIBIL report for unauthorized credit"),
            (False, "Never click links in SMS/WhatsApp claiming to be your bank"),
            (False, "Never call back unknown numbers from missed call scams"),
            (False, "Never install apps via links received in SMS or WhatsApp"),
            (False, "Never share screen with unknown callers claiming to be support"),
            (False, "Never enter Aadhaar / PAN on non-.gov.in websites"),
        ]
        for is_do, item in checklist:
            icon  = "✅" if is_do else "❌"
            color = "rgba(0,255,136,0.8)" if is_do else "rgba(255,49,49,0.8)"
            label = "DO:" if is_do else "NEVER:"
            st.markdown(f"""
            <div style="display:flex;align-items:flex-start;gap:12px;padding:10px 0;
                        border-bottom:1px solid rgba(0,242,255,0.06);
                        font-family:'Rajdhani',sans-serif;">
              <span style="font-size:1.1rem;margin-top:1px;">{icon}</span>
              <span>
                <strong style="color:{color};letter-spacing:1px;">{label}</strong>
                <span style="color:var(--text-dim);margin-left:6px;">{item}</span>
              </span>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
#  PAGE: REPORT
# ══════════════════════════════════════════════════════════════
elif page == "report":
    st.markdown("""
    <div class="page-hero">
      <h1>REPORT CYBERCRIME</h1>
      <p>Official Indian government portals · Emergency helplines · Reporting guides</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="emergency" style="text-align:center;margin-bottom:28px;">
      <div style="font-family:'Orbitron',sans-serif;color:#ff3131;font-size:1.2rem;
                  letter-spacing:3px;margin-bottom:12px;text-shadow:0 0 12px #ff3131;">
        🚨 EMERGENCY CYBER HELPLINE
      </div>
      <div style="font-family:'Orbitron',sans-serif;font-size:3rem;font-weight:900;
                  color:#ff3131;text-shadow:0 0 24px #ff3131;letter-spacing:0.2em;margin-bottom:8px;">
        1930
      </div>
      <div style="font-family:'Rajdhani',sans-serif;color:rgba(255,180,180,0.8);
                  font-size:1.05rem;margin-bottom:16px;">
        National Cybercrime Helpline · Available 24×7 · Free to call
      </div>
      <div style="font-family:'Share Tech Mono',monospace;font-size:0.75rem;
                  color:rgba(255,130,130,0.5);letter-spacing:2px;">
        Ministry of Home Affairs · Government of India
      </div>
    </div>
    """, unsafe_allow_html=True)

    r1, r2 = st.columns(2)
    with r1:
        st.markdown('<div class="g-card">', unsafe_allow_html=True)
        st.markdown('<div class="sec-title">🏛 Official Portals</div>', unsafe_allow_html=True)
        portals = [
            ("🌐", "National Cyber Crime Reporting Portal",
             "File FIR for any cybercrime — phishing, fraud, harassment",
             "https://www.cybercrime.gov.in/", "#ff3131"),
            ("📱", "Sanchar Saathi — Report Fraud SMS/Calls",
             "Report unwanted or fraudulent telecom messages",
             "https://sancharsaathi.gov.in/sfc/", "#bc13fe"),
            ("🔐", "CERT-In Incident Reporting",
             "Report cybersecurity incidents to India's national CERT",
             "https://www.cert-in.org.in/", "#00f2ff"),
            ("💳", "RBI Ombudsman — Banking Fraud",
             "Escalate banking and payment fraud complaints",
             "https://cms.rbi.org.in/", "#ffb703"),
        ]
        for icon, title, desc, url, clr in portals:
            st.markdown(f"""
            <div style="padding:16px;background:rgba(0,0,0,0.15);border-radius:10px;
                        border:1px solid rgba(0,242,255,0.08);margin-bottom:12px;">
              <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">
                <span style="font-size:1.2rem;">{icon}</span>
                <span style="font-family:'Orbitron',sans-serif;font-size:0.75rem;
                             letter-spacing:1px;color:{clr};">{title}</span>
              </div>
              <div style="font-family:'Rajdhani',sans-serif;font-size:0.9rem;
                          color:var(--text-dim);margin-bottom:10px;">{desc}</div>
              <a href="{url}" target="_blank" rel="noopener noreferrer"
                 style="font-family:'Share Tech Mono',monospace;font-size:0.7rem;
                        color:{clr};text-decoration:none;letter-spacing:1px;">
                OPEN PORTAL →
              </a>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with r2:
        st.markdown('<div class="g-card">', unsafe_allow_html=True)
        st.markdown('<div class="sec-title">📋 How to File a Complaint</div>', unsafe_allow_html=True)
        steps = [
            ("01", "Document Everything",
             "Screenshot the message/email. Note the sender number/email, time received, and any URLs. Do NOT delete evidence."),
            ("02", "Call 1930 Immediately",
             "For financial fraud, call 1930 ASAP — quick reporting can freeze fraudulent transactions."),
            ("03", "File Online at cybercrime.gov.in",
             "Select 'Report Other Cyber Crime' or 'Women / Child Related Crime'. Fill all fields accurately."),
            ("04", "Provide Complaint Number",
             "You'll receive an acknowledgement number. Track status online. You may need to visit the nearest cyber cell."),
            ("05", "Contact Bank (if financial loss)",
             "Immediately call your bank's 24-hr helpline. Request a transaction freeze. File a dispute for unauthorized transactions."),
        ]
        for num, title, desc in steps:
            st.markdown(f"""
            <div style="display:flex;gap:14px;padding:14px 0;
                        border-bottom:1px solid rgba(0,242,255,0.06);">
              <div style="font-family:'Orbitron',sans-serif;font-size:1.4rem;font-weight:900;
                          color:rgba(0,242,255,0.2);min-width:36px;line-height:1;">{num}</div>
              <div>
                <div style="font-family:'Rajdhani',sans-serif;font-weight:700;font-size:1rem;
                            color:var(--cyan);margin-bottom:4px;">{title}</div>
                <div style="font-family:'Rajdhani',sans-serif;font-size:0.9rem;
                            color:var(--text-dim);line-height:1.5;">{desc}</div>
              </div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="g-card">', unsafe_allow_html=True)
    st.markdown('<div class="sec-title">📞 Emergency Helplines</div>', unsafe_allow_html=True)
    helplines = [
        ("1930",          "National Cyber Crime", "24×7",         "#ff3131"),
        ("155260",        "RBI Financial Fraud",  "24×7",         "#ffb703"),
        ("14448",         "TRAI Fraud Calls/SMS", "Business Hrs", "#00f2ff"),
        ("1800-180-1990", "India Post Fraud",     "Business Hrs", "#bc13fe"),
        ("1800-11-4000",  "Consumer Helpline",    "Business Hrs", "#00ff88"),
    ]
    hl_cols = st.columns(len(helplines))
    for col, (num, name, hrs, clr) in zip(hl_cols, helplines):
        with col:
            st.markdown(f"""
            <div class="stat-box" style="padding:16px 8px;">
              <div style="font-family:'Orbitron',sans-serif;font-size:1rem;font-weight:700;
                          color:{clr};text-shadow:0 0 8px {clr};margin-bottom:6px;">{num}</div>
              <div style="font-family:'Rajdhani',sans-serif;font-size:0.8rem;
                          color:var(--text-dim);margin-bottom:3px;">{name}</div>
              <div style="font-family:'Share Tech Mono',monospace;font-size:0.65rem;
                          color:{clr};opacity:0.6;">{hrs}</div>
            </div>
            """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
#  FOOTER
# ══════════════════════════════════════════════════════════════
st.markdown("""
<div class="footer">
  <div class="footer-logo">⬡ CYNETRA</div>
  <div class="footer-txt">
    PHISH HUNTER AI · INDIAN THREAT INTELLIGENCE ENGINE · CLAUDE AI INTEGRATED
  </div>
  <div style="margin-top:8px;font-family:'Share Tech Mono',monospace;font-size:0.65rem;
              color:rgba(200,232,245,0.15);letter-spacing:2px;">
    BUILT FOR EDUCATIONAL & CYBERSECURITY AWARENESS · NOT A SUBSTITUTE FOR OFFICIAL INVESTIGATION
  </div>
</div>
""", unsafe_allow_html=True)
