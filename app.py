from flask import Flask, render_template, request, redirect, url_for, session
from memory.process import Proceso
from memory.memory_manager import MemoryManager
from memory.mmu import traducir_direccion_con_gestion

app = Flask(__name__)
app.secret_key = "simulador_memoria"

# Variable global para el modo paso a paso
gestor_memoria_global = None

# Procesos disponibles
procesos = [
    Proceso("App1", 0x08000000, {"varX": 0x0012, "contador": 0x0100}, 2, "fijo"),
    Proceso("App2", 0x10000000, {"buffer": 0x0200, "resultado": 0x0300}, 3, "variable"),
    Proceso("App3", 0x20000000, {"temp": 0x0040, "flag": 0x0100}, 1, "fijo"),
    Proceso("App4", 0x30000000, {"pos": 0x0050, "limit": 0x0090}, 4, "variable"),
    Proceso("App5", 0x40000000, {"msg": 0x0020, "code": 0x0080}, 2, "fijo"),
]

# Obtener procesos seleccionados
def obtener_procesos_seleccionados(nombres):
    return [p for p in procesos if p.nombre in nombres]

@app.route("/")
def index():
    return render_template("index.html", procesos=procesos)

@app.route("/traducir", methods=["POST"])
def traducir():
    global gestor_memoria_global

    nombres_procesos = request.form.getlist("procesos")
    algoritmo = request.form.get("algoritmo", "FIFO")
    marcos = int(request.form.get("marcos", 3))
    modo_paso = "modo_paso" in request.form

    session["procesos"] = nombres_procesos
    session["algoritmo"] = algoritmo
    session["marcos"] = marcos
    session["modo_paso"] = modo_paso

    if modo_paso:
        pasos = []
        for p in obtener_procesos_seleccionados(nombres_procesos):
            for var in p.tabla_simbolos:
                pasos.append((p.nombre, var))
        session["cola_pasos"] = pasos
        session["paso_actual"] = 0
        gestor_memoria_global = MemoryManager(num_marcos=marcos, algoritmo=algoritmo)
        return redirect(url_for("paso"))

    procesos_seleccionados = obtener_procesos_seleccionados(nombres_procesos)
    gestor_memoria = MemoryManager(num_marcos=marcos, algoritmo=algoritmo)
    resultados = []
    flujo_ejecucion = []

    for proceso in procesos_seleccionados:
        for variable in proceso.tabla_simbolos:
            direccion_virtual = proceso.obtener_direccion_virtual(variable)
            estado_antes = set((pid, pag) for pid, pag in gestor_memoria.swap)
            direccion_fisica, pagina, offset = traducir_direccion_con_gestion(
                proceso, direccion_virtual, gestor_memoria
            )

            estado_despues = set((pid, pag) for pid, pag in gestor_memoria.swap)
            swap_ocurrido = len(estado_despues) > len(estado_antes)

            reemplazo = estado_despues - estado_antes
            flujo_ejecucion.append({
                "proceso": proceso.nombre,
                "variable": variable,
                "swap": bool(reemplazo),
                "expulsado": list(reemplazo)[0] if reemplazo else None,
                "direccion_virtual": hex(direccion_virtual),
                "direccion_fisica": hex(direccion_fisica),
                "pagina": pagina,
                "offset": offset
            })

            resultados.append({
                "proceso": proceso.nombre,
                "variable": variable,
                "direccion_virtual": hex(direccion_virtual),
                "pagina": pagina,
                "offset": offset,
                "direccion_fisica": hex(direccion_fisica),
                "tabla_paginas": proceso.obtener_tabla_paginas()
            })

    estado_memoria = gestor_memoria.obtener_estado()
    estadisticas = gestor_memoria.obtener_estadisticas()

    return render_template("index.html",
                           procesos=procesos,
                           resultados=resultados,
                           estado_memoria=estado_memoria,
                           estadisticas=estadisticas,
                           algoritmo=algoritmo,
                           marcos=marcos,
                           flujo_ejecucion=flujo_ejecucion)

@app.route("/paso")
def paso():
    global gestor_memoria_global

    paso_actual = session.get("paso_actual", 0)
    cola = session.get("cola_pasos", [])
    if paso_actual >= len(cola):
        return redirect(url_for("index"))  
    nombre_proc, variable = cola[paso_actual]
    proceso = next(p for p in procesos if p.nombre == nombre_proc)
    algoritmo = session.get("algoritmo", "FIFO")
    marcos = session.get("marcos", 3)
    if gestor_memoria_global is None:
        gestor_memoria_global = MemoryManager(num_marcos=marcos, algoritmo=algoritmo)
    gestor_memoria = gestor_memoria_global
    direccion_virtual = proceso.obtener_direccion_virtual(variable)
    direccion_fisica, pagina, offset = traducir_direccion_con_gestion(
        proceso, direccion_virtual, gestor_memoria
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
        "siguiente": url_for("paso"),
        "ultimo": paso_actual + 1 == len(cola)
    }

    return render_template("paso.html", info=info)

if __name__ == "__main__":
    app.run(debug=True)
