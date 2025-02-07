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
import modules.Personas
import modules.Personas.localutils
import utils
from utils import USERDATA_DIR
import modules
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
def index(user):
    return render_template("index.html")


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


app.register_blueprint(modules.ComedorBlueprint)
app.register_blueprint(modules.ResumenDiarioBlueprint)
app.register_blueprint(modules.RecetasBlueprint)
app.register_blueprint(modules.PersonasBlueprint)
app.register_blueprint(modules.CafeBlueprint)
app.register_blueprint(modules.AdminBlueprint)

if __name__ == "__main__":
    if utils.os.environ.get("GAL_DOCKERTUNNEL_MYURL") != None:
        tunnel = utils.DirectTunnel(
            utils.os.environ.get("GAL_DOCKERTUNNEL_MYURL"),
            utils.os.environ.get("GAL_DOCKERTUNNEL_ORCHURL", "https://grp.naiel.fyi"),
        )
    else:
        tunnel = utils.PinggyTunnel()
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
    if getattr(utils.sys, "frozen", False):
        HOST = "127.0.0.1"
    else:
        HOST = "0.0.0.0"

    config = utils.get_config()

    BASE = "/rd/" + config["Clave Proxy"]
    app.wsgi_app = DispatcherMiddleware(
        app.wsgi_app,
        {BASE: app.wsgi_app},
    )
    app.run(HOST, 8129, False)
    tunnel.stop()
