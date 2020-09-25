#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author: Oriol Aranda

#################################
# ********* UTILITIES **********
#################################

"""
Module containing some useful functions for the AnswerGenerator module and for the DialogManager module
"""

import speech_recognition as sr
import pandas as pd
import unicodedata
import webbrowser
import requests
import random
import json
import pafy
import re
from datetime import datetime, timedelta
from urllib.parse import urlencode
from bs4 import BeautifulSoup as bs
from time import sleep

from googletrans import Translator
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from youtubesearchpython import SearchVideos


def load_json(path):
    with open(path) as json_file:
        return json.load(json_file)


def load_stories():
    headers = ['title', 'author', 'year', 'public_domain', 'category', 'link']
    interest = ['title', 'author', 'category', 'link']
    stories = pd.read_csv('../assistant/data/stories_es.csv', sep=',', quotechar='"', encoding='utf8', names=headers, header=0)
    return {k: v for k, v in zip(interest, stories[interest].transpose().values.tolist())}


def stories_selection(stories):
    choices = list(range(len(stories['title'])))
    titles = [stories['title'][i] + ' de ' + stories['author'][i] for i in random.sample(choices, 5)]
    return titles


def load_jokes(read_jokes):
    f = open('../assistant/data/jokes_es.txt')
    jokes = {k: v.strip() for k, v in enumerate(f.readlines()) if k not in read_jokes}
    f.close()
    return jokes


def select_joke(jokes):
    i_joke = random.choice(list(jokes.keys()))
    return i_joke, jokes[i_joke]


def load_riddles(read_riddles):
    headers = ['pregunta', 'solucion', 'acierta', 'ayuda', 'pide_solucion', 'dificultad', 'temas']
    selected = ['pregunta', 'solucion', 'acierta', 'ayuda', 'pide_solucion']
    riddles = pd.read_csv('../assistant/data/riddles_es.csv', sep=',', quotechar='"', encoding='utf8', names=selected, header=0)
    riddles = {k: v for k, v in enumerate(riddles[selected].values.tolist()) if k not in read_riddles}

    return riddles


def select_riddle(profile, riddles):
    if profile['riddles']['actual'] < 0:
        profile['riddles']['actual'] = random.choice(list(riddles.keys()))
    return riddles[profile['riddles']['actual']][0]


def intent_info(profile):
    events = [shave_accents(x) for _, el in profile['events']['info'].items() for x in el]
    return {"carers": profile['carers'], "events": events}


def date(day='dia', delay='hoy'):
    now = datetime.now()
    if delay == 'mañana':
        now = now + timedelta(days=1)
    if day == 'dia':
        months = ("Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto",
                  "Septiembre", "Octubre", "Noviembre", "Diciembre")
        semana = ("lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo")
        wk_day, day, month, year = now.isoweekday(), now.day, months[now.month - 1], now.year
        return f'{semana[wk_day - 1]} {day} de {month} de {year}'
    if day == 'hora':
        article = "la" if now.hour == 1 else "las"
        return f'Són {article} {now.strftime("%H:%M")}'


def get_weather_data(url):
    USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36"
    # US english
    LANGUAGE = "es-ES,es;q=0.5"
    session = requests.Session()
    session.headers['User-Agent'] = USER_AGENT
    session.headers['Accept-Language'] = LANGUAGE
    session.headers['Content-Language'] = LANGUAGE
    html = session.get(url)
    # create a new soup
    soup = bs(html.text, "html.parser")
    # store all results on this dictionary
    result = {'region': soup.find("div", attrs={"id": "wob_loc"}).text,
              'temp_now': soup.find("span", attrs={"id": "wob_tm"}).text,
              'weather_now': soup.find("span", attrs={"id": "wob_dc"}).text.lower(),  # get actual weather
              'precipitation': soup.find("span", attrs={"id": "wob_pp"}).text,
              'humidity': soup.find("span", attrs={"id": "wob_hm"}).text,
              'wind': soup.find("span", attrs={"id": "wob_ws"}).text}
    # get next few days' weather
    next_days = []
    days = soup.find("div", attrs={"id": "wob_dp"})
    for day in days.findAll("div", attrs={"class": "wob_df"}):
        # extract the name of the day
        # day_name = day.find("div", attrs={"class": "vk_lgy"}).attrs['aria-label']
        day_name = day.find("div", attrs={"class": "QrNVmd"}).attrs['aria-label']
        # get weather status for that day
        weather = day.find("img").attrs["alt"].lower()
        temp = day.findAll("span", {"class": "wob_t"})
        # maximum temparature in Celsius, use temp[1].text if you want fahrenheit
        max_temp = temp[0].text
        # minimum temparature in Celsius, use temp[3].text if you want fahrenheit
        min_temp = temp[2].text
        next_days.append({"name": day_name, "weather": weather, "max_temp": max_temp, "min_temp": min_temp})
    # append to result
    result['next_days'] = next_days
    return result


