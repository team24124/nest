# Convert to json file for JavaScript
import json

def flatten_team_data_team(team):
    return {
        'team_number': team.team_number,
        'country': team.country,
        'state_prov': team.state_prov,
        'city': team.city,
        'home_region': team.home_region,
        'games_played': team.games_played,
        'epa_total': team.epa_total,
        'auto_total': team.auto_total,
        'tele_total': team.tele_total,
        'historical_epa': team.historical_epa,
        'historical_auto_epa': team.historical_auto_epa,
        'historical_tele_epa': team.historical_tele_epa,
        'opr_total_vals': team.opr_total_vals,
        'opr_auto_vals': team.opr_auto_vals,
        'opr_tele_vals': team.opr_tele_vals,
        'opr_end_vals': team.opr_end_vals,
        'opr': team.opr,
        'opr_auto': team.opr_auto,
        'opr_tele': team.opr_tele,
        'opr_end': team.opr_end
    }

def save_team_data(teams):
    # Flatten all team objects (assuming teams is a dict)
    data = {team_number: flatten_team_data_team(team) for team_number, team in teams.items()}

    # Save to file
    with open("world_team_data_latest.json", "w") as f:
        json.dump(data, f, indent=2)