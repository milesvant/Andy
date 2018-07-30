import re


class Andy_Helper:
    """A helper class which classifies commands into categories for Andy"""

    def __init__(self):
        self.command_keywords = {
            "music": ["play", "pause", "spotify", "music", "skip", "next",
                      "song", "playing", "playlist", "previous", "volume",
                      "quiet", "loud", ],
            "weather": ["weather", ],
            "calendar": ["calendar", "schedule", "events", ],
            "sms": ["text", "message", "sms"],
            "wiki": ["search", "look up", "what is ", "who is ", "what are ", "who are "],
            "sports": ["score", "game", ],
        }

    def classify_command(self, command):
        """Translates a command into a label which describes what kind of
            command it is (e.g. music or weather)"""
        labels = []
        for label in self.command_keywords:
            for keyword in self.command_keywords[label]:
                if keyword in command:
                    labels.append(label)
        return labels
