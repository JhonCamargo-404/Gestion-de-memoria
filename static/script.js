document.addEventListener("DOMContentLoaded", function () {
    const pasosJson = document.getElementById("pasos-json");
    if (!pasosJson) return;

    const pasos = JSON.parse(pasosJson.textContent);
    const pasoElements = document.querySelectorAll(".paso");

    // Mostrar detalles al hacer clic
    pasoElements.forEach((el, idx) => {
        el.addEventListener("click", () => mostrarDetallesPaso(idx));
    });

    function mostrarDetallesPaso(index) {
        const paso = pasos[index];
        if (!paso) return;

        document.getElementById("det-proceso").textContent = paso.proceso;
        document.getElementById("det-variable").textContent = paso.variable;
        document.getElementById("det-virt").textContent = paso.direccion_virtual;
        document.getElementById("det-fisica").textContent = paso.direccion_fisica;
        document.getElementById("det-pag").textContent = paso.pagina;
        document.getElementById("det-offset").textContent = paso.offset;
        document.getElementById("texto-explicacion").textContent = paso.explicacion;

        document.getElementById("detallesPaso").style.display = "block";
        document.getElementById("explicacionPaso").style.display = "block";

        pasoElements.forEach(el => el.classList.remove("activo"));
        pasoElements[index].classList.add("activo");
    }

    // Simulación visual de FIFO
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
                cola.shift();  // FIFO: eliminar más antigua
            }
            cola.push(paso.pagina); // agregar nueva página
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
            label.innerHTML = "⬅️ Reemplazo";
            label.style.marginTop = "4px";
            columna.appendChild(label);
        }

        container.appendChild(columna);
    });
}
