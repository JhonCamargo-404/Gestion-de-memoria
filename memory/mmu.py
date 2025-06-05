PAGE_SIZE = 4096 

def dividir_direccion_virtual(direccion_virtual):
    """
    Divide una dirección virtual en número de página y offset.
    Args:
        direccion_virtual (int): Dirección virtual a dividir.
    Returns:
        tuple: (pagina, offset)
    """
    pagina = direccion_virtual // PAGE_SIZE
    offset = direccion_virtual % PAGE_SIZE
    return pagina, offset

def traducir_direccion_con_gestion(proceso, direccion_virtual, gestor_memoria):
    """
    Traduce una dirección virtual a física, gestionando la carga de páginas si es necesario.
    Args:
        proceso: Objeto del proceso que solicita la traducción.
        direccion_virtual (int): Dirección virtual a traducir.
        gestor_memoria: Instancia del gestor de memoria.
    Returns:
        tuple: (direccion_fisica, pagina, offset)
    """
    pagina, offset = dividir_direccion_virtual(direccion_virtual)
    pid = id(proceso)
    if pagina not in proceso.tabla_paginas:
        # Si la página no está asignada, se carga en memoria y se asigna un marco
        marco = gestor_memoria.cargar_pagina(proceso, pagina)
        proceso.asignar_marco(pagina, marco)
    else:
        # Si ya está asignada, se actualiza LRU si corresponde
        marco = proceso.tabla_paginas[pagina]
        gestor_memoria.actualizar_lru(pid, pagina)

    direccion_fisica = marco * PAGE_SIZE + offset
    return direccion_fisica, pagina, offset

def obtener_info_traduccion(direccion_virtual):
    """
    Obtiene información desglosada de una dirección virtual.
    Args:
        direccion_virtual (int): Dirección virtual a analizar.
    Returns:
        dict: Información con dirección virtual, página y offset.
    """
    pagina, offset = dividir_direccion_virtual(direccion_virtual)
    return {
        "direccion_virtual": hex(direccion_virtual),
        "pagina": pagina,
        "offset": offset
    }
