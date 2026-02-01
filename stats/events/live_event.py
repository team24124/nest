import time
import requests

from stats.data import get_auth, get_config, get_season_score_parser
from stats.calculations.epa_live import update_epa_from_match
from stats.teams.Team import Team
from stats.data.live_epa_state import live_epa_state
import time

def poll_live_event_and_update_epa(event_code: str) -> None:
    try:
        # 1. Call FIRST API
        # matches = get_live_matches(event_code)

        # 2. Call Nighthawks EPA calculator
        # epa_results = calculate_epa(matches)

        # MOCK example for now
        epa_results = {
            1234: 12.3,
            5678: 9.8
        }

        live_epa_state["epa_by_team"] = epa_results
        live_epa_state["last_update"] = time.strftime("%H:%M:%S")
        live_epa_state["status"] = "running"

    except Exception as e:
        live_epa_state["status"] = f"error: {e}"


def _resolve_match_teams(
    season: int,
    event_code: str,
    match_number: int,
    team_data: dict[int, Team]
):
    """
    Resolve red and blue teams for a specific match number.
    """

    response = requests.get(
        f"https://ftc-api.firstinspires.org/v2.0/{season}/matches/{event_code}",
        auth=get_auth()
    )

    matches = response.json().get("matches", [])

    match = next(
        (m for m in matches if m["matchNumber"] == match_number),
        None
    )

    if not match:
        return [], []

    red = []
    blue = []
    for team in match["teams"]:
        team_number = team["teamNumber"]
        if team_number not in team_data:
            continue

        if team["station"].startswith("Red"):
            red.append(team_data[team_number])
        else:
            blue.append(team_data[team_number])

    return red, blue


def push_epa_to_nighthawks(teams: list[Team]):
    """
    Push updated EPA values to Nighthawks Stats API.
    """

    for team in teams:
        payload = {
            "teamNumber": team.team_number,
            "epaTotal": team.epa_total,
            "epaAuto": team.epa_auto_total,
            "epaTele": team.epa_tele_total,
            "gamesPlayed": team.games_played
        }

        try:
            requests.post(
                "https://nighthawks-stats.vercel.app/api/epa/update",
                json=payload,
                timeout=3
            )
        except Exception:
            pass
