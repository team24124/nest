import tkinter as tk
import webbrowser

from app import Controller
from app.widget.VerticalScrolledFrame import VerticalScrolledFrame
from stats.team import Team


class TeamStatWindow(tk.Toplevel):
    def __init__(self, root, controller: Controller, team: Team):
        super().__init__(root)
        self.title(f"{team.team_number} - Nighthawks Event Statistics Tool (NEST)")
        self.geometry("600x400")
        #self.minsize(300, 400)
        self.resizable(width=False, height=False)
        icon = tk.PhotoImage(file='./app/favicon.png')
        self.wm_iconphoto(False, icon)

        # Title
        tk.Label(self, text=f"{team.name} ({team.team_number})", font=("Segoe UI", 9, 'bold')).grid(row=0, column=0,
                                                                                                    padx=5, pady=5,
                                                                                                    sticky="w")
        # Location Info
        locale_frame = tk.Frame(self)
        tk.Label(locale_frame, text=f"{team.country}, {team.state_prov}, {team.city} (Home Region: {team.home_region})").pack(side="left", anchor="w")
        locale_frame.grid(row=1, column=0, padx=5, sticky="w")

        # Open FTC Events Page
        tk.Button(self, text=f"View on FTC Events",
                  command=lambda: webbrowser.open_new(
                      f"https://ftc-events.firstinspires.org/team/{team.team_number}")).grid(row=2, column=0, padx=5,
                                                                                             pady=5, sticky="w")

        # Statistics
        event_code = controller.shared_data["event_code"]
        stats = VerticalScrolledFrame(self)
        tk.Label(stats.interior, text=f"Ranking at Event: {team.rankings[event_code]}").pack(side="top", anchor="w",
                                                                                             padx=5, pady=5)
        tk.Label(stats.interior, text=f"EPA: {team.epa_total}").pack(side="top", anchor="w", padx=5, pady=5)
        tk.Label(stats.interior, text=f"Auto EPA: {team.auto_total}").pack(side="top", anchor="w", padx=5, pady=5)
        tk.Label(stats.interior, text=f"Tele EPA: {team.tele_total}").pack(side="top", anchor="w", padx=5, pady=5)
        tk.Label(stats.interior, text=f"OPR: {team.opr}").pack(side="top", anchor="w", padx=5, pady=5)
        tk.Label(stats.interior, text=f"Auto OPR: {team.opr_auto}").pack(side="top", anchor="w", padx=5, pady=5)
        tk.Label(stats.interior, text=f"Tele OPR: {team.opr_tele}").pack(side="top", anchor="w", padx=5, pady=5)
        tk.Label(stats.interior, text=f"Endgame OPR: {team.opr_end}").pack(side="top", anchor="w", padx=5, pady=5)

        stats.grid(row=3, column=0, padx=5, pady=5, sticky="news")

        self.columnconfigure(0, weight=1)
        self.rowconfigure(3, weight=1)
