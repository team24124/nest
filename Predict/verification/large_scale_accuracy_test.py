# IMPORTS
import os
import sys
import json
import requests
import math
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from stats.data import get_auth, get_config
from stats.averages import get_start_avg
from stats.teams.Team import Team
from stats.calculations.epa import calculate_epa
from Predict.predict_win_loss import predict_match_outcome

# FUNCTIONS
def fetch_events(season, auth):
    url = f"https://ftc-api.firstinspires.org/v2.0/{season}/events"
    r = requests.get(url, auth=auth, timeout=10)
    return r.json().get('events', []) if r.status_code == 200 else []

def fetch_scores(season, event_code, auth):
    url = f"https://ftc-api.firstinspires.org/v2.0/{season}/scores/{event_code}/qual"
    r = requests.get(url, auth=auth, timeout=15)
    return r.json().get('matchScores', []) if r.status_code == 200 else []

def fetch_matches(season, event_code, auth):
    url = f"https://ftc-api.firstinspires.org/v2.0/{season}/matches/{event_code}?tournamentLevel=qual"
    r = requests.get(url, auth=auth, timeout=15)
    return r.json().get('matches', []) if r.status_code == 200 else []

# MAIN
def main():
    season = 2025
    auth = get_auth()
    avg_data = get_start_avg()
    C_CONSTANT = 120 
    
    print(f"Large Scale Verification (Season {season})")
    
    events = fetch_events(season, auth)
    valid_types = get_config()['allowed_events']
    # Filter and Sort
    all_events = [e for e in events if int(e['type']) in valid_types]
    all_events.sort(key=lambda x: x['dateStart'] if x['dateStart'] else "9999")
    
    print(f"Discovered {len(all_events)} valid events")
    
    master_teams = {} # PERSISTENT state across the whole season
    
    stats = {
        "early": {"correct": 0, "total": 0}, # Events 1-100
        "mid": {"correct": 0, "total": 0},   # Events 101-300
        "late": {"correct": 0, "total": 0},  # Events 301+
        "global": {"correct": 0, "total": 0}
    }

    target_count = min(300, len(all_events)) 
    
    for i, event in enumerate(all_events[:target_count]):
        e_code = event['code']
        matches_raw = fetch_matches(season, e_code, auth)
        scores_raw = fetch_scores(season, e_code, auth)
        
        if not matches_raw or not scores_raw: continue
        
        score_map = {s['matchNumber']: s for s in scores_raw}
        matches_raw.sort(key=lambda x: x['matchNumber'])
        
        phase = "early" if i < 100 else "mid" if i < 300 else "late"
        
        for m in matches_raw:
            m_num = m['matchNumber']
            if m_num not in score_map: continue
            
            red_teams = [t['teamNumber'] for t in m['teams'] if 'Red' in t['station']]
            blue_teams = [t['teamNumber'] for t in m['teams'] if 'Blue' in t['station']]
            if len(red_teams) < 2 or len(blue_teams) < 2: continue
            
            # Initialize teams on first appearance in the season
            for t in red_teams + blue_teams:
                if t not in master_teams:
                    nt = Team(t, "", "", "", "", "")
                    nt.update_epa(avg_data[0]/2, avg_data[1]/2, avg_data[2]/2, 0)
                    master_teams[t] = nt
            
            # PREDICT
            r_auto = sum(master_teams[t].epa_auto_total for t in red_teams)
            b_auto = sum(master_teams[t].epa_auto_total for t in blue_teams)
            r_tele = sum(master_teams[t].epa_tele_total for t in red_teams)
            b_tele = sum(master_teams[t].epa_tele_total for t in blue_teams)
            r_end = sum(master_teams[t].epa_endgame_total for t in red_teams)
            b_end = sum(master_teams[t].epa_endgame_total for t in blue_teams)
            
            red_win_prob = predict_match_outcome(r_auto, r_tele, r_end, b_auto, b_tele, b_end, c=C_CONSTANT)
            predicted_winner = "RED" if red_win_prob > 0.5 else "BLUE"
            
            # ACTUAL
            s_info = score_map[m_num]
            r_info = next(a for a in s_info['alliances'] if a['alliance'].lower() == 'red')
            b_info = next(a for a in s_info['alliances'] if a['alliance'].lower() == 'blue')
            m_red_s = r_info['totalPoints'] - b_info['foulPointsCommitted']
            m_blue_s = b_info['totalPoints'] - r_info['foulPointsCommitted']
            
            if m_red_s != m_blue_s: # Skip ties
                actual_winner = "RED" if m_red_s > m_blue_s else "BLUE"
                stats["global"]["total"] += 1
                stats[phase]["total"] += 1
                if actual_winner == predicted_winner:
                    stats["global"]["correct"] += 1
                    stats[phase]["correct"] += 1
            
            # UPDATE STATE
            gp = sum(master_teams[t].games_played for t in red_teams + blue_teams) / 4
            rsa = r_info['autoArtifactPoints'] + r_info['autoLeavePoints'] + r_info['autoPatternPoints']
            bsa = b_info['autoArtifactPoints'] + b_info['autoLeavePoints'] + b_info['autoPatternPoints']
            rst = r_info['teleopArtifactPoints'] + r_info['teleopDepotPoints'] + r_info['teleopPatternPoints']
            bst = b_info['teleopArtifactPoints'] + b_info['teleopDepotPoints'] + b_info['teleopPatternPoints']
            rse, bse = m_red_s - rsa - rst, m_blue_s - bsa - bst
            
            cra, cba = calculate_epa(r_auto, b_auto, rsa, bsa, gp)
            crt, cbt = calculate_epa(r_tele, b_tele, rst, bst, gp)
            cre, cbe = calculate_epa(r_end, b_end, rse, bse, gp)
            cr, cb = calculate_epa(sum(master_teams[t].epa_total for t in red_teams), 
                                   sum(master_teams[t].epa_total for t in blue_teams), m_red_s, m_blue_s, gp)
            
            for t in red_teams: master_teams[t].update_epa(cr, cra, crt, cre)
            for t in blue_teams: master_teams[t].update_epa(cb, cba, cbt, cbe)

        if (i+1) % 10 == 0:
            total_matches = stats["global"]["total"]
            current_acc = stats["global"]["correct"] / total_matches if total_matches > 0 else 0
            print(f"Processed {i+1}/{target_count} events... Matches: {total_matches}, Acc: {current_acc:.2%}", end='\r')

    print("\n" + "="*20)
    print("Verification Results")
    print("="*20)
    
    for p in ["early", "mid", "late"]:
        if stats[p]["total"] == 0: continue
        acc = stats[p]["correct"] / stats[p]["total"]
        print(f"{p.capitalize():<10} Phase: {acc:.2%} ({stats[p]['correct']}/{stats[p]['total']})")
    
    print("-" * 50)
    g_acc = stats["global"]["correct"] / stats["global"]["total"]
    g_total = stats["global"]["total"]
    g_err = math.sqrt(g_acc * (1 - g_acc) / g_total)
    
    print(f"Global Accuracy : {g_acc:.2%}")
    print(f"Total Matches   : {g_total}")
    print(f"Statistical Err : ±{g_err:.2%}")
    print(f"95% CI: {g_acc - 1.96*g_err:.2%} - {g_acc + 1.96*g_err:.2%}")
    print("="*50)

if __name__ == "__main__":
    main()
