from mod_utils import mod_google_auth
from googleapiclient.discovery import build
from datetime import timedelta, date
import logging

today = date.today()
tomorrow = date.today() + timedelta(days=1)

logger = logging.getLogger(__name__)


class ToDo:
    def __init__(self, api_key):
        # This module authenticates from Google Auth API. We pull in the auth module 
        # wrapper to keep it clean. 
        logger.info("Initializing Module: ToDo: GOOGLE")
        ga = mod_google_auth.GoogleAuth()
        self.creds = ga.login()

    def list(self):
        logging.info("Entering ToDo.list()")
        service = build('tasks', 'v1', credentials=self.creds)

        items = []

        # Fetch Results from all lists where todo is in the name
        tasklists = service.tasklists().list().execute()
        for tasklist in tasklists['items']:
            if "todo" in tasklist['title'].lower():
                results = service.tasks().list(tasklist=tasklist['id']).execute()

                # Loop through results and format them for ingest
                if 'items' in list(results.keys()):
                    for task in results['items']:

                        is_today = False
                        if 'due' in list(task.keys()):
                            if task['due'].startswith(today.strftime("%Y-%m-%d")):
                                is_today = True
                            elif task['due'].startswith(tomorrow.strftime("%Y-%m-%d")):
                                pass
                            else:
                                # if this task is 3 days or more in the future, don't show it
                                continue

                        items.append({
                            "content": task['title'],
                            "priority": task['position'],
                            "today": is_today
                        })

        # Return results to main program
        return items
