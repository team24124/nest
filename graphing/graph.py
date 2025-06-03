from tkinter import StringVar

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

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
    fig = px.bar(data_frame=df, x="Team Number", y=stat.get(), title=title)
    fig.show()

def make_team_scatter(event, teams, stat: StringVar):
    figure = go.Figure()
    stat_value = stat.get()
    for team in teams.values():
        stats = vars(team)
        figure.add_trace(go.Scatter(y=stats[stat_value], mode='markers+lines', name=team.team_number))

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


def make_stat_scatter(event, teams, stat_x: StringVar, stat_y: StringVar):
    data_x = []
    data_y = []
    team_numbers = []

    stat_x_value = stat_x.get()
    stat_y_value = stat_y.get()

    title = f"{stat_x_value} vs. {stat_y_value} of teams at {event.name} ({event.event_code})"

    for team in teams.values():
        stats = vars(team)
        data_x.append(stats[stat_x_value])
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