import spotipy
import spotipy.util as util
import os
import yaml
from time import sleep
from .spotify_helper import Spotify_Helper


class Spotify:
    """Wrapper around a spotipy.Spotify object which can log in a user as well
        as translate and execute user commands.

        Attributes:
            _spotify: a spotipy.Spotify object
            helper: a Spotify_Helper object which helps process user commands
            auth: True if a user is logged in, and False otherwise
    """

    def __init__(self):
        self._spotify = spotipy.Spotify()
        self.helper = Spotify_Helper()
        self.auth = False

    def login(self, username):
        """Logs in username to Spotify."""
        scope = "user-modify-playback-state \
        user-read-currently-playing \
        user-read-playback-state"
        CREDENTIALS_FILE = "{}/spotify-credentials.yaml".format(
            os.path.abspath(os.path.dirname(__file__))
        )
        if os.path.exists(CREDENTIALS_FILE):
            with open(CREDENTIALS_FILE) as cf:
                credentials = yaml.load(cf)
                client_id = credentials['CLIENT_ID']
                client_secret = credentials['CLIENT_SECRET']
                redirect_url = credentials['REDIRECT_URL']
        else:
            client_id = os.environ.get('SPOTIFY_CLIENT_ID')
            client_secret = os.environ.get('SPOTIFY_CLIENT_SECRET')
            redirect_url = os.environ.get('SPOTIFY_REDIRECT_URL')
        token = util.prompt_for_user_token(
            username, scope,
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_url)
        if token:
            self._spotify = spotipy.Spotify(auth=token)
            self.auth = True
        else:
            raise ValueError("Could not connect to Spotify at this time.")

    def need_auth(fun):
        def wrapped_fun(self, *args, **kwargs):
            if self.auth:
                fun(self, *args, **kwargs)
            else:
                raise ValueError("Not logged in to Spotify.")
        return wrapped_fun

    @need_auth
    def resume_playback(self):
        self._spotify.start_playback()

    @need_auth
    def pause_playback(self):
        self._spotify.pause_playback()

    @need_auth
    def next_playback(self):
        self._spotify.next_track()

    @need_auth
    def previous_playback(self):
        self._spotify.previous_track()

    @need_auth
    def search_and_play(self, query):
        """Searches for a query on Spotify and plays the top result"""
        results = []
        for result in self._spotify.search(query,
                                           type="track",
                                           limit=1)['tracks']['items']:
            results.append(result['uri'])
        if results is not []:
            self._spotify.start_playback(uris=results)
        else:
            raise ValueError("No Spotify results for this search query.")

    @need_auth
    def play_song(self, uri):
        pass

    def route_command(self, command, say):
        """Executes and generates  a string response for a given spotify
            command.

            Args:
                command: a string command which requests some action or
                    information related to Spotify.
                say: A function which will say (either through text to speech
                    or printing) a string in the main speaker loop
            Returns:
                True if a command was executed (or failed while executed) and
                    false if the command was invalid.
        """
        label, query = self.helper.parse_command(command)
        if label == "resume":
            say("Resuming Spotify")
            self.resume_playback()
        elif label == "pause":
            say("Pausing Spotify")
            self.pause_playback()
        elif label == "previous":
            say("Playing previous song")
            self.previous_playback()
        elif label == "next":
            say("Playing next song")
            self.next_playback()
        elif label == "search":
            try:
                self.search_and_play(query)
                # Need to sleep for a moment for the currently playing data
                # to update
                sleep(0.5)
                track_info = self._spotify.currently_playing()['item']
                say("Playing {} by {}".format(
                    track_info['name'],
                    track_info['artists'][0]['name']
                ))
            except ValueError:
                say("No search results for that query on Spotify")
            except TypeError:
                say("An error occurred while searching for that query on \
Spotify")
        elif label == "current":
            if self.auth:
                track_info = self._spotify.currently_playing()['item']
                return "The currently playing song is {} by {}".format(
                    track_info['name'],
                    track_info['artists'][0]['name']
                )
            else:
                say("Not logged into Spotify")
        else:
            return False
        return True