def weather(day='hoy', location="castellar del vallès", verbose=False):
    URL = "https://www.google.com/search?lr=lang_es&ie=UTF-8&"
    URL += urlencode({'q': "tiempo " + location})
    data = get_weather_data(URL)
    if day == 'hoy':
        if verbose:
            print("Tiempo actual para:", data["region"])
            print(f"Temperatura: {data['temp_now']}°C")
            print("Descripción:", data['weather_now'])
            print("Precipitación:", data["precipitation"])
            print("Humedad:", data["humidity"])
            print("Viento:", data["wind"])
        return f"Hoy, en {data['region']} tenemos un día {data['weather_now']}. Ahora hay {data['temp_now']} " \
               f"grados y una probabilidad del {data['precipitation']} de que llueva. Un viento de {data['wind']} y " \
               f"una humedad del {data['humidity']}."
    if day == 'mañana':
        dayweather = data["next_days"][0]
        if verbose:
            print("Tiempo para mañana en:", data["region"])
            print("Descripción:", dayweather['weather'])
            print(f"Temperatura máxima: {dayweather['max_temp']}°C")
            print(f"Temperatura mínima: {dayweather['min_temp']}°C")
        return f"Mañana, según veo en la predicción para {data['region']}, tendremos {dayweather['weather']}, con " \
               f"una temperatura máxima de {dayweather['max_temp']} grados y una mínima de {dayweather['min_temp']} grados."
    if day == 'semana':
        hm = ['hoy', 'mañana']
        text = f"La previsión de esta semana en {data['region']} es esta:"
        last = len(data['next_days']) - 1
        for i, dayweather in enumerate(data["next_days"]):
            if i == last:
                text += f" y el {dayweather['name']} {dayweather['weather']}. Eso es todo, a ver si no fallan esta vez!"
            elif i in [0, 1]:
                text += f"{hm[i]} {dayweather['weather']},"
            else:
                text += f" el {dayweather['name']} {dayweather['weather']},"
            if verbose:
                print("====", dayweather["name"], "====")
                print("Descripción:", dayweather["weather"])
                print(f"Temperatura máxima: {dayweather['max_temp']}°C")
                print(f"Temperatura mínima: {dayweather['min_temp']}°C")
        return text


def play_music(player, music):
    search = SearchVideos(music, offset=1, mode='dict', max_results=2)
    url_video = search.result()['search_result'][0]['link']
    url_video_ = search.result()['search_result'][1]['link']
    try:
        video = pafy.new(url_video)
        stream_audio = video.getbestaudio()
    except:
        video = pafy.new(url_video_)
        stream_audio = video.getbestaudio()
    # filename = stream_audio.download(filepath='/tmp/name.'+stream_audio.extension)
    stream_audio_url = stream_audio.url_https
    player.set_mrl(stream_audio_url, ":no-video")  # Set player media


