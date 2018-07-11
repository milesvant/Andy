import spotipy
import spotipy.util as util
import os
import yaml
from time import sleep
from .spotify_helper import SpotifyHelper


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
        self.helper = SpotifyHelper()
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
            self.volume = 100
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

    @need_auth
    def list_playlists(self, say, listen):
        """Allows a user to view a list of their most popular playlists.

           Args:
                say: A function which will say (either through text to speech
                    or printing) a string in the main speaker loop
                listen: A function which will listen and record user input
                    through either speech to text or through the CLI
        """
        index = 1
        playlist_by_index = {}
        # make global dictionaries of playlist uri's for later lookup,
        # as well as a local dicitonary of indices to playlist names for
        # display purposes
        self.playlist_uri_by_index = {}
        self.playlist_uri_by_name = {}
        for playlist in self._spotify.current_user_playlists()['items']:
            playlist_by_index[index] = playlist['name']
            self.playlist_uri_by_index[index] = playlist['uri']
            self.playlist_uri_by_name[
                playlist['name']
            ] = playlist['uri']
            index += 1
        num_playlists = index
        current_username = self._spotify.current_user()['id']
        say("{}'s playlists:".format(current_username))
        index = 1
        current_end = 5
        stop = False
        while not stop:
            # Print playlists in increments of five until you've run out of
            # playlists or the user requests a stop
            while index <= current_end and index < num_playlists:
                say("{}: {}".format(index, playlist_by_index[index]))
                index += 1
            current_end += 5
            if index == num_playlists:
                stop = True
            else:
                say("Continue listing? ")
                stop = (listen().lower() not in self.helper.positive_words)

    @need_auth
    def play_playlist(self, say, query):
        """Plays a playlist by name or index"""
        try:
            query = int(query)
            playlist_uri = self.playlist_uri_by_index[query]
        except ValueError:
            playlist_uri = self.playlist_uri_by_name[query]
        say("Playing playlist {}".format(query))
        self._spotify.start_playback(context_uri=playlist_uri)

    @need_auth
    def volume_up(self):
        if self.volume != 100:
            self.volume += 20
            self._spotify.volume(self.volume)

    @need_auth
    def volume_down(self):
        if self.volume != 0:
            self.volume -= 20
            self._spotify.volume(self.volume)

    def route_command(self, command, say, listen):
        """Executes and generates  a string response for a given spotify
            command.

            Args:
                command: a string command which requests some action or
                    information related to Spotify.
                say: A function which will say (either through text to speech
                    or printing) a string in the main speaker loop
                listen: A function which will listen and record user input
                    through either speech to text or through the CLI
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
                say("The currently playing song is {} by {}".format(
                    track_info['name'],
                    track_info['artists'][0]['name']
                ))
            else:
                say("Not logged into Spotify")
        elif label == "list playlist":
            self.list_playlists(say, listen)
        elif label == "play playlist":
            self.play_playlist(say, query)
        elif label == "volume up":
            self.volume_up()
            say("Turning the volume up to {}".format(self.volume))
        elif label == "volume down":
            self.volume_down()
            say("Turning the volume down to {}".format(self.volume))
        else:
            return False
        return True
