
const jsonElement = document.getElementById("pasos-json");
const pasos = JSON.parse(jsonElement.textContent);

function mostrarDetalles(index) {
    const p = pasos[index];

    document.getElementById('det-proceso').innerText = p.proceso;
    document.getElementById('det-variable').innerText = p.variable;
    document.getElementById('det-virt').innerText = p.direccion_virtual;
    document.getElementById('det-fisica').innerText = p.direccion_fisica;
    document.getElementById('det-pag').innerText = p.pagina;
    document.getElementById('det-offset').innerText = p.offset;
    document.getElementById('detallesPaso').style.display = 'block';
}
