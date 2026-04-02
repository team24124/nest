import requests
from stats.data import get_auth, get_config

def test_api():
    auth = get_auth()
    season = get_config()['season']
    event_code = "CAABNILT1" # Known event
    
    print(f"Testing API for {event_code} ({season})...")
    url = f"https://ftc-api.firstinspires.org/v2.0/{season}/scores/{event_code}/qual"
    try:
        r = requests.get(url, auth=auth, timeout=10)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            scores = r.json().get('matchScores', [])
            print(f"Found {len(scores)} scores.")
        else:
            print(f"Error: {r.text}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_api()
