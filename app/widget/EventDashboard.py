from tkinter import ttk
from threading import Thread
import tkinter as tk
from app import Controller
from app.window.TeamWindow import TeamsWindow
from stats.event import Event, get_all_events, get_all_events_by_teams
import webbrowser


class EventDashboard(tk.Frame):
    def __init__(self, root: tk.Tk, controller: Controller):
        super().__init__(root)
        self.controller = controller
        self.root = root

        title_label = tk.Label(self, text="Event Overview", font=("Segoe UI", 11))
        self.active_label = tk.Label(self, text=f"Active Event: {controller.shared_data["event_code"]}")

        self.event_info_frame = tk.Frame(self)

        self.name_label = tk.Label(self.event_info_frame, text=f"")
        self.location_label = tk.Label(self.event_info_frame, text=f"")
        self.num_teams_label = tk.Label(self.event_info_frame, text=f"Number of Teams: ")

        self.teams_button = tk.Button(self, text="View Teams", command=self.on_click_view_teams, state="disabled")

        title_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.active_label.grid(row=1, column=0, padx=5, sticky="w")

        # TODO: Alliance Score Prediction

        self.name_label.pack()
        self.location_label.pack()
        self.num_teams_label.pack()

        self.columnconfigure(0, weight=1)
        self.rowconfigure(3, weight=1)

        self.bind('<<event_code_updated>>', lambda event: self.handle_event_update(event))
        self.bind('<<team_stats_updated>>', lambda event: self.handle_stats_update(event))

    def on_click_view_teams(self):
        TeamsWindow(self.root, self.controller)

    def handle_event_update(self, e):
        event_code = self.controller.shared_data["event_code"]
        event: Event = self.controller.shared_data["event"]

        self.active_label.config(text=f"Active Event: {event_code}")
        self.name_label.config(text=f"{event.name}", cursor="hand2", font=("Segoe UI", 9,'underline'))
        self.location_label.config(text=f"{event.country}, {event.state_province}, {event.city}")
        self.num_teams_label.config(text=f"Number of Teams: {len(event.team_list)}")

        self.name_label.bind("<Button-1>", lambda e2: webbrowser.open_new(f"https://ftc-events.firstinspires.org/2024/{event_code}"))

        self.event_info_frame.grid(row=2, column=0, padx=5, pady=5, sticky="news")
        self.teams_button.grid(row=3, column=0, padx=5, pady=5, sticky="sw")

    def handle_stats_update(self, e):
        self.teams_button.config(state="normal")
