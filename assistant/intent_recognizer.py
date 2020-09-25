#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author: Oriol Aranda

#####################################
# ******* INTENT RECOGNIZER ********
#####################################

import re
from model import IIntentRecognition
from utilities.utilities import load_json


class IntentRecognizer(IIntentRecognition):
    """
    Intent Recognition module
    """

    def __init__(self, info, st_table=load_json('../assistant/data/state_transition_table.json')):
        self.list_args_0 = []
        self.list_args_1 = []
        self.info = info
        self.domain_intents_list = {k: [x for x in v.keys() if ('0' not in x) and ('1' not in x)] for k, v in
                                    st_table.items()}
        self.grammars = dict(self.compile_grammars())

    def compile_grammars(self):

        ################
        # FAM = GENERAL
        ################

        saludo = (
            'saludo',
            r'(?P<saludo>hola|buenos dias|buenas( noches| tardes)?|hey)'
        )
        como_llamas = (
            'COMO_LLAMAS',
            r'quien eres|cual es tu nombre|como te (llamas|llaman|apoda[sn])'
        )
        como_estas = (
            'COMO_ESTAS',
            rf'(como estas|que tal estas|como lo llevas|estas (bien|mal|regular)|te encuentras (bien|mal|regular)|como te encuentras|como te va|como andas|que haces)'
        )
        cuantos_anyos = (
            'CUANTOS_ANYOS',
            rf'cuantos años (tienes|cumples)'
        )
        despedida = (
            'DESPEDIDA',
            r'(?P<despedida>adios|hasta (luego|pronto|mañana)|chao|salir)'
        )
        repetir = (
            'REPETIR',
            r'((no (te |lo )?entendi)|repetir|repitelo|repetirias|repitieras|(volver|volvieras) a decir)'
        )
        gracias = (
            'gracias',
            r'((muchas|muchisimas) )?gracias'
        )
        nada = (
            'nada',
            r'(^no)|((nada( mas)?|ninguna( cancion|imagen|foto|adivinanza)?|ninguno|ningun( cuento|narracion|libro|acertijo)|me equivoque|me he equivocado)( perdon(a)?| gracias)?)$|da igual|dejalo|dejemoslo'
        )

        no_recuerda = (
            'no_recuerda',
            r'no lo se|no me acuerdo|se me ha olvidado|no te se decir|(no tengo )?(ni )?idea|no (lo)? recuerdo'
        )
        urgente = (
            'urgente',
            r'si|urgente|no puedo|otro (momento|rato)'
        )
        pregunta = (
            'pregunta',
            r'pregunta|^vale |vale$|de acuerdo|venga|dale'
        )

        general_grs = [saludo, despedida, no_recuerda, nada, como_llamas, como_estas, cuantos_anyos, gracias,
                       repetir, urgente, pregunta]

        #####################
        # FAM = PRESENTACION
        #####################

        nombre = (
            'nombre',
            r'((me llamo|me llaman|mi nombre es|me conocen (por|como)) )?(?P<nombre>(\w+))?( (?P<apellido>\w+( \w+)?))?'
        )
        solo_nombre = (
            'solo_nombre',
            r'((me llamo|me llaman|mi nombre es|me conocen (por|como)) )?(?P<nombre>(\w+)( \w+)?)?'
        )
        apellido = (
            'apellido',
            r'(de apellido |mi apellido es )?((me llamo|me llaman|mi nombre es|me conoce(n)? (por|como)) )?(?P<apellido>\w+( \w+)?)'
        )
        anyos = (
            'anyos',
            r'(acabo de cumplir |he cumplido |cumplo |tengo )?(?P<anyos>\d+)( años| tacos)?'
        )
        sexo = (
            'sexo',
            r'(es |me siento |soy )?(un |una )?(?P<sexo>hombre|mujer)?'
        )
        sexo_bot = (
            'sexo_bot',
            r'(un |una |me )?(?P<sexo_bot>hombre|mujer|(da )?igual)?'
        )

        trato = (
            'trato',
            r'(de )?(?P<trato>usted|tu)?'
        )
        lengua = (
            'lengua',
            r'(?P<lengua>catala(n)?|castella(no)?|español)?'
        )

        presentacion_grs = [nombre, anyos, solo_nombre, apellido, sexo, sexo_bot, trato, lengua]
        pres0_grs = [nombre, anyos, apellido, solo_nombre, trato, lengua, sexo_bot, sexo]
        pres1_grs = [nombre]
        #####################
        # FAM = ESTADO SALUD
        #####################

        BIEN = r'(?:bastante |mas o menos |muy |mucho (?:mas)?)?(?:bien|mejor|excelente|perfet[oa]|energic[ao]|feliz)'
        MAL = r'(?:en (?:la mierda|el pozo)|(?:bastante |mas o menos |muy |mucho mas |un poco )?(?:mal|fatal|cansad[ao]|acabad[ao]|triste|sin fuerzas|agotad[ao]|agobiad[ao]|enferm[ao]|rebentad[oa]|maread[oa]))'
        estado_salud_bien = (
            'estado_salud_bien',
            rf'(?:(?<!no )(?:estoy |me (?:encuentro|siento|noto) ){BIEN})|(?:no (?:estoy |me (?:encuentro|siento|noto) ){MAL})'
        )
        estado_salud_mal = (
            'estado_salud_mal',
            rf'(?P<estado_salud_mal>(estoy |me (encuentro|siento|noto) ){MAL}|no (estoy |me (encuentro|siento|noto) ){BIEN}|ayuda(me)?)'
        )

        estado_salud_grs = [estado_salud_bien, estado_salud_mal]

        ########################
        # FAM = ENTRETENIMIENTO
        ########################

        CONTAR = r'((cuenta|contar)(me|nos|as)?|explica(r)?(me|nos|as)?|lee(r)?(me|nos)?|leyeras|escuchar|oir|pon(er)?(me|nos)|pusieras|hacemos|hacer|hagamos)'
        preg_entretener = (
            'preg_entretener',
            rf'(({CONTAR}( algo| (cualquier|alguna) cosa)?)( por favor)?\??$|(que(.*?){CONTAR})$)'
        )
        cont_adivinanza = (
            'contar_adivinanza',
            rf'{CONTAR} ((un(a)?|algun(a|o)?)(s)? )?(adivinanza(s)?|acertijo(s)?)( de| sobre)?( (?P<adivinanza>(\w+)( \w+)*?))?( por favor)?'
        )
        continuar_adivinanza = (
            'continuar_adivinanza',
            r'(continuar|seguir) (.*?)(adivinanza|acertijo|enigma)'
        )
        retpetir_adivinanza = (
            'repetir_adivinanza',
            r'repetir|volver a (leer|escuchar)'
        )
        solucion_adivinanza = (
            'solucion_adivinanza',
            r'me rindo|nos rendimos|(da(r)?(me|nos)?|(decir|di)(me|nos)?) la ((solucion|respuesta)( correcta)?)'
        )
        ayuda_adivinanza = (
            'ayuda_adivinanza',
            r'(da(r)?(me|nos)?|(decir|di)(me|nos)?) (una|alguna) pista|ayuda'
        )
        respuesta_adivinanza = (
            'respuesta_adivinanza',
            r'(creo que )?(la (solucion|respuesta) )?(es|sea) (?P<respuesta>(\w+)( \w+)*)'
        )
        finalizar_adivinanza = (
            'finalizar_adivinanza',
            r'salir|(seguir(e)?|continuar(e)?)|mas tarde|luego|despues'
        )

        contar_cuento = (
            'contar_cuento',
            rf'{CONTAR} (el|la|un|una|alguna?) (lectura|cuento|narracion|historia|libro)( de| del)?( (?P<cuento>(\w+)( \w+)*))?( por favor)?'
        )

        continuar_cuento = (
            'continuar_cuento',
            r'(continuar|seguir) (.*?)(cuento|lectura|libro|narracion|historia)'
        )
        cont_chiste = (
            'CONTAR_CHISTE',
            rf'{CONTAR} ((un|algun)(os)? )?(chiste(s)?)( de| sobre)?( (?P<chiste>(\w+)( \w+)*))?( por favor)?'
        )
        esc_cancion = (
            'ESC_CANCION',
            rf'(pon(er)?(me|nos)?|pusieras|escuchar|oir)( (la|una|un poco de))?( cancion| musica)?( (de |del )?(?P<cancion>(\w+)( \w+)*))?( por favor)?'
        )
        jugar = (
            'JUGAR',
            r'((juego|juguemos|jugamos|jugar)( a)?)( (un|algun)?(algo| juego))?'
        )

        que_cancion = (
            'que_cancion',
            r'(?P<cancion>(\w+)( \w+)*)( por favor)?'
        )

        que_cuento = (
            'que_cuento',
            rf'({CONTAR})?(?P<cuento>(\w+)( \w+)*)( por favor)?'
        )
        si = (
            'si',
            r'^si |si$|^vale |vale$|de acuerdo|venga|dale|por favor|exacto|correcto|cierto'
        )
        no = (
            'no',
            r'^no |no$|ya (esta|basta)|incorrecto|falso'
        )
        otros = (
            'otros',
            r'otr[oa](s)?|algun[ao](s)?( mas| otr[ao]s)?|nuev[ao]'
        )

        cuento = (
            'cuento',
            r'cuento|libro|narracion|historia|lectura|leer'
        )
        cancion = (
            'cancion',
            r'cancion|musica|escuchar'
        )
        chiste = (
            'chiste',
            r'chiste|broma'
        )
        adivinanza = (
            'adivinanza',
            r'adivinanza|acertijo|enigma'
        )

        entretenimiento0_grs = [contar_cuento, esc_cancion]
        entretenimiento_grs = [preg_entretener, jugar, cont_adivinanza, contar_cuento,
                               cont_chiste, esc_cancion, continuar_cuento, que_cancion, que_cuento,
                               si, no, otros, cuento, cancion, chiste, adivinanza, retpetir_adivinanza,
                               respuesta_adivinanza, solucion_adivinanza, ayuda_adivinanza, continuar_adivinanza,
                               finalizar_adivinanza]

        ###############
        # FAM = DIARIA
        ###############

        dia = (
            'DIA',
            r'(en )?que (fecha|dia( de la semana)?) (es|sera|estamos)( (?P<dia>hoy|mañana))?( por favor)?'
        )
        hora = (
            'HORA',
            r'la hora|que hora (es|tienes)'
        )
        tiempo = (
            'TIEMPO',
            r'(tiempo|(tiempo|prevision( del tiempo)?)(( hay)? (para|de))|hara|hace|hay|(nos )?va a hacer(nos)?)( (?P<dia>hoy|mañana|((?:(durante )?(toda )?esta|la|entre) semana)))?( por favor)?'
        )
        poner_alarma = (
            'poner_alarma',
            r'((gustaria|quiero|quisiera|pon(er)?(me)?|tener)( (otra|una|la)?( nueva)? alarma| (otro|un|el)?( nuevo)? despertador)|despiertame|despertar(me)?)( (para|a) la(s)? (?P<hora>(\d{,2}:\d{,2}|\d+)))?( (de|por)? (la )?(?P<horario>mañana|tarde|pm|am))?( por favor)?'
        )
        cambiar_alarma = (
            'cambiar_alarma',
            r'cambia(r)? (la hora (de |del))?(la alarma|(el)? despertador)|(cambiar l[ao]|cambiarl[ao])'
        )
        que_horario = (
            'que_horario',
            r'(de|por)?(la)?(?P<horario>mañana|madrugada|noche|tarde|pm|am)'
        )
        que_hora = (
            'que_hora',
            r'(a |para )?(la(s)? )?(?P<hora>\d{,2}:\d{,2}|\d{,2})( (de|por)? (la)? (?P<horario>mañana|madrugada|noche|tarde|pm|am))?( por favor)?'
        )
        desactivar_alarma = (
            'desactivar_alarma',
            r'(desactiva(r)?|elimina(r)?|quita(r)?) la alarma|(desactivarl[oa]|desactivar l[ao])'
        )
        activar_alarma = (
            'activar_alarma',
            r'activa(r)? (la|una) alarma|(activarl[ao]|activar l[ao])'
        )

        diaria_grs = [dia, hora, tiempo, poner_alarma, cambiar_alarma, que_horario, que_hora, desactivar_alarma,
                      activar_alarma]

        diaria0_grs = [poner_alarma]
        diaria1_grs = [poner_alarma, que_hora]

        ###############
        # FAM = BUSCAR
        ###############
        buscar = (
            'BUSCAR',
            r'(busca(r|as|me)?|busques|enseñ(ar(as)?|ame|arme|es)|saber)( algo|( sobre| si)? (?P<texto>(\w+)( \w+)*))?( por favor)?'
        )
        buscar_imagen = (
            'BUSCAR_IMAGEN',
            r'(busca(r|as|me)?|busques|ver|mostrar(as|me)?|enseñ(ar(as)?|ame|arme|es)|encontrar(me|as)?)( alguna(s)?| una(s)?)?( imagen(es)?| foto(s)?)( de| sobre)?( (?P<imagenes>(\w+)( \w+)*))?( por favor)?'
        )
        buscar_loc = (
            'BUSCAR_LOC',
            r'((busca(r|as|me)?|busques|encontrar(me|as)?|saber|sabes|ver|mostrar(as|me)?|enseñ(ar(as)?|ame|arme|es)) )?(donde (esta( situad[oa])?|se (encuentra|encontrar|situa)))(( un(a)?| la| el) (localizacion|ubicacion|ciudad|pueblo|sitio|montaña|pais)( de)?)?( (?P<localizacion>(\w+)( \w+)*))?'
        )

        que_buscar = (
            'que_buscar',
            r'(?P<texto>(\w+)( \w+)*)( por favor)?'
        )
        que_imagen = (
            'que_imagen',
            r'(?P<imagenes>(\w+)( \w+)*)( por favor)?'
        )
        que_loc = (
            'que_loc',
            r'(?P<localizacion>(\w+)( \w+)*)( por favor)?'
        )

        buscar0_grs = [buscar_imagen, buscar_loc, buscar, que_buscar, que_imagen, que_loc]

        buscar_grs = [buscar_imagen, buscar_loc, buscar, que_buscar, que_imagen, que_loc]

        ###############
        # FAM = PLAYER
        ###############

        continuar = (
            'continuar',
            r'continua(r)?|que siga|sigue|seguir|dale|play'
        )
        pausar = (
            'pausar',
            r'pausa(r)?|(para(r)?|espera(r)?) un momento|pause|para(r)?( por favor| gracias)|para(r)?$'
        )
        parar = (
            'parar',
            r'stop|basta|quita(r)?|no (me apetece|quiero) (seguir( escuchando| escuchar)?)( mas)?|ya (tengo bastante|esta|basta)|segui(r|mos|re) (luego|mas tarde)'
        )
        cambiar_cancion = (
            'cambiar_cancion',
            r'cambia(r)?|pon(er)? otr[ao]'
        )
        bajar_vol = (
            'bajar_vol',
            r'baja(r)?( un poco)?( mas)?( el volumen)?'
        )
        subir_vol = (
            'subir_vol',
            r'(subir|sube)( un poco)?( mas)?( el volumen)?'
        )
        mas = (
            'mas',
            r'mas'
        )
        menos = (
            'menos',
            r'menos'
        )
        cambiar_cuento = (
            'cambiar_cuento',
            r'cambia(r)?|pon(er)? otr[ao]'
        )

        play_grs = [continuar, pausar, parar, cambiar_cancion, cambiar_cuento, bajar_vol, subir_vol, mas, menos]

        ###############
        # FAM = LLAMAR
        ###############

        llamar = (
            'llamar',
            r'llam[ea](r)?( (con|por|al)( el)?( telefono( movil)?| movil))? a(l| la| el)?( (numero|un))?( (?P<num_contacto>(\d+)( \d+){,2}))?( (mi )?(?P<status>hij[oa]|herman[oa]|niet[oa]|niñ[oa]|amig[oa]))?( (?P<contacto>([a-zA-Z]+)( [a-zA-Z]+)*?))?( por favor)?'
        )
        quien_llamar = (
            'quien_llamar',
            r'(a(l| la| el)? )?((?P<num_contacto>(\d+)( \d+){,2}))?((?P<contacto>([a-zA-Z]+)( [a-zA-Z]+)*?))?( (mi )?(?P<status>hij[oa]|herman[oa]|niet[oa]|niñ[oa]|amig[ao]))?( por favor)?'
        )
        nadie = (
            'nadie',
            r'nadie'
        )

        llamar_grs = [llamar, quien_llamar, nadie]
        llamar0_grs = [llamar]

        ##################
        # FAM = PASTILLA
        ##################

        recordar_pastilla = (
            'recordar_pastilla',
            r'(hora|cuando|cuant[ao]s|dia).*(pastilla(s)?|medicamiento(s)?)( (?P<pastilla>[a-zA-Z]+))?( por favor)?'
        )

        pill_grs = [recordar_pastilla]

        ###################
        # FAM = FECHA EVENTO
        ####################
        eventos = "|".join(self.info['events'])
        fecha_evento = (
            'fecha_evento',
            rf'((cuando|que (dia|hora)) (tengo|tenia|tendre)? ((el|la|un|una) )?|((hoy|mañana|esto) )?tengo ((hoy|mañana|esto) )?)(?P<evento>{eventos})?'
        )

        que_evento = (
            'que_evento',
            rf'((cuando|que (dia|hora)) (tengo|tenia|tendre)? ((el|la|un|una) )?|((hoy|mañana|esto) )?tengo ((hoy|mañana|esto) )?)?(que (ir|visitar|llegar) )?(?P<evento>(\w+)( \w+)*)'
        )

        evento_grs = [fecha_evento, que_evento]
        evento0_grs = [fecha_evento]

        ###################
        # FAM = CUIDADOR
        ###################
        cuidador = "|".join([x.lower() for x in self.info['carers']['names'].values()])
        dia_cuidador = (
            'dia_cuidador',
            rf'que dia(s)? (vendra(n)?|(le(s)? toca|va(n)? a) venir|viene(n)?) (([ae]l|la|l[ao]s|mi(s)?) (cuidador(a(s)?|es)?|asistent[ea](s)?|ayudant[ea](s)?|chic[ao](s)?|hombre(s)?|mujer(es)?)|(a )?(?P<cuidador>{cuidador}))'
        )

        hora_cuidador = (
            'hora_cuidador',
            rf'((cuando|(a )?que hora(s)?) (llega(ra(n)?)?|viene(n)?|(le(s)? toca|va(n)? a) (venir|llegar)|vendra(n)?)|(a )?que hora(s)? viene(n)?) ((el )?(?P<dia>hoy|mañana|lunes|martes|miercoles|jueves|viernes|sabado|domingo) )?(([ae]l |la |l[ao]s |mi(s)? )?(cuidador(a(s)?|es)?|asistent[ea](s)?|ayudant[ea](s)?|chic[ao](s)?|hombre(s)?|mujer(es)?)|(a )?(?P<cuidador>{cuidador}))'
        )

        nombre_cuidador = (
            'nombre_cuidador',
            r'(((el|los) )?nombre(s)? de|cuidador(a(s)?|es)? como se (dice(n)?|decia(n)?|llama(n|ba)?)|cual(es)? (es|son) (el|los) nombre(s)? (del|de los|de mi(s)?)|como se (dice(n)?|decia(n)?|llama(n|ba(n)?)?))( (mi(s)?|[ae]l|l[oa]s|la))? (cuidador(a(s)?|es)?|asistent[ea](s)?|ayudant[ea](s)?|chic[ao](s)?|hombre(s)?|mujer(es)?)'
        )

        cuidador_grs = [dia_cuidador, hora_cuidador, nombre_cuidador]

        #################
        # FAM = JUGAR
        #################

        respuesta = (
            'respuesta',
            r'((a ver|creo es|es|esta) )?(?P<respuesta>(\w+)( \w+)*)'
        )
        fin_juego = (
            'fin_juego',
            r'no quiero seguir|finaliza(r)?|acaba(r)?|despues|para(r)?|abandon(o|ar)'
        )
        jugar_grs = [respuesta, fin_juego]

        ################
        # PREG_DEVELOP
        ################
        qualificacio = (
            'qualificacio',
            r'(?P<calidad>bien|mal|bueno|aceptable|excelente|pesimo)'
        )
        preg_develop_grs = [qualificacio]


        grs_lists = [general_grs, presentacion_grs, estado_salud_grs, entretenimiento_grs, diaria_grs,
                     buscar_grs, play_grs, llamar_grs, pill_grs, evento_grs, cuidador_grs, jugar_grs, preg_develop_grs]

        self.list_args_0 = [x.lower() for x, y in
                            entretenimiento0_grs + buscar0_grs + diaria0_grs + llamar0_grs + pres0_grs + evento0_grs]
        self.list_args_1 = [x.lower() for x, y in diaria1_grs + pres1_grs]
        for intent, gr in [gram for gr_list in grs_lists for gram in gr_list]:
            yield intent.lower(), re.compile(gr)

    def get_intent(self, text: str, frame: dict) -> bool:
        intents = self.domain_intents_list[frame['DOM']]
        intents_list = [(intent, self.grammars[intent]) for intent in intents]
        for intent, gr in intents_list:
            result = gr.search(text.lower())
            if result and 'INT' not in frame:
                dic = {k: v for k, v in result.groupdict().items() if v}
                if intent in self.list_args_0 and not dic:
                    frame['INT'] = intent + "_0"
                elif intent in self.list_args_1 and len(dic) == 1:
                    frame['INT'] = intent + "_1"
                    frame.update(dic)
                else:
                    frame['INT'] = intent
                    frame.update(dic)
                print("frame: ", frame)
                return True
        else:
            print(frame)
            return False