def play_youtube_music(music):
    _path = '../env/lib/python3.6/site-packages/selenium/bin_log_webdriver/firefox'
    driver = webdriver.Firefox(executable_path=f'{_path}/geckodriver', 
                               service_log_path=f'{_path}/geckodriver.log')
    driver.maximize_window()

    wait = WebDriverWait(driver, 5)
    presence = EC.presence_of_element_located
    visible = EC.visibility_of_element_located

    # Navigate to url with video being appended to search_query
    driver.get("https://music.youtube.com/search?q=" + music)

    # play the video

    # wait.until(visible((By.ID, "video-title")))
    # driver.find_element_by_id("video-title").click()
    selector = 'ytmusic-shelf-renderer.style-scope:nth-child(1) > div:nth-child(4) > ytmusic-responsive-list-item-renderer:nth-child(1) > div:nth-child(2) > ytmusic-item-thumbnail-overlay-renderer:nth-child(5) > div:nth-child(2) > ytmusic-play-button-renderer:nth-child(1) > div:nth-child(1) > yt-icon:nth-child(1)'
    wait.until(visible((By.CSS_SELECTOR, selector)))
    driver.find_element_by_css_selector(selector).click()


def play_story(player, url_video, time):
    try:
        video = pafy.new(url_video)
        stream_audio = video.getbestaudio()
    except:
        print("video not available")
        # filename = stream_audio.download(filepath='/tmp/name.'+stream_audio.extension)
    else:
        stream_audio_url = stream_audio.url_https
        player.set_mrl(stream_audio_url, ":no-video")
        player.play()
        sleep(0.1)
        player.set_time(time)


def play_youtube_story(link):
    _path = '../env/lib/python3.6/site-packages/selenium/bin_log_webdriver/firefox'
    driver = webdriver.Firefox(executable_path=f'{_path}/geckodriver', 
                               service_log_path=f'{_path}/geckodriver.log')
    driver.maximize_window()
    wait = WebDriverWait(driver, 3)
    visible = EC.visibility_of_element_located
    # Navigate to url with video being appended to search_query
    driver.get(link)
    selector = '.ytp-large-play-button'
    wait.until(visible((By.CSS_SELECTOR, selector)))
    driver.find_element_by_css_selector(selector).click()  # play video


def find_story(stories, story):
    titles = stories['title']
    authors = stories['author']
    categories = stories['category']
    for i, tac in enumerate(zip(titles, authors, categories)):
        t_, a_, c_ = (shave_accents(x.lower()) for x in tac)
        if story in t_ or story in a_ or story in c_:
            return t_, stories['link'][i]
    return "", None


def search(text):
    # search_results = google.search("cual es la capital de nicaragua", lang='es')
    url = 'https://google.com/search?q=' + text
    webbrowser.get().open(url)


def search_images(img):
    url = 'https://google.com/search?q=' + img + '&tbm=isch' + '&tbs=isz:l'
    webbrowser.get().open(url)


def search_location(location):
    url = 'https://google.es/maps/search/' + location.title() + ",+Barcelona" + '/&amp;'
    webbrowser.get().open(url)


def found_contact(contacts, contact_num, contact_name, contact_status):
    filtered_status, filtered_name, filtered_num = set(), set(), set()
    dif_status_name, dif_name_num, dif_status_num = set(), set(), set()
    if contact_status:
        filtered_status = set(
            (nom, apodo, status, num) for nom, apodo, status, num in contacts if contact_status == status)
    if contact_name:
        filtered_name = set((nom, apodo, status, num) for nom, apodo, status, num in contacts if
                            (contact_name in nom.lower()) or (contact_name in apodo.lower()))
    if contact_num:
        filtered_num = set((nom, apodo, status, num) for nom, apodo, status, num in contacts if contact_num == num)

    dif_status_name = filtered_status & filtered_name
    dif_name_num = filtered_name & filtered_num
    dif_status_num = filtered_status & filtered_num
    dif_status_name_num = dif_status_name & filtered_num
    filtered_list = [filtered_status, filtered_name, filtered_num, dif_status_name, dif_name_num, dif_status_num,
                     dif_status_name_num]

    filtered = sorted([x for x in filtered_list if len(x) != 0], key=lambda x: len(x), reverse=False)
    if len(filtered) == 0:
        return False, set()
    tipus = list(filtered[0])[0][2]
    if len(filtered[0]) == 1:
        return tipus, list(filtered[0])
    if all(1 for x in list(filtered[0]) if tipus == x[2]):
        return tipus, list(filtered[0])
    return False, list(filtered[0])


