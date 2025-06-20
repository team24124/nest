from tkinter import ttk, filedialog
import tkinter as tk


class NumberEntry(tk.Entry):
    def __init__(self, root: tk.Frame, width = 3, default=0, *args, **kw):
        validate_cmd = root.register(self.validate_input)
        super().__init__(root, validate='key', validatecommand=(validate_cmd, '%P'), width=width, *args, **kw)

        self.width = width

        # Insert DDefault Value
        self.insert(-1, f"{default}")

    def validate_input(self, p):
        max_length = self.width
        if len(p) > max_length:
            return False

        if str.isdigit(p) or p == "":
            return True
        else:
            return False

class FloatEntry(tk.Entry):
    def __init__(self, root: tk.Frame, width = 3, default=0, *args, **kw):
        validate_cmd = root.register(self.validate_input)
        super().__init__(root, validate='key', validatecommand=(validate_cmd, '%P'), width=width, *args, **kw)

        self.width = width

        # Insert Default Value
        self.insert(-1, f"{default}")

    def validate_input(self, p):
        max_length = self.width
        if len(p) > max_length:
            return False
        try:
            float(p)
            return True
        except ValueError:
            return False





