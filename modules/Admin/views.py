from flask import Blueprint, request, send_file, render_template, url_for, redirect, make_response
from random import randint
from ..Personas.localutils import PersonAuth, with_auth
from ..Personas.models import DB_PERSONAS
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
                "Foto": "https://www.iconexperience.com/_img/v_collection_png/256x256/shadow/scientist.png",
            }
        )
        return redirect(url_for("Personas.auth_scan", err = "Codigo del usuario creado: " + code + " - PIN: (" + request.form.get("pin", "").upper() + ")"))
    return render_template("admin/setup/adminaccount.html")
