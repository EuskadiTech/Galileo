from flask import (
    Blueprint,
    request,
    send_file,
    render_template,
    url_for,
    redirect,
    make_response,
    g,
)
from io import BytesIO
from markdown import markdown
from .models import DB_PERSONAS, DB_REGIONES, DB_CENTROS
from ..Cafe.models import ANILLAS
from random import randint
from . import localutils
from .localutils import PersonAuth, with_auth, confirm_deletion
from utils import USERDATA_DIR, os, check_path
from glob import glob
from modules import G_PERMS, addperm

app = Blueprint("Personas", __name__)


# region Auth
@app.route("/auth/scan", methods=["GET", "POST"])
def auth_scan():
    if request.method == "POST":
        user = localutils.PersonAuth(request.form["code"])
        try:
            user.isLoggedIn()
        except localutils.PinRequired:
            return redirect(url_for("Personas.auth_pin", code=request.form["code"]))
        except Exception as e:
            return redirect(url_for("Personas.auth_scan", err=e))
        resp = make_response(redirect(url_for("index")))
        resp.set_cookie("AUTH_CODE", request.form["code"])
        resp.set_cookie("AUTH_PIN", "")
        return resp
    return render_template("personas/auth/scan.html", err=request.args.get("err"))


@app.route("/auth/pin", methods=["GET", "POST"])
def auth_pin():
    if request.method == "POST":
        user = localutils.PersonAuth(request.form["code"], request.form["pin"])
        try:
            user.isLoggedIn()
        except localutils.PinRequired:
            return redirect(url_for("Personas.auth_pin", code=request.form["code"]))
        resp = make_response(redirect(url_for("index")))
        resp.set_cookie("AUTH_CODE", request.form["code"])
        resp.set_cookie("AUTH_PIN", request.form["pin"])
        return resp
    return render_template(
        "personas/auth/pin.html", code=request.args["code"], err=request.args.get("err")
    )


@app.route("/auth/logout", methods=["GET", "POST"])
def auth_logout():
    resp = make_response(redirect(url_for("index")))
    resp.set_cookie("AUTH_CODE", "")
    resp.set_cookie("AUTH_PIN", "")
    return resp


# endregion


@app.route("/personas", methods=["GET"])
@with_auth("personas:read")
def index():
    return render_template(
        "personas/index.html", personas=DB_PERSONAS.get_all(), USER=g.user
    )


@app.route("/personas/print", methods=["GET"])
@with_auth("personas:read")
def printcards():
    return render_template(
        "personas/print.html", recetas=DB_PERSONAS.get_all(), USER=g.user
    )


@app.route("/personas/print_stickers", methods=["GET"])
@with_auth("personas:read")
def printstickers():
    return render_template(
        "personas/printstickers.html", recetas=DB_PERSONAS.get_all(), USER=g.user
    )


@app.route("/personas/new", methods=["GET", "POST"])
@with_auth("personas:write")
def new():
    regioness = DB_REGIONES.get_all()
    centros = DB_CENTROS.get_all()
    if request.method == "POST":
        code = str(randint(100, 9999))
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
                "SC_Anilla": request.form.get("SC_Anilla_Nombre", "Sin Anilla")
                + ";"
                + request.form.get("SC_Anilla_Color", "#ff00ff"),
                "Foto": request.form.get("Foto", ""),
            }
        )
        return redirect(url_for("Personas.index"))
    check_path(USERDATA_DIR + "uploads")
    check_path(USERDATA_DIR + "uploads/personas")
    avatars = [
        file.replace("\\", "/")
        for file in glob(os.path.join(USERDATA_DIR, "uploads/personas"))
    ]
    return render_template("personas/new.html", AVATARS=avatars, regiones=regioness, centros=centros)


