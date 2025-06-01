document.addEventListener("DOMContentLoaded", function () {
    const pasosJson = document.getElementById("pasos-json");
    if (pasosJson) {
        const pasos = JSON.parse(pasosJson.textContent);
        const pasoElements = document.querySelectorAll(".paso");

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
            document.getElementById("texto-explicacion").innerHTML = paso.explicacion;

            document.getElementById("detallesPaso").style.display = "block";
            document.getElementById("explicacionPaso").style.display = "block";

            pasoElements.forEach(el => el.classList.remove("activo"));
            pasoElements[index].classList.add("activo");
        }

        actualizarColaFIFO(pasos);
    }

    const formAgregar = document.getElementById("form-agregar-proceso");
    if (formAgregar) {
        formAgregar.addEventListener("submit", function (e) {
            e.preventDefault();

            const nombre = document.getElementById("nombre").value.trim();
            const base_suffix = document.getElementById("base_virtual_suffix").value.trim();
            const base_virtual = "0x" + base_suffix;
            const paginas = document.getElementById("paginas").value;
            const esquema = document.getElementById("esquema").value;

            if (!nombre || !base_suffix || !paginas) {
                alert("Debes diligenciar todos los campos obligatorios.");
                return;
            }

            const rows = document.querySelectorAll("#tabla-variables tbody tr");
            let variables = [];
            rows.forEach(row => {
                const nombre = row.querySelector(".var-nombre").textContent.trim();
                const offset = row.querySelector(".var-offset").textContent.trim();
                variables.push(`${nombre}:0x${offset}`);
            });

            fetch("/agregar_proceso_ajax", {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                body: `nombre=${encodeURIComponent(nombre)}&base_virtual=${encodeURIComponent(base_virtual)}&paginas=${encodeURIComponent(paginas)}&esquema=${encodeURIComponent(esquema)}&variables=${encodeURIComponent(variables.join(","))}`
            })
            .then(response => {
                if (!response.ok) throw new Error("Error en el servidor");
                return response.json();
            })
            .then(data => {
                const lista = document.getElementById("lista-procesos") || document.querySelector(".panel-izquierdo .bloque:nth-child(2)");
                lista.insertAdjacentHTML("beforeend", data.checkbox_html);
                formAgregar.reset();
                document.querySelector("#tabla-variables tbody").innerHTML = "";
            })
            .catch(err => alert("Error al agregar el proceso: " + err.message));
        });
    }

    const hexInputs = [
        document.getElementById("base_virtual_suffix"),
        document.getElementById("var-offset")
    ];

    hexInputs.forEach(input => {
        if (input) {
            input.addEventListener("input", () => {
                input.value = input.value.toUpperCase().replace(/[^0-9A-F]/g, "");
            });
        }
    });
});

function agregarVariable() {
    const nombre = document.getElementById("var-nombre").value.trim();
    const offset = document.getElementById("var-offset").value.trim();
    if (!nombre || !offset) return;

    const tbody = document.querySelector("#tabla-variables tbody");

    const fila = document.createElement("tr");
    fila.innerHTML = `
        <td class="var-nombre">${nombre}</td>
        <td class="var-offset">${offset}</td>
        <td><button type="button" onclick="this.closest('tr').remove()">✕</button></td>
    `;

    tbody.appendChild(fila);
    document.getElementById("var-nombre").value = "";
    document.getElementById("var-offset").value = "";
}

function actualizarColaFIFO(pasos) {
    const container = document.getElementById("fifo-visual-container");
    if (!container) return;

    container.innerHTML = "";
    const cola = [];

    pasos.forEach((paso, index) => {
        if (paso.fallo_pagina) {
            if (paso.swap && paso.expulsado) {
                cola.shift();
            }
            cola.push(paso.pagina);
        }

        const columna = document.createElement("div");
        columna.className = `fifo-step ${paso.swap ? "dequeue" : "enqueue"}`;
        columna.innerHTML = `<div>Paso ${index + 1}</div><div class="arrow">${paso.swap ? "⬆" : "⬇"}</div>`;

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
