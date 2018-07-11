from pyowm import OWM
from pyowm.exceptions.not_found_error import NotFoundError
from urllib.request import urlopen
from urllib.error import HTTPError
from .weather_helper import WeatherHelper
from datetime import datetime, timedelta
import requests
import os
import yaml
import socket
import re


class Weather:
    """Class which generates info and responses about the weather for Andy.

       Attributes:
        _OWM: OWM object that this class wraps
        current_location: a dictionary containing the current city, latitude,
            and longitude of this Weather instance. Weather can be determined
            for areas other than the current position, but the current
            information is cached to reduce API requests.
        helper: a Weather_Helper object which will perform the parsing
            and interpretation of commands for this class.
    """

    def __init__(self):
        CREDENTIALS_FILE = "{}/weather-credentials.yaml".format(
            os.path.abspath(os.path.dirname(__file__)))
        if os.path.exists(CREDENTIALS_FILE):
            with open(CREDENTIALS_FILE) as cf:
                credentials = yaml.load(cf)
                owm_api_key = credentials['OWM_API_KEY']
                self.ipstack_api_key = credentials['IPSTACK_API_KEY']
        else:
            owm_api_key = os.environ.get('OWM_API_KEY')
            self.ipstack_api_key = os.environ.get('IPSTACK_API_KEY')
        self._OWM = OWM(owm_api_key)
        self.current_location = self.get_current_location()
        self.helper = WeatherHelper()

    def get_ip_address(self):
        """Returns a string of the current (public) IP address."""
        return urlopen('http://ip.42.pl/raw').read().decode("utf-8")

    def get_current_location(self):
        """Returns a dictionary with the current city name, latitude, and
            longitude based on the current IP address."""
        url = 'http://api.ipstack.com/{}?access_key={}'.format(
            self.get_ip_address(), self.ipstack_api_key
        )
        data = requests.get(url=url).json()
        return dict(
            city=data['city'],
            latitude=data['latitude'],
            longitude=data['longitude'],
        )

    def get_current_weather(self, location=None):
        """Gets the weather today at some location.

            Args:
                The (string) name of a location to find the weather at,
                defaults to None and uses current location if no arg is given.
            Returns:
                A pyowm weather object.
        """
        if location is None:
            return self._OWM.weather_at_coords(
                self.current_location['latitude'],
                self.current_location['longitude'])
        else:
            return self._OWM.weather_at_place(location)

    def get_tomorrow_weather(self, location=None):
        """Gets the weather tomorrow at some location.

            Args:
                The (string) name of a location to find the weather at,
                defaults to None and uses current location if no arg is given.
            Returns:
                A pyowm weather object.
        """
        tomorrow = datetime.now() + timedelta(days=1)
        if location is None:
            return self._OWM.three_hours_forecast_at_coords(
                self.current_location['latitude'],
                self.current_location['longitude'],
            ).get_weather_at(tomorrow)
        else:
            return self._OWM.three_hours_forecast(
                location).get_weather_at(tomorrow)

    def translate_weather_code(self, code):
        """Translates a numerical OWM weather status code to its english
            equivalent."""
        code = str(code)
        if code.startswith("2"):
            return "a thunderstorm"
        elif code.startswith("3"):
            return "drizzling"
        elif code.startswith("5"):
            return "raining"
        elif code.startswith("6"):
            return "snowing"
        elif code == "800":
            return "clear"
        elif code.startswith("8"):
            return "cloudy"
        else:
            return None

    def route_command(self, command, say, listen):
        """Generates a string response for a given weather command.

            Args:
                command: a string command which requests some information about
                    the weather.
                say: A function which will say (either through text to speech
                    or printing) a string in the main speaker loop
                listen: A function which will listen and record user input
                    through either speech to text or through the CLI
            Returns:
                True if a command was executed (or failed while executed) and
                    false if the command was invalid.
        """
        label, external_location = self.helper.parse_command(command)
        if label == "current today":
            weather = self.get_current_weather().get_weather()
            weather_code = self.translate_weather_code(
                weather.get_weather_code())
            if weather_code is not None:
                say('The weather today in {} will be {} with a minimum of {} degrees and a maximum of {} degrees.'.format(
                    self.current_location['city'],
                    weather_code,
                    weather.get_temperature(unit='fahrenheit')['temp_min'],
                    weather.get_temperature(unit='fahrenheit')['temp_max'],
                ))
            else:
                say('The weather today in {} will be a minimum of {} degrees and a maximum of {} degrees.'.format(
                    self.current_location['city'],
                    weather.get_temperature(unit='fahrenheit')['temp_min'],
                    weather.get_temperature(unit='fahrenheit')['temp_max'],
                ))
        elif label == "current tomorrow":
            weather = self.get_tomorrow_weather()
            weather_code = self.translate_weather_code(
                weather.get_weather_code())
            if weather_code is not None:
                say('The weather tomorrow in {} will be {} and {} degrees.'.format(
                    self.current_location['city'],
                    weather_code,
                    weather.get_temperature(unit='fahrenheit')['temp_max'],
                ))
            else:
                say('The weather tomorrow in {} will be {} degrees.'.format(
                    self.current_location['city'],
                    weather.get_temperature(unit='fahrenheit')['temp_max'],
                ))
        elif label == "external today":
            try:
                weather = self.get_current_weather(
                    location=external_location).get_weather()
                weather_code = self.translate_weather_code(
                    weather.get_weather_code())
                if weather_code is not None:
                    say('The weather today in {} will be {} with a minimum of {} degrees and a maximum of {} degrees.'.format(
                        external_location,
                        weather_code,
                        weather.get_temperature(unit='fahrenheit')['temp_min'],
                        weather.get_temperature(unit='fahrenheit')['temp_max'],
                    ))
                else:
                    say('The weather today in {} will be a minimum of {} degrees and a maximum of {} degrees.'.format(
                        external_location,
                        weather.get_temperature(unit='fahrenheit')['temp_min'],
                        weather.get_temperature(unit='fahrenheit')['temp_max'],
                    ))
            except NotFoundError:
                say("Please clarify your weather query.")
        elif label == "external tomorrow":
            try:
                weather = self.get_tomorrow_weather(external_location)
                weather_code = self.translate_weather_code(
                    weather.get_weather_code())
                if weather_code is not None:
                    say('The weather tomorrow in {} will be {} and {} degrees.'.format(
                        external_location,
                        weather_code,
                        weather.get_temperature(unit='fahrenheit')['temp_min'],
                    ))
                else:
                    say('The weather tomorrow in {} will be {} degrees.'.format(
                        external_location,
                        weather.get_temperature(unit='fahrenheit')['temp_min'],
                    ))
            except NotFoundError:
                say("Please clarify your weather query.")
        else:
            return False
        return True
