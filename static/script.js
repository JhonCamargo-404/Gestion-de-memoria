document.addEventListener("DOMContentLoaded", function () {
    const pasosJson = document.getElementById("pasos-json");
    if (!pasosJson) return;

    const pasos = JSON.parse(pasosJson.textContent);
    const pasoElements = document.querySelectorAll(".paso");

    pasoElements.forEach((el, idx) => {
        el.addEventListener("click", () => mostrarDetallesPaso(idx));
    });

    function mostrarDetallesPaso(index) {
        const paso = pasos[index];
        if (!paso) return;

        // Actualizar los detalles visibles
        document.getElementById("det-proceso").textContent = paso.proceso;
        document.getElementById("det-variable").textContent = paso.variable;
        document.getElementById("det-virt").textContent = paso.direccion_virtual;
        document.getElementById("det-fisica").textContent = paso.direccion_fisica;
        document.getElementById("det-pag").textContent = paso.pagina;
        document.getElementById("det-offset").textContent = paso.offset;
        document.getElementById("texto-explicacion").textContent = paso.explicacion;

        document.getElementById("detallesPaso").style.display = "block";
        document.getElementById("explicacionPaso").style.display = "block";

        // Resaltar el paso seleccionado
        pasoElements.forEach(el => el.classList.remove("activo"));
        pasoElements[index].classList.add("activo");
    }
});
