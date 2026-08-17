"""history.py - Append daily summary to history JSON for GitHub Pages."""

import json, pathlib, statistics
from datetime import datetime
from config import ROOT_DIR

HISTORY_PATH = ROOT_DIR / 'docs' / 'data' / 'history.json'


def save_daily_summary(conn):
    """Append today's summary to history. Returns summary dict."""
    pathlib.Path(HISTORY_PATH).parent.mkdir(parents=True, exist_ok=True)

    rows = conn.execute('SELECT title,price,location,score,source FROM rooms WHERE price>=200 AND price<=350').fetchall()
    if not rows:
        return None

    prices = [r[1] for r in rows if r[1] and r[1] > 0]
    scores = [r[3] for r in rows]
    sources = {}
    for r in rows:
        src = r[4]
        if src not in sources:
            sources[src] = {'count': 0, 'prices': []}
        sources[src]['count'] += 1
        if r[1] and r[1] > 0:
            sources[src]['prices'].append(r[1])

    summary = {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'total': len(rows),
        'good': len([s for s in scores if s >= 50]),
        'avg_price': round(statistics.mean(prices)) if prices else 0,
        'median_price': round(statistics.median(prices)) if prices else 0,
        'avg_score': round(statistics.mean(scores), 1),
        'by_source': {
            src: {'count': d['count'], 'avg_price': round(statistics.mean(d['prices'])) if d['prices'] else 0}
            for src, d in sources.items()
        }
    }

    history = []
    if HISTORY_PATH.exists():
        try:
            history = json.loads(HISTORY_PATH.read_text())
        except (json.JSONDecodeError, OSError):
            history = []

    history.append(summary)
    HISTORY_PATH.write_text(json.dumps(history, indent=2))

    print(f'  History: day {len(history)} saved ({summary["total"]} listings, avg ${summary["avg_price"]:,.0f})')
    return summary
