import csv
import os
from stats.data.scores import EventData

def import_manual_data(csv_path: str):
    """
    Reads manual match data from a CSV file and prepares data structures for OPR/EPA calculation.
    
    Expected CSV Format:
    Team1,Team2,TotalScore,AutoScore,TeleScore,EndScore
    
    :param csv_path: Path to the CSV file.
    :return: Tuple (team_list, game_matrix, event_data)
    """
    
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    matches = []
    unique_teams = set()

    # Pass 1: Read all data and identify unique teams
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
             # Basic cleaning and type conversion
            t1 = int(row['Team1'])
            t2 = int(row['Team2'])
            
            # Add to unique set
            unique_teams.add(t1)
            unique_teams.add(t2)
            
            # Store row data for second pass
            matches.append({
                'teams': [t1, t2],
                'scores': {
                    'total': float(row.get('TotalScore', 0)),
                    'auto': float(row.get('AutoScore', 0)),
                    'tele': float(row.get('TeleScore', 0)),
                    'end': float(row.get('EndScore', 0))
                }
            })

    # Convert set to sorted list for consistent matrix indexing
    team_list = sorted(list(unique_teams))
    
    # Initialize structures
    game_matrix = []
    event_data = EventData()

    # Pass 2: Build Matrix and EventData
    season = 2025 # Default
    for i in range(0, len(matches), 2):
        m1 = matches[i]
        # Check if there's a pair (Blue alliance)
        if i + 1 < len(matches):
            m2 = matches[i+1]
        else:
            # Create a dummy opponent if the last match is missing a pair
            m2 = {'teams': [0, 0], 'scores': {'total': 0, 'auto': 0, 'tele': 0, 'end': 0}}

        # matrix rows for both alliances
        for m in [m1, m2]:
            matrix_row = [0] * len(team_list)
            for team in m['teams']:
                if team in team_list:
                    index = team_list.index(team)
                    matrix_row[index] = 1
            game_matrix.append(matrix_row)

        # Create MatchData for EPA
        from stats.data.scores import AllianceScoreData, MatchData
        red_asd = AllianceScoreData(m1['scores']['total'], m1['scores']['auto'], m1['scores']['tele'], m1['scores']['end'])
        blue_asd = AllianceScoreData(m2['scores']['total'], m2['scores']['auto'], m2['scores']['tele'], m2['scores']['end'])
        
        match_obj = MatchData(season, "MANUAL", (i//2)+1, "Q", red_asd, blue_asd)
        event_data.add(match_obj)

    return team_list, game_matrix, event_data
