from ..module_helper import ModuleHelper
import re


class StocksHelper(ModuleHelper):

    def __init__(self):
        """A class which parses and interprets commands to a Stocks object.

            Attributes:
                stocks_re: a dictionary from string labels to lists of regular
                    expressions which match commands with similar meanings (e.g.
                    'Play the previous song' and 'play the song before this one')
        """
        self.stocks_re = {
            "price": [re.compile("[A-Z|a-z|\'| ]*stock price of [A-Z|a-z]+( today)?\??"),
                      re.compile("[A-Z|a-z|\'| ]price of [A-Z|a-z]+ stock( today)?\??")],
        }

    def parse_command(self, command):
        """Transforms a command into a label.

            Args:
                command: string, command entered by user

            Returns:
                the label of the first regular expression in
                self.stocks_re which matches command, then either None or
                the ticker to search for
        """
        for label in self.stocks_re:
            for regexp in self.stocks_re[label]:
                if regexp.fullmatch(command):
                    ticker = None
                    if label == "price":
                        ticker = command.split("price of ")[1]
                        if "stock " in ticker:
                            ticker = ticker.split(" stock")[0]
                        elif " today" in ticker:
                            ticker = ticker.split(" today")[0]
                    return label, ticker
        return None, None
