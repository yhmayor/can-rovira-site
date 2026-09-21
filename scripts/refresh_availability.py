#!/usr/bin/env python3
"""
Fetches the Airbnb and Booking.com iCal calendars for Can Rovira and writes
a merged list of booked dates to data/availability.json.

Reads the two feed URLs from environment variables so the URLs themselves
never have to live in the repository:
    AIRBNB_ICAL_URL
    BOOKING_ICAL_URL

Run daily by .github/workflows/refresh-calendar.yml
"""

import json
import os
import re
import sys
import urllib.request
from datetime import date, datetime, timedelta

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "availability.json")


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; CanRoviraCalendarBot/1.0)"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", errors="replace")


def parse_date(value: str) -> date:
    value = value.strip()
    # DATE form: 20260924
    if re.fullmatch(r"\d{8}", value):
        return datetime.strptime(value, "%Y%m%d").date()
    # DATE-TIME form: 20260924T000000Z (take the date portion)
    m = re.match(r"(\d{8})T", value)
    if m:
        return datetime.strptime(m.group(1), "%Y%m%d").date()
    raise ValueError(f"Unrecognised date value: {value}")


def extract_ranges(ics_text: str):
    """
    Very small, dependency-free VEVENT parser. Airbnb and Booking.com both
    export plain-text .ics with unfolded-enough lines for DTSTART/DTEND to
    be readable via simple regex; this avoids needing the `icalendar`
    package in CI.
    """
    ranges = []
    # Normalise line folding (RFC 5545: continuation lines start with a space)
    unfolded = ics_text.replace("\r\n ", "").replace("\n ", "")
    events = unfolded.split("BEGIN:VEVENT")[1:]
    for block in events:
        block = block.split("END:VEVENT")[0]
        start_match = re.search(r"DTSTART[^:]*:(\S+)", block)
        end_match = re.search(r"DTEND[^:]*:(\S+)", block)
        if not start_match or not end_match:
            continue
        try:
            start = parse_date(start_match.group(1))
            end = parse_date(end_match.group(1))
        except ValueError:
            continue
        # iCal DTEND for all-day/blocked ranges is exclusive (the checkout
        # day itself is not blocked), so stop one day short.
        cur = start
        while cur < end:
            ranges.append(cur)
            cur += timedelta(days=1)
    return ranges


def main():
    airbnb_url = os.environ.get("AIRBNB_ICAL_URL", "").strip()
    booking_url = os.environ.get("BOOKING_ICAL_URL", "").strip()

    if not airbnb_url and not booking_url:
        print("No calendar URLs configured (AIRBNB_ICAL_URL / BOOKING_ICAL_URL). Nothing to do.", file=sys.stderr)
        sys.exit(1)

    booked_dates = set()
    sources_ok = []

    for name, url in (("airbnb", airbnb_url), ("booking", booking_url)):
        if not url:
            continue
        try:
            text = fetch(url)
            dates = extract_ranges(text)
            booked_dates.update(dates)
            sources_ok.append(name)
            print(f"{name}: {len(dates)} booked days found")
        except Exception as exc:
            print(f"WARNING: failed to fetch/parse {name} calendar: {exc}", file=sys.stderr)

    if not sources_ok:
        print("Both calendar fetches failed; leaving existing availability.json untouched.", file=sys.stderr)
        sys.exit(1)

    payload = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "sources_ok": sources_ok,
        "booked": sorted(d.isoformat() for d in booked_dates),
    }

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(payload, f, indent=2)

    print(f"Wrote {len(payload['booked'])} booked dates to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
