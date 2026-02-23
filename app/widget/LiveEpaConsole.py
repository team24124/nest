import tkinter as tk
from datetime import datetime
import threading
from app.Controller import Controller
from stats.data import get_season_score_parser, get_config
import requests
class LiveEpaConsole(tk.Frame):
    def __init__(self, root: tk.Tk, controller: Controller):
        super().__init__(root)
        self.root = root
        self.controller = controller
        self.processed_matches = set()

        # UI Layout
        title_label = tk.Label(self, text="Live EPA Feed", font=("Segoe UI", 11))
        title_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.text_area = tk.Text(self, height=10, width=50, state="disabled",
                                 bg="#f8f8f8", font=("Consolas", 9))
        self.text_area.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

        self.root.bind('<<team_stats_updated>>', lambda e: self.start_polling())

        self.team_entry = tk.Entry(self)
        self.team_entry.grid(row=3, column=0, padx=5, pady=5, sticky="ew")

        self.graph_btn = tk.Button(self, text="Graph EPA Trendline", command=self.launch_trend_graph)
        self.graph_btn.grid(row=4, column=0, padx=5, pady=5, sticky="ew")

    def start_polling(self):
        self.update_loop()

    def update_loop(self):
        event_code = self.controller.shared_data.get("event_code")
        team_data = self.controller.shared_data.get("teams")

        if event_code and team_data and event_code != "MANUAL":
            # FIX: Start the logic in a background thread to prevent freezing
            threading.Thread(target=self.run_logic, args=(event_code, team_data), daemon=True).start()

        self.after(180000, self.update_loop)
    def run_logic(self, event_code, team_data):
        try:
            season = get_config()['season']
            parser = get_season_score_parser(season)
            event_data = parser.parse(event_code)

            # event_data.matches is a list of MatchData objects
            sorted_matches = sorted(event_data.matches, key=lambda m: m.match_number)

            new_found = False
            for match in sorted_matches:
                m_name = match.get_match_name()

                if m_name not in self.processed_matches and match.red_alliance.total_score > 0:
                    self.process_match_data(match, team_data)
                    self.processed_matches.add(m_name)
                    new_found = True

            if new_found:
                self.after(0, lambda: self._refresh_display(team_data))

        except Exception as e:
            print(f"Live EPA Widget Error: {e}")

    def _resolve_teams_for_match(self, match_obj):
        team_data = self.controller.shared_data.get("teams")
        event = self.controller.shared_data.get("event")

        if not team_data or not event:
            return [], []


        # Check for .matches, then .match_list, then .match_schedule
        schedule = None
        for attr in ['matches', 'match_list', 'match_schedule']:
            if hasattr(event, attr):
                schedule = getattr(event, attr)
                break

        if not schedule:
            print(f"CRITICAL: Event object has NO schedule attribute. (Checked matches, match_list, match_schedule)")
            return [], []

        red_teams, blue_teams = [], []
        match_num = match_obj.match_number

        try:
            # 2. Search for the specific match
            scheduled_match = next((m for m in schedule if m.match_number == match_num), None)

            if scheduled_match:
                # 3. Pull teams using the attributes from your match objects
                # Change .red_teams / .blue_teams to match your schedule object's attributes
                r_nums = getattr(scheduled_match, 'red_teams', [])
                b_nums = getattr(scheduled_match, 'blue_teams', [])

                red_teams = [team_data[t] for t in r_nums if t in team_data]
                blue_teams = [team_data[t] for t in b_nums if t in team_data]

                if not red_teams or not blue_teams:
                    print(f"Match {match_num}: Found in schedule, but teams are missing from team_data!")
            else:
                print(f"Match {match_num}: Not found in the event schedule.")

        except Exception as e:
            print(f"Internal Schedule Error on Match {match_num}: {e}")

        return red_teams, blue_teams

    def sync_to_nighthawks_api(team):
        """Sends the updated team EPA data to the Nighthawks web server."""
        api_url = "https://your-nighthawks-api.com/v1/update_team"  # Replace with your real URL
        api_key = "YOUR_SECRET_KEY"  # Replace with your real API Key

        payload = {
            "team_number": team.team_number,
            "epa_total": round(team.epa_total, 2),
            "epa_auto": round(team.epa_auto_total, 2),
            "last_match": team.last_match_name,
            "history": team.historical_epa[-10:]  # Optional: send last 10 matches
        }

        try:
            response = requests.post(
                api_url,
                json=payload,
                headers={"X-API-KEY": api_key},
                timeout=5
            )
            if response.status_code == 200:
                print(f"Successfully synced Team {team.team_number} to API.")
            else:
                print(f"API Sync failed for Team {team.team_number}: {response.status_code}")
        except Exception as e:
            print(f"Could not connect to Nighthawks API: {e}")

    def process_match_data(self, match_obj, team_data):
        """Updates EPA using MatchData object attributes."""
        red_teams, blue_teams = self._resolve_teams_for_match(match_obj)

        if len(red_teams) >= 2 and len(blue_teams) >= 2:
            from stats.calculations.epa import calculate_epa

            t1, t2 = red_teams[0], red_teams[1]
            t3, t4 = blue_teams[0], blue_teams[1]

            m_name = match_obj.get_match_name()
            for t in [t1, t2, t3, t4]:
                t.update_game_played(m_name)

            games_played = (t1.games_played + t2.games_played + t3.games_played + t4.games_played) / 4

            # Access attributes directly from match_obj (MatchData) and alliances (AllianceScoreData)
            change_red, change_blue = calculate_epa(
                (t1.epa_total + t2.epa_total),
                (t3.epa_total + t4.epa_total),
                match_obj.red_alliance.total_score,
                match_obj.blue_alliance.total_score,
                games_played
            )

            change_red_auto, change_blue_auto = calculate_epa(
                (t1.epa_auto_total + t2.epa_auto_total),
                (t3.epa_auto_total + t4.epa_auto_total),
                match_obj.red_alliance.auto_score,
                match_obj.blue_alliance.auto_score,
                games_played
            )

            # Update the Team Objects and RECORD HISTORY
            for t in [t1, t2]:
                t.update_epa(change_red, change_red_auto, 0)
                # Ensure the list exists and append the new total
                if not hasattr(t, 'historical_epa'): t.historical_epa = []
                t.historical_epa.append(t.epa_total)
                threading.Thread(target=self.sync_to_nighthawks_api, args=(t,), daemon=True).start()

            for t in [t3, t4]:
                t.update_epa(change_blue, change_blue_auto, 0)
                if not hasattr(t, 'historical_epa'): t.historical_epa = []
                t.historical_epa.append(t.epa_total)
                threading.Thread(target=self.sync_to_nighthawks_api, args=(t,), daemon=True).start()

    def _refresh_display(self, team_data):
        self.text_area.config(state="normal")
        self.text_area.delete("1.0", "end")
        self.text_area.insert("end", f"Last Update: {datetime.now().strftime('%H:%M:%S')}\n")
        self.text_area.insert("end", "-" * 30 + "\n")
        sorted_teams = sorted(team_data.values(), key=lambda t: t.epa_total, reverse=True)
        for team in sorted_teams[:len(sorted_teams)]:
            self.text_area.insert("end", f"Team {team.team_number}: {team.epa_total:.2f}\n")
        self.text_area.config(state="disabled")

    def launch_trend_graph(self):
        from graphing.graph import make_live_epa_trend

        event = self.controller.shared_data.get("event")
        teams = self.controller.shared_data.get("teams")

        raw_input = self.team_entry.get()
        if not raw_input or not event or not teams:
            return

        target_list = [t.strip() for t in raw_input.split(",") if t.strip().isdigit()]

        # Filter the list to only include teams that actually have history
        valid_targets = []
        for t_num in target_list:
            team = teams.get(int(t_num))
            if team and hasattr(team, 'historical_epa') and len(team.historical_epa) > 0:
                valid_targets.append(t_num)

        if not valid_targets:
            print("None of the selected teams have match history yet.")
            return

        make_live_epa_trend(event, teams, valid_targets)


