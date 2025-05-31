from collections import deque

class MemoryManager:
    def __init__(self, num_marcos=4, algoritmo="FIFO"):
        self.num_marcos = num_marcos
        self.memoria_fisica = {}  # {marco: (pid, pagina)}
        self.swap = set()         # {(pid, pagina)}
        self.pila_fifo = deque()  # FIFO: orden de llegada
        self.recientes = {}       # LRU: {(pid, pagina): tiempo}
        self.algoritmo = algoritmo
        self.tiempo = 0
        self.total_accesos = 0
        self.total_fallos_pagina = 0
        self.total_reemplazos = 0
        self.__reset_estadisticas()
        
    def __reset_estadisticas(self):
        self.total_accesos = 0
        self.total_fallos_pagina = 0
        self.total_reemplazos = 0
        self.tiempo = 0

    def cargar_pagina(self, proceso, pagina):
        pid = id(proceso)
        self.total_accesos += 1

        # Página ya está en memoria
        for marco, (p, pag) in self.memoria_fisica.items():
            if p == pid and pag == pagina:
                self.actualizar_lru(pid, pagina)
                return marco

        # Fallo de página
        self.total_fallos_pagina += 1

        # Hay espacio en memoria
        if len(self.memoria_fisica) < self.num_marcos:
            marco_libre = self._primer_marco_libre()
            self.memoria_fisica[marco_libre] = (pid, pagina)
            self.actualizar_lru(pid, pagina)
            self.pila_fifo.append(marco_libre)
            return marco_libre

        # Reemplazo
        self.total_reemplazos += 1
        marco_reemplazo = self.seleccionar_marco_reemplazo()
        if marco_reemplazo is None:
            raise RuntimeError("No se encontró marco válido para reemplazo.")

        pid_old, pag_old = self.memoria_fisica[marco_reemplazo]

        # Eliminar de recientes si estamos en LRU
        if self.algoritmo == "LRU":
            self.recientes.pop((pid_old, pag_old), None)

        self.swap.add((pid_old, pag_old))
        self.memoria_fisica[marco_reemplazo] = (pid, pagina)
        self.actualizar_lru(pid, pagina)

        if self.algoritmo == "FIFO":
            self.pila_fifo.append(marco_reemplazo)

        return marco_reemplazo

    def seleccionar_marco_reemplazo(self):
        if self.algoritmo == "FIFO":
            if self.pila_fifo:
                return self.pila_fifo.popleft()
            else:
                raise RuntimeError("La cola FIFO está vacía. No se puede hacer reemplazo.")

        elif self.algoritmo == "LRU":
            if not self.recientes:
                raise RuntimeError("No hay registros en LRU para seleccionar reemplazo.")

            menos_usado = min(self.recientes, key=self.recientes.get)
            for marco, (p, pag) in self.memoria_fisica.items():
                if (p, pag) == menos_usado:
                    return marco

            raise RuntimeError("No se encontró el marco correspondiente al menos usado en LRU.")

        else:
            raise ValueError(f"Algoritmo '{self.algoritmo}' no soportado.")

    def actualizar_lru(self, pid, pagina):
        if self.algoritmo == "LRU":
            # Solo registrar si la página está actualmente en memoria
            if any((p == pid and pag == pagina) for (p, pag) in self.memoria_fisica.values()):
                self.tiempo += 1
                self.recientes[(pid, pagina)] = self.tiempo

    def _primer_marco_libre(self):
        for i in range(self.num_marcos):
            if i not in self.memoria_fisica:
                return i
        raise RuntimeError("No hay marcos libres disponibles")

    def obtener_estado(self):
        memoria = {i: self.memoria_fisica.get(i, None) for i in range(self.num_marcos)}
        return {
            "memoria_fisica": memoria,
            "swap": list(self.swap)
        }

    def obtener_estadisticas(self):
        tasa_fallos = (self.total_fallos_pagina / self.total_accesos * 100) if self.total_accesos > 0 else 0
        return {
            "accesos": self.total_accesos,
            "fallos_pagina": self.total_fallos_pagina,
            "reemplazos": self.total_reemplazos,
            "tasa_fallos": round(tasa_fallos, 2)
        }
