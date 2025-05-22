from flask import Flask, render_template, request, redirect, url_for, session
from memory.process import Proceso
from memory.memory_manager import MemoryManager
from memory.mmu import traducir_direccion_con_gestion, obtener_info_traduccion

app = Flask(__name__)
app.secret_key = "simulador_memoria"

# Crear proceso de prueba
tabla_simbolos = {
    "varX": 0x0012,
    "contador": 0x0100,
    "buffer": 0x0200,
    "resultado": 0x0300
}

proceso_demo = Proceso(
    nombre="App1",
    base_virtual=0x08000000,
    tabla_simbolos=tabla_simbolos
)

@app.route("/")
def index():
    return render_template("index.html", variables=list(tabla_simbolos.keys()))

@app.route("/traducir", methods=["POST"])
def traducir():
    variable = request.form["variable"]
    algoritmo = request.form.get("algoritmo", "FIFO")
    marcos = int(request.form.get("marcos", 3))
    modo_paso = "modo_paso" in request.form

    # Guardar en sesión
    session["variable"] = variable
    session["algoritmo"] = algoritmo
    session["marcos"] = marcos
    session["modo_paso"] = modo_paso

    if modo_paso:
        return redirect(url_for("paso_1"))
    else:
        gestor_memoria = MemoryManager(num_marcos=marcos, algoritmo=algoritmo)
        direccion_virtual = proceso_demo.obtener_direccion_virtual(variable)
        direccion_fisica, pagina, offset = traducir_direccion_con_gestion(
            proceso_demo, direccion_virtual, gestor_memoria
        )

        resultado = {
            "variable": variable,
            "direccion_virtual": hex(direccion_virtual),
            "pagina": pagina,
            "offset": offset,
            "direccion_fisica": hex(direccion_fisica),
            "estado_memoria": gestor_memoria.obtener_estado(),
            "tabla_paginas": proceso_demo.obtener_tabla_paginas(),
            "algoritmo": algoritmo,
            "marcos": marcos
        }

        return render_template("resultado.html", resultado=resultado)

@app.route("/paso1")
def paso_1():
    variable = session.get("variable")
    algoritmo = session.get("algoritmo")
    marcos = session.get("marcos")

    info = {
        "mensaje": f"Buscando la variable '{variable}' en la tabla de símbolos...",
        "siguiente": url_for("paso_2"),
        "paso": 1
    }
    return render_template("paso.html", info=info)

@app.route("/paso2")
def paso_2():
    variable = session.get("variable")
    direccion_virtual = proceso_demo.obtener_direccion_virtual(variable)
    pagina, offset = direccion_virtual // 4096, direccion_virtual % 4096

    session["direccion_virtual"] = direccion_virtual
    session["pagina"] = pagina
    session["offset"] = offset

    info = {
        "mensaje": f"Dirección virtual calculada: {hex(direccion_virtual)}. Página: {pagina}, Offset: {offset}",
        "siguiente": url_for("paso_3"),
        "paso": 2
    }
    return render_template("paso.html", info=info)

@app.route("/paso3")
def paso_3():
    algoritmo = session.get("algoritmo")
    marcos = session.get("marcos")
    direccion_virtual = session.get("direccion_virtual")

    gestor_memoria = MemoryManager(num_marcos=marcos, algoritmo=algoritmo)
    direccion_fisica, pagina, offset = traducir_direccion_con_gestion(
        proceso_demo, direccion_virtual, gestor_memoria
    )

    resultado = {
        "variable": session.get("variable"),
        "direccion_virtual": hex(direccion_virtual),
        "pagina": pagina,
        "offset": offset,
        "direccion_fisica": hex(direccion_fisica),
        "estado_memoria": gestor_memoria.obtener_estado(),
        "tabla_paginas": proceso_demo.obtener_tabla_paginas(),
        "algoritmo": algoritmo,
        "marcos": marcos
    }

    return render_template("resultado.html", resultado=resultado)

if __name__ == "__main__":
    app.run(debug=True)
