import tkinter as tk
from tkinter import ttk
from app import Controller
from graphing.graph import make_stat_scatter
from stats.events import get_event_rankings
from stats.events.Event import Event


class StatScatterPlot(tk.Frame):
    def __init__(self, root: tk.Tk, controller: Controller):
        super().__init__(root)
        self.controller = controller
        self.root = root

        self.valid_x_options = ["epa_total", "epa_auto_total", "epa_tele_total", "opr", "opr_auto", "opr_tele", "opr_end", "event_ranking"]
        self.selected_x_option = tk.StringVar(value="epa_total")

        self.valid_y_options = ["epa_total", "epa_auto_total", "epa_tele_total", "opr", "opr_auto", "opr_tele", "opr_end", "event_ranking"]
        self.selected_y_option = tk.StringVar(value="opr")

        title_label = tk.Label(self, text="Statistic vs. Statistic (Scatterplot)", font=("Segoe UI", 11))

        stat_frame = tk.Frame(self)
        stat_x_label = tk.Label(stat_frame, text="X Axis")
        stat_y_label = tk.Label(stat_frame, text="Y Axis")
        stat_x_options = ttk.OptionMenu(stat_frame, self.selected_x_option, "epa_total", *self.valid_x_options)
        stat_y_options = ttk.OptionMenu(stat_frame, self.selected_y_option, "opr", *self.valid_y_options)
        rank_disclaimer = tk.Label(self, text="Rankings only work on events WITHOUT divisions. View division rankings by their event.")

        self.graph_button = tk.Button(self, text="Graph", state="disabled", width=20, height=2, command=self.make_graph)

        stat_x_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        stat_x_options.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        stat_y_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        stat_y_options.grid(row=1, column=1, padx=5, pady=5, sticky="w")


        title_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        stat_frame.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.graph_button.grid(row=3, column=0, padx=5, pady=5, sticky="sw")
        rank_disclaimer.grid(row=4, column=0, padx=5, pady=5, sticky="w")

        self.rowconfigure(3, weight=1)

        self.bind('<<team_stats_updated>>', lambda event: self.handle_stats_update(event))

    def handle_stats_update(self, e):
        self.graph_button.config(state="normal")

    def make_graph(self):
        event: Event = self.controller.shared_data["event"]
        team_data = self.controller.shared_data["teams"]
        event_rankings = get_event_rankings(event.event_code)
        make_stat_scatter(event, team_data, event_rankings, self.selected_x_option, self.selected_y_option)
