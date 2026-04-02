import os
import sys
import numpy as np
import requests
from datetime import datetime

# Path to nest root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stats.calculations.epa import calculate_epa
from stats.averages import get_start_avg
from stats.data import get_config, get_auth, get_season_score_parser
from stats.teams.Team import Team
from stats.events.Event import Event

def get_blue_win_prob(red_epa, blue_epa, c):
    """
    Calculate Blue alliance win probability.
    Using formula: P(Blue) = 1 / (1 + 10^((Red - Blue)/C))
    """
    return 1 / (1 + 10 ** ((red_epa - blue_epa) / c))

def log_loss(c, data):
    if len(data) == 0: return 0
    total_loss = 0
    for r_epa, b_epa, actual in data:
        # actual=1 = Blue won
        prob = get_blue_win_prob(r_epa, b_epa, c)
        prob = max(min(prob, 0.9999), 0.0001)
        total_loss += -(actual * np.log(prob) + (1 - actual) * np.log(1 - prob))
    return total_loss / len(data)

def find_best_c(data):
    best_c = 100
    min_loss = float('inf')
    for c in range(20, 1001, 5): 
        l = log_loss(c, data)
        if l < min_loss:
            min_loss = l
            best_c = c
    return best_c, min_loss

def fetch_teams_for_event(event_code, auth, season):
    url = f"https://ftc-api.firstinspires.org/v2.0/{season}/teams?eventCode={event_code}"
    try:
        response = requests.get(url, auth=auth, timeout=10)
        return [t['teamNumber'] for t in response.json().get('teams', [])] if response.status_code == 200 else []
    except:
        return []

def create_game_matrix_manual(event_code, team_list, auth, season):
    url = f"https://ftc-api.firstinspires.org/v2.0/{season}/matches/{event_code}?tournamentLevel=qual"
    try:
        response = requests.get(url, auth=auth, timeout=10)
        if response.status_code != 200: return [], []
        matches = response.json().get('matches', [])
        matrix = []
        for m in matches:
            red = [0] * len(team_list)
            blue = [0] * len(team_list)
            if 'teams' not in m: continue
            for t in m['teams']:
                if t['teamNumber'] not in team_list: continue
                idx = team_list.index(t['teamNumber'])
                if 'Red' in t['station']: red[idx] = 1
                else: blue[idx] = 1
            matrix.append(red); matrix.append(blue)
        return matrix, matches
    except:
        return [], []

