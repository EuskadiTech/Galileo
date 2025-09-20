from utils import DateParser
from .models import DB_COMEDOR
import csv


def list_comedor():
    return DB_COMEDOR.get_all()


def list_comedor_months():
    out = {}
    m = DB_COMEDOR.get_all()
    for value in m.values():
        month = value["month"]
        menu = value["menu"]
        out[month] = month
    return out


def list_comedor_menus():
    out = {}
    m = DB_COMEDOR.get_all()
    for value in m.values():
        month = value["month"]
        menu = value["menu"]
        out[menu] = menu
    return out


def list_comedor_monthMenu():
    out = {}
    m = DB_COMEDOR.get_all()
    for value in m.values():
        month = value["month"]
        menu = value["menu"]
        if out.get(month) == None:
            out[month] = {}
        out[month][menu] = value
    return out


def fromDay_comedor(day = None, menu: str = "*"):
    if day == None:
        day = DateParser().pretty_day_code()
    out = {}
    month = day.split("-")[0] + "-" + day.split("-")[1]
    dayc = day

    def query(data):
        if data["month"] != month:
            return False
        if data["menu"] != menu and menu != "*":
            return False
        return True

    previous = DB_COMEDOR.get_by_query(query).values()
    for menu in previous:
        if menu["data"].get(dayc) != None:
            out[menu["menu"]] = menu["data"][dayc]
    return out


def load_comedor(content: str):
    out_meta = {}
    meta = content.split("---")[0]
    metareader = csv.DictReader(meta.splitlines(), delimiter=";")
    for row in metareader:
        out_meta = row

    def query(data):
        if data["month"] != out_meta["YYYY-MM"]:
            return False
        if data["menu"] != out_meta["Menu"]:
            return False
        return True

    previous = DB_COMEDOR.get_by_query(query)
    if previous != {}:
        for key in previous.keys():
            DB_COMEDOR.delete_by_id(key)
    data = content.split("---")[1].strip()
    datareader = csv.DictReader(data.splitlines(), delimiter=";")
    out_data = {}
    for row in datareader:
        out_data[row["YYYY-MM-DD"]] = row
    result = {"meta": out_meta, "data": out_data}
    dbi = {
        "menu": out_meta["Menu"],
        "month": out_meta["YYYY-MM"],
        "meta": out_meta,
        "data": out_data,
        "source_plain": content,
    }
    DB_COMEDOR.add(dbi)
    return result, dbi
