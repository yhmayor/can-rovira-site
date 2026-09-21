# Can Rovira website — self-refreshing availability

This is a plain static website (no server needed) with one extra piece: a
scheduled job that checks your Airbnb and Booking.com calendars once a day
and updates the availability calendar on the site automatically.

Hosting is free, using GitHub Pages. Setup takes about 10 minutes, once.

## What's in here

```
index.html                          the website itself
assets/img/hero.jpg                 the house photo
data/availability.json              the live booked-dates file (auto-updated)
scripts/refresh_availability.py     the script that fetches both calendars
.github/workflows/refresh-calendar.yml   the daily automation
```

## One-time setup

### 1. Create a GitHub account (if you don't have one)
Free, at github.com.

### 2. Create a new repository
- Click "New repository"
- Name it anything, e.g. `can-rovira-site`
- Keep it **public** (GitHub Pages needs this on the free plan) — this is
  fine, since the site itself is meant to be public anyway. Your actual
  calendar links are kept private separately (step 4), never committed to
  the repository.
- Upload every file and folder in this package into the repository,
  keeping the same folder structure.

### 3. Turn on GitHub Pages
- In the repository, go to **Settings → Pages**
- Under "Build and deployment", set **Source** to **GitHub Actions**

### 4. Add your calendar links as secrets (keeps them private)
- Go to **Settings → Secrets and variables → Actions**
- Click **New repository secret** and add:
  - Name: `AIRBNB_ICAL_URL` — Value: your Airbnb export link
  - Name: `BOOKING_ICAL_URL` — Value: your Booking.com export link

### 5. Run it once
- Go to the **Actions** tab → "Refresh availability calendar" → **Run workflow**
- After a minute or two, your site will be live at:
  `https://<your-username>.github.io/<repository-name>/`

From here on, it refreshes automatically every day at 05:00 UTC — no
further action needed. You can also trigger a manual refresh any time
from the Actions tab.

## Changing the daily refresh time

Edit the `cron` line in `.github/workflows/refresh-calendar.yml`. It uses
standard cron syntax in UTC, e.g. `0 5 * * *` = 05:00 UTC every day.

## Using your own domain

Once the site is live on GitHub Pages, you can point a custom domain
(e.g. `www.canrovira.com`) at it for a small yearly domain-registration
fee — GitHub's hosting itself stays free. Ask if you'd like help with
this step when you're ready.
