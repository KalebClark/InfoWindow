from mod_utils import mod_google_auth
from googleapiclient.discovery import build
import logging

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

        # Fetch Results
        results = service.tasks().list(tasklist='YVJWSXk4cXVhZk1aSGlmag').execute()

        items = []

        # Loop through results and format them for ingest
        for task in results['items']:
            items.append({
                "content": task['title'],
                "priority": task['position']
            })

        # Return results to main program
        return items