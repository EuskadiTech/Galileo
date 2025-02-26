from flask import Blueprint, request, send_file, render_template, url_for, redirect
from io import BytesIO
from markdown import markdown
from .models import DB_PARTS
from ..Personas.localutils import with_auth
app = Blueprint("Inventario", __name__)


@app.route("/inventario", methods=["GET"])
@with_auth("inventario:_module")
def index(user):
    return render_template("inventario/index.html", parts=DB_PARTS.get_all(), USER=user)


@app.route("/inventario/new", methods=["GET", "POST"])
@with_auth("inventario:write")
def new(user):
    if request.method == "POST":
        DB_PARTS.add(
            {
                "Codigo": request.form.get("Codigo", ""),
                "Nombre": request.form.get("Nombre", ""),
                "Lugar": request.form.get("Lugar", ""),
                "Notas": request.form.get("Notas", ""),
            }
        )
        return redirect(url_for("Inventario.index"))
    return render_template("inventario/new.html", USER=user)


@app.route("/inventario/<rid>", methods=["GET"])
@with_auth("inventario:read")
def part(user, rid):
    part = DB_PARTS.get_by_id(str(rid))
    return render_template(
        "inventario/edit.html",
        part=part,
        rid=rid,
        USER=user
    )


@app.route("/inventario/<rid>/edit", methods=["GET", "POST"])
@with_auth("inventario:write")
def edit(user, rid):
    part = DB_PARTS.get_by_id(str(rid))
    if request.method == "POST":
        DB_PARTS.update_by_id(
            str(rid),
            {
                "Codigo": request.form.get("Codigo", part["Codigo"]),
                "Nombre": request.form.get("Nombre", part["Nombre"]),
                "Lugar": request.form.get("Lugar", part["Lugar"]),
                "Notas": request.form.get("Notas", part["Notas"]),
            },
        )
        return redirect(url_for("Inventario.index"))
    return render_template("inventario/edit.html", part=part, rid=rid, USER=user)


@app.route("/inventario/<rid>/del", methods=["GET", "POST"])
@with_auth("inventario:delete")
def part__del(user, rid):
    if request.method == "POST" and request.form.get("deletecapcha") == "ELIMINAR":
        DB_PARTS.delete_by_id(str(rid))
        return redirect(url_for("Inventario.index"))
    return render_template("confirmDeletion.html", USER=user)