def get_pills(pastilla, pills):
    semana = ("lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo")

    def cantidad(qnt, color=""):
        dc = {1: "una", 2: "dos", 3: "tres", 4: "cuatro", "cinco": 5, "seis": 6}
        plural = {"roja": "rojas", "verde": "verdes", "azul": "azules"}
        quant = dc[qnt]
        quant += " pastilla" if qnt == 1 else " pastillas"
        if color:
            quant += " " + (color if qnt == 1 else plural[color])
        return quant

    if pastilla:
        id, day_list = None, None
        for k, v in pills['pills_id'].items():
            if pastilla in v[0].lower() or pastilla in v[1].lower():
                id, day_list = (k, v[0], v[1]), v[2]
                break
        if id:
            days = [(semana[int(day)], pills['schedule'][day][id[0]]) for day in day_list]
            resp = ". ".join(
                [f"el {day}: " + ", ".join([f"{cantidad(qnt)} a las {hr}" for qnt, hr in xs]) for day, xs in days])
            return f"La pastilla {id[2]} ({id[1]}) tienes que tomarla: " + resp
    now = datetime.now()
    local_now = now.strftime('%H:%M')
    day = now.isoweekday()
    filtered = [(pills['pills_id'][k][:2], vi) for k, v in pills['schedule'][str(day - 1)].items() for vi in v if
                vi[1] > local_now]
    filtered.sort(key=lambda x: x[1][1], reverse=False)
    if filtered:
        return "Hoy tienes que tomarte: " + ", ".join(
            [f"{cantidad(qnt, color)} ({nom}) a las {hr}" for [nom, color], [qnt, hr] in filtered])
    return "Hoy no tienes que tomarte ninguna pastilla"


def get_alarm_time(hora, horario):
    now = datetime.now()
    if len(hora) in [1, 2]:
        h0, h1 = hora, '00'
    else:
        h0, h1 = hora.split(':')
    if horario in ['pm', 'tarde', 'noche'] and int(h0) < 12:
        h0 = (int(h0) + 12) % 24
    elif int(h0) == 12:
        h0 = int(h0)
    alarm = datetime(day=now.day, month=now.month, year=now.year, hour=int(h0), minute=int(h1), second=now.second)
    if alarm < now:
        alarm += timedelta(days=1)
    dif = str(alarm - now).split('.')[0]
    h, m, s = re.split(':', dif)
    return alarm.strftime('%H:%M'), f"He puesto una alarma a las {alarm.strftime('%H:%M')}. " \
                                    f"Va a sonar en {h} horas {m} minutos."


def carer_date(carer, name, day, hora=True):
    reverse_names = {v.lower(): k for k, v in carer['names'].items()}

    def horas_rango(x):
        return f"de {x[0]} a {x[1]}"

    def articulo(x):
        return f"el {x}" if x not in ["hoy", "mañana"] else f"{x}"

    semana = ("lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo")
    day_num = {k: str(v) for v, k in enumerate(semana)}
    hoy = datetime.now().isoweekday() - 1
    dia_resp = {v: k for k, v in day_num.items()}
    dia_resp.update({str(hoy): "hoy", str(hoy + 1): "mañana"})
    if hora:
        if day in ['hoy', 'mañana']:
            day = str(hoy) if day == "hoy" else str(hoy + 1)
        elif day in semana:
            day = day_num[day]
        else:
            day = False
        if day in carer['schedule']:  # prioritat al dia
            if name in reverse_names:
                try:
                    [h1, h2] = carer['schedule'][day][reverse_names[name]]
                    return f"{articulo(dia_resp[day]).title()} a {name.title()} le toca venir de {h1} a {h2}"
                except KeyError:
                    resp = f"{dia_resp[day].title()} {name.title()} no viene! "
                    h_c = carer['schedule'][day].items()
                    if h_c:
                        resp += "Vienen " if len(h_c) > 1 else "Viene "
                        resp += "y ".join([f"{carer['names'][nom]} {horas_rango(horas)}" for nom, horas in h_c])
                    return resp
            else:
                resp = f"{dia_resp[day].title()}"
                h_c = carer['schedule'][day].items()
                if h_c:
                    resp += " van a venir" if len(h_c) > 1 else " va a venir "
                    resp += list_elem([f"{carer['names'][nom]} {horas_rango(horas)}" for nom, horas in h_c])
                return resp
        else:  # no tenim dia
            if name in reverse_names:  # tenim nom cuidador
                k = reverse_names[name]
                dias_ = carer['days'][k][hoy:] + carer['days'][k][:hoy]
                return list_elem([f"{articulo(dia_resp[i])} {horas_rango(carer['schedule'][i][k])}" for i in dias_])
            else:
                aux = [carer['names'][k] + " viene " + list_elem(
                    [f"{articulo(dia_resp[vi])} {horas_rango(carer['schedule'][vi][k])}" for vi in v])
                       for k, v in carer['days'].items()]
            return ". ".join(aux)
    else:  # demana dies del cuidador no hores
        if name in reverse_names:
            dias_ = [articulo(dia_resp[d]) for d in carer['days'][reverse_names[name]]]
            return f"{name.title()} viene {list_elem(dias_[hoy:] + dias_[:hoy])}."
        else:
            return ". ".join([f"{carer['names'][n].title()} va a venir {list_elem([articulo(dia_resp[x]) for x in d])}"
                              for n, d in carer['days'].items()])


