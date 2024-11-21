from flask import Blueprint, request, render_template, url_for, redirect
from ..Personas.models import DB_PERSONAS
import utils
from .models import DB_COMANDAS
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
        total = 10
        data = {
            "MetodoDePago": request.form.getlist("MetodoDePago"),
            "Anilla": request.form.getlist("Anilla"),
            "Tipo": request.form.getlist("Tipo"),
            "Cafeina": request.form.getlist("Cafeina"),
            "Complementos": request.form.getlist("Complementos"),
            "Tama_o": request.form.getlist("Tama_o"),
            "Leche": request.form.getlist("Leche"),
            "Temperatura": request.form.getlist("Temperatura"),
            "Endulzantes": request.form.getlist("Endulzantes"),
            "VarInfusion": request.form.get("VarInfusion"),
            "notas": request.form.get("notas"),
            "_persona": rid,
            "_grupo": "00 Sin Agrupar;white;black;",
            "_fase": "cocina"
        }
        if data["Tama_o"][0] == "Grande" and data["Leche"][0] != "Sin Leche":
            total += 20
        if data["Tama_o"][0] != "Grande" and data["Leche"][0] != "Sin Leche":
            total += 10
        if "Cafe" in data["Tipo"] or "Cafe Soluble" in data["Tipo"]:
            total += 10
        if "Receta del dia" in data["Complementos"]:
            total += 10
        data["_precio"] = total
        DB_COMANDAS.add(data)
        return redirect(url_for("Cafe.select"))
    return render_template(
        "cafe/comanda.html",
        personas = DB_PERSONAS.get_all(),
        anillas = ANILLAS,
        client = DB_PERSONAS.get_by_id(rid),
        Receta = get_receta(),
        last_comanda = {}
    )

@app.route("/cafe/cocina", methods=["GET", "POST"])
def cocina():
    # if request.method == "POST":
    #     data = {
    #         "MetodoDePago": request.form.getlist("MetodoDePago"),
    #         "Anilla": request.form.getlist("Anilla"),
    #         "Tipo": request.form.getlist("Tipo"),
    #         "Cafeina": request.form.getlist("Cafeina"),
    #         "Complementos": request.form.getlist("Complementos"),
    #         "Tama_o": request.form.getlist("Tama_o"),
    #         "Leche": request.form.getlist("Leche"),
    #         "Temperatura": request.form.getlist("Temperatura"),
    #         "Endulzantes": request.form.getlist("Endulzantes"),
    #         "VarInfusion": request.form.get("VarInfusion"),
    #         "notas": request.form.get("notas"),
    #     }
    #     DB_COMANDAS.add(data)
    #     return redirect(url_for("Cafe.select"))
    regiones = {}
    def query(data):
        if data["_fase"] == "cocina":
            return True
    for key, val in  DB_COMANDAS.get_by_query(query).items():
        persona = DB_PERSONAS.get_by_id(val["_persona"])
        if regiones.get(persona["Region"]) == None:
            regiones[persona["Region"]] = []
        regiones[persona["Region"]].append((key,val))
    return render_template(
        "cafe/cocina.html",
        personas = DB_PERSONAS.get_all(),
        Receta = get_receta(),
        comandas = DB_COMANDAS.get_by_query(query).items(),
        regiones=regiones
    )

@app.route("/cafe/pago", methods=["GET", "POST"])
def pago():
    # if request.method == "POST":
    #     data = {
    #         "MetodoDePago": request.form.getlist("MetodoDePago"),
    #         "Anilla": request.form.getlist("Anilla"),
    #         "Tipo": request.form.getlist("Tipo"),
    #         "Cafeina": request.form.getlist("Cafeina"),
    #         "Complementos": request.form.getlist("Complementos"),
    #         "Tama_o": request.form.getlist("Tama_o"),
    #         "Leche": request.form.getlist("Leche"),
    #         "Temperatura": request.form.getlist("Temperatura"),
    #         "Endulzantes": request.form.getlist("Endulzantes"),
    #         "VarInfusion": request.form.get("VarInfusion"),
    #         "notas": request.form.get("notas"),
    #     }
    #     DB_COMANDAS.add(data)
    #     return redirect(url_for("Cafe.select"))
    regiones = {}
    def query(data):
        if data["_fase"] == "pago":
            return True
    for key, val in  DB_COMANDAS.get_by_query(query).items():
        persona = DB_PERSONAS.get_by_id(val["_persona"])
        if regiones.get(persona["Region"]) == None:
            regiones[persona["Region"]] = []
        regiones[persona["Region"]].append((key,val))
    return render_template(
        "cafe/pago.html",
        personas = DB_PERSONAS.get_all(),
        Receta = get_receta(),
        comandas = DB_COMANDAS.get_by_query(query).items(),
        regiones=regiones
    )

@app.route("/cafe/updategrp", methods=["GET"])
def updategrp():
    DB_COMANDAS.update_by_id(request.args["f"], {"_grupo": request.args["v"]})
    return redirect(url_for("Cafe.cocina"))

@app.route("/cafe/del_cocina/<rid>", methods=["GET"])
def rdel(rid):
    DB_COMANDAS.update_by_id(rid, {"_fase": "pago"})
    return redirect(url_for("Cafe.cocina"))

@app.route("/cafe/del_pago/<rid>", methods=["GET"])
def rdel_pago(rid):
    com = DB_COMANDAS.get_by_id(rid)
    puntos = DB_PERSONAS.get_by_id(com["_persona"])["Puntos"]
    if com["MetodoDePago"][0] == "Efectivo":
        puntos += 1
    if com["MetodoDePago"][0] == "Puntos":
        puntos -= 10
    DB_PERSONAS.update_by_id(com["_persona"], {"Puntos": puntos})
    DB_COMANDAS.delete_by_id(rid)
    # DB_COMANDAS.update_by_id(rid, {"_fase": "_archive"})
    return redirect(url_for("Cafe.pago"))
