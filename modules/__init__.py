G_NAV = [
    {"text": "Inicio", "endpoint": "index", "role": "*"},
    {"text": "Resumen Diario", "endpoint": "ResumenDiario.index", "role": "resumendiario:_module"},
    {
        "text": "SuperCafé",
        "endpoint": "Cafe.index",
        "subitems": [
            {"text": "Ajustes", "endpoint": "Cafe.config", "role": "cafe:write"},
            {"text": "Iniciar Comanda", "endpoint": "Cafe.select", "role": "cafe:send"},
            {
                "text": "Historial del Clientx",
                "endpoint": "Personas.scan",
                "role":  "personas:read",
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
            {"text": "Menús descargados", "endpoint": "Comedor.index", "role": "comedor:read"},
            {"text": "Ver menú", "endpoint": "Comedor.byDayModal", "role": "comedor:read"},
            {"text": "Importar Menú", "endpoint": "Comedor.loadMenuModal", "role": "comedor:write"},
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
            {"text": "> Buscar por Codigo", "endpoint": "Personas.scan", "role": "personas:read"},
            "divider",
            {"text": "Imprimir tarjetas", "endpoint": "Personas.printcards", "role": "personas:read"},
            {"text": "Imprimir pegatinas", "endpoint": "Personas.printstickers", "role": "personas:read"},
            "divider",
            {"text": "Regiones", "endpoint": "Personas.regiones", "role": "personas:read"},
        ],
        "role": "personas:_module",
    },
    {
        "text": "Recetas",
        "endpoint": "Recetas.index",
        "subitems": [
            {
                "text": "Recetas",
                "endpoint": "Recetas.index",
                "role": "recetas:read",
            },
            {"text": "> Crear", "endpoint": "Recetas.new", "role": "recetas:write"},
        ],
        "role": "recetas:_module",
    },
    {
        "text": "Inventario",
        "endpoint": "Inventario.index",
        "subitems": [
            {
                "text": "Partes",
                "endpoint": "Inventario.index",
                "role": "inventario:read",
            },
            {"text": "> Crear", "endpoint": "Inventario.new", "role": "inventario:write"},
        ],
        "role": "inventario:_module",
    },
    {
        "text": "Admin",
        "subitems": [
            {"text": "Archivos", "endpoint": "Admin.files", "role": "admin"},
        ],
        "role": "admin",
    },
    {"text": "Cerrar sesión", "endpoint": "Personas.auth_logout", "role": "*"},
]