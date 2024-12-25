from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    send_from_directory,
)
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.wrappers import Response
from os.path import join as path_join
import logging
import sentry_sdk
import webbrowser
from launcher import get_local_version

import modules.Personas
import modules.Personas.localutils
import utils
from utils import USERDATA_DIR
import modules

sentry_sdk.init(
    dsn="https://d77090e7896c5eb40bd1375e3e0e9539@o4508296642560000.ingest.de.sentry.io/4508296645443664",
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for tracing.
    traces_sample_rate=1.0,
    _experiments={
        # Set continuous_profiling_auto_start to True
        # to automatically start the profiler on when
        # possible.
        "continuous_profiling_auto_start": True,
    },
)

app = Flask(
    __name__,
    static_folder=path_join(utils.APPDATA_DIR, "static"),
    template_folder=path_join(utils.APPDATA_DIR, "templates"),
)


@app.context_processor
def inject_nav():
    nav = [
        {"text": "Inicio", "endpoint": "index"},
        {"text": "Resumen Diario", "endpoint": "ResumenDiario.index"},
        {
            "text": "SuperCafé",
            "endpoint": "Cafe.index",
            "subitems": [
                {"text": "Ajustes", "endpoint": "Cafe.config"},
                {"text": "Iniciar Comanda", "endpoint": "Cafe.select"},
                "divider",
                {"text": "Pant. Cocina", "endpoint": "Cafe.cocina"},
                {"text": "Pant. Pago", "endpoint": "Cafe.pago"},
            ],
        },
        {
            "text": "Comedor",
            "endpoint": "Comedor.index",
            "subitems": [
                {"text": "Menús descargados", "endpoint": "Comedor.index"},
                {"text": "Ver menú", "endpoint": "Comedor.byDayModal"},
                {"text": "Importar Menú", "endpoint": "Comedor.loadMenuModal"},
                "divider",
                {"text": "API: Menú de hoy", "endpoint": "Comedor.api__today"},
            ],
        },
        {
            "text": "Personas",
            "endpoint": "Personas.index",
            "subitems": [
                {"text": "Personas", "endpoint": "Personas.index"},
                {"text": "> Crear", "endpoint": "Personas.new"},
                {"text": "> Buscar por Codigo", "endpoint": "Personas.scan"},
                "divider",
                {"text": "Imprimir tarjetas", "endpoint": "Personas.print"},
            ],
        },
        {
            "text": "Recetas",
            "endpoint": "Recetas.index",
            "subitems": [
                {"text": "Recetas", "endpoint": "Recetas.index"},
                {"text": "> Crear", "endpoint": "Recetas.new"},
            ],
        },
    ]
    return dict(G_NAV=nav, G_CNAV=request.endpoint)


## Disable Logging
log = logging.getLogger("werkzeug")
log.setLevel(logging.CRITICAL)
log.disabled = True


@app.route("/", methods=["GET"])
@modules.Personas.localutils.with_auth()
def index(user):
    return render_template("index.html", VERSION=get_local_version(), USER=user)


@app.route("/api/purgecache", methods=["GET"])
def api__purgecache():
    utils.clear_cache()
    return "Hecho!"


@app.route("/status", methods=["GET"])
def status():
    utils.clear_cache()
    return "G-Serv is online."


@app.route("/uploads/<fspath>")
def get_upload(fspath):
    print("/uploads/" + fspath)
    print("FS " + USERDATA_DIR + "uploads" + "/" + fspath)
    return send_from_directory(USERDATA_DIR + "uploads", fspath)


app.register_blueprint(modules.ComedorBlueprint)
app.register_blueprint(modules.ResumenDiarioBlueprint)
app.register_blueprint(modules.RecetasBlueprint)
app.register_blueprint(modules.PersonasBlueprint)
app.register_blueprint(modules.CafeBlueprint)
app.register_blueprint(modules.AdminBlueprint)

if __name__ == "__main__":
    # try:
    #     import pyi_splash
    #     pyi_splash.update_text('Sistema arrancado.')
    #     pyi_splash.close()
    # except:
    #     pass
    tunnel = utils.Tunnel()
    TIP = tunnel.start()
    print(
        f"""
------------------------------------
Servidor arrancado

Puedes acceder a Galileo desde:
- http://127.0.0.1:8129/ (local)
- {TIP} (no caduca)


No cierres esta ventana.
------------------------------------
"""
    )
    HOST = "127.0.0.1"
    if utils.os.environ.get("ISDOCKER") != None:
        HOST = "0.0.0.0"

    config = utils.get_config()

    BASE = "/rd/" + config["Clave Proxy"]
    app.wsgi_app = DispatcherMiddleware(
        app.wsgi_app,
        {BASE: app.wsgi_app},
    )
    try:
        if utils.os.environ.get("ISDOCKER") == None:
            webbrowser.open_new_tab(TIP)
    except:
        print("[D] No se ha podido iniciar el navegador web.")
    app.run(HOST, 8129, False)
    tunnel.stop()
