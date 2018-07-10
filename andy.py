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
import pyttsx3
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
from spotify.spotify import Spotify
from weather.weather import Weather
from andy_calendar.andy_calendar import Calendar
from speech_to_text.speech_to_text import AndySpeechToText
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
        if self.user_spoken:
            self.stt = AndySpeechToText()
        if self.andy_spoken:
            self.speech_engine = pyttsx3.init()
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

    def text_input(self):
        user_input = input("> ")
        return user_input

    def prompt(self):
        """Prompts the user for input to Andy"""
        if self.user_spoken:
            command = self.stt.record_and_convert()
            if command is None:
                command = ""
            self.route_command(command.lower())
        else:
            command = self.text_input()
            self.route_command(command.lower())

    def route_command(self, command):
        """Sends a user command to the corresponding module where it will be
            executed."""
        labels = self.helper.classify_command(command)
        # set the function that will record user input for the other modules
        if self.user_spoken:
            listen = self.stt.record_and_convert
        else:
            listen = self.text_input
        if "music" in labels:
            if self.current_music is not None:
                try:
                    result = self.current_music.route_command(
                        command,
                        self.say,
                        listen
                    )
                    if result:
                        return
                except spotipy.client.SpotifyException:
                    self.say("Error executing Spotify command")
                    return
            else:
                self.say("No music currently selected.")
                return
        if "weather" in labels:
            try:
                result = self.weather.route_command(
                    command,
                    self.say,
                    listen
                )
                if result:
                    return
            except pyowm.exceptions.api_call_error.APICallError:
                self.say("An error occurred while connecting to Open Weather \
                Map")
                return
        if "calendar" in labels:
            try:
                result = self.calendar.route_command(
                    command,
                    self.say,
                    listen
                )
                if result:
                    return
            except googleapiclient.errors.HttpError:
                self.say("An error occurred while connecting to Google \
                Calendar")
                return
        self.say("Cannot understand command")

    def say(self, text):
        """Says given text, either through printing it or using
            speech-to-text."""
        if self.andy_spoken:
            self.speech_engine.say(text)
            self.speech_engine.runAndWait()
            print(text)
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
