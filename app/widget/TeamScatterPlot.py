import sys
import tkinter as tk
import tkinter.messagebox
from tkinter import ttk
from app import Controller
from app.widget.NumberEntry import NumberEntry
from graphing.graph import make_bar_graph, make_team_scatter
from graphing.search import get_top_n_teams
from stats.event import Event
from stats.team import Team


class TeamScatterPlot(tk.Frame):
    def __init__(self, root: tk.Tk, controller: Controller):
        super().__init__(root)
        self.controller = controller
        self.root = root

        self.valid_team_options = ["historical_epa", "historical_auto_epa", "historical_tele_epa", "opr_total_vals",
                                   "opr_auto_vals", "opr_tele_vals", "opr_end_vals"]
        self.selected_option = tk.StringVar(value=self.valid_team_options[0])

        title_label = tk.Label(self, text="Historical Statistics (Line Graph)", font=("Segoe UI", 11))

        stat_frame = tk.Frame(self)
        stat_label = tk.Label(stat_frame, text="Statistic")
        stat_options = ttk.OptionMenu(stat_frame, self.selected_option, self.valid_team_options[0], *self.valid_team_options)

        team_frame = tk.Frame(self)
        team_label = tk.Label(team_frame, text="Teams")
        self.team_entry = tk.Entry(team_frame, width=50)

        num_team_frame = tk.Frame(self)
        num_team_label = tk.Label(num_team_frame, text="Include top n teams: ")
        self.num_team_entry = NumberEntry(num_team_frame)

        self.graph_button = tk.Button(self, text="Graph", state="disabled", width=20, height=2, command=self.make_graph)

        stat_label.grid(row=0, column=0, padx=5, pady=5)
        stat_options.grid(row=0, column=1, padx=5, pady=5)

        team_label.grid(row=0, column=0, padx=5, pady=5)
        self.team_entry.grid(row=0, column=1, padx=5, pady=5)

        num_team_label.grid(row=0, column=0, padx=5, pady=5)
        self.num_team_entry.grid(row=0, column=1, padx=5, pady=5)

        title_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        stat_frame.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        team_frame.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        num_team_frame.grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.graph_button.grid(row=4, column=0, padx=5, pady=5, sticky="sw")

        self.rowconfigure(4, weight=1)

        self.bind('<<team_stats_updated>>', lambda event: self.handle_stats_update(event))

    def handle_stats_update(self, e):
        self.graph_button.config(state="normal")

    def make_graph(self):
        event: Event = self.controller.shared_data["event"]
        team_data: dict[str, Team] = self.controller.shared_data["teams"]
        n = int(self.num_team_entry.get())

        selected_team_numbers = self.team_entry.get().replace(" ", "").split(",")
        selected_teams = get_top_n_teams(n, team_data, self.selected_option)

        if self.team_entry.get() != "":
            for team_number in selected_team_numbers:
                if team_number in team_data.keys():
                    selected_teams[team_number] = team_data[team_number]
                else:
                    err_msg = f"One of the team numbers ({team_number}) you entered is not present at the current event"
                    print(err_msg, file=sys.stderr)
                    tkinter.messagebox.showerror(title="Team not found.", message=err_msg)
                    return

        make_team_scatter(event, selected_teams, self.selected_option)
