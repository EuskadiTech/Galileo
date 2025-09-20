from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    send_from_directory,
)
from werkzeug.wrappers import Response
from os.path import join as path_join
import logging
import sentry_sdk
import utils
from utils import USERDATA_DIR, check_path
import modules
import modules.Comedor.views
import modules.ResumenDiario.views
import modules.Personas.views
import modules.Cafe.views
import modules.Admin.views

from modules.AutoModule.localutils import load_from_dir

from flask_qrcode import QRcode

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
QRcode(app)

@app.context_processor
def inject_nav():
    return dict(G_NAV=modules.G_NAV, G_CNAV=request.endpoint)


## Disable Logging
log = logging.getLogger("werkzeug")
log.setLevel(logging.CRITICAL)
log.disabled = True


@app.route("/", methods=["GET"])
@modules.Personas.localutils.with_auth()
def index():
    return render_template("_layout.html")


@app.route("/api/purgecache", methods=["GET"])
def api__purgecache():
    utils.clear_cache()
    return "Hecho!"


@app.route("/status", methods=["GET"])
def status():
    utils.clear_cache()
    return "G-Serv is online."


@app.route("/uploads/<path:path>")
def get_upload(path):
    return send_from_directory(USERDATA_DIR + "uploads", path)

print("Cargando modulo: (incrustado)")
app.register_blueprint(modules.Comedor.views.app)
app.register_blueprint(modules.ResumenDiario.views.app)
app.register_blueprint(modules.Personas.views.app)
app.register_blueprint(modules.Cafe.views.app)
app.register_blueprint(modules.Admin.views.app)

check_path("mods")
for mod in load_from_dir():
    app.register_blueprint(mod)

if __name__ == "__main__":
    print(
        """
------------------------------------
Servidor arrancado

Puedes acceder a Galileo desde:
- http://127.0.0.1:8129/ (local)


No cierres esta ventana.
------------------------------------
"""
    )
    if getattr(utils.sys, "frozen", False):
        HOST = "127.0.0.1"
    else:
        HOST = "0.0.0.0"

    app.run(HOST, 8129, False)
