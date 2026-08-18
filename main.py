import os
import datetime
import pandas as pd
import numpy as np
import yfinance as yf
from flask import Flask, render_template_string, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = 'kemisetso_gold_h1_robot_secret_key'

# Credentials Configuration
CRED_ID = "069 890 7756"
CRED_PASS = "Kemisetso@2009"
CRED_ADMIN = "Kemisetso.Fx"
CRED_QUESTION = "None of ur business"

FOOTER_BRAND = "Kemisetso.Fx"
SYMBOL = "GC=F"  # Gold Futures (XAU/USD)

def fetch_h1_gold_data():
    try:
        ticker = yf.Ticker(SYMBOL)
        df = ticker.history(period="60d", interval="1h")
        if df.empty or len(df) < 50:
            return None
        return df
    except Exception:
        return None

def analyze_h1_gold(df):
    close = df['Close']
    high = df['High']
    low = df['Low']

    # Moving Averages
    df['EMA9'] = close.ewm(span=9, adjust=False).mean()
    df['EMA21'] = close.ewm(span=21, adjust=False).mean()
    df['EMA200'] = close.ewm(span=200, adjust=False).mean()

    # RSI (14)
    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / (loss + 1e-9)
    df['RSI'] = 100 - (100 / (1 + rs))

    # MACD (12, 26, 9)
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    df['MACD'] = ema12 - ema26
    df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()

    # ATR (14)
    tr = np.maximum(high - low, np.maximum(abs(high - close.shift(1)), abs(low - close.shift(1))))
    df['ATR'] = pd.Series(tr, index=df.index).rolling(14).mean()

    # ADX (14)
    plus_dm = high.diff()
    minus_dm = low.diff()
    plus_dm = np.where((plus_dm > minus_dm) & (plus_dm > 0), plus_dm, 0.0)
    minus_dm = np.where((minus_dm > plus_dm) & (minus_dm > 0), minus_dm, 0.0)
    tr_smooth = pd.Series(tr, index=df.index).rolling(14).mean()
    plus_di = 100 * (pd.Series(plus_dm, index=df.index).rolling(14).mean() / (tr_smooth + 1e-9))
    minus_di = 100 * (pd.Series(minus_dm, index=df.index).rolling(14).mean() / (tr_smooth + 1e-9))
    dx = 100 * (abs(plus_di - minus_di) / (plus_di + minus_di + 1e-9))
    df['ADX'] = dx.rolling(14).mean()

    latest = df.iloc[-1]
    price = round(latest['Close'], 2)
    ema9, ema21, ema200 = latest['EMA9'], latest['EMA21'], latest['EMA200']
    rsi, adx, atr = latest['RSI'], latest['ADX'], latest['ATR']
    macd, macd_sig = latest['MACD'], latest['MACD_Signal']

    score = 0
    # Bullish scoring
    if price > ema200: score += 20
    if ema9 > ema21: score += 20
    if macd > macd_sig: score += 20
    if 45 <= rsi <= 65: score += 20
    if adx >= 22: score += 20

    # Bearish scoring
    bear_score = 0
    if price < ema200: bear_score += 20
    if ema9 < ema21: bear_score += 20
    if macd < macd_sig: bear_score += 20
    if 35 <= rsi <= 55: bear_score += 20
    if adx >= 22: bear_score += 20

    # Decision Matrix
    if score >= 80:
        signal = "STRONG BUY"
        accuracy = min(score, 94)
        lot_advice = "✅ SAFE FOR 0.01 LOT SIZE"
        hold_time = "2 Hours 30 Minutes"
        cooldown = "NO COOLDOWN NEEDED - ENTER DIRECTLY"
        sl = round(price - (atr * 1.5), 2)
        tp = round(price + (atr * 2.5), 2)
    elif bear_score >= 80:
        signal = "STRONG SELL"
        accuracy = min(bear_score, 94)
        lot_advice = "✅ SAFE FOR 0.01 LOT SIZE"
        hold_time = "2 Hours 30 Minutes"
        cooldown = "NO COOLDOWN NEEDED - ENTER DIRECTLY"
        sl = round(price + (atr * 1.5), 2)
        tp = round(price - (atr * 2.5), 2)
    elif score >= 60:
        signal = "MODERATE BUY"
        accuracy = 72
        lot_advice = "⚠️ SAFE FOR 0.01 LOT ONLY (STRICT SL)"
        hold_time = "1 Hour 45 Minutes"
        cooldown = "WAIT 15 MINUTES FOR VOLATILITY TO STABILIZE"
        sl = round(price - (atr * 1.2), 2)
        tp = round(price + (atr * 1.8), 2)
    elif bear_score >= 60:
        signal = "MODERATE SELL"
        accuracy = 72
        lot_advice = "⚠️ SAFE FOR 0.01 LOT ONLY (STRICT SL)"
        hold_time = "1 Hour 45 Minutes"
        cooldown = "WAIT 15 MINUTES FOR VOLATILITY TO STABILIZE"
        sl = round(price + (atr * 1.2), 2)
        tp = round(price - (atr * 1.8), 2)
    elif score >= 40:
        signal = "WEAK BUY"
        accuracy = 51
        lot_advice = "⛔ DO NOT ENTER WITH 0.01 LOT - TOO RISKY"
        hold_time = "N/A"
        cooldown = "WAIT 45 MINUTES FOR MARKET TO COOL DOWN"
        sl, tp = "-", "-"
    elif bear_score >= 40:
        signal = "WEAK SELL"
        accuracy = 51
        lot_advice = "⛔ DO NOT ENTER WITH 0.01 LOT - TOO RISKY"
        hold_time = "N/A"
        cooldown = "WAIT 45 MINUTES FOR MARKET TO COOL DOWN"
        sl, tp = "-", "-"
    else:
        signal = "DONT ENTER"
        accuracy = 35
        lot_advice = "⛔ DO NOT ENTER - MARKET CONSOLIDATING"
        hold_time = "N/A"
        cooldown = "WAIT 1 HOUR 30 MINUTES FOR CLEAR BREAKOUT"
        sl, tp = "-", "-"

    return {
        "Price": price, "Signal": signal, "Accuracy": f"{accuracy}%",
        "LotAdvice": lot_advice, "HoldTime": hold_time, "Cooldown": cooldown,
        "SL": sl, "TP": tp, "RSI": round(rsi, 1), "ADX": round(adx, 1),
        "EMA200_Bias": "BULLISH" if price > ema200 else "BEARISH"
    }

