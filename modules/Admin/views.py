from flask import Blueprint, request, send_file, render_template, url_for, redirect, make_response
from werkzeug.utils import secure_filename
from random import randint
from ..Personas.localutils import PersonAuth, with_auth
from ..Personas.models import DB_PERSONAS
from utils import USERDATA_DIR, os, check_path
from os.path import join as join_path
app = Blueprint("Admin", __name__)

@app.route("/admin/setup/adminaccount", methods=["GET", "POST"])
def setup__adminaccount():
    def admins(data):
        if "admin" in data["Roles"]:
            return True
    if DB_PERSONAS.get_by_query(admins) != {}:
        return "Cannot start onboarding, there is a admin"
    user = {}
    if request.method == "POST":
        code = str(randint(100,9999))
        DB_PERSONAS.add(
            {
                "Nombre": request.form.get("nombre", ""),
                "Roles": [
                    "admin",
                    "personas:_module",
                ],
                "Puntos": 0,
                "F-nac": request.form.get("fecha", ""),
                "markdown": request.form.get("markdown", ""),
                "Codigo": code,
                "PIN": request.form.get("pin", "").upper(),
                "Region": request.form.get("region", "Sin Aula"),
                "SC_lastcomanda": {},
                "SC_Anilla": "de color ?;#ff00ff",
                "Foto": "",
            }
        )
        return redirect(url_for("Personas.auth_scan", err = "Codigo del usuario creado: " + code + " - PIN: (" + request.form.get("pin", "").upper() + ")"))
    return render_template("admin/setup/adminaccount.html")


@app.route("/admin/files/<path:path>", methods=["GET", "POST"])
@app.route("/admin/files/", methods=["GET", "POST"], defaults={"path": ""})
@with_auth("admin")
def files(user, path):
    check_path(USERDATA_DIR + "uploads")
    check_path(USERDATA_DIR + "uploads/personas")
    base_path = os.path.join(USERDATA_DIR + "uploads/")
    full_path = os.path.normpath(os.path.join(base_path, path))
    if not full_path.startswith(base_path):
        raise Exception("Invalid path")
    files = [f for f in os.listdir(full_path) if os.path.isfile(os.path.join(full_path, f))]
    folders = [f for f in os.listdir(full_path) if os.path.isdir(os.path.join(full_path, f))]
    return render_template("admin/files.html", files = files, folders = folders, path = path)


@app.route("/admin/files_rm/", methods=["GET", "POST"], defaults={"path": ""})
@app.route("/admin/files_rm/<path:path>", methods=["GET", "POST"])
@with_auth("admin")
def filesrm(user, path):
    base_path = os.path.join(USERDATA_DIR + "uploads/")
    full_path = os.path.normpath(os.path.join(base_path, path))
    if not full_path.startswith(base_path):
        raise Exception("Invalid path")
    if request.method == "POST" and request.form.get("deletecapcha") == "ELIMINAR":
        os.unlink(full_path)
        return redirect(url_for("Admin.files", path = "/".join(path.split("/")[:-1])))
    return render_template("confirmDeletion.html", USER=user)

@app.route("/admin/files_rmdir/", methods=["GET"], defaults={"path": ""})
@app.route("/admin/files_rmdir/<path:path>", methods=["GET"])
@with_auth("admin")
def filesrmdir(user, path):
    base_path = os.path.join(USERDATA_DIR + "uploads/")
    full_path = os.path.normpath(os.path.join(base_path, path))
    if not full_path.startswith(base_path):
        raise Exception("Invalid path")
    try:
        os.rmdir(full_path)
    except OSError:
        return render_template("admin/filesrmdir_err.html")
    return redirect(url_for("Admin.files", path = "/".join(path.split("/")[:-1])))


@app.route("/admin/files_up/", methods=["GET", "POST"], defaults={"path": ""})
@app.route("/admin/files_up/<path:path>", methods=["GET", "POST"])
@with_auth("admin")
def filesupload(user, path):
    base_path = os.path.join(USERDATA_DIR + "uploads/")
    full_path = os.path.normpath(os.path.join(base_path, path))
    if not full_path.startswith(base_path):
        raise Exception("Invalid path")
    if request.method == "POST":
        folder = full_path
        file = request.files["Archivo"]
        filename = secure_filename(file.filename)
        file.save(os.path.join(folder, filename))
        return redirect(url_for("Admin.files", path = path))
    return render_template("admin/filesupload.html", path=path)

@app.route("/admin/files_mkd/", methods=["GET", "POST"], defaults={"path": ""})
@app.route("/admin/files_mkd/<path:path>", methods=["GET", "POST"])
@with_auth("admin")
def filesmkdir(user, path):
    return redirect(url_for("Admin.files", path = path))

@app.route("/admin/files_mv/", methods=["GET", "POST"], defaults={"path": ""})
@app.route("/admin/files_mv/<path:path>", methods=["GET", "POST"])
@with_auth("admin")
def filesmv(user, path):
    base_path = os.path.join(USERDATA_DIR + "uploads/")
    full_path = os.path.normpath(os.path.join(base_path, path))
    if not full_path.startswith(base_path):
        raise Exception("Invalid path")
    folder = "/".join(path.split("/")[:-1])
    if request.method == "POST":
        origen_path = os.path.normpath(os.path.join(base_path, request.form["Origen"]))
        destino_path = os.path.normpath(os.path.join(base_path, request.form["Destino"]))
        if not origen_path.startswith(base_path) or not destino_path.startswith(base_path):
            raise Exception("Invalid path")
        os.rename(origen_path, destino_path)
        return redirect(url_for("Admin.files", path = folder))
    return render_template("admin/filesmv.html", path=folder, filename = path)