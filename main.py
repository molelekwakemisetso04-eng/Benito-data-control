from flask import Flask, render_template_string

app = Flask(__name__)

# Expanded database with 33 realistic fixtures
FIXTURES_DB = [
    # TODAY FIXTURES
    {"date": "today", "home": "Mamelodi Sundowns", "away": "Siwelele", "straight": "Mamelodi Sundowns", "market": "Straight Win (1)", "odds": 1.25, "prob": 88.5, "league": "Betway Prem"},
    {"date": "today", "home": "Real Madrid", "away": "Getafe", "straight": "Real Madrid", "market": "Straight Win (1)", "odds": 1.30, "prob": 86.2, "league": "La Liga"},
    {"date": "today", "home": "Bayern Munich", "away": "Augsburg", "straight": "Bayern Munich", "market": "Over 2.5 Goals", "odds": 1.35, "prob": 85.0, "league": "Bundesliga"},
    {"date": "today", "home": "Arsenal", "away": "Southampton", "straight": "Arsenal", "market": "Straight Win (1)", "odds": 1.28, "prob": 83.4, "league": "EPL"},
    {"date": "today", "home": "PSG", "away": "Nantes", "straight": "PSG", "market": "Straight Win (1)", "odds": 1.32, "prob": 82.1, "league": "Ligue 1"},
    {"date": "today", "home": "Manchester City", "away": "Leicester City", "straight": "Manchester City", "market": "Straight Win (1)", "odds": 1.22, "prob": 81.5, "league": "EPL"},
    {"date": "today", "home": "Inter Milan", "away": "Empoli", "straight": "Inter Milan", "market": "Straight Win (1)", "odds": 1.27, "prob": 80.9, "league": "Serie A"},
    {"date": "today", "home": "Sporting CP", "away": "Boavista", "straight": "Sporting CP", "market": "Straight Win (1)", "odds": 1.20, "prob": 80.2, "league": "Primeira Liga"},
    {"date": "today", "home": "PSV Eindhoven", "away": "Breda", "straight": "PSV Eindhoven", "market": "Over 2.5 Goals", "odds": 1.30, "prob": 79.5, "league": "Eredivisie"},
    {"date": "today", "home": "Celtic", "away": "Kilmarnock", "straight": "Celtic", "market": "Straight Win (1)", "odds": 1.18, "prob": 79.0, "league": "Scottish Premiership"},
    {"date": "today", "home": "Atlético Madrid", "away": "Rayo Vallecano", "straight": "Atlético Madrid", "market": "Straight Win (1)", "odds": 1.40, "prob": 78.4, "league": "La Liga"},

    # TOMORROW FIXTURES
    {"date": "tomorrow", "home": "Stellenbosch", "away": "Sekhukhune", "straight": "Stellenbosch", "market": "Double Chance (1X)", "odds": 1.22, "prob": 81.0, "league": "Betway Prem"},
    {"date": "tomorrow", "home": "Barcelona", "away": "Las Palmas", "straight": "Barcelona", "market": "Over 1.5 Goals", "odds": 1.20, "prob": 80.5, "league": "La Liga"},
    {"date": "tomorrow", "home": "Liverpool", "away": "Ipswich", "straight": "Liverpool", "market": "Straight Win (1)", "odds": 1.35, "prob": 79.8, "league": "EPL"},
    {"date": "tomorrow", "home": "Leverkusen", "away": "Bochum", "straight": "Leverkusen", "market": "Over 2.5 Goals", "odds": 1.40, "prob": 78.9, "league": "Bundesliga"},
    {"date": "tomorrow", "home": "Chelsea", "away": "Everton", "straight": "Chelsea", "market": "Straight Win (1)", "odds": 1.42, "prob": 77.5, "league": "EPL"},
    {"date": "tomorrow", "home": "Benfica", "away": "Farense", "straight": "Benfica", "market": "Straight Win (1)", "odds": 1.25, "prob": 77.1, "league": "Primeira Liga"},
    {"date": "tomorrow", "home": "Napoli", "away": "Monza", "straight": "Napoli", "market": "Straight Win (1)", "odds": 1.38, "prob": 76.8, "league": "Serie A"},
    {"date": "tomorrow", "home": "Monaco", "away": "Angers", "straight": "Monaco", "market": "Over 1.5 Goals", "odds": 1.22, "prob": 76.2, "league": "Ligue 1"},
    {"date": "tomorrow", "home": "Ajax", "away": "Willem II", "straight": "Ajax", "market": "Straight Win (1)", "odds": 1.32, "prob": 75.8, "league": "Eredivisie"},
    {"date": "tomorrow", "home": "Feyenoord", "away": "Zwolle", "straight": "Feyenoord", "market": "Straight Win (1)", "odds": 1.28, "prob": 75.3, "league": "Eredivisie"},

    # UPCOMING FIXTURES
    {"date": "upcoming", "home": "Kaizer Chiefs", "away": "AmaZulu", "straight": "Kaizer Chiefs", "market": "Straight Win (1)", "odds": 1.45, "prob": 76.8, "league": "Betway Prem"},
    {"date": "upcoming", "home": "Juventus", "away": "Venezia", "straight": "Juventus", "market": "Straight Win (1)", "odds": 1.45, "prob": 75.9, "league": "Serie A"},
    {"date": "upcoming", "home": "Orlando Pirates", "away": "Durban City", "straight": "Orlando Pirates", "market": "Straight Win (1)", "odds": 1.38, "prob": 75.2, "league": "Betway Prem"},
    {"date": "upcoming", "home": "AC Milan", "away": "Genoa", "straight": "AC Milan", "market": "Straight Win (1)", "odds": 1.42, "prob": 74.8, "league": "Serie A"},
    {"date": "upcoming", "home": "Tottenham", "away": "Bournemouth", "straight": "Tottenham", "market": "Over 2.5 Goals", "odds": 1.48, "prob": 74.1, "league": "EPL"},
    {"date": "upcoming", "home": "Dortmund", "away": "Mainz", "straight": "Dortmund", "market": "Straight Win (1)", "odds": 1.36, "prob": 73.6, "league": "Bundesliga"},
    {"date": "upcoming", "home": "Porto", "away": "Rio Ave", "straight": "Porto", "market": "Straight Win (1)", "odds": 1.26, "prob": 73.2, "league": "Primeira Liga"},
    {"date": "upcoming", "home": "Atalanta", "away": "Cagliari", "straight": "Atalanta", "market": "Over 1.5 Goals", "odds": 1.24, "prob": 72.8, "league": "Serie A"},
    {"date": "upcoming", "home": "Lille", "away": "Le Havre", "straight": "Lille", "market": "Straight Win (1)", "odds": 1.40, "prob": 72.3, "league": "Ligue 1"},
    {"date": "upcoming", "home": "Aston Villa", "away": "Wolves", "straight": "Aston Villa", "market": "Straight Win (1)", "odds": 1.50, "prob": 71.9, "league": "EPL"},
    {"date": "upcoming", "home": "Real Sociedad", "away": "Mallorca", "straight": "Real Sociedad", "market": "Double Chance (1X)", "odds": 1.22, "prob": 71.2, "league": "La Liga"},
    {"date": "upcoming", "home": "SuperSport Utd", "away": "Polokwane City", "straight": "SuperSport Utd", "market": "Double Chance (1X)", "odds": 1.25, "prob": 70.8, "league": "Betway Prem"}
]

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Kemisetso's Betway Predictor</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { 
            background: #0f172a; 
            color: #ffffff; 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            padding: 15px; 
            margin: 0; 
            position: relative;
            overflow-x: hidden;
        }

        /* Floating Money Background Effect */
        .money-bg {
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            pointer-events: none;
            z-index: 0;
            opacity: 0.12;
            font-size: 2.5rem;
            display: flex;
            flex-wrap: wrap;
            justify-content: space-around;
            align-content: space-around;
        }

        .container { position: relative; z-index: 1; max-width: 600px; margin: 0 auto; }

        .banner { 
            background: linear-gradient(135deg, #15803d, #166534); 
            padding: 20px; 
            text-align: center; 
            border-radius: 12px; 
            box-shadow: 0 4px 15px rgba(0,0,0,0.5);
            margin-bottom: 20px; 
        }
        .banner h2 { margin: 0; font-size: 1.5rem; color: #ffffff; letter-spacing: 1px; }
        .author { color: #fde047; font-weight: bold; margin-top: 6px; font-size: 0.95rem; }

        /* Control Panel Styles */
        .controls {
            background: #1e293b;
            padding: 15px;
            border-radius: 10px;
            border: 1px solid #334155;
            margin-bottom: 20px;
        }
        .control-group { margin-bottom: 12px; }
        .control-group:last-child { margin-bottom: 0; }
        label { display: block; font-size: 0.85rem; color: #94a3b8; margin-bottom: 5px; font-weight: bold; }
        
        .btn-group { display: flex; gap: 8px; }
        .btn {
            flex: 1;
            padding: 8px 12px;
            background: #0f172a;
            border: 1px solid #475569;
            color: #fff;
            border-radius: 6px;
            cursor: pointer;
            font-weight: bold;
            font-size: 0.85rem;
        }
        .btn.active { background: #22c55e; border-color: #22c55e; color: #000; }

        select, input[type="number"] {
            width: 100%;
            padding: 10px;
            background: #0f172a;
            border: 1px solid #475569;
            color: #fff;
            border-radius: 6px;
            box-sizing: border-box;
            font-size: 0.95rem;
        }

        /* Match Cards */
        .card { 
            background: #1e293b; 
            border: 1px solid #334155; 
            border-radius: 10px; 
            padding: 14px; 
            margin-bottom: 12px; 
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        }
        .team-name { color: #38bdf8; font-size: 1.1em; font-weight: bold; }
        .league-tag { color: #94a3b8; font-size: 0.8em; margin-left: 5px; }
        .market { color: #4ade80; font-weight: bold; }
        .odds { color: #facc15; font-weight: bold; }

        /* Payout Box */
        .payout-box { 
            background: linear-gradient(135deg, #451a03, #290f02); 
            border: 2px solid #facc15; 
            padding: 18px; 
            border-radius: 12px; 
            text-align: center; 
            margin-top: 25px; 
            box-shadow: 0 4px 20px rgba(250, 204, 21, 0.2);
        }
        .payout-box h3 { margin-top: 0; color: #facc15; }
        .payout-val { color: #4ade80; font-weight: bold; font-size: 1.4em; }
    </style>
</head>
<body>

    <div class="money-bg">
        💵 💸 💵 💸 💵 💸 💵 💸
        💸 💵 💸 💵 💸 💵 💸 💵
        💵 💸 💵 💸 💵 💸 💵 💸
        💸 💵 💸 💵 💸 💵 💸 💵
    </div>

    <div class="container">
        <div class="banner">
            <h2>💵 BETWAY SELECTOR DASHBOARD 💵</h2>
            <div class="author">Developed by: Kemisetso</div>
        </div>

        <div class="controls">
            <div class="control-group">
                <label>1. FILTER BY DATE</label>
                <div class="btn-group">
                    <button class="btn active" onclick="setFilter('all', this)">ALL</button>
                    <button class="btn" onclick="setFilter('today', this)">TODAY</button>
                    <button class="btn" onclick="setFilter('tomorrow', this)">TOMORROW</button>
                </div>
            </div>

            <div class="control-group" style="margin-top: 12px;">
                <label>2. SELECT NUMBER OF PICKS</label>
                <select id="pickCount" onchange="renderMatches()">
                    <option value="8">Top 8 Picks</option>
                    <option value="20" selected>Top 20 Picks</option>
                    <option value="33">Top 33 Picks (All)</option>
                </select>
            </div>

            <div class="control-group" style="margin-top: 12px;">
                <label>3. STAKE AMOUNT (R)</label>
                <input type="number" id="stakeInput" value="1.00" step="0.50" min="1" oninput="renderMatches()">
            </div>
        </div>

        <h3 id="sectionTitle">Top Predictions</h3>

        <div id="matchList"></div>

        <div class="payout-box">
            <h3>💰 ESTIMATED PAYOUT 💰</h3>
            <p>Total Selected Teams: <strong id="outTeams">0</strong></p>
            <p>Combined Multiplier: <span class="odds" id="outOdds">1.00x</span></p>
            <p>Potential Return: <span class="payout-val" id="outPayout">R0.00</span></p>
        </div>
    </div>

    <script>
        const FIXTURES = {{ fixtures|tojson }};
        let currentDateFilter = 'all';

        function setFilter(filter, btn) {
            currentDateFilter = filter;
            document.querySelectorAll('.btn-group .btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            renderMatches();
        }

        function renderMatches() {
            const count = parseInt(document.getElementById('pickCount').value);
            const stake = parseFloat(document.getElementById('stakeInput').value) || 1.00;
            
            let filtered = FIXTURES;
            if (currentDateFilter !== 'all') {
                filtered = FIXTURES.filter(f => f.date === currentDateFilter);
            }

            let sorted = filtered.sort((a, b) => b.prob - a.prob).slice(0, count);

            const container = document.getElementById('matchList');
            container.innerHTML = '';

            let totalOdds = 1.0;

            sorted.forEach((m, idx) => {
                totalOdds *= m.odds;
                const card = document.createElement('div');
                card.className = 'card';
                card.innerHTML = `
                    <div><span class="team-name">#${idx + 1} ${m.straight.toUpperCase()}</span> <span class="league-tag">(${m.league})</span></div>
                    <div style="color: #cbd5e1; margin: 6px 0; font-size: 0.9em;">Match: ${m.home} vs ${m.away}</div>
                    <div style="font-size: 0.9em;">Best Bet: <span class="market">${m.market}</span> @ Odds: <span class="odds">${m.odds.toFixed(2)}</span></div>
                    <div style="font-size: 0.8em; color: #64748b; margin-top: 4px;">Win Confidence: ${m.prob}%</div>
                `;
                container.appendChild(card);
            });

            const payout = totalOdds * stake;

            document.getElementById('sectionTitle').innerText = `Top Predictions (${sorted.length} Teams)`;
            document.getElementById('outTeams').innerText = sorted.length;
            document.getElementById('outOdds').innerText = totalOdds.toFixed(2) + 'x';
            document.getElementById('outPayout').innerText = 'R' + payout.toLocaleString('en-ZA', {minimumFractionDigits: 2, maximumFractionDigits: 2});
        }

        // Initial render on page load
        renderMatches();
    </script>

</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE, fixtures=FIXTURES_DB)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
