from memory.memory_manager import MemoryManager
from memory.mmu import traducir_direccion_con_gestion

class SimuladorService:
    def generar_explicacion_paso(self, nombre_proceso, variable, direccion_virtual, pagina, offset,
                                  direccion_fisica, fallo_pagina, marco, expulsado=None):
        PAGE_SIZE = 4096
        html = []

        html.append(f"<p><strong>Proceso:</strong> {nombre_proceso}</p>")
        html.append(f"<p><strong>Variable:</strong> {variable}</p>")
        html.append(f"<p><strong>Dirección virtual:</strong> {hex(direccion_virtual)}</p>")

        html.append("<p><strong>Traducción de dirección virtual:</strong></p>")
        html.append("<ul>")
        html.append(f"<li><strong>Número de página:</strong> {direccion_virtual} // {PAGE_SIZE} = {pagina}</li>")
        html.append(f"<li><strong>Offset:</strong> {direccion_virtual} % {PAGE_SIZE} = {offset}</li>")
        html.append("</ul>")

        if fallo_pagina:
            html.append(f"<p><strong>Estado previo:</strong> la página {pagina} no se encontraba en la tabla de páginas del proceso, por lo tanto se produjo un <strong>fallo de página</strong>.</p>")

            html.append("<p><strong>Acción realizada:</strong></p>")
            html.append("<ul>")
            if expulsado:
                pid_expulsado, pagina_expulsada = expulsado
                html.append("<li>La memoria estaba llena, se aplicó el algoritmo FIFO.</li>")
                html.append(f"<li>Se expulsó la página {pagina_expulsada} del proceso con ID {pid_expulsado} hacia el área de swap.</li>")
            else:
                html.append("<li>Había marcos libres disponibles, por lo que la página fue cargada directamente sin reemplazo.</li>")
            html.append(f"<li>La página {pagina} fue asignada al marco{marco}.</li>")
            html.append("</ul>")
        else:
            html.append(f"<p><strong>Estado previo:</strong> la página {pagina} ya estaba cargada en memoria, no se generó fallo de página.</p>")
            html.append("<p><strong>Acción realizada:</strong></p>")
            html.append(f"<ul><li>Se accede directamente al marco {marco} ya asignado.</li></ul>")

        html.append("<p><strong>Cálculo de dirección física:</strong></p>")
        html.append("<ul>")
        html.append(f"<li>Dirección física = marco × tamaño de página + offset = {marco} × {PAGE_SIZE} + {offset} = {direccion_fisica}</li>")
        html.append(f"<li>Este valor decimal {direccion_fisica} se convierte a hexadecimal para representar la dirección física como {hex(direccion_fisica)}.</li>")
        html.append(f"<li><strong>Resultado final:</strong> dirección física = {hex(direccion_fisica)}</li>")
        html.append("</ul>")

        return "\n".join(html)

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

                explicacion = self.generar_explicacion_paso(
                    nombre_proceso=proceso.nombre,
                    variable=variable,
                    direccion_virtual=direccion_virtual,
                    pagina=pagina,
                    offset=offset,
                    direccion_fisica=direccion_fisica,
                    fallo_pagina=hubo_fallo,
                    marco=marco,
                    expulsado=expulsado
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