@app.route("/personas/scan", methods=["GET", "POST"])
@with_auth("personas:read")
def scan():
    if request.method == "POST":

        def query(data):
            if data["Codigo"] == str(request.form["code"]):
                return True

        keys = list(DB_PERSONAS.get_by_query(query).keys())[0]
        return redirect(url_for("Personas.persona", rid=keys))
    return render_template("personas/scan.html", USER=g.user)


@app.route("/personas/<rid>", methods=["GET"])
@with_auth("personas:read")
def persona(rid):
    receta = DB_PERSONAS.get_by_id(str(rid))
    return render_template(
        "personas/persona.html",
        receta=receta,
        content=markdown(receta["markdown"]),
        rid=rid,
        USER=g.user,
    )


@app.route("/personas/<rid>/pointop", methods=["GET"])
@with_auth("personas:write")
def pointop(rid):
    receta = DB_PERSONAS.get_by_id(str(rid))
    DB_PERSONAS.update_by_id(
        str(rid),
        {
            "Puntos": int(receta["Puntos"] + int(request.args["val"])),
        },
    )
    return "OK"


@app.route("/personas/<rid>/edit", methods=["GET", "POST"])
@with_auth("personas:write")
def edit(rid):
    receta = DB_PERSONAS.get_by_id(str(rid))
    regioness = DB_REGIONES.get_all()
    centros = DB_CENTROS.get_all()
    if request.method == "POST":
        try:
            DB_PERSONAS.update_by_id(
                str(rid),
                {
                    "Nombre": request.form.get("Nombre", receta["Nombre"]),
                    "Roles": request.form.getlist("roles[]"),
                    "F-nac": request.form.get("fecha", receta["F-nac"]),
                    "Puntos": int(request.form.get("Puntos", receta["Puntos"])),
                    "Codigo": request.form.get("Codigo", receta["Codigo"]),
                    "markdown": request.form.get("markdown", receta["markdown"]),
                    "PIN": request.form.get("PIN", receta["PIN"]).upper(),
                    "Region": request.form.get("Region", receta["Region"]).upper(),
                    "SC_Anilla": request.form.get("SC_Anilla_Nombre", "Sin Anilla")
                    + ";"
                    + request.form.get("SC_Anilla_Color", "#ff00ff"),
                    "Foto": request.form.get("Foto", ""),
                },
            )
        except:
            DB_PERSONAS.add_new_key("Foto", "")
        return redirect(url_for("Personas.index"))
    picpath = USERDATA_DIR + "uploads/personas"
    check_path(USERDATA_DIR + "uploads")
    check_path(USERDATA_DIR + "uploads/personas")

    avatars = [
        file.replace("\\", "/").removeprefix(
            os.path.join(USERDATA_DIR, "uploads/personas/").replace("\\", "/")
        )
        for file in glob(
            os.path.join(USERDATA_DIR, "uploads/personas/**"), recursive=True
        )
        if os.path.isfile(file)
    ]
    return render_template(
        "personas/edit.html",
        receta=receta,
        rid=rid,
        ANILLAS=ANILLAS,
        USER=g.user,
        AVATARS=avatars,
        regiones=regioness,
        centros=centros,
        G_PERMS=G_PERMS,
    )


@app.route("/personas/<rid>/del", methods=["GET", "POST"])
@confirm_deletion
@with_auth("personas:delete")
def rdel(rid):
    if request.method == "POST" and request.form.get("deletecapcha") == "ELIMINAR":
        DB_PERSONAS.delete_by_id(str(rid))
        return redirect(url_for("Personas.index"))
    return render_template("confirmDeletion.html", USER=g.user)


@app.route("/personas_regiones")
@with_auth("personas:read")
def regiones():
    return render_template(
        "personas/regiones/index.html", regiones=DB_REGIONES.get_all(), centros=DB_CENTROS.get_all(), USER=g.user
    )


