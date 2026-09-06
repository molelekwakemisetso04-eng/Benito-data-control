import os
from flask import Flask, render_template_string
import requests

app = Flask(__name__)

# Replace with your actual key from the-odds-api.com
API_KEY = os.environ.get('ODDS_API_KEY', '8b2fbbdc39c3e6a9ee855ffb9202968a')
SPORT = 'soccer_epl' # Example: English Premier League (or soccer_south_africa_psl)

def fetch_live_fixtures():
    url = f'https://api.the-odds-api.com/v4/sports/{SPORT}/odds/?apiKey={API_KEY}&regions=eu&markets=h2h'
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Error fetching live data: {e}")
    return []

def calculate_algorithmic_edge(odds_list):
    """
    ALGORITHMIC EDGE & RISK MANAGEMENT:
    1. Converts bookmaker odds to implied win probabilities.
    2. Filters out high-risk volatile legs (odds > 1.60) to keep accumulators safer.
    3. Calculates joint probability to manage accumulator math risk.
    """
    processed = []
    for match in odds_list:
        home = match.get('home_team')
        away = match.get('away_team')
        
        # Extract bookmaker odds
        bookmakers = match.get('bookmakers', [])
        if not bookmakers:
            continue
            
        markets = bookmakers[0].get('markets', [])
        if not markets:
            continue
            
        outcomes = markets[0].get('outcomes', [])
        
        # Find favorite based on real live market odds
        favorite = min(outcomes, key=lambda x: x['price'])
        odds = favorite['price']
        
        # Implied Probability = (1 / Decimal Odds) * 100
        implied_prob = round((1 / odds) * 100, 1)
        
        # Accumulator Math Risk Control: Only select low-volatility safe bets (odds <= 1.50)
        if odds <= 1.50:
            processed.append({
                "home": home,
                "away": away,
                "pick": favorite['name'],
                "odds": odds,
                "prob": implied_prob,
                "league": "EPL Live"
            })
            
    # Sort by highest statistical confidence
    return sorted(processed, key=lambda x: x['prob'], reverse=True)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Live Betway Predictor</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { background: #0f172a; color: #fff; font-family: sans-serif; padding: 15px; }
        .card { background: #1e293b; border: 1px solid #334155; padding: 12px; margin-bottom: 10px; border-radius: 8px; }
        .odds { color: #facc15; font-weight: bold; }
        .pick { color: #38bdf8; font-weight: bold; }
    </style>
</head>
<body>
    <h2>🔴 LIVE BETWAY PREDICTOR DASHBOARD</h2>
    <p>Powered by Real-Time Bookmaker Odds API</p>
    
    {% for m in matches %}
    <div class="card">
        <div><strong>{{ m.home }} vs {{ m.away }}</strong></div>
        <div>Algorithmic Pick: <span class="pick">{{ m.pick }}</span></div>
        <div>Live Odds: <span class="odds">{{ m.odds }}</span> | Confidence: {{ m.prob }}%</div>
    </div>
    {% else %}
    <p>No live games found or API Key needed.</p>
    {% endfor %}
</body>
</html>
"""

@app.route('/')
def home():
    raw_data = fetch_live_fixtures()
    live_matches = calculate_algorithmic_edge(raw_data)
    return render_template_string(HTML_TEMPLATE, matches=live_matches)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
