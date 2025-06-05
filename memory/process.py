class Proceso:
    def __init__(self, nombre, base_virtual, tabla_simbolos, tamano_paginas, esquema_carga="variable"):
        """
        Inicializa un proceso con su nombre, base virtual, tabla de símbolos, tamaño de página y esquema de carga.
        Args:
            nombre (str): Nombre del proceso.
            base_virtual (int): Dirección base virtual del proceso.
            tabla_simbolos (dict): Tabla de símbolos con variables y sus offsets.
            tamano_paginas (int): Tamaño de las páginas.
            esquema_carga (str): Esquema de carga de páginas (por defecto "variable").
        """
        self.nombre = nombre
        self.base_virtual = base_virtual
        self.tabla_simbolos = tabla_simbolos 
        self.tabla_paginas = {} 
        self.tamano_paginas = tamano_paginas
        self.esquema_carga = esquema_carga

    def obtener_direccion_virtual(self, variable):
        """
        Obtiene la dirección virtual de una variable a partir de la tabla de símbolos.
        Args:
            variable (str): Nombre de la variable.
        Returns:
            int: Dirección virtual de la variable.
        Raises:
            ValueError: Si la variable no está en la tabla de símbolos.
        """
        if variable in self.tabla_simbolos:
            offset = self.tabla_simbolos[variable]
            return self.base_virtual + offset
        else:
            raise ValueError(f"Variable '{variable}' no encontrada en la tabla de símbolos.")

    def asignar_marco(self, pagina, marco):
        """
        Asigna un marco físico a una página virtual en la tabla de páginas del proceso.
        Args:
            pagina (int): Número de página virtual.
            marco (int): Número de marco físico.
        """
        self.tabla_paginas[pagina] = marco

    def obtener_tabla_paginas(self):
        """
        Retorna una copia de la tabla de páginas del proceso.
        Returns:
            dict: Tabla de páginas {pagina: marco}.
        """
        return dict(self.tabla_paginas)

    def __repr__(self):
        """
        Representación en string del proceso para depuración.
        Returns:
            str: Representación del proceso.
        """
        return (
            f"Proceso({self.nombre}, base={hex(self.base_virtual)}, "
            f"tamano_paginas={self.tamano_paginas}, esquema={self.esquema_carga})"
        )
