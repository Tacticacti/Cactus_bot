import json
import os

FILE_PATH = "users.json"

def load_users():
    """Returns a dictionary of {AoC_Name: Discord_ID}"""
    if not os.path.exists(FILE_PATH):
        return {}
    try:
        with open(FILE_PATH, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading users: {e}")
        return {}

def save_user(aoc_name, discord_id):
    """Saves a link between an AoC name and a Discord ID"""
    data = load_users()
    data[str(aoc_name)] = int(discord_id)
    
    try:
        with open(FILE_PATH, "w") as f:
            json.dump(data, f, indent=4)
        return True
    except Exception as e:
        print(f"❌ Error saving user: {e}")
        return False

def get_discord_mention(aoc_name):
    """Returns a ping string <@123> if found, else returns the name"""
    data = load_users()
    for key, val in data.items():
        if key.lower() == str(aoc_name).lower():
            return f"<@{val}>"
    return aoc_name

# --- NEW FUNCTION ---
def get_aoc_name_by_id(discord_id):
    """Checks if a Discord ID is already linked to ANY name. Returns the name or None."""
    data = load_users()
    for aoc_name, saved_id in data.items():
        if saved_id == int(discord_id):
            return aoc_name
    return None