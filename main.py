import os
import urllib.request
import json
import pandas as pd
import numpy as np
import datetime
from flask import Flask, render_template_string, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = 'kemisetso_robot_secure_session_key'

# Credentials Configuration
CRED_ID = "069 890 7756"
CRED_PASS = "Kemisetso@2009"
CRED_ADMIN = "Kemisetso.Fx"
CRED_QUESTION = "None of ur business"

INSTRUMENTS = {
    "GOLD (XAU/USD)": "GC=F",
    "US30 (INDEX 30)": "^DJI"
}

EXECUTION_TIMEFRAME = "30m"
TREND_TIMEFRAME = "60m"
FOOTER_BRAND = "Kemisetso.Fx"

def get_market_session():
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    hour = now_utc.hour
    active_sessions = []
    if 0 <= hour < 9:
        active_sessions.append("Asian")
    if 7 <= hour < 16:
        active_sessions.append("London")
    if 13 <= hour < 22:
        active_sessions.append("New York")
    session_name = " & ".join(active_sessions) if active_sessions else "Off-Market Hours"
    return session_name

def fetch_data(symbol, interval, range_str="10d"):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval={interval}&range={range_str}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
        result = data['chart']['result'][0]
        timestamps = result['timestamp']
        indicators = result['indicators']['quote'][0]
        df = pd.DataFrame({
            'High': indicators['high'],
            'Low': indicators['low'],
            'Close': indicators['close']
        }, index=pd.to_datetime(timestamps, unit='s')).dropna()
        return df
    except Exception:
        return None

def calculate_advanced_indicators(df_30m, df_1h):
    # HTF Trend Check (EMA 50 on 1H)
    df_1h['EMA50_HTF'] = df_1h['Close'].ewm(span=50, adjust=False).mean()
    htf_bullish = df_1h['Close'].iloc[-1] > df_1h['EMA50_HTF'].iloc[-1]

    close, high, low = df_30m['Close'], df_30m['High'], df_30m['Low']
    
    # EMAs
    df_30m['EMA_Fast'] = close.ewm(span=9, adjust=False).mean()
    df_30m['EMA_Slow'] = close.ewm(span=21, adjust=False).mean()

    # RSI (14)
    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / (loss + 1e-9)
    df_30m['RSI'] = 100 - (100 / (1 + rs))

    # MACD
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    df_30m['MACD'] = ema12 - ema26
    df_30m['MACD_Signal'] = df_30m['MACD'].ewm(span=9, adjust=False).mean()

    # ATR (14)
    tr = np.maximum(high - low, np.maximum(abs(high - close.shift(1)), abs(low - close.shift(1))))
    df_30m['ATR'] = pd.Series(tr).rolling(14).mean()

    # ADX (14)
    plus_dm = high.diff()
    minus_dm = low.diff()
    plus_dm = np.where((plus_dm > minus_dm) & (plus_dm > 0), plus_dm, 0.0)
    minus_dm = np.where((minus_dm > plus_dm) & (minus_dm > 0), minus_dm, 0.0)
    tr_smooth = pd.Series(tr).rolling(14).mean()
    plus_di = 100 * (pd.Series(plus_dm).rolling(14).mean() / (tr_smooth + 1e-9))
    minus_di = 100 * (pd.Series(minus_dm).rolling(14).mean() / (tr_smooth + 1e-9))
    dx = 100 * (abs(plus_di - minus_di) / (plus_di + minus_di + 1e-9))
    df_30m['ADX'] = dx.rolling(14).mean()

    return df_30m, htf_bullish

def analyze_signals(name, df_30m, htf_bullish):
    latest = df_30m.iloc[-1]
    current_price = round(latest['Close'], 2)
    atr, adx, rsi = latest['ATR'], latest['ADX'], latest['RSI']
    ema_fast, ema_slow = latest['EMA_Fast'], latest['EMA_Slow']
    macd, macd_sig = latest['MACD'], latest['MACD_Signal']

    confidence = 0
    
    # Indicator Confluence Setup
    if ema_fast > ema_slow: confidence += 25
    if htf_bullish: confidence += 25
    if macd > macd_sig: confidence += 20
    if 40 <= rsi <= 65: confidence += 15
    if adx >= 20: confidence += 15

    # Determine Signal and Risk Breakdown
    if confidence >= 70:
        signal = "BUY"
        risk_level = "LOW RISK - HIGH CONFLUENCE" if confidence >= 85 else "MEDIUM RISK SCALP"
        sl = round(current_price - (atr * 1.2), 2)
        tp = round(current_price + (atr * 1.8), 2)
        advice = f"✅ STABILITY HIGH ({confidence}%): ENTER BUY"
    elif confidence <= 30:
        signal = "SELL"
        risk_level = "LOW RISK - HIGH CONFLUENCE" if confidence <= 15 else "MEDIUM RISK SCALP"
        sl = round(current_price + (atr * 1.2), 2)
        tp = round(current_price - (atr * 1.8), 2)
        advice = f"✅ STABILITY HIGH ({100-confidence}%): ENTER SELL"
    else:
        # High-Risk / Uncertain Territory Signal
        signal = "BUY (RISKY)" if ema_fast > ema_slow else "SELL (RISKY)"
        risk_level = "⚠️ HIGH RISK / VOLATILE - REDUCE LOT SIZE"
        sl = round(current_price - (atr * 1.0), 2) if "BUY" in signal else round(current_price + (atr * 1.0), 2)
        tp = round(current_price + (atr * 1.2), 2) if "BUY" in signal else round(current_price - (atr * 1.2), 2)
        advice = f"⚠️ HIGH RISK ZONE: Confluence is low ({confidence}%). Exercise caution!"

    return {
        "Name": name, "Price": current_price, "Signal": signal, "Confidence": f"{confidence}%",
        "RSI": round(rsi, 1), "ADX": round(adx, 1), "HTF_Bias": "BULLISH" if htf_bullish else "BEARISH",
        "SL": sl, "TP": tp, "RiskLevel": risk_level, "Advice": advice
    }

