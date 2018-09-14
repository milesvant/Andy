import re


class Marvin_Helper:
    """A helper class which classifies commands into categories for Marvin"""

    def __init__(self):
        self.command_keywords = {
            "music": ["play", "pause", "spotify", "music", "skip", "next",
                      "song", "playing", "playlist", "previous", "volume",
                      "quiet", "loud", ],
            "weather": ["weather", ],
            "calendar": ["calendar", "schedule", "events", ],
            "sms": ["text", "message", "sms"],
            "wiki": ["search", "look up", "what is ", "who is ", "what are ", "who are "],
            "sports": ["score", "game", "record", ],
            "stocks": ["stock"],
        }

    def classify_command(self, command):
        """Translates a command into a labels which describes what kind of
            command it could be (e.g. music or weather)"""
        labels = []
        for label in self.command_keywords:
            for keyword in self.command_keywords[label]:
                if keyword in command:
                    labels.append(label)
        return labels
