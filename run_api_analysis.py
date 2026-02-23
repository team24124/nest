
import os
import sys

# Ensure current directory is in path
sys.path.append(os.getcwd())

from stats.calculations import update_teams_at_event
from stats.averages import get_start_avg
from stats.events import get_event_by_code
from stats.data import get_config

def main():
    event_code = "CAABCAQ"
    print(f"Fetching data for event: {event_code} via API...")

    try:
        event = get_event_by_code(event_code)
    except Exception as e:
        print(f"Error fetching event: {e}")
        return

    if not event:
        print(f"Event {event_code} found, but might be filtered out by event type or not exist.")
        from stats.events import get_event
        try:
            event = get_event(event_code)
        except Exception as e:
             print(f"Could not force fetch event: {e}")
             return

    print(f"Event Found: {event.name} ({event.city}, {event.state_province})")
    print(f"Teams: {len(event.team_list)}")

    team_data = {}
    
    # Pre-populate team_data with blank Team objects to ensure calculate_opr has targets
    # Actually update_teams_at_event does this:
    # for team_number in team_number_list: if team_number not in team_data.keys(): team = get_team_from_ftc...
    # So we can pass an empty dict.

    print("Fetching matches and calculating stats...")
    avg_total, avg_auto, avg_tele = get_start_avg()
    
    try:
        update_teams_at_event(event, team_data, avg_total, avg_auto, avg_tele)
    except Exception as e:
        print(f"Error updating teams: {e}")
        import traceback
        traceback.print_exc()
        return

    print(f"\n{'Team':<8} | {'OPR':<12} | {'EPA':<12}")
    print("-" * 40)
    
    # Sort teams by Total OPR (team.opr)
    sorted_teams = sorted(team_data.values(), key=lambda t: t.opr, reverse=True)

    for team in sorted_teams:
        print(f"{team.team_number:<8} | {team.opr:<12.4f} | {team.epa_total:<12.4f}")

if __name__ == "__main__":
    main()
