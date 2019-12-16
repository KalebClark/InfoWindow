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

    def list(self):
        service = build('calendar', 'v3', credentials=self.creds)

        now = dt.utcnow().isoformat() + 'Z'
        result = service.events().list(calendarId='primary', timeMin=now,
                                       maxResults=20,
                                       singleEvents=True,
                                       orderBy='startTime').execute()

        events = result.get('items', [])

        # 2019-11-05T10:00:00-08:00
        items = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))

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
                "content": event['summary']
            })

        return items
