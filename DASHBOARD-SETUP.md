# H Visual Media Daily Dashboard - Automation Setup Guide

## Overview
This solution automatically generates an HTML dashboard from your Google Calendar events every day at 6:00 AM and commits it to your GitHub repository.

## Files Included

1. **dashboard.html** - Interactive dashboard (pulls live calendar data)
2. **generate-dashboard.py** - Python script to generate static HTML dashboard
3. **update-dashboard.yml** - GitHub Actions workflow for daily automation
4. **index.html** - Output file (generated daily, replaces existing)

## Setup Steps

### Step 1: Add Files to Your Repository

1. Clone your `brianhuntvisual/weekly-dashboard` repository:
   ```bash
   git clone https://github.com/brianhuntvisual/weekly-dashboard.git
   cd weekly-dashboard
   ```

2. Copy these files into your repo:
   - `generate-dashboard.py` → repo root
   - `update-dashboard.yml` → `.github/workflows/` directory (create the folders if needed)

3. Optionally add `dashboard.html` as a backup/reference

### Step 2: Set Up Google Calendar API Credentials

#### Option A: Using Service Account (Recommended for GitHub Actions)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the Google Calendar API
4. Create a Service Account:
   - Go to "Service Accounts"
   - Click "Create Service Account"
   - Fill in name: `github-dashboard-updater`
   - Grant Editor role
5. Create a key:
   - Select the service account
   - Go to "Keys" tab
   - Create new JSON key
   - Download the JSON file

#### Option B: Using OAuth (If you prefer user authentication)

1. In Google Cloud Console, create an OAuth 2.0 Client ID
2. Download credentials as JSON

### Step 3: Add GitHub Secret

1. Go to your GitHub repository
2. Settings → Secrets and variables → Actions
3. Create a new secret called `GOOGLE_CREDENTIALS`
4. Paste the entire contents of your Google credentials JSON file (from Step 2)

### Step 4: Configure the Workflow (Optional)

Edit `.github/workflows/update-dashboard.yml` to change:
- **Schedule time**: Modify the cron expression
  - Current: `0 11 * * *` (6:00 AM EST / 11:00 AM UTC)
  - Format: `minute hour day month day-of-week`
  - Examples:
    - `0 8 * * *` = 8:00 AM daily
    - `0 8 * * 1-5` = 8:00 AM weekdays only
    - `0 22 * * *` = 10:00 PM daily

### Step 5: Test the Workflow

1. Push the files to your repository
2. Go to GitHub → Actions
3. Click on "Update Daily Dashboard" workflow
4. Click "Run workflow" to test manually
5. Check that it completes successfully and `index.html` is updated

### Step 6: Verify the Output

Once the workflow runs:
1. Your `index.html` file will be automatically updated with today's calendar
2. File includes:
   - Today's date and time
   - Meeting count and work hours
   - Complete schedule with all events
   - Conflict detection (overlapping meetings)
   - Back-to-back warnings
   - Microsoft Teams and video call badges

## Features

✅ **Automatic Daily Updates** - Runs every morning without manual intervention
✅ **Schedule Conflict Detection** - Highlights overlapping meetings
✅ **Work Hours Calculation** - Shows total scheduled work time
✅ **Smart Categorization** - Excludes personal activities from work hours
✅ **Meeting Badges** - Identifies Teams meetings and video calls
✅ **Responsive Design** - Works on mobile and desktop
✅ **Dark Theme** - Easy on the eyes

## Troubleshooting

### Workflow not running?
- Check that `.github/workflows/update-dashboard.yml` is in the correct path
- Verify the `GOOGLE_CREDENTIALS` secret is set (Settings → Secrets)
- Check workflow logs in GitHub Actions tab

### API errors?
- Verify service account has Calendar API access
- Check that credentials JSON is valid (no extra spaces/quotes)
- Ensure service account email is added to your Google Calendar (optional but recommended)

### Dashboard not updating?
- Check GitHub Actions logs for errors
- Verify `generate-dashboard.py` is in repo root
- Ensure Python dependencies are installed (`google-auth-oauthlib`, `google-api-python-client`)

## Manual Updates

To run the dashboard generation locally:

```bash
# Set up credentials
export GOOGLE_CREDENTIALS='your_credentials_json_here'

# or create credentials.json in the repo root

# Run the script
python generate-dashboard.py
```

## Customization

### Modify the Python Script
Edit `generate-dashboard.py` to:
- Change work hour calculations
- Exclude certain calendar events
- Add custom styling
- Modify stat calculations

### Modify the Styling
Edit the `<style>` section in `generate-dashboard.py` or `dashboard.html` to customize colors, fonts, and layout

### Change Calendar to Sync
In `generate-dashboard.py`, modify:
```python
CALENDAR_ID = 'primary'  # Change to specific calendar ID if needed
```

## What Gets Tracked

The dashboard automatically tracks:
- All timed events for the day
- All-day events
- Event start/end times
- Overlapping meetings
- Back-to-back meeting gaps (< 5 minutes)
- Personal activities vs work meetings
- Meeting type (Teams, video, etc.)

## Deployment

Your dashboard is already hosted on GitHub Pages at:
```
https://brianhuntvisual.github.io/weekly-dashboard/
```

Simply access this URL to see today's updated dashboard!

## Support

If you encounter issues:
1. Check the workflow logs on GitHub Actions
2. Verify all files are in the correct locations
3. Test the Python script locally with valid credentials
4. Review Google Calendar API documentation for permission issues

---

**Dashboard updates daily at 6:00 AM EST**
Last updated: $(date)
