from flask import Flask, redirect, request, Response
import requests

app = Flask(__name__)
URLS = {}
BASE_URL_RP = "https://rp.tech.eus/"
KO_TEMPLATE = """<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8" />
    <meta content="width=device-width,initial-scale=1" name="viewport" />
    <style>
      * {
        font-family: arial;
      }
      header {
        border: 1px solid #000;
        margin-bottom: 5px;
        font-size: large;
        font-weight: 600;
      }
      header a {
        color: white;
      }
      .red {
        background-color: red;
      }
    </style>
    <title>Galileo Proxy Disconnected</title>
    <meta http-equiv="refresh" content="10">
  </head>

  <body>
    <header style="background-color: #000; color: #fff">
      Galileo
    </header>
    <main>
      <center>
        <h1>Servidor Galileo Desconectado</h1>
        <h2>
          El servidor al que estabas intentando acceder no esta conectado al
          Proxy Galileo
        </h2>
        <h3>(Podria estar apagado, en reposo, o sin internet)</h3>
      </center>
    </main>
  </body>
</html>

"""


@app.route("/__rp/publish", methods=["POST"])
def publish():
    URLS[request.json["conid"]] = request.json["baseurl"]
    return {"url": BASE_URL_RP + "open/" + request.json["conid"]}


@app.route("/creq/<pid>/SuperAI/menu", methods=["POST"])
def creq__menuComedor(pid):
    f = request.files["file"]
    co = f.read()
    req = requests.post(
        "http://192.168.0.3:1880/endpoint/calcMenuAI",
        files={"file": co},
        data=request.form,
    )
    return req.text


@app.route("/open/<pid>")
def open(pid):
    return redirect("/rd/" + pid)


@app.route("/rd/<pid>/", methods=["GET", "POST"], defaults={"path": ""})
@app.route("/rd/<pid>/<path:path>", methods=["GET", "POST"])
def proxy(pid, path):
    try:
        SITE_NAME = URLS[pid]
        url = f"{SITE_NAME}/rd/{pid}/{path}"
        Allow = True
        if str(path).startswith("api"):
            Allow = False
        if request.method == "GET":
            resp = requests.get(url, params=request.args, allow_redirects=Allow)
            excluded_headers = [
                "content-encoding",
                "content-length",
                "transfer-encoding",
                "connection",
            ]
            headers = [
                (name, value)
                for (name, value) in resp.raw.headers.items()
                if name.lower() not in excluded_headers
            ]
            response = Response(resp.content, resp.status_code, headers)
            return response
        elif request.method == "POST":
            resp = requests.post(
                url,
                data=request.form,
                params=request.args,
                files=request.files,
                allow_redirects=Allow,
            )
            excluded_headers = [
                "content-encoding",
                "content-length",
                "transfer-encoding",
                "connection",
            ]
            headers = [
                (name, value)
                for (name, value) in resp.raw.headers.items()
                if name.lower() not in excluded_headers
            ]
            response = Response(resp.content, resp.status_code, headers)
            return response
    except KeyError:
        return KO_TEMPLATE
    except requests.exceptions.ConnectionError:
        return KO_TEMPLATE


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8229, debug=False)
