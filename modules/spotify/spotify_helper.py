import re
from ..module_helper import ModuleHelper
from collections import OrderedDict


class SpotifyHelper(ModuleHelper):
    """A class which parses and interprets commands to a Spotify object.

        Attributes:
            spotify_re: an OrderedDict from string labels to lists of regular
                expressions which match commands with similar meanings (e.g.
                'Play the previous song' and 'play the song before this one')
    """

    def __init__(self):
        ModuleHelper.__init__(self)
        self.spotify_re = [
            ("resume", [re.compile('[A-Z|a-z| ]*(resume|play)( spotify| music| \
my music)?'), ]),
            ("pause", [re.compile('[A-Z|a-z| ]*(pause|stop)( spotify| music| \
my music)?'), ]),
            ("next", [re.compile('[A-Z|a-z| ]*skip[A-Z|a-z| ]*'),
                      re.compile('[A-Z|a-z| ]*next( song)?'), ]),
            ("previous", [re.compile('[A-Z|a-z| ]*previous( song)?'),
                          re.compile('[A-Z|a-z| ]*song before[A-Z|a-z| ]*')]),
            ("play playlist", [
             re.compile('[A-Z|a-z|\'| ]*(play)[A-Z|a-z|\'| ]*(playlist)\
[A-Z|a-z|\'| |0-9|\!]*')]),
            ("search", [
             re.compile('[A-Z|a-z| ]*play [A-Z|a-z|\'| |0-9]+( by \
[A-Z|a-z|\'| |0-9]+)?( on spotify)?'), ]),
            ("current", [re.compile('[A-Z|a-z|\'| ]*what[A-Z|a-z|\'| ]+(song|\
playing|playing now)\??'), ]),
            ("list playlist", [
             re.compile('[A-Z|a-z|\'| ]*(list|what)[A-Z|a-z|\'| ]*playlist(s)?\
[A-Z|a-z|\'| ]*')]),
            ("volume up", [
             re.compile('[A-Z|a-z|\'| ]*(volume|sound|song) up[A-Z|a-z|\'|\
 ]*'),
             re.compile('[A-Z|a-z|\'| ]*loud(er)?[A-Z|a-z|\'| ]*'),
             ]),
            ("volume down", [
                re.compile('[A-Z|a-z|\'| ]*(volume|sound|song) down[A-Z|a-z|\'|\
 ]*'),
                re.compile('[A-Z|a-z|\'| ]*quiet(er)?[A-Z|a-z|\'| ]*'),
            ]),
        ]
        self.spotify_re = OrderedDict(self.spotify_re)

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
                    elif label == "play playlist":
                        if "playlists " in command and "playlist " \
                                not in command:
                            playlist_term = command.split("playlists ")[1]
                        else:
                            playlist_term = command.split("playlist ")[1]
                        if playlist_term in list(self.number_dict.keys()):
                            playlist_term = self.number_dict[playlist_term]
                        return label, playlist_term
                    else:
                        return label, None
        return None, None
