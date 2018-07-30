from .sms_helper import SMSHelper
from twilio.rest import Client
from twilio.base.exceptions import TwilioException
import os
import yaml


class SMS:
    """Class that enables Andy to send text messages using the Twilio API.

       Attributes:
            client: Twilio Client object
            twilio_number: The outgoing phone number registered with the Twilio
                account that this client uses.
            sms_suffix: A string which will be appended to the end of each
                SMS sent to show it's source and sender.
            helper: A SMSHelper object which will perform the parsing
                and interpretation of commands for this class.
    """

    def __init__(self, my_name):
        self.client, self.twilio_number = self.authenticate()
        self.sms_suffix = "Sent from Andy by: {}".format(my_name)
        self.helper = SMSHelper()

    def authenticate(self):
        """Authenticates and returns the Twilio Client object which will be used
            by this class, as well as (one of) the phone number(s) used by
            the Twilio account."""
        CREDENTIALS_FILE = "{}/twilio-credentials.yaml".format(
            os.path.abspath(os.path.dirname(__file__)))
        # load credentials from file if possible
        if os.path.exists(CREDENTIALS_FILE):
            with open(CREDENTIALS_FILE) as cf:
                credentials = yaml.load(cf)
                twilio_id = credentials['TWILIO_ACCOUNT_SID']
                twilio_token = credentials['TWILIO_ACCOUNT_TOKEN']
                twilio_number = credentials['TWILIO_PHONE_NUMBER']
        # if credentials file doesn't exist, then load credentials from
        # environment
        else:
            twilio_id = os.environ.get('TWILIO_ACCOUNT_SID')
            twilio_token = os.environ.get('TWILIO_ACCOUNT_TOKEN')
            twilio_number = os.environ.get('TWILIO_PHONE_NUMBER')
        return Client(twilio_id, twilio_token), twilio_number

    def send_message(self, say, listen):
        """Sends a SMS message through Twilio's API.

           Args:
                say: A function which will say (either through text to speech
                    or printing) a string in the main speaker loop
                listen: A function which will listen and record user input
                    through either speech to text or through the CLI
        """
        say("To what number?")
        number_string = listen()
        # Convert to form usable by Twilio Client Library
        number_string.replace('-', '')
        # Confirm number is correct
        confirmed = False
        while not confirmed:
            say("Please confirm number: {}".format(number_string))
            response = listen()
            if response in self.helper.positive_words:
                break
            say("Enter number again please: ")
            number_string = listen()
            number_string.replace('-', '')
        number_string = "+1" + number_string
        say("Ready for message")
        message = listen()
        # Confirm message is correct
        confirmed = False
        while not confirmed:
            say("Please confirm message: {}".format(message))
            response = listen()
            if response in self.helper.positive_words:
                break
            say("Enter message again please: ")
            message = listen()
        message = "{}\n{}".format(message, self.sms_suffix)
        try:
            self.client.messages.create(
                body=message,
                from_=self.twilio_number,
                to=number_string
            )
            say("Message successfully sent")
        except TwilioException:
            say("Failure while sending message")

    def route_command(self, command, say, listen):
        """Executes and generates  a string response for a given SMS
            command.

            Args:
                command: a string command which requests some action or
                    information related to SMS's.
                say: A function which will say (either through text to speech
                    or printing) a string in the main speaker loop
                listen: A function which will listen and record user input
                    through either speech to text or through the CLI
            Returns:
                True if a command was executed (or failed while executed) and
                    false if the command was invalid.
        """
        label = self.helper.parse_command(command)
        if label == "send":
            self.send_message(say, listen)
        else:
            return False
        return True
