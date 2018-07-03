import re


class Andy_Helper:
    """A helper class which classifies commands into categories for Andy"""

    def __init__(self):
        self.command_keywords = {
            "music": ["play", "pause", "spotify", "music", "skip", "next",
                      "song", "playing", ],
            "weather": ["weather", ],
            "": [""],
        }

    def classify_command(self, command):
        """Translates a command into a label which describes what kind of
            command it is (e.g. music or weather)"""
        for label in self.command_keywords:
            for keyword in self.command_keywords[label]:
                if keyword in command:
                    return label
        else:
            return None
