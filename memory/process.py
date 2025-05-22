class Proceso:
    def __init__(self, nombre, base_virtual, tabla_simbolos):
        """
        :param nombre: Nombre del proceso (ej. "App1")
        :param base_virtual: Dirección base del espacio virtual (ej. 0x08000000)
        :param tabla_simbolos: Diccionario con las variables y sus offsets relativos
        """
        self.nombre = nombre
        self.base_virtual = base_virtual
        self.tabla_simbolos = tabla_simbolos  # {'varX': 0x0012, 'contador': 0x0100, ...}
        self.tabla_paginas = {}  # {numero_pagina: marco_fisico}

    def obtener_direccion_virtual(self, variable):
        """
        Dada una variable simbólica, calcula la dirección virtual sumando base + offset
        """
        if variable in self.tabla_simbolos:
            offset = self.tabla_simbolos[variable]
            return self.base_virtual + offset
        else:
            raise ValueError(f"Variable '{variable}' no encontrada en la tabla de símbolos.")

    def asignar_marco(self, pagina, marco):
        """
        Asocia una página virtual con un marco físico
        """
        self.tabla_paginas[pagina] = marco

    def obtener_tabla_paginas(self):
        """
        Devuelve una copia de la tabla de páginas para visualización
        """
        return dict(self.tabla_paginas)

    def __repr__(self):
        return f"Proceso({self.nombre}, base={hex(self.base_virtual)})"
