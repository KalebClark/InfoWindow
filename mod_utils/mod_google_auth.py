from apiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from mod_utils import iw_utils
import pickle
import os.path
import sys
import logging

logger = logging.getLogger(__name__)


class GoogleAuth:
    def __init__(self):
        logger.info("Initializing Module: GoogleAuth")
        self.scopes = [
            'https://www.googleapis.com/auth/calendar',
            'https://www.googleapis.com/auth/tasks'
        ]

        self.creds = None

    def getCWD(self):
        path = os.path.dirname(os.path.realpath(sys.argv[0]))
        return path

    def login(self): 

        # Check for pickle.
        # if os.path.exists('token.pickle'):
        pickle_token_file_path = os.path.join(self.getCWD(), '/token.pickle')
        if os.path.exists(pickle_token_file_path):
            logger.info("token.pickle Exists. Attempting read")
            with open(pickle_token_file_path, 'rb') as token:
                self.creds = pickle.load(token)
        else:
            logger.info("%s NOT FOUND" % pickle_token_file_path)
        
        # If there are no valid creds, let user login.
        # If we get to this point there is a user interaction that needs
        # to happen. Must generate some sort of display on e-ink to let the
        # user know that they need to run interactivly.
        if not self.creds or not self.creds.valid:
            logger.info("Credentials do not exist, or are not valid.")

            # Requires input from user. Write error to e-ink if is run from cron.
            # if iw_utils.isCron():
            #     iw_utils.HandleError("Google Credentials do not exist, or are not valid")

            if self.creds and self.creds.expired and self.creds.refresh_token:
                logging.info("Refreshing Google Auth Credentials")
                self.creds.refresh(Request())
            else:
                # Check to see if google_secret.json exists. Throw error if not
                google_secrets_file_path = os.path.join(self.getCWD, '/google_secret.json')
                if not os.path.exists(google_secrets_file_path):
                    logger.info("%s does not exist" % google_secrets_file_path)

                # Requires input from user. Write error to e-ink if is run from cron.
                if iw_utils.isCron():
                    iw_utils.HandleError('Message')

                flow = InstalledAppFlow.from_client_secrets_file(
                    google_secrets_file_path, self.scopes
                )

                self.creds = flow.run_console()
            
            # Write pickle file
            logger.info("Writing %s file", pickle_token_file_path)
            with open(pickle_token_file_path, 'wb') as token:
                pickle.dump(self.creds, token)

        return self.creds