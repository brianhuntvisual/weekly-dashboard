#!/usr/bin/env python3
"""
Generate H Visual Media Daily Dashboard from Google Calendar
Runs daily and updates index.html with today's events
"""

import json
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from google.oauth2 import service_account
import os

# Configuration
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
CALENDAR_ID = 'primary'

def get_calendar_service():
    """Authenticate with Google Calendar API"""
    # Uses GOOGLE_CREDENTIALS environment variable or service account JSON
    credentials_json = os.getenv('GOOGLE_CREDENTIALS')

    if credentials_json:
        creds_dict = json.loads(credentials_json)
    else:
        creds_dict = json.load(open('credentials.json'))

    credentials = service_account.Credentials.from_service_account_info(
        creds_dict,
        scopes=SCOPES
    )

    from google.auth.transport.requests import Request
    credentials.refresh(Request())

    from googleapiclient.discovery import build
    return build('calendar', 'v3', credentials=credentials)

def get_today_events(service):
    """Fetch today's calendar events"""
    today = datetime.now().date()
    start = datetime.combine(today, datetime.min.time()).isoformat() + 'Z'
    end = datetime.combine(today, datetime.max.time()).isoformat() + 'Z'

    events_result = service.events().list(
        calendarId=CALENDAR_ID,
        timeMin=start,
        timeMax=end,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    return events_result.get('items', [])

def detect_conflicts(events):
    """Find overlapping events"""
    conflicts = []
    for i, event1 in enumerate(events):
        for j, event2 in enumerate(events[i+1:], start=i+1):
            start1 = datetime.fromisoformat(
                event1['start'].get('dateTime', event1['start'].get('date')).replace('Z', '+00:00')
            )
            end1 = datetime.fromisoformat(
                event1['end'].get('dateTime', event1['end'].get('date')).replace('Z', '+00:00')
            )
            start2 = datetime.fromisoformat(
                event2['start'].get('dateTime', event2['start'].get('date')).replace('Z', '+00:00')
            )
            end2 = datetime.fromisoformat(
                event2['end'].get('dateTime', event2['end'].get('date')).replace('Z', '+00:00')
            )

            if start1 < end2 and end1 > start2:
                conflicts.append((i, j))

    return conflicts

def generate_html(events):
    """Generate HTML dashboard"""
    today = datetime.now().date()
    today_str = today.strftime('%A, %B %d, %Y')
    time_str = datetime.now().strftime('%I:%M %p')

    conflicts = detect_conflicts(events)
    conflict_pairs = set()
    for i, j in conflicts:
        conflict_pairs.add(i)
        conflict_pairs.add(j)

    # Calculate stats
    timed_events = [e for e in events if 'dateTime' in e['start']]
    work_events = [e for e in timed_events if e['summary'] not in ['Gym', 'organize gear', 'bike ride']]

    total_minutes = 0
    for event in work_events:
        start = datetime.fromisoformat(event['start']['dateTime'].replace('Z', '+00:00'))
        end = datetime.fromisoformat(event['end']['dateTime'].replace('Z', '+00:00'))
        total_minutes += (end - start).total_seconds() / 60

    work_hours = total_minutes / 60
    free_hours = max(0, 10 - work_hours)

    # Build schedule HTML
    schedule_html = ''
    for idx, event in enumerate(timed_events):
        start = datetime.fromisoformat(event['start']['dateTime'].replace('Z', '+00:00'))
        end = datetime.fromisoformat(event['end']['dateTime'].replace('Z', '+00:00'))

        start_time = start.strftime('%I:%M %p')
        end_time = end.strftime('%I:%M %p')
        time_str = f'{start_time} – {end_time}'

        is_conflict = idx in conflict_pairs
        conflict_class = ' conflict' if is_conflict else ''

        badges = ''
        if 'Teams' in event.get('description', ''):
            badges += '<span class="badge teams">Teams</span> '
        if 'video' in event['summary'].lower():
            badges += '<span class="badge video">Video</span>'

        conflict_badge = '<span class="badge conflict">CONFLICT</span>' if is_conflict else ''

        schedule_html += f'''
            <li class="schedule-item{conflict_class}">
                <span class="time">{time_str}</span>
                <span class="event-title{conflict_class}">{event['summary']}</span>
                {badges} {conflict_badge}
            </li>
        '''

    # Build alerts
    alerts_html = ''
    if conflicts:
        alerts_html += '<div class="priority-section"><h3>⚠️ Schedule Conflicts</h3>'
        for i, j in conflicts:
            e1 = events[i]['summary']
            e2 = events[j]['summary']
            alerts_html += f'<div class="priority-item">{e1} ↔ {e2}</div>'
        alerts_html += '</div>'

    # Check back-to-back meetings
    back_to_back_count = 0
    for i in range(1, len(timed_events)):
        prev_end = datetime.fromisoformat(timed_events[i-1]['end']['dateTime'].replace('Z', '+00:00'))
        curr_start = datetime.fromisoformat(timed_events[i]['start']['dateTime'].replace('Z', '+00:00'))
        if (curr_start - prev_end).total_seconds() < 300:
            back_to_back_count += 1

    if back_to_back_count > 0:
        alerts_html += f'''
            <div class="priority-section"><h3>Back-to-Back Meetings</h3>
            <div class="priority-item">You have {back_to_back_count} set(s) with minimal break time</div>
            </div>
        '''

    if not alerts_html:
        alerts_html = '<div style="color: #51cf66; padding: 15px; text-align: center;">✓ No scheduling conflicts</div>'

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>H Visual Media — Daily Dashboard</title>
    <style>
        :root {{
            --primary: #1a1a1a;
            --secondary: #2d2d2d;
            --accent: #ff6b6b;
            --text: #ffffff;
            --text-dim: #b0b0b0;
            --success: #51cf66;
            --warning: #ffd43b;
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            color: var(--text);
            min-height: 100vh;
            padding: 20px;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}

        header {{
            text-align: center;
            margin-bottom: 40px;
            border-bottom: 2px solid var(--accent);
            padding-bottom: 20px;
        }}

        header h1 {{
            font-size: 2.5em;
            margin-bottom: 5px;
            color: var(--text);
        }}

        header .date-time {{
            color: var(--text-dim);
            font-size: 1.1em;
        }}

        .dashboard-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .card {{
            background: var(--secondary);
            border-radius: 10px;
            padding: 25px;
            border-left: 4px solid var(--accent);
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }}

        .card h2 {{
            font-size: 1.3em;
            margin-bottom: 15px;
            color: var(--accent);
            text-transform: uppercase;
            letter-spacing: 1px;
        }}

        .stats {{
            display: flex;
            justify-content: space-around;
            text-align: center;
        }}

        .stat {{
            flex: 1;
        }}

        .stat-value {{
            font-size: 2em;
            font-weight: bold;
            color: var(--accent);
            margin-bottom: 5px;
        }}

        .stat-label {{
            font-size: 0.9em;
            color: var(--text-dim);
        }}

        .schedule {{
            list-style: none;
        }}

        .schedule-item {{
            padding: 15px;
            margin-bottom: 10px;
            background: var(--primary);
            border-radius: 6px;
            border-left: 3px solid var(--accent);
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 15px;
        }}

        .schedule-item.conflict {{
            border-left-color: var(--warning);
            background: rgba(255, 212, 59, 0.1);
        }}

        .time {{
            font-weight: bold;
            color: var(--accent);
            min-width: 100px;
            font-size: 0.9em;
        }}

        .event-title {{
            flex: 1;
            color: var(--text);
        }}

        .event-title.conflict {{
            color: var(--warning);
        }}

        .badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.75em;
            font-weight: bold;
        }}

        .badge.conflict {{
            background: var(--warning);
            color: var(--primary);
        }}

        .badge.teams {{
            background: #0078d4;
            color: white;
        }}

        .badge.video {{
            background: #ea4335;
            color: white;
        }}

        .priority-section {{
            background: var(--primary);
            border-radius: 6px;
            padding: 15px;
            margin-top: 15px;
        }}

        .priority-section h3 {{
            color: var(--warning);
            margin-bottom: 10px;
            font-size: 0.95em;
        }}

        .priority-item {{
            color: var(--text);
            margin-bottom: 8px;
            padding-left: 15px;
            position: relative;
        }}

        .priority-item:before {{
            content: "⚠";
            position: absolute;
            left: 0;
            color: var(--warning);
        }}

        .updated-at {{
            text-align: center;
            color: var(--text-dim);
            font-size: 0.85em;
            margin-top: 30px;
        }}

        @media (max-width: 768px) {{
            header h1 {{
                font-size: 1.8em;
            }}

            .dashboard-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>H Visual Media — Daily Dashboard</h1>
            <div class="date-time">{today_str} at {time_str}</div>
        </header>

        <div class="dashboard-grid">
            <div class="card">
                <h2>Today's Overview</h2>
                <div class="stats">
                    <div class="stat">
                        <div class="stat-value">{len(work_events)}</div>
                        <div class="stat-label">Meetings</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value">{work_hours:.1f}</div>
                        <div class="stat-label">Work Hours</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value">{free_hours:.1f}</div>
                        <div class="stat-label">Free Time</div>
                    </div>
                </div>
            </div>

            <div class="card">
                <h2>⚠️ Alerts & Issues</h2>
                {alerts_html}
            </div>
        </div>

        <div class="card">
            <h2>📅 Today's Schedule</h2>
            <ul class="schedule">
                {schedule_html if schedule_html else '<li style="padding: 20px; text-align: center; color: #b0b0b0;">No scheduled events for today</li>'}
            </ul>
        </div>

        <div class="updated-at">
            <p>Last updated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
            <p style="font-size: 0.8em; margin-top: 10px;">Dashboard updates daily at 6:00 AM</p>
        </div>
    </div>
</body>
</html>
'''

    return html

def main():
    """Main execution"""
    try:
        service = get_calendar_service()
        events = get_today_events(service)

        html = generate_html(events)

        with open('index.html', 'w') as f:
            f.write(html)

        print(f'✓ Dashboard generated: {len(events)} events found')
        print(f'✓ File updated: index.html')

    except Exception as e:
        print(f'✗ Error: {e}')
        exit(1)

if __name__ == '__main__':
    main()