@app.route("/personas_regiones/new", methods=["GET", "POST"])
@with_auth("personas:write")
def regiones_new():
    centros = DB_CENTROS.get_all()
    if request.method == "POST":
        DB_REGIONES.add(
            {
                "Nombre": request.form.get("Nombre", ""),
                "Color": request.form.get("Color", "lightblue"),
                "Centro": request.form.get("Centro", ""),
            }
        )
        return redirect(url_for("Personas.regiones"))
    return render_template("personas/regiones/new.html", centros=centros, USER=g.user)


@app.route("/personas_regiones/<rid>/del", methods=["GET", "POST"])
@with_auth("personas:delete")
def regiones_rdel(rid):
    if request.method == "POST" and request.form.get("deletecapcha") == "ELIMINAR":
        DB_REGIONES.delete_by_id(str(rid))
        return redirect(url_for("Personas.regiones"))
    return render_template("confirmDeletion.html", USER=g.user)


@app.route("/personas_regiones/<rid>/edit", methods=["GET", "POST"])
@with_auth("personas:write")
def regiones_edit(rid):
    region = DB_REGIONES.get_by_id(str(rid))
    centros = DB_CENTROS.get_all()
    if request.method == "POST":
        DB_REGIONES.update_by_id(
            str(rid),
            {
                "Nombre": request.form.get("Nombre", region["Nombre"]),
                "Color": request.form.get("Color", region["Color"]),
                "Centro": request.form.get("Centro", region.get("Centro", "")),
            },
        )
        return redirect(url_for("Personas.regiones"))

    return render_template(
        "personas/regiones/edit.html", region=region, centros=centros, rid=rid, USER=g.user
    )


@app.route("/personas_regiones/<rid>")
@with_auth("personas:read")
def regiones_region(rid):
    region = DB_REGIONES.get_by_id(str(rid))
    return render_template(
        "personas/regiones/region.html", region=region, rid=rid, USER=g.user
    )


# Centro routes
@app.route("/personas_centros")
@with_auth("personas:read")
def centros():
    return render_template(
        "personas/centros/index.html", centros=DB_CENTROS.get_all(), USER=g.user
    )


@app.route("/personas_centros/new", methods=["GET", "POST"])
@with_auth("personas:write")
def centros_new():
    if request.method == "POST":
        DB_CENTROS.add(
            {
                "Nombre": request.form.get("Nombre", ""),
                "Color": request.form.get("Color", "lightblue"),
            }
        )
        return redirect(url_for("Personas.centros"))
    return render_template("personas/centros/new.html", USER=g.user)


@app.route("/personas_centros/<rid>/del", methods=["GET", "POST"])
@with_auth("personas:delete")
def centros_rdel(rid):
    if request.method == "POST" and request.form.get("deletecapcha") == "ELIMINAR":
        DB_CENTROS.delete_by_id(str(rid))
        return redirect(url_for("Personas.centros"))
    return render_template("confirmDeletion.html", USER=g.user)


@app.route("/personas_centros/<rid>/edit", methods=["GET", "POST"])
@with_auth("personas:write")
def centros_edit(rid):
    centro = DB_CENTROS.get_by_id(str(rid))
    if request.method == "POST":
        DB_CENTROS.update_by_id(
            str(rid),
            {
                "Nombre": request.form.get("Nombre", centro["Nombre"]),
                "Color": request.form.get("Color", centro["Color"]),
            },
        )
        return redirect(url_for("Personas.centros"))

    return render_template(
        "personas/centros/edit.html", centro=centro, rid=rid, USER=g.user
    )


@app.route("/personas_centros/<rid>")
@with_auth("personas:read")
def centros_centro(rid):
    centro = DB_CENTROS.get_by_id(str(rid))
    return render_template(
        "personas/centros/centro.html", centro=centro, rid=rid, USER=g.user
    )


addperm("Personas", "Acceder", "personas:_module")
addperm("Personas", "Leer", "personas:read")
addperm("Personas", "Escribir", "personas:write")
addperm("Personas", "Borrar", "personas:delete")
