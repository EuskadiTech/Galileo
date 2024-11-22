from .models import DB_PERSONAS
#region Auth
class UnknownCodeError(Exception):
    pass
class PinRequired(Exception):
    pass
class InvalidPin(Exception):
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
        keys = list(DB_PERSONAS.get_by_query(query).keys())
        if len(keys) < 1:
            raise UnknownCodeError("El Usuario no existe")
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
