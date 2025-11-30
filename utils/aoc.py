import requests
import config

def get_leaderboard_data():
    """
    Fetches the private leaderboard JSON from Advent of Code.
    """
    if not config.AOC_SESSION or not config.LEADERBOARD_ID:
        print("❌ Error: Missing AoC credentials in config.")
        return None

    url = f"https://adventofcode.com/{config.YEAR}/leaderboard/private/view/{config.LEADERBOARD_ID}.json"
    headers = {"Cookie": f"session={config.AOC_SESSION}"}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"❌ Error fetching data: Status {response.status_code}")
            return None
        return response.json()
    except Exception as e:
        print(f"❌ Exception while fetching data: {e}")
        return None