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

app = Blueprint("Comedor", __name__)


@app.route("/comedor", methods=["GET"])
def index():
    comedor = list_comedor()
    return render_template(
        "comedor/index.html",
        comedor=comedor,
        today=fromDay_comedor(),
    )


@app.route("/comedor/loadMenuModal", methods=["GET"])
def loadMenuModal():
    return render_template("comedor/loadMenuModal.html")


@app.route("/comedor/request", methods=["GET"])
def centralreq():
    return render_template("comedor/request.html")


@app.route("/comedor/byDayModal", methods=["GET"])
def byDayModal():
    return render_template(
        "comedor/byDayModal.html",
        menus=list_comedor_menus(),
        months=list_comedor_months(),
    )


@app.route("/comedor/getMenu")
def getMenu():
    results = fromDay_comedor(**request.args)
    day = DateParser(request.args["day"]).pretty_dayCode()
    return render_template("comedor/getMenu.html", results=results, day=day)


@app.route("/api/comedor/loadMenu", methods=["POST"])
def api__loadMenu():
    f = request.files["file"]
    co = f.read().decode("utf-8")
    load_comedor(co)
    return redirect(url_for("Comedor.index"))


@app.route("/api/comedor/reqMenu", methods=["POST"])
def api__reqMenu():
    config = get_config()
    pid = config["Clave Proxy"]
    f = request.files["file"]
    co = f.read()
    req = requests.post(
        f"https://rp.tech.eus/creq/{pid}/SuperAI/menu",
        files={"file": co},
        data=request.form,
    )
    load_comedor(req.text)
    return redirect(url_for("Comedor.index"))


@app.route("/api/comedor/deleteMenu/<mid>")
def api__deleteMenu(mid):
    DB_COMEDOR.delete_by_id(str(mid))
    return redirect(url_for("Comedor.index"))


@app.route("/api/comedor/downloadMenu/<mid>")
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
    return fromDay_comedor()
