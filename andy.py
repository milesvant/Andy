import aiml
import os
import glob
import yaml
import re
import spotipy
from spotify.spotify import Spotify
from weather.weather import Weather


class Andy:
    """
    """

    def __init__(self, default_music=None, spoken=False):
        self.spotify = Spotify()
        self.weather = Weather()
        self.kernel = aiml.Kernel()
        self.load_aiml()
        self.spoken = spoken
        if default_music is None:
            self.current_music = None
        else:
            if default_music == "spotify":
                self.current_music = self.spotify
        self.andy_commands = {"music": ["pause", "resume", "play", "stop",
                                        "play previous", "previous",
                                        "play previous song", "previous song",
                                        "skip", "next", "next song",
                                        "play next song"],
                              "weather": ["weather", ], }

    def load_aiml(self):
        # load each file in the aiml/ folder into the AIML interpreter
        for file in glob.glob('{}/aiml/*.xml'.format(
                os.path.abspath(os.path.dirname(__name__)))):
            self.kernel.learn(file)

    def prompt(self):
        if self.spoken:
            pass
        else:
            user_input = input("> ")
            self.respond(user_input)
            self.route_command(user_input.lower())

    def route_command(self, command):
        if 'spotify' in command:
            try:
                self.spotify.route_command(command)
                self.current_music = self.spotify
            except spotipy.client.SpotifyException:
                self.say("Error executing Spotify command")
        elif command in self.andy_commands['music']:
            if self.current_music is not None:
                try:
                    self.current_music.route_command(command)
                except spotipy.client.SpotifyException:
                    self.say("Error executing Spotify command")
            else:
                raise ValueError("No music currently selected.")
        elif 'weather' in command:
            self.say(self.weather.route_command(command))
        else:
            pass

    def respond(self, response):
        if self.spoken:
            pass
        else:
            print(self.kernel.respond(response))

    def say(self, text):
        if self.spoken:
            pass
        else:
            print(text)

    def loop(self):
        while True:
            self.prompt()
