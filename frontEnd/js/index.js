const API_BASE_URL = 'http://127.0.0.1:8000';
const API_VERSION_PREFIX = '/app/v1';

// Endpoint de registro de visita alineado con el backend (receptionist_router)
const REGISTER_VISIT_ENDPOINT = `${API_VERSION_PREFIX}/receptionist/register_full_visit`;


document.addEventListener('DOMContentLoaded', () => {
    // Obtener los datos de sesión almacenados en localStorage
    const accessToken = localStorage.getItem('access_token');
    const userVenueId = localStorage.getItem('user_venue_id'); // ID de la sede del usuario
    const currentUserId = localStorage.getItem('user_id');     // ID del usuario autenticado

    // --- VERIFICACIÓN DE AUTENTICACIÓN ---
    if (!accessToken) {
        console.log("No access token found. Redirecting to login page.");
        window.location.href = 'login.html';
        return; 
    } else {
        console.log("Access token found. User is logged in.");
        const userInfoDiv = document.getElementById('user-info');
        if (userInfoDiv) {
            userInfoDiv.textContent = `Usuario ID: ${currentUserId || 'No disponible'}, Sede ID: ${userVenueId || 'No disponible'}`;
        }

        const sedeInput = document.getElementById('sede');
        if (sedeInput && userVenueId) {
            sedeInput.value = userVenueId;
            sedeInput.disabled = true; 
            sedeInput.style.backgroundColor = '#e9e9e9'; 
        }
        
        const supervisorIdInput = document.getElementById('supervisor_id');
        // Este campo se prellena en el frontend y AHORA SÍ se envía al backend
        // según el esquema VisitCreateRequest que el backend está cargando.
        if (supervisorIdInput && currentUserId) {
            supervisorIdInput.value = currentUserId;
            supervisorIdInput.disabled = true; 
            supervisorIdInput.style.backgroundColor = '#e9e9e9'; 
        }
    }
    // --- FIN VERIFICACIÓN DE AUTENTICACIÓN ---


    // --- Inicialización de fecha y hora actuales ---
    const fechaInput = document.getElementById('fecha');
    const horaIngInput = document.getElementById('hora_ing');

    if (fechaInput && horaIngInput) {
        const now = new Date(); 

        const year = now.getFullYear();
        const month = String(now.getMonth() + 1).padStart(2, '0'); 
        const day = String(now.getDate()).padStart(2, '0');
        fechaInput.value = `${year}-${month}-${day}`;

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
            localStorage.clear(); 
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
            const fecha = document.getElementById('fecha').value; 
            const horaIngreso = document.getElementById('hora_ing').value;
            const nombreVisitante = document.getElementById('nombre_visitante').value;
            const apellidoVisitante = document.getElementById('apellido_visitante').value;
            const tipoDocumentoRadio = document.querySelector('input[name="id_card_type"]:checked');
            const idCardTypeId = tipoDocumentoRadio ? parseInt(tipoDocumentoRadio.value) : null;
            const documento = document.getElementById('documento').value; // Este es el número de documento (STRING)
            const emailVisitante = document.getElementById('email_visitante').value;
            const phoneVisitante = document.getElementById('phone_visitante').value;
            const sedeValue = parseInt(document.getElementById('sede').value); 
            const supervisorIdValue = parseInt(document.getElementById('supervisor_id').value); // ID del supervisor

            // Motivo de Visita (requerido por el backend)
            const reasonVisit = document.getElementById('reason_visit').value; 

            // Construir el objeto de datos a enviar a la API
            const completeVisitData = {
                name: nombreVisitante,
                last_name: apellidoVisitante,
                id_card: documento, // CAMBIO CLAVE: Coincide con 'id_card' en el backend (STRING)
                phone: phoneVisitante,
                email: emailVisitante,
                id_card_type_id: idCardTypeId,
                fecha: fecha,
                hora_ing: horaIngreso,
                
                // Campos de acceso
                reason_visit: reasonVisit, // Coincide con 'reason_visit' en el backend
                sede: sedeValue, // Coincide con 'sede' en el backend (INT)
                supervisor_id: supervisorIdValue, // Coincide con 'supervisor_id' en el backend (INT)
            };

            console.log("Datos a enviar (VisitCreateRequest):", completeVisitData);

            const token = localStorage.getItem('access_token');
            if (!token) {
                console.error('No hay token de autenticación. Redirigiendo a login.');
                window.location.href = 'login.html'; 
                return;
            }

            try {
                const response = await fetch(`${API_BASE_URL}${REGISTER_VISIT_ENDPOINT}`, {
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
                    if (response.status === 422 && result.detail && Array.isArray(result.detail)) {
                         const errorDetails = result.detail.map(err => `${err.loc.join('.')} -> ${err.msg}`).join('\n');
                         throw new Error(`Error ${response.status} (Validación): \n${errorDetails}`);
                    } else {
                        throw new Error(`Error ${response.status}: ${result.detail || JSON.stringify(result)}`);
                    }
                }

                statusMessageDiv.textContent = `Registro de visita y visitante creado con éxito. ID de Acceso: ${result.id}`; 
                statusMessageDiv.style.color = 'green';
                event.target.reset(); 

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
