import aiml
import os
import glob
import yaml
import re
import sys
import spotipy
from spotify.spotify import Spotify
from weather.weather import Weather
from andy_helper import Andy_Helper


class Andy:
    """Creates an AI assistant which can respond to spoken or typed commands
        of numerous kinds.

       Attributes:
            spotify: A Spotify object, executes and responds to Spotify
                commands
            weather: A weather object, executes and responds to Weather
                commands
            helper: A helper which chooses which module to send commands to
            kernel: An AIML kernel which responds to some messages to Andy
            spoken: True if Andy should use text to speech, and False if
                print statements should be used
            current_music: If music is currently being played or used, then
                current_music is equal to corresponding music module object in
                Andy's attributes
       """

    def __init__(self, default_music=None, spoken=False):
        self.spotify = Spotify()
        self.weather = Weather()
        self.helper = Andy_Helper()
        self.kernel = aiml.Kernel()
        self.load_aiml()
        self.spoken = spoken
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
        if self.spoken:
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
            self.say(self.weather.route_command(command))
        else:
            self.say("Cannot understand command")

    def say(self, text):
        """'Says' given text, either through printing it or using
            speech-to-text."""
        if self.spoken:
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
