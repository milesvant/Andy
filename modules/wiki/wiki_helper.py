from ..module_helper import ModuleHelper
import re


class WikiHelper(ModuleHelper):
    """A class which parses and interprets commands to a Wiki object.

        Attributes:
            wiki_re: a dictionary from string labels to lists of regular
                expressions which match commands with similar meanings (e.g.
                'What's the weather today?' and 'What's the weather outside
                now')
    """

    def __init__(self):
        ModuleHelper.__init__(self)
        self.wiki_re = {
            "search": [re.compile("[A-Z|a-z|\'| ]*(search|look up) [A-Z|a-z\
|\'|0-9| |:]*(on wikipedia)?"), re.compile("[A-Z|a-z|\'| ]*(what is|who is) \
[A-Z|a-z|\'|0-9| |:]*\??"), ],
        }

    def parse_command(self, command):
        """Transforms a command into a label.

            Args:
                command: string, command entered by user

            Returns:
                the label of the first regular expression in
                self.wiki_re which matches command
        """
        for label in self.wiki_re:
            for regexp in self.wiki_re[label]:
                if regexp.fullmatch(command):
                    if label == "search":
                        if "search " in command and "look up " not in command:
                            command = command.split("search ")[1]
                        elif "look up " in command:
                            command = command.split("look up ")[1]
                        elif "what is " in command:
                            command = command.split("what is ")[1].replace(
                                "?", "")
                        elif "who is " in command:
                            command = command.split("who is ")[1].replace(
                                "?", "")
                        if "on wikipedia" in command:
                            command = command.split(" on wikipedia")[0]
                        return label, command
        return None
