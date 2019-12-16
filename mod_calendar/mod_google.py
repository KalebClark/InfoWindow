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
                if "primary" in calendar_list_entry.keys():
                    if calendar_list_entry['primary']:
                        calendar_ids.append(calendar_list_entry['id'])
                    elif calendar_list_entry['summary'] == self.additional:
                        calendar_ids.append(calendar_list_entry['id'])
            page_token = calendar_list.get('nextPageToken')
            if not page_token:
                break

        for id in calendar_ids:
            result = service.events().list(calendarId=id, timeMin=now,
                                           maxResults=10,
                                           singleEvents=True,
                                           orderBy='startTime').execute()

            for event in result.get('items', []):
                start = event['start'].get('dateTime', event['start'].get('date'))
                if start in events.keys():
                    start = "%sa" % start
                events[start] = event

        # 2019-11-05T10:00:00-08:00

        for event_key in sorted(events.keys()):
            start = events[event_key]['start'].get('dateTime', events[event_key]['start'].get('date'))

            # Sunrise and Sunset.
            if self.timeformat == "12h":
                st_date = dt.strftime(dtparse(start), format='%m-%d-%Y')
                st_time = dt.strftime(dtparse(start), format='%I:%M%p')
            else:
                st_date = dt.strftime(dtparse(start), format='%d.%m.%Y')
                st_time = dt.strftime(dtparse(start), format='%H:%M')

            items.append({
                "date": st_date,
                "time": st_time,
                "content": events[event_key]['summary']
            })

        return items
