import os, sys
from datetime import datetime
import requests
from requests import Response
import json
import time
import subprocess
import uuid

APPDATA_DIR = "."
USERDATA_DIR = "./"

DEFAULT_CONFIG = {
    "Resumen Diario": {
        "Weather": {"Enabled": True, "Location": "Ortuella"},
        "Jokes": {"Enabled": True, "Url": "https://naiel.fyi/chistes.txt"},
    },
    "Clave Proxy": str(uuid.uuid4()),
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
        if iso == None:
            self.dt = datetime.now()
        else:
            self.dt = datetime.fromisoformat(iso)

    def human_day(self):
        """Returns the day as a human format in the current locale

        Returns:
            string: Result in locale's format
        """
        hdow: str = self.LOCALE_DATE["DAY_OF_WEEK"][self.dt.weekday()]
        hmonth: str = self.LOCALE_DATE["MONTH"][self.dt.month - 1]
        format: str = self.LOCALE_DATE["FORMATS"]["Day"]
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
        result = f"{self.dt.hour}:{self.dt.minute}"
        return result

    def pretty_monthCode(self):
        """Returns the month as a string in the format YYYY-MM

        Returns:
            string: Result in YYYY-MM
        """
        result = f"{self.dt.year}-{self.dt.month}"
        return result

    def pretty_dayCode(self):
        """Returns the day as a string in the format YYYY-MM-DD

        Returns:
            string: Result in YYYY-MM-DD
        """
        result = f"{self.dt.year}-{self.dt.month}-{self.dt.day}"
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


TUNNEL = None
TUNNEL_URLS = []


def start_tunnel(retries: int = 10):
    global TUNNEL
    if os.environ.get("ISDOCKER") != None:
        return ["", ""]
    cmd = f"ssh -p 443 -L11129:127.0.0.1:4300 -o StrictHostKeyChecking=no -o ServerAliveInterval=30 -t -R0:127.0.0.1:8129 force@a.pinggy.io x:https x:xff x:fullurl"
    print("> Arrancando Tunel SSH")
    TUNNEL = subprocess.Popen(
        cmd.split(" "),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        stdin=subprocess.DEVNULL,
    )
    for i in range(0, retries):
        try:
            global TUNNEL_URLS
            TUNNEL_URLS.append(
                requests.get("http://127.0.0.1:11129/urls").json().get("urls")[-1]
            )
            print("> Tunel SSH Disponible")
            break
        except:
            time.sleep(3)
    config = get_config()
    oti = "ETRP No Disp."
    if config.get("Clave Proxy") != None:
        oti = requests.post(
            "https://rp.tech.eus/__rp/publish",
            json={"conid": config["Clave Proxy"], "baseurl": TUNNEL_URLS[0]},
        ).json()["url"]
    TUNNEL_URLS.append(oti)
    return TUNNEL_URLS


def stop_tunnel():
    global TUNNEL
    try:
        TUNNEL.terminate()
        TUNNEL.kill()
    except:
        pass