def date_event(events, event):
    months = ("Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto",
              "Septiembre", "Octubre", "Noviembre", "Diciembre")
    semana = ("lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo")

    # retorna articulo + dia de la semana ("hoy" o "mañana" si es necesario tambien)
    def day_str(num_day):
        hoy = datetime.now().isoweekday() - 1
        dia_resp = {str(k): v for k, v in enumerate(semana)}
        dia_resp.update({str(hoy): "hoy", str(hoy + 1): "mañana"})
        day = dia_resp[num_day]
        return f"{'el ' if day not in ['hoy', 'mañana'] else ''}{day}"

    # retorna {dia_semana} {num_dia} de {mes}
    def fecha_evento(day, month, year):
        dia = datetime(day=day, month=month, year=year).isoweekday() - 1
        return f"{day_str(str(dia))} {day} de {months[month - 1]}"

    reverse_events = {shave_accents(vi): k for k, v in events['info'].items() for vi in v}
    if event in reverse_events:
        event = reverse_events[event]
        res_events = [x for x in events['schedule'] if x[0] == event]
        if len(res_events) < 1:
            return f"No he encontrado ningún evento de {events['info'][event][0]} en tu agenda."
        return f"Tienes {events['info'][event][0]} " + list_elem([f"{fecha_evento(*x[2:5])} a las {x[5]} en {x[1]} "
                                                                  for x in res_events])
    return "¡Lo siento, no he encontrado información sobre este evento!"


def game_level(words: list, level: list) -> list:
    i = random.choice(words)
    while i in level:
        i = random.choice(words)
    level.append(i)
    return level


def eq_seqs(a: list, b: list) -> bool:
    if len(a) != len(b):
        return False
    return all(map(lambda x, y: x == shave_accents(y.lower()), a, b))


def record_mic():
    """Record audio from the mic, return AudioData type"""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)
        return audio


def translation():
    """Translate from language to spanish"""
    translator = Translator()

    def traduir(text, src='auto', dest='es'):
        try:
            trans_text = translator.translate(text, src=src, dest=dest).text
        except BaseException:
            raise
        return trans_text

    return traduir


def shave_accents(string, accents=('COMBINING ACUTE ACCENT', 'COMBINING GRAVE ACCENT')):
    accents = set(map(unicodedata.lookup, accents))
    chars = [c for c in unicodedata.normalize('NFD', string) if c not in accents]
    return unicodedata.normalize('NFC', ''.join(chars))


def list_elem(ls: list) -> str:
    if len(ls) > 1:
        return ", ".join(ls[:-1]) + " y " + str(ls[-1])
    return "" if len(ls) < 1 else str(ls[0])


def eval_regex(sent, expr):
    result = re.search(expr, sent)
    if result:
        return True
    else:
        return None
