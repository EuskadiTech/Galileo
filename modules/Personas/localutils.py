from .models import DB_PERSONAS
from flask import redirect, url_for, request, g
from functools import wraps

#region Auth
class UnknownCodeError(Exception):
    pass
class PinRequired(Exception):
    pass
class InvalidPin(Exception):
    pass
class LoggedOutError(Exception):
    pass
class NotAllowed(Exception):
    pass
class PersonAuth:
    def __init__(self, code: str, pin: str = ""):
        self.userCode = code
        self.userPin = pin
    def isLoggedIn(self, needsRole: str = ""):
        def query(data):
            if data["Codigo"] == str(self.userCode):
                return True
        if self.userCode == "UNK":
            raise LoggedOutError("No has iniciado sesión")
        keys = list(DB_PERSONAS.get_by_query(query).keys())
        if len(keys) < 1:
            raise UnknownCodeError("El Usuario no existe")
        self.rid = str(keys[0])
        person = DB_PERSONAS.get_by_id(str(keys[0]))
        if person["PIN"] != "" and self.userPin == "":
            raise PinRequired("Este usuario requiere un PIN")
        if person["PIN"] != self.userPin.upper():
            raise InvalidPin("El PIN introducido no es correcto")
        if needsRole not in person["Roles"] and needsRole != "":
            if "admin" not in person["Roles"]:
                raise NotAllowed("No estas autorizado; Te falta el rol " + needsRole)
        self.u = person
        return True
#endregion

def with_auth(role: str = ""):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if DB_PERSONAS.get_all() == {}:
                return redirect(url_for("Personas.new", err = "Configura a un Administrador"))
            try:
                user = PersonAuth(request.cookies.get('AUTH_CODE', "UNK"), request.cookies.get('AUTH_PIN'))
                user.isLoggedIn(role)
            except Exception as e:
                return redirect(url_for("Personas.auth_scan", err=e.args))
            
            return f(user=user, *args, **kwargs)
        return decorated_function
    return decorator