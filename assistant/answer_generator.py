#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author: Oriol Aranda


#################################
# ****** ANSWER GENERATOR *******
#################################

import random
from model import IAnswerGenerator
from utilities.utilities import date, weather, select_riddle, select_joke, get_pills, get_alarm_time, list_elem, \
    carer_date, date_event, game_level, eq_seqs


class AnswerGenerator(IAnswerGenerator):
    """
    Answer Generator module
    """

    def __init__(self, profile, books_titles, riddles, jokes):
        self.profile = profile
        self.books_titles = books_titles
        self.jokes = jokes
        self.riddles = riddles
        self.pills = self.profile['pills']

    def get_answer(self, frame: dict) -> str:
        # self.resp = load_json('data/responses.json')
        # return self.resp[frame['DOM']]

        ##########
        # GENERAL
        ##########
        if frame['DOM'] == 'SALUDO':
            return "¡Hola! ¿en qué puedo ayudarte?"
        if frame['DOM'] == 'START':
            if frame.get('llamar', False):
                return "Ahora te atenderá emergencias. Llamando..."
        if frame['DOM'] == 'EXIT':
            return "¡Hasta pronto!"
        if frame['DOM'] == 'COMO_LLAMAS':
            return "Me llamo Alex y soy tu asistente personal inteligente"
        if frame['DOM'] == 'COMO_ESTAS':
            return "Estoy muy bien, gracias por preguntar!"
        if frame['DOM'] == 'CUANTOS_ANYOS':
            return "Nací hace 1 mes! no está nada mal, verdad?"
        if frame['DOM'] == 'REPETIR':
            return "Sí, perdona."
        if frame['DOM'] == 'GRACIAS':
            l_res = ["¡No hay de qué!", "¡Para eso estamos!", "¡De nada!", "¡Para lo que quieras!"]
            return random.choice(l_res)

        ###############
        # PRESENTACIÓN
        ###############
        if frame['DOM'] == 'PRESENTACION':
            return f"¡Encantado de conocerte {frame['nombre'].title()}! Gracias por responder a todas las preguntas." \
                   "Soy Alex, tu nuevo asistente personal inteligente. " \
                   "Mi única función es ayudarte en todo lo que pueda. Puedo recordarte la medicación," \
                   "recordarte eventos que tengas programados en el calendario, entretenerte con algun cuento, musica," \
                   " adivinanzas o chistes. Puedo incluso jugar a un juego, decirte el tiempo de hoy,mañana y " \
                   "toda la semana, despertate a la hora que quieras con el despertador, llamar a tus hijos o alguno de " \
                   "tus amigos.¡Y algunas funciones más! Solo tienes que hablar conmigo como si de un humano se tratara."
        if frame['DOM'] == 'PREG_NOMBRE':
            return "¿Cómo te llamas?"
        if frame['DOM'] == 'NOMBRE':
            return "¿Puedes decirme tu nombre?"
        if frame['DOM'] == 'APELLIDO':
            return f"De acuerdo {frame['nombre'].title()}. ¿Y tu apellido?"
        if frame['DOM'] == 'ANYOS':
            return f"¡Perfecto {frame['nombre'].title()}!¿Cuántos años tienes?"
        if frame['DOM'] == 'REP_NOMBRE':
            l_res = [f"¿Te llamas {frame['nombre'].title()} y de apellido {frame['apellido'].title()}?",
                     f"{frame['nombre'].title()} y de apellido {frame['apellido'].title()} ¿verdad?"]
            return random.choice(l_res)
        if frame['DOM'] == 'REP_ANYOS':
            return f"¿Tienes {frame['anyos']} años?"
        if frame['DOM'] == 'SEXO':
            return "¿Eres un hombre, o una mujer?"
        if frame['DOM'] == 'REP_SEXO':
            if 'hombre' in frame['sexo']:
                return "Eres un hombre, ¿cierto?"
            return "eres una mujer, ¿cierto?"
        if frame['DOM'] == 'SEXO_BOT':
            return "¿Prefieres un asistente mujer, hombre o te da igual?"
        if frame['DOM'] == 'TRATO':
            return "Qué tipo de trato prefieres que tenga contigo de usted o de tú?"
        if frame['DOM'] == 'LENGUA':
            return "En qué idioma prefieres que te hable, ¿Catalán o Castellano?"

        ####################
        # PREG_INFO_USUARIO
        ####################
        if frame['DOM'] == 'PREG_INFO_USUARIO':
            return "¿Estás contento con el cuidador nuevo?"

        ####################
        # PREG_ESTADO_SALUD
        ####################
        if frame['DOM'] == 'PREG_ESTADO_SALUD':
            return "¿Cómo te encuentras hoy?"

        ###############
        # ESTADO SALUD
        ###############

        if frame['DOM'] == 'ESTADO_SALUD_BIEN':
            return "¡Me alegro!¡Comer sano y hacer ejercicio siempre ayuda!¿Qué puedo hacer por ti?"
        if frame['DOM'] == 'ESTADO_SALUD_MAL':
            return "!Esto no es bueno!¿Quieres llamar a alguien?"

        ##################
        # ENTRETENIMIENTO
        ##################

        if frame['DOM'] == 'PREG_ENTRETENER':
            return "Puedo contarte una adivinanza, un cuento, un chiste, ponerte una canción o jugar a un juego de " \
                   "memoria.¿Qué prefieres?"

        ##########
        # CUENTO
        ##########

        if frame['DOM'] == 'NO_CUENTO':
            return "Lo siento, parece que no tengo este libro. ¿Quieres que te diga cuales tengo hoy disponibles?"
        if frame['DOM'] == 'CONTINUAR_CUENTO':
            cuento_actual = self.profile['books']['actual']['title']
            return f'¡Perfecto! Vamos a seguir con "{cuento_actual}"'
        if frame['DOM'] == 'LISTA_CUENTOS':
            books_list = ". ".join(self.books_titles[:-1]) + " y " + self.books_titles[-1]
            return f"¿Qué cuento prefieres que te lea? Estos son los cuentos que tengo a mano: {books_list}"
        if frame['DOM'] == 'CONTAR_CUENTO_0':
            cuento_actual = self.profile['books']['actual']['title']
            if cuento_actual:
                return f'¿Quieres seguir con "{cuento_actual}", el cuento que estábamos leyendo?'
            else:
                return ""

        ##########
        # CHISTE
        ##########
        if frame['DOM'] == 'CONTAR_CHISTE':
            i_joke, actual_joke = select_joke(self.jokes)
            self.profile['jokes']['read'].append(i_joke)
            if frame.get('chiste', False):
                frame['chiste'] = actual_joke
                return actual_joke
            else:
                frame['chiste'] = actual_joke
                return "A ver si te sabes este. " + actual_joke
        if frame['DOM'] == 'REPETIR_CHISTE':
            return "Ahí va otra vez: " + frame['chiste']
        if frame['DOM'] == 'MAS_CHISTES':
            return "¿Te cuento otro?"

        ##############
        # ADIVINANZA
        ##############

        if frame['DOM'] == 'CONTAR_ADIVINANZA_0':
            if self.profile['riddles']['actual'] < 0:
                return select_riddle(self.profile, self.riddles)
            else:
                return ""
        if frame['DOM'] == 'EXISTE_ADIVINANZA':
            return f'¿Quieres seguir con la ultima adivinanza que te conté?'
        if frame['DOM'] == 'CONTINUAR_ADIVINANZA':
            if self.profile['riddles']['actual'] >= 0:
                return f'Puedo repetirla, ayudarte, darte la solucion o puedes ir diciendo respuestas.'
            else:
                return "No hay ninguna adivinanza empezada. Te leo esta: " + select_riddle(self.profile, self.riddles)
        if frame['DOM'] == 'CONTAR_ADIVINANZA_NUEVA':
            self.profile['riddles']['actual'] = -1
            return select_riddle(self.profile, self.riddles)
        if frame['DOM'] == 'REPETIR_ADIVINANZA':
            return self.riddles[self.profile['riddles']['actual']][0]
        if frame['DOM'] == 'AYUDA_ADIVINANZA':
            return self.riddles[self.profile['riddles']['actual']][3]
        if frame['DOM'] == 'DAR_SOLUCION':
            return "¿Quieres que te dé la respuesta correcta?"
        if frame['DOM'] == 'RESOLVER_ADIVINANZA':
            if frame.get('solucion', False):
                del frame['solucion']
                return "La respuesta no es correcta, ¡pero sígue intentándolo!"
        if frame['DOM'] == 'SOLUCION_BUENA':
            return self.riddles[self.profile['riddles']['actual']][4]
        if frame['DOM'] == 'SEGUIR_PROBANDO':
            return "Sigue pensando, ¡ya casi lo tienes!"
        if frame['DOM'] == 'OTRA_ADIVINANZA':
            solucion = ""
            if frame.get('solucion', False):
                solucion = self.riddles[self.profile['riddles']['actual']][2]
                self.profile['riddles']['actual'] = -1
            return solucion + "Tengo otro acertijo, ¿quieres que te lo cuente?"
        if frame['DOM'] == 'FINALIZAR_ADIVINANZA':
            return "Cuando quieras puedes seguir o continuar con ella pidiéndomelo."

        ###########
        # CANCION
        ###########

        if frame['DOM'] == 'ESC_CANCION':
            return "¡Escucha!"
        if frame['DOM'] == 'ESC_CANCION_0':
            return "¿Qué canción quieres escuchar?"

        ##########
        # DIARIA
        ##########

        if frame['DOM'] == 'DIA':
            if frame.get('dia', None):
                return date('dia', frame['dia'])
            return date('dia')
        if frame['DOM'] == 'HORA':
            return date('hora')
        if frame['DOM'] == 'TIEMPO':
            if frame.get('dia', None):
                if "semana" in frame['dia']:
                    frame['dia'] = 'semana'
                return weather(frame['dia'])
            return weather()

        ##########
        # ALARMA
        ##########
        if frame['DOM'] == 'PREGUNTA_ALARMA':
            if self.profile['alarm']['activa']:
                if frame['INT'] == 'poner_alarma':
                    pass
                elif frame['INT'] == 'poner_alarma_1':
                    frame['DOM'] = 'PREG_ALARMA_1'
                else:
                    frame['DOM'] = 'PREG_ALARMA_0'
                return f"Hay una alarma activa para las {self.profile['alarm']['local']}.¿Quieres cambiarla?"
            elif not self.profile['alarm']['local'] and frame['INT'] == 'poner_alarma':
                frame['DOM'] = 'PONER_ALARMA'
            elif not self.profile['alarm']['local'] and (
                    frame['INT'] == 'poner_alarma_0' or frame['INT'] == 'cambiar_alarma'):
                frame['DOM'] = 'PONER_ALARMA_0'
            elif not self.profile['alarm']['local'] and frame['INT'] == 'poner_alarma_1':
                frame['DOM'] = 'PONER_ALARMA_1'
            else:
                if frame['INT'] == 'poner_alarma':
                    pass
                elif frame['INT'] == 'poner_alarma_1':
                    frame['DOM'] = 'PREG_ALARMA_1'
                else:
                    frame['DOM'] = 'PREG_ALARMA_0'
                return f"La alarma actual está desactivada. Quieres activar la alarma a las {self.profile['alarm']['local']} o prefieres cambiarla?"

        if frame['DOM'] == 'PONER_ALARMA':
            hora = frame.get('hora', False)
            horario = frame.get('horario', False)

            local, res = get_alarm_time(hora, horario)
            self.profile['alarm']['local'] = local
            self.profile['alarm']['activa'] = True
            frame['DOM'] = 'START'
            return res
        if frame['DOM'] == 'PONER_ALARMA_0':
            return "¡De acuerdo! A qué hora quieres que te despierte?"
        if frame['DOM'] == 'PONER_ALARMA_1':
            return "¿De la mañana o de la tarde?"
        if frame['DOM'] == 'ACTIVAR_ALARMA':
            if not self.profile['alarm']['activa']:
                if self.profile['alarm']['local']:
                    return f"Quieres activar la alarma a las {self.profile['alarm']['local']}?"
                else:
                    frame['DOM'] = 'START'
                    return f"No hay ninguna alarma para activar. Pideme poner una alarma si quieres."
            return f"Actualmente la alarma está activa a las {self.profile['alarm']['local']}"
        if frame['DOM'] == 'DESACTIVAR_ALARMA':
            if self.profile['alarm']['activa']:
                return f"Seguro que quieres desactivar la alarma actual puesta a las {self.profile['alarm']['local']}?"
            return "La alarma ya está desactivada. ¡Podrás dormir un poquito más!"
        if frame['DOM'] == 'DESACTIVO_ALARMA':
            return "He desactivado la alarma! Puedes activarla o poner otra pidiéndomelo."
        if frame['DOM'] == 'ACTIVO_ALARMA':
            return f"He activado la alarma! Voy a despertarte a las {self.profile['alarm']['local']}."

        ##########
        # BUSCAR
        ##########

        if frame['DOM'] == 'BUSCAR_IMAGEN':
            return "Estas son las imágenes que he encontrado!"
        if frame['DOM'] == 'BUSCAR_IMAGEN_0':
            return "¿Imágenes sobre qué?"
        if frame['DOM'] == 'BUSCAR_LOC':
            return "¡Aquí está!"
        if frame['DOM'] == 'BUSCAR_LOC_0':
            return "¿Qué localización quieres buscar?"
        if frame['DOM'] == 'BUSCAR':
            return "Bien! Esto es lo que he encontrado!"
        if frame['DOM'] == 'BUSCAR_0':
            return "¿Qué quieres buscar?"

        if frame['DOM'] == 'NADA':
            return "¡De acuerdo!¿Puedo ayudarte en algo más?"
        if frame['DOM'] == 'NADA_EXIT':
            return "¡De acuerdo, hasta la proxima!"
        if frame['DOM'] == 'NO_RECUERDA':
            return "¡No pasa nada!Cuando te acuerdes, pídemelo otra vez!"
        if frame['DOM'] == 'NO_RECUERDA_EXIT':
            return "¡Tranquila!Cuando te acuerdes, pídemelo otra vez!"

        ##########
        # LLAMAR
        ##########

        if frame['DOM'] == 'LLAMAR_SEGURO':
            nom, apodo, status, num = frame['contacto']
            contacto = ""
            if status in ['hijo', 'hija', 'hermano', 'hermana', 'nieto', 'nieta']:
                contacto += f"tu {status} {nom.split()[0]}"
            else:
                contacto += f'{nom}'
            return "Quieres llamar a " + contacto + f" con el número +{num}?"
        if frame['DOM'] == 'LLAMAR_DEF':
            return "Llamando..."
        if frame['DOM'] == 'LLAMAR_0':
            return "¿A quién quieres llamar?"
        if frame['DOM'] == 'ESCOGER_CONTACTO':
            tipo = frame['lista_contactos'][0]
            if tipo:
                return f"¿A cual de tus {tipo + 's'} quieres llamar? " + frame['lista_contactos'][1]
            else:
                return "Hay mas de un contacto ¿A cual de estos quieres llamar? " + frame['lista_contactos'][1]
        if frame['DOM'] == 'NO_CONTACTO':
            return "No existe ningún contacto. ¿A quién quieres llamar?"
        if frame['DOM'] == 'NO_ENTENDER_CONTACTO':
            return "Perdona, no lo entendí bien."

        #################
        # FAM = PASTILLA
        #################
        if frame['DOM'] == 'RECORDAR_PASTILLA':
            return get_pills(frame.get('pastilla', False), self.pills)

        ############
        # CUIDADOR
        ############
        if frame['DOM'] == 'NOMBRE_CUIDADOR':
            carers = self.profile['carers']['names'].values()
            if len(carers) == 1:
                return f"Tu cuidador se llama: {list(carers)[0]}."
            elif len(carers) > 1:
                return f"Tus cuidadores son: {list_elem(list(carers))}."
            return "No tienes ningún cuidador o cuidadora actualmente."
        if frame['DOM'] == 'DIA_CUIDADOR':
            name = frame.get('cuidador', False)
            return carer_date(self.profile['carer'], name, False, False)
        if frame['DOM'] == 'HORA_CUIDADOR':
            name = frame.get('cuidador', False)
            dia = frame.get('dia', False)
            return carer_date(self.profile['carer'], name, dia)

        ##########
        # EVENTO
        ##########
        if frame['DOM'] == 'FECHA_EVENTO_0':
            return "No he entendido qué evento me has dicho. ¿Puedes repetir el evento?"
        if frame['DOM'] == 'FECHA_EVENTO':
            return date_event(self.profile['events'], frame['evento'])

        ##############
        # JUGAR
        ##############
        if frame['DOM'] == 'JUGAR':
            level = game_level(self.profile['games']['memory'], [])
            frame['nivel'] = level
            return "¡Bienvenido al juego de memoria! Tienes que repetir las palabras que yo diga en orden. " \
                   "¿Estás listo? ¡Empecemos! Primer nivel: " + ", ".join([level[0].title()] + level[1:])

        if frame['DOM'] == 'SIGUIENTE_NIVEL':
            answer = frame['respuesta'].split()
            if eq_seqs(answer, frame['nivel']):
                new_lvl = game_level(self.profile['games']['memory'], frame['nivel'])
                congrats = ["Muy bien", "Perfecto", "Bien", "Correcto", "Sigue así", "Lo haces bien",
                            "Lo haces muy bien", "Fácil", "Eso es", "Eres un profesional", "Eres un maestro",
                            "Impresionante", "Bien hecho"]
                return f"{random.choice(congrats)}! Nivel {len(new_lvl)}. " + ", ".join(
                    [new_lvl[0].title()] + new_lvl[1:])
            else:
                bad = ["No es correcto", "No", "Vuelve a intentarlo", "Prueba de nuevo", "Inténtalo de nuevo",
                       "Incorrecto", "Casi lo tienes", "Casi", "Ha estado cerca", "Prueba otra vez"]
                return f"{random.choice(bad)}! Si quieres puedo repetirlo."
        if frame['DOM'] == 'FINALIZAR_JUEGO':
            return "¿Seguro que quieres abandonar el juego? Se va a perder todo el progreso que hayas conseguido."
        if frame['DOM'] == 'FINALIZAR_JUEGO_DEF':
            return "De acuerdo, hasta la próxima!"
        if frame['DOM'] == 'REPETIR_NIVEL':
            return "Atento: " + ", ".join(frame['nivel'])


        ##############
        # PREG_DEVELOP
        ##############
        if frame['DOM'] == 'RESPOSTA_DEVELOP':
            return "Gracias por tu opinión!"

        return ""
