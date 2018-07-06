import os
from datetime import datetime, timedelta
from dateutil import tz
from googleapiclient import discovery
from httplib2 import Http
from oauth2client import file, client, tools
from .calendar_helper import Calendar_Helper


class Calendar:
    """Class which allows Andy to interact with the Google Calendar API.

        Attributes:
            helper: A Calendar_Helper object which assists with the
                interpretation of user commands.
            calendar: An object which enables calls to the Google Calendar API.
    """

    def __init__(self):
        self.helper = Calendar_Helper()
        self.calendar = self.authorize()

    def authorize(self):
        """Authorizes this program to read and write a user's Google Calendar.

           Returns:
                An object which enables calls to the Google Calendar API.
        """
        # read+write scope
        SCOPES = 'https://www.googleapis.com/auth/calendar'
        store = file.Storage('credentials.json')
        creds = store.get()
        if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets(
                '{}/client-secret.json'.format(
                    os.path.abspath(os.path.dirname(__file__))), SCOPES)
            creds = tools.run_flow(flow, store)
        service = discovery.build('calendar', 'v3',
                                  http=creds.authorize(Http()))
        return service

    def get_today_events(self):
        """Returns a list of the events on the current day."""
        today = datetime.utcnow().date()
        start = datetime(today.year, today.month, today.day)
        end = start + timedelta(1)
        # Put dates in correct format for the API call
        start = (start.isoformat()) + 'Z'
        end = (end.isoformat()) + 'Z'

        events_result = self.calendar.events().list(
            calendarId='primary',
            timeMin=start,
            timeMax=end,
            singleEvents=True,
            orderBy='startTime',
        ).execute()
        events = events_result.get('items', [])
        return events

    def route_command(self, command):
        """Executes and generates a string response for a given Calendar
            command.

            Args:
                command: a string command which requests some action or
                    information related to Google Calendar.
            Returns:
                A string response to the command.
        """
        label, args = self.helper.parse_command(command)
        if label == "today events":
            events = self.get_today_events()
            if not events:
                return "No upcoming events found."
            else:
                response = ""
                for event in events:
                    start = event['start'].get('dateTime',
                                               event['start'].get('date'))
                    response += start + ": "
                    response += event['summary']
                    response += "\n"
                return response
        else:
            return None
