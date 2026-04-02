import os
import sys
import json

# Path to the nest root 
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Predict.predict_win_loss import predict_match_outcome
from stats.averages import get_start_avg

def main():
    season = 2025
    C_CONSTANT = 100
    avg_total, avg_auto, avg_tele = get_start_avg()
    # Baseline for teams not in cache (avg / 2 teams)
    default_epa = {
        "total": avg_total / 2,
        "auto": avg_auto / 2,
        "tele": avg_tele / 2,
        "endgame": (avg_total - avg_auto - avg_tele) / 2
    }

    # Load Cache
    cache_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "CAABCMP1214.json")
    cache_data = {}
    if os.path.exists(cache_path):
        with open(cache_path, 'r') as f:
            cache_data = json.load(f)
    else:
        print(f"Warning: Data file {cache_path} not found. Using defaults.")

    print(f"Match Prediction (Source: CAABCMP1214.json)", flush=True)
    print(f"C={C_CONSTANT}", flush=True)
    
    try:
        red1 = input("Enter Red Team 1: ").strip()
        red2 = input("Enter Red Team 2: ").strip()
        blue1 = input("Enter Blue Team 1: ").strip()
        blue2 = input("Enter Blue Team 2: ").strip()
        
        teams = {"Red": [red1, red2], "Blue": [blue1, blue2]}
        alliance_stats = {"Red": {"auto": 0.0, "tele": 0.0, "end": 0.0, "total": 0.0},
                          "Blue": {"auto": 0.0, "tele": 0.0, "end": 0.0, "total": 0.0}}
        
        print("\nTeam Data:")
        print("-" * 40)

        for alliance, t_nums in teams.items():
            for t in t_nums:
                if t in cache_data:
                    d = cache_data[t]
                    t_total = d.get('epa_total', 0)
                    t_auto = d.get('auto_epa_total', 0)
                    t_tele = d.get('tele_epa_total', 0)
                    t_end = t_total - t_auto - t_tele
                    
                    print(f"Team {t:<6} ({alliance}): EPA {t_total:>5.1f} (Auto: {t_auto:>4.1f}, Tele: {t_tele:>4.1f}, End: {t_end:>4.1f})")
                    alliance_stats[alliance]["auto"] += t_auto
                    alliance_stats[alliance]["tele"] += t_tele
                    alliance_stats[alliance]["end"] += t_end
                    alliance_stats[alliance]["total"] += t_total
                else:
                    print(f"Team {t:<6} ({alliance}): [Using Default Initialization]")
                    alliance_stats[alliance]["auto"] += default_epa["auto"]
                    alliance_stats[alliance]["tele"] += default_epa["tele"]
                    alliance_stats[alliance]["end"] += default_epa["endgame"]
                    alliance_stats[alliance]["total"] += default_epa["total"]

        # Calculate prediction
        ra, rt, re = alliance_stats["Red"]["auto"], alliance_stats["Red"]["tele"], alliance_stats["Red"]["end"]
        ba, bt, be = alliance_stats["Blue"]["auto"], alliance_stats["Blue"]["tele"], alliance_stats["Blue"]["end"]
        
        red_win_prob = predict_match_outcome(ra, rt, re, ba, bt, be, c=C_CONSTANT)
        blue_win_prob = 1.0 - red_win_prob
        
        epa_r = alliance_stats["Red"]["total"]
        epa_b = alliance_stats["Blue"]["total"]
        delta = epa_b - epa_r
        
        print("-" * 40)
        print(f"Red  ({red1}, {red2}) | EPA Total: {epa_r:.1f}")
        print(f"Blue ({blue1}, {blue2}) | EPA Total: {epa_b:.1f}")
        print(f"Δ(Blue-Red): {delta:+.1f}")
        print(f"Pred Win Rate: R: {red_win_prob:.1%} B: {blue_win_prob:.1%}")
        print("-" * 40)
        

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
