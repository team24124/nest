import tkinter as tk
from tkinter import ttk

from app import Controller
from app.widget.TeamProfile import TeamProfile
from app.widget.VerticalScrolledFrame import VerticalScrolledFrame
from app.window.TeamStatWindow import TeamStatWindow

class TeamsWindow(tk.Toplevel):
    def __init__(self, root, controller: Controller):
        super().__init__(root)
        self.controller = controller
        self.title("Teams - Nighthawks Event Statistics Tool (NEST)")
        self.geometry("500x500")
        self.minsize(500, 500)
        icon = tk.PhotoImage(file='./app/favicon.png')
        self.wm_iconphoto(False, icon)

        teams_list = controller.shared_data["teams"]
        event_code = controller.shared_data["event_code"]

        tk.Label(self, text=f"View Teams At Event ({event_code})").pack(side="top", anchor="w", padx=5, pady=5)
        frame = VerticalScrolledFrame(self)

        for team in teams_list.values():
            TeamProfile(frame.interior, controller, team).pack(anchor="center", expand=True, fill="both")

        frame.pack(fill="both", expand=True)

    def view_team(self, team_number):
        teams_list = self.controller.shared_data["teams"]
        TeamStatWindow(self, self.controller, teams_list[team_number])
