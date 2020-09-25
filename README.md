# geriatric-assistant
Geriatric Assistant: An intelligent personal virtual assistant for elderly people.
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

Els intents estan fets amb gramàtiques regulars (regexp), en castellà. Tot i això, fent servir el google traductor, l'assistent hauria de ser funcional en múltiples idiomes: de moment català, castellà i anglès.

**FUNCIONALITATS**

Estan agrupades per families.

    FAM = PRESENTACION (frases d'informació general de l'usuari, previsiblement
                        necessaries només en una fase de primer o primers contactes)
    
    - NOM: ej. Me llamo Juan
    - AÑOS: ej. Tengo 90 años
    - SEXO: ej. Soy un hombre
    - LENGUA: ej. Hablo en castellano
    ...
    
    FAM = PREGUNTAS (Preguntes que fa el xatbot a l'usuari abans que aquest realitzi 
                     l'acció que volia)
    - PREGUNTA SALUD: ej. Bot: ¿Cómo te encuentras?
    - PREGUNTA INFO: ej. Bot: ¿Qué te pareció tu nuevo cuidador?


    FAM = GENERAL (preguntes relecionades amb informació o tracte amb el bot)
    
    - COMO TE LLAMAS: ej. ¿como te llamas?
    - SALUDO: ej. Buenos dias
    - DESPEDIDA: ej. Hasta luego
    - COMO ESTAS: ej. ¿como estas?
    - CUANTOS AÑOS: ej. ¿cuantos años tienes?
    - REPETIR: ej. ¿perdona, podrías repetirlo?
    
    
    FAM = ESTADO SALUD (frases d'informació sobre l'estat de salut de l'usuari
                        un dels dominis prioritaris)
    
    - ESTADO SALUD BIEN: ej. Estoy muy bien
    - ESTADO SALUD MAL: ej. Estoy un poco triste
    
    
    FAM = ENTRETENIMIENTO (preguntes, frases per activar funcions per entretenir a
                           l'usuari. Totes les funcions tindran un exemple com a minim
                           per a poder provar-la)
    
    - PREG ENTRETENER: ej. ¿Puedes contarme algo?
    - CONTAR ADIVINANZA: ej. ¿Podrias leerme una adivinanza?
    - CONTAR CUENTO: ej. Me gustaria que me leyeras una narracion
    - CONTAR CHISTE: ej. Cuentame un chiste
    - ESCUCHAR CANCION: ej. Ponme una cancion de Los Rolling Stones
    - JUEGO DE MEMORIA: ej. ¿Jugamos a algo?
    
    
    FAM = DIARIA (preguntes sobre informació diària. i.e hora, dia, temps, etc)
    
    - DIA: ej. ¿Qué día es hoy?
    - HORA: ej. ¿Puedes decirme la hora?
    - TIEMPO: ej. ¿Qué prevision hay para mañana?
    
    
    FAM = BUSCAR (buscar a google informació o imatges i ubicacions al maps)
    
    - BUSCAR IMAGEN: ej. ¿Me puedes enseñar fotos de Francia?
    - BUSCAR LOCALIZACION: ej. ¿Dónde está Barcelona?
    - BUSCAR: ej. Quiero saber cuál es la capital de Italia
    
    
    FAM = LLAMAR (trucar a un familiar/amic)
    - LLAMAR: ej. quiero llamar a mi hijo 
    
    
    FAM = CUIDADORES (informació rellevant del cuidador)
    - NOMBRE CUIDADOR: ej. ¿Cómo se llama el cuidador?
    - HORA CUIDADOR: ej. ¿A qué hora llega el cuidador hoy?
    - DIA CUIDADOR: ej. ¿Qué días viene el cuidador? o ¿Viene hoy el cuidador?
    
    
    FAM = DESPERTADOR (té un despertador, pots posar-lo/canviar-lo, activar-lo o desactivar-lo)
    - PONER ALARMA: ej. Quiero poner una alarma a las 8 de la mañana, por favor.
    - ACTIVAR ALARMA: ej. ¿Puedes activar la alarma?
    - DESACTIVAR ALARMA: ej. Quiero desactivar la alarma.

    FAM = RECORDATORIOS (recorda a quines hores t'has de prendre algun medicament o tens algun event)
    - MEDICAMENTOS: ej. ¿A qué hora tengo que tomarme el ibuprofeno?
    - EVENTOS: ej. ¿Qué día tengo médico?
    
 
