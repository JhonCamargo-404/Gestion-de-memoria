document.addEventListener("DOMContentLoaded", function () {
    const pasoDataElement = document.getElementById("pasos-json");
    if (!pasoDataElement) {
        console.warn("No se encontró el elemento pasos-json.");
        return;
    }

    let pasos;
    try {
        pasos = JSON.parse(pasoDataElement.textContent);
    } catch (error) {
        console.error("No se pudo parsear los datos de pasos:", error);
        return;
    }

    const pasoDivs = document.querySelectorAll(".paso");
    if (pasoDivs.length === 0) {
        console.warn("No se encontraron elementos con clase 'paso'.");
        return;
    }

    pasoDivs.forEach((el, index) => {
        el.style.cursor = "pointer";  // para que el usuario vea que es clickeable
        el.addEventListener("click", () => {
            const paso = pasos[index];

            console.log("Click en paso:", paso);

            document.getElementById("det-proceso").textContent = paso.proceso;
            document.getElementById("det-variable").textContent = paso.variable;
            document.getElementById("det-virt").textContent = paso.direccion_virtual;
            document.getElementById("det-fisica").textContent = paso.direccion_fisica;
            document.getElementById("det-pag").textContent = paso.pagina;
            document.getElementById("det-offset").textContent = paso.offset;

            document.getElementById("detallesPaso").style.display = "block";

            if (paso.explicacion) {
                document.getElementById("texto-explicacion").textContent = paso.explicacion;
                document.getElementById("explicacionPaso").style.display = "block";
            } else {
                document.getElementById("explicacionPaso").style.display = "none";
            }
        });
    });
});
