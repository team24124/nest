from stats.calculations.epa import calculate_epa
from stats.data.scores import MatchData
from stats.teams.Team import Team

def update_epa_from_match(
    match: MatchData,
    red_teams: list[Team],
    blue_teams: list[Team]
):
    teams = red_teams + blue_teams

    # Skip if already processed
    match_name = match.get_match_name()
    if match_name in red_teams[0].matches:
        return

    # Update games played first
    for team in teams:
        team.update_game_played(match_name)

    games_played = sum(t.games_played for t in teams) / 4

    # Total EPA
    red_epa = sum(t.epa_total for t in red_teams)
    blue_epa = sum(t.epa_total for t in blue_teams)

    change_red, change_blue = calculate_epa(
        red_epa,
        blue_epa,
        match.red_alliance.total_score,
        match.blue_alliance.total_score,
        games_played
    )

    # Auto
    red_auto_epa = sum(t.epa_auto_total for t in red_teams)
    blue_auto_epa = sum(t.epa_auto_total for t in blue_teams)

    change_red_auto, change_blue_auto = calculate_epa(
        red_auto_epa,
        blue_auto_epa,
        match.red_alliance.auto_score,
        match.blue_alliance.auto_score,
        games_played
    )

    # Tele
    red_tele_epa = sum(t.epa_tele_total for t in red_teams)
    blue_tele_epa = sum(t.epa_tele_total for t in blue_teams)

    change_red_tele, change_blue_tele = calculate_epa(
        red_tele_epa,
        blue_tele_epa,
        match.red_alliance.tele_score,
        match.blue_alliance.tele_score,
        games_played
    )

    for team in red_teams:
        team.update_epa(change_red, change_red_auto, change_red_tele)

    for team in blue_teams:
        team.update_epa(change_blue, change_blue_auto, change_blue_tele)

    for team in red_teams + blue_teams:
        if not hasattr(team, 'epa_history'):
            team.epa_history = []

        # Capture the EPA at this specific point in time
        team.epa_history.append(team.epa_total)