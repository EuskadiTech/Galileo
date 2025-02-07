from flask import Blueprint, request, send_file, render_template, url_for, redirect
from markdown import markdown
from .models import DB_PARTS
from ..Personas.localutils import with_auth
app = Blueprint("Recetas", __name__)


@app.route("/inventario", methods=["GET"])
@with_auth("inventario:_module")
def index(user):
    return render_template("inventario/index.html", recetas=DB_PARTS.get_all(), USER=user)


@app.route("/inventario/part/new", methods=["GET", "POST"])
@with_auth("inventario:write")
def part__new(user):
    if request.method == "POST":
        DB_PARTS.add(
            {
                "Codigo": request.form.get("Codigo", ""),
                "Nombre": request.form.get("Nombre", ""),
                "Ubicacion": request.form.get("Ubicacion", ""),
                "Estado": request.form.get("Estado", ""),
                "Notas": request.form.get("Notas", ""),
                "_meta": {},
            }
        )
        return redirect(url_for("Inventario.index"))
    return render_template("inventario/part__new.html", USER=user)


@app.route("/inventario/part/<rid>", methods=["GET"])
@with_auth("inventario:read")
def part(user, rid):
    part = DB_PARTS.get_by_id(str(rid))
    return render_template(
        "inventario/part.html",
        part=part,
        rid=rid
    )


@app.route("/inventario/part/<rid>/edit", methods=["GET", "POST"])
@with_auth("inventario:write")
def part__edit(user, rid):
    receta = DB_PARTS.get_by_id(str(rid))
    if request.method == "POST":
        DB_PARTS.update_by_id(
            str(rid),
            {
                "Codigo": request.form.get("Codigo", ""),
                "Nombre": request.form.get("Nombre", ""),
                "Ubicacion": request.form.get("Ubicacion", ""),
                "Estado": request.form.get("Estado", ""),
                "Notas": request.form.get("Notas", ""),
            },
        )
        return redirect(url_for("Inventario.index"))
    return render_template("inventario/part__edit.html", receta=receta, rid=rid, USER=user)


@app.route("/inventario/part/<rid>/del", methods=["GET", "POST"])
@with_auth("inventario:delete")
def part__del(user, rid):
    if request.method == "POST" and request.form.get("deletecapcha") == "ELIMINAR":
        DB_PARTS.delete_by_id(str(rid))
        return redirect(url_for("Inventario.index"))
    return render_template("confirmDeletion.html")
