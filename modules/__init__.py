MODS = [
    {"text": "ADM: Archivos", "endpoint": "Admin.files", "role": "admin"},
]
G_NAV = [
    {"text": "Inicio", "endpoint": "index", "role": "*"},
    {
        "text": "Resumen Diario",
        "endpoint": "ResumenDiario.index",
        "role": "resumendiario:_module",
    },
    {
        "text": "SuperCafé",
        "endpoint": "Cafe.index",
        "subitems": [
            {"text": "Ajustes", "endpoint": "Cafe.config", "role": "cafe:write"},
            {"text": "Iniciar Comanda", "endpoint": "Cafe.select", "role": "cafe:send"},
            {
                "text": "Historial del Clientx",
                "endpoint": "Personas.scan",
                "role": "personas:read",
            },
            "divider",
            {"text": "Pant. Cocina", "endpoint": "Cafe.cocina", "role": "cafe:cocina"},
            {"text": "Pant. Pago", "endpoint": "Cafe.pago", "role": "cafe:pago"},
        ],
        "role": "cafe:_module",
    },
    {
        "text": "Comedor",
        "endpoint": "Comedor.index",
        "subitems": [
            {
                "text": "Menús descargados",
                "endpoint": "Comedor.index",
                "role": "comedor:read",
            },
            {
                "text": "Ver menú",
                "endpoint": "Comedor.byDayModal",
                "role": "comedor:read",
            },
            {
                "text": "Importar Menú",
                "endpoint": "Comedor.loadMenuModal",
                "role": "comedor:write",
            },
            "divider",
            {"text": "API: Menú de hoy", "endpoint": "Comedor.api__today", "role": "*"},
        ],
        "role": "comedor:_module",
    },
    {
        "text": "Personas",
        "endpoint": "Personas.index",
        "subitems": [
            {"text": "Personas", "endpoint": "Personas.index", "role": "personas:read"},
            {"text": "> Crear", "endpoint": "Personas.new", "role": "personas:write"},
            {
                "text": "> Buscar por Codigo",
                "endpoint": "Personas.scan",
                "role": "personas:read",
            },
            "divider",
            {
                "text": "Imprimir tarjetas",
                "endpoint": "Personas.printcards",
                "role": "personas:read",
            },
            {
                "text": "Imprimir pegatinas",
                "endpoint": "Personas.printstickers",
                "role": "personas:read",
            },
            "divider",
            {
                "text": "Regiones",
                "endpoint": "Personas.regiones",
                "role": "personas:read",
            },
        ],
        "role": "personas:_module",
    },
    {
        "text": "Modulos",
        "subitems": MODS,
        "role": "*",
    },
]

G_PERMS = {"Sistema": []}


def addnav(nav):
    G_NAV.append(nav)

def addautonav(nav):
    MODS.append(nav)


def addperm(app, label, role):
    if G_PERMS.get(app) == None:
        G_PERMS[app] = []
    G_PERMS[app].append({"label": label, "role": role})


addperm("Sistema", "Admin", "admin")

