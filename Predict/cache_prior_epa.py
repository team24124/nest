import os
import sys
import json
import requests
from datetime import datetime

# Ensure current directory is in path (nest root)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stats.data import get_auth, get_config
from stats.averages import get_start_avg
from stats.teams.Team import Team
from stats.calculations.epa import calculate_epa

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
    cache_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"career_epa_cache_{season}.json")
    
    print(f"EPA Cache Generator (Season {season})")
    
    all_events = fetch_events(season, auth)
    # Filter valid event types
    valid_types = get_config()['allowed_events']
    all_events = [e for e in all_events if int(e['type']) in valid_types]
    all_events.sort(key=lambda x: x['dateStart'])
    
    global_teams = {}
    processed_count = 0
    total_events = len(all_events)
    
    print(f"Processing {total_events} events for full season simulation...")
    
    for i, event in enumerate(all_events):
        e_code = event['code']
        # Fetching data
        matches_raw = fetch_matches(season, e_code, auth)
        scores_raw = fetch_scores(season, e_code, auth)
        
        if not matches_raw or not scores_raw:
            continue
            
        score_map = {s['matchNumber']: s for s in scores_raw}
        matches_raw.sort(key=lambda x: x['matchNumber'])
        
        for m in matches_raw:
            m_num = m['matchNumber']
            if m_num not in score_map: continue
            
            red_teams = [t['teamNumber'] for t in m['teams'] if 'Red' in t['station']]
            blue_teams = [t['teamNumber'] for t in m['teams'] if 'Blue' in t['station']]
            if len(red_teams) < 2 or len(blue_teams) < 2: continue
            
            for t in red_teams + blue_teams:
                if t not in global_teams:
                    nt = Team(t, f"Team {t}", "", "", "", "")
                    nt.update_epa(avg_data[0]/2, avg_data[1]/2, avg_data[2]/2, 0)
                    global_teams[t] = nt
            
            # EPA Logic (Simplified capture for cache)
            # Pre EPAs
            r_auto = sum(global_teams[t].epa_auto_total for t in red_teams)
            b_auto = sum(global_teams[t].epa_auto_total for t in blue_teams)
            r_tele = sum(global_teams[t].epa_tele_total for t in red_teams)
            b_tele = sum(global_teams[t].epa_tele_total for t in blue_teams)
            r_end = sum(global_teams[t].epa_endgame_total for t in red_teams)
            b_end = sum(global_teams[t].epa_endgame_total for t in blue_teams)
            r_total = sum(global_teams[t].epa_total for t in red_teams)
            b_total = sum(global_teams[t].epa_total for t in blue_teams)
            
            s_info = score_map[m_num]
            r_info = next(a for a in s_info['alliances'] if a['alliance'].lower() == 'red')
            b_info = next(a for a in s_info['alliances'] if a['alliance'].lower() == 'blue')
            m_red_s = r_info['totalPoints'] - b_info['foulPointsCommitted']
            m_blue_s = b_info['totalPoints'] - r_info['foulPointsCommitted']
            
            gp = sum(global_teams[t].games_played for t in red_teams + blue_teams) / 4
            for t in red_teams + blue_teams: global_teams[t].update_game_played(f"{season}{e_code}Q{m_num}")
            
            rsa = r_info['autoArtifactPoints'] + r_info['autoLeavePoints'] + r_info['autoPatternPoints']
            bsa = b_info['autoArtifactPoints'] + b_info['autoLeavePoints'] + b_info['autoPatternPoints']
            rst = r_info['teleopArtifactPoints'] + r_info['teleopDepotPoints'] + r_info['teleopPatternPoints']
            bst = b_info['teleopArtifactPoints'] + b_info['teleopDepotPoints'] + b_info['teleopPatternPoints']
            rse, bse = m_red_s - rsa - rst, m_blue_s - bsa - bst
            
            cra, cba = calculate_epa(r_auto, b_auto, rsa, bsa, gp)
            crt, cbt = calculate_epa(r_tele, b_tele, rst, bst, gp)
            cre, cbe = calculate_epa(r_end, b_end, rse, bse, gp)
            cr, cb = calculate_epa(r_total, b_total, m_red_s, m_blue_s, gp)
            
            for t in red_teams: global_teams[t].update_epa(cr, cra, crt, cre)
            for t in blue_teams: global_teams[t].update_epa(cb, cba, cbt, cbe)
            
        processed_count += 1
        if processed_count % 10 == 0:
            print(f"Processed {processed_count}/{total_events} events...", end='\r')

    # Convert global_teams to serializable dict
    cache_data = {}
    for t_num, team in global_teams.items():
        cache_data[str(t_num)] = {
            "total": team.epa_total,
            "auto": team.epa_auto_total,
            "tele": team.epa_tele_total,
            "endgame": team.epa_endgame_total,
            "gp": team.games_played
        }
        
    with open(cache_file, 'w') as f:
        json.dump(cache_data, f, indent=4)
        
    print(f"\nCache generated successfully for {len(cache_data)} teams at {cache_file}")

if __name__ == "__main__":
    main()
