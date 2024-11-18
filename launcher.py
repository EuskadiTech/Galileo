import platform
import requests
import os

OS = platform.system()
BASE_URL = "https://github.com/EuskadiTech/Galileo/releases/latest/download/"
EXE_NAME = ""

if OS == "Windows":
    EXE_NAME = "G-Serv.exe"

def get_online_version():
    req = requests.get(BASE_URL + "version.txt")
    return req.text

def get_local_version():
    if not os.path.exists("version.txt"):
        with open("version.txt", "w") as f:
            f.write("v0.0.0")
    with open("version.txt", "r") as f:
        return f.read()

def update(new_version):
    req = requests.get(BASE_URL + EXE_NAME)
    with open(EXE_NAME, "wb") as exe:
        exe.write(req.content)
    with open("version.txt", "w") as f:
        f.write(new_version)
    return True

def launch():
    os.system(EXE_NAME)

if __name__=="__main__":
    try:
        ver = get_online_version()
        latest = get_online_version().replace("v", "").split(".")
        current = get_local_version().replace("v", "").split(".")

        diff_mayor = int(latest[0]) - int(current[0])
        diff_minor = int(latest[1]) - int(current[1])
        diff_patch = int(latest[2]) - int(current[2])

        if diff_mayor != 0:
            update(ver)
        if diff_minor != 0:
            update(ver)
        if diff_patch != 0:
            update(ver)
        if not os.path.exists(EXE_NAME):
            update(ver)
    except:
        pass
    launch()