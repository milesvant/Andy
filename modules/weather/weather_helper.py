import re
from ..module_helper import ModuleHelper


class WeatherHelper(ModuleHelper):
    """A class which parses and interprets commands to a Weather object.

        Attributes:
            weather_re: a dictionary from string labels to lists of regular
                expressions which match commands with similar meanings (e.g.
                'What's the weather today?' and 'What's the weather outside
                now')
    """

    def __init__(self):
        ModuleHelper.__init__(self)
        self.weather_re = {
            # weather today in the current location
            "current today": [re.compile('[A-Z|a-z|\'| ]*weather (outside )?\
(going to be )?today\??'),
                              re.compile('[A-Z|a-z|\'| ]*weather (outside )?\
(now|like)\??'), ],
            # weather tomorrow in the current location
            "current tomorrow": [re.compile('[A-Z|a-z|\'| ]*weather (going to \
be )?tomorrow\??'), ],
            # weather today in an external location
            "external today": [re.compile('[A-Z|a-z|\'| ]*weather \
(going to be )?today in [A-Z|a-z|\'| ]+?'),
                               re.compile('[A-Z|a-z|\'| ]*weather now in \
[A-Z|a-z|\'| ]+\??'),
                               re.compile('[A-Z|a-z|\'| ]*weather in \
[A-Z|a-z|\'| ]+ (going to be )?today\??'),
                               re.compile('[A-Z|a-z|\'| ]*weather in \
[A-Z|a-z|\'| ]+ now\??'), ],
            # weather tomorrow in an external location
            "external tomorrow": [re.compile('[A-Z|a-z|\'| ]*weather (going to \
be )?tomorrow in [A-Z|a-z|\'| ]+\??'),
                                  re.compile('[A-Z|a-z|\'| ]*weather in \
[A-Z|a-z|\'| ]+( going to be)? tomorrow\??'), ],
            # weather on specified date in current location
            "current specific": [re.compile('[A-Z|a-z|\'| ]*weather (going to \
be )?on (monday|tuesday|wednesday|thursday|friday|saturday|sunday)\??'), ],
            # weather on specified date in external location
            "external specific": [re.compile('[A-Z|a-z|\'| ]*weather (going to \
be )?on (monday|tuesday|wednesday|thursday|friday|saturday|sunday) in \
[A-Z|a-z|\'| ]+\??'),
                                  re.compile('[A-Z|a-z|\'| ]*weather (going to \
be )?in [A-Z|a-z|\'| ]+ on (monday|tuesday|wednesday|thursday|friday|saturday\
|sunday)\??')],
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
                    if "external" in label and "specific" not in label:
                        splits = command.split("in ")[1].split(" ")
                        if len(splits) == 1 or len(splits) == 2:
                            external_location = splits[0]
                        else:
                            external_location = " ".join(splits[0:-1])
                        return label, external_location
                    elif label == "external specific":
                        if command.find(" on ") < command.find(" in "):
                            split_on = command.split(" on ")[1]
                            split_in = split_on.split(" in ")
                            day = self.weekday_to_int[split_in[0]]
                            external_location = split_in[1].replace('?', '')
                            return label, (day, external_location)
                        else:
                            split_in = command.split(" in ")[1]
                            split_on = split_in.split(" on ")
                            day = self.weekday_to_int[split_on[1]]
                            external_location = split_on[0].replace('?', '')
                            return label, (day, external_location)
                    elif label == "current specific":
                        day = self.weekday_to_int[
                            command.split("on ")[1].replace('?', '')]
                        return label, day
                    else:
                        return label, None
        return None, None
