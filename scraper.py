"""
scraper.py - Craigslist scraping logic.
"""

import requests
from bs4 import BeautifulSoup
import re
from filters import should_skip, score_listing
from config import CRAIGSLIST_REGIONS, MIN_PRICE, MAX_PRICE


def scrape_craigslist(conn):
    """Scrape all Craigslist regions. Returns count of new listings."""
    from database import save_listing
    from discord import send_alert

    saved = 0
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}

    for region in CRAIGSLIST_REGIONS:
        try:
            url = f'https://{region}.craigslist.org/search/roo?min_price={MIN_PRICE}&max_price={MAX_PRICE}'
            r = requests.get(url, headers=headers, timeout=15)
            soup = BeautifulSoup(r.text, 'html.parser')

            for row in soup.find_all('li', class_='cl-static-search-result'):
                listing = parse_row(row, region)
                if not listing:
                    continue

                title, price, href, location = listing

                if should_skip(title):
                    continue

                score = score_listing(title, price)

                if save_listing(conn, 'craigslist', href, title, price, href, location, score):
                    saved += 1
                    if score >= 50:
                        send_alert(title, price, href, location, score)
        except:
            pass

    return saved


def parse_row(row, region):
    """Parse a Craigslist search result row. Returns (title, price, url, location) or None."""
    link = row.find('a', href=True)
    if not link:
        return None

    href = link['href']
    if not href.startswith('http'):
        href = f'https://{region}.craigslist.org' + href

    title_el = row.find('div', class_='title')
    title = title_el.text.strip() if title_el else ''

    price_el = row.find('div', class_='price')
    price_text = price_el.text.strip() if price_el else ''
    price_match = re.search(r'\$([\d,]+)', price_text)
    if not price_match:
        return None
    price = float(price_match.group(1).replace(',', ''))

    loc_el = row.find('div', class_='location')
    location = loc_el.text.strip() if loc_el else region

    return title, price, href, location
