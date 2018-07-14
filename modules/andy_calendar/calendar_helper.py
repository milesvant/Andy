import re
from datetime import datetime
from ..module_helper import ModuleHelper


class CalendarHelper(ModuleHelper):
    """A class which parses and interprets commands to a Calendar object.

        Attributes:
            calendar_re: a dictionary from string labels to lists of regular
                expressions which match commands with similar meanings (e.g.
                'schedule today' and 'What are my calendar events today?')
            int_to_weekday: a dictionary from ints to the corresponding string
                of the day of the week (where Monday is 0 and Sunday is 6)
            weekeday_to_int: a dictionary from string names of the days of the
                week to their corresponding index in the week
                (i.e. 0 -> monday)
    """

    def __init__(self):
        ModuleHelper.__init__(self)
        self.calendar_re = {
            "today events": [re.compile('[A-Z|a-z| |\']*(calendar|schedule|\
events)[A-Z|a-z| |\']*today\??'), ],
            "tomorrow events": [re.compile('[A-Z|a-z| |\']*(calendar|schedule\
|events)[A-Z|a-z| |\']*tomorrow\??'), ],
            "current week events": [re.compile('[A-Z|a-z| |\']*(calendar|\
schedule|events)[A-Z|a-z| |\']*(this|next) week\??'), ],
        }

        self.int_to_weekday = {
            0: "Monday",
            1: "Tuesday",
            2: "Wednesday",
            3: "Thursday",
            4: "Friday",
            5: "Saturday",
            6: "Sunday",
        }

        self.weekday_to_int = {
            "monday": 0,
            "tuesday": 1,
            "wednesday": 2,
            "thursday": 3,
            "friday": 4,
            "saturday": 5,
            "sunday": 6,
        }

    def parse_command(self, command):
        """Transforms a command into a label.

            Args:
                command: string, command entered by user

            Returns:
                the label of the first regular expression in
                self.calendar_re which matches command, then None
        """
        for label in self.calendar_re:
            for regexp in self.calendar_re[label]:
                if regexp.fullmatch(command):
                    return label, None
        return None, None

    def get_non_military_time(self, time_string):
        """Removes dates and military time from strings returned by the Google
            Calendar API.

            Example:
                2018-07-11T16:30:00-04:00 -> 4:30 PM
        """
        after_t = time_string.split('T')[1]
        time = after_t[0:5]
        # convert from military time and add AM/PM
        if int(time[0:2]) > 12:
            time = str(int(time[0:2]) - 12) + time[2:5] + " PM"
        else:
            time += " AM"
        return time

    def get_day_of_week_from_string(self, time_string):
        """Converts a string returned from a Google Calendar API call to a
            day of the week.

            Example:
                2018-07-11T16:30:00-04:00 -> Wednesday
        """
        year = time_string[0:4]
        month = time_string[5:7]
        day = time_string[8:10]
        date = datetime(int(year), int(month), int(day))
        day_of_week = date.weekday()
        return self.int_to_weekday[day_of_week]
