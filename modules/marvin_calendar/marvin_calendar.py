import os
from datetime import datetime, timedelta
from dateutil import tz
from googleapiclient import discovery
from httplib2 import Http
from oauth2client import file, client, tools
from .calendar_helper import CalendarHelper


class Calendar:
    """Class which allows Marvin to interact with the Google Calendar API.

        Attributes:
            helper: A Calendar_Helper object which assists with the
                interpretation of user commands.
            calendar: An object which enables calls to the Google Calendar API.
    """

    def __init__(self):
        self.helper = CalendarHelper()
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

    def get_tomorrow_events(self):
        """Returns a list of the events on the day after the current day."""
        today = datetime.utcnow().date()
        start = datetime(today.year, today.month, today.day) + timedelta(1)
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

    def get_this_week_events(self):
        """Returns a list of the events on the week containing the current
            day."""
        today = datetime.utcnow().date()
        start_of_week = datetime(today.year, today.month, today.day)
        end_of_week = start_of_week + timedelta(6)
        # Put dates in correct format for the API call
        start_of_week = (start_of_week.isoformat()) + 'Z'
        end_of_week = (end_of_week.isoformat()) + 'Z'

        events_result = self.calendar.events().list(
            calendarId='primary',
            timeMin=start_of_week,
            timeMax=end_of_week,
            singleEvents=True,
            orderBy='startTime',
        ).execute()
        events = events_result.get('items', [])
        return events

    def route_command(self, command, say, listen):
        """Executes and generates a string response for a given Calendar
            command.

            Args:
                command: a string command which requests some action or
                    information related to Google Calendar.
                say: A function which will say (either through text to speech
                    or printing) a string in the main speaker loop
                listen: A function which will listen and record user input
                    through either speech to text or through the CLI
            Returns:
                True if a command was executed (or failed while executed) and
                    false if the command was invalid.
        """
        label, args = self.helper.parse_command(command)
        # list today's events
        if label == "today events":
            events = self.get_today_events()
            if not events:
                say("No upcoming events today found.")
            else:
                response = "Today's events:\n"
                for event in events:
                    start = self.helper.get_non_military_time(
                        event['start'].get(
                            'dateTime',
                            event['start'].get('date')))
                    end = self.helper.get_non_military_time(event['end'].get(
                        'dateTime',
                        event['end'].get('date')))
                    response += "From " + start + " to " + end + " - "
                    response += event['summary'] + "\n"
                say(response)
        # list tomorrow's events
        elif label == "tomorrow events":
            events = self.get_tomorrow_events()
            if not events:
                say("No events found tomorrow.")
            else:
                response = "Tommorow's events:\n"
                for event in events:
                    start = self.helper.get_non_military_time(
                        event['start'].get(
                            'dateTime',
                            event['start'].get('date')))
                    end = self.helper.get_non_military_time(event['end'].get(
                        'dateTime',
                        event['end'].get('date')))
                    response += "From " + start + " to " + end + " - "
                    response += event['summary'] + "\n"
                say(response)
        # list this week's events
        elif label == "current week events":
            events = self.get_this_week_events()
            if not events:
                say("No events found this week.")
            else:
                response = "This week's events:\n"
                for event in events:
                    day_of_week = self.helper.get_day_of_week_from_string(
                        event['start'].get(
                            'dateTime',
                            event['start'].get('date')))
                    start = self.helper.get_non_military_time(
                        event['start'].get(
                            'dateTime',
                            event['start'].get('date')))
                    end = self.helper.get_non_military_time(event['end'].get(
                        'dateTime',
                        event['end'].get('date')))
                    response += "On " + day_of_week + " from " + start + " to "
                    response += end + " - " + event['summary'] + "\n"
                say(response)
        else:
            return False
        return True
