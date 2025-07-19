import sys
import tkinter.messagebox
import traceback
from queue import Queue
from concurrent.futures import ThreadPoolExecutor
from tkinter import ttk, filedialog
import tkinter as tk
from app.Controller import Controller, broadcast_event
from stats.averages import get_start_avg
from stats.calculations import update_teams_at_event
from stats.events.Event import Event

from stats.events import get_event, get_division_events
from stats.export import export_team_data
from stats.teams import get_team_data_from_event
from stats.teams.Team import Team


class MainControl(tk.Frame):
    def __init__(self, root: tk.Tk, controller: Controller):
        super().__init__(root)
        self.controller = controller
        self.root = root
        self.executor = ThreadPoolExecutor(max_workers=1)
        title_label = tk.Label(self, text="Main Control", font=("Segoe UI", 11))

        # Event Code Entry & Button
        event_frame = tk.Frame(self)
        event_label = tk.Label(event_frame, text="Event Code", font=("Segoe UI", 9))
        self.event_entry = ttk.Entry(event_frame, width=20)
        self.event_submit = tk.Button(event_frame, text="Check", command=self.on_click)

        export_frame = tk.Frame(self)
        self.export_button = tk.Button(export_frame, text="Export to JSON", state="disabled", command=self.export_json)
        self.refresh_button = tk.Button(export_frame, text="Refresh", state="disabled", command=self.update_data)

        event_label.grid(row=0, column=0, padx=5)
        self.event_entry.grid(row=0, column=1, padx=5)
        self.event_submit.grid(row=0, column=2, padx=5)

        # Processing Label
        self.processing_label = tk.Label(self, text="Processing Data...")

        title_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        event_frame.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        export_frame.grid(row=3, column=0, padx=5, pady=5, sticky="sw")

        # Layout for export frame
        self.export_button.grid(row=0, column=0, padx=5, pady=5, sticky="sw")
        self.refresh_button.grid(row=0, column=1, padx=5, pady=5, sticky="sw")

        self.columnconfigure(0, weight=1)
        self.rowconfigure(3, weight=1)

        self.bind('<<event_code_updated>>', lambda event: self.handle_event_update(event))

    def on_click(self):
        event_code = self.event_entry.get()
        event = get_event(event_code)

        if event_code != "":
            self.controller.shared_data["event_code"] = event_code
            self.controller.shared_data["event"] = event
            broadcast_event(self.root, "<<event_code_updated>>")
        else:
            tkinter.messagebox.showinfo(title="No Event Found",
                                        message=f"The event code you entered ({event_code}) could not be found")
            print(f"The event ({event_code}) you entered could not be found.", file=sys.stderr)

    def export_json(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            title="Save JSON file"
        )

        team_data = self.controller.shared_data["teams"]

        export_team_data(team_data, file_path)
        pass


    def handle_event_update(self, e):
        event: Event = self.controller.shared_data["event"]
        self.get_data(event)
        pass


    def get_data(self, event: Event):
        print("Getting data...")
        future = self.executor.submit(get_team_data_from_event, event.event_code)

        # Disable relevant GUI components
        self.processing_label.grid(row=3, column=1, padx=5, pady=5, sticky="se")
        self.event_submit.config(state="disabled")
        self.event_entry.config(state="disabled")

        self.after(100, self.check_future, future)
        pass

    def update_data(self):
        print("Updating data...")
        event = self.controller.shared_data["event"]
        team_data = self.controller.shared_data["teams"]

        events = [ event ] + get_division_events(event.event_code)
        print(events)
        avg_total, avg_auto, avg_tele = get_start_avg()
        for event in events:
            update_teams_at_event(event, team_data, avg_total, avg_auto, avg_tele)

        print("Teams updated.")
        self.controller.shared_data["teams"] = team_data

    def check_future(self, future):
        if future.done():
            try:
                result: dict[int, Team] = future.result()
                self.processing_label.grid_forget()

                # Reenable GUI components
                self.event_submit.config(state="normal")
                self.event_entry.config(state="normal")
                self.export_button.config(state="normal")
                self.refresh_button.config(state="normal")

                # Move result team data into shared_data
                self.controller.shared_data["teams"] = result

                self.update_data()

                # Send virtual event to notify graphs to enable
                broadcast_event(self.root, "<<team_stats_updated>>")
                print("Team data successfully retrieved.")

                # print(result)
            except Exception as e:
                traceback.print_exception(type(e), e, e.__traceback__)
        else:
            self.after(100, self.check_future, future)
        pass
