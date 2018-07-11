import re
from ..module_helper import ModuleHelper


class WeatherHelper(ModuleHelper):
    """A class which parses and interprets commands to a Weather object.

        Attributes:
            weather_re: a dictionary from string labels to lists of regular
                expressions which match commands with similar meanings (e.g.
                'What's the weather today?' and 'What's the weather outside now')
    """

    def __init__(self):
        ModuleHelper.__init__(self)
        self.weather_re = {
            "current today": [re.compile('[A-Z|a-z|\'| ]*weather (outside )?(going to be )?today\??'),
                              re.compile('[A-Z|a-z|\'| ]*weather (outside )?(now|like)\??'), ],
            "current tomorrow": [re.compile('[A-Z|a-z|\'| ]*weather (going to be )?tomorrow\??'), ],
            "external today": [re.compile('[A-Z|a-z|\'| ]*weather (going to be )?today in [A-Z|a-z|\'| ]+?'),
                               re.compile('[A-Z|a-z|\'| ]*weather now in [A-Z|a-z|\'| ]+\??'),
                               re.compile(
                                   '[A-Z|a-z|\'| ]*weather in [A-Z|a-z|\'| ]+ (going to be )?today\??'),
                               re.compile('[A-Z|a-z|\'| ]*weather in [A-Z|a-z|\'| ]+ now\??'), ],
            "external tomorrow": [re.compile('[A-Z|a-z|\'| ]*weather (going to be )?tomorrow in [A-Z|a-z|\'| ]+\??'),
                                  re.compile('[A-Z|a-z|\'| ]*weather in [A-Z|a-z|\'| ]+( going to be)? tomorrow\??'), ],
        }

    def parse_command(self, command):
        """Transforms a command into a label and possibly a location.

            Args:
                command: string, command entered by user

            Returns:
                a label (if any is matched) which describes what the command is
                requesting, along with a location if the command is requesting
                weather information on a location that's not the current
                location (and None otherwise). If no regexp is matched,
                (None, None) is returned.
        """
        for label in self.weather_re:
            for regexp in self.weather_re[label]:
                if regexp.fullmatch(command):
                    if "external" in label:
                        splits = command.split("in ")[1].split(" ")
                        if len(splits) == 1 or len(splits) == 2:
                            external_location = splits[0]
                        else:
                            external_location = " ".join(splits[0:-1])
                        return label, external_location
                    else:
                        return label, None
        return None, None
