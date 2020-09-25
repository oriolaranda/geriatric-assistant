#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author: Oriol Aranda

###################################
# ****** SPEECH SYNTHESIZER *******
###################################

import os
from io import BytesIO
from model import ITextToSpeech
from gtts import gTTS, gTTSError
from random import randint
from playsound import playsound


def decorator(lang):
    def _synth(text: str):
        try:
            tts = gTTS(text=text, lang=lang, slow=False)
        except gTTSError:
            raise
        return tts
    return _synth


class SpeechSynthesizer(ITextToSpeech):
    """
    Text to Speech module
    """

    def __init__(self, lang='es'):
        if lang not in ['en', 'es', 'ca']:
            raise ValueError('invalid argument for lang')
        if lang == 'es':
            lang = 'es-es'
        self.synth = decorator(lang)

    def speak(self, text):
        print("Bot: ", text)
        audio = self.synth(text)
        ran = randint(1, 10000000)
        audio_file = 'audio-' + str(ran) + '.mp3'
        audio.save('./audios/'+audio_file)
        playsound('./audios/' + audio_file)
        os.remove('./audios/'+audio_file)

    def synthesize(self, text):
        audio = self.synth(text)
        mp3_fp = BytesIO()
        audio.write_to_fp(mp3_fp)  # mp3 is the default format
        return mp3_fp
