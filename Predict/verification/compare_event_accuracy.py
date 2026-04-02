import os
import sys
import json
import requests
import math
from datetime import datetime

# Path to nest root
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from stats.data import get_auth, get_config
from stats.averages import get_start_avg
from stats.teams.Team import Team
from stats.calculations.epa import calculate_epa
from Predict.predict_win_loss import predict_match_outcome

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

def main():
    season = 2025
    auth = get_auth()
    avg_data = get_start_avg()
    C_CONSTANT = 120 
    
    print(f"Acc Analysis (AB, CAN): (Season {season})")
    
    all_raw_events = fetch_events(season, auth)
    
    # Filter for Alberta, Canada
    # Verified fields: stateprov="AB", regionCode="CAAB", country="Canada"
    alberta_events = [
        e for e in all_raw_events 
        if (e.get('stateprov') == "AB" or e.get('regionCode') == "CAAB") and e.get('country') == "Canada"
    ]
    
    if not alberta_events:
        print("No events found for Alberta, Canada.")
        return
        
    # Sort chronologically
    alberta_events.sort(key=lambda x: x['dateStart'] if x['dateStart'] else "9999")
    
    print(f"Discovered {len(alberta_events)} events in the region. Starting simulation...")
    
    master_teams = {} # Persistent state for chronological simulation
    
    # Trackers
    event_reports = []
    stats = {
        "Meets": {"correct": 0, "total": 0},
        "Tournaments": {"correct": 0, "total": 0},
        "Scrimmages": {"correct": 0, "total": 0}
    }

    for i, event in enumerate(alberta_events):
        e_code = event['code']
        e_name = event['name']
        e_type = int(event['type'])
        
        if "Scrimmage" in e_name:
            category = "Scrimmages"
        else:
            category = "Meets" if e_type == 1 else "Tournaments"
        
        matches_raw = fetch_matches(season, e_code, auth)
        scores_raw = fetch_scores(season, e_code, auth)
        
        if not matches_raw or not scores_raw:
            continue
            
        score_map = {s['matchNumber']: s for s in scores_raw}
        matches_raw.sort(key=lambda x: x['matchNumber'])
        
        e_correct = 0
        e_total = 0
        
        for m in matches_raw:
            m_num = m['matchNumber']
            if m_num not in score_map: continue
            
            red_teams = [t['teamNumber'] for t in m['teams'] if 'Red' in t['station']]
            blue_teams = [t['teamNumber'] for t in m['teams'] if 'Blue' in t['station']]
            if len(red_teams) < 2 or len(blue_teams) < 2: continue
            
            # Init Teams
            for t in red_teams + blue_teams:
                if t not in master_teams:
                    nt = Team(t, "", "", "", "", "")
                    nt.update_epa(avg_data[0]/2, avg_data[1]/2, avg_data[2]/2, 0)
                    master_teams[t] = nt
            
            # Predict
            r_auto = sum(master_teams[t].epa_auto_total for t in red_teams)
            b_auto = sum(master_teams[t].epa_auto_total for t in blue_teams)
            r_tele = sum(master_teams[t].epa_tele_total for t in red_teams)
            b_tele = sum(master_teams[t].epa_tele_total for t in blue_teams)
            r_end = sum(master_teams[t].epa_endgame_total for t in red_teams)
            b_end = sum(master_teams[t].epa_endgame_total for t in blue_teams)
            
            red_win_prob = predict_match_outcome(r_auto, r_tele, r_end, b_auto, b_tele, b_end, c=C_CONSTANT)
            
            # Actual
            s_info = score_map[m_num]
            r_info = next(a for a in s_info['alliances'] if a['alliance'].lower() == 'red')
            b_info = next(a for a in s_info['alliances'] if a['alliance'].lower() == 'blue')
            m_red_s = r_info['totalPoints'] - b_info['foulPointsCommitted']
            m_blue_s = b_info['totalPoints'] - r_info['foulPointsCommitted']
            
            if m_red_s != m_blue_s:
                actual_winner = "RED" if m_red_s > m_blue_s else "BLUE"
                predicted_winner = "RED" if red_win_prob > 0.5 else "BLUE"
                
                e_total += 1
                stats[category]["total"] += 1
                if actual_winner == predicted_winner:
                    e_correct += 1
                    stats[category]["correct"] += 1
            
            # Update State
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

        # Record event result
        if e_total > 0:
            acc = e_correct / e_total
            event_reports.append({
                "code": e_code,
                "name": e_name,
                "acc": acc,
                "matches": e_total,
                "category": category
            })
        
        print(f"Processed {i+1}/{len(alberta_events)} events: {e_code}", end='\r')

    # Output detailed report
    print("\n\nIndividual Event Acc")
    print("-" * 90)
    print(f"{'Event Code':<12} | {'Category':<12} | {'Matches':<8} | {'Accuracy':<10} | {'Event Name'}")
    print("-" * 90)
    for rep in event_reports:
        print(f"{rep['code']:<12} | {rep['category']:<12} | {rep['matches']:<8} | {rep['acc']:>8.2%} | {rep['name']}")
    
    print("\n" + "="*50)
    print("Acc By Type (AB, CAN)")
    print("="*50)
    
    for cat in ["Meets", "Tournaments", "Scrimmages"]:
        c = stats[cat]["correct"]
        t = stats[cat]["total"]
        if t == 0: continue
        acc = c / t
        print(f"{cat:<12}: {acc:.2%} ({c}/{t})")
    
    print("-" * 50)
    total_c = stats["Meets"]["correct"] + stats["Tournaments"]["correct"]
    total_t = stats["Meets"]["total"] + stats["Tournaments"]["total"]
    if total_t > 0:
        g_acc = total_c / total_t
        err = math.sqrt(g_acc * (1 - g_acc) / total_t)
        print(f"Global region accuracy: {g_acc:.2%} ({total_c}/{total_t})")
        print(f"Statistical Err: ±{err:.2%}")
    print("="*50)

if __name__ == "__main__":
    main()
