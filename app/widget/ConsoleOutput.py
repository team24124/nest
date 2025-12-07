from tkinter import ttk
import tkinter as tk
from app import Controller
from tkinter import ttk
import tkinter as tk
from app import Controller


class ConsoleOutput(tk.Frame):
    def __init__(self, root: tk.Tk, controller: Controller):
        super().__init__(root)
        self.controller = controller
        self.root = root

        self.console_text = tk.Text(self, state='disabled', height=10)
        self.console_text.pack(expand=True, fill='both')

        self.clear_button = tk.Button(self, text="Clear", command=self.clear_console, width=25)
        self.clear_button.pack(anchor="se", side="right", pady=5)

    def clear_console(self):
        self.console_text.config(state='normal')
        self.console_text.delete('1.0', tk.END)
        self.console_text.config(state='disabled')

class TextRedirector(object):
    def __init__(self, widget, tag):
        self.widget = widget
        self.tag = tag

    def write(self, text):
        self.widget.configure(state='normal') # Edit mode
        self.widget.insert(tk.END, text, (self.tag,)) # insert new text at the end of the widget
        self.widget.configure(state='disabled') # Static mode
        self.widget.see(tk.END) # Scroll down
        self.widget.tag_config("stderr", foreground="red")
        self.widget.update_idletasks() # Update the console

    def flush(self):
        pass