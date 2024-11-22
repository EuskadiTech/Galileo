from pysondb import PysonDB
from utils import USERDATA_DIR

DB_PERSONAS = PysonDB(USERDATA_DIR + "db.personas.axd")
DB_PERSONAS.add_new_key("SC_lastcomanda", {})
DB_PERSONAS.add_new_key("SC_Anilla", "Sin Anilla")