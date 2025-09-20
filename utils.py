import os, sys
from datetime import datetime
import requests
from requests import Response
import json
import uuid



APPDATA_DIR = "."
USERDATA_DIR = "./"

DEFAULT_CONFIG = {
    "Resumen Diario": {
        "Weather": {"Enabled": True, "Location": "Ortuella"},
        "Jokes": {"Enabled": True, "Url": "https://naiel.fyi/chistes.txt"},
    },
    "Clave Proxy": str(uuid.uuid4()),
    "Receta": "No Disp.",
}


CONFIG = None
REQ_CACHE = {}

if hasattr(sys, "_MEIPASS"):
    APPDATA_DIR = os.path.join(sys._MEIPASS)
if os.environ.get("ISDOCKER") != None:
    USERDATA_DIR = os.environ.get("DATAPATH", "/data/")


# region Type Parsers
class DateParser:
    """Parser for ISO datetime strings"""

    LOCALE_DATE = {
        "DAY_OF_WEEK": (
            "Lunes",
            "Martes",
            "Miercoles",
            "Jueves",
            "Viernes",
            "Sabado",
            "Domingo",
        ),
        "MONTH": (
            "Enero",
            "Febrero",
            "Marzo",
            "Abril",
            "Mayo",
            "Junio",
            "Julio",
            "Agosto",
            "Septiembre",
            "Octubre",
            "Noviembre",
            "Diciembre",
        ),
        "FORMATS": {
            "Day": "{hdow} {day} de {hmonth} del {year}",
        },
    }

    def __init__(self, iso=None, locale: dict = LOCALE_DATE) -> None:
        """Parser for ISO datetime strings

        Args:
            iso (string, optional): Custom datetime, if not now. Defaults to None.
            locale (dict, optional): Custom locale config. Defaults to Spanish.
        """
        self.locale = locale
        if iso == None:
            self.dt = datetime.now()
        else:
            self.dt = datetime.fromisoformat(iso)

    def human_day(self):
        """Returns the day as a human format in the current locale

        Returns:
            string: Result in locale's format
        """
        hdow: str = self.locale["DAY_OF_WEEK"][self.dt.weekday()]
        hmonth: str = self.locale["MONTH"][self.dt.month - 1]
        format: str = self.locale["FORMATS"]["Day"]
        result: str = format.format(
            hdow=hdow,
            hmonth=hmonth,
            day=self.dt.day,
            month=self.dt.month,
            year=self.dt.year,
        )
        return result

    def pretty_time(self):
        """Returns the Time as a string in the HH:MM format.

        Returns:
            string: Result in HH:MM
        """
        result = f"{self.dt.hour:02d}:{self.dt.minute:02d}"
        return result

    def pretty_monthCode(self):
        """Returns the month as a string in the format YYYY-MM

        Returns:
            string: Result in YYYY-MM
        """
        result = f"{self.dt.year}-{self.dt.month:02d}"
        return result

    def pretty_dayCode(self):
        """Returns the day as a string in the format YYYY-MM-DD

        Returns:
            string: Result in YYYY-MM-DD
        """
        result = f"{self.dt.year}-{self.dt.month:02d}-{self.dt.day:02d}"
        return result


# endregion


def cached_request(name: str, *args, **kwargs):
    global REQ_CACHE
    if REQ_CACHE.get(name) != None:
        resp: Response = REQ_CACHE[name]
        return resp
    REQ_CACHE[name] = requests.get(*args, **kwargs)
    resp: Response = REQ_CACHE[name]
    return resp


def clear_cache():
    global REQ_CACHE
    REQ_CACHE = {}


def get_config():
    global CONFIG
    if not os.path.exists(USERDATA_DIR + "config.json"):
        json.dump(DEFAULT_CONFIG, open(USERDATA_DIR + "config.json", "w"))
    CONFIG = json.load(open(USERDATA_DIR + "config.json", "r"))
    return CONFIG

def set_config(setconf):
    global CONFIG
    json.dump(setconf, open(USERDATA_DIR + "config.json", "w"))
    CONFIG = json.load(open(USERDATA_DIR + "config.json", "r"))
    return CONFIG

def check_path(path):
    if not os.path.isdir(path):
        os.mkdir(path)

def pysonsort(dic: dict, keyToSort: str, reverse: bool = False):
    r = sorted(dic.items(), key=lambda x:x[1][keyToSort], reverse=reverse)
    return dict(r)

