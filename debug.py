from server import app

if __name__ == "__main__":
    # try:
    #     import pyi_splash
    #     pyi_splash.update_text('Sistema arrancado.')
    #     pyi_splash.close()
    # except:
    #     pass
    print(
        """
------------------------------------
Servidor arrancado

Puedes acceder a Galileo desde:
- http://{IP}:8129/

No cierres esta ventana.
    MODO DEBUG - NO USAR EN PROD
------------------------------------
"""
    )
    app.run("0.0.0.0", 8129, True)
