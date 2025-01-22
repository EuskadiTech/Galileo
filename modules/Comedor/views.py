from flask import Blueprint, request, send_file, render_template, url_for, redirect
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

app = Blueprint("Comedor", __name__)


@app.route("/comedor", methods=["GET"])
@with_auth("comedor:read")
def index(user):
    comedor = list_comedor()
    return render_template(
        "comedor/index.html",
        comedor=comedor,
        today=fromDay_comedor(), USER=user
    )


@app.route("/comedor/loadMenuModal", methods=["GET"])
@with_auth("comedor:write")
def loadMenuModal(user):
    return render_template("comedor/loadMenuModal.html", USER=user)


@app.route("/comedor/request", methods=["GET"])
@with_auth("comedor:write")
def centralreq(user):
    return render_template("comedor/request.html", USER=user)


@app.route("/comedor/byDayModal", methods=["GET"])
@with_auth("comedor:read")
def byDayModal(user):
    return render_template(
        "comedor/byDayModal.html",
        menus=list_comedor_menus(),
        months=list_comedor_months(), USER=user
    )


@app.route("/comedor/getMenu")
@with_auth("comedor:read")
def getMenu(user):
    day = DateParser(request.args.get("day")).pretty_dayCode()
    results = fromDay_comedor(day=day, menu=request.args.get("menu", "*"))
    return render_template("comedor/getMenu.html", results=results, day=day, USER=user)


@app.route("/api/comedor/loadMenu", methods=["POST"])
@with_auth("comedor:write")
def api__loadMenu(user):
    f = request.files["file"]
    co = f.read().decode("utf-8")
    load_comedor(co)
    return redirect(url_for("Comedor.index"))


@app.route("/api/comedor/reqMenu", methods=["POST"])
@with_auth("comedor:write")
def api__reqMenu(user):
    config = get_config()
    pid = config["Clave Proxy"]
    f = request.files["file"]
    co = f.read()
    req = requests.post(
        f"https://grp.naiel.fyi/creq/{pid}/SuperAI/menu",
        files={"file": co},
        data=request.form,
    )
    load_comedor(req.text)
    return redirect(url_for("Comedor.index"))


@app.route("/api/comedor/deleteMenu/<mid>")
@confirm_deletion
@with_auth("comedor:delete")
def api__deleteMenu(user, mid):
    if request.method == "POST" and request.form.get("deletecapcha") == "ELIMINAR":
        DB_COMEDOR.delete_by_id(str(mid))
        return redirect(url_for("Comedor.index"))
    return render_template("confirmDeletion.html", USER=user)


@app.route("/api/comedor/downloadMenu/<mid>")
@with_auth("comedor:read")
def api__downloadMenu(user, mid):
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
    return fromDay_comedor()
