import os
import sys

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from stats.data.manual_import import import_manual_data
from stats.calculations.opr import calculate_opr

def main():
    csv_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "../events/manual_matches.csv"))
    if not os.path.exists(csv_file):
        print(f"Error: {csv_file} not found.")
        return

    print(f"rReading {csv_file} ...")
    try:
        team_list, game_matrix, event_data = import_manual_data(csv_file)
    except Exception as e:
        print(f"Error importing data: {e}")
        return

    print(f"Found {len(team_list)} teams and {len(game_matrix)} match records.")

    print("Calculating EPA...")
    try:
        # Calculate EPA
        from stats.teams.Team import Team
        from stats.averages import get_start_avg
        from stats.calculations.epa import update_epa
        
        # Create dictionary of Team objects
        team_data = {}
        avg_total, avg_auto, avg_tele = get_start_avg()
        for t_num in team_list:
            t = Team(t_num, f"Team {t_num}", "US", "CA", "City", "Region")
            t.update_epa(avg_total / 2, avg_auto / 2, avg_tele / 2) # Start at half alliance avg
            team_data[t_num] = t
            
        update_epa(team_list, game_matrix, event_data, team_data)
        
    except Exception as e:
        print(f"Error calculating: {e}")
        import traceback
        traceback.print_exc()
        return

    print("\nEPA")
    
    # Combine data for sorting
    combined_results = []
    for t_num in team_list:
        combined_results.append({
            'num': t_num,
            'epa': team_data[t_num].epa_total
        })
    
    # Sort by EPA descending
    combined_results.sort(key=lambda x: x['epa'], reverse=True)

    for item in combined_results:
        print(f"{item['num']:<6} : {item['epa']:.4f}")

if __name__ == "__main__":
    main()
