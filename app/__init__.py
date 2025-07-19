import tkinter as tk
import sys
from concurrent.futures.thread import ThreadPoolExecutor
from multiprocessing.pool import ThreadPool

from app.Controller import Controller
from app.widget.BarGraph import BarGraph
from app.widget.EventDashboard import EventDashboard
from app.widget.MainControl import MainControl
from app.widget.ConsoleOutput import ConsoleOutput, TextRedirector
from app.widget.StatScatterPlot import StatScatterPlot
from app.widget.TeamScatterPlot import TeamScatterPlot
from stats.events.Event import Event


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Nighthawks Event Statistics Tool (NEST)")

        # Setup and geometry
        self.geometry("800x600+100+50")
        self.minsize(1000, 600)
        self.configure(background="GhostWhite")

        # Setup Controller
        self.controller = Controller()

        # Icon
        icon = tk.PhotoImage(file='./app/favicon.png')
        self.wm_iconphoto(False, icon)

        # Widgets
        self.main = MainControl(self, controller=self.controller)
        self.main.grid(row=0, column=0, padx=5, pady=5, sticky="news")

        self.dash = EventDashboard(self, controller=self.controller)
        self.dash.grid(row=1, column=0, padx=5, pady=5, sticky="news")

        self.output = ConsoleOutput(self, controller=self.controller)
        self.output.grid(row=2, column=0, padx=5, pady=5, sticky="news")

        self.bargraph = BarGraph(self, controller=self.controller)
        self.bargraph.grid(row=0, column=1, padx=5, pady=5, sticky="news")

        self.teamscatter = TeamScatterPlot(self, controller=self.controller)
        self.teamscatter.grid(row=1, column=1, padx=5, pady=5, sticky="news")

        self.statscatter = StatScatterPlot(self, controller=self.controller)
        self.statscatter.grid(row=2, column=1, padx=5, pady=5, sticky="news")

        self.redirect_sysstd() # Redirect console output to the app

        self.columnconfigure(0, weight=1, uniform="group1")
        self.columnconfigure(1, weight=1, uniform="group1")

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=2)

        # Run
        self.mainloop()

    def redirect_sysstd(self):
        # We specify that sys.stdout point to TextRedirector
        sys.stdout = TextRedirector(self.output.console_text, "stdout")
        sys.stderr = TextRedirector(self.output.console_text, "stderr")

