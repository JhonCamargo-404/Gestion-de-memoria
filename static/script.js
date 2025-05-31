document.addEventListener("DOMContentLoaded", function () {
    const pasoDataElement = document.getElementById("pasos-json");
    if (!pasoDataElement) return;

    let pasos;
    try {
        pasos = JSON.parse(pasoDataElement.textContent);
    } catch (error) {
        console.error("No se pudo parsear los datos de pasos:", error);
        return;
    }

    const pasoDivs = document.querySelectorAll(".paso");

    pasoDivs.forEach((el, index) => {
        el.addEventListener("click", () => {
            const paso = pasos[index];

            // Mostrar detalles del paso
            document.getElementById("det-proceso").textContent = paso.proceso;
            document.getElementById("det-variable").textContent = paso.variable;
            document.getElementById("det-virt").textContent = paso.direccion_virtual;
            document.getElementById("det-fisica").textContent = paso.direccion_fisica;
            document.getElementById("det-pag").textContent = paso.pagina;
            document.getElementById("det-offset").textContent = paso.offset;

            document.getElementById("detallesPaso").style.display = "block";

            // Mostrar explicación didáctica del paso
            if (paso.explicacion) {
                document.getElementById("texto-explicacion").textContent = paso.explicacion;
                document.getElementById("explicacionPaso").style.display = "block";
            } else {
                document.getElementById("explicacionPaso").style.display = "none";
            }
        });
    });
});
