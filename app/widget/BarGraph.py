import tkinter as tk
from tkinter import ttk
from app import Controller
from graphing.graph import make_bar_graph
from stats.event import Event


class BarGraph(tk.Frame):
    def __init__(self, root: tk.Tk, controller: Controller):
        super().__init__(root)
        self.controller = controller
        self.root = root

        self.valid_team_options = ["epa_total", "auto_total", "tele_total", "opr", "opr_auto", "opr_tele", "opr_end"]
        self.selected_option = tk.StringVar(value=self.valid_team_options[0])

        stat_frame = tk.Frame(self)

        title_label = tk.Label(self, text="Teams vs. Statistic (Bar Graph)", font=("Segoe UI", 11))
        stat_label = tk.Label(stat_frame, text="Statistic")
        stat_options = ttk.OptionMenu(stat_frame, self.selected_option, self.valid_team_options[0], *self.valid_team_options)


        self.graph_button = tk.Button(self, text="Graph", state="disabled", width=20, height=2, command=self.make_graph)

        stat_label.grid(row=0, column=0, padx=5, pady=5)
        stat_options.grid(row=0, column=1, padx=5, pady=5)

        title_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        stat_frame.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.graph_button.grid(row=3, column=0, padx=5, pady=5, sticky="w")

        self.bind('<<team_stats_updated>>', lambda event: self.handle_stats_update(event))

    def handle_stats_update(self, e):
        self.graph_button.config(state="normal")

    def make_graph(self):
        event: Event = self.controller.shared_data["event"]
        team_data = self.controller.shared_data["teams"]
        make_bar_graph(event, team_data, self.selected_option)
