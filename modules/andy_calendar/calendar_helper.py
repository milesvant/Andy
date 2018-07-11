import re
from ..module_helper import ModuleHelper


class CalendarHelper(ModuleHelper):
    """A class which parses and interprets commands to a Calendar object.

        Attributes:
            calendar_re: a dictionary from string labels to lists of regular
                expressions which match commands with similar meanings (e.g.
                'schedule today' and 'What are my calendar events today?')
    """

    def __init__(self):
        ModuleHelper.__init__(self)
        self.calendar_re = {
            "today events": [re.compile('[A-Z|a-z| |\']*(calendar|schedule|events)[A-Z|a-z| |\']*today\??'), ],
        }

    def parse_command(self, command):
        """Transforms a command into a label.

            Args:
                command: string, command entered by user

            Returns:
                the label of the first regular expression in
                self.spotify_re which matches command, then either None or
                the query to search for if the command was requesting a search
                of spotify.
        """
        for label in self.calendar_re:
            for regexp in self.calendar_re[label]:
                if regexp.fullmatch(command):
                    return label, None
        return None, None
