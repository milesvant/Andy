import re


class Spotify_Helper:
    """A class which parses and interprets commands to a Spotify object.

        Attributes:
            spotify_re: a dictionary from string labels to lists of regular
                expressions which match commands with similar meanings (e.g.
                'Play the previous song' and 'play the song before this one')
    """

    def __init__(self):
        self.spotify_re = {
            "resume": [re.compile('[A-Z|a-z| ]*(resume|play)( spotify| music| my music)?'), ],
            "pause": [re.compile('[A-Z|a-z| ]*(pause|stop)( spotify| music| my music)?'), ],
            "next": [re.compile('[A-Z|a-z| ]*skip[A-Z|a-z| ]*'),
                     re.compile('[A-Z|a-z| ]*next( song)?'), ],
            "previous": [re.compile('[A-Z|a-z| ]*previous( song)?'),
                         re.compile('[A-Z|a-z| ]*song before[A-Z|a-z| ]*'), ],
            "search": [re.compile('[A-Z|a-z| ]*play [A-Z|a-z|\'| |0-9]+( by [A-Z|a-z|\'| |0-9]+)?( on spotify)?'), ],
            "current": [re.compile('[A-Z|a-z|\'| ]*what[A-Z|a-z|\'| ]+(song|playing|playing now)\??'), ],
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
        for label in self.spotify_re:
            for regexp in self.spotify_re[label]:
                if regexp.fullmatch(command):
                    if label == "search":
                        search_plus = command.split("play ")[1]
                        if " on spotify" in search_plus:
                            search_plus = search_plus.split(" on spotify")[0]
                        query = " ".join(search_plus.split(" by "))
                        return label, query
                    else:
                        return label, None
        return None, None
