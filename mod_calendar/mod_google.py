from mod_utils import mod_google_auth
from googleapiclient.discovery import build
from dateutil.parser import parse as dtparse
from datetime import datetime as dt
import logging

# Silence goofy google deprecated errors
logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)


class Cal:
    def __init__(self, api_key):
        ga = mod_google_auth.GoogleAuth()
        self.creds = ga.login()

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
            st_date = dt.strftime(dtparse(start), format='%m-%d-%Y')
            st_time = dt.strftime(dtparse(start), format='%I:%M%p')
            items.append({
                "date": st_date,
                "time": st_time,
                "content": event['summary']
            })

        return items
