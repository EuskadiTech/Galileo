from flask import Blueprint, request, send_file, render_template, url_for, redirect
from io import BytesIO
from markdown import markdown
from .models import DB_RECETAS
from ..Personas.localutils import PersonAuth
app = Blueprint("Recetas", __name__)


@app.route("/recetas", methods=["GET"])
def index():
    try:
        user = PersonAuth(request.cookies.get('AUTH_CODE', "UNK"), request.cookies.get('AUTH_PIN'))
        user.isLoggedIn("recetas:read")
    except Exception as e:
        return redirect(url_for("Personas.auth_scan", err=e.args))
    return render_template("recetas/index.html", recetas=DB_RECETAS.get_all(), USER=user)


@app.route("/recetas/new", methods=["GET", "POST"])
def new():
    try:
        user = PersonAuth(request.cookies.get('AUTH_CODE', "UNK"), request.cookies.get('AUTH_PIN'))
        user.isLoggedIn("recetas:write")
    except Exception as e:
        return redirect(url_for("Personas.auth_scan", err=e.args))
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
def receta(rid):
    try:
        user = PersonAuth(request.cookies.get('AUTH_CODE', "UNK"), request.cookies.get('AUTH_PIN'))
        user.isLoggedIn("recetas:read")
    except Exception as e:
        return redirect(url_for("Personas.auth_scan", err=e.args))
    receta = DB_RECETAS.get_by_id(str(rid))
    return render_template(
        "recetas/receta.html",
        receta=receta,
        content=markdown(receta["content"]),
        rid=rid,
        USER=user
    )


@app.route("/recetas/<rid>/edit", methods=["GET", "POST"])
def edit(rid):
    try:
        user = PersonAuth(request.cookies.get('AUTH_CODE', "UNK"), request.cookies.get('AUTH_PIN'))
        user.isLoggedIn("recetas:write")
    except Exception as e:
        return redirect(url_for("Personas.auth_scan", err=e.args))
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
def receta__del(rid):
    try:
        user = PersonAuth(request.cookies.get('AUTH_CODE', "UNK"), request.cookies.get('AUTH_PIN'))
        user.isLoggedIn("recetas:delete")
    except Exception as e:
        return redirect(url_for("Personas.auth_scan", err=e.args))
    if request.method == "POST":
        DB_RECETAS.delete_by_id(str(rid))
        return redirect(url_for("Recetas.index"))
    receta = DB_RECETAS.get_by_id(str(rid))
    return render_template("recetas/del.html", receta=receta, USER=user)
