from flask import Blueprint, request, render_template, url_for, redirect
from ..Personas.models import DB_PERSONAS
import utils
from .models import DB_COMANDAS, ANILLAS
from ..Personas.localutils import PersonAuth
app = Blueprint("Cafe", __name__)

def set_receta(receta):
    conf = utils.get_config()
    conf["Receta"] = receta
    utils.set_config(conf)

def get_receta():
    conf: dict = utils.get_config()
    return conf.get("Receta", "No Disp.")

@app.route("/cafe", methods=["GET"])
def index():
    try:
        user = PersonAuth(request.cookies.get('AUTH_CODE', "UNK"), request.cookies.get('AUTH_PIN'))
        user.isLoggedIn("cafe:read")
    except Exception as e:
        return redirect(url_for("Personas.auth_scan", err=e.args))
    return render_template(
        "cafe/index.html",
        Receta = get_receta(), USER=user
    )
@app.route("/cafe/config", methods=["GET", "POST"])
def config():
    try:
        user = PersonAuth(request.cookies.get('AUTH_CODE', "UNK"), request.cookies.get('AUTH_PIN'))
        user.isLoggedIn("cafe:write")
    except Exception as e:
        return redirect(url_for("Personas.auth_scan", err=e.args))
    if request.method == "POST":
        set_receta(request.form["receta"])
        return redirect(url_for("Cafe.index"))
    return render_template(
        "cafe/config.html",
        Receta = get_receta(), USER=user
    )

@app.route("/cafe/select", methods=["GET", "POST"])
def select():
    try:
        user = PersonAuth(request.cookies.get('AUTH_CODE', "UNK"), request.cookies.get('AUTH_PIN'))
        user.isLoggedIn("cafe:write")
    except Exception as e:
        return redirect(url_for("Personas.auth_scan", err=e.args))
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
def comanda(rid):
    try:
        user = PersonAuth(request.cookies.get('AUTH_CODE', "UNK"), request.cookies.get('AUTH_PIN'))
        user.isLoggedIn("cafe:write")
    except Exception as e:
        return redirect(url_for("Personas.auth_scan", err=e.args))
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
            "_fase": "Cocina"
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
        last_comanda = {}, USER=user
    )

@app.route("/cafe/cocina", methods=["GET", "POST"])
def cocina():
    try:
        user = PersonAuth(request.cookies.get('AUTH_CODE', "UNK"), request.cookies.get('AUTH_PIN'))
        user.isLoggedIn("cafe:write")
    except Exception as e:
        return redirect(url_for("Personas.auth_scan", err=e.args))
    regiones = {}
    def query(data):
        if data["_fase"] == "cocina":
            return True
        if data["_fase"] == "Cocina":
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
        regiones=regiones, USER=user
    )

@app.route("/cafe/pago", methods=["GET", "POST"])
def pago():
    try:
        user = PersonAuth(request.cookies.get('AUTH_CODE', "UNK"), request.cookies.get('AUTH_PIN'))
        user.isLoggedIn("cafe:write")
    except Exception as e:
        return redirect(url_for("Personas.auth_scan", err=e.args))
    regiones = {}
    def query(data):
        if data["_fase"] == "pago":
            return True
        if data["_fase"] == "Pago":
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
        regiones=regiones, USER=user
    )

@app.route("/cafe/historial/<rid>", methods=["GET", "POST"])
def historial(rid):
    try:
        user = PersonAuth(request.cookies.get('AUTH_CODE', "UNK"), request.cookies.get('AUTH_PIN'))
        user.isLoggedIn("cafe:read")
    except Exception as e:
        return redirect(url_for("Personas.auth_scan", err=e.args))
    regiones = {}
    def query(data):
        if data["_persona"] == rid:
            return True
    for key, val in  DB_COMANDAS.get_by_query(query).items():
        persona = DB_PERSONAS.get_by_id(val["_persona"])
        if regiones.get(persona["Region"]) == None:
            regiones[persona["Region"]] = []
        regiones[persona["Region"]].append((key,val))
    return render_template(
        "cafe/display.html",
        fase = "Historial",
        personas = DB_PERSONAS.get_all(),
        Receta = "Receta del dia",
        comandas = DB_COMANDAS.get_by_query(query).items(),
        regiones = regiones, USER=user
    )

@app.route("/cafe/updategrp", methods=["GET"])
def updategrp():
    try:
        user = PersonAuth(request.cookies.get('AUTH_CODE', "UNK"), request.cookies.get('AUTH_PIN'))
        user.isLoggedIn("cafe:write")
    except Exception as e:
        return redirect(url_for("Personas.auth_scan", err=e.args))
    DB_COMANDAS.update_by_id(request.args["f"], {"_grupo": request.args["v"]})
    return redirect(url_for("Cafe.cocina"))

@app.route("/cafe/del_cocina/<rid>", methods=["GET"])
def rdel(rid):
    try:
        user = PersonAuth(request.cookies.get('AUTH_CODE', "UNK"), request.cookies.get('AUTH_PIN'))
        user.isLoggedIn("cafe:write")
    except Exception as e:
        return redirect(url_for("Personas.auth_scan", err=e.args))
    DB_COMANDAS.update_by_id(rid, {"_fase": "Pago"})
    return redirect(url_for("Cafe.cocina"))

@app.route("/cafe/del_pago/<rid>", methods=["GET"])
def rdel_pago(rid):
    try:
        user = PersonAuth(request.cookies.get('AUTH_CODE', "UNK"), request.cookies.get('AUTH_PIN'))
        user.isLoggedIn("cafe:write")
    except Exception as e:
        return redirect(url_for("Personas.auth_scan", err=e.args))
    com = DB_COMANDAS.get_by_id(rid)
    puntos = DB_PERSONAS.get_by_id(com["_persona"])["Puntos"]
    if com["MetodoDePago"][0] == "Efectivo":
        puntos += 1
    if com["MetodoDePago"][0] == "Puntos":
        puntos -= 10
    DB_PERSONAS.update_by_id(com["_persona"], {"Puntos": puntos, "SC_lastcomanda": com})
    # DB_COMANDAS.delete_by_id(rid)
    DB_COMANDAS.update_by_id(rid, {"_fase": "Historial"})
    return redirect(url_for("Cafe.pago"))
