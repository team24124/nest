from stats.team import Team


class Controller:
    """
    Centralized controller for manipulating shared data across the entire app
    """
    def __init__(self):
        self.shared_data = {"event_code": None,
                            "event": None,
                            "all_considered_events": None,
                            "region_code": None,
                            "teams": None,
                            "season": "2024",
                            "setting_calc_avg": True,
                            "epa_avg": 0,
                            "epa_auto_avg": 0,
                            "epa_tele_avg": 0
                            }

    def is_event_selected(self):
        return self.shared_data["event_code"] is not None

    def is_data_calculated(self):
        return self.shared_data["teams"] is not None


def broadcast_event(widget, virtual_event):
    widget.event_generate(virtual_event)
    for child_widget in widget.winfo_children():
        broadcast_event(child_widget, virtual_event)