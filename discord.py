"""
discord.py - Send notifications to Discord.
"""

import requests
import time
from datetime import datetime
from config import DISCORD_WEBHOOK


def send_alert(title, price, url, location, score):
    """Send a listing alert to Discord."""
    if not DISCORD_WEBHOOK:
        print(f'  [NO WEBHOOK] [{score}] ${price:.0f} - {title[:50]}')
        return

    color = 0x00ff00 if score >= 70 else 0xffff00 if score >= 50 else 0xff9900
    embed = {
        'title': f'[{score}/100] ${price:.0f}/mo - {title[:75]}',
        'url': url,
        'color': color,
        'fields': [
            {'name': 'Location', 'value': location or 'AZ', 'inline': True},
            {'name': 'Score', 'value': f'{score}/100', 'inline': True},
        ],
        'footer': {'text': f'Found {datetime.now().strftime("%m/%d %I:%M %p")}'}
    }
    try:
        resp = requests.post(DISCORD_WEBHOOK, json={'embeds': [embed]}, timeout=10)
        if resp.status_code == 204:
            print(f'  [{score}] ${price:.0f} - {title[:50]}')
        elif resp.status_code == 429:
            retry = resp.json().get('retry_after', 2)
            time.sleep(retry + 0.5)
            requests.post(DISCORD_WEBHOOK, json={'embeds': [embed]}, timeout=10)
    except:
        pass
    time.sleep(1.5)
