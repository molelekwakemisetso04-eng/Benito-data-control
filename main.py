import os
from flask import Flask, render_template_string
import requests

app = Flask(__name__)

# Insert your real API key from the-odds-api.com below
API_KEY = os.environ.get('ODDS_API_KEY', '8b2fbbdc39c3e6a9ee855ffb9202968a')

LEAGUES = [
    'soccer_epl', 
    'soccer_spain_la_liga', 
    'soccer_italy_serie_a', 
    'soccer_germany_bundesliga', 
    'soccer_france_ligue_one'
]

def calculate_no_vig_fair_prob(outcomes):
    """
    Calculates fair probabilities by removing the bookmaker overround (vig).
    """
    raw_implied_probs = [1.0 / o['price'] for o in outcomes]
    total_margin = sum(raw_implied_probs)
    # De-vig multiplicative normalization
    fair_probs = [p / total_margin for p in raw_implied_probs]
    return fair_probs, total_margin

def fetch_positive_ev_bets():
    positive_ev_picks = []
    
    if API_KEY == '8b2fbbdc39c3e6a9ee855ffb9202968a':
        return []

    for league in LEAGUES:
        url = f'https://api.the-odds-api.com/v4/sports/{league}/odds/?apiKey={8b2fbbdc39c3e6a9ee855ffb9202968a}&regions=eu&markets=h2h'
        try:
            res = requests.get(url, timeout=5)
            if res.status_code == 200:
                data = res.json()
                for match in data:
                    home = match.get('home_team')
                    away = match.get('away_team')
                    bookmakers = match.get('bookmakers', [])
                    
                    if len(bookmakers) < 2:
                        continue # Need multiple bookmakers to establish a consensus fair market
                        
                    # 1. Establish Sharp/Consensus Fair Odds across bookmakers
                    all_home_odds, all_draw_odds, all_away_odds = [], [], []
                    for bm in bookmakers:
                        for m in bm.get('markets', []):
                            if m['key'] == 'h2h':
                                for o in m['outcomes']:
                                    if o['name'] == home: all_home_odds.append(o['price'])
                                    elif o['name'] == away: all_away_odds.append(o['price'])
                                    elif o['name'] == 'Draw': all_draw_odds.append(o['price'])

                    if not all_home_odds or not all_draw_odds:
                        continue

                    # Average market price across books
                    avg_home = sum(all_home_odds) / len(all_home_odds)
                    avg_draw = sum(all_draw_odds) / len(all_draw_odds)
                    avg_away = sum(all_away_odds) / len(all_away_odds) if all_away_odds else 3.50

                    # Compute de-vigged fair probabilities from market consensus
                    fair_probs, vig = calculate_no_vig_fair_prob([
                        {'price': avg_home}, {'price': avg_draw}, {'price': avg_away}
                    ])

                    outcomes_map = [
                        (home, avg_home, fair_probs[0]),
                        ('Draw', avg_draw, fair_probs[1]),
                        (away, avg_away, fair_probs[2])
                    ]

                    # 2. Find Soft Bookmaker mispricings against consensus fair probability
                    for bm in bookmakers:
                        bm_name = bm['title']
                        for m in bm.get('markets', []):
                            if m['key'] == 'h2h':
                                for o in m['outcomes']:
                                    # Find matching outcome
                                    target = next((item for item in outcomes_map if item[0] == o['name']), None)
                                    if not target: continue
                                    
                                    price = o['price']
                                    fair_prob = target[2]
                                    
                                    # Expected Value Calculation
                                    ev = (price * fair_prob) - 1.0
                                    
                                    # Fractional Kelly Criterion (0.25 Quarter Kelly)
                                    # Kelly % = EV / (Odds - 1)
                                    if ev > 0.01: # Filter for +1% EV or higher
                                        raw_kelly = ev / (price - 1.0)
                                        quarter_kelly_pct = round(raw_kelly * 0.25 * 100, 2)
                                        
                                        positive_ev_picks.append({
                                            'home': home,
                                            'away': away,
                                            'pick': o['name'],
                                            'bookmaker': bm_name,
                                            'odds': price,
                                            'fair_prob': round(fair_prob * 100, 1),
                                            'ev_pct': round(ev * 100, 2),
                                            'kelly_pct': min(quarter_kelly_pct, 5.0), # Cap max single stake at 5% of bankroll
                                            'league': league.replace('soccer_', '').replace('_', ' ').title()
                                        })
        except Exception as e:
            print(f"Error processing {league}: {e}")

    # Return top value bets sorted by highest Expected Value percentage
    return sorted(positive_ev_picks, key=lambda x: x['ev_pct'], reverse=True)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>+EV Value Betting Dashboard</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { background: #0f172a; color: #ffffff; font-family: sans-serif; padding: 15px; margin: 0; }
        .container { max-width: 600px; margin: 0 auto; }
        .banner { background: linear-gradient(135deg, #1e3a8a, #1e40af); padding: 18px; text-align: center; border-radius: 12px; margin-bottom: 20px; }
        .banner h2 { margin: 0; font-size: 1.3rem; color: #60a5fa; }
        
        .bankroll-box { background: #1e293b; padding: 15px; border-radius: 10px; border: 1px solid #334155; margin-bottom: 20px; }
        label { display: block; font-size: 0.85rem; color: #94a3b8; margin-bottom: 5px; font-weight: bold; }
        input[type="number"] { width: 100%; padding: 10px; background: #0f172a; border: 1px solid #475569; color: #fff; border-radius: 6px; box-sizing: border-box; }

        .card { background: #1e293b; border: 1px solid #334155; border-radius: 10px; padding: 14px; margin-bottom: 12px; }
        .team-name { color: #38bdf8; font-weight: bold; }
        .ev-tag { background: #15803d; color: #fff; padding: 2px 6px; border-radius: 4px; font-weight: bold; font-size: 0.8em; float: right; }
        .odds { color: #facc15; font-weight: bold; }
        .stake-val { color: #4ade80; font-weight: bold; }
        .strategy-note { background: #312e81; border: 1px solid #6366f1; padding: 12px; border-radius: 8px; font-size: 0.85rem; margin-bottom: 20px; line-height: 1.4; }
    </style>
</head>
<body>

    <div class="container">
        <div class="banner">
            <h2>🎯 SHARP VALUE BETTING ENGINE</h2>
            <div style="color: #cbd5e1; font-size: 0.85rem; margin-top: 4px;">De-vigged Fair Odds & Kelly Criterion Staking</div>
        </div>

        <div class="strategy-note">
            <strong>🛡️ Risk Mitigation Strategy:</strong> Accumulators removed. Place these selections strictly as <strong>Singles</strong> or <strong>Small Doubles (2 Legs max)</strong>. Bet sizes are auto-calculated using Quarter-Kelly bankroll management.
        </div>

        <div class="bankroll-box">
            <label>YOUR TOTAL BANKROLL (R)</label>
            <input type="number" id="bankrollInput" value="1000" step="100" min="100" oninput="renderPicks()">
        </div>

        <h3 id="sectionTitle">Top Expected Value (+EV) Opportunities</h3>

        <div id="matchList"></div>
    </div>

    <script>
        const PICKS = {{ picks|tojson }};

        function renderPicks() {
            const bankroll = parseFloat(document.getElementById('bankrollInput').value) || 1000;
            const container = document.getElementById('matchList');
            container.innerHTML = '';

            if (!PICKS || PICKS.length === 0) {
                container.innerHTML = '<p style="text-align:center; color:#94a3b8;">No +EV edge opportunities found in live market right now. Check back when markets update.</p>';
                return;
            }

            PICKS.slice(0, 15).forEach((m, idx) => {
                const stakeAmount = (bankroll * (m.kelly_pct / 100)).toFixed(2);
                const card = document.createElement('div');
                card.className = 'card';
                card.innerHTML = `
                    <span class="ev-tag">+${m.ev_pct}% EV</span>
                    <div><span class="team-name">#${idx + 1} ${m.pick}</span> <small style="color:#94a3b8;">(${m.league})</small></div>
                    <div style="color: #cbd5e1; margin: 6px 0; font-size: 0.85em;">Match: ${m.home} vs ${m.away}</div>
                    <div style="font-size: 0.85em; margin-bottom: 6px;">
                        Bookmaker: <strong>${m.bookmaker}</strong> | Odds: <span class="odds">${m.odds.toFixed(2)}</span>
                    </div>
                    <div style="font-size: 0.8em; color: #94a3b8; border-top: 1px solid #334155; padding-top: 6px; margin-top: 6px;">
                        Fair Win Prob: ${m.fair_prob}% | Recommended Stake: <span class="stake-val">R${stakeAmount}</span> (${m.kelly_pct}% of bankroll)
                    </div>
                `;
                container.appendChild(card);
            });
        }

        renderPicks();
    </script>

</body>
</html>
"""

@app.route('/')
def home():
    ev_picks = fetch_positive_ev_bets()
    return render_template_string(HTML_TEMPLATE, picks=ev_picks)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
