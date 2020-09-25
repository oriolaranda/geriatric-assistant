#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author: Oriol Aranda

import sys
sys.path.append('../assistant')

import json
import speech_recognition as sr
import io
from flask import Flask, render_template, request, make_response, Response
from dialog_manager import DialogManager
from pydub import AudioSegment
from json import loads
from requests_toolbelt import MultipartEncoder

app = Flask(__name__)


@app.route('/')
def home():
    return render_template("userview.html")


@app.route('/s2t', methods=['POST'])
def spech_to_text():
    req_audio_blob = request.files['audio'].read()
    req_data = loads(request.form['info'])
    frame = req_data['frame']
    lang = req_data['lang']
    user = req_data['user']

    audio_segment = AudioSegment.from_ogg(io.BytesIO(req_audio_blob))
    audio_file = "../assistant/audios/output.wav"  # fitxer on es guarda l'audio de l'usuari
    file_handle = audio_segment.export(audio_file, format="wav")
    # audio_file = io.BytesIO()
    # AudioFile(fileobject) fileobject ha d'estar en format WAV/AIFF/FLAC
    # audio_file = audio_segment.export(audio_file, format="wav")
    # audio_wav = AudioSegment.from_wav(audio_file)
    # audio = sr.AudioData(audio_wav, audio_segment.frame_rate, audio_segment.sample_width)
    # sr.AudioFile(audio_file) no funciona, tq audio_file = io.BytesIO() en format wav... ????

    r = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio = r.record(source)  # format sr.AudioData

    dialog = DialogManager(lang=lang, user=user)  # instanciem el DialogManager
    new_frame, text_answer, audio_answer = dialog.get_response_audio(frame, audio)
    # audio answer format mp3, using AudioSegment export to another format
    response = MultipartEncoder(
        fields={
            'new_frame': json.dumps(new_frame),
            'text_answer': text_answer,
            'audio_answer': ('filename', audio_answer, 'audio/mp3')}
    )
    return Response(response.to_string(), mimetype=response.content_type)


@app.route('/assistant_text', methods=['POST'])
def assistant_text():
    req_data = request.get_json()  # obtenim els parametres que ens han enviat a la request
    text = req_data['input_text']
    frame = req_data['frame']
    lang = req_data['lang']
    user = req_data['user']

    dialog = DialogManager(lang=lang, user=user)  # instanciem el DialogManager
    new_frame, answer = dialog.get_response_text(frame, text)  # obtenim el nou estat (frame) i la resposta en text
    response = {  # preparem response
        "new_frame": new_frame,
        "text_answer": answer
    }
    return make_response(response)


@app.route('/assistant_audio', methods=['POST'])
def assistant_audio():
    # TODO: Endpoint audio
    pass


if __name__ == '__main__':
    app.run(debug=True)
