from flask import Flask, render_template_string, request

app = Flask(__name__)

FIXTURES_DB = [
    # TODAY FIXTURES
    {"date": "today", "home": "Mamelodi Sundowns", "away": "Siwelele", "straight": "Mamelodi Sundowns", "market": "Straight Win (1)", "odds": 1.25, "prob": 88.5, "league": "Betway Prem"},
    {"date": "today", "home": "Real Madrid", "away": "Getafe", "straight": "Real Madrid", "market": "Straight Win (1)", "odds": 1.30, "prob": 86.2, "league": "La Liga"},
    {"date": "today", "home": "Bayern Munich", "away": "Augsburg", "straight": "Bayern Munich", "market": "Over 2.5 Goals", "odds": 1.35, "prob": 85.0, "league": "Bundesliga"},
    {"date": "today", "home": "Arsenal", "away": "Southampton", "straight": "Arsenal", "market": "Straight Win (1)", "odds": 1.28, "prob": 83.4, "league": "EPL"},
    {"date": "today", "home": "PSG", "away": "Nantes", "straight": "PSG", "market": "Straight Win (1)", "odds": 1.32, "prob": 82.1, "league": "Ligue 1"},
    
    # TOMORROW FIXTURES
    {"date": "tomorrow", "home": "Stellenbosch", "away": "Sekhukhune", "straight": "Stellenbosch", "market": "Double Chance (1X)", "odds": 1.22, "prob": 81.0, "league": "Betway Prem"},
    {"date": "tomorrow", "home": "Barcelona", "away": "Las Palmas", "straight": "Barcelona", "market": "Over 1.5 Goals", "odds": 1.20, "prob": 80.5, "league": "La Liga"},
    {"date": "tomorrow", "home": "Liverpool", "away": "Ipswich", "straight": "Liverpool", "market": "Straight Win (1)", "odds": 1.35, "prob": 79.8, "league": "EPL"},
    {"date": "tomorrow", "home": "Leverkusen", "away": "Bochum", "straight": "Leverkusen", "market": "Over 2.5 Goals", "odds": 1.40, "prob": 78.9, "league": "Bundesliga"},

    # UPCOMING FIXTURES
    {"date": "upcoming", "home": "Kaizer Chiefs", "away": "AmaZulu", "straight": "Kaizer Chiefs", "market": "Straight Win (1)", "odds": 1.45, "prob": 76.8, "league": "Betway Prem"},
    {"date": "upcoming", "home": "Juventus", "away": "Venezia", "straight": "Juventus", "market": "Straight Win (1)", "odds": 1.45, "prob": 75.9, "league": "Serie A"},
    {"date": "upcoming", "home": "Orlando Pirates", "away": "Durban City", "straight": "Orlando Pirates", "market": "Straight Win (1)", "odds": 1.38, "prob": 75.2, "league": "Betway Prem"},
]

# Generate additional fixtures dynamically up to 33 teams
for i in range(13, 34):
    FIXTURES_DB.append({
        "date": "upcoming", "home": f"Team Alpha {i}", "away": f"Team Beta {i}",
        "straight": f"Team Alpha {i}", "market": "Straight Win (1)",
        "odds": round(1.20 + (i * 0.01), 2), "prob": round(75.0 - (i * 0.4), 1), "league": "Global Top Tier"
    })

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Kemisetso's Betway Predictor</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { background-color: #121212; color: #ffffff; font-family: Arial, sans-serif; padding: 15px; margin: 0; }
        .banner { background-color: #2e7d32; padding: 15px; text-align: center; border-radius: 8px; margin-bottom: 20px; }
        .banner h2 { margin: 0; color: #ffffff; }
        .author { color: #ffd54f; font-weight: bold; margin-top: 5px; }
        .card { background-color: #1e1e1e; border: 1px solid #333; border-radius: 8px; padding: 12px; margin-bottom: 12px; }
        .team-name { color: #4fc3f7; font-size: 1.1em; font-weight: bold; }
        .market { color: #81c784; font-weight: bold; }
        .odds { color: #ffd54f; font-weight: bold; }
        .payout-box { background-color: #332900; border: 1px solid #ffd54f; padding: 15px; border-radius: 8px; text-align: center; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="banner">
        <h2>💵 BETWAY SELECTOR DASHBOARD 💵</h2>
        <div class="author">Developed by: Kemisetso</div>
    </div>

    <h3>Top Predictions ({{ matches|length }} Teams)</h3>

    {% for m in matches %}
    <div class="card">
        <div><span class="team-name">#{{ loop.index }} {{ m.straight|upper }}</span> ({{ m.league }})</div>
        <div style="color: #aaa; margin: 5px 0;">Match: {{ m.home }} vs {{ m.away }}</div>
        <div>Best Bet: <span class="market">{{ m.market }}</span> @ Odds: <span class="odds">{{ m.odds }}</span></div>
        <div style="font-size: 0.85em; color: #888;">Win Confidence: {{ m.prob }}%</div>
    </div>
    {% endfor %}

    <div class="payout-box">
        <h3>💰 ESTIMATED PAYOUT 💰</h3>
        <p>Total Selected Teams: <strong>{{ matches|length }}</strong></p>
        <p>Combined Multiplier: <span class="odds">{{ total_odds }}x</span></p>
        <p>Potential Return on R1.00: <span style="color: #81c784; font-weight: bold; font-size: 1.2em;">R{{ payout }}</span></p>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    count = int(request.args.get('count', 20))
    sorted_matches = sorted(FIXTURES_DB, key=lambda x: x["prob"], reverse=True)[:count]
    
    total_odds = 1.0
    for match in sorted_matches:
        total_odds *= match["odds"]
    
    payout = round(total_odds * 1.00, 2)
    
    return render_template_string(
        HTML_TEMPLATE, 
        matches=sorted_matches, 
        total_odds=round(total_odds, 2), 
        payout=payout
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
