// Archivo JavaScript de EcoAcción
// Se encarga de pequeños detalles visuales, sin funciones complicadas

// Esta función anima la barra de progreso cuando carga el dashboard
function animarBarraProgreso() {
    const barra = document.querySelector(".barra-progreso-relleno");

    if (barra) {
        const anchoFinal = barra.style.width;
        // Empezamos en 0% y luego la llevamos al valor final con transición CSS
        barra.style.width = "0%";
        setTimeout(() => {
            barra.style.width = anchoFinal;
        }, 200);
    }
}

// Esta función pide confirmación antes de marcar un reto como completado
function confirmarCompletarReto(botones) {
    botones.forEach((boton) => {
        boton.addEventListener("click", (evento) => {
            const confirmado = confirm("¿Seguro que completaste este reto?");
            if (!confirmado) {
                evento.preventDefault();
            }
        });
    });
}

// Cuando el contenido de la página termina de cargar...
document.addEventListener("DOMContentLoaded", () => {
    animarBarraProgreso();

    const botonesCompletar = document.querySelectorAll(".btn-completar");
    confirmarCompletarReto(botonesCompletar);
});
