import os
import sys
import json
import requests
from datetime import datetime

# Ensure current directory is in path (nest root)
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from stats.data import get_auth, get_config
from stats.averages import get_start_avg
from stats.teams.Team import Team
from stats.calculations.epa import calculate_epa
from Predict.predict_win_loss import predict_match_outcome

def main():
    target_event_code = "CAABCMP"
    season = 2025
    auth = get_auth()
    avg_data = get_start_avg()
    # Constant
    C_CONSTANT = 120 
    
    print(f"Verification for event: {target_event_code}")
    print(f"Using Constant C: {C_CONSTANT} | Weighted Model (1.2/1.0/0.8)")
    
    # 1. Load Cache
    cache_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), f"career_epa_cache_{season}.json")
    cache_data = {}
    if os.path.exists(cache_path):
        with open(cache_path, 'r') as f:
            cache_data = json.load(f)
        print(f"Historical data for {len(cache_data)} teams available.")
    else:
        print(f"Cache not found. Using default initialization.")
    print(f"Verification Starting...")

    # 2. Fetch Matches & Scores
    match_url = f"https://ftc-api.firstinspires.org/v2.0/{season}/matches/{target_event_code}?tournamentLevel=qual"
    m_r = requests.get(match_url, auth=auth, timeout=10)
    target_matches = m_r.json().get('matches', []) if m_r.status_code == 200 else []
    
    score_url = f"https://ftc-api.firstinspires.org/v2.0/{season}/scores/{target_event_code}/qual"
    s_r = requests.get(score_url, auth=auth, timeout=10)
    target_scores = s_r.json().get('matchScores', []) if s_r.status_code == 200 else []
    
    if not target_matches or not target_scores:
        print("Failed to fetch event data.")
        return
        
    score_map = {s['matchNumber']: s for s in target_scores}
    target_matches.sort(key=lambda x: x['matchNumber'])
    
    print(f"\nQualification Match Win Rate Predictions:")
    print("-" * 80)
    
    global_teams = {}
    correct_p, total_m = 0, 0
    correct_p5, total_m5 = 0, 0
    
    for m in target_matches:
        m_num = m['matchNumber']
        if m_num not in score_map: continue
        red_teams = [t['teamNumber'] for t in m['teams'] if 'Red' in t['station']]
        blue_teams = [t['teamNumber'] for t in m['teams'] if 'Blue' in t['station']]
        if len(red_teams) < 2 or len(blue_teams) < 2: continue
        
        # Initialize teams from cache
        for t in red_teams + blue_teams:
            if t not in global_teams:
                nt = Team(t, f"Team {t}", "", "", "", "")
                t_str = str(t)
                if t_str in cache_data:
                    c = cache_data[t_str]
                    # Inject historical values
                    nt.epa_total = c['total']
                    nt.epa_auto_total = c['auto']
                    nt.epa_tele_total = c['tele']
                    nt.epa_endgame_total = c['endgame']
                    nt.games_played = c['gp']
                else:
                    nt.update_epa(avg_data[0]/2, avg_data[1]/2, avg_data[2]/2, 0)
                global_teams[t] = nt
        
        # Prediction
        r_auto = sum(global_teams[t].epa_auto_total for t in red_teams)
        b_auto = sum(global_teams[t].epa_auto_total for t in blue_teams)
        r_tele = sum(global_teams[t].epa_tele_total for t in red_teams)
        b_tele = sum(global_teams[t].epa_tele_total for t in blue_teams)
        r_end = sum(global_teams[t].epa_endgame_total for t in red_teams)
        b_end = sum(global_teams[t].epa_endgame_total for t in blue_teams)
        
        red_win_prob = predict_match_outcome(r_auto, r_tele, r_end, b_auto, b_tele, b_end, c=C_CONSTANT)
        blue_win_prob = 1 - red_win_prob
        
        # Results
        s_info = score_map[m_num]
        r_info = next(a for a in s_info['alliances'] if a['alliance'].lower() == 'red')
        b_info = next(a for a in s_info['alliances'] if a['alliance'].lower() == 'blue')
        m_red_score = r_info['totalPoints'] - b_info['foulPointsCommitted']
        m_blue_score = b_info['totalPoints'] - r_info['foulPointsCommitted']
        winner = "RED" if m_red_score > m_blue_score else "BLUE" if m_blue_score > m_red_score else "TIE"
        pred_correct = (red_win_prob > 0.5 and winner == "RED") or (red_win_prob < 0.5 and winner == "BLUE")
        
        if winner != "TIE":
            total_m += 1
            if pred_correct: correct_p += 1
            if m_num >= 5:
                total_m5 += 1
                if pred_correct: correct_p5 += 1
        
        # UI Print
        epa_r = sum(global_teams[t].epa_total for t in red_teams)
        epa_b = sum(global_teams[t].epa_total for t in blue_teams)
        delta = epa_b - epa_r
        print(f"Q {m_num:02}")
        print(f"Red  ({red_teams[0]}, {red_teams[1]}) | EPA Total: {epa_r:.1f}")
        print(f"Blue ({blue_teams[0]}, {blue_teams[1]}) | EPA Total: {epa_b:.1f}")
        print(f"Δ(Blue-Red): {delta:+.1f}")
        print(f"Pred Win Rate: R: {red_win_prob:.1%} B: {blue_win_prob:.1%}")
        print(f"Actual Win : {winner[0]}")
        print("-" * 48)
        
        # UPDATE
        gp = sum(global_teams[t].games_played for t in red_teams + blue_teams) / 4
        for t in red_teams + blue_teams: global_teams[t].update_game_played(f"{season}{target_event_code}Q{m_num}")
        rsa = r_info['autoArtifactPoints'] + r_info['autoLeavePoints'] + r_info['autoPatternPoints']
        bsa = b_info['autoArtifactPoints'] + b_info['autoLeavePoints'] + b_info['autoPatternPoints']
        rst = r_info['teleopArtifactPoints'] + r_info['teleopDepotPoints'] + r_info['teleopPatternPoints']
        bst = b_info['teleopArtifactPoints'] + b_info['teleopDepotPoints'] + b_info['teleopPatternPoints']
        rse, bse = m_red_score - rsa - rst, m_blue_score - bsa - bst
        cra, cba = calculate_epa(r_auto, b_auto, rsa, bsa, gp)
        crt, cbt = calculate_epa(r_tele, b_tele, rst, bst, gp)
        cre, cbe = calculate_epa(r_end, b_end, rse, bse, gp)
        cr, cb = calculate_epa(epa_r, epa_b, m_red_score, m_blue_score, gp)
        for t in red_teams: global_teams[t].update_epa(cr, cra, crt, cre)
        for t in blue_teams: global_teams[t].update_epa(cb, cba, cbt, cbe)

    print(f"-" * 48)
    print(f"Event Accuracy: {correct_p/total_m:.2%} ({correct_p}/{total_m})")
    print(f"Accuracy Round 5+: {correct_p5/total_m5:.2%} ({correct_p5}/{total_m5})")

if __name__ == "__main__":
    main()
