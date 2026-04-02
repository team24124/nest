import os
import sys
import requests

# Path to nest root
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from stats.data import get_auth

def fetch_events(season, auth):
    url = f"https://ftc-api.firstinspires.org/v2.0/{season}/events"
    r = requests.get(url, auth=auth, timeout=10)
    return r.json().get('events', []) if r.status_code == 200 else []

def main():
    season = 2025
    auth = get_auth()
    events = fetch_events(season, auth)
    
    countries = set()
    states = set()
    
    for e in events:
        if e.get('code') == "CAABCPM1":
            import json
            print(f"Details for CAABCPM1:\n{json.dumps(e, indent=4)}")
            break

    print("\nUnique Countries:", sorted(list(countries)))
    print("Unique States (first 50):", sorted(list(states))[:50])

if __name__ == "__main__":
    main()
