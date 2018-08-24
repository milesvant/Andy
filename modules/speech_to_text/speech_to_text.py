# Copyright 2017 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
from sys import byteorder
from array import array
from struct import pack
from google.cloud import speech
from tensorflow.contrib.framework.python.ops import audio_ops as contrib_audio

import tensorflow as tf
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

        Methods load_graph, load_labels, and run_graph are adapted from
        tensorflow examples, Apache license provided above.

       Attributes:
            THRESHOLD: The volume threshold to be considered silent vs. not
            CHUNK_SIZE: The number of samples in each chunk
            FORMAT: The number of bits in the recording samples
            RATE: The sampling rate of the microphone
            client: A google speech to text API client
            config: The configuration object for the google speech to text API
                client
            labels_list: a list of the labels used in the trained tensorflow
                model
    """

    def __init__(self):
        self.THRESHOLD = 500
        self.CHUNK_SIZE = 1024
        self.FORMAT = pyaudio.paInt16
        self.RATE = 16000
        self.client = speech.SpeechClient()
        self.config = speech.types.RecognitionConfig(
            encoding='LINEAR16',
            language_code='en-US',
            sample_rate_hertz=self.RATE,
        )
        current_dir = os.path.abspath(os.path.dirname(__file__))
        self.labels_list = self.load_labels(
            "{}/conv_labels.txt".format(current_dir))
        # load graph, which is stored in the default session
        self.load_graph("{}/frozen_graph.pb".format(current_dir))

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

    def record_after_wake_word(self):
        """Records a command to the file <current time>.wav, without waiting
            for user input. Returns the filename (without the .wav suffix)"""
        now = datetime.datetime.utcnow()
        current_dir = os.path.abspath(os.path.dirname(__file__))
        filepath = "{}/files/{}.wav".format(current_dir, str(now))
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

    def record_and_convert(self, after_wake_word=False):
        """Packages together the recording and conversion to text methods"""
        if after_wake_word:
            filename = self.record_after_wake_word()
        else:
            filename = self.record_for_andy()
        text = self.convert_to_text(filename)
        print(text)
        os.remove(filename)
        return text

    def load_graph(self, filename):
        """Unpersists graph from file as default graph."""
        with tf.gfile.FastGFile(filename, 'rb') as f:
            graph_def = tf.GraphDef()
            graph_def.ParseFromString(f.read())
            tf.import_graph_def(graph_def, name='')

    def load_labels(self, filename):
        """Read in labels, one label per line."""
        return [line.rstrip() for line in tf.gfile.GFile(filename)]

    def run_graph(self, wav_data, labels, input_layer_name, output_layer_name,
                  num_top_predictions):
        """Runs the audio data through the graph and prints predictions."""
        with tf.Session() as sess:
            # Feed the audio data as input to the graph.
            #   predictions  will contain a two-dimensional array, where one
            #   dimension represents the input image count, and the other has
            #   predictions per class
            softmax_tensor = sess.graph.get_tensor_by_name(output_layer_name)
            predictions, = sess.run(softmax_tensor,
                                    {input_layer_name: wav_data})

            # Sort to show labels in order of confidence
            top_k = predictions.argsort()[-num_top_predictions:][::-1]
            scores = {}
            for node_id in top_k:
                human_string = labels[node_id]
                score = predictions[node_id]
                scores[human_string] = score
            return scores

    def label_wav(self, wav):
        """Loads the model and labels, and runs the inference to print
            predictions."""
        with open(wav, 'rb') as wav_file:
            wav_data = wav_file.read()
        return self.run_graph(wav_data,
                              self.labels_list,
                              'wav_data:0',
                              'labels_softmax:0', 3)

    def is_wake_word(self, scores):
        """True if the scores dictionary says the probability that file was of
            the word 'marvin' is greater than 90%, and False otherwise."""
        return (scores['marvin'] > 0.90)

    def detect_wake_word(self):
        """Loops until the word 'marvin' is detected, then returns."""
        done = False
        while not done:
            now = datetime.datetime.utcnow()
            current_dir = os.path.abspath(os.path.dirname(__file__))
            filepath = "{}/files/{}.wav".format(current_dir, str(now))
            self.record_to_file(filepath)
            done = self.is_wake_word(self.label_wav(filepath))
            os.remove(filepath)
        self.play_notification_sound()
        return

    def play_notification_sound(self):
        current_dir = os.path.abspath(os.path.dirname(__file__))

        f = wave.open("{}/files/notification.wav".format(current_dir), "rb")
        p = pyaudio.PyAudio()
        stream = p.open(format=p.get_format_from_width(f.getsampwidth()),
                        channels=f.getnchannels(),
                        rate=f.getframerate(),
                        output=True)
        data = f.readframes(self.CHUNK_SIZE)
        while data:
            stream.write(data)
            data = f.readframes(self.CHUNK_SIZE)
        stream.stop_stream()
        stream.close()
        p.terminate()
