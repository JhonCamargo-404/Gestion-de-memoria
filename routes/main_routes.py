from flask import Blueprint, render_template, request, redirect, url_for, session
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
    modo_paso = "modo_paso" in request.form

    session["procesos"] = nombres_procesos
    session["marcos"] = marcos
    session["modo_paso"] = modo_paso

    if modo_paso:
        pasos = []
        for p in procesos:
            if p.nombre in nombres_procesos:
                for var in p.tabla_simbolos:
                    pasos.append((p.nombre, var))
        session["cola_pasos"] = pasos
        session["paso_actual"] = 0
        return redirect(url_for("main_routes.paso"))

    resultado_fifo = service.ejecutar_simulacion_fifo(nombres_procesos, procesos, marcos)

    return render_template("index.html",
                           procesos=procesos,
                           resultados=resultado_fifo["resultados"],
                           flujo_ejecucion=resultado_fifo["flujo_ejecucion"],
                           estado_memoria=resultado_fifo["estado_memoria"],
                           estadisticas=resultado_fifo["estadisticas"],
                           algoritmo="FIFO",
                           marcos=marcos)

@main_routes.route("/paso")
def paso():
    from memory.memory_manager import MemoryManager
    from memory.mmu import traducir_direccion_con_gestion

    paso_actual = session.get("paso_actual", 0)
    cola = session.get("cola_pasos", [])
    if paso_actual >= len(cola):
        return redirect(url_for("main_routes.index"))

    nombre_proc, variable = cola[paso_actual]
    proceso = next(p for p in procesos if p.nombre == nombre_proc)
    marcos = session.get("marcos", 3)

    if "gestor_memoria_global" not in session:
        session["gestor_memoria_global"] = {}

    if "memoria_fisica" not in session["gestor_memoria_global"]:
        session["gestor_memoria_global"] = MemoryManager(num_marcos=marcos, algoritmo="FIFO")

    gestor_memoria = session["gestor_memoria_global"]

    direccion_virtual = proceso.obtener_direccion_virtual(variable)
    estado_antes = set((pid, pag) for pid, pag in gestor_memoria.swap)
    tabla_paginas_antes = dict(proceso.tabla_paginas)

    direccion_fisica, pagina, offset = traducir_direccion_con_gestion(proceso, direccion_virtual, gestor_memoria)
    marco = proceso.tabla_paginas[pagina]
    estado_despues = set((pid, pag) for pid, pag in gestor_memoria.swap)
    reemplazo = estado_despues - estado_antes
    expulsado = list(reemplazo)[0] if reemplazo else None
    hubo_fallo = pagina not in tabla_paginas_antes

    if hubo_fallo:
        if expulsado:
            explicacion = (
                f"El proceso {proceso.nombre} accedió a la dirección virtual {hex(direccion_virtual)}, "
                f"correspondiente a la página {pagina}. Esta página no estaba en memoria, "
                f"por lo tanto se produjo un fallo de página. "
                f"Se reemplazó la página {expulsado[1]} del proceso con ID {expulsado[0]} para liberar espacio."
            )
        else:
            explicacion = (
                f"El proceso {proceso.nombre} accedió a la dirección virtual {hex(direccion_virtual)}, "
                f"correspondiente a la página {pagina}. Esta página no estaba en memoria, "
                f"pero había marcos disponibles, así que fue cargada sin necesidad de reemplazo."
            )
    else:
        explicacion = (
            f"El proceso {proceso.nombre} accedió a la dirección virtual {hex(direccion_virtual)}, "
            f"y la página {pagina} ya estaba cargada en memoria (no hubo fallo de página)."
        )

    session["paso_actual"] = paso_actual + 1
    info = {
        "proceso": proceso.nombre,
        "variable": variable,
        "direccion_virtual": hex(direccion_virtual),
        "pagina": pagina,
        "offset": offset,
        "direccion_fisica": hex(direccion_fisica),
        "estado_memoria": gestor_memoria.obtener_estado(),
        "tabla_paginas": proceso.obtener_tabla_paginas(),
        "explicacion": explicacion,
        "fallo_pagina": hubo_fallo,
        "marco": marco,
        "siguiente": url_for("main_routes.paso"),
        "ultimo": paso_actual + 1 == len(cola)
    }

    return render_template("paso.html", info=info)
