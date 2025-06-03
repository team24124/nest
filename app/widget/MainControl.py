import sys
import tkinter.messagebox
import traceback
from queue import Queue
from concurrent.futures import ThreadPoolExecutor
from tkinter import ttk, filedialog
import tkinter as tk
from app.Controller import Controller, broadcast_event
from stats.event import validate_event, Event
from stats.export import save_team_data
from stats.opr_epa import calculate_event_epa_opr
from stats.team import Team


class MainControl(tk.Frame):
    def __init__(self, root: tk.Tk, controller: Controller):
        super().__init__(root)
        self.controller = controller
        self.root = root
        self.executor = ThreadPoolExecutor(max_workers=1)
        title_label = tk.Label(self, text="Main Control", font=("Segoe UI", 11))

        event_frame = tk.Frame(self)
        event_label = tk.Label(event_frame, text="Event Code", font=("Segoe UI", 9))
        self.event_entry = ttk.Entry(event_frame, width=20)
        self.event_submit = tk.Button(event_frame, text="Check", command=self.on_click)

        region_label = tk.Label(event_frame, text="Region")
        self.region_entry = ttk.Entry(event_frame, width=20)

        self.export_button = tk.Button(event_frame, text="Export to JSON", state="disabled", command=self.export_json)

        region_label.grid(row=0, column=0, padx=5, pady=5)
        self.region_entry.grid(row=0, column=1, padx=5, pady=5)

        event_label.grid(row=0, column=0, padx=5, pady=5)
        self.event_entry.grid(row=0, column=1, padx=5, pady=5)
        self.event_submit.grid(row=0, column=2, padx=5, pady=5)
        region_label.grid(row=1, column=0)
        self.region_entry.grid(row=1, column=1)

        self.processing_label = tk.Label(self, text="Processing Data...")

        title_label.pack(side="top", anchor="w")
        event_frame.pack(side="left", anchor="nw")

        self.export_button.grid(row=2, column=0, padx=10, pady=5)

        self.bind('<<event_code_updated>>', lambda event: self.handle_event_update(event))

    def on_click(self):
        event_code = self.event_entry.get()
        region_code = self.region_entry.get()
        event = validate_event(event_code)

        if event is not None:
            self.controller.shared_data["event_code"] = event_code
            self.controller.shared_data["event"] = event
            self.controller.shared_data["region_code"] = region_code
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

        save_team_data(team_data, file_path)

    def handle_event_update(self, e):
        event: Event = self.controller.shared_data["event"]

        self.calculate_data(event)

    def calculate_data(self, event):
        region_code = self.controller.shared_data["region_code"]
        future = self.executor.submit(calculate_event_epa_opr, event.team_list, region_code)
        self.processing_label.pack(side="bottom", anchor="s")
        self.event_submit.config(state="disabled")
        self.event_entry.config(state="disabled")
        self.region_entry.config(state="disabled")
        self.after(100, self.check_future, future)

    def check_future(self, future):
        if future.done():
            try:
                result: dict[str, Team] = future.result()
                self.processing_label.pack_forget()
                self.event_submit.config(state="normal")
                self.event_entry.config(state="normal")
                self.region_entry.config(state="normal")
                self.export_button.config(state="normal")

                # Move result team data into shared_data
                self.controller.shared_data["teams"] = result
                # Send virtual event to notify graphs to enable
                broadcast_event(self.root, "<<team_stats_updated>>")

                # print(result)
            except Exception as e:
                traceback.print_exception(type(e), e, e.__traceback__)
        else:
            self.after(100, self.check_future, future)
