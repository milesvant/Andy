import aiml
import os
import glob
import yaml
import re
import sys
import spotipy
import pyowm
import googleapiclient
import pyaudio
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
from spotify.spotify import Spotify
from weather.weather import Weather
from andy_calendar.andy_calendar import Calendar
from andy_helper import Andy_Helper


class Andy:
    """Creates an AI assistant which can respond to spoken or typed commands
        of numerous kinds.

       Attributes:
            spotify: A Spotify object, executes and responds to Spotify
                commands
            weather: A Weather object, executes and responds to Weather
                commands
            calendar: A Calendar object, executes and responds to Calendar
                commands
            helper: A helper which chooses which module to send commands to
            kernel: An AIML kernel which responds to some messages to Andy
            user_spoken: True if Andy should listen to commands through the
                microphone, and False if the command line should be used
            andy_spoken: True if Andy should use text to speech, and False if
                print statements should be used
            current_music: If music is currently being played or used, then
                current_music is equal to corresponding music module object in
                Andy's attributes
       """

    def __init__(self, default_music=None,
                 user_spoken=False, andy_spoken=False):
        self.spotify = Spotify()
        self.weather = Weather()
        self.calendar = Calendar()
        self.helper = Andy_Helper()
        self.kernel = aiml.Kernel()
        self.load_aiml()
        self.user_spoken = user_spoken
        self.andy_spoken = andy_spoken
        if default_music is None:
            self.current_music = None
        else:
            if default_music == "spotify":
                self.current_music = self.spotify

    def load_aiml(self):
        """loads each file in the aiml/ folder into the AIML interpreter"""
        for file in glob.glob('{}/aiml/*.xml'.format(
                os.path.abspath(os.path.dirname(__name__)))):
            self.kernel.learn(file)

    def prompt(self):
        """Prompts the user for input to Andy"""
        if self.user_spoken:
            pass
        else:
            user_input = input("> ")
            self.route_command(user_input.lower())

    def route_command(self, command):
        """Sends a user command to the corresponding module where it will be
            executed."""
        label = self.helper.classify_command(command)
        if label == "music":
            if self.current_music is not None:
                try:
                    self.say(self.current_music.route_command(command))
                except spotipy.client.SpotifyException:
                    self.say("Error executing Spotify command")
            else:
                self.say("No music currently selected.")
        elif label == "weather":
            try:
                self.say(self.weather.route_command(command))
            except pyowm.exceptions.api_call_error.APICallError:
                self.say("An error occurred while connecting to Open Weather Map")
        elif label == "calendar":
            try:
                self.say(self.calendar.route_command(command))
            except googleapiclient.errors.HttpError:
                self.say("An error occurred while connecting to Google Calendar")
        else:
            self.say("Cannot understand command")

    def say(self, text):
        """Says given text, either through printing it or using
            speech-to-text."""
        if self.andy_spoken:
            pass
        else:
            print(text)

    def loop(self):
        """Generates a REPL for Andy"""
        while True:
            try:
                self.prompt()
            except KeyboardInterrupt:
                self.say("Goodbye!")
                sys.exit()
