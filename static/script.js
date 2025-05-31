document.addEventListener("DOMContentLoaded", function () {
    const pasosJson = document.getElementById("pasos-json");
    if (!pasosJson) return;

    const pasos = JSON.parse(pasosJson.textContent);
    const pasoElements = document.querySelectorAll(".paso");

    // Asociar clics a los bloques del flujo
    pasoElements.forEach((el, idx) => {
        el.addEventListener("click", () => mostrarDetallesPaso(idx));
    });

    function mostrarDetallesPaso(index) {
        const paso = pasos[index];
        if (!paso) return;

        // Mostrar datos técnicos
        document.getElementById("det-proceso").textContent = paso.proceso;
        document.getElementById("det-variable").textContent = paso.variable;
        document.getElementById("det-virt").textContent = paso.direccion_virtual;
        document.getElementById("det-fisica").textContent = paso.direccion_fisica;
        document.getElementById("det-pag").textContent = paso.pagina;
        document.getElementById("det-offset").textContent = paso.offset;

        // Mostrar explicación narrativa en HTML estructurado
        document.getElementById("texto-explicacion").innerHTML = paso.explicacion;

        // Activar bloques de visualización
        document.getElementById("detallesPaso").style.display = "block";
        document.getElementById("explicacionPaso").style.display = "block";

        // Resaltar paso activo
        pasoElements.forEach(el => el.classList.remove("activo"));
        pasoElements[index].classList.add("activo");
    }

    // Construcción de la cola FIFO
    actualizarColaFIFO(pasos);
});

function actualizarColaFIFO(pasos) {
    const container = document.getElementById("fifo-visual-container");
    if (!container) return;

    container.innerHTML = "";
    const cola = [];

    pasos.forEach((paso, index) => {
        if (paso.fallo_pagina) {
            if (paso.swap && paso.expulsado) {
                cola.shift(); // eliminar el más antiguo
            }
            cola.push(paso.pagina);
        }

        const columna = document.createElement("div");
        columna.className = `fifo-step ${paso.swap ? "dequeue" : "enqueue"}`;
        columna.innerHTML = `<div>Paso ${index + 1}</div><div class="arrow">${paso.swap ? "⬆️" : "⬇️"}</div>`;

        cola.slice().reverse().forEach(pagina => {
            const block = document.createElement("div");
            block.className = "fifo-block";
            block.textContent = pagina;
            columna.appendChild(block);
        });

        if (paso.swap) {
            const label = document.createElement("div");
            label.textContent = "Reemplazo";
            label.style.marginTop = "4px";
            columna.appendChild(label);
        }

        container.appendChild(columna);
    });
}
