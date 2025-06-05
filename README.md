# Simulador de Memoria con MMU y Paginación FIFO

Este proyecto implementa un simulador interactivo que ilustra el funcionamiento del sistema de memoria de un sistema operativo, específicamente la traducción de direcciones virtuales a físicas a través de una Unidad de Manejo de Memoria (MMU), utilizando paginación sobre demanda y el algoritmo FIFO para el reemplazo de páginas.

## Objetivo del Proyecto

Simular y visualizar de forma didáctica:
- La traducción de direcciones simbólicas a virtuales y físicas.
- La gestión de procesos con espacios de direcciones virtuales.
- El comportamiento de la MMU con paginación sobre demanda.
- El algoritmo FIFO como mecanismo de reemplazo de páginas.
- Casos de fallo de página y carga desde el espacio de intercambio.

## Tecnologías Utilizadas

| Lenguaje / Herramienta | Versión / Uso                   |
|------------------------|---------------------------------|
| Python                 | 3.11.x – Backend (Flask)        |
| Flask                  | Para rutas y servidor web       |
| HTML/CSS/JavaScript    | Interfaz de usuario             |
| JSON                   | Persistencia de procesos        |

## Estructura del Proyecto

```

memory\_simulator/
├── app.py
├── routes/
│   └── main\_routes.py
├── services/
│   └── simulador\_service.py
├── memory/
│   ├── memory\_manager.py
│   ├── mmu.py
│   └── proceso.py
├── templates/
│   └── index.html
├── static/
│   ├── styles.css
│   └── script.js
└── data/
└── procesos.json

```

## Funcionalidades Implementadas

- Ingreso y visualización de procesos definidos manual o dinámicamente.
- Construcción de direcciones simbólicas, cálculo de direcciones virtuales.
- Visualización detallada paso a paso del proceso de traducción.
- Manejo de memoria física y swap.
- Simulación de paginación bajo demanda.
- Algoritmo FIFO como política de reemplazo.
- Persistencia de procesos agregados dinámicamente (archivo JSON).
- Estadísticas de rendimiento (fallos, reemplazos, tasa de fallos).
- Visualización gráfica de la cola FIFO.
