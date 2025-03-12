from flask import Blueprint, request, render_template
from utils import DateParser, get_config, cached_request
from random import choice
from ..Comedor.localutils import fromDay_comedor
from ..Cafe.views import get_receta
from ..Personas.localutils import with_auth
from ..Personas.models import DB_PERSONAS
from modules import addperm
app = Blueprint("ResumenDiario", __name__)


@app.route("/resumendiario", methods=["GET"])
@with_auth("resumendiario:_module")
def index():
    today = DateParser()
    data = {
        "Print": False,
        "PrintCols": "auto-fill",
        "Today": today.human_day(),
        "Time": today.pretty_time(),
        "Weather": {"Icon": "", "Text": "No disponible"},
        "Jokes": "",
        "Joke": "",
        "Comedor": fromDay_comedor(),
        "ComedorOKKO": {"OK": "suficiente", "KO": "poca"},
        "Receta": get_receta(),
        "NoticiasEuskadiTech": ""
    }
    config = get_config()
    if "print" in request.args.keys():
        data["Print"] = True
        data["PrintCols"] = "3"
    if config["Resumen Diario"]["Weather"]["Enabled"]:
        loc = config["Resumen Diario"]["Weather"]["Location"]
        data["Weather"]["Icon"] = cached_request(
            "resumen-diario:weather_icon", f"https://wttr.in/{loc}?lang=es&format=%c"
        ).text
        data["Weather"]["Text"] = cached_request(
            "resumen-diario:weather_text",
            f"https://wttr.in/{loc}?lang=es&format=%C<ul><li>Temperatura: %t</li><li>Viento: %w</li><li>Humedad: %h</li><li>Lluvia: %p</li></ul>",
        ).text

    if config["Resumen Diario"]["Jokes"]["Enabled"]:
        data["Jokes"] = cached_request(
            "resumen-diario:jokes", "http://127.0.0.1:8129/static/jokes.txt"
        ).text.split("\n")
        data["Joke"] = choice(data["Jokes"])

    def isFree(dat):
        if dat["Puntos"] >= 10:
            return True

    data["CafeFree"] = DB_PERSONAS.get_by_query(isFree).values()
    return render_template(
        "resumendiario/index.html", data=data, config=config["Resumen Diario"]
    )

addperm("Resumen Diario", "Acceder", "resumendiario:_module")