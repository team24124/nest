from tkinter import ttk, filedialog
import tkinter as tk


def validate_input(p):
    max_length = 3
    if len(p) > max_length:
        return False

    if str.isdigit(p) or p == "":
        return True
    else:
        return False


class NumberEntry(tk.Entry):
    def __init__(self, root: tk.Frame, width = 3):
        validate_cmd = root.register(validate_input)
        super().__init__(root, validate='key', validatecommand=(validate_cmd, '%P'), width=width)

        self.insert(-1, "0")





