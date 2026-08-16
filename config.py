"""
config.py - All settings in one place.
Change price, location, filters here.
"""

import pathlib
from dotenv import load_dotenv

load_dotenv()

# Paths
ROOT_DIR = pathlib.Path(__file__).parent
DB_PATH = str(ROOT_DIR / 'data' / 'rooms.db')

# Discord
DISCORD_WEBHOOK = __import__('os').environ.get('DISCORD_WEBHOOK_URL_ROOM')

# Price range (monthly)
MIN_PRICE = 200
MAX_PRICE = 350

# Minimum score to send to Discord (0-100)
MIN_SCORE = 50

# Craigslist regions to scrape
CRAIGSLIST_REGIONS = [
    'phoenix', 'tucson', 'flagstaff', 'yuma', 'prescott',
    'mohave', 'showlow', 'sierravista',
]
