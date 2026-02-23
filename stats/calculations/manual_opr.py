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

    print("Calculating OPR...")
    try:
        # Calculate OPR
        results = calculate_opr(game_matrix, event_data)
        total_oprs = results[0]
    except Exception as e:
        print(f"Error calculating: {e}")
        return

    print("\nOPR")
    
    # Combine data for sorting
    combined_results = []
    for i, t_num in enumerate(team_list):
        combined_results.append({
            'num': t_num,
            'opr': total_oprs[i]
        })
    
    # Sort by OPR descending
    combined_results.sort(key=lambda x: x['opr'], reverse=True)

    for item in combined_results:
        print(f"{item['num']:<6} : {item['opr']:.4f}")

if __name__ == "__main__":
    main()
