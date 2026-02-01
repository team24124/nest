from stats.events.Event import Event
from stats.teams.Team import Team


class Controller:
    """
    Centralized controller for manipulating shared data across the entire app
    """
    def __init__(self):
        self.shared_data = {
            "event_code": None,
            "event": None,
            "teams": None,
        }


    def is_event_selected(self):
        return self.shared_data["event_code"] is not None

    def is_data_calculated(self):
        return self.shared_data["teams"] is not None


def broadcast_event(widget, virtual_event):
    widget.event_generate(virtual_event)
    for child_widget in widget.winfo_children():
        broadcast_event(child_widget, virtual_event)