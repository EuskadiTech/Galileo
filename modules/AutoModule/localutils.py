from flask import Blueprint, request, render_template, url_for, redirect, g
from markdown import markdown
from ..Personas.localutils import with_auth
from pysondb import PysonDB
from modules import addnav, addperm
from utils import USERDATA_DIR
from glob import glob
import json
class ModelView:
    def custom_routes(self):
        pass

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

        @self.app.route(f"/{tablename}", methods=["GET"])
        @with_auth(f"{tablename}:read")
        def index():
            return render_template(
                "automod/index.html", CONF=CONF, items=model.get_all()
            )

        @self.app.route(f"/{tablename}/new", methods=["GET", "POST"])
        @with_auth(f"{tablename}:create")
        def create():
            if request.method == "POST":
                inp = {}
                for key, value in self.DATA_SCHEME.items():
                    inp[key] = request.form.get(key, value["default"])
                model.add(inp)
                return redirect(url_for(f"{modulename}.index"))
            return render_template("automod/create.html", CONF=CONF)

        @self.app.route(f"/{tablename}/<rid>", methods=["GET"])
        @with_auth(f"{tablename}:read")
        def read(rid):
            item = model.get_by_id(str(rid))
            return render_template(
                "automod/read.html",
                CONF=CONF,
                item=item,
                rid=rid,
            )

        @self.app.route(f"/{tablename}/<rid>/edit", methods=["GET", "POST"])
        @with_auth(f"{tablename}:update")
        def update(rid):
            item = model.get_by_id(str(rid))
            if request.method == "POST":
                inp = {}
                for key, value in self.DATA_SCHEME.items():
                    inp[key] = request.form.get(key, item[key])
                model.update_by_id(rid, inp)
                return redirect(url_for(f"{modulename}.index"))
            return render_template(
                "automod/update.html", CONF=CONF, item=item, rid=rid, USER=g.user
            )

        @self.app.route(f"/{tablename}/<rid>/del", methods=["GET", "POST"])
        @with_auth(f"{tablename}:delete")
        def delete(rid):
            if (
                request.method == "POST"
                and request.form.get("deletecapcha") == "ELIMINAR"
            ):
                model.delete_by_id(str(rid))
                return redirect(url_for(f"{modulename}.index"))
            return render_template("confirmDeletion.html", USER=g.user)

        self.app = self.app
        addnav(
            {
                "text": plural,
                "endpoint": modulename + ".index",
                "subitems": [
                    {
                        "text": "Lista de " + plural,
                        "endpoint": modulename + ".index",
                        "role": tablename + ":read",
                    },
                    {
                        "text": "> Añadir " + singular,
                        "endpoint": modulename + ".create",
                        "role": tablename + ":create",
                    },
                ],
                "role": modulename + ":_module",
            }
        )
        addperm(plural, "Acceder", modulename + "._module")
        addperm(plural, "Leer", modulename + ".read")
        addperm(plural, "Añadir " + plural, modulename + ".create")
        addperm(plural, "Actualizar " + plural, modulename + ".update")
        addperm(plural, "Borrar " + plural, modulename + ".delete")

def load_config(config: dict):
    database = PysonDB(USERDATA_DIR + f"db.{config['db']}.axd")


    DATA_SCHEME = config["data_scheme"]
    view = ModelView(config["name"], database, config["singular"], config["plural"], DATA_SCHEME)

    return view.app

def load_from_dir():
    mods = glob(USERDATA_DIR + "mods/**.json", recursive=True)
    loaded = []
    for mod in mods:
        print("Cargando modulo: " + mod)
        loaded.append(load_config(json.load(open(mod, "r"))))
    return loaded
