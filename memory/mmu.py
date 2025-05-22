PAGE_SIZE = 4096  # Tamaño fijo de página: 4KB

def dividir_direccion_virtual(direccion_virtual):
    """
    Divide una dirección virtual en número de página y offset.
    :param direccion_virtual: Dirección virtual completa
    :return: (numero_pagina, offset)
    """
    pagina = direccion_virtual // PAGE_SIZE
    offset = direccion_virtual % PAGE_SIZE
    return pagina, offset

def traducir_direccion_con_gestion(proceso, direccion_virtual, gestor_memoria):
    """
    Simula la traducción de una dirección virtual a física con gestión de memoria incluida.
    :param proceso: Objeto Proceso
    :param direccion_virtual: Dirección virtual solicitada
    :param gestor_memoria: Objeto MemoryManager
    :return: (direccion_fisica, numero_pagina, offset)
    """
    pagina, offset = dividir_direccion_virtual(direccion_virtual)
    pid = id(proceso)

    # Verificar si la página ya está en la tabla de páginas del proceso
    if pagina not in proceso.tabla_paginas:
        marco = gestor_memoria.cargar_pagina(proceso, pagina)
        proceso.asignar_marco(pagina, marco)
    else:
        marco = proceso.tabla_paginas[pagina]
        gestor_memoria.actualizar_lru(pid, pagina)

    direccion_fisica = marco * PAGE_SIZE + offset
    return direccion_fisica, pagina, offset

def obtener_info_traduccion(direccion_virtual):
    """
    Devuelve los componentes de una dirección virtual en texto para explicación.
    """
    pagina, offset = dividir_direccion_virtual(direccion_virtual)
    return {
        "direccion_virtual": hex(direccion_virtual),
        "pagina": pagina,
        "offset": offset
    }
