from itertools import islice
from tkinter import StringVar

from stats.teams.Team import Team


def get_top_n_teams(number_of_teams, teams: dict[int, Team], stat: StringVar):
    sorted_teams = sorted(teams, key=lambda x: vars(teams[x])[stat.get()][-1], reverse=True)

    top_teams = list(sorted_teams)[:number_of_teams]
    return {top_team: teams[top_team] for top_team in top_teams} # get top number of teams from sorted list