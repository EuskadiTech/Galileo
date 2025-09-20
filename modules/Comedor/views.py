from flask import Blueprint, request, send_file, render_template, url_for, redirect, g
from io import BytesIO
import requests
from utils import DateParser
from .models import DB_COMEDOR
from .localutils import (
    list_comedor,
    list_comedor_menus,
    list_comedor_monthMenu,
    list_comedor_months,
    load_comedor,
    fromDay_comedor,
)
from utils import get_config
from ..Personas.localutils import PersonAuth, with_auth, confirm_deletion
from modules import addperm

app = Blueprint("Comedor", __name__)


@app.route("/comedor", methods=["GET"])
@with_auth("comedor:read")
def index():
    comedor = list_comedor()
    return render_template(
        "comedor/index.html", comedor=comedor, today=fromDay_comedor(), USER=g.user
    )


@app.route("/comedor/loadMenuModal", methods=["GET"])
@with_auth("comedor:write")
def loadMenuModal():
    return render_template("comedor/loadMenuModal.html", USER=g.user)


@app.route("/comedor/request", methods=["GET"])
@with_auth("comedor:write")
def centralreq():
    return render_template("comedor/request.html", USER=g.user)


@app.route("/comedor/byDayModal", methods=["GET"])
@with_auth("comedor:read")
def byDayModal():
    return render_template(
        "comedor/byDayModal.html",
        menus=list_comedor_menus(),
        months=list_comedor_months(),
        USER=g.user,
    )


@app.route("/comedor/getMenu")
@with_auth("comedor:read")
def getMenu():
    day = DateParser(request.args.get("day")).pretty_day_code()
    results = fromDay_comedor(day=day, menu=request.args.get("menu", "*"))
    return render_template(
        "comedor/getMenu.html", results=results, day=day, USER=g.user
    )


@app.route("/api/comedor/loadMenu", methods=["POST"])
@with_auth("comedor:write")
def api__loadMenu():
    f = request.files["file"]
    co = f.read().decode("utf-8")
    load_comedor(co)
    return redirect(url_for("Comedor.index"))


@app.route("/api/comedor/deleteMenu/<mid>")
@confirm_deletion
@with_auth("comedor:delete")
def api__deleteMenu(mid):
    if request.method == "POST" and request.form.get("deletecapcha") == "ELIMINAR":
        DB_COMEDOR.delete_by_id(str(mid))
        return redirect(url_for("Comedor.index"))
    return render_template("confirmDeletion.html", USER=g.user)


@app.route("/api/comedor/downloadMenu/<mid>")
@with_auth("comedor:read")
def api__downloadMenu(mid):
    bio = BytesIO()
    menu = DB_COMEDOR.get_by_id(str(mid))
    bio.write(menu["source_plain"].encode("utf-8"))
    bio.seek(0)
    return send_file(
        bio,
        "text/plain",
        as_attachment=True,
        download_name=f"Menu {menu['menu']} del mes {menu['month']}.axl",
    )


@app.route("/api/comedor/today")
def api__today():
    # GUEST ACCESS API
    day = DateParser(request.args.get("day")).pretty_day_code()
    results = fromDay_comedor(day=day, menu=request.args.get("menu", "*"))
    return results


addperm("Comedor", "Acceder", "comedor:_module")
addperm("Comedor", "Leer", "comedor:read")
addperm("Comedor", "Escribir", "comedor:write")
addperm("Comedor", "Borrar", "comedor:delete")
