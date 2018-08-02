import re
import calendar
from datetime import datetime, timedelta
from ..module_helper import ModuleHelper


class SportsHelper(ModuleHelper):
    """A class which parses and interprets commands to a Sports object.

        Attributes:
            sports_re: a dictionary from string labels to lists of regular
                expressions which match commands with similar meanings (e.g.
                'schedule today' and 'What are my calendar events today?')
            baseball_teams_to_abbrev: a dictionary from baseball team names to
                their official abbreviations
            abbrev_to_baseball_teams: the inverse dictionary of
                baseball_teams_to_abbrev
    """

    def __init__(self):
        ModuleHelper.__init__(self)
        self.sports_re = {
            'result today': [re.compile('[A-Z|a-z|\'| ]*score of the [A-Z|a-z\
|\'| ]+ game( today)?\??'), ],
            'result yesterday': [re.compile('[A-Z|a-z|\'| ]*score of the [A-Z|\
a-z|\'| ]+ game yesterday\??')],
            'result specific': [re.compile('[A-Z|a-z|\'| ]*score of the [A-Z|\
a-z|\'| ]+ game (on|last) (monday|tuesday|wednesday|thursday|friday|saturday|\
sunday)\??')],
            'record': [re.compile(
                '[A-Z|a-z|\'| ]*record (of|for) the [A-Z|a-z|\'| ]+\
( this year)?\??'), re.compile('[A-Z|a-z|\'| ]*the [A-Z|a-z|\'| ]* record( this\
 year)?\??')],
        }
        self.baseball_teams_to_abbrev = {
            'diamondbacks': 'ARI',
            'braves': 'ATL',
            'orioles': 'BAL',
            'red sox': 'BOS',
            'cubs': 'CHC',
            'white sox': 'CHW',
            'indians': 'CLE',
            'rockies': 'COL',
            'tigers': 'DET',
            'marlins': 'MIA',
            'astros': 'HOU',
            'royals': 'KC',
            'angels': 'LAA',
            'dodgers': 'LAD',
            'brewers': 'MIL',
            'twins': 'MIN',
            'mets': 'NYM',
            'yankees': 'NYY',
            'a\'s': 'OAK',
            'phillies': 'PHI',
            'pirates': 'PIT',
            'mariners': 'SEA',
            'padres': 'SD',
            'giants': 'SF',
            'cardinals': 'STL',
            'rays': 'TB',
            'rangers': 'TEX',
            'blue jays': 'TOR',
            'nationals': 'WSN',
        }
        self.abbrev_to_baseball_teams = {
            'ARI': 'diamondbacks',
            'ATL': 'braves',
            'BAL': 'orioles',
            'BOS': 'red sox',
            'CHC': 'cubs',
            'CHW': 'white sox',
            'CLE': 'indians',
            'COL': 'rockies',
            'DET': 'tigers',
            'MIA': 'marlins',
            'HOU': 'astros',
            'KC': 'royals',
            'LAA': 'angels',
            'LAD': 'dodgers',
            'MIL': 'brewers',
            'MIN': 'twins',
            'NYM': 'mets',
            'NYY': 'yankees',
            'OAK': 'a\'s',
            'PHI': 'phillies',
            'PIT': 'pirates',
            'SEA': 'mariners',
            'SD': 'padres',
            'SFG': 'giants',
            'STL': 'cardinals',
            'TB': 'rays',
            'TEX': 'rangers',
            'TOR': 'blue jays',
            'WSN': 'nationals',
        }

    def day_of_week_to_date(self, day, today):
        """Creates a datetime object out of a weekday string.

           Args:
                day: the string of a weekday name (e.g. "monday" or "tuesday")
                today: the datetime object representing today
           Returns:
                the datetime object for the most recent instance of the given
                weekday
        """
        day = self.weekday_to_int[day]
        if today.weekday() >= day:
            return (today + timedelta(today.weekday() - day))
        else:
            return (today - timedelta((today.weekday() - day) % 7))

    def date_to_dataframe_index(self, date):
        """Converts datetime objects into the format used by the pybasball
            pandas objects (e.g. 2018-7-30 -> Monday, Jul 30)"""
        day_of_the_week = self.int_to_weekday[date.weekday()]
        month_abbr = calendar.month_abbr[date.month]
        day_number = date.day
        index = "{}, {} {}".format(day_of_the_week, month_abbr, day_number)
        return index

    def dataframe_first_instance_of(self, df, index):
        """Finds the first instance of a given date in a pandas object and
            returns its index, or -1 if it is not found."""
        for i in range(len(df['Date'])):
            try:
                if df['Date'][i] == index:
                    return i
            except KeyError:
                pass
        return -1

    def dataframe_last_non_nan(self, df):
        """Finds the last instance of a W-L record that isn't nan in a pandas
            series."""
        last = None
        for i in range(len(df['W-L'])):
            try:
                record = df['W-L'][i]
                if record is None:
                    return last
                else:
                    last = record
            except KeyError:
                pass
        return ""

    def parse_command(self, command):
        """Transforms a command into a label.

            Args:
                command: string, command entered by user

            Returns:
                the label of the first regular expression in
                self.sports_re which matches command, then either a team name,
                or a dictionary with a team name and day of the week name.
                None, None is returned if no matches to regular expressions
                can be found.
        """
        for label in self.sports_re:
            for regexp in self.sports_re[label]:
                if regexp.fullmatch(command):
                    if label == "result today" or label == "result yesterday":
                        team_name = (command.split("score of the ")[1]).split(
                            " game")[0]
                        return label, team_name
                    elif label == "result specific":
                        team_name = (command.split("score of the ")[1]).split(
                            " game")[0]
                        if " game on " in command:
                            day_of_week = (command.split(" game on ")[1])
                        else:
                            day_of_week = (command.split(" game last ")[1])
                        if '?' in day_of_week:
                            day_of_week = day_of_week[:-1]
                        return label, {"team": team_name, "day": day_of_week}
                    elif label == "record":
                        if command.endswith('?'):
                            command = command.split('?')[0]
                        if command.endswith('record') or command.endswith('record this year'):
                            team_name = (command.split(" record")[0]).split(
                                " the ")[1]
                            if team_name.endswith("\'s"):
                                team_name = team_name[:-2]
                            elif team_name.endswith("\'"):
                                team_name = team_name[:-1]
                            return label, team_name
                        else:
                            if " of the " in command:
                                team_name = command.split(" of the ")[1]
                            else:
                                team_name = command.split(" for the ")[1]
                            if " this year" in command:
                                team_name = team_name.split(" this year")[0]
                            return label, team_name
        return None, None
