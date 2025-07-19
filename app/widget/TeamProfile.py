import tkinter as tk

from app import Controller
from app.window.TeamStatWindow import TeamStatWindow
from stats.teams.Team import Team


class TeamProfile(tk.Frame):
    def __init__(self, root: tk.Tk, controller: Controller, team: Team):
        super().__init__(root)
        self.controller = controller
        self.root = root

        self.team = team

        tk.Label(self, text=team.team_number).pack(side="left", anchor='w', pady=5, padx=5)
        tk.Label(self, text=team.name).pack(side="left", anchor="w", pady=5, padx=5)
        tk.Button(self, text="View", command=self.view_team).pack(side="left",anchor="w", pady=5,padx=5)

    def view_team(self):
        TeamStatWindow(self, self.controller, self.team)