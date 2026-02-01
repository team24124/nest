from tkinter import StringVar, BooleanVar

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from stats.teams import Team


def make_bar_graph(event, teams, stat: StringVar):
    data = []
    stat_value = stat.get()
    for team in teams.values():
        stats = vars(team)
        data.append((str(team.team_number), stats[stat_value]))

    # Sort data into descending order
    data.sort(reverse=True, key=lambda x: x[1])
    title = f"{stat_value} for teams at {event.name} ({event.event_code})"

    df = pd.DataFrame(data, columns=["Team Number", stat.get()])
    fig = px.bar(data_frame=df, x="Team Number", y=stat.get(), title=title, template="simple_white")
    fig.show()


def make_team_scatter(event, teams: dict[int, Team], only_event_matches: BooleanVar, stat: StringVar):
    figure = go.Figure()
    stat_value = stat.get()

    # Add a line for each selected team
    for team in teams.values():
        first_index = -1
        last_index = -1

        # If only showing matches from this event look for the first and last index of those matches
        if only_event_matches.get():
            for index, match in enumerate(team.matches):
                is_event_match = event.event_code in match
                if is_event_match:
                    if first_index == -1: first_index = index
                    if index > last_index: last_index = index

        stats = vars(team)
        figure.add_trace(go.Scatter(
            y=stats[stat_value][first_index:last_index+1] if only_event_matches.get() else stats[stat_value],
            mode='markers+lines',
            name=team.team_number,
            line=dict(shape='spline')
        ))

    figure.update_layout(
        title=dict(text=f"{stat_value} of teams at {event.name} ({event.event_code})"),
        xaxis=dict(
            title=dict(text="Games Played")
        ),
        yaxis=dict(
            title=dict(text=stat_value)
        ),
        legend=dict(
            title=dict(text="Teams")
        ),
    )
    figure.show()


def make_stat_scatter(event, teams, event_rankings, stat_x: StringVar, stat_y: StringVar):
    data_x = []
    data_y = []
    team_numbers = []

    stat_x_value = stat_x.get()
    stat_y_value = stat_y.get()

    title = f"{stat_x_value} vs. {stat_y_value} of teams at {event.name} ({event.event_code})"

    for team in teams.values():
        stats = vars(team)
        if stat_x_value == 'event_ranking':
            if event_rankings:
                data_x.append(event_rankings[team.team_number])
            else:
                raise ValueError(
                    "You tried to view rankings on an event with divisions. Use individual division events to do this instead.")
        else:
            data_x.append(stats[stat_x_value])

        if stat_y_value == 'event_ranking':
            if event_rankings:
                data_y.append(event_rankings[team.team_number])
            else:
                raise ValueError(
                    "You tried to view rankings on an event with divisions. Use individual division events to do this instead.")
        else:
            data_y.append(stats[stat_y_value])
        team_numbers.append(team.team_number)

    figure = go.Figure(data=go.Scatter(
        x=data_x,
        y=data_y,
        mode='markers+text',
        text=team_numbers,
        textposition='bottom center',
        marker=dict(size=10)
    ))
    figure.update_layout(
        title=dict(text=title),
        xaxis=dict(
            title=dict(text=stat_x_value)
        ),
        yaxis=dict(
            title=dict(text=stat_y_value)
        ),
        legend=dict(
            title=dict(text="Teams")
        ),
    )

    figure.show()


def make_live_epa_trend(event, teams: dict[int, Team], target_team_numbers: list):
    """
    Creates an interactive Plotly line graph showing the EPA trend
    for specific teams during the live event.
    """
    figure = go.Figure()

    # Inside graphing/graph.py
    for t_num in target_team_numbers:
        team = teams.get(int(t_num))
        if team and team.historical_epa:  # Use the correct name from Team.py!
            figure.add_trace(go.Scatter(
                y=team.historical_epa,
                mode='lines+markers',
                name=f"Team {t_num}"
            ))

    figure.update_layout(
        title=dict(text=f"Live EPA Progression: {event.name} ({event.event_code})"),
        xaxis=dict(title=dict(text="Matches Played")),
        yaxis=dict(title=dict(text="EPA Value")),
        template="simple_white",
        hovermode="x unified"
    )

    figure.show()
