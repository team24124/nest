# Convert to json file for JavaScript
import json
import tkinter.messagebox
import traceback

from stats.event import Event


def flatten_team_data_team(team):
    return {
        'team_number': team.team_number,
        'country': team.country,
        'state_prov': team.state_prov,
        'city': team.city,
        'home_region': team.home_region,
        'games_played': team.games_played,
        'epa_total': team.epa_total,
        'auto_total': team.epa_auto_total,
        'tele_total': team.epa_tele_total,
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

def flatten_event_data(event: Event):
    return {
        'event_code': event.event_code,
        'event_name': event.name,
        'country': event.country,
        'state_province': event.state_province,
        'city': event.city,
        'team_list': list(event.team_list.keys())
    }

def save_event_data(events, path):
    # Flatten event objects (assuming events is a dict)
    data = {event_code: flatten_event_data(event) for event_code, event in events.items()}

    # Save to file
    if path:
        try:
            with open(path, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            traceback.print_exception(type(e), e, e.__traceback__)
            tkinter.messagebox.showerror(title="Export to JSON (Events)", message="Something went wrong while saving the file")

def save_team_data(teams, path):
    # Flatten all team objects (assuming teams is a dict)
    data = {team_number: flatten_team_data_team(team) for team_number, team in teams.items()}

    # Save to file
    if path:
        try:
            with open(path, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            traceback.print_exception(type(e), e, e.__traceback__)
            tkinter.messagebox.showerror(title="Export to JSON", message="Something went wrong while saving the file")