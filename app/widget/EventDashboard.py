from tkinter import ttk
from threading import Thread
import tkinter as tk
from app import Controller
from stats.event import Event, get_all_events, get_all_events_by_teams
import webbrowser


class EventDashboard(tk.Frame):
    def __init__(self, root: tk.Tk, controller: Controller):
        super().__init__(root)
        self.controller = controller
        self.root = root

        title_label = tk.Label(self, text="Event Overview", font=("Segoe UI", 11))

        self.active_label = tk.Label(self, text=f"Active Event: {controller.shared_data["event_code"]}")
        self.name_label = tk.Label(self, text=f"")
        self.location_label = tk.Label(self, text=f"")
        self.num_teams_label = tk.Label(self, text=f"Number of Teams: ")

        title_label.pack(side="top", anchor="w")
        self.active_label.pack(side="top", anchor="w")

        self.bind('<<event_code_updated>>', lambda event: self.handle_event_update(event))

    def handle_event_update(self, e):
        event_code = self.controller.shared_data["event_code"]
        event: Event = self.controller.shared_data["event"]

        self.active_label.config(text=f"Active Event: {event_code}")
        self.name_label.config(text=f"{event.name}", cursor="hand2")
        self.location_label.config(text=f"{event.country}, {event.state_province}, {event.city}")
        self.num_teams_label.config(text=f"Number of Teams: {len(event.team_list)}")

        self.name_label.bind("<Button-1>", lambda e2: webbrowser.open_new(f"https://ftc-events.firstinspires.org/2024/{event_code}"))

        self.active_label.pack()
        self.name_label.pack()
        self.location_label.pack()
        self.num_teams_label.pack()
