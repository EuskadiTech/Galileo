from flask import Blueprint, request, send_file, render_template, url_for, redirect
from io import BytesIO
from markdown import markdown
from .models import DB_PERSONAS

from random import randint

app = Blueprint("Personas", __name__)


@app.route("/personas", methods=["GET"])
def index():
    return render_template("personas/index.html", personas=DB_PERSONAS.get_all())

@app.route("/personas/print", methods=["GET"])
def print():
    return render_template("personas/print.html", recetas=DB_PERSONAS.get_all())


@app.route("/personas/new", methods=["GET", "POST"])
def new():
    if request.method == "POST":
        DB_PERSONAS.add(
            {
                "Nombre": request.form.get("nombre", ""),
                "Roles": request.form.get("roles", ""),
                "Puntos": 0,
                "F-nac": request.form.get("fecha", ""),
                "markdown": request.form.get("markdown", ""),
                "Codigo": str(randint(100,9999)),
                "PIN": request.form.get("pin", "").upper(),
                "Region": request.form.get("region", "Sin Aula"),
            }
        )
        return redirect(url_for("Personas.index"))
    return render_template("personas/new.html")

@app.route("/personas/scan", methods=["GET", "POST"])
def scan():
    if request.method == "POST":
        def query(data):
            if data["Codigo"] == str(request.form["code"]):
                return True
        keys = list(DB_PERSONAS.get_by_query(query).keys())[0]
        return redirect(url_for("Personas.persona", rid=keys))
    return render_template("personas/scan.html")


@app.route("/personas/<rid>", methods=["GET"])
def persona(rid):
    receta = DB_PERSONAS.get_by_id(str(rid))
    return render_template(
        "personas/persona.html",
        receta=receta,
        content=markdown(receta["markdown"]),
        rid=rid,
    )


@app.route("/personas/<rid>/edit", methods=["GET", "POST"])
def edit(rid):
    receta = DB_PERSONAS.get_by_id(str(rid))
    if request.method == "POST":
        DB_PERSONAS.update_by_id(
            str(rid),
            {
                "Nombre": request.form.get("nombre", receta["Nombre"]),
                "Roles": request.form.get("roles", receta["Roles"]),
                "F-nac": request.form.get("fecha", receta["F-nac"]),
                "Puntos": int(request.form.get("puntos", receta["Puntos"])),
                "Codigo": request.form.get("codigo", receta["Codigo"]),
                "markdown": request.form.get("markdown", receta["markdown"]),
                "PIN": request.form.get("pin", receta["PIN"]).upper(),
                "Region": request.form.get("region", receta["Region"]).upper(),
            }
        )
        return redirect(url_for("Personas.index"))
    return render_template("personas/edit.html", receta=receta, rid=rid)


@app.route("/personas/<rid>/del", methods=["GET", "POST"])
def rdel(rid):
    if request.method == "POST":
        DB_PERSONAS.delete_by_id(str(rid))
        return redirect(url_for("Personas.index"))
    receta = DB_PERSONAS.get_by_id(str(rid))
    return render_template("personas/del.html", receta=receta)
