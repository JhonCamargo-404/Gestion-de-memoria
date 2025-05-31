from memory.memory_manager import MemoryManager
from memory.mmu import traducir_direccion_con_gestion

class SimuladorService:
    def ejecutar_simulacion_fifo(self, nombres_procesos, procesos, marcos):
        gestor_memoria = MemoryManager(num_marcos=marcos, algoritmo="FIFO")

        procesos_seleccionados = [p for p in procesos if p.nombre in nombres_procesos]
        resultados = []
        flujo_ejecucion = []

        for proceso in procesos_seleccionados:
            proceso.tabla_paginas.clear()
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

        return {
            "resultados": resultados,
            "flujo_ejecucion": flujo_ejecucion,
            "estado_memoria": estado_memoria,
            "estadisticas": estadisticas
        }
