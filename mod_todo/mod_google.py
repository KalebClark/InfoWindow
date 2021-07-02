from mod_utils import mod_google_auth
from googleapiclient.discovery import build
from datetime import datetime
import logging

now = datetime.now()

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
                if 'items' in results.keys():
                    for task in results['items']:

                        today = False
                        if 'due' in task.keys():
                            if task['due'].startswith(now.strftime("%Y-%m-%d")):
                                today = True

                        items.append({
                            "content": task['title'],
                            "priority": task['position'],
                            "today": today
                        })

        # Return results to main program
        return items
