from flask import render_template, redirect, url_for
from memory.memory_manager import MemoryManager
from memory.mmu import traducir_direccion_con_gestion

class SimuladorService:
    def ejecutar_simulacion(self, nombres_procesos, procesos, algoritmo, marcos):
        gestor_memoria = MemoryManager(num_marcos=marcos, algoritmo=algoritmo)
        flujo_ejecucion = []

        for proceso in [p for p in procesos if p.nombre in nombres_procesos]:
            for variable in proceso.tabla_simbolos:
                direccion_virtual = proceso.obtener_direccion_virtual(variable)
                estado_antes = set((pid, pag) for pid, pag in gestor_memoria.swap)
                tabla_paginas_antes = dict(proceso.tabla_paginas)

                direccion_fisica, pagina, offset = traducir_direccion_con_gestion(
                    proceso, direccion_virtual, gestor_memoria
                )
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

                flujo_ejecucion.append({
                    "proceso": proceso.nombre,
                    "variable": variable,
                    "swap": bool(reemplazo),
                    "expulsado": expulsado,
                    "direccion_virtual": hex(direccion_virtual),
                    "direccion_fisica": hex(direccion_fisica),
                    "pagina": pagina,
                    "offset": offset,
                    "explicacion": explicacion,
                    "fallo_pagina": hubo_fallo,
                    "marco": marco
                })

        estado_memoria = gestor_memoria.obtener_estado()
        estadisticas = gestor_memoria.obtener_estadisticas()

        return render_template("index.html",
                               procesos=procesos,
                               resultados=[],
                               estado_memoria=estado_memoria,
                               estadisticas=estadisticas,
                               algoritmo=algoritmo,
                               marcos=marcos,
                               flujo_ejecucion=flujo_ejecucion)

    def ejecutar_paso(self, session, procesos, gestor_memoria_global):
        paso_actual = session.get("paso_actual", 0)
        cola = session.get("cola_pasos", [])
        if paso_actual >= len(cola):
            return redirect(url_for("main.index"))

        nombre_proc, variable = cola[paso_actual]
        proceso = next(p for p in procesos if p.nombre == nombre_proc)
        algoritmo = session.get("algoritmo", "FIFO")
        marcos = session.get("marcos", 3)

        if gestor_memoria_global is None:
            gestor_memoria_global = MemoryManager(num_marcos=marcos, algoritmo=algoritmo)

        gestor_memoria = gestor_memoria_global
        direccion_virtual = proceso.obtener_direccion_virtual(variable)

        estado_antes = set((pid, pag) for pid, pag in gestor_memoria.swap)
        tabla_paginas_antes = dict(proceso.tabla_paginas)

        direccion_fisica, pagina, offset = traducir_direccion_con_gestion(
            proceso, direccion_virtual, gestor_memoria
        )
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
        return render_template("paso.html", info={
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
            "siguiente": url_for("main.paso"),
            "ultimo": paso_actual + 1 == len(cola)
        })
