import os
import json

def main():
    # Load Data
    data_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "CAABCMP1117.json")
    
    if not os.path.exists(data_file):
        print(f"Error: Data file {data_file} not found.")
        return

    with open(data_file, 'r') as f:
        data = json.load(f)

    # Process teams
    teams_list = []
    for t_num, d in data.items():
        t_total = d.get('epa_total', 0)
        t_auto = d.get('auto_epa_total', 0)
        t_tele = d.get('tele_epa_total', 0)
        t_end = t_total - t_auto - t_tele
        t_opr = d.get('opr', 0)
        t_name = d.get('team_name', 'Unknown')
        
        teams_list.append({
            "num": t_num,
            "name": t_name,
            "total": t_total,
            "auto": t_auto,
            "tele": t_tele,
            "end": t_end,
            "opr": t_opr
        })

    # Sort by EPA Total descending
    teams_list.sort(key=lambda x: x['total'], reverse=True)

    # Print Results
    print(f"Event Predicted Rankings")
    print("-" * 60)
    
    for i, team in enumerate(teams_list, 1):
        line = f"{i}. {team['num']} ({team['name']}) - "
        line += f"EPA: {team['total']:.1f} "
        line += f"Auto: {team['auto']:.1f} "
        line += f"Tele: {team['tele']:.1f} "
        line += f"End: {team['end']:.1f} "
        line += f"OPR: {team['opr']:.1f}"
        print(line)

    print("-" * 60)
    print(f"Total teams ranked: {len(teams_list)}")

if __name__ == "__main__":
    main()
