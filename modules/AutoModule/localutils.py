from flask import Blueprint, request, render_template, url_for, redirect, g
from markdown import markdown
from ..Personas.localutils import with_auth, with_api_auth
from pysondb import PysonDB, errors
from modules import addnav, addautonav, addperm
from utils import USERDATA_DIR, check_path
from glob import glob
from uuid import uuid4
import json
import re

class ModelView:
    def __init__(
        self,
        modulename: str,
        model: PysonDB,
        singular: str,
        plural: str,
        data_scheme: dict,
    ):
        self.DATA_SCHEME = data_scheme
        self.app = Blueprint(modulename, __name__)
        tablename = modulename.lower()
        CONF = {
            "modulename": modulename,
            "tablename": tablename,
            "singular": singular,
            "plural": plural,
            "scheme": self.DATA_SCHEME,
        }
        basefolder = "uploads/automod/" + modulename

        def upfile(file, reqid):
            filename = file.filename
            print("Subiendo archivo:", filename)
            f = "uploads/automod/" + modulename + "/" + reqid + "/"
            p = f + filename
            filesave = USERDATA_DIR + p
            check_path(USERDATA_DIR + f)
            file.save(filesave)
            return "automod/" + modulename + "/" + reqid + "/" + filename

        check_path(USERDATA_DIR + "uploads")
        check_path(USERDATA_DIR + "uploads/automod")
        check_path(USERDATA_DIR + basefolder)

        @self.app.route(f"/{tablename}", methods=["GET"])
        @with_auth(f"{tablename}:read")
        def index():
            return render_template(
                "automod/index.html",
                CONF=CONF,
                items=model.get_all(),
                markdown=markdown,
            )

        @self.app.route(f"/api/{tablename}", methods=["GET"])
        @with_api_auth(f"{tablename}:read")
        def api__list():
            return model.get_all()

        @self.app.route(f"/{tablename}/new", methods=["GET", "POST"])
        @with_auth(f"{tablename}:create")
        def create():
            if request.method == "POST":
                inp = {}
                for key, value in self.DATA_SCHEME.items():
                    if value["type"] == "image":
                        filespaths = []
                        files = request.files.getlist(key)
                        reqid = str(uuid4()).split("-")[0]
                        for file in files:
                            filespaths.append(upfile(file, reqid))
                        inp[key] = filespaths
                    else:
                        inp[key] = request.form.get(key, value["default"])
                try:
                    model.add(inp)
                except errors.UnknownKeyError as ex:
                    # TODO: fix this hacky mess
                    unknown_keys = (
                        ex.args[0]
                        .replace("Unrecognized key(s) ['", "")
                        .replace("']", "")
                        .split("', '")
                    )
                    for key in unknown_keys:
                        model.add_new_key(key, self.DATA_SCHEME[key].get("default"))
                    model.add(inp)
                return redirect(url_for(f"{modulename}.index"))
            return render_template("automod/create.html", CONF=CONF, markdown=markdown)

        @self.app.route(f"/api/{tablename}/new", methods=["POST"])
        @with_api_auth(f"{tablename}:create")
        def api__create():
            inp = {}
            for key, value in self.DATA_SCHEME.items():
                if value["type"] == "image":
                    filespaths = []
                    files = request.files.getlist(key)
                    reqid = str(uuid4()).split("-")[0]
                    for file in files:
                        filespaths.append(upfile(file, reqid))
                    inp[key] = filespaths
                else:
                    inp[key] = request.form.get(key, value["default"])
            try:
                rid = model.add(inp)
            except errors.UnknownKeyError as ex:
                # TODO: fix this hacky mess
                unknown_keys = (
                    ex.args[0]
                    .replace("Unrecognized key(s) ['", "")
                    .replace("']", "")
                    .split("', '")
                )
                for key in unknown_keys:
                    model.add_new_key(key, self.DATA_SCHEME[key].get("default"))
                rid = model.add(inp)
            return {"status": "success", "id": rid}

        @self.app.route(f"/{tablename}/<rid>", methods=["GET"])
        @with_auth(f"{tablename}:read")
        def read(rid):
            item = model.get_by_id(str(rid))
            return render_template(
                "automod/read.html", CONF=CONF, item=item, rid=rid, markdown=markdown
            )

        @self.app.route(f"/api/{tablename}/<rid>", methods=["GET"])
        @with_api_auth(f"{tablename}:read")
        def api__read(rid):
            return model.get_by_id(str(rid))

        @self.app.route(f"/{tablename}/<rid>/edit", methods=["GET", "POST"])
        @with_auth(f"{tablename}:update")
        def update(rid):
            item = model.get_by_id(str(rid))
            if request.method == "POST":
                inp = {}
                for key, value in self.DATA_SCHEME.items():
                    if (
                        value["type"] == "image"
                        and request.form.get("AXL__replacefile", "DO_NOT")
                        == "AXL__replacefile"
                    ):
                        filespaths = []
                        files = request.files.getlist(key)
                        reqid = str(uuid4()).split("-")[0]
                        for file in files:
                            filespaths.append(upfile(file, reqid))
                        inp[key] = filespaths
                    elif (
                        value["type"] == "image"
                        and request.form.get("AXL__replacefile", "DO_NOT")
                        == "AXL__addfile"
                    ):
                        filespaths = item[key]
                        files = request.files.getlist(key)
                        reqid = str(uuid4()).split("-")[0]
                        for file in files:
                            filespaths.append(upfile(file, reqid))
                        inp[key] = filespaths
                    else:
                        inp[key] = request.form.get(
                            key, item.get(key, value["default"])
                        )
                try:
                    model.update_by_id(rid, inp)
                except errors.UnknownKeyError as ex:
                    # TODO: fix this hacky mess
                    unknown_keys = (
                        ex.args[0]
                        .replace("Unrecognized key(s) ['", "")
                        .replace("']", "")
                        .split("', '")
                    )
                    for key in unknown_keys:
                        model.add_new_key(key, self.DATA_SCHEME[key].get("default"))
                    model.update_by_id(rid, inp)
                return redirect(url_for(f"{modulename}.index"))
            return render_template(
                "automod/update.html",
                CONF=CONF,
                item=item,
                rid=rid,
                USER=g.user,
                markdown=markdown,
            )

        @self.app.route(f"/api/{tablename}/<rid>/edit", methods=["POST"])
        @with_api_auth(f"{tablename}:update")
            # Only allow alphanumeric, dash, and underscore in ids
            if not re.match(r'^[A-Za-z0-9_-]+$', rid):
                return {"status": "error", "message": "Invalid ID"}, 400
        def api__update(rid):
            item = model.get_by_id(str(rid))
            inp = {}
            for key, value in self.DATA_SCHEME.items():
                if (
                    value["type"] == "image"
                    and request.form.get("AXL__replacefile", "DO_NOT")
                    == "AXL__replacefile"
                ):
                    filespaths = []
                    files = request.files.getlist(key)
                    reqid = str(uuid4()).split("-")[0]
                    for file in files:
                        filespaths.append(upfile(file, reqid))
                    inp[key] = filespaths
                elif (
                    value["type"] == "image"
                    and request.form.get("AXL__replacefile", "DO_NOT") == "AXL__addfile"
                ):
                    filespaths = item[key]
                    files = request.files.getlist(key)
                    reqid = str(uuid4()).split("-")[0]
                    for file in files:
                        filespaths.append(upfile(file, reqid))
                    inp[key] = filespaths
                else:
                    inp[key] = request.form.get(key, item.get(key, value["default"]))
            try:
                model.update_by_id(rid, inp)
            except errors.UnknownKeyError as ex:
                # TODO: fix this hacky mess
                unknown_keys = (
                    ex.args[0]
                    .replace("Unrecognized key(s) ['", "")
                    .replace("']", "")
                    .split("', '")
                )
                for key in unknown_keys:
                    model.add_new_key(key, self.DATA_SCHEME[key].get("default"))
                model.update_by_id(rid, inp)
            return {"status": "success", "id": rid}

        @self.app.route(f"/{tablename}/<rid>/del", methods=["GET", "POST"])
        @with_auth(f"{tablename}:delete")
        def delete(rid):
            if (
                request.method == "POST"
                and request.form.get("deletecapcha") == "ELIMINAR"
            ):
                model.delete_by_id(str(rid))
                return redirect(url_for(f"{modulename}.index"))
            return render_template(
                "confirmDeletion.html", USER=g.user, markdown=markdown
            )

        @self.app.route(f"/api/{tablename}/<rid>/del", methods=["POST"])
        @with_api_auth(f"{tablename}:read")
        def api__delete(rid):
            model.delete_by_id(str(rid))
            return {"status": "success"}

        self.app = self.app
        addautonav(
            {
                "text": modulename,
                "endpoint": modulename + ".index",
                "role": tablename + ":read",
            }
        )
        addperm(plural, "Menú", modulename + "._module")
        addperm(plural, "Leer", modulename + ".read")
        addperm(plural, "Crear", modulename + ".create")
        addperm(plural, "Actualizar", modulename + ".update")
        addperm(plural, "Borrar", modulename + ".delete")


def load_config(config: dict):
    database = PysonDB(USERDATA_DIR + f"db.{config['db']}.axd")

    DATA_SCHEME = config["data_scheme"]
    view = ModelView(
        config["name"], database, config["singular"], config["plural"], DATA_SCHEME
    )

    return view.app


def load_from_dir():
    mods = glob(USERDATA_DIR + "mods/*.json")
    loaded = []
    for mod in mods:
        print("Cargando modulo: " + mod)
        loaded.append(load_config(json.load(open(mod, "r", encoding="utf-8"))))
    return loaded
