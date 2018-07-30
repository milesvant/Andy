from .wiki_helper import WikiHelper
import wikipedia


class Wiki:
    """Class which allows Andy to look up queries on Wikipedia.

       Attributes:
            helper: a WikiHelper object which will perform the parsing
                and interpretation of commands for this class.
    """

    def __init__(self):
        self.helper = WikiHelper()

    def route_command(self, command, say, listen):
        """Generates a string response for a given wiki command.

            Args:
                command: a string command which requests some information on
                    wikipedia.
                say: A function which will say(either through text to speech
                    or printing) a string in the main speaker loop
                listen: A function which will listen and record user input
                    through either speech to text or through the CLI
            Returns:
                True if a command was executed (or failed while executed) and
                    false if the command was invalid.
        """
        label, query = self.helper.parse_command(command)
        if label == "search":
            # say("Searching for information about {} on Wikipedia".format(
            #    query))
            try:
                say(wikipedia.summary(query, sentences=2))
            except wikipedia.exceptions.PageError:
                say("Could not find any results for that query")
            except wikipedia.exceptions.DisambiguationError:
                say("Can you please clarify your query")
        else:
            return False
        return True
