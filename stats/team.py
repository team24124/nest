# Create team object to store information
class Team:
    def __init__(self, team_number, country, state_prov, city, home_region):
        self.games_played = 0
        self.team_number = team_number

        # Rankings at each event
        self.rankings = {}

        self.country = country
        self.state_prov = state_prov
        self.city = city
        self.home_region = home_region

        self.epa_total = 0
        self.auto_total = 0
        self.tele_total = 0
        self.historical_epa = []
        self.historical_auto_epa = []
        self.historical_tele_epa = []
        self.opr_total_vals = []
        self.opr_auto_vals = []
        self.opr_tele_vals = []
        self.opr_end_vals = []
        self.opr = 0
        self.opr_auto = 0
        self.opr_tele = 0
        self.opr_end = 0

    def update_event_rank(self, event_code, event_rank):
        self.rankings[event_code] = event_rank

    def update_epa(self, new_epa):
        self.epa_total = new_epa
        self.historical_epa.append(new_epa)
        self.games_played+=1

    def update_auto_epa(self, new_epa_auto):
      self.auto_total = new_epa_auto
      self.historical_auto_epa.append(new_epa_auto)

    def update_tele_epa(self, new_epa_tele):
      self.tele_total = new_epa_tele
      self.historical_tele_epa.append(new_epa_tele)

    def update_opr(self, opr_total, opr_auto, opr_tele, opr_end):
      self.opr_total_vals.append(opr_total)
      self.opr_auto_vals.append(opr_auto)
      self.opr_tele_vals.append(opr_tele)
      self.opr_end_vals.append(opr_end)
      self.opr = opr_total
      self.opr_auto = opr_auto
      self.opr_tele = opr_tele
      self.opr_end = opr_end

    def __repr__(self):
        return f"Team #{self.team_number} | Games Played: {self.games_played} | EPA Total: {self.epa_total}"