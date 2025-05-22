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

    def cargar_pagina(self, proceso, pagina):
        pid = id(proceso)

        # Verificar si ya está cargada
        for marco, (p, pag) in self.memoria_fisica.items():
            if p == pid and pag == pagina:
                self.actualizar_lru(pid, pagina)
                return marco

        # Verificar espacio disponible
        if len(self.memoria_fisica) < self.num_marcos:
            marco_libre = self._primer_marco_libre()
            self.memoria_fisica[marco_libre] = (pid, pagina)
            self.actualizar_lru(pid, pagina)
            self.pila_fifo.append(marco_libre)
            return marco_libre

        # Si está llena → reemplazo
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
        """Devuelve el estado actual de memoria y swap para visualización."""
        memoria = {i: self.memoria_fisica.get(i, None) for i in range(self.num_marcos)}
        return {
            "memoria_fisica": memoria,
            "swap": list(self.swap)
        }
