const API_BASE_URL = 'http://127.0.0.1:8000';
const API_VERSION_PREFIX = '/app/v1';

// Lógica de llenado de Sede y redirección si no hay token/sede
document.addEventListener('DOMContentLoaded', () => {
    const sedeInput = document.getElementById('sede');
    const userVenueId = localStorage.getItem('user_venue_id');
    const accessToken = localStorage.getItem('access_token'); // También verificar el token

    if (!accessToken) {
        alert('No ha iniciado sesión. Será redirigido a la página de login.');
        window.location.href = 'login.html';
        return; // Detener la ejecución
    }

    if (userVenueId) {
        sedeInput.value = userVenueId;
    } else {
        alert('No se pudo obtener la sede del usuario. Por favor, inicie sesión de nuevo.');
        window.location.href = '/login.html';
    }

    // Manejar botón de cerrar sesión
    const logoutButton = document.getElementById('logoutButton');
    if (logoutButton) {
        logoutButton.addEventListener('click', (event) => {
            event.preventDefault();
            localStorage.clear(); // Limpia todos los datos de sesión
            alert('Sesión cerrada correctamente.');
            window.location.href = 'login.html'; // Redirige al login
        });
    }
});

// Manejar el envío del formulario de registro de visita
document.getElementById('createVisitForm').addEventListener('submit', async (event) => {
    event.preventDefault(); // Prevenir el envío tradicional del formulario

    const statusMessageDiv = document.getElementById('statusMessage');
    statusMessageDiv.textContent = 'Enviando...';
    statusMessageDiv.style.color = 'black';

    // Recoger los datos del formulario
    const fecha = document.getElementById('fecha').value;
    const nombreVisitante = document.getElementById('nombre_visitante').value;
    const apellidoVisitante = document.getElementById('apellido_visitante').value;
    const tipoDocumentoRadio = document.querySelector('input[name="id_card_type"]:checked');
    const idCardTypeId = tipoDocumentoRadio ? parseInt(tipoDocumentoRadio.value) : null;
    const documento = document.getElementById('documento').value;
    const emailVisitante = document.getElementById('email_visitante').value;
    const phoneVisitante = document.getElementById('phone_visitante').value;
    const sedeId = parseInt(document.getElementById('sede').value);
    const supervisorId = parseInt(document.getElementById('supervisor_id').value);
    const horaIngreso = document.getElementById('hora_ing').value; // Formato HH:MM
    const reasonVisit = document.getElementById('reason_visit').value;


    // Construir el objeto de datos del visitante para la API
    // Ajusta los nombres de las propiedades para que coincidan con tu VisitorCreate Schema
    const visitorData = {
        name: nombreVisitante,
        last_name: apellidoVisitante,
        id_card: parseInt(documento), // Asegúrate de que sea un número
        phone: phoneVisitante,
        email: emailVisitante,
        // picture: "default_pic.jpg", // Si tienes una imagen por defecto
        supervisor_id: supervisorId,
        venue_id: sedeId,
        id_card_type_id: idCardTypeId,
        // Si la fecha y hora de ingreso son parte del esquema del visitante
        // y no de un registro de visita separado, tendrías que incluirlas aquí
        // O el backend las generará. Tu esquema de visitante no las incluye.
    };

    console.log("Datos a enviar:", visitorData); // Para depuración

    const accessToken = localStorage.getItem('access_token');
    if (!accessToken) {
        alert('No hay token de autenticación. Por favor, inicie sesión.');
        window.location.href = 'login.html';
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}${API_VERSION_PREFIX}/visitors/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${accessToken}`
            },
            body: JSON.stringify(visitorData)
        });

        const result = await response.json();
        console.log("Respuesta de la API:", result); // Para depuración

        if (!response.ok) {
            throw new Error(`Error ${response.status}: ${result.detail || JSON.stringify(result)}`);
        }

        statusMessageDiv.textContent = `Registro de visitante creado con éxito. ID: ${result.id}`;
        statusMessageDiv.style.color = 'green';
        event.target.reset(); // Limpiar el formulario
        // Mantener el campo sede con el valor predeterminado después de resetear
        document.getElementById('sede').value = localStorage.getItem('user_venue_id');

    } catch (error) {
        console.error('Error al crear registro de visitante:', error);
        statusMessageDiv.textContent = `Error al crear registro: ${error.message}`;
        statusMessageDiv.style.color = 'red';
    }
});