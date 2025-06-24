// frontEnd/js/registros.js

document.addEventListener('DOMContentLoaded', async () => {
    // Verificar autenticación al cargar la página
    const accessToken = localStorage.getItem('access_token');
    if (!accessToken) {
        // Redirigir a la página de login si no hay token
        window.location.href = 'login.html';
        return; // Detener la ejecución del script
    }

    // Inicializar el botón de logout
    const logoutButton = document.getElementById('logoutButton');
    if (logoutButton) {
        logoutButton.addEventListener('click', async () => {
            localStorage.removeItem('access_token');
            window.location.href = 'login.html';
        });
    }

    const API_BASE_URL = 'http://127.0.0.1:8000/app/v1'; // Ajusta si tu API tiene otra URL base

    // Elementos del DOM
    const fechaFilterInput = document.getElementById('fechaFilter');
    const documentoFilterInput = document.getElementById('documentoFilter');
    const searchDateBtn = document.getElementById('searchDateBtn');
    const searchDocumentBtn = document.getElementById('searchDocumentBtn');
    const clearFiltersBtn = document.getElementById('clearFiltersBtn');
    const recordsTableBody = document.getElementById('recordsTableBody');
    const statusMessageDiv = document.getElementById('statusMessage');

    // --- Funciones de Utilidad ---
    function showStatusMessage(message, type) {
        statusMessageDiv.textContent = message;
        statusMessageDiv.className = `status-message show ${type}`;
        setTimeout(() => {
            statusMessageDiv.classList.remove('show');
        }, 5000);
    }

    function formatDate(isoString) {
        if (!isoString) return 'N/A';
        const date = new Date(isoString);
        // Formato DD/MM/YYYY
        const day = String(date.getDate()).padStart(2, '0');
        const month = String(date.getMonth() + 1).padStart(2, '0'); // Meses son 0-11
        const year = date.getFullYear();
        return `${day}/${month}/${year}`;
    }

    function formatTime(isoString) {
        if (!isoString) return 'N/A';
        const date = new Date(isoString);
        // Formato HH:MM
        const hours = String(date.getHours()).padStart(2, '0');
        const minutes = String(date.getMinutes()).padStart(2, '0');
        return `${hours}:${minutes}`;
    }

    // --- Carga de Registros de Acceso ---
    async function loadAccessRecords(dateFilter = null, idCardFilter = null) {
        recordsTableBody.innerHTML = '<tr><td colspan="10" class="text-center">Cargando registros...</td></tr>';
        
        let url = `${API_BASE_URL}/access/`;
        const params = new URLSearchParams();

        if (dateFilter) {
            params.append('date_filter', dateFilter);
        }
        if (idCardFilter) {
            params.append('id_card_filter', idCardFilter);
        }
        
        if (params.toString()) {
            url += `?${params.toString()}`;
        }

        try {
            const response = await fetch(url, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${accessToken}`
                }
            });

            if (!response.ok) {
                // Si la respuesta no es OK, intenta leer el error del backend
                const errorData = await response.json();
                console.error('Error al cargar registros:', errorData.detail || errorData.message || response.statusText);
                showStatusMessage(`Error al cargar registros: ${errorData.detail || response.statusText || 'Verifica la consola.'}`, 'error');
                recordsTableBody.innerHTML = `<tr><td colspan="10" class="text-center">Error: ${errorData.detail || 'No se pudieron cargar los registros.'}</td></tr>`;
                return;
            }

            const records = await response.json();
            displayAccessRecords(records);

        } catch (error) {
            console.error('Error en la conexión o procesamiento:', error);
            showStatusMessage('Error en la conexión con el servidor. Intenta de nuevo.', 'error');
            recordsTableBody.innerHTML = '<tr><td colspan="10" class="text-center">No se pudieron cargar los registros (problema de red).</td></tr>';
        }
    }

    // --- Renderizado de la Tabla ---
    function displayAccessRecords(records) {
        recordsTableBody.innerHTML = ''; // Limpiar tabla antes de añadir nuevos datos
        if (records.length === 0) {
            recordsTableBody.innerHTML = '<tr><td colspan="10" class="text-center">No hay registros para mostrar con los filtros actuales.</td></tr>';
            return;
        }

        records.forEach(record => {
            const row = recordsTableBody.insertRow();
            
            // Formato de fecha y hora para mostrar
            const entryDateFormatted = formatDate(record.entry_date);
            const entryTimeFormatted = formatTime(record.entry_date);
            const exitTimeFormatted = formatTime(record.exit_date);
            
            // Campos de la tabla
            row.insertCell(0).textContent = entryDateFormatted;
            row.insertCell(1).textContent = entryTimeFormatted;
            // Estado "PENDIENTE" si no hay hora de salida
            const exitCell = row.insertCell(2);
            if (record.exit_date === null) {
                exitCell.innerHTML = '<span class="pending">PENDIENTE</span>';
            } else {
                exitCell.textContent = exitTimeFormatted;
            }
            
            row.insertCell(3).textContent = record.visitor_name || 'N/A';
            row.insertCell(4).textContent = record.visitor_id_card || 'N/A';
            row.insertCell(5).textContent = record.id_card_type_name || 'N/A';
            row.insertCell(6).textContent = record.venue_name || 'N/A';
            row.insertCell(7).textContent = record.supervisor_name || 'N/A';
            row.insertCell(8).textContent = record.access_reason || 'N/A';

            // Columna de Acciones
            const actionsCell = row.insertCell(9);
            actionsCell.classList.add('action-buttons'); // Clase para espaciado de botones

            // Botón "Marcar Salida" (solo si exit_date es null)
            if (record.exit_date === null) {
                const markExitBtn = document.createElement('button');
                markExitBtn.textContent = 'Marcar Salida';
                markExitBtn.classList.add('btn', 'btn-salida');
                markExitBtn.addEventListener('click', () => markExit(record.id));
                actionsCell.appendChild(markExitBtn);
            }

            // Botón "Ver"
            const viewBtn = document.createElement('button');
            viewBtn.innerHTML = '<ph-eye-bold></ph-eye-bold>'; // Icono de ojo de Phosphor
            viewBtn.classList.add('btn', 'btn-ver');
            viewBtn.title = 'Ver Detalles';
            viewBtn.addEventListener('click', () => viewRecord(record.id));
            actionsCell.appendChild(viewBtn);

            // Botón "Editar"
            const editBtn = document.createElement('button');
            editBtn.innerHTML = '<ph-pencil-simple-bold></ph-pencil-simple-bold>'; // Icono de lápiz de Phosphor
            editBtn.classList.add('btn', 'btn-editar');
            editBtn.title = 'Editar Registro';
            editBtn.addEventListener('click', () => editRecord(record.id));
            actionsCell.appendChild(editBtn);

            // Botón "Eliminar"
            const deleteBtn = document.createElement('button');
            deleteBtn.innerHTML = '<ph-trash-bold></ph-trash-bold>'; // Icono de cubo de basura de Phosphor
            deleteBtn.classList.add('btn', 'btn-eliminar');
            deleteBtn.title = 'Eliminar Registro';
            deleteBtn.addEventListener('click', () => confirmDeleteRecord(record.id));
            actionsCell.appendChild(deleteBtn);
        });
    }

    // --- Funciones de Acción (Marcas de tiempo, ver, editar, eliminar) ---

    // Función para Marcar Salida
    async function markExit(accessId) {
        showStatusMessage('Marcando salida...', 'info');
        try {
            const response = await fetch(`${API_BASE_URL}/access/${accessId}`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${accessToken}`
                },
                body: JSON.stringify({ exit_date: new Date().toISOString() }) // Enviar la hora actual
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Error al marcar salida');
            }

            showStatusMessage('Salida marcada exitosamente.', 'success');
            // Recargar registros para reflejar el cambio
            await loadAccessRecords(fechaFilterInput.value, documentoFilterInput.value);
        } catch (error) {
            console.error('Error al marcar salida:', error);
            showStatusMessage(`Error al marcar salida: ${error.message}`, 'error');
        }
    }

    // Función para Ver Detalles (puedes implementarla como un modal o redirigir)
    async function viewRecord(accessId) {
        showStatusMessage(`Ver registro ${accessId}`, 'info');
        // Implementa aquí la lógica para mostrar un modal con los detalles completos
        // o redirigir a una página de detalles.
    }

    // Función para Editar Registro (puedes implementarla como un modal o redirigir)
    async function editRecord(accessId) {
        showStatusMessage(`Editar registro ${accessId}`, 'info');
        // Implementa aquí la lógica para un formulario de edición en un modal
        // o redirigir a una página de edición con los datos del registro.
    }

    // Función para Confirmar Eliminación (usar un modal personalizado, NO alert/confirm)
    async function confirmDeleteRecord(accessId) {
        // En lugar de confirm(), usa un modal de confirmación HTML/CSS personalizado
        // Por ahora, un mensaje simple para demostrar
        if (window.confirm(`¿Estás seguro de eliminar el registro ${accessId}?`)) {
            await deleteRecord(accessId);
        }
    }

    // Función para Eliminar Registro
    async function deleteRecord(accessId) {
        showStatusMessage('Eliminando registro...', 'info');
        try {
            const response = await fetch(`${API_BASE_URL}/access/${accessId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${accessToken}`
                }
            });

            if (response.status === 204) { // 204 No Content para eliminación exitosa
                showStatusMessage('Registro eliminado exitosamente.', 'success');
                // Recargar registros para reflejar el cambio
                await loadAccessRecords(fechaFilterInput.value, documentoFilterInput.value);
            } else if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Error al eliminar registro');
            } else {
                showStatusMessage('Registro eliminado, pero la respuesta no fue 204.', 'info');
                await loadAccessRecords(fechaFilterInput.value, documentoFilterInput.value);
            }
        } catch (error) {
            console.error('Error al eliminar registro:', error);
            showStatusMessage(`Error al eliminar registro: ${error.message}`, 'error');
        }
    }

    // --- Inicialización y Event Listeners ---
    // Establecer la fecha actual en el filtro al cargar
    const today = new Date();
    const year = today.getFullYear();
    const month = String(today.getMonth() + 1).padStart(2, '0');
    const day = String(today.getDate()).padStart(2, '0');
    fechaFilterInput.value = `${year}-${month}-${day}`;

    // Cargar los registros del día actual al inicio
    await loadAccessRecords(fechaFilterInput.value);

    // Event Listeners para los botones de filtro
    searchDateBtn.addEventListener('click', () => {
        loadAccessRecords(fechaFilterInput.value, documentoFilterInput.value);
    });

    searchDocumentBtn.addEventListener('click', () => {
        loadAccessRecords(fechaFilterInput.value, documentoFilterInput.value);
    });

    clearFiltersBtn.addEventListener('click', () => {
        fechaFilterInput.value = ''; // Limpiar campo de fecha
        documentoFilterInput.value = ''; // Limpiar campo de documento
        loadAccessRecords(); // Cargar todos los registros sin filtros
    });

    // Añadir listener para el Enter en los campos de filtro
    fechaFilterInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            loadAccessRecords(fechaFilterInput.value, documentoFilterInput.value);
        }
    });

    documentoFilterInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            loadAccessRecords(fechaFilterInput.value, documentoFilterInput.value);
        }
    });
});
