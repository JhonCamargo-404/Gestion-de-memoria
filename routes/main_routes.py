from flask import Blueprint, render_template, request, redirect, url_for, session
from services.simulador_service import SimuladorService
from memory.process import Proceso
from memory.memory_manager import MemoryManager

main_routes = Blueprint("main", __name__)

procesos = [
    Proceso("App1", 0x08000000, {"varX": 0x0012, "contador": 0x0100}, 2, "fijo"),
    Proceso("App2", 0x10000000, {"buffer": 0x0200, "resultado": 0x0300}, 3, "variable"),
    Proceso("App3", 0x20000000, {"temp": 0x0040, "flag": 0x0100}, 1, "fijo"),
    Proceso("App4", 0x30000000, {"pos": 0x0050, "limit": 0x0090}, 4, "variable"),
    Proceso("App5", 0x40000000, {"msg": 0x0020, "code": 0x0080}, 2, "fijo"),
]

gestor_memoria_global = None

def obtener_procesos_seleccionados(nombres):
    return [p for p in procesos if p.nombre in nombres]

@main_routes.route("/")
def index():
    global gestor_memoria_global
    gestor_memoria_global = None
    session.clear()
    return render_template("index.html", procesos=procesos)

@main_routes.route("/traducir", methods=["POST"])
def traducir():
    global gestor_memoria_global
    gestor_memoria_global = None
    for proceso in procesos:
        proceso.tabla_paginas = {}

    nombres_procesos = request.form.getlist("procesos")
    algoritmo = request.form.get("algoritmo", "FIFO")
    marcos = int(request.form.get("marcos", 3))
    modo_paso = "modo_paso" in request.form

    session["procesos"] = nombres_procesos
    session["algoritmo"] = algoritmo
    session["marcos"] = marcos
    session["modo_paso"] = modo_paso

    if modo_paso:
        pasos = [(p.nombre, var) for p in obtener_procesos_seleccionados(nombres_procesos) for var in p.tabla_simbolos]
        session["cola_pasos"] = pasos
        session["paso_actual"] = 0
        gestor_memoria_global = MemoryManager(num_marcos=marcos, algoritmo=algoritmo)
        return redirect(url_for("main.paso"))

    service = SimuladorService()
    return service.ejecutar_simulacion(nombres_procesos, procesos, algoritmo, marcos)

@main_routes.route("/paso")
def paso():
    global gestor_memoria_global
    service = SimuladorService()
    return service.ejecutar_paso(session, procesos, gestor_memoria_global)
