import os
import sys
import json
import requests
from datetime import datetime

# Ensure current directory is in path (nest root)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stats.calculations import update_teams_at_event
from stats.averages import get_start_avg
from stats.events import get_event_by_code
from stats.data import get_auth, get_config
from Predict.predict_win_loss import predict_match_outcome
from stats.events.Event import Event
from stats.teams.Team import Team

def fetch_match_schedule(event_code, auth, season):
    """Fetch the complete match schedule (including team info) from API"""
    url = f"https://ftc-api.firstinspires.org/v2.0/{season}/matches/{event_code}?tournamentLevel=qual"
    response = requests.get(url, auth=auth)
    if response.status_code != 200:
        return []
    return response.json().get('matches', [])

def main():
    season = get_config()['season']
    auth = get_auth()
    avg_total, avg_auto, avg_tele = get_start_avg()
    
    # Load Cache
    cache_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"career_epa_cache_{season}.json")
    cache_data = {}
    cache_load_msg = "--- [Notice] Cache not found. Falling back to default initialization. ---"
    if os.path.exists(cache_path):
        with open(cache_path, 'r') as f:
            cache_data = json.load(f)
        cache_load_msg = f"--- [Cache Loaded] Historical data for {len(cache_data)} teams available. ---"

    print("Searching for available events...")
    url = f"https://ftc-api.firstinspires.org/v2.0/{season}/events"
    response = requests.get(url, auth=auth)
    if response.status_code != 200:
        print("Failed to fetch event list.")
        return
        
    all_events = response.json().get('events', [])
    
    found_event_data = None
    schedule = []
    
    # Check top 25 events for an available schedule
    for target_data in all_events[:25]:
        event_code = target_data['code']
        schedule = fetch_match_schedule(event_code, auth, season)
        if schedule:
            found_event_data = target_data
            break
            
    if not found_event_data:
        print("No matches found in the top 25 events.")
        return
        
    print(f"Verification for event: {found_event_data['code']}")
    print(f"Using Constant C: 120 | Weighted Model (1.2/1.0/0.8)")
    print(cache_load_msg)
    print(f"--- Done. Verification Starting... ---")
    
    target_event = Event(found_event_data)

    # Initialize Teams
    team_data = {}
    for t_num in target_event.team_list:
        nt = Team(t_num, f"Team {t_num}", "", "", "", "")
        t_str = str(t_num)
        if t_str in cache_data:
            c = cache_data[t_str]
            nt.epa_total = c['total']
            nt.epa_auto_total = c['auto']
            nt.epa_tele_total = c['tele']
            nt.epa_endgame_total = c['endgame']
            nt.games_played = c['gp']
        else:
            nt.update_epa(avg_total/2, avg_auto/2, avg_tele/2, 0)
        team_data[t_num] = nt

    try:
        update_teams_at_event(target_event, team_data, avg_total, avg_auto, avg_tele)
    except Exception as e:
        pass

    # Output Predictions
    print(f"Qualification Match Win Rate Predictions (Fast Load):")
    print("-" * 80)

    display_count = 0
    correct_p, total_m = 0, 0
    correct_p5, total_m5 = 0, 0

    for m in schedule:
        if display_count >= 25: break
            
        match_num = m['matchNumber']
        red_teams = [t['teamNumber'] for t in m['teams'] if 'Red' in t['station']]
        blue_teams = [t['teamNumber'] for t in m['teams'] if 'Blue' in t['station']]
        if len(red_teams) < 2 or len(blue_teams) < 2: continue
        
        # Prepare component EPAs
        epa_r = sum(team_data[t].epa_total for t in red_teams if t in team_data)
        epa_b = sum(team_data[t].epa_total for t in blue_teams if t in team_data)
        r_auto = sum(team_data[t].epa_auto_total for t in red_teams if t in team_data)
        b_auto = sum(team_data[t].epa_auto_total for t in blue_teams if t in team_data)
        r_tele = sum(team_data[t].epa_tele_total for t in red_teams if t in team_data)
        b_tele = sum(team_data[t].epa_tele_total for t in blue_teams if t in team_data)
        r_end = sum(team_data[t].epa_endgame_total for t in red_teams if t in team_data)
        b_end = sum(team_data[t].epa_endgame_total for t in blue_teams if t in team_data)
        
        # C=120
        win_prob_red = predict_match_outcome(r_auto, r_tele, r_end, b_auto, b_tele, b_end, c=120)
        win_prob_blue = 1 - win_prob_red
        delta = epa_b - epa_r
        
        status = ""
        if m.get('scoreRedFinal') is not None:
            winner = "RED" if m['scoreRedFinal'] > m['scoreBlueFinal'] else "BLUE" if m['scoreBlueFinal'] > m['scoreRedFinal'] else "TIE"
            if winner != "TIE":
                total_m += 1
                pred_correct = (win_prob_red > 0.5 and winner == "RED") or (win_prob_red < 0.5 and winner == "BLUE")
                if pred_correct: correct_p += 1
                if match_num >= 5:
                    total_m5 += 1
                    if pred_correct: correct_p5 += 1
            status = f"\nActual Win : {winner[0]}"

        print(f"Q {match_num:02}")
        print(f"Red  ({red_teams[0]}, {red_teams[1]}) | EPA Total: {epa_r:.1f}")
        print(f"Blue ({blue_teams[0]}, {blue_teams[1]}) | EPA Total: {epa_b:.1f}")
        print(f"Δ(Blue-Red): {delta:+.1f}")
        print(f"Pred Win Rate: B: {win_prob_blue:.1%}  R: {win_prob_red:.1%}{status}")
        print("-" * 48)
        display_count += 1

    if total_m > 0:
        print(f"-" * 75)
        print(f"Final Event Accuracy (Cached EPA): {correct_p/total_m:.2%} ({correct_p}/{total_m})")
        if total_m5 > 0:
            print(f"Accuracy Round 5+:                {correct_p5/total_m5:.2%} ({correct_p5}/{total_m5})")

if __name__ == "__main__":
    main()
