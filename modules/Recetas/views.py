from flask import Blueprint, request, send_file, render_template, url_for, redirect
from io import BytesIO
from markdown import markdown
from .models import DB_RECETAS
from ..Personas.localutils import PersonAuth, with_auth
app = Blueprint("Recetas", __name__)


@app.route("/recetas", methods=["GET"])
@with_auth("recetas:_module")
def index(user):
    return render_template("recetas/index.html", recetas=DB_RECETAS.get_all(), USER=user)


@app.route("/recetas/new", methods=["GET", "POST"])
@with_auth("recetas:write")
def new(user):
    if request.method == "POST":
        DB_RECETAS.add(
            {
                "Nombre": request.form.get("nombre", ""),
                "Origen": "Local",
                "OrigenURL": "",
                "content": request.form.get("receta", ""),
                "YYYY-MM-DD": request.form.get("fecha", ""),
            }
        )
        return redirect(url_for("Recetas.index"))
    return render_template("recetas/new.html", USER=user)


@app.route("/recetas/<rid>", methods=["GET"])
@with_auth("recetas:read")
def receta(user, rid):
    receta = DB_RECETAS.get_by_id(str(rid))
    return render_template(
        "recetas/receta.html",
        receta=receta,
        content=markdown(receta["content"]),
        rid=rid,
        USER=user
    )


@app.route("/recetas/<rid>/edit", methods=["GET", "POST"])
@with_auth("recetas:write")
def edit(user, rid):
    receta = DB_RECETAS.get_by_id(str(rid))
    if request.method == "POST":
        DB_RECETAS.update_by_id(
            str(rid),
            {
                "Nombre": request.form.get("nombre", receta["Nombre"]),
                "Origen": receta["Origen"],
                "OrigenURL": receta["OrigenURL"],
                "content": request.form.get("receta", receta["content"]),
                "YYYY-MM-DD": request.form.get("fecha", receta["YYYY-MM-DD"]),
            },
        )
        return redirect(url_for("Recetas.index"))
    return render_template("recetas/edit.html", receta=receta, rid=rid, USER=user)


@app.route("/recetas/<rid>/del", methods=["GET", "POST"])
@with_auth("recetas:delete")
def receta__del(user, rid):
    if request.method == "POST":
        DB_RECETAS.delete_by_id(str(rid))
        return redirect(url_for("Recetas.index"))
    receta = DB_RECETAS.get_by_id(str(rid))
    return render_template("recetas/del.html", receta=receta, USER=user)
