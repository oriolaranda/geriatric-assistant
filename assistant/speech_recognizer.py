#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author: Oriol Aranda

##################################
# ****** SPEECH RECOGNIZER *******
##################################

from model import ISpeechToText
import speech_recognition as sr


def decorator(f, lang):
    def inner(audio):
        text = f(audio, language=lang)
        return text
    return inner


class SpeechRecognizer(ISpeechToText):
    """ Speech to text module

        :param model arguments: 'google', 'cmu_sphinx'
        :param lang arguments: 'en', 'es-es', 'ca'
        :return audio
    """

    def __init__(self, model='google', lang='es'):

        if model not in ['google', 'sphinx']:
            raise ValueError('invalid argument for model')
        if lang not in ['en', 'es', 'ca']:
            raise ValueError('invalid argument for lang')
        if model == 'google':
            self._recognize = decorator(sr.Recognizer().recognize_google, lang)
        elif model == 'sphinx':
            lang += '-US' if lang == 'en' else '-ES'
            print(lang)
            self._recognize = decorator(sr.Recognizer().recognize_sphinx, lang)

    def recognize(self, audio):
        try:
            text = self._recognize(audio)
        except sr.UnknownValueError:
            raise
        except sr.RequestError:
            raise
        else:
            return text.lower()
