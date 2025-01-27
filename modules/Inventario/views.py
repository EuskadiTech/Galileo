from flask import Blueprint, request, render_template, url_for, redirect
from .models import DB_INVENTARIO_PART, DB_INVENTARIO_ZONA
from ..Personas.localutils import with_auth
app = Blueprint("Inventario", __name__)


@app.route("/inventario/part", methods=["GET"])
@with_auth("inventario:_module")
def part(user):
    return render_template("inventario/part/index.html", parts=DB_INVENTARIO_PART.get_all(), USER=user)


@app.route("/inventario/part/new", methods=["GET", "POST"])
@with_auth("inventario:write")
def part__new(user):
    if request.method == "POST":
        DB_INVENTARIO_PART.add(
            {
                "Nombre": request.form.get("Nombre", ""),
                "Origen": "Local",
                "Codigo": request.form.get("Codigo", ""),
                "Notas": request.form.get("Notas", ""),
                "Zona": request.form.get("Zona", ""),
            }
        )
        return redirect(url_for("Inventario.index"))
    return render_template("inventario/part/new.html", USER=user)


@app.route("/inventario/part/<rid>", methods=["GET"])
@with_auth("inventario:read")
def part__get(user, rid):
    part = DB_INVENTARIO_PART.get_by_id(str(rid))
    return render_template(
        "inventario/part/get.html",
        part=part,
        rid=rid,
        USER=user
    )


@app.route("/inventario/part/<rid>/edit", methods=["GET", "POST"])
@with_auth("inventario:write")
def part__edit(user, rid):
    receta = DB_INVENTARIO_PART.get_by_id(str(rid))
    if request.method == "POST":
        DB_INVENTARIO_PART.update_by_id(
            str(rid),
            {
                "Nombre": request.form.get("Nombre", receta["Nombre"]),
                "Origen": "Local",
                "Codigo": request.form.get("Codigo", receta["Codigo"]),
                "Notas": request.form.get("Notas", receta["Notas"]),
                "Zona": request.form.get("Zona", receta["Zona"]),
            }
        )
        return redirect(url_for("Inventario.index"))
    return render_template("inventario/part/edit.html", part=part, rid=rid, USER=user)


@app.route("/inventario/part/<rid>/del", methods=["GET", "POST"])
@with_auth("inventario:delete")
def part__del(user, rid):
    if request.method == "POST" and request.form.get("deletecapcha") == "ELIMINAR":
        DB_INVENTARIO_PART.delete_by_id(str(rid))
        return redirect(url_for("inventario.index"))
    return render_template("confirmDeletion.html", USER=user, item="Elemento de Inventario")


###
@app.route("/inventario/zone", methods=["GET"])
@with_auth("inventario:_module")
def zone(user):
    return render_template("inventario/zone/index.html", zones=DB_INVENTARIO_ZONA.get_all(), USER=user)


@app.route("/inventario/zone/new", methods=["GET", "POST"])
@with_auth("inventario:write")
def zone__new(user):
    if request.method == "POST":
        DB_INVENTARIO_ZONA.add(
            {
                "Nombre": request.form.get("Nombre", ""),
                "Codigo": request.form.get("Codigo", ""),
                "Notas": request.form.get("Notas", ""),
            }
        )
        return redirect(url_for("Inventario.index"))
    return render_template("inventario/zone/new.html", USER=user)


@app.route("/inventario/zone/<rid>", methods=["GET"])
@with_auth("inventario:read")
def zone__get(user, rid):
    zone = DB_INVENTARIO_ZONA.get_by_id(str(rid))
    return render_template(
        "inventario/zone/get.html",
        zone=zone,
        rid=rid,
        USER=user
    )


@app.route("/inventario/zone/<rid>/edit", methods=["GET", "POST"])
@with_auth("inventario:write")
def zone__edit(user, rid):
    receta = DB_INVENTARIO_ZONA.get_by_id(str(rid))
    if request.method == "POST":
        DB_INVENTARIO_ZONA.update_by_id(
            str(rid),
            {
                "Nombre": request.form.get("Nombre", receta["Nombre"]),
                "Codigo": request.form.get("Codigo", receta["Codigo"]),
                "Notas": request.form.get("Notas", receta["Notas"]),
            }
        )
        return redirect(url_for("Inventario.index"))
    return render_template("inventario/zone/edit.html", zone=zone, rid=rid, USER=user)


@app.route("/inventario/zone/<rid>/del", methods=["GET", "POST"])
@with_auth("inventario:delete")
def zone__del(user, rid):
    if request.method == "POST" and request.form.get("deletecapcha") == "ELIMINAR":
        DB_INVENTARIO_ZONA.delete_by_id(str(rid))
        return redirect(url_for("inventario.index"))
    return render_template("confirmDeletion.html", USER=user, item="Elemento de Inventario")
