import tkinter as tk

from numpy.f2py.cfuncs import commonhooks
from numpy.ma.extras import average

from app import Controller
from app.widget.NumberEntry import NumberEntry, FloatEntry


class SettingsWindow(tk.Toplevel):
    def __init__(self, root, controller: Controller):
        super().__init__(root)
        self.controller = controller
        self.title("Settings - Nighthawks Event Statistics Tool (NEST)")
        self.geometry("600x400")
        self.minsize(600, 400)
        self.resizable(width=False, height=False)
        icon = tk.PhotoImage(file='./app/favicon.png')
        self.wm_iconphoto(False, icon)

        self.season_frame = tk.Frame(self)
        tk.Label(self.season_frame, text="Current Season").pack(side="left", padx=5)
        self.season_entry = NumberEntry(self.season_frame, width=4, default=controller.shared_data["season"])
        self.season_entry.pack(side="left", padx=5)

        self.averages_frame = tk.Frame(self)
        self.calc_avg_flag = tk.BooleanVar(None, controller.shared_data["setting_calc_avg"])
        tk.Radiobutton(self.averages_frame, text="Calculate Average", variable=self.calc_avg_flag, value=True,
                       command=self.on_select).grid(row=0, column=0, padx=5, pady=5)
        tk.Radiobutton(self.averages_frame, text="Use Predetermined", variable=self.calc_avg_flag, value=False,
                       command=self.on_select).grid(row=0, column=1, padx=5, pady=5)

        self.epa_avg_entry = FloatEntry(self.averages_frame, default=self.controller.shared_data["epa_avg"], width=8)
        self.epa_auto_avg_entry = FloatEntry(self.averages_frame, default=self.controller.shared_data["epa_auto_avg"], width=8)
        self.epa_tele_avg_entry = FloatEntry(self.averages_frame, default=self.controller.shared_data["epa_tele_avg"], width=8)

        self.refresh_avg_entries()

        tk.Label(self.averages_frame, text="EPA Total Average").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        tk.Label(self.averages_frame, text="EPA Auto Average").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        tk.Label(self.averages_frame, text="EPA TeleOp Average").grid(row=3, column=0, padx=5, pady=5, sticky="w")

        self.epa_avg_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        self.epa_auto_avg_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        self.epa_tele_avg_entry.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        self.season_frame.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.averages_frame.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        tk.Button(self, text="Save Changes", command=self.on_save).grid(row=3, column=0, padx=5, pady=5, sticky="w")
        tk.Button(self, text="Close Without Saving", command=lambda: self.destroy()).grid(row=4, column=0, padx=5, pady=5, sticky="w")

    def on_select(self):
        # True if the avg should be calculated in real time, false if a predetermined avg should be used
        self.controller.shared_data["setting_calc_avg"] = bool(self.calc_avg_flag.get())
        self.refresh_avg_entries()

    def on_save(self):
        self.controller.shared_data["season"] = self.season_entry.get()
        self.controller.shared_data["setting_calc_avg"] = bool(self.calc_avg_flag.get())

        if not bool(self.calc_avg_flag.get()):
            self.controller.shared_data["epa_avg"] = float(self.epa_avg_entry.get())
            self.controller.shared_data["epa_auto_avg"] = float(self.epa_auto_avg_entry.get())
            self.controller.shared_data["epa_tele_avg"] = float(self.epa_tele_avg_entry.get())

        self.destroy()

    def refresh_avg_entries(self):
        if not self.calc_avg_flag.get():
            self.epa_avg_entry.config(state="normal")
            self.epa_auto_avg_entry.config(state="normal")
            self.epa_tele_avg_entry.config(state="normal")

            if self.epa_avg_entry.get() == '':
                self.epa_avg_entry.insert(-1, "0")

            if self.epa_auto_avg_entry.get() == '':
                self.epa_auto_avg_entry.insert(-1, "0")

            if self.epa_tele_avg_entry.get() == '':
                self.epa_tele_avg_entry.insert(-1, "0")
        else:
            self.epa_avg_entry.config(state="disabled")
            self.epa_auto_avg_entry.config(state="disabled")
            self.epa_tele_avg_entry.config(state="disabled")