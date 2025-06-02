import sys
import traceback
from queue import Queue
from concurrent.futures import ThreadPoolExecutor
from tkinter import ttk
import tkinter as tk
from app.Controller import Controller, broadcast_event
from stats.event import validate_event, Event
from stats.opr_epa import calculate_event_epa_opr


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

        region_frame = tk.Frame(self)
        region_label = tk.Label(region_frame, text="Region")
        self.region_entry = ttk.Entry(region_frame, width= 20)

        region_label.grid(row=0, column=0, padx=5, pady=5)
        self.region_entry.grid(row=0, column=1, padx=5, pady=5)

        event_label.grid(row=0, column=0, padx=5, pady=5)
        self.event_entry.grid(row=0, column=1, padx=5, pady=5)
        self.event_submit.grid(row=0, column=2, padx=5, pady=5)

        self.processing_label = tk.Label(self, text="Processing Data...")

        title_label.pack(side="top", anchor="w")
        event_frame.pack(side="left", anchor="w")
        region_frame.pack(side="left", anchor="w")

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
            print(f"The event ({event_code}) you entered could not be found.", file=sys.stderr)

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
                result = future.result()
                self.processing_label.pack_forget()
                self.event_submit.config(state="normal")
                self.event_entry.config(state="normal")
                self.region_entry.config(state="normal")

                # Move result team data into shared_data
                # Send virtual event to notify graphs to enable
                # Show export for team and event jsons

                # print(result)
            except Exception as e:
                traceback.print_exception(type(e), e, e.__traceback__)
        else:
            self.after(100, self.check_future, future)




