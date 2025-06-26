const API_BASE_URL = 'http://127.0.0.1:8000';
const API_VERSION_PREFIX = '/app/v1';

document.addEventListener('DOMContentLoaded', () => {
    // Obtener los datos de sesión almacenados en localStorage
    const accessToken = localStorage.getItem('access_token');
    const userVenueId = localStorage.getItem('user_venue_id'); // ID de la sede del usuario
    const currentUserId = localStorage.getItem('user_id');     // ID del usuario autenticado

    // --- VERIFICACIÓN DE AUTENTICACIÓN: Esta es la parte modificada ---
    if (!accessToken) {
        // Si no hay token de acceso, redirigir inmediatamente a la página de login
        console.log("No access token found. Redirecting to login page.");
        window.location.href = 'login.html';
        return; // Detener la ejecución del script aquí para evitar que se cargue el formulario
    } else {
        // Si hay un token, el usuario está logueado, continuar con la inicialización del formulario
        console.log("Access token found. User is logged in.");
        const userInfoDiv = document.getElementById('user-info');
        if (userInfoDiv) {
            userInfoDiv.textContent = `Usuario ID: ${currentUserId || 'No disponible'}, Sede ID: ${userVenueId || 'No disponible'}`;
        }

        const sedeInput = document.getElementById('sede');
        if (sedeInput && userVenueId) {
            sedeInput.value = userVenueId;
            sedeInput.disabled = true; // Deshabilita el campo
            sedeInput.style.backgroundColor = '#e9e9e9'; // Cambia el color para indicar que está deshabilitado
        }
        
        const supervisorIdInput = document.getElementById('supervisor_id');
        if (supervisorIdInput && currentUserId) {
            supervisorIdInput.value = currentUserId;
            supervisorIdInput.disabled = true; // Deshabilita el campo
            supervisorIdInput.style.backgroundColor = '#e9e9e9'; // Cambia el color para indicar que está deshabilitado
        }
    }
    // --- FIN VERIFICACIÓN DE AUTENTICACIÓN ---


    // --- Inicialización de fecha y hora actuales ---
    const fechaInput = document.getElementById('fecha');
    const horaIngInput = document.getElementById('hora_ing');

    if (fechaInput && horaIngInput) {
        const now = new Date(); // Obtiene la fecha y hora actuales

        // Formato YYYY-MM-DD para la fecha
        const year = now.getFullYear();
        const month = String(now.getMonth() + 1).padStart(2, '0'); // Meses son 0-11
        const day = String(now.getDate()).padStart(2, '0');
        fechaInput.value = `${year}-${month}-${day}`;

        // Formato HH:MM para la hora
        const hours = String(now.getHours()).padStart(2, '0');
        const minutes = String(now.getMinutes()).padStart(2, '0');
        horaIngInput.value = `${hours}:${minutes}`;
    }

    // =========================================================================
    // *** Lógica para el botón de cerrar sesión ***
    // =========================================================================
    const logoutButton = document.getElementById('logoutButton');
    if (logoutButton) {
        logoutButton.addEventListener('click', (event) => {
            event.preventDefault();
            localStorage.clear(); // Limpia todos los datos de la sesión
            // Eliminado el 'alert' para una transición más fluida
            window.location.href = 'login.html';
        });
    }

    // =========================================================================
    // *** LÓGICA DEL FORMULARIO DE REGISTRO DE VISITAS ***
    // =========================================================================
    const createVisitForm = document.getElementById('createVisitForm');
    if (createVisitForm) {
        createVisitForm.addEventListener('submit', async (event) => {
            event.preventDefault();

            const statusMessageDiv = document.getElementById('statusMessage');
            statusMessageDiv.textContent = 'Enviando datos...';
            statusMessageDiv.style.color = 'black';

            // Obtener los valores de los campos del formulario
            const fecha = document.getElementById('fecha').value; // Valor automático
            const nombreVisitante = document.getElementById('nombre_visitante').value;
            const apellidoVisitante = document.getElementById('apellido_visitante').value;
            const tipoDocumentoRadio = document.querySelector('input[name="id_card_type"]:checked');
            const idCardTypeId = tipoDocumentoRadio ? parseInt(tipoDocumentoRadio.value) : null;
            const documento = document.getElementById('documento').value;
            const emailVisitante = document.getElementById('email_visitante').value;
            const phoneVisitante = document.getElementById('phone_visitante').value;
            const sede = parseInt(document.getElementById('sede').value); // Valor automático, deshabilitado
            const supervisor_id = parseInt(document.getElementById('supervisor_id').value); // Valor automático, deshabilitado
            const horaIngreso = document.getElementById('hora_ing').value; // Valor automático
            const reasonVisit = document.getElementById('reason_visit').value;

            // Construir el objeto de datos a enviar a la API
            const completeVisitData = {
                name: nombreVisitante,
                last_name: apellidoVisitante,
                id_card: parseInt(documento),
                phone: phoneVisitante,
                email: emailVisitante,
                id_card_type_id: idCardTypeId,
                fecha: fecha,
                hora_ing: horaIngreso,
                reason_visit: reasonVisit,
                sede: sede,
                supervisor_id: supervisor_id, // Se envía el ID numérico
            };

            console.log("Datos a enviar (VisitCreateRequest):", completeVisitData);

            const token = localStorage.getItem('access_token');
            if (!token) {
                // Esta verificación es redundante si la primera ya redirigió
                // Pero es una buena capa de seguridad si el token se pierde entre interacciones.
                // Reemplazando alert con console.error y redirigiendo.
                console.error('No hay token de autenticación. Redirigiendo a login.');
                window.location.href = 'login.html'; 
                return;
            }

            try {
                const response = await fetch(`${API_BASE_URL}${API_VERSION_PREFIX}/visitors/register_visit`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify(completeVisitData)
                });

                const result = await response.json();
                console.log("Respuesta de la API:", result);

                if (!response.ok) {
                    throw new Error(`Error ${response.status}: ${result.detail || JSON.stringify(result)}`);
                }

                statusMessageDiv.textContent = `Registro de visita y visitante creado con éxito. ID de Acceso: ${result.access_id}`;
                statusMessageDiv.style.color = 'green';
                event.target.reset(); // Limpiar el formulario

                // Asegurar que los campos de sede y supervisor_id vuelvan a llenarse después de un reset
                document.getElementById('sede').value = localStorage.getItem('user_venue_id');
                document.getElementById('supervisor_id').value = localStorage.getItem('user_id');

            } catch (error) {
                console.error('Error al registrar la visita completa:', error);
                statusMessageDiv.textContent = `Error al registrar la visita: ${error.message}`;
                statusMessageDiv.style.color = 'red';
            }
        });
    }

});
