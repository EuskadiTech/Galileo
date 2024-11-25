from flask import Blueprint, request, send_file, render_template, url_for, redirect, make_response
from io import BytesIO
from markdown import markdown
from .models import DB_PERSONAS
from ..Cafe.models import ANILLAS
from random import randint
from . import localutils
from .localutils import PersonAuth
app = Blueprint("Personas", __name__)


@app.route("/personas", methods=["GET"])
def index():
    try:
        user = PersonAuth(request.cookies.get('AUTH_CODE', "UNK"), request.cookies.get('AUTH_PIN'))
        user.isLoggedIn("personas:read")
    except Exception as e:
        return redirect(url_for("Personas.auth_scan", err=e.args))
    return render_template("personas/index.html", personas=DB_PERSONAS.get_all(), USER=user)

@app.route("/personas/print", methods=["GET"])
def print():
    try:
        user = PersonAuth(request.cookies.get('AUTH_CODE', "UNK"), request.cookies.get('AUTH_PIN'))
        user.isLoggedIn("personas:read")
    except Exception as e:
        return redirect(url_for("Personas.auth_scan", err=e.args))
    return render_template("personas/print.html", recetas=DB_PERSONAS.get_all(), USER=user)


@app.route("/personas/new", methods=["GET", "POST"])
def new():
    er = True
    if DB_PERSONAS.get_all() != {}:
        er = False
        try:
            user = PersonAuth(request.cookies.get('AUTH_CODE', "UNK"), request.cookies.get('AUTH_PIN'))
            user.isLoggedIn("personas:write")
        except Exception as e:
            return redirect(url_for("Personas.auth_scan", err=e.args))
    user = {}
    if request.method == "POST":
        code = str(randint(100,9999))
        DB_PERSONAS.add(
            {
                "Nombre": request.form.get("nombre", ""),
                "Roles": request.form.getlist("roles[]"),
                "Puntos": 0,
                "F-nac": request.form.get("fecha", ""),
                "markdown": request.form.get("markdown", ""),
                "Codigo": code,
                "PIN": request.form.get("pin", "").upper(),
                "Region": request.form.get("region", "Sin Aula"),
                "SC_lastcomanda": {},
                "SC_Anilla": request.form.get("SC_Anilla_Nombre", "Sin Anilla") + ";" + request.form.get("SC_Anilla_Color", "#ff00ff"),
            }
        )
        if er:
            return redirect(url_for("Personas.auth_scan", err = "Codigo del usuario creado: " + code))
        return redirect(url_for("Personas.index"))
    return render_template("personas/new.html", ANILLAS=ANILLAS, USER=user, err=request.args.get("err"))

@app.route("/personas/scan", methods=["GET", "POST"])
def scan():
    try:
        user = PersonAuth(request.cookies.get('AUTH_CODE', "UNK"), request.cookies.get('AUTH_PIN'))
        user.isLoggedIn("personas:read")
    except Exception as e:
        return redirect(url_for("Personas.auth_scan", err=e.args))
    if request.method == "POST":
        def query(data):
            if data["Codigo"] == str(request.form["code"]):
                return True
        keys = list(DB_PERSONAS.get_by_query(query).keys())[0]
        return redirect(url_for("Personas.persona", rid=keys))
    return render_template("personas/scan.html", USER=user)

#region Auth
@app.route("/auth/scan", methods=["GET", "POST"])
def auth_scan():
    if request.method == "POST":
        user = localutils.PersonAuth(request.form["code"])
        try:
            user.isLoggedIn()
        except localutils.PinRequired:
            return redirect(url_for("Personas.auth_pin", code = request.form["code"]))
        except Exception as e:
            return redirect(url_for("Personas.auth_scan", err = e))
        resp = make_response(redirect(url_for("index")))
        resp.set_cookie('AUTH_CODE', request.form["code"])
        resp.set_cookie('AUTH_PIN', "")
        return resp
    return render_template("personas/auth/scan.html", err=request.args.get("err"))

@app.route("/auth/pin", methods=["GET", "POST"])
def auth_pin():
    if request.method == "POST":
        user = localutils.PersonAuth(request.form["code"], request.form["pin"])
        try:
            user.isLoggedIn()
        except localutils.PinRequired:
            return redirect(url_for("Personas.auth_pin", code = request.form["code"]))
        resp = make_response(redirect(url_for("index")))
        resp.set_cookie('AUTH_CODE', request.form["code"])
        resp.set_cookie('AUTH_PIN', request.form["pin"])
        return resp
    return render_template("personas/auth/pin.html", code = request.args["code"], err=request.args.get("err"))

@app.route("/auth/logout", methods=["GET", "POST"])
def auth_logout():
    resp = make_response(redirect(url_for("index")))
    resp.set_cookie('AUTH_CODE', "")
    resp.set_cookie('AUTH_PIN', "")
    return resp

#endregion

@app.route("/personas/<rid>", methods=["GET"])
def persona(rid):
    try:
        user = PersonAuth(request.cookies.get('AUTH_CODE', "UNK"), request.cookies.get('AUTH_PIN'))
        user.isLoggedIn("personas:read")
    except Exception as e:
        return redirect(url_for("Personas.auth_scan", err=e.args))
    receta = DB_PERSONAS.get_by_id(str(rid))
    return render_template(
        "personas/persona.html",
        receta=receta,
        content=markdown(receta["markdown"]),
        rid=rid, USER=user
    )


@app.route("/personas/<rid>/edit", methods=["GET", "POST"])
def edit(rid):
    try:
        user = PersonAuth(request.cookies.get('AUTH_CODE', "UNK"), request.cookies.get('AUTH_PIN'))
        user.isLoggedIn("personas:write")
    except Exception as e:
        return redirect(url_for("Personas.auth_scan", err=e.args))
    receta = DB_PERSONAS.get_by_id(str(rid))
    if request.method == "POST":
        DB_PERSONAS.update_by_id(
            str(rid),
            {
                "Nombre": request.form.get("nombre", receta["Nombre"]),
                "Roles": request.form.getlist("roles[]"),
                "F-nac": request.form.get("fecha", receta["F-nac"]),
                "Puntos": int(request.form.get("puntos", receta["Puntos"])),
                "Codigo": request.form.get("codigo", receta["Codigo"]),
                "markdown": request.form.get("markdown", receta["markdown"]),
                "PIN": request.form.get("pin", receta["PIN"]).upper(),
                "Region": request.form.get("region", receta["Region"]).upper(),
                "SC_Anilla": request.form.get("SC_Anilla_Nombre", "Sin Anilla") + ";" + request.form.get("SC_Anilla_Color", "#ff00ff"),
            }
        )
        return redirect(url_for("Personas.index"))
    return render_template("personas/edit.html", receta=receta, rid=rid, ANILLAS=ANILLAS, USER=user)


@app.route("/personas/<rid>/del", methods=["GET", "POST"])
def rdel(rid):
    try:
        user = PersonAuth(request.cookies.get('AUTH_CODE', "UNK"), request.cookies.get('AUTH_PIN'))
        user.isLoggedIn("personas:write")
    except Exception as e:
        return redirect(url_for("Personas.auth_scan", err=e.args))
    if request.method == "POST":
        DB_PERSONAS.delete_by_id(str(rid))
        return redirect(url_for("Personas.index"))
    receta = DB_PERSONAS.get_by_id(str(rid))
    return render_template("personas/del.html", receta=receta, USER=user)
