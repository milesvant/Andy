import spotipy
import spotipy.util as util
import os
import yaml


class Spotify:
    """
    """

    def __init__(self):
        self._spotify = spotipy.Spotify()
        self.auth = False

    def login(self, username, scope="user-modify-playback-state"):
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
        def wrapped_fun(self):
            if self.auth:
                fun(self)
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

    def route_command(self, command):
        if command == "resume spotify" \
                or command == "play spotify" \
                or command == "resume" \
                or command == "play":
            self.resume_playback()
        elif command == "pause spotify" \
                or command == "stop spotify" \
                or command == "pause":
            self.pause_playback()
        elif command == "play previous" \
                or command == "previous" \
                or command == "play previous song" \
                or command == "previous song":
            self.previous_playback()
        elif command == "skip" \
                or command == "next" \
                or command == "next song" \
                or command == "play next song":
            self.next_playback()
        else:
            pass
