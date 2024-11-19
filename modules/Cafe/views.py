from flask import Blueprint, request, render_template, url_for, redirect
from ..Personas.models import DB_PERSONAS
import utils

app = Blueprint("Cafe", __name__)

def set_receta(receta):
    conf = utils.get_config()
    conf["Receta"] = receta
    utils.set_config(conf)

def get_receta():
    conf: dict = utils.get_config()
    return conf.get("Receta", "No Disp.")
ANILLAS = [
    {
        "name": "Salmón",
        "color": "#e89689",
        "text": "black"
    },
    {
        "name": "Rosa",
        "color": "#ba5961",
        "text": "black"
    },
    {
        "name": "Verde Claro",
        "color": "#96b3ad",
        "text": "black"
    },
    {
        "name": "Turquesa",
        "color": "#5bbdb3",
        "text": "black"
    },
    {
        "name": "Marrón",
        "color": "#403233",
        "text": "white"
    },
    {
        "name": "Blanco",
        "color": "white",
        "text": "black"
    },
    {
        "name": "Negro",
        "color": "black",
        "text": "white"
    },
    {
        "name": "Amarillo",
        "color": "#edde3b",
        "text": "black"
    },
    {
        "name": "Gris",
        "color": "gray",
        "text": "white"
    },
    {
        "name": "Rojo",
        "color": "#a81900",
        "text": "white"
    },
    {
        "name": "Rojo Oscuro",
        "color": "#610d14",
        "text": "white"
    }
]

@app.route("/cafe", methods=["GET"])
def index():
    return render_template(
        "cafe/index.html",
        Receta = get_receta()
    )
@app.route("/cafe/config", methods=["GET", "POST"])
def config():
    if request.method == "POST":
        set_receta(request.form["receta"])
        return redirect(url_for("Cafe.index"))
    return render_template(
        "cafe/config.html",
        Receta = get_receta()
    )

@app.route("/cafe/select", methods=["GET", "POST"])
def select():
    if request.method == "POST":
        def query(data):
            if data["Codigo"] == str(request.form["code"]):
                return True
        keys = list(DB_PERSONAS.get_by_query(query).keys())[0]
        return redirect(url_for("Cafe.comanda", rid=keys))
    return render_template(
        "cafe/select.html",
        personas = DB_PERSONAS.get_all()
    )

@app.route("/cafe/comanda/<rid>", methods=["GET", "POST"])
def comanda(rid):
    if request.method == "POST":
        def query(data):
            if data["Codigo"] == str(request.form["code"]):
                return True
        keys = list(DB_PERSONAS.get_by_query(query).keys())[0]
        return redirect(url_for("Cafe.comanda", rid=keys))
    return render_template(
        "cafe/comanda.html",
        personas = DB_PERSONAS.get_all(),
        anillas = ANILLAS,
        client = DB_PERSONAS.get_by_id(rid),
        Receta = get_receta()
    )
