import os
import sys
import json
import requests

# Ensure path to nest root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stats.data import get_auth, get_config
from Predict.predict_win_loss import predict_match_outcome

def fetch_match_schedule(event_code, auth, season):
    """Fetch the complete match schedule (including team info) from API"""
    url = f"https://ftc-api.firstinspires.org/v2.0/{season}/matches/{event_code}?tournamentLevel=qual"
    response = requests.get(url, auth=auth)
    if response.status_code != 200:
        print(f"Failed to fetch schedule for {event_code}. Code: {response.status_code}")
        return []
    return response.json().get('matches', [])

def main():
    season = 2025
    event_code = "CAABCMP"
    auth = get_auth()
    
    # Load Data from JSON
    data_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "CAABCMP9-26.json")
    if not os.path.exists(data_file):
        print(f"Error: Data file {data_file} not found.")
        return

    with open(data_file, 'r') as f:
        teams_data = json.load(f)

    # Fetch official schedule
    print(f"Fetching schedule for {event_code}...")
    schedule = fetch_match_schedule(event_code, auth, season)
    if not schedule:
        print("No schedule found. Prediction aborted.")
        return

    # Initialize Standings
    # standings = { team_num: {"RP": 0, "Score": 0, "Wins": 0, "Losses": 0, "Ties": 0, "GP": 0} }
    standings = {}
    for t_num in teams_data.keys():
        standings[int(t_num)] = {"RP": 0, "Score": 0, "Wins": 0, "Losses": 0, "Ties": 0, "Matches": 0}

    # Simulate Matches
    print(f"Simulating {len(schedule)} qualification matches...")
    for m in schedule:
        red_teams = [t['teamNumber'] for t in m['teams'] if 'Red' in t['station']]
        blue_teams = [t['teamNumber'] for t in m['teams'] if 'Blue' in t['station']]
        
        if not red_teams or not blue_teams: continue

        # Calculate Alliance EPAs
        stats = {"Red": {"auto": 0.0, "tele": 0.0, "end": 0.0, "total": 0.0},
                 "Blue": {"auto": 0.0, "tele": 0.0, "end": 0.0, "total": 0.0}}
        
        for t in red_teams:
            d = teams_data.get(str(t), {})
            stats["Red"]["auto"] += d.get('auto_epa_total', 0)
            stats["Red"]["tele"] += d.get('tele_epa_total', 0)
            stats["Red"]["total"] += d.get('epa_total', 0)
        stats["Red"]["end"] = stats["Red"]["total"] - stats["Red"]["auto"] - stats["Red"]["tele"]

        for t in blue_teams:
            d = teams_data.get(str(t), {})
            stats["Blue"]["auto"] += d.get('auto_epa_total', 0)
            stats["Blue"]["tele"] += d.get('tele_epa_total', 0)
            stats["Blue"]["total"] += d.get('epa_total', 0)
        stats["Blue"]["end"] = stats["Blue"]["total"] - stats["Blue"]["auto"] - stats["Blue"]["tele"]

        # Predict outcome
        prob_red = predict_match_outcome(
            stats["Red"]["auto"], stats["Red"]["tele"], stats["Red"]["end"],
            stats["Blue"]["auto"], stats["Blue"]["tele"], stats["Blue"]["end"],
            c=120
        )

        # RP Allocation (2 for win, 1 for tie, 0 for loss)
        # We'll use 0.5 as threshold, but can be more nuanced if needed
        if prob_red > 0.505:
            winner, r_rp, b_rp = "Red", 2, 0
        elif prob_red < 0.495:
            winner, r_rp, b_rp = "Blue", 0, 2
        else:
            winner, r_rp, b_rp = "Tie", 1, 1

        # Update Standings
        for t in red_teams:
            if t in standings:
                standings[t]["RP"] += r_rp
                standings[t]["Score"] += stats["Red"]["total"]
                standings[t]["Matches"] += 1
                if winner == "Red": standings[t]["Wins"] += 1
                elif winner == "Blue": standings[t]["Losses"] += 1
                else: standings[t]["Ties"] += 1
        
        for t in blue_teams:
            if t in standings:
                standings[t]["RP"] += b_rp
                standings[t]["Score"] += stats["Blue"]["total"]
                standings[t]["Matches"] += 1
                if winner == "Blue": standings[t]["Wins"] += 1
                elif winner == "Red": standings[t]["Losses"] += 1
                else: standings[t]["Ties"] += 1

    # Rank and Display
    # Sort by RP (Descending), then Score (Descending)
    sorted_standings = sorted(
        standings.items(), 
        key=lambda x: (x[1]['RP'], x[1]['Score']), 
        reverse=True
    )

    print("\n--- Predicted Event Rankings (Simulation Based) ---")
    print("-" * 80)
    
    for i, (t_num, s) in enumerate(sorted_standings, 1):
        d = teams_data.get(str(t_num), {})
        name = d.get('team_name', 'Unknown')
        
        t_total = d.get('epa_total', 0)
        t_auto = d.get('auto_epa_total', 0)
        t_tele = d.get('tele_epa_total', 0)
        t_end = t_total - t_auto - t_tele
        t_opr = d.get('opr', 0)
        
        wlt = f"{s['Wins']}-{s['Losses']}-{s['Ties']}"
        avg_score = s['Score'] / s['Matches'] if s['Matches'] > 0 else 0
        
        # Format: {Rank}. {Team} ({Name}) - EPA: {Total} Auto: {Auto} Tele: {Tele} End: {End} OPR: {OPR} [RP: {RP}, WLT: {WLT}]
        line = f"{i}. {t_num} ({name}) - "
        line += f"EPA: {t_total:.1f} "
        line += f"Auto: {t_auto:.1f} "
        line += f"Tele: {t_tele:.1f} "
        line += f"End: {t_end:.1f} "
        line += f"OPR: {t_opr:.1f} "
        line += f"[RP: {s['RP']}, WLT: {wlt}, Avg: {avg_score:.1f}]"
        print(line)

    print("-" * 80)
    print(f"Total teams simulated: {len(sorted_standings)}")

if __name__ == "__main__":
    main()