LOGIN_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Login | Kemisetso's Robot</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: 'Segoe UI', Tahoma, sans-serif; background: #0f172a; color: #f8fafc; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }
        .login-card { background: #1e293b; padding: 30px; border-radius: 12px; border: 1px solid #334155; width: 90%; max-width: 400px; }
        h1 { color: #f59e0b; font-size: 20px; text-align: center; margin-bottom: 20px; }
        label { display: block; margin-top: 10px; font-size: 12px; color: #cbd5e1; }
        input { width: 100%; padding: 10px; margin-top: 5px; box-sizing: border-box; background: #0f172a; border: 1px solid #475569; color: #fff; border-radius: 6px; }
        button { width: 100%; padding: 12px; margin-top: 20px; background: #f59e0b; border: none; border-radius: 6px; font-weight: bold; color: #0f172a; cursor: pointer; }
        .error { background: #ef4444; color: white; padding: 10px; border-radius: 6px; font-size: 12px; text-align: center; margin-bottom: 10px; }
    </style>
</head>
<body>
    <div class="login-card">
        <h1>Kemisetso's Robot Portal</h1>
        {% with messages = get_flashed_messages() %}
          {% if messages %}<div class="error">{{ messages[0] }}</div>{% endif %}
        {% endwith %}
        <form method="POST">
            <label>ID Number:</label>
            <input type="text" name="user_id" required placeholder="069 ...">

            <label>Password:</label>
            <input type="password" name="password" required placeholder="Password">

            <label>Admin Login Name:</label>
            <input type="text" name="admin_name" required placeholder="Admin Name">

            <label>Why are you here?</label>
            <input type="text" name="why_here" required placeholder="Answer here">

            <button type="submit">Authenticate Portal</button>
        </form>
    </div>
</body>
</html>
"""

DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Welcome to Kemisetso's Robot</title>
    <meta http-equiv="refresh" content="10">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: monospace; background: #0f172a; color: #38bdf8; padding: 20px; margin: 0; }
        header { display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #f59e0b; padding-bottom: 10px; margin-bottom: 20px; }
        h1 { color: #f59e0b; margin: 0; font-size: 20px; }
        .logout-btn { background: #ef4444; color: white; padding: 6px 12px; text-decoration: none; border-radius: 4px; font-size: 12px; }
        .card { background: #1e293b; border: 1px solid #334155; padding: 15px; margin-bottom: 15px; border-radius: 8px; }
        .BUY { color: #22c55e; font-weight: bold; }
        .SELL { color: #ef4444; font-weight: bold; }
        .RISKY { color: #f59e0b; font-weight: bold; }
        .risk-badge { background: #334155; padding: 4px 8px; border-radius: 4px; font-size: 11px; color: #f8fafc; }
    </style>
</head>
<body>
    <header>
        <h1>Welcome to Kemisetso's Robot</h1>
        <a href="/logout" class="logout-btn">Logout</a>
    </header>
    <p>🌐 ACTIVE SESSION: <b>{{ session_name }}</b> | ⏱️ TIMEFRAME: <b>30M</b> | 🕒 REFRESH: {{ now_str }}</p>
    
    {% for r in results %}
    <div class="card">
        <h2>► {{ r.Name }} | Price: {{ r.Price }}</h2>
        <p>├─ Signal: <span class="{% if 'RISKY' in r.Signal %}RISKY{% elif 'BUY' in r.Signal %}BUY{% else %}SELL{% endif %}">{{ r.Signal }}</span> (Confluence: {{ r.Confidence }})</p>
        <p>├─ Technicals: RSI (14): {{ r.RSI }} | ADX: {{ r.ADX }} | HTF Bias: {{ r.HTF_Bias }}</p>
        <p>├─ Risk Status: <span class="risk-badge">{{ r.RiskLevel }}</span></p>
        <p>├─ Targets: Stop Loss: {{ r.SL }} | Take Profit: {{ r.TP }}</p>
        <p>└─ Strategy Guidance: {{ r.Advice }}</p>
    </div>
    {% endfor %}
</body>
</html>
"""

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form.get('user_id', '').strip()
        password = request.form.get('password', '').strip()
        admin_name = request.form.get('admin_name', '').strip()
        why_here = request.form.get('why_here', '').strip()

        if (user_id == CRED_ID and 
            password == CRED_PASS and 
            admin_name == CRED_ADMIN and 
            why_here == CRED_QUESTION):
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid Authentication Credentials.')
            return redirect(url_for('login'))
            
    return render_template_string(LOGIN_HTML)

@app.route('/')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    session_name = get_market_session()
    results = []
    
    for name, symbol in INSTRUMENTS.items():
        df_30m = fetch_data(symbol, EXECUTION_TIMEFRAME, "10d")
        df_1h = fetch_data(symbol, TREND_TIMEFRAME, "15d")
        if df_30m is not None and df_1h is not None:
            df_30m, htf_bullish = calculate_advanced_indicators(df_30m, df_1h)
            res = analyze_signals(name, df_30m, htf_bullish)
            results.append(res)

    return render_template_string(DASHBOARD_HTML, results=results, session_name=session_name, now_str=now_str)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
