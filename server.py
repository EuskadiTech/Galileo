from flask import Flask, render_template, request
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.wrappers import Response
from os.path import join as path_join
import logging
import sentry_sdk
from launcher import get_local_version

import utils
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

## Disable Logging
log = logging.getLogger("werkzeug")
log.setLevel(logging.CRITICAL)
log.disabled = True


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", VERSION = get_local_version())


@app.route("/api/purgecache", methods=["GET"])
def api__purgecache():
    utils.clear_cache()
    return "Hecho!"


if __name__ == "__main__":
    # try:
    #     import pyi_splash
    #     pyi_splash.update_text('Sistema arrancado.')
    #     pyi_splash.close()
    # except:
    #     pass
    TIP = utils.start_tunnel()
    TUNNELIP0 = TIP[0]
    TUNNELIP1 = TIP[1]
    print(
        f"""
------------------------------------
Servidor arrancado

Puedes acceder a Galileo desde:
- http://127.0.0.1:8129/ (local)
- {TUNNELIP0} (caduca en 1 hora)
- {TUNNELIP1} (no caduca)


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
    app.register_blueprint(modules.ComedorBlueprint)
    app.register_blueprint(modules.ResumenDiarioBlueprint)
    app.register_blueprint(modules.RecetasBlueprint)
    app.run(HOST, 8129, False)
    utils.stop_tunnel()
