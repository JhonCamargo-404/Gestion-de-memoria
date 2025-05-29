class Proceso:
    def __init__(self, nombre, base_virtual, tabla_simbolos, tamano_paginas, esquema_carga="variable"):
        self.nombre = nombre
        self.base_virtual = base_virtual
        self.tabla_simbolos = tabla_simbolos 
        self.tabla_paginas = {} 
        self.tamano_paginas = tamano_paginas
        self.esquema_carga = esquema_carga

    def obtener_direccion_virtual(self, variable):
        if variable in self.tabla_simbolos:
            offset = self.tabla_simbolos[variable]
            return self.base_virtual + offset
        else:
            raise ValueError(f"Variable '{variable}' no encontrada en la tabla de símbolos.")

    def asignar_marco(self, pagina, marco):
        self.tabla_paginas[pagina] = marco

    def obtener_tabla_paginas(self):
        return dict(self.tabla_paginas)

    def __repr__(self):
        return (
            f"Proceso({self.nombre}, base={hex(self.base_virtual)}, "
            f"tamano_paginas={self.tamano_paginas}, esquema={self.esquema_carga})"
        )
