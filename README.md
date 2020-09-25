# geriatric-assistant
Geriatric Assistant: A personal intelligent virtual assistant for old people.
Using NLP for creating the chatbot.

Links d'interès (development):

- SpeechRecognition -> https://pypi.org/project/SpeechRecognition/
- CMUSphinx -> https://cmusphinx.github.io/wiki/
- CMUSphinx downloads -> https://sourceforge.net/projects/cmusphinx/files/
- Kaldi android -> https://github.com/alphacep/kaldi-android-demo
- vosk-api -> https://github.com/alphacep/vosk-api
- Audio in python -> https://realpython.com/playing-and-recording-sound-python/
- Stream audio/video pafy -> https://pythonhosted.org/pafy/
- Rhasspy -> https://rhasspy.readthedocs.io/en/latest/
- google weather -> https://www.thepythoncode.com/article/extract-weather-data-python
- TTS català -> https://collectivat.cat/blog/2019-12-05-sintesi-de-la-parla-xxnn/


**INTENTS**

De moment està fet en castellà.
    No he fet servir accents, i a més fa el reconeixement del text
    previament passat a minuscules per tant és case insensitive.
    Estan dividits per dominis (no són definitius, depèn de les funcionalitats finals)
    
    DOM = GENERAL (preguntes relecionades amb informació o tracte amb el bot)
    
    - COMO TE LLAMAS: ej. ¿como te llamas?
    - SALUDO: ej. Buenos dias
    - DESPEDIDA: ej. Hasta luego
    - COMO ESTAS: ej. ¿como estas?
    - CUANTOS AÑOS: ej. ¿cuantos años tienes?
    - REPETIR: ej. ¿perdona, podrías repetirlo?
    
    DOM = PRESENTACION (frases d'informació general de l'usuari, previsiblement
                        necessaries només en una fase de primer o primers contactes.
                        Possiblement també preguntes per fer de tant en tant i anar
                        obtenint més informació personal seva, ej. fills,etc.)
    
    - NOM: ej. me llamo Oriol
    - AÑOS: ej. tengo 22 años
    
    
    DOM = ESTADO SALUD (frases d'informació sobre l'estat de salut de l'usuari
                        un dels dominis prioritaris)
    
    - ESTADO SALUD BIEN: ej. estoy muy bien
    - ESTADO SALUD MAL: ej. estoy un poco triste
    
    DOM = ENTRETENIMIENTO (preguntes, frases per activar funcions per entretenir a
                           l'usuari. Totes les funcions tindran un exemple com a minim
                           per a poder provar-la)
    
    - PREG ENTRETENER: ej. ¿puedes contarme algo?
    - CONTAR ADIVINANZA: ej. ¿podrias leerme una adivinanza?
    - CONTAR CUENTO: ej. me gustaria que me leyeras una narracion
    - CONTAR CHISTE: ej. cuentame un chiste
    - ESCUCHAR CANCION: ej. ponme una cancion de Los Rolling Stones
    - JUGAR: ej. ¿jugamos a algo?
    
    
    DOM = DIARIA (preguntes sobre informació diària. i.e hora, dia, temps, etc)
    
    - DIA: ej. ¿qué día es hoy?
    - HORA: ej. ¿puedes decirme la hora?
    - TIEMPO: ej. ¿qué prevision hay para mañana?
    
    
    DOM = BUSCAR (buscar a google informació o imatges i ubicacions al maps)
    
    - BUSCAR IMAGEN: ej. ¿Me puedes enseñar fotos de Francia?
    - BUSCAR LOCALIZACION: ej. ¿dónde está Barcelona?
    - BUSCAR: ej. quiero saber cuál es la capital de Italia
    
    
    DOM = LLAMAR (trucar a un familiar/amic) # working on
    
    DOM = AGENDA (controlar agenda, events, medicaments, horaris) # working on

    

**TODO**
- more intent functions and their responses/answers
- clarification, confirmation, rejection, simple grounding