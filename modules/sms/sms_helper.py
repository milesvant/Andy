from ..module_helper import ModuleHelper
import re


class SMSHelper(ModuleHelper):

    def __init__(self):
        ModuleHelper.__init__(self)
        self.sms_re = {
            "send": [re.compile("[A-Z|a-z|\'| ]*send( | a )(message|text|sms)\
[A-Z|a-z|\'| ]*"), ],
        }

    def parse_command(self, command):
        """Transforms a command into a label.

            Args:
                command: string, command entered by user

            Returns:
                the label of the first regular expression in
                self.sms_re which matches command
        """
        for label in self.sms_re:
            for regexp in self.sms_re[label]:
                if regexp.fullmatch(command):
                    return label
        return None
