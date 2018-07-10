import re
from collections import OrderedDict


class Spotify_Helper:
    """A class which parses and interprets commands to a Spotify object.

        Attributes:
            spotify_re: an OrderedDict from string labels to lists of regular
                expressions which match commands with similar meanings (e.g.
                'Play the previous song' and 'play the song before this one')
            positive_words: a list of words which are affirmative responses to
                questions
            negative_words: a list of words which are negative responses to
                questions
            number_dict: a dictionary from string words to their corresponding
                ints
    """

    def __init__(self):
        self.spotify_re = [
            ("resume", [re.compile('[A-Z|a-z| ]*(resume|play)( spotify| music| my music)?'), ]),
            ("pause", [re.compile('[A-Z|a-z| ]*(pause|stop)( spotify| music| my music)?'), ]),
            ("next", [re.compile('[A-Z|a-z| ]*skip[A-Z|a-z| ]*'),
                      re.compile('[A-Z|a-z| ]*next( song)?'), ]),
            ("previous", [re.compile('[A-Z|a-z| ]*previous( song)?'),
                          re.compile('[A-Z|a-z| ]*song before[A-Z|a-z| ]*'), ]),
            ("play playlist", [
             re.compile('[A-Z|a-z|\'| ]*(play)[A-Z|a-z|\'| ]*(playlist)[A-Z|a-z|\'| |0-9|\!]*')]),
            ("search", [
             re.compile('[A-Z|a-z| ]*play [A-Z|a-z|\'| |0-9]+( by [A-Z|a-z|\'| |0-9]+)?( on spotify)?'), ]),
            ("current", [re.compile('[A-Z|a-z|\'| ]*what[A-Z|a-z|\'| ]+(song|playing|playing now)\??'), ]),
            ("list playlist", [
             re.compile('[A-Z|a-z|\'| ]*(list|what)[A-Z|a-z|\'| ]*playlist(s)?[A-Z|a-z|\'| ]*')]),
            ("volume up", [
             re.compile('[A-Z|a-z|\'| ]*(volume|sound|song) up[A-Z|a-z|\'| ]*'),
             re.compile('[A-Z|a-z|\'| ]*quieter[A-Z|a-z|\'| ]*'),
             ]),
            ("volume down", [
                re.compile('[A-Z|a-z|\'| ]*(volume|sound|song) down[A-Z|a-z|\'| ]*'),
                re.compile('[A-Z|a-z|\'| ]*louder[A-Z|a-z|\'| ]*'),
            ]),
        ]
        self.spotify_re = OrderedDict(self.spotify_re)

        self.positive_words = ["yes", "sure", "ok"]
        self.negative_words = ["no", "nope"]
        self.number_dict = self.init_number_dict()

    def init_number_dict(self):
        d = {
            'one': 1,
            'two': 2,
            'three': 3,
            'four': 4,
            'five': 5,
            'six': 6,
            'seven': 7,
            'eight': 8,
            'nine': 9,
            'ten': 10,
            'eleven': 11,
            'twelve': 12,
            'thirteen': 13,
            'fourteen': 14,
            'fifteen': 15,
            'sixteen': 16,
            'seventeen': 17,
            'eighteen': 18,
            'nineteen': 19,
            'twenty': 20,
            'thirty': 30,
            'forty': 40,
            'fifty': 50,
        }
        inverse_d = {
            1: 'one',
            2: 'two',
            3: 'three',
            4: 'four',
            5: 'five',
            6: 'six',
            7: 'seven',
            8: 'eight',
            9: 'nine',
        }
        for i in range(1, 10):
            d["twenty" + " " + inverse_d[i]] = 20 + i
        for i in range(1, 10):
            d["thirty" + " " + inverse_d[i]] = 30 + i
        for i in range(1, 10):
            d["fourty" + " " + inverse_d[i]] = 40 + i
        return d

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
