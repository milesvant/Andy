from sys import byteorder
from array import array
from struct import pack
from google.cloud import speech

import pyaudio
import wave
import datetime
import os
import io


class AndySpeechToText:
    """Class which records commands and uses Google's API to perform the
            speech to text functionality for Andy.

        Methods in between is_silent and record_to_file are adapted from this
        Stack Overflow answer:
        https://stackoverflow.com/questions/892199/detect-record-audio-in-python
        courtesy of the user cryo

       Attributes:
            THRESHOLD: The volume threshold to be considered silent vs. not
            CHUNK_SIZE: The number of samples in each chunk
            FORMAT: The number of bits in the recording samples
            RATE: The sampling rate of the microphone
            client: A google speech to text API client
            config: The configuration object for the google speech to text API
                client
    """

    def __init__(self):
        self.THRESHOLD = 500
        self.CHUNK_SIZE = 1024
        self.FORMAT = pyaudio.paInt16
        self.RATE = 44100
        self.client = speech.SpeechClient()
        self.config = speech.types.RecognitionConfig(
            encoding='LINEAR16',
            language_code='en-US',
            sample_rate_hertz=self.RATE,
        )

    def is_silent(self, snd_data):
        "Returns 'True' if below the 'silent' self.THRESHOLD"
        return max(snd_data) < self.THRESHOLD

    def normalize(self, snd_data):
        "Average the volume out"
        MAXIMUM = 16384
        times = float(MAXIMUM)/max(abs(i) for i in snd_data)

        r = array('h')
        for i in snd_data:
            r.append(int(i*times))
        return r

    def trim(self, snd_data):
        "Trim the blank spots at the start and end"
        def _trim(snd_data):
            snd_started = False
            r = array('h')

            for i in snd_data:
                if not snd_started and abs(i) > self.THRESHOLD:
                    snd_started = True
                    r.append(i)

                elif snd_started:
                    r.append(i)
            return r

        # Trim to the left
        snd_data = _trim(snd_data)

        # Trim to the right
        snd_data.reverse()
        snd_data = _trim(snd_data)
        snd_data.reverse()
        return snd_data

    def add_silence(self, snd_data, seconds):
        "Add silence to the start and end of 'snd_data' of length 'seconds'\
            (float)"
        r = array('h', [0 for i in range(int(seconds*self.RATE))])
        r.extend(snd_data)
        r.extend([0 for i in range(int(seconds*self.RATE))])
        return r

    def record(self):
        """
        Record a word or words from the microphone and
        return the data as an array of signed shorts.

        Normalizes the audio, trims silence from the
        start and end, and pads with 0.5 seconds of
        blank sound to make sure VLC et al can play
        it without getting chopped off.
        """
        p = pyaudio.PyAudio()
        stream = p.open(format=self.FORMAT, channels=1, rate=self.RATE,
                        input=True, output=True,
                        frames_per_buffer=self.CHUNK_SIZE)

        num_silent = 0
        snd_started = False

        r = array('h')

        while 1:
            # little endian, signed short
            snd_data = array('h', stream.read(self.CHUNK_SIZE,
                                              exception_on_overflow=False),)
            if byteorder == 'big':
                snd_data.byteswap()
            r.extend(snd_data)

            silent = self.is_silent(snd_data)

            if silent and snd_started:
                num_silent += 1
            elif not silent and not snd_started:
                snd_started = True

            if snd_started and num_silent > 30:
                break

        sample_width = p.get_sample_size(self.FORMAT)
        stream.stop_stream()
        stream.close()
        p.terminate()

        r = self.normalize(r)
        r = self.trim(r)
        r = self.add_silence(r, 0.5)
        return sample_width, r

    def record_to_file(self, path):
        "Records from the microphone and outputs the resulting data to 'path'"
        sample_width, data = self.record()
        data = pack('<' + ('h'*len(data)), *data)

        wf = wave.open(path, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(sample_width)
        wf.setframerate(self.RATE)
        wf.writeframes(data)
        wf.close()

    def record_for_andy(self):
        """Upon user input, records a command to the file <current time>.wav,
            then returns the filename"""
        now = datetime.datetime.utcnow()
        current_dir = os.path.abspath(os.path.dirname(__file__))
        filepath = "{}/files/{}.wav".format(current_dir, str(now))
        input("> ")
        self.record_to_file(filepath)
        return filepath

    def convert_to_text(self, filename):
        """Sends the audio file to the google API and returns the text
            transcript received"""
        with io.open(filename, 'rb') as stream:
            requests = [speech.types.StreamingRecognizeRequest(
                audio_content=stream.read(),
            )]
        streaming_config = speech.types.StreamingRecognitionConfig(
            config=self.config,
        )
        results = self.client.streaming_recognize(
            streaming_config,
            requests,
        )
        for result in results:
            return result.results[0].alternatives[0].transcript

    def record_and_convert(self):
        """Packages together the recording and conversion to text methods"""
        filename = self.record_for_andy()
        text = self.convert_to_text(filename)
        os.remove(filename)
        return text
