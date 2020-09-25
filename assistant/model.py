#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Oriol Aranda

######################################
# ************ MODEL ****************
######################################

"""
Module implementing all the Interfaces and objects for the chatbot

- XatbotModule Interface
- Speech To Text Interface
- Intent Recognition Interface
- Dialog Management Interface
- Answers Generation Interface
- Text To Speech Interface

"""

from abc import ABC, abstractmethod
from speech_recognition import AudioData
from io import BytesIO


class IXatbotModule(ABC):
    """
    Interface for XatbotModule.
    The app is designed for being as much generic as possible: an undefined number of modules that can be replicated,
    different sub modules with specific type of tasks and implemented as required.
    """


class ISpeechToText(IXatbotModule):
    """
    Interface for Speech To Text module
    """

    @abstractmethod
    def recognize(self, audio: AudioData) -> str:
        """
        Function to recognize the text from the input audio

        :param audio: Input audio from user
        :return text: Text recognized from audio
        """
        pass


class IIntentRecognition(IXatbotModule):
    """
    Interface for Intent Recognition Module
    """

    @abstractmethod
    def get_intent(self, text: str, frame: dict) -> bool:
        """
        Function to recognize the intent from the input text and attached to the actual frame.
        :param frame: Representation of the domain/state
        :param text: Input recognized text
        :return bool: true if has recognized any intent, false otherwise
        """
        pass


class IDialogManagement(IXatbotModule):
    """
        Interface for Dialog Management Module
    """

    @abstractmethod
    def start(self) -> None:
        """
        Function to start the dialog with the assistant as a native app using the system microphone.
        :return: None
        """
        pass

    @abstractmethod
    def get_response_text(self, frame: dict, text: str) -> (dict, str):
        """
        Function to get the response for a certain domain/estate of the dialog and an input text. Used for the API,
        response returned in text format.
        :param frame: Representation of the domain/estate
        :param text: Input user text
        :return: Frame and text response
        """
        pass

    @abstractmethod
    def get_response_audio(self, frame: dict, audio: AudioData) -> (dict, BytesIO):
        """
        Function to get the response for certain domain/estate of the dialog and an input audio. Used for the API,
        response returned in audio format.
        :param frame: Representation of the domain/estate
        :param audio: Input user audio
        :return: Frame and audio response (BytesIO object file in mp3 format)
        """
        pass


class IAnswerGenerator(IXatbotModule):
    """
    Interface for Answer Generator Module
    """

    @abstractmethod
    def get_answer(self, frame: dict) -> str:
        """
        Function to return the answer for a certain domain/estate of the dialog
        :param frame: Representation of the domain/estate
        :return str: Response text
        """
        pass


class ITextToSpeech(IXatbotModule):
    """
        Interface for Text To Speech Module
    """

    @abstractmethod
    def speak(self, text: str) -> None:
        """
        Function to reproduce the audio directly
        :param text: Text to synthesize
        :return: None
        """
        pass

    @abstractmethod
    def synthesize(self, text: str) -> BytesIO:
        """
        Function to return the text synthesized
        :param text: Text to synthesize
        :return: audio synthesized (BytesIO object file in mp3 format)
        """
        pass
