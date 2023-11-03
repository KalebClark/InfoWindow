from mod_utils import mod_google_auth
from googleapiclient.discovery import build
from dateutil.parser import parse as dtparse
from datetime import datetime as dt
import logging

# Silence goofy google deprecated errors
logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)


class Cal:
    def __init__(self, options):
        ga = mod_google_auth.GoogleAuth()
        self.creds = ga.login()
        self.timeformat = options["timeformat"]
        self.additional = options["additional"]
        self.ignored = options["ignored"]
        self.sunday_first_dow = options["sunday_first_dow"]

    def list(self):
        calendar_ids = []
        events = {}
        items = []

        service = build('calendar', 'v3', credentials=self.creds)
        now = dt.utcnow().isoformat() + 'Z'

        page_token = None
        while True:
            calendar_list = service.calendarList().list(pageToken=page_token).execute()
            for calendar_list_entry in calendar_list['items']:
                if "primary" in list(calendar_list_entry.keys()):
                    if calendar_list_entry['primary']:
                        calendar_ids.append(calendar_list_entry['id'])
                elif calendar_list_entry['summary'] in self.additional:
                    calendar_ids.append(calendar_list_entry['id'])
            page_token = calendar_list.get('nextPageToken')
            if not page_token:
                break

        for id in calendar_ids:
            result = service.events().list(calendarId=id, timeMin=now,
                                           maxResults=30,
                                           singleEvents=True,
                                           orderBy='startTime').execute()

            for event in result.get('items', []):
                if event['summary'] in self.ignored:
                    continue
                initial_start = event['start'].get('dateTime', event['start'].get('date'))
                start = "%s-0" % initial_start
                counter = 0
                while start in list(events.keys()):
                    counter += 1
                    start = "%s-%s" % (initial_start, counter)

                events[start] = event

        day_start_ts_now = dt.timestamp(dt.now().replace(hour=0, minute=0, second=0, microsecond=0))

        for event_key in sorted(events.keys()):
            start = events[event_key]['start'].get('dateTime', events[event_key]['start'].get('date'))
            if int(dt.strftime(dtparse(start), '%Y%m%d')) <= int(dt.strftime(dt.today(), '%Y%m%d')):
                today = True
            else:
                today = False

            # Sunrise and Sunset.
            if self.timeformat == "12h":
                st_date = dt.strftime(dtparse(start), '%m-%d')
                st_time = dt.strftime(dtparse(start), '%I:%M %p')
            else:
                st_date = dt.strftime(dtparse(start), '%d.%m')
                st_time = dt.strftime(dtparse(start), '%H:%M')

            if self.sunday_first_dow:
                week = dt.strftime(dtparse(start), '%U')
            else:
                week = dt.strftime(dtparse(start), '%W')

            event_start_ts_now = dt.timestamp(dtparse(start).replace(hour=0, minute=0, second=0, microsecond=0))

            items.append({
                "date": st_date,
                "time": st_time,
                "content": events[event_key]['summary'],
                "today": today,
                "week": int(week),
                "days_away": (event_start_ts_now - day_start_ts_now) // 86400, # days away
                "weeks_away": (event_start_ts_now - day_start_ts_now) // 604800 # weeks away
            })

        return items
