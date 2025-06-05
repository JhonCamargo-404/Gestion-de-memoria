import os
import json
from flask import Blueprint, render_template, request, redirect, session, jsonify
from memory.process import Proceso
from services.simulador_service import SimuladorService

main_routes = Blueprint("main_routes", __name__)
service = SimuladorService()
archivo_procesos = "procesos.json"

procesos = []

# ------------------------------
# FUNCIONES DE CARGA Y GUARDADO
# ------------------------------
def cargar_procesos_desde_archivo():
    """
    Carga la lista de procesos desde un archivo JSON.
    Si el archivo no existe, inicializa una lista de procesos por defecto.
    """
    global procesos
    if not os.path.exists(archivo_procesos):
        procesos = [
            Proceso("EditorTexto", 0x08000000, {"varX": 0x0012, "contador": 0x0100}, 2, "fijo"),
            Proceso("Compilador", 0x10000000, {"buffer": 0x0200, "resultado": 0x0300}, 3, "variable"),
            Proceso("Logger",     0x20000000, {"temp": 0x0040, "flag": 0x0100}, 1, "fijo"),
            Proceso("Juego",      0x30000000, {"pos": 0x0050, "limit": 0x0090}, 4, "variable"),
            Proceso("ClienteRed", 0x40000000, {"msg": 0x0020, "code": 0x0080}, 2, "fijo"),
        ]
    else:
        with open(archivo_procesos, "r") as f:
            datos = json.load(f)
            procesos = [Proceso(
                p["nombre"],
                p["base_virtual"],
                p["tabla_simbolos"],
                p["tamano_paginas"],
                p["esquema_carga"]
            ) for p in datos]

def guardar_todos_los_procesos():
    """
    Guarda todos los procesos actuales en el archivo JSON.
    """
    datos_limpios = [
        {
            "nombre": p.nombre,
            "base_virtual": p.base_virtual,
            "tabla_simbolos": p.tabla_simbolos,
            "tamano_paginas": p.tamano_paginas,
            "esquema_carga": p.esquema_carga
        } for p in procesos
    ]
    with open(archivo_procesos, "w") as f:
        json.dump(datos_limpios, f, indent=4)

def guardar_proceso_en_archivo(proceso):
    """
    Agrega un nuevo proceso a la lista y lo guarda en el archivo JSON.
    Args:
        proceso (Proceso): Proceso a guardar.
    """
    procesos.append(proceso)
    guardar_todos_los_procesos()

# ------------------------------
# RUTAS FLASK
# ------------------------------
@main_routes.route("/")
def index():
    """
    Ruta principal. Limpia la sesión y muestra la página principal con la lista de procesos.
    """
    session.clear()
    return render_template("index.html", procesos=procesos)

@main_routes.route("/traducir", methods=["POST"])
def traducir():
    """
    Ruta para traducir direcciones virtuales a físicas usando el simulador.
    Reinicia las tablas de páginas de los procesos y ejecuta la simulación FIFO.
    """
    for proceso in procesos:
        proceso.tabla_paginas = {}

    nombres_procesos = request.form.getlist("procesos")
    marcos = int(request.form.get("marcos", 3))

    session["procesos"] = nombres_procesos
    session["marcos"] = marcos

    resultado_fifo = service.ejecutar_simulacion_fifo(nombres_procesos, procesos, marcos)

    return render_template("index.html",
                           procesos=procesos,
                           resultados=resultado_fifo["resultados"],
                           flujo_ejecucion=resultado_fifo["flujo_ejecucion"],
                           estado_memoria=resultado_fifo["estado_memoria"],
                           estadisticas=resultado_fifo["estadisticas"],
                           algoritmo="FIFO",
                           marcos=marcos)

@main_routes.route("/agregar_proceso_ajax", methods=["POST"])
def agregar_proceso_ajax():
    """
    Ruta para agregar un nuevo proceso mediante una petición AJAX.
    Recibe los datos del formulario, crea el proceso y lo guarda.
    Devuelve el HTML del checkbox para el nuevo proceso.
    """
    nombre = request.form["nombre"]
    base_virtual = int(request.form["base_virtual"], 16)
    paginas = int(request.form["paginas"])
    esquema = request.form["esquema"]
    variables_raw = request.form["variables"].replace(" ", "").split(",")

    tabla_simbolos = {}
    for entrada in variables_raw:
        if ":" not in entrada:
            continue
        nombre_var, offset_hex = entrada.split(":")
        try:
            tabla_simbolos[nombre_var] = int(offset_hex, 16)
        except ValueError:
            continue

    nuevo_proceso = Proceso(nombre, base_virtual, tabla_simbolos, paginas, esquema)
    guardar_proceso_en_archivo(nuevo_proceso)

    checkbox_html = generar_checkbox_html(nuevo_proceso)
    return jsonify({"checkbox_html": checkbox_html})

# ------------------------------
# FUNCIONES DE RENDER HTML
# ------------------------------
def generar_checkbox_html(proceso):
    """
    Genera el HTML para el checkbox de selección de un proceso.
    Args:
        proceso (Proceso): Proceso para el cual generar el checkbox.
    Returns:
        str: HTML del checkbox.
    """
    return f"""
    <div class=\"form-control\">
        <label>
            <input type=\"checkbox\" name=\"procesos\" value=\"{proceso.nombre}\">
            <strong>{proceso.nombre}</strong><br>
            <small>Tamaño: {proceso.tamano_paginas} páginas - Esquema: {proceso.esquema_carga}</small>
        </label>
    </div>
    """
