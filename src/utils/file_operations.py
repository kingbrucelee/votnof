import json
import os
from src.config import WATCHED_PRINTS_FILE

# Structure for storing watched prints
# Format: {user_id: {print_number: last_change_date}}
watched_prints = {}


def load_watched_prints():
    """Loads watched prints from the file."""
    global watched_prints
    if os.path.exists(WATCHED_PRINTS_FILE):
        with open(WATCHED_PRINTS_FILE, "r") as f:
            watched_prints = json.load(f)
    else:
        watched_prints = {}
    return watched_prints


def save_watched_prints():
    """Saves watched prints to the file."""
    os.makedirs(os.path.dirname(WATCHED_PRINTS_FILE), exist_ok=True)
    with open(WATCHED_PRINTS_FILE, "w") as f:
        json.dump(watched_prints, f)


def get_watched_prints():
    """Returns the dictionary of watched prints."""
    global watched_prints
    if not watched_prints:
        load_watched_prints()
    return watched_prints


def add_watched_print(user_id, print_nr, change_date):
    """Adds a print to the watched list."""
    global watched_prints
    user_id = str(user_id)

    if user_id not in watched_prints:
        watched_prints[user_id] = {}

    watched_prints[user_id][print_nr] = change_date
    save_watched_prints()
    return True


def remove_watched_print(user_id, print_nr):
    """Removes a print from the watched list."""
    global watched_prints
    user_id = str(user_id)

    if user_id in watched_prints and print_nr in watched_prints[user_id]:
        del watched_prints[user_id][print_nr]
        save_watched_prints()
        return True
    return False


def update_print_change_date(user_id, print_nr, new_date):
    """Updates the change date for a watched print."""
    global watched_prints
    user_id = str(user_id)

    if user_id in watched_prints and print_nr in watched_prints[user_id]:
        watched_prints[user_id][print_nr] = new_date
        save_watched_prints()
        return True
    return False


def get_user_watched_prints(user_id):
    """Retrieves the list of prints watched by a user."""
    global watched_prints
    user_id = str(user_id)

    if user_id in watched_prints:
        return watched_prints[user_id]
    return {}
