import datetime

# --- COLOR CODES FOR TERMUX / TERMINAL ---
GREEN_BG = "\033[42m\033[30m"
CYAN_BG = "\033[46m\033[30m"
YELLOW_BG = "\033[43m\033[30m"
BOLD = "\033[1m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"

HEADER = f"{CYAN}=================================================={RESET}"
FOOTER = f"{CYAN}=================================================={RESET}"
AUTHOR = f"{BOLD}{YELLOW}Developed by: Kemisetso{RESET}"

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

# Fill up to 33 teams dynamically
for i in range(13, 34):
    FIXTURES_DB.append({
        "date": "upcoming", "home": f"Team Alpha {i}", "away": f"Team Beta {i}",
        "straight": f"Team Alpha {i}", "market": "Straight Win (1)",
        "odds": round(1.20 + (i * 0.01), 2), "prob": round(75.0 - (i * 0.4), 1), "league": "Global Top Tier"
    })

def print_money_banner():
    print(f"{GREEN} 💵 💵 💵 💵 💵 💵 💵 💵 💵 💵 💵 💵 💵 💵 💵 💵 💵 💵 💵 💵 {RESET}")
    print(f"{GREEN_BG}             BETWAY SELECTOR & PAYOUT CALCULATOR            {RESET}")
    print(f"{GREEN} 💵 💵 💵 💵 💵 💵 💵 💵 💵 💵 💵 💵 💵 💵 💵 💵 💵 💵 💵 💵 {RESET}")

def calculate_returns(selected_matches, stake=1.00):
    total_odds = 1.0
    for match in selected_matches:
        total_odds *= match["odds"]
    possible_payout = total_odds * stake
    return round(total_odds, 2), round(possible_payout, 2)

def main():
    print_money_banner()
    print(f"                     {AUTHOR}\n")
    
    print(f"{BOLD}[1] Select Date Filter:{RESET}")
    print(" 1 - Today's Matches")
    print(" 2 - Tomorrow's Matches")
    print(" 3 - Upcoming Matches (All)")
    date_choice = input("Enter choice (1, 2, or 3): ").strip()
    
    date_map = {"1": "today", "2": "tomorrow", "3": "upcoming"}
    selected_date = date_map.get(date_choice, "upcoming")

    print(f"\n{BOLD}[2] Select Number of Picks:{RESET}")
    count_input = input("Enter count (8, 20, 33): ").strip()
    
    try:
        count = int(count_input)
    except ValueError:
        count = 20

    filtered = [f for f in FIXTURES_DB if f["date"] == selected_date or selected_date == "upcoming"]
    sorted_matches = sorted(filtered, key=lambda x: x["prob"], reverse=True)[:count]

    print(f"\n{HEADER}")
    print(f"{CYAN_BG}    TOP {len(sorted_matches)} TEAM LEADERBOARD ({selected_date.upper()})    {RESET}")
    print(f"{HEADER}")
    
    for rank, m in enumerate(sorted_matches, 1):
        print(f"{BOLD}{rank:02d}. {m['straight'].upper()}{RESET}")
        print(f"    League: {m['league']} | Match: {m['home']} vs {m['away']}")
        print(f"    Best Bet Market: {GREEN}{m['market']}{RESET} @ Odds: {YELLOW}{m['odds']}{RESET}")
        print(f"    Win Confidence: {m['prob']}%")
        print("-" * 50)

    total_odds, payout = calculate_returns(sorted_matches, stake=1.00)
    
    print(f"\n{HEADER}")
    print(f"{YELLOW_BG}           💰 ESTIMATED PAYOUT CALCULATION 💰         {RESET}")
    print(f"{HEADER}")
    print(f" Total Selected Teams: {BOLD}{len(sorted_matches)}{RESET}")
    print(f" Stake Amount: {BOLD}R1.00{RESET}")
    print(f" Combined Odds Multiplier: {YELLOW}{total_odds}x{RESET}")
    print(f" Potential Return: {GREEN_BG} R{payout} {RESET}")
    print(HEADER)
    print(f"{AUTHOR}\n{HEADER}")

if __name__ == "__main__":
    main()
