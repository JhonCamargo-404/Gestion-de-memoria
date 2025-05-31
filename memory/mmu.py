PAGE_SIZE = 4096 

def dividir_direccion_virtual(direccion_virtual):
    pagina = direccion_virtual // PAGE_SIZE
    offset = direccion_virtual % PAGE_SIZE
    return pagina, offset

def traducir_direccion_con_gestion(proceso, direccion_virtual, gestor_memoria):
    pagina, offset = dividir_direccion_virtual(direccion_virtual)
    pid = id(proceso)
    if pagina not in proceso.tabla_paginas:
        marco = gestor_memoria.cargar_pagina(proceso, pagina)
        proceso.asignar_marco(pagina, marco)
    else:
        marco = proceso.tabla_paginas[pagina]
        gestor_memoria.actualizar_lru(pid, pagina)

    direccion_fisica = marco * PAGE_SIZE + offset
    return direccion_fisica, pagina, offset

def obtener_info_traduccion(direccion_virtual):
    pagina, offset = dividir_direccion_virtual(direccion_virtual)
    return {
        "direccion_virtual": hex(direccion_virtual),
        "pagina": pagina,
        "offset": offset
    }
