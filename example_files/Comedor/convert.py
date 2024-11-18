import yaml
from datetime import datetime

_SCHEME = {
    "<date>": {
        "<menu>": {
            "TXT1": "<P1 TXT>",
            "IMG1": "<P1 IMG>",
            "TXT2": "<P2 TXT>",
            "IMG2": "<P2 IMG>",
            "TXT3": "<P3 TXT>",
            "IMG3": "<P3 IMG>",
            "STAT": "Suficiente|Poca"
        }
    }
}

e: dict = yaml.safe_load(open("in.yml"))
now = datetime.now()
MONT = input("Mes  > ")
MENU = input("Menu > ")
out = f"""Origin;Menu;YYYY-MM;Description;Link
EuskadiTech(TM);{MENU};{MONT};Menu {MENU}, Mes {MONT};https://tech.eus
---
YYYY-MM-DD;P1 Text;P1 Img;P2 Text;P2 Img;P3 Text;P3 Img;IsEnought\n"""
COUNT = 0
for key, value in e.items():
    COUNT += 1
    stat = "OK"
    if value[MENU].get("STAT", "Suficiente") != "Suficiente":
        stat = "KO"
    out += (
        key
        + ";"
        + value[MENU].get("TXT1", "")
        + ";"
        + value[MENU].get("IMG1", "")
        + ";"
        + value[MENU].get("TXT2", "")
        + ";"
        + value[MENU].get("IMG2", "")
        + ";"
        + value[MENU].get("TXT3", "")
        + ";"
        + value[MENU].get("IMG3", "")
        + ";"
        + stat
        + "\n"
    )
print("Elementos creados correctamente:", COUNT)
with open(f"Menu {MENU} del mes {MONT}.axl", "w") as f:
    f.write(out)
