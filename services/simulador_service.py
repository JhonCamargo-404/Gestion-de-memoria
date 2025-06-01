from memory.memory_manager import MemoryManager
from memory.mmu import traducir_direccion_con_gestion

class SimuladorService:
    def generar_explicacion_paso(self, nombre_proceso, variable, direccion_virtual, pagina, offset,
                                  direccion_fisica, fallo_pagina, marco, expulsado=None, base_virtual=None):
        PAGE_SIZE = 4096
        html = []

        html.append(f"<p><strong>Proceso:</strong> {nombre_proceso}</p>")
        html.append(f"<p><strong>Variable:</strong> {variable}</p>")

        if base_virtual is not None:
            html.append(f"<p><strong>Cálculo de Dirección Virtual</strong></p>")
            html.append("<ul>")
            html.append(f"<li>Base virtual del proceso: {hex(base_virtual)} (decimal: {base_virtual})</li>")
            html.append(f"<li>Offset de la variable '{variable}': {hex(offset)} (decimal: {offset})</li>")
            html.append("</ul>")
            html.append(f"<div style='margin-left:1em;'>Dirección virtual = base virtual + offset</div>")
            html.append(f"<div style='margin-left:1em;'>{base_virtual} + {offset} = {direccion_virtual} = {hex(direccion_virtual)}</div>")

        html.append(f"<p><strong>División de la Dirección Virtual</strong></p>")
        html.append("<ul>")
        html.append(f"<li>Tamaño de página: {PAGE_SIZE} bytes</li>")
        html.append("</ul>")
        html.append("""
            <div style="margin-left:1em;">
                Número de página =  Dirección virtual ÷ Tamaño de página <br>
                Número de página =  {} ÷ {} = {}
            </div>
            <div style="margin-left:1em; margin-top:0.5em;">
                Offset = Dirección virtual mod Tamaño de página<br>
                Offset = {} mod {} = {}
            </div>
        """.format(direccion_virtual, PAGE_SIZE, pagina, direccion_virtual, PAGE_SIZE, offset))

        if fallo_pagina:
            html.append(f"<p><strong>Fallo de Página Detectado</strong></p>")
            html.append(f"<p>La página {pagina} no se encontraba en la tabla de páginas del proceso.</p>")
            if expulsado:
                pid_expulsado, pagina_expulsada = expulsado
                html.append(f"<li>Se aplicó la política FIFO. Se expulsó la página {pagina_expulsada} del proceso con ID {pid_expulsado} hacia swap.</li>")
            else:
                html.append("<li>Se cargó la nueva página en un marco libre.</li>")
            html.append(f"<li>La página {pagina} fue asignada al marco {marco}.</li></ul>")
        else:
            html.append(f"<p><strong>Acceso sin Fallo de Página</strong></p>")
            html.append(f"<p>La página {pagina} ya estaba cargada en memoria física.</p>")

        html.append(f"<p><strong>Cálculo de Dirección Física</strong></p>")
        html.append("""
            <div style="margin-left:1em;">
                Dirección física = marco × tamaño de página + offset<br>
                Dirección física = {} × {} + {} = {} = {}
            </div>
        """.format(marco, PAGE_SIZE, offset, direccion_fisica, hex(direccion_fisica)))

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
                    expulsado=expulsado,
                    base_virtual=proceso.base_virtual
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