LOGIN_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Login | Kemisetso's Gold H1 Robot</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: 'Segoe UI', Tahoma, sans-serif; background: #030712; color: #f8fafc; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }
        .login-card { background: rgba(17, 24, 39, 0.95); padding: 35px; border-radius: 16px; border: 1px solid #374151; width: 90%; max-width: 400px; box-shadow: 0 10px 25px rgba(0,0,0,0.8); }
        h1 { color: #f59e0b; font-size: 22px; text-align: center; margin-bottom: 20px; text-transform: uppercase; letter-spacing: 1px; }
        label { display: block; margin-top: 12px; font-size: 12px; color: #9ca3af; font-weight: 600; }
        input { width: 100%; padding: 12px; margin-top: 5px; box-sizing: border-box; background: #0b0f19; border: 1px solid #374151; color: #fff; border-radius: 8px; }
        button { width: 100%; padding: 14px; margin-top: 22px; background: #f59e0b; border: none; border-radius: 8px; font-weight: bold; color: #030712; cursor: pointer; text-transform: uppercase; }
        .error { background: #dc2626; color: white; padding: 10px; border-radius: 6px; font-size: 12px; text-align: center; margin-bottom: 12px; }
    </style>
</head>
<body>
    <div class="login-card">
        <h1>Gold H1 Command Center</h1>
        {% with messages = get_flashed_messages() %}
          {% if messages %}<div class="error">{{ messages[0] }}</div>{% endif %}
        {% endwith %}
        <form method="POST">
            <label>ID Number:</label>
            <input type="text" name="user_id" required placeholder="069 ...">

            <label>Password:</label>
            <input type="password" name="password" required>

            <label>Admin Name:</label>
            <input type="text" name="admin_name" required>

            <label>Why are you here?</label>
            <input type="text" name="why_here" required>

            <button type="submit">Authenticate Terminal</button>
        </form>
    </div>
</body>
</html>
"""

DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Kemisetso's Gold H1 Robot</title>
    <meta http-equiv="refresh" content="30">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            font-family: 'Segoe UI', monospace;
            margin: 0; padding: 20px;
            color: #f3f4f6;
            background: #030712 url('https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?q=80&w=1920&auto=format&fit=crop') no-repeat center center fixed;
            background-size: cover;
        }
        .overlay { background: rgba(3, 7, 18, 0.88); position: fixed; top: 0; left: 0; right: 0; bottom: 0; z-index: -1; }
        header { display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #f59e0b; padding-bottom: 12px; margin-bottom: 25px; }
        h1 { color: #f59e0b; margin: 0; font-size: 22px; letter-spacing: 1px; }
        .logout-btn { background: #dc2626; color: white; padding: 8px 16px; text-decoration: none; border-radius: 6px; font-size: 12px; font-weight: bold; }
        .card { background: rgba(17, 24, 39, 0.92); border: 1px solid #374151; padding: 20px; border-radius: 12px; max-width: 800px; margin: 0 auto 20px auto; box-shadow: 0 10px 25px rgba(0,0,0,0.6); }
        .badge { padding: 6px 12px; border-radius: 6px; font-weight: bold; font-size: 14px; display: inline-block; }
        .STRONG_BUY, .MODERATE_BUY { background: #16a34a; color: #fff; }
        .STRONG_SELL, .MODERATE_SELL { background: #dc2626; color: #fff; }
        .WEAK_BUY, .WEAK_SELL, .DONT_ENTER { background: #d97706; color: #fff; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-top: 15px; }
        .box { background: #0b0f19; border: 1px solid #1f2937; padding: 12px; border-radius: 8px; font-size: 13px; }
        .box-title { font-size: 11px; color: #9ca3af; text-transform: uppercase; margin-bottom: 4px; }
        .box-value { font-size: 16px; font-weight: bold; color: #f59e0b; }
        .robot-bg { text-align: center; margin-top: 30px; }
        .robot-bg img { width: 140px; opacity: 0.85; filter: drop-shadow(0 0 10px #f59e0b); }
    </style>
</head>
<body>
    <div class="overlay"></div>
    <header>
        <h1>🤖 KEMISETSO GOLD H1 ROBOT</h1>
        <a href="/logout" class="logout-btn">LOCK TERMINAL</a>
    </header>

    <div class="card">
        <h2>GOLD (XAU/USD) - H1 TIMEFRAME ANALYSIS</h2>
        <p><b>Market Price:</b> ${{ data.Price }} | <b>Last Sync:</b> {{ now_str }}</p>
        
        <div style="margin: 15px 0;">
            <span class="badge {{ data.Signal.replace(' ', '_') }}">{{ data.Signal }}</span>
            <span style="margin-left: 10px; font-size: 16px; font-weight: bold; color: #f59e0b;">Accuracy Score: {{ data.Accuracy }}</span>
        </div>

        <div class="grid">
            <div class="box">
                <div class="box-title">0.01 Lot Size Eligibility</div>
                <div>{{ data.LotAdvice }}</div>
            </div>
            <div class="box">
                <div class="box-title">Recommended Hold Duration</div>
                <div class="box-value">{{ data.HoldTime }}</div>
            </div>
            <div class="box">
                <div class="box-title">Market Cooldown / Entry Status</div>
                <div>{{ data.Cooldown }}</div>
            </div>
            <div class="box">
                <div class="box-title">HTF EMA 200 Trend Bias</div>
                <div class="box-value">{{ data.EMA200_Bias }}</div>
            </div>
            <div class="box">
                <div class="box-title">Stop Loss (SL)</div>
                <div class="box-value">{{ data.SL }}</div>
            </div>
            <div class="box">
                <div class="box-title">Take Profit (TP)</div>
                <div class="box-value">{{ data.TP }}</div>
            </div>
        </div>

        <div style="margin-top: 15px; font-size: 12px; color: #9ca3af;">
            Technicals: RSI(14): {{ data.RSI }} | ADX: {{ data.ADX }}
        </div>
    </div>

    <div class="robot-bg">
        <img src="https://cdn-icons-png.flaticon.com/512/4712/4712109.png" alt="Robot Core">
        <p style="font-size: 11px; color: #6b7280; margin-top: 5px;">POWERED BY {{ brand }} AUTOMATION CORE</p>
    </div>
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
    df = fetch_h1_gold_data()
    
    if df is not None:
        analysis = analyze_h1_gold(df)
    else:
        analysis = {
            "Price": "N/A", "Signal": "DONT ENTER", "Accuracy": "0%",
            "LotAdvice": "DATA FETCH ERROR", "HoldTime": "N/A",
            "Cooldown": "TRY AGAIN IN 1 MINUTE", "SL": "-", "TP": "-",
            "RSI": "N/A", "ADX": "N/A", "EMA200_Bias": "N/A"
        }

    return render_template_string(DASHBOARD_HTML, data=analysis, now_str=now_str, brand=FOOTER_BRAND)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
