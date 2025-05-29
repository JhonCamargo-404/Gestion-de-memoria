from collections import deque

class MemoryManager:
    def __init__(self, num_marcos=4, algoritmo="FIFO"):
        self.num_marcos = num_marcos
        self.memoria_fisica = {}  # marco: (pid, numero_pagina)
        self.swap = set()         # conjunto de paginas en swap
        self.pila_fifo = deque()  # para FIFO
        self.recientes = {}       # para LRU: {(pid, pagina): timestamp}
        self.algoritmo = algoritmo
        self.tiempo = 0           # contador de accesos

        # Estadísticas
        self.total_accesos = 0
        self.total_fallos_pagina = 0
        self.total_reemplazos = 0

    def cargar_pagina(self, proceso, pagina):
        pid = id(proceso)
        self.total_accesos += 1

        # Verificar si ya está cargada
        for marco, (p, pag) in self.memoria_fisica.items():
            if p == pid and pag == pagina:
                self.actualizar_lru(pid, pagina)
                return marco

        # Página no estaba en memoria → fallo de página
        self.total_fallos_pagina += 1

        # Verificar espacio disponible
        if len(self.memoria_fisica) < self.num_marcos:
            marco_libre = self._primer_marco_libre()
            self.memoria_fisica[marco_libre] = (pid, pagina)
            self.actualizar_lru(pid, pagina)
            self.pila_fifo.append(marco_libre)
            return marco_libre

        # Si está llena → reemplazo
        self.total_reemplazos += 1
        marco_reemplazo = self.seleccionar_marco_reemplazo()
        pid_old, pag_old = self.memoria_fisica[marco_reemplazo]
        self.swap.add((pid_old, pag_old))
        self.memoria_fisica[marco_reemplazo] = (pid, pagina)
        self.actualizar_lru(pid, pagina)
        if self.algoritmo == "FIFO":
            self.pila_fifo.append(marco_reemplazo)
        return marco_reemplazo

    def seleccionar_marco_reemplazo(self):
        if self.algoritmo == "FIFO":
            return self.pila_fifo.popleft()
        elif self.algoritmo == "LRU":
            menos_usado = min(self.recientes, key=self.recientes.get)
            for marco, (p, pag) in self.memoria_fisica.items():
                if (p, pag) == menos_usado:
                    return marco
        else:
            raise ValueError("Algoritmo no soportado")

    def actualizar_lru(self, pid, pagina):
        if self.algoritmo == "LRU":
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
