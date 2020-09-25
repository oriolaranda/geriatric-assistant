#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author: Oriol Aranda

###############################
# ****** DIALOG MANAGER *******
###############################

import random
from io import BytesIO
from utilities.utilities import shave_accents, search, search_images, search_location, \
    find_story, eval_regex, found_contact, load_json, load_stories, load_riddles, load_jokes, \
    stories_selection, play_youtube_music, play_youtube_story, intent_info, translation
from speech_recognition import UnknownValueError, RequestError
from speech_recognizer import SpeechRecognizer
from speech_synthesizer import SpeechSynthesizer
from answer_generator import AnswerGenerator
from intent_recognizer import IntentRecognizer
from model import IDialogManagement
from utilities.prettyjson import prettyjson


class DialogManager(IDialogManagement):
    """
    Dialog  Manager module
    """

    def __init__(self, lang='es', user='default'):
        # *** INIT ATTRIBUTES ***
        self.user = user
        self.profile = load_json(f'../assistant/data/users/{user}/profile.json')
        self.state_transition_table = load_json('../assistant/data/state_transition_table.json')
        self.stories = load_stories()
        self.riddles = load_riddles(self.profile['riddles']['read'])
        self.jokes = load_jokes(self.profile['jokes']['read'])
        self.actual_riddle = self.profile['riddles']['actual']
        self.contacts = self.profile['contacts_list']
        self.actual_alarm = self.profile['alarm']
        self.google_translate = translation()
        self.lang = lang

        # *** INIT MODULES ***
        self.rec = SpeechRecognizer(lang=lang)
        self.syn = SpeechSynthesizer(lang=lang)
        self.irec = IntentRecognizer(intent_info(self.profile), self.state_transition_table)
        self.resp = AnswerGenerator(self.profile, stories_selection(self.stories), self.riddles, self.jokes)

    def get_response_text(self, frame, text):
        """
        API get_response in text format
        :return: new frame (dict) and text response (str)
        """
        response = self.welcome_response(frame)
        if response:
            return response  # Start conversation but the assistant has the iniciative
        if text:
            if self.lang != 'es':
                text = self.google_translate(text, src=self.lang, dest='es')
            text = shave_accents(text)
            intent = self.irec.get_intent(text, frame)
            if intent:
                self.get_new_domain(frame)
                answer = self.answering_text(frame)
                if frame['DOM'] == 'START':
                    response = {'DOM': 'START'}, answer
                else:
                    del frame['INT']
                    response = frame, answer
                self.save_profile()
                return response
        return frame, ""

    def get_response_audio(self, frame, audio):
        """
        API get_response in audio format
        :return: new frame (dict) and audio response (BytesIO mp3 format)
        """
        response = self.welcome_response(frame)
        if response:
            new_frame, text_response = response
        else:
            try:
                text = self.rec.recognize(audio)
            except UnknownValueError or RequestError:
                return frame, "", BytesIO()
            new_frame, text_response = self.get_response_text(frame, text)

        audio_response = self.syn.synthesize(text_response)
        return new_frame, text_response, audio_response

    def welcome_response(self, frame):
        if frame['DOM'] == 'START_CONVERSATION':
            return {'DOM': 'START'}, f"¡Hola {self.profile['name']}!¿En qué puedo ayudarte?"
        if frame['DOM'] == 'START_PREG_DEVELOP':
            pregunta = random.choice(["Com ha anat el dia", "Que t'ha semblat el servei neteja"])
            return {'DOM': 'PREG_DEVELOP'}, pregunta
        if frame['DOM'] in ['START_0', 'START_1']:
            # START_0 -> PREG_ESTADO_SALUD , START_1 -> PREG_INFO_USUARIO
            return frame, f"¡Hola {self.profile['name']}!, me gustaría preguntarte algo. Es urgente?"
        return None

    def answering_text(self, frame: dict) -> str:
        answer = self.resp.get_answer(frame)
        dom_before = frame['DOM']
        if answer and self.lang != 'es':
            answer = self.google_translate(answer, src='es', dest=self.lang)
        self.execute_task(frame)
        answer_next = self.resp.get_answer(frame)
        dom_next = frame['DOM']
        if answer_next and dom_next != dom_before:
            if self.lang != 'es':
                answer_next = self.google_translate(answer_next, src='es', dest=self.lang)
            answer += " " + answer_next
        return answer

    def get_new_domain(self, frame: dict) -> None:
        domain, intent = frame['DOM'], frame['INT']
        frame['DOM'] = self.state_transition_table[domain][intent]

    def execute_task(self, frame: dict) -> None:
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
            poner_alarma_cloud()
            frame['DOM'] = 'START'
        if frame['DOM'] == 'DESACTIVO_ALARMA':
            self.profile['alarm']['activa'] = False
            desactivar_alarma_cloud()
            frame['DOM'] = 'START'
        if frame['DOM'] == 'ACTIVO_ALARMA':
            self.profile['alarm']['activa'] = True
            activar_alarma_cloud()
            frame['DOM'] = 'START'
        if frame['DOM'] == 'ACTIVAR_ALARMA':
            if self.profile['alarm']['activa']:
                frame['DOM'] = 'START'
        if frame['DOM'] == 'DESACTIVAR_ALARMA':
            if not self.profile['alarm']['activa']:
                frame['DOM'] = 'START'

        # ***** LLAMAR *****

        if frame['DOM'] == 'LLAMAR':
            num_contacto = frame.get('num_contacto', "")
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
            llamar_cloud()
            frame['DOM'] = 'START'

        # **** RECORDAR PASTILLA ****

        if frame['DOM'] == 'RECORDAR_PASTILLA':
            frame['DOM'] = 'START'

        # **** CUENTO ****
        if frame['DOM'] == 'CONTINUAR_CUENTO':
            frame['cuento'] = 'actual'
            frame['DOM'] = 'CONTAR_CUENTO'
        if frame['DOM'] == 'CAMBIAR_CUENTO':
            frame['DOM'] = 'CONTAR_CUENTO'
        if frame['DOM'] == 'CAMBIAR_CUENTO_0':
            frame['DOM'] = 'LISTA_CUENTOS'
        if frame['DOM'] == 'CONTAR_CUENTO':
            exp = r'(actual|estaba(s|mos)? leyendo|otro dia|ultima vez|ayer|antes)( por favor| gracias)?$'
            cuento = frame.get('cuento', False)
            actual = not cuento or eval_regex(cuento, exp)  # m'esta demanant l'actual?
            cuento_actual = self.profile['books']['actual']['title']
            if actual and not cuento_actual:
                frame['DOM'] = 'NO_CUENTO'
            else:
                if actual:
                    frame['cuento'] = cuento_actual
                title, story_link = find_story(self.stories, frame['cuento'])
                if story_link:
                    self.profile['books']['actual']['title'] = title
                    play_youtube_story(story_link)
                    frame['DOM'] = 'START'
                else:
                    frame['DOM'] = 'NO_CUENTO'

        if frame['DOM'] == 'CONTAR_CUENTO_0':
            cuento_actual = self.profile['books']['actual']['title']
            if not cuento_actual:
                frame['DOM'] = 'LISTA_CUENTOS'

        # **** CANCION ****

        if frame['DOM'] == 'ESC_CANCION':
            escuchar_cancion_cloud()
            play_youtube_music(frame['cancion'])
            frame['DOM'] = 'START'

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

        if frame['DOM'] == 'RESPEUSTA_PREG_USUARIO_SI':
            respuesta_preg_usuario = "si"
            frame['DOM'] = 'START'
        if frame['DOM'] == 'RESPEUSTA_PREG_USUARIO_NO':
            respuesta_preg_usuario = "no"
            frame['DOM'] = 'START'

        if frame['DOM'] == 'RESPOSTA_DEVELOP':
            calidad_respuesta = frame['calidad']
            if calidad_respuesta != "excelente":
                # frame['DOM'] = "..."
                # TODO: Si l'estat no es excel·lent anar a un altre estat: Que mejorarias?
                pass
            else:
                frame['DOM'] = 'START'

    def save_profile(self):
        """
        Save profile in json format
        """
        with open(f'../assistant/data/users/{self.user}/profile.json', 'w') as fp:
            txt = prettyjson(self.profile, indent=4, maxlinelength=80)
            fp.write(txt)

    # *** IGNORE (main) ***
    def start(self) -> None:
        pass


##########################
#                        #
# CLOUD FUNCTIONALITIES  #
#                        #
##########################

def llamar_cloud():
    pass


def poner_alarma_cloud():
    pass


def activar_alarma_cloud():
    pass


def desactivar_alarma_cloud():
    pass


def buscar_cloud():
    pass


def buscar_imagenes_cloud():
    pass


def buscar_loccalizacion_cloud():
    pass


def escuchar_cancion_cloud():
    pass


def escuchar_cuento_cloud():
    pass
