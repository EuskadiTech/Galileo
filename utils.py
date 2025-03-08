import os, sys
from datetime import datetime
import requests
from requests import Response
import json
from time import sleep
import subprocess
import uuid
from threading import Event, Thread
import webbrowser



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
#region Tunnels
class PinggyTunnel:
    # TODO: Implement https://ssi.sh/ as a tunnel
    TUNNEL = None
    TIMEOUT_TUNNEL = 3000 # 50 min
    TIMEOUT_CACHE = 900 # 15 min
    TRIGGER = Event()
    def __init__(self):
        pass
    
    def loop(self):
        TIMER_TUNNEL = 0
        TIMER_CACHE = 0
        while True:
            TIMER_TUNNEL += 1
            TIMER_CACHE += 1
            if self.TRIGGER.is_set():
                break
            if self.TUNNEL == None:
                self.start_ssh_tunnel()
            if TIMER_TUNNEL > self.TIMEOUT_TUNNEL:
                print(">> Recargando Tunel SSH")
                try:
                    self.stop_ssh_tunnel()
                    TIMER_TUNNEL = 0
                    sleep(1)
                    self.start_ssh_tunnel()
                except:
                    print("D] No se ha podido recargar el Tunel SSH")
            try:
                requests.get("http://127.0.0.1:11129/urls").json().get("urls")[-1]
            except:
                try:
                    print(">> Recargando Tunel SSH por fallo")
                    self.stop_ssh_tunnel()
                    TIMER_TUNNEL = 0
                    sleep(1)
                    self.start_ssh_tunnel()
                    sleep(3)
                except:
                    print("D] No se ha podido recargar el Tunel SSH")
            if TIMER_CACHE > self.TIMEOUT_CACHE:
                print(">> Vaciando Cache HTTP")
                TIMER_CACHE = 0
                clear_cache()
            sleep(1)
    
    def start(self):
        config = get_config()
        self.thread = Thread(target=self.loop)
        self.thread.start()
        try:
            if getattr(sys, "frozen", False):
                webbrowser.open_new_tab("http://127.0.0.1:8129")
        except:
            print("[D] No se ha podido iniciar el navegador web.")
        return "https://grp.naiel.fyi/rd/" + config["Clave Proxy"]
    
    def stop(self):
        self.TRIGGER.set()
        self.thread.join()
    
    def start_ssh_tunnel(self, retries: int = 10):
        cmd = f"ssh -p 443 -L11129:127.0.0.1:4300 -o StrictHostKeyChecking=no -o ServerAliveInterval=30 -t -R0:127.0.0.1:8129 force@a.pinggy.io x:https x:xff x:fullurl"
        print(" > Arrancando Tunel SSH")
        self.TUNNEL = subprocess.Popen(
            cmd.split(" "),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
        )
        TUNNEL_URLS = []
        for i in range(0, retries):
            try:
                TUNNEL_URLS.append(
                    requests.get("http://127.0.0.1:11129/urls").json().get("urls")[-1]
                )
                print(" > Tunel SSH Disponible")
                break
            except:
                sleep(3)
        config = get_config()
        oti = "ETRP No Disp."
        if config.get("Clave Proxy") != None:
            oti = requests.post(
                "https://grp.naiel.fyi/__rp/publish",
                json={"conid": config["Clave Proxy"], "baseurl": TUNNEL_URLS[0]},
            ).json()["url"]
        TUNNEL_URLS.append(oti)
        return TUNNEL_URLS

    def stop_ssh_tunnel(self):
        try:
            self.TUNNEL.terminate()
            self.TUNNEL.kill()
            self.TUNNEL = None
        except:
            pass

class DirectTunnel:
    """Use this tunnel if Orch can connect to the server directly"""
    TIMEOUT_TUNNEL = 3000 # 50 min
    TIMEOUT_CACHE = 900 # 15 min
    TRIGGER = Event()
    def __init__(self, myurl: str, orchurl: str):
        self.orchurl = orchurl
        self.myurl = myurl
    
    def loop(self):
        TIMER_CACHE = 0
        self.start_ssh_tunnel()
        while True:
            TIMER_CACHE += 1
            if self.TRIGGER.is_set():
                break
            if TIMER_CACHE > self.TIMEOUT_CACHE:
                print(">> Vaciando Cache HTTP")
                TIMER_CACHE = 0
                clear_cache()
            sleep(1)
    
    def start(self):
        config = get_config()
        self.thread = Thread(target=self.loop)
        self.thread.start()
        try:
            if getattr(sys, "frozen", False):
                webbrowser.open_new_tab("http://127.0.0.1:8129")
        except:
            print("[D] No se ha podido iniciar el navegador web.")
        return self.orchurl + "/rd/" + config["Clave Proxy"]
    
    def stop(self):
        self.TRIGGER.set()
        self.thread.join()
    
    def start_ssh_tunnel(self, retries: int = 10):
        TUNNEL_URLS = ["", ""]
        config = get_config()
        oti = "ETRP No Disp."
        if config.get("Clave Proxy") != None:
            oti = requests.post(
                self.orchurl + "/__rp/publish",
                json={"conid": config["Clave Proxy"], "baseurl": self.myurl},
            ).json()["url"]
        TUNNEL_URLS.append(oti)
        return TUNNEL_URLS

    def stop_ssh_tunnel(self):
        pass
#endregion
