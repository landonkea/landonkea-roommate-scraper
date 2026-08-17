"""
main.py - Entry point. Calls everything else.
"""

from datetime import datetime
from database import init_db, clear_old, get_top_listings, get_stats
from scraper import scrape_all, scrape_padsplit
from history import save_daily_summary


def main():
    conn = init_db()
    clear_old(conn)

    print(f'Starting scrape at {datetime.now()}')

    saved = scrape_all(conn)
    print(f'Craigslist + sites: +{saved} listings')

    ps = scrape_padsplit(conn)
    print(f'PadSplit: +{ps} listings')

    total, good = get_stats(conn)
    print(f'\nDone - {total} total, {good} good (score >= 50)')
    save_daily_summary(conn)

    print('\n--- TOP LISTINGS ---')
    for title, price, url, loc, score in get_top_listings(conn):
        print(f'[{score}] ${price:.0f} - {title[:55]}')
        print(f'    {loc} | {url}')

    conn.close()


if __name__ == '__main__':
    main()
