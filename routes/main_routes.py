from flask import Blueprint, render_template, request, session
from memory.process import Proceso
from services.simulador_service import SimuladorService

main_routes = Blueprint("main_routes", __name__)
service = SimuladorService()

procesos = [
    Proceso("App1", 0x08000000, {"varX": 0x0012, "contador": 0x0100}, 2, "fijo"),
    Proceso("App2", 0x10000000, {"buffer": 0x0200, "resultado": 0x0300}, 3, "variable"),
    Proceso("App3", 0x20000000, {"temp": 0x0040, "flag": 0x0100}, 1, "fijo"),
    Proceso("App4", 0x30000000, {"pos": 0x0050, "limit": 0x0090}, 4, "variable"),
    Proceso("App5", 0x40000000, {"msg": 0x0020, "code": 0x0080}, 2, "fijo"),
]

@main_routes.route("/")
def index():
    session.clear()
    return render_template("index.html", procesos=procesos)

@main_routes.route("/traducir", methods=["POST"])
def traducir():
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
