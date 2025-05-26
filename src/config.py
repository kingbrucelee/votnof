# File paths
WATCHED_PRINTS_FILE = "data/watched_prints.json"

# API endpoints
API_BASE_URL = "https://api.sejm.gov.pl/sejm/term10"
PRINTS_ENDPOINT = f"{API_BASE_URL}/prints"
PROCESSES_ENDPOINT = f"{API_BASE_URL}/processes"

# Magic numbers
PRINT_CHECK_INTERVAL_HOURS = 1
WEEKLY_REPORT_DAY = 0
WEEKLY_REPORT_HOUR = 9
DISCORD_MAX_MESSAGE_LENGTH = 2000
# Ensure data directory exists
import os

os.makedirs(os.path.dirname(WATCHED_PRINTS_FILE), exist_ok=True)
