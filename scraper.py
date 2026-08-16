"""
scraper.py - All scraping logic.
"""

import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth
import time
import re
from filters import should_skip, score_listing
from config import CRAIGSLIST_REGIONS, MIN_PRICE, MAX_PRICE


GENERIC_JS = """() => {
    const results = [];
    const seen = new Set();
    document.querySelectorAll('a').forEach(link => {
        const href = link.href;
        if (!href.includes('DOMAIN') || seen.has(href)) return;
        seen.add(href);
        const container = link.closest('li') || link.closest('article') || link.closest('div') || link;
        const text = (container.innerText || '').substring(0, 500);
        if (text.includes('$') && text.length > 20) {
            results.push({href, text});
        }
    });
    return results;
}"""

PADSPLIT_JS = """() => {
    const results = [];
    const seen = new Set();
    document.querySelectorAll('a').forEach(link => {
        const href = link.href;
        if (!href.includes('padsplit.com/rooms-for-rent/listing') || seen.has(href)) return;
        seen.add(href);
        const container = link.closest('li') || link.closest('article') || link.closest('div') || link;
        const text = (container.innerText || '').substring(0, 500);
        if (text.includes('$') && text.length > 20) {
            results.push({href, text});
        }
    });
    return results;
}"""

AZ_CITIES = [
    'phoenix', 'tucson', 'mesa', 'chandler', 'glendale', 'scottsdale',
    'tempe', 'peoria', 'surprise', 'flagstaff', 'prescott', 'sedona',
    'yuma', 'lake-havasu-city', 'sierra-vista', 'show-low', 'maricopa',
    'avondale', 'goodyear', 'buckeye', 'casa-grande', 'florence',
]

PLAYWRIGHT_SITES = [
    {'name': 'spareroom', 'domain': 'spareroom.com', 'url': 'https://www.spareroom.com/rooms-for-rent/{}_az'},
    {'name': 'roomster', 'domain': 'roomster.com', 'url': 'https://roomster.com/rooms-for-rent/{}-az'},
    {'name': 'cirtru', 'domain': 'cirtru.com', 'url': 'https://www.cirtru.com/rooms-for-rent/{}-az'},
    {'name': 'roommatenation', 'domain': 'roommatenation.com', 'url': 'https://roommatenation.com/us/az/{}'},
    {'name': 'iroomit', 'domain': 'iroomit.com', 'url': 'https://www.iroomit.com/rooms-for-rent/{}-az'},
]


def scrape_all(conn):
    """Scrape Craigslist + all Playwright sites. Returns total saved."""
    from database import save_listing
    from discord import send_alert

    saved = 0
    saved += scrape_craigslist(conn, save_listing, send_alert)
    saved += scrape_playwright_sites(conn, save_listing, send_alert)
    return saved


def scrape_craigslist(conn, save_listing, send_alert):
    """Scrape Craigslist."""
    saved = 0
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}

    for region in CRAIGSLIST_REGIONS:
        try:
            url = f'https://{region}.craigslist.org/search/roo?min_price={MIN_PRICE}&max_price={MAX_PRICE}'
            r = requests.get(url, headers=headers, timeout=15)
            soup = BeautifulSoup(r.text, 'html.parser')

            for row in soup.find_all('li', class_='cl-static-search-result'):
                listing = parse_cl_row(row, region)
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


def scrape_playwright_sites(conn, save_listing, send_alert):
    """Scrape all Playwright-based sites. One browser per site."""
    saved = 0

    for site in PLAYWRIGHT_SITES:
        try:
            saved += scrape_one_site(conn, site, save_listing, send_alert)
        except Exception as e:
            print(f'  {site["name"]}: error - {e}')

    return saved


def scrape_one_site(conn, site, save_listing, send_alert):
    """Scrape one site with its own browser."""
    saved = 0
    name = site['name']
    domain = site['domain']
    url_template = site['url']
    js = GENERIC_JS.replace('DOMAIN', domain)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        Stealth().apply_stealth_sync(context)
        page = context.new_page()

        for city in AZ_CITIES:
            url = url_template.format(city)
            try:
                page.goto(url, wait_until='domcontentloaded', timeout=12000)
                time.sleep(2)
            except:
                continue

            try:
                for _ in range(3):
                    page.evaluate('window.scrollBy(0, 800)')
                    time.sleep(0.3)
            except:
                pass

            try:
                data = page.evaluate(js)
            except:
                continue

            for item in data:
                href = item.get('href', '')
                text = item.get('text', '')
                price_match = re.search(r'\$([\d,]+)', text)
                if not price_match:
                    continue
                price = float(price_match.group(1).replace(',', ''))
                if price < MIN_PRICE or price > MAX_PRICE:
                    continue

                lines = [l.strip() for l in text.split('\n') if l.strip()]
                title = ''
                for line in lines:
                    if len(line) > 10 and '$' not in line:
                        title = line
                        break
                if not title:
                    title = lines[0] if lines else 'Room listing'

                if should_skip(title):
                    continue

                score = score_listing(title, price)

                if save_listing(conn, name, href, title, price, href, city, score):
                    saved += 1
                    if score >= 50:
                        send_alert(title, price, href, city, score)

        browser.close()

    print(f'  {name}: +{saved}')
    return saved


def scrape_padsplit(conn):
    """Scrape PadSplit with its own browser."""
    from database import save_listing
    from discord import send_alert

    saved = 0

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            Stealth().apply_stealth_sync(context)
            page = context.new_page()

            for city in AZ_CITIES:
                url = f'https://www.padsplit.com/rooms-for-rent/{city}-az'
                try:
                    page.goto(url, wait_until='domcontentloaded', timeout=12000)
                    time.sleep(2)
                except:
                    continue

                try:
                    for _ in range(5):
                        page.evaluate('window.scrollBy(0, 1000)')
                        time.sleep(0.3)
                except:
                    pass

                try:
                    data = page.evaluate(PADSPLIT_JS)
                except:
                    continue

                for item in data:
                    href = item.get('href', '')
                    if '/az/' not in href:
                        continue
                    text = item.get('text', '')
                    price_match = re.search(r'\$([\d,]+)', text)
                    if not price_match:
                        continue
                    price = float(price_match.group(1).replace(',', ''))
                    if price < MIN_PRICE or price > MAX_PRICE:
                        continue

                    lines = [l.strip() for l in text.split('\n') if l.strip()]
                    title = ''
                    for line in lines:
                        if len(line) > 10 and '$' not in line:
                            title = line
                            break
                    if not title:
                        title = lines[0] if lines else 'Room listing'

                    if should_skip(title):
                        continue

                    score = score_listing(title, price)

                    if save_listing(conn, 'padsplit', href, title, price, href, city, score):
                        saved += 1
                        if score >= 50:
                            send_alert(title, price, href, city, score)

            browser.close()
    except Exception as e:
        print(f'  padsplit: error - {e}')

    print(f'  padsplit: +{saved}')
    return saved


def parse_cl_row(row, region):
    """Parse a Craigslist search result row."""
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
