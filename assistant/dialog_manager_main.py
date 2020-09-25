#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author: Oriol Aranda

####################################
# ****** DIALOG MANAGER MAIN *******
####################################

import vlc
from utilities.utilities import record_mic, shave_accents, play_music, search, search_images, search_location, \
    play_story, find_story, eval_regex, found_contact, load_json, load_stories, load_riddles, load_jokes, \
    stories_selection
from speech_recognizer import SpeechRecognizer
from speech_synthesizer import SpeechSynthesizer
from answer_generator import AnswerGenerator
from intent_recognizer import IntentRecognizer
from speech_recognition import RequestError, UnknownValueError
from model import IDialogManagement
from googletrans import Translator
from utilities.prettyjson import prettyjson


def _traduir():
    translator = Translator()

    def traduir(text, src, dest):
        try:
            trans_text = translator.translate(text, src=src, dest=dest).text
        except BaseException:
            raise RequestError("Error al traducir")
        return trans_text

    return traduir


class DialogManagerMain(IDialogManagement):
    """
    Dialog  Manager module
    """

    def __init__(self, lang='es', user='default'):
        self.user = user
        self.profile = load_json(f'data/users/{user}/profile.json')
        self.state_transition_table = load_json('data/state_transition_table.json')
        self.stories = load_stories()
        self.riddles = load_riddles(self.profile['riddles']['read'])
        self.jokes = load_jokes(self.profile['jokes']['read'])
        self.actual_riddle = self.profile['riddles']['actual']
        self.contacts = self.profile['contacts_list']
        self.actual_alarm = self.profile['alarm']

        instance = vlc.Instance()  # define VLC instance
        self.player = instance.media_player_new()
        self.player.audio_set_volume(70)

        self.traduir = _traduir()
        self.lang = lang
        self.rec = SpeechRecognizer(lang=lang)
        self.syn = SpeechSynthesizer(lang=lang)
        eventos = [shave_accents(x) for _, el in self.profile['events']['info'].items() for x in el]
        info = {"carers": self.profile['carers'], "events": eventos}
        self.irec = IntentRecognizer(info, self.state_transition_table)
        stories_ = stories_selection(self.stories)
        self.resp = AnswerGenerator(self.profile, stories_, self.riddles, self.jokes)

    def start(self):
        """
        Main execution function, not api
        """
        if not self.profile['welcome']:
            frame = {'DOM': 'SETUP'}
            self.syn.speak("¡Hola!¡Voy a hacerte unas preguntas! Será un momento.")
            self.syn.speak("¿Cómo te llamas?")
            frame['DOM'] = 'PREG_NOMBRE'
        elif False:
            self.syn.speak(f"¡Hola {self.profile['name']}!, me gustaría preguntarte algo. Es urgente?")
            if True:
                frame = {'DOM': 'START_1'}
            else:
                frame = {'DOM': 'START_0'}
        else:
            frame = {'DOM': 'START'}
            self.syn.speak(f"¡Hola {self.profile['name']}!¿En qué puedo ayudarte?")
        while True:
            text = self.recognize()
            self.stop_player(frame)
            if self.lang == 'ca':
                text = self.traduir(text, src=self.lang, dest='es')
            intent = self.irec.get_intent(text, frame)
            if intent:
                self.get_new_domain(frame)
                self.answering(frame)
                if frame['DOM'] == 'START':
                    frame = {'DOM': frame['DOM']}
                else:
                    del frame['INT']

    def recognize(self):
        text = ""
        while True:
            voice = record_mic()
            try:
                text = self.rec.recognize(voice)
            except UnknownValueError:
                continue
            except RequestError:
                self.syn.speak("Lo siento, en estos momentos no puedo ayudarte. Prueba en un rato.")
            else:
                break
        print('Me:', text)
        return shave_accents(text)

    def answering(self, frame):
        answer_before = self.resp.get_answer(frame)
        dom_before = frame['DOM']
        if answer_before:
            if self.lang != 'es':
                answer_before = self.traduir(answer_before, src='es', dest=self.lang)

            self.syn.speak(answer_before)
        self.execute_task(frame)
        answer_next = self.resp.get_answer(frame)
        dom_next = frame['DOM']
        if answer_next and dom_next != dom_before:
            if self.lang != 'es':
                answer_next = self.traduir(answer_next, src='es', dest=self.lang)
            self.syn.speak(answer_next)

    def get_new_domain(self, frame):
        domain, intent = frame['DOM'], frame['INT']
        frame['DOM'] = self.state_transition_table[domain][intent]

    def execute_task(self, frame):
        """
        Execute function, slots semantic analysis and lambda transitions
        """
        # *** PRESENTACION ***

        if frame['DOM'] == 'PRESENTACION':
            self.profile['welcome'] = True
            self.profile['name'] = frame['nombre'].title()
            self.profile['surname'] = frame['apellido'].title()
            self.profile['age'] = frame['anyos']
            self.profile['gender'] = "male" if "hombre" == frame['sexo'] else "female"
            self.profile['gender_bot'] = "male" if "hombre" == frame['sexo_bot'] else "female"
            self.profile['senior_treatment'] = "tu" == frame['trato']
            self.profile['language_bot'] = "ca" if "catala" in frame['lengua'] else "es"
            print(self.profile)
            frame['DOM'] = 'START'

        # *** GENERALES ***

        if frame['DOM'] == 'ESTADO_SALUD_BIEN':
            frame['DOM'] = 'START'
        if frame['DOM'] == 'SALUDO':
            frame['DOM'] = 'START'
        if frame['DOM'] == 'COMO_LLAMAS':
            frame['DOM'] = 'START'
        if frame['DOM'] == 'COMO_ESTAS':
            frame['DOM'] = 'START'
        if frame['DOM'] == 'CUANTOS_ANYOS':
            frame['DOM'] = 'START'
        if frame['DOM'] == 'NADA':
            frame['DOM'] = 'START'
        if frame['DOM'] == 'NADA_EXIT':
            frame['DOM'] = 'EXIT'
        if frame['DOM'] == 'NO_RECUERDA':
            frame['DOM'] = 'START'
        if frame['DOM'] == 'NO_RECUERDA_EXIT':
            frame['DOM'] = 'EXIT'

        # *** BUSCAR ***

        if frame['DOM'] == 'BUSCAR':
            search(frame['texto'])
            frame['DOM'] = 'START'
        if frame['DOM'] == 'BUSCAR_IMAGEN':
            search_images(frame['imagenes'])
            frame['DOM'] = 'START'
        if frame['DOM'] == 'BUSCAR_LOC':
            search_location(frame['localizacion'])
            frame['DOM'] = 'START'

        # ***** ALARMA *****

        if frame['DOM'] == 'PREGUNTA_ALARMA':
            if self.profile['alarm']['activa']:
                pass
            elif not self.profile['alarm']['local']:
                if frame['INT'] == 'poner_alarma':
                    pass
                elif frame['INT'] == 'poner_alarma_0':
                    frame['DOM'] = 'PONER_ALARMA_0'
                else:
                    frame['DOM'] = 'PONER_ALARMA_1'
        if frame['DOM'] == 'PONER_ALARMA':
            frame['DOM'] = 'START'
        if frame['DOM'] == 'DESACTIVO_ALARMA':
            self.profile['alarm']['activa'] = False
            frame['DOM'] = 'START'
        if frame['DOM'] == 'ACTIVO_ALARMA':
            self.profile['alarm']['activa'] = True
            frame['DOM'] = 'START'
        if frame['DOM'] == 'ACTIVAR_ALARMA':
            if self.profile['alarm']['activa']:
                frame['DOM'] = 'START'
        if frame['DOM'] == 'DESACTIVAR_ALARMA':
            if not self.profile['alarm']['activa']:
                frame['DOM'] = 'START'

        # ***** LLAMAR *****

        if frame['DOM'] == 'LLAMAR':
            num_contacto = frame.get('num_contacto', False)
            if num_contacto:
                num = "".join(num_contacto.split())
                num_contacto = num[:3] + " " + num[3:6] + " " + num[6:9]
            name_contacto = frame.get('contacto', False)
            status_contacto = frame.get('status', False)
            tipo, filtered = found_contact(self.contacts, num_contacto, name_contacto, status_contacto)
            if len(filtered) == 1:
                if tipo == 'emergencia':
                    frame['llamar'] = True
                    frame['DOM'] = 'START'
                else:
                    frame['DOM'] = 'LLAMAR_SEGURO'
                frame['contacto'] = filtered[0]
                self.contacts = self.profile['contacts_list']
            elif len(filtered) > 1:
                frame['DOM'] = 'ESCOGER_CONTACTO'
                if tipo in ['hijo', 'hija', 'hermano', 'hermana', 'nieto', 'nieta']:
                    lista_contactos_posibles = ". ".join([f'{nom.split()[0]}' for nom, _, _, _ in filtered])
                else:
                    lista_contactos_posibles = ". ".join([f'{nom}' for nom, _, _, _ in filtered])
                self.contacts = filtered
                frame['lista_contactos'] = status_contacto, lista_contactos_posibles
            else:
                frame['DOM'] = 'NO_CONTACTO'
        if frame['DOM'] == 'NO_ENTENDER_CONTACTO':
            frame['DOM'] = 'LLAMAR_0'
        if frame['DOM'] == 'LLAMAR_DEF':
            frame['DOM'] = 'START'

        # **** RECORDAR PASTILLA ****

        if frame['DOM'] == 'RECORDAR_PASTILLA':
            frame['DOM'] = 'START'

        # **** CUENTO ****

        if frame['DOM'] == 'CONTINUAR_CUENTO':
            frame['cuento'] = 'actual'
            frame['DOM'] = 'CONTAR_CUENTO'
        if frame['DOM'] == 'CAMBIAR_CUENTO':
            time = max(0, self.player.get_time() - 5000)
            self.profile['books']['actual']['time'] = time
            self.player.stop()
            frame['DOM'] = 'CONTAR_CUENTO'
        if frame['DOM'] == 'CAMBIAR_CUENTO_0':
            time = max(0, self.player.get_time() - 5000)
            self.profile['books']['actual']['time'] = time
            self.player.stop()
            frame['DOM'] = 'LISTA_CUENTOS'
        if frame['DOM'] == 'CONTAR_CUENTO':
            exp = r'(actual|estaba(s|mos)? leyendo|otro dia|ultima vez|ayer|antes)( por favor| gracias)?$'
            cuento = frame.get('cuento', False)
            actual = not cuento or eval_regex(cuento, exp)  # m'esta demanant l'actual?
            cuento_actual = self.profile['books']['actual']['title']
            if actual and not cuento_actual:
                frame['DOM'] = 'NO_CUENTO'
            else:
                time = 0
                if actual:
                    frame['cuento'] = cuento_actual
                    time = self.profile['books']['actual']['time']
                title, story_link = find_story(self.stories, frame['cuento'])
                if story_link:
                    play_story(self.player, story_link, time)
                    self.profile['books']['actual']['title'] = title
                    frame['DOM'] = 'PLAY_STORY'
                else:
                    frame['DOM'] = 'NO_CUENTO'

        if frame['DOM'] == 'CONTAR_CUENTO_0':
            cuento_actual = self.profile['books']['actual']['title']
            if not cuento_actual:
                frame['DOM'] = 'LISTA_CUENTOS'
        elif frame['DOM'] == 'PLAY_STORY':
            self.player.play()
        elif frame['DOM'] == 'PAUSE_STORY':
            self.player.pause()
        elif frame['DOM'] == 'STOP_STORY':
            time = max(0, self.player.get_time() - 5000)
            self.profile['books']['actual']['time'] = time
            self.player.stop()
            frame['DOM'] = 'START'
        elif frame['DOM'] == 'BAJAR_VOL_STORY':
            vol = self.player.audio_get_volume()
            self.player.audio_set_volume(vol - 10)
        elif frame['DOM'] == 'SUBIR_VOL_STORY':
            vol = self.player.audio_get_volume()
            self.player.audio_set_volume(vol + 10)

        # **** CANCION ****

        if frame['DOM'] == 'ESC_CANCION':
            play_music(self.player, frame['cancion'])
            frame['DOM'] = 'PLAY_MUSIC'
        if frame['DOM'] == 'CAMBIAR_CANCION':
            self.player.stop()
            play_music(self.player, frame['cancion'])
            frame['DOM'] = 'PLAY_MUSIC'
        if frame['DOM'] == 'CAMBIAR_CANCION_0':
            self.player.stop()
            frame['DOM'] = 'ESC_CANCION_0'
        if frame['DOM'] == 'PLAY_MUSIC':
            self.player.play()
        elif frame['DOM'] == 'PAUSE_MUSIC':
            self.player.pause()
        elif frame['DOM'] == 'STOP_MUSIC':
            self.player.stop()
            frame['DOM'] = 'START'
        elif frame['DOM'] == 'BAJAR_VOL_MUSIC':
            vol = self.player.audio_get_volume()
            self.player.audio_set_volume(vol - 10)
        elif frame['DOM'] == 'SUBIR_VOL_MUSIC':
            vol = self.player.audio_get_volume()
            self.player.audio_set_volume(vol + 10)

        # ***** ADIVINANZA *****

        if frame['DOM'] == 'CONTAR_ADIVINANZA_0':
            if self.actual_riddle < 0:
                frame['DOM'] = 'RESOLVER_ADIVINANZA'
            else:
                frame['DOM'] = 'EXISTE_ADIVINANZA'
        if frame['DOM'] == 'REPETIR_ADIVINANZA':
            frame['DOM'] = 'RESOLVER_ADIVINANZA'
        if frame['DOM'] == 'CONTAR_ADIVINANZA_NUEVA':
            frame['DOM'] = 'RESOLVER_ADIVINANZA'
        if frame['DOM'] == 'CONTINUAR_ADIVINANZA':
            frame['DOM'] = 'RESOLVER_ADIVINANZA'
        if frame['DOM'] == 'EVALUAR_RESPUESTA':
            frame['DOM'] = 'RESOLVER_ADIVINANZA'
            frame['solucion'] = True
            respuestas = self.riddles[self.profile['riddles']['actual']][1].split(' / ')
            for res in respuestas:
                if frame['respuesta'] in shave_accents(res.lower()):
                    frame['DOM'] = 'OTRA_ADIVINANZA'
                    break
        if frame['DOM'] == 'OTRA_ADIVINANZA':
            self.profile['riddles']['read'].append(self.profile['riddles']['actual'])
        if frame['DOM'] == 'SOLUCION_BUENA':
            self.profile['riddles']['read'].append(self.profile['riddles']['actual'])
            self.profile['riddles']['actual'] = -1
            frame['DOM'] = 'OTRA_ADIVINANZA'
        if frame['DOM'] == 'AYUDA_ADIVINANZA':
            frame['DOM'] = 'RESOLVER_ADIVINANZA'
        if frame['DOM'] == 'SEGUIR_PROBANDO':
            frame['DOM'] = 'RESOLVER_ADIVINANZA'
        if frame['DOM'] == 'FINALIZAR_ADIVINANZA':
            self.actual_riddle = self.profile['riddles']['actual']
            frame['DOM'] = 'START'

        # **** CHISTES ****

        if frame['DOM'] == 'CONTAR_CHISTE':
            frame['DOM'] = 'MAS_CHISTES'
        if frame['DOM'] == 'REPETIR_CHISTE':
            frame['DOM'] = 'MAS_CHISTES'

        # ***** JUEGO *****

        if frame['DOM'] == 'JUGAR':
            frame['DOM'] = 'RESOLVER_NIVEL'
        if frame['DOM'] == 'SIGUIENTE_NIVEL':
            frame['DOM'] = 'RESOLVER_NIVEL'
        if frame['DOM'] == 'REPETIR_NIVEL':
            frame['DOM'] = 'RESOLVER_NIVEL'
        if frame['DOM'] == 'FINALIZAR_JUEGO_DEF':
            frame['DOM'] = 'START'

        # ***** DIARIA *****

        if frame['DOM'] == 'DIA':
            frame['DOM'] = 'START'
        if frame['DOM'] == 'HORA':
            frame['DOM'] = 'START'
        if frame['DOM'] == 'TIEMPO':
            frame['DOM'] = 'START'

        # ***** CUIDADOR *****

        if frame['DOM'] == 'NOMBRE_CUIDADOR':
            frame['DOM'] = 'START'
        if frame['DOM'] == 'DIA_CUIDADOR':
            frame['DOM'] = 'START'
        if frame['DOM'] == 'HORA_CUIDADOR':
            frame['DOM'] = 'START'

        # ***** EVENTO ******
        if frame['DOM'] == 'FECHA_EVENTO':
            frame['DOM'] = 'START'

        # *** END ***
        if frame['DOM'] == 'GRACIAS':
            frame['DOM'] = 'START'
        if frame['DOM'] == 'EXIT':
            self.save_profile()
            exit()

    def save_profile(self):
        """
        Save profile in json format
        """
        with open(f'data/users/{self.user}/profile.json', 'w') as fp:
            txt = prettyjson(self.profile, indent=4, maxlinelength=80)
            fp.write(txt)

    def stop_player(self, frame):
        """
        Function reliable in main execution. Ignore on API
        """
        if self.player.get_position() > 0.990:
            self.player.stop()
            frame['DOM'] = 'START'

    # *** IGNORE (API) ***
    def get_response_audio(self, frame: dict, audio) -> (dict,):
        return None, None

    def get_response_text(self, frame: dict, text: str) -> (dict, str):
        return None, None