def main():
    season = get_config()['season']
    auth = get_auth()
    avg_total, _, _ = get_start_avg()
    
    print("Fetching all events for 2025...", flush=True)
    url = f"https://ftc-api.firstinspires.org/v2.0/{season}/events"
    all_events_raw = requests.get(url, auth=auth, timeout=15).json().get('events', [])
    # Sort events by date
    all_events_raw.sort(key=lambda x: x.get('dateStart', ''))
    
    # SAMPLING STRATEGY: Take 1 out of every 4 events to ensure broad coverage without excessive time
    sampled_events = all_events_raw[::4]
    total_sampled = len(sampled_events)
    
    match_samples = []
    actual_data_count = 0
    
    # GLOBAL CONTEXT: Maintain teams across the entire season
    global_teams = {}
    
    print(f"Phase 2: Running with Prior EPA (Cross-Event Initialization)...", flush=True)
    print(f"Sampling {total_sampled} events out of {len(all_events_raw)} total...", flush=True)
    
    for i, e_data in enumerate(sampled_events):
        event_code = e_data['code']
        # Progress log
        if (i + 1) % 20 == 0:
            print(f"  Progress Check: Checked {i+1}/{total_sampled} events. Teams in DB: {len(global_teams)}. Matches: {len(match_samples)}", flush=True)

        try:
            # Quick check for scores
            check_scores = requests.get(f"https://ftc-api.firstinspires.org/v2.0/{season}/scores/{event_code}/qual", auth=auth, timeout=5)
            if check_scores.status_code != 200 or not check_scores.json().get('matchScores'):
                continue

            team_list = fetch_teams_for_event(event_code, auth, season)
            if not team_list: continue
            
            game_matrix, _ = create_game_matrix_manual(event_code, team_list, auth, season)
            event_data = get_season_score_parser(season).parse(event_code)
            if not event_data.matches: continue
            
            actual_data_count += 1
            
            # Check if team exists in global_teams, else initialize
            local_event_teams = {}
            for t_num in team_list:
                if t_num in global_teams:
                    local_event_teams[t_num] = global_teams[t_num]
                else:
                    nt = Team(t_num, "", "", "", "", "")
                    # Initialize components at 0, total at avg/2
                    nt.update_epa(avg_total/2, 0, 0, 0)
                    global_teams[t_num] = nt
                    local_event_teams[t_num] = nt
            
            m_idx = 0
            for j in range(0, len(game_matrix), 2):
                if m_idx >= len(event_data.matches): break
                red_idx = np.where(np.array(game_matrix[j]) == 1)[0]
                blue_idx = np.where(np.array(game_matrix[j+1]) == 1)[0]
                if not len(red_idx) or not len(blue_idx): 
                    m_idx += 1; continue
                
                # ΔR = 1.2 * ΔAuto + 1.0 * ΔTele + 0.8 * ΔEnd
                r_auto = sum(local_event_teams[team_list[idx]].epa_auto_total for idx in red_idx)
                b_auto = sum(local_event_teams[team_list[idx]].epa_auto_total for idx in blue_idx)
                r_tele = sum(local_event_teams[team_list[idx]].epa_tele_total for idx in red_idx)
                b_tele = sum(local_event_teams[team_list[idx]].epa_tele_total for idx in blue_idx)
                r_end = sum(local_event_teams[team_list[idx]].epa_endgame_total for idx in red_idx)
                b_end = sum(local_event_teams[team_list[idx]].epa_endgame_total for idx in blue_idx)
                
                # Weighted difference for Blue alliance
                diff_weighted = 1.2 * (r_auto - b_auto) + 1.0 * (r_tele - b_tele) + 0.8 * (r_end - b_end)
                # Note: formula uses get_blue_win_prob(red, blue, c) -> 1 / (1 + 10**((red-blue)/c))
                # To stick to our weighted logic:
                # store (r_epa_effective, b_epa_effective) where epa_effective = 1.2*auto + 1.0*tele + 0.8*end
                r_eff = 1.2 * r_auto + 1.0 * r_tele + 0.8 * r_end
                b_eff = 1.2 * b_auto + 1.0 * b_tele + 0.8 * b_end
                
                m_score = event_data.matches[m_idx]
                rs, bs = m_score.red_alliance.total_score, m_score.blue_alliance.total_score
                
                res = 0.5 if rs == bs else (1 if bs > rs else 0)
                # Store effective EPAs for the optimizer
                match_samples.append((r_eff, b_eff, res))
                
                # UPDATE EPAs USING COMPONENTS
                # Scores
                rsa, bsa = m_score.red_alliance.auto_score, m_score.blue_alliance.auto_score
                rst, bst = m_score.red_alliance.tele_score, m_score.blue_alliance.tele_score
                rse, bse = rs - rsa - rst, bs - bsa - bst
                
                gp = sum(local_event_teams[team_list[idx]].games_played for idx in list(red_idx) + list(blue_idx)) / 4
                for idx in list(red_idx) + list(blue_idx): local_event_teams[team_list[idx]].update_game_played("")
                
                # Delta calculations
                cr, cb = calculate_epa(sum(local_event_teams[team_list[idx]].epa_total for idx in red_idx), 
                                       sum(local_event_teams[team_list[idx]].epa_total for idx in blue_idx), 
                                       rs, bs, gp)
                cra, cba = calculate_epa(r_auto, b_auto, rsa, bsa, gp)
                crt, cbt = calculate_epa(r_tele, b_tele, rst, bst, gp)
                cre, cbe = calculate_epa(r_end, b_end, rse, bse, gp)
                
                for idx in red_idx: local_event_teams[team_list[idx]].update_epa(cr, cra, crt, cre)
                for idx in blue_idx: local_event_teams[team_list[idx]].update_epa(cb, cba, cbt, cbe)
                m_idx += 1
        except:
            continue

    print(f"\nSampling Completed. Processed {actual_data_count} events with data. Total Matches: {len(match_samples)}", flush=True)
    
    if not match_samples: return

    # Results calculation
    best_c, min_l = find_best_c(match_samples)
    baseline_50_loss = -np.log(0.5)
    
    total_non_tie = sum(1 for r, b, res in match_samples if res != 0.5)
    correct_high_epa = sum(1 for r, b, res in match_samples if (res==1 and b>r) or (res==0 and r>b))
    model_accuracy = correct_high_epa / total_non_tie if total_non_tie > 0 else 0
    
    print(f"\nStatistical Results", flush=True)
    print(f"Total Matches:     {len(match_samples)}", flush=True)
    print(f"Optimal Constant C: {best_c}", flush=True)
    print(f"Model Log-Loss:    {min_l:.4f}", flush=True)
    print(f"Model Accuracy:    {model_accuracy:.2%}", flush=True)
    print(f"Improvement over 50/50: {(baseline_50_loss - min_l) / baseline_50_loss:.2%} (Log-loss)", flush=True)

if __name__ == "__main__":
    main()
