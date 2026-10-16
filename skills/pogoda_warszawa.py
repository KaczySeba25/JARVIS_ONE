"""Skill: pogoda_warszawa
Skrypt pobierający aktualną pogodę w Warszawie (opis: zwraca warunek i temperaturę, np. "Clear +15°C")
"""
import requests

URL = 'https://wttr.in/Warsaw?format=%C+%t'


def run():
    try:
        r = requests.get(URL, timeout=10)
        r.raise_for_status()
        return r.text.strip()[:2000]
    except Exception as e:
        return 'Blad pobierania: ' + str(e)
