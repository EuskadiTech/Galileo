from flask import Blueprint, request, render_template, url_for, redirect
from ..Personas.models import DB_PERSONAS
import utils
from .models import DB_COMANDAS, ANILLAS
from ..Personas.localutils import PersonAuth, with_auth
app = Blueprint("Cafe", __name__)

def set_receta(receta):
    conf = utils.get_config()
    conf["Receta"] = receta
    utils.set_config(conf)

def get_receta():
    conf: dict = utils.get_config()
    return conf.get("Receta", "No Disp.")

@app.route("/cafe", methods=["GET"])
@with_auth("cafe:_module")
def index(user):
    return render_template(
        "cafe/index.html",
        Receta = get_receta(), USER=user
    )
@app.route("/cafe/config", methods=["GET", "POST"])
@with_auth("cafe:write")
def config(user):
    if request.method == "POST":
        set_receta(request.form["receta"])
        return redirect(url_for("Cafe.index"))
    return render_template(
        "cafe/config.html",
        Receta = get_receta(), USER=user
    )

@app.route("/cafe/select", methods=["GET", "POST"])
@with_auth("cafe:send")
def select(user):
    if request.method == "POST":
        def query(data):
            if data["Codigo"] == str(request.form["code"]):
                return True
        keys = list(DB_PERSONAS.get_by_query(query).keys())[0]
        return redirect(url_for("Cafe.comanda", rid=keys))
    return render_template(
        "cafe/select.html",
        personas = DB_PERSONAS.get_all(), USER=user
    )

@app.route("/cafe/comanda/<rid>", methods=["GET", "POST"])
@with_auth("cafe:send")
def comanda(user, rid):
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
            "_fase": "Cocina - " + utils.DateParser().pretty_dayCode(),
        }
        if data["Tama_o"][0] == "Grande" and data["Leche"][0] != "Sin Leche":
            total += 20
        if data["Tama_o"][0] != "Grande" and data["Leche"][0] != "Sin Leche":
            total += 10
        if "Cafe" in data["Tipo"] or "Cafe Soluble" in data["Tipo"]:
            total += 20
        if "Colacao" in data["Tipo"]:
            total += 20
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
        last_comanda = {}, USER=user
    )

@app.route("/cafe/cocina", methods=["GET", "POST"])
@with_auth("cafe:cocina")
def cocina(user):
    regiones = {}
    def query(data):
        if "cocina" in data["_fase"]:
            return True
        if "Cocina" in data["_fase"]:
            return True
    for key, val in  DB_COMANDAS.get_by_query(query).items():
        persona = DB_PERSONAS.get_by_id(val["_persona"])
        if regiones.get(persona["Region"]) == None:
            regiones[persona["Region"]] = []
        regiones[persona["Region"]].append((key,val))
    return render_template(
        "cafe/display.html",
        fase = "Cocina",
        personas = DB_PERSONAS.get_all(),
        Receta = get_receta(),
        comandas = DB_COMANDAS.get_by_query(query).items(),
        regiones=regiones, USER=user, fc="cocina", ft="Pago"
    )

@app.route("/cafe/pago", methods=["GET", "POST"])
@with_auth("cafe:pago")
def pago(user):
    regiones = {}
    def query(data):
        if "pago" in data["_fase"]:
            return True
        if "Pago" in data["_fase"]:
            return True
    for key, val in  DB_COMANDAS.get_by_query(query).items():
        persona = DB_PERSONAS.get_by_id(val["_persona"])
        if regiones.get(persona["Region"]) == None:
            regiones[persona["Region"]] = []
        regiones[persona["Region"]].append((key,val))
    return render_template(
        "cafe/display.html",
        fase = "Pago",
        personas = DB_PERSONAS.get_all(),
        Receta = get_receta(),
        comandas = DB_COMANDAS.get_by_query(query).items(),
        regiones=regiones, USER=user, fc="pago", ft="Historial"
    )

@app.route("/cafe/historialfilter", methods=["GET", "POST"])
@with_auth("cafe:read")
def historial(user):
    regiones = {}
    def query(data):
        if request.args.get("fase") != None:
            if request.args.get("fase") not in data["_fase"]:
                return False
        if request.args.get("rid") != None:
            if request.args.get("rid") != data["_persona"]:
                return False
        return True
    for key, val in  DB_COMANDAS.get_by_query(query).items():
        persona = DB_PERSONAS.get_by_id(val["_persona"])
        if regiones.get(persona["Region"]) == None:
            regiones[persona["Region"]] = []
        regiones[persona["Region"]].append((key,val))
    return render_template(
        "cafe/display.html",
        fase = "Historial por filtro",
        personas = DB_PERSONAS.get_all(),
        Receta = "Receta del dia",
        comandas = DB_COMANDAS.get_by_query(query).items(),
        regiones = regiones, USER=user
    )

@app.route("/cafe/updategrp", methods=["GET"])
@with_auth("cafe:cocina")
def updategrp(user):
    DB_COMANDAS.update_by_id(request.args["f"], {"_grupo": request.args["v"]})
    return redirect(url_for("Cafe.cocina"))

@app.route("/cafe/transfer_fase/<rid>/<ft>/<fc>", methods=["GET"])
@with_auth("cafe:cocina")
def rdel(user, rid, ft, fc):
    DB_COMANDAS.update_by_id(rid, {"_fase": ft + " - " + utils.DateParser().pretty_dayCode()})
    if "pago" in fc:
        com = DB_COMANDAS.get_by_id(rid)
        puntos = DB_PERSONAS.get_by_id(com["_persona"])["Puntos"]
        if com["MetodoDePago"][0] == "Efectivo":
            puntos += 1
        if com["MetodoDePago"][0] == "Puntos":
            puntos -= 10
        DB_PERSONAS.update_by_id(com["_persona"], {"Puntos": puntos, "SC_lastcomanda": com})
        # DB_COMANDAS.delete_by_id(rid)
    return redirect(url_for("Cafe." + fc))
