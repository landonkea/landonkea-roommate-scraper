# Roommate Scraper - Site Status

What was tried, what works, what doesn't, and why.

## Working Sites (7)

| Site | Status | Notes |
|------|--------|-------|
| Craigslist | ✅ Working | Best source. 8 AZ regions, fast (requests-based). |
| SpareRoom | ✅ Working | ~14 listings. Playwright required. |
| Roomster | ✅ Working | ~22 listings. Playwright required. |
| PadSplit | ✅ Working | ~17 listings. Cheapest private rooms ($154-$250). Playwright required. |
| Cirtru | ✅ Working | ~24 listings. Playwright required. |
| RoommateNation | ✅ Working | ~11 listings. Playwright required. |
| iROOMit | ✅ Working | ~19 listings. Playwright required. |

## Blocked / Not Working (12)

| Site | Status | Reason |
|------|--------|--------|
| HotPads | ❌ Blocked | Akamai bot protection. Enterprise-grade, needs residential proxy. |
| Roommates.com | ❌ Blocked | Cloudflare "Just a moment..." challenge. Needs browser fingerprint bypass. |
| Roomies.com | ❌ Blocked | Cloudflare challenge. Same issue as Roommates.com. |
| Locanto | ❌ Blocked | Cloudflare challenge. |
| Oodle | ❌ Blocked | Cloudflare challenge. |
| Redfin | ❌ Blocked | Custom bot detection ("Are You a Robot?"). |
| Realtor.com | ❌ Blocked | Returns 503 Service Unavailable. |
| Zumper | ⚠️ Works but useless | Prices start at $720/mo. No rooms under $350 in AZ. |
| PadMapper | ⚠️ Works but useless | Only shows full apartments, no shared rooms. |
| Geebo | ⚠️ Works but useless | Has the site, but zero Arizona listings. |
| ClassifiedAds | ❌ Broken | Returns 404 Not Found. |
| Diggz | ❌ Broken | Returns 0 results for all AZ cities. |

## Why Blocked Sites Can't Be Fixed

All blocked sites use one of:
- **Cloudflare** (Roommates.com, Roomies, Locanto, Oodle) — Requires residential IP proxy ($50-100/mo)
- **Akamai** (HotPads) — Enterprise bot detection, even harder to bypass
- **Custom** (Redfin) — JavaScript fingerprinting detection

These protections are specifically designed to block scrapers. No amount of Playwright/stealth fixes will bypass them without paying for proxy infrastructure.

## Recommendation

The 7 working sites cover the Arizona roommate market well. Craigslist alone has 500+ listings. Adding the other 6 Playwright sites brings total coverage to 700+ listings across the state. The blocked sites (HotPads, Redfin, etc.) mostly list full apartments or rentals over $500/mo anyway — not the budget room share market this scraper targets.
