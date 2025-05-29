from flask import Flask, render_template, request, redirect, url_for, session
from memory.process import Proceso
from memory.memory_manager import MemoryManager
from memory.mmu import traducir_direccion_con_gestion, obtener_info_traduccion

app = Flask(__name__)
app.secret_key = "simulador_memoria"

# Procesos de ejemplo (configurables)
procesos = [
    Proceso("App1", 0x08000000, {"varX": 0x0012, "contador": 0x0100}, 2, "fijo"),
    Proceso("App2", 0x10000000, {"buffer": 0x0200, "resultado": 0x0300}, 3, "variable"),
    Proceso("App3", 0x20000000, {"temp": 0x0040, "flag": 0x0100}, 1, "fijo"),
    Proceso("App4", 0x30000000, {"pos": 0x0050, "limit": 0x0090}, 4, "variable"),
    Proceso("App5", 0x40000000, {"msg": 0x0020, "code": 0x0080}, 2, "fijo"),
]

# Buscar procesos por nombre
def obtener_procesos_seleccionados(nombres):
    return [p for p in procesos if p.nombre in nombres]

@app.route("/")
def index():
    return render_template("index.html", procesos=procesos)

@app.route("/traducir", methods=["POST"])
def traducir():
    nombres_procesos = request.form.getlist("procesos")
    algoritmo = request.form.get("algoritmo", "FIFO")
    marcos = int(request.form.get("marcos", 3))
    modo_paso = "modo_paso" in request.form

    # Guardar en sesión
    session["procesos"] = nombres_procesos
    session["algoritmo"] = algoritmo
    session["marcos"] = marcos
    session["modo_paso"] = modo_paso

    procesos_seleccionados = obtener_procesos_seleccionados(nombres_procesos)
    gestor_memoria = MemoryManager(num_marcos=marcos, algoritmo=algoritmo)

    resultados = []

    for proceso in procesos_seleccionados:
        for variable in proceso.tabla_simbolos:
            direccion_virtual = proceso.obtener_direccion_virtual(variable)
            direccion_fisica, pagina, offset = traducir_direccion_con_gestion(
                proceso, direccion_virtual, gestor_memoria
            )

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

    return render_template("resultado.html",
                           resultados=resultados,
                           estado_memoria=estado_memoria,
                           estadisticas=estadisticas,
                           algoritmo=algoritmo,
                           marcos=marcos)

if __name__ == "__main__":
    app.run(debug=True)
