// frontEnd/js/registros.js

document.addEventListener('DOMContentLoaded', async () => {
    const accessToken = localStorage.getItem('access_token');
    if (!accessToken) {
        window.location.href = 'login.html';
        return;
    }

    const logoutButton = document.getElementById('logoutButton');
    if (logoutButton) {
        logoutButton.addEventListener('click', async () => {
            localStorage.removeItem('access_token');
            window.location.href = 'login.html';
        });
    }

    const API_BASE_URL = 'http://127.0.0.1:8000/app/v1';

    const fechaFilterInput = document.getElementById('fechaFilter');
    const documentoFilterInput = document.getElementById('documentoFilter');
    const searchDateBtn = document.getElementById('searchDateBtn');
    const searchDocumentBtn = document.getElementById('searchDocumentBtn');
    const clearFiltersBtn = document.getElementById('clearFiltersBtn');
    const recordsTableBody = document.getElementById('recordsTableBody');
    const statusMessageDiv = document.getElementById('statusMessage');

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
        const day = String(date.getDate()).padStart(2, '0');
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const year = date.getFullYear();
        return `${day}/${month}/${year}`;
    }

    function formatTime(isoString) {
        if (!isoString) return 'N/A';
        const date = new Date(isoString);
        const hours = String(date.getHours()).padStart(2, '0');
        const minutes = String(date.getMinutes()).padStart(2, '0');
        return `${hours}:${minutes}`;
    }

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
                const errorData = await response.json();
                console.error('Error al cargar registros:', errorData.detail || errorData.message || response.statusText);
                showStatusMessage(`Error al cargar registros: ${errorData.detail || response.statusText || 'Verifica la consola.'}`, 'error');
                recordsTableBody.innerHTML = `<tr><td colspan="10" class="text-center">Error: ${errorData.detail || 'No se pudieron cargar los registros.'}</td></tr>`;
                return;
            }

            const records = await response.json();
            console.log("Registros recibidos del backend:", records); // <--- AÑADIDA ESTA LÍNEA CLAVE PARA DEPURAR
            displayAccessRecords(records);

        } catch (error) {
            console.error('Error en la conexión o procesamiento:', error);
            showStatusMessage('Error en la conexión con el servidor. Intenta de nuevo.', 'error');
            recordsTableBody.innerHTML = '<tr><td colspan="10" class="text-center">No se pudieron cargar los registros (problema de red).</td></tr>';
        }
    }

    function displayAccessRecords(records) {
        recordsTableBody.innerHTML = '';
        if (records.length === 0) {
            recordsTableBody.innerHTML = '<tr><td colspan="10" class="text-center">No hay registros para mostrar con los filtros actuales.</td></tr>';
            return;
        }

        records.forEach(record => {
            const row = recordsTableBody.insertRow();
            
            const entryDateOnly = formatDate(record.entry_time); 
            const entryTimeOnly = formatTime(record.entry_time); 
            const exitTimeOnly = formatTime(record.exit_time);
            
            row.insertCell(0).textContent = entryDateOnly;
            row.insertCell(1).textContent = record.visitor_full_name || 'N/A';
            row.insertCell(2).textContent = record.id_card_type_name_at_access || 'N/A';
            row.insertCell(3).textContent = record.id_card_number_at_access || 'N/A';
            row.insertCell(4).textContent = record.venue_name || 'N/A';
            row.insertCell(5).textContent = record.logged_by_user_email || 'N/A';
            row.insertCell(6).textContent = entryTimeOnly;
            
            const exitCell = row.insertCell(7);
            if (record.exit_time === null) {
                exitCell.innerHTML = '<span class="pending">PENDIENTE</span>';
            } else {
                exitCell.textContent = exitTimeOnly;
            }
            
            row.insertCell(8).textContent = record.access_reason || 'N/A';

            const actionsCell = row.insertCell(9);
            actionsCell.classList.add('action-buttons'); 

            if (record.exit_time === null) {
                const markExitBtn = document.createElement('button');
                markExitBtn.textContent = 'Marcar Salida';
                markExitBtn.classList.add('btn', 'btn-salida');
                markExitBtn.addEventListener('click', () => markExit(record.id));
                actionsCell.appendChild(markExitBtn);
            }

            const viewBtn = document.createElement('button');
            viewBtn.innerHTML = '<i class="material-icons">visibility</i>'; 
            viewBtn.classList.add('btn', 'btn-icon', 'btn-ver'); 
            viewBtn.title = 'Ver Detalles';
            viewBtn.addEventListener('click', () => viewRecord(record.id));
            actionsCell.appendChild(viewBtn);

            const editBtn = document.createElement('button');
            editBtn.innerHTML = '<i class="material-icons">edit</i>'; 
            editBtn.classList.add('btn', 'btn-icon', 'btn-editar');
            editBtn.title = 'Editar Registro';
            editBtn.addEventListener('click', () => editRecord(record.id));
            actionsCell.appendChild(editBtn);

            const deleteBtn = document.createElement('button');
            deleteBtn.innerHTML = '<i class="material-icons">delete</i>'; 
            deleteBtn.classList.add('btn', 'btn-icon', 'btn-eliminar');
            deleteBtn.title = 'Eliminar Registro';
            deleteBtn.addEventListener('click', () => confirmDeleteRecord(record.id));
            actionsCell.appendChild(deleteBtn);

            const refreshBtn = document.createElement('button');
            refreshBtn.innerHTML = '<i class="material-icons">refresh</i>'; 
            refreshBtn.classList.add('btn', 'btn-icon', 'btn-refresh');
            refreshBtn.title = 'Actualizar Registro';
            refreshBtn.addEventListener('click', () => loadAccessRecords(fechaFilterInput.value, documentoFilterInput.value));
            actionsCell.appendChild(refreshBtn);
        });
    }

    async function markExit(accessId) {
        showStatusMessage('Marcando salida...', 'info');
        try {
            const response = await fetch(`${API_BASE_URL}/access/${accessId}/exit`, { 
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${accessToken}`
                },
            });

            if (!response.ok) {
                const errorData = await response.json();
                console.error('Error al marcar salida:', errorData.detail || errorData.message || response.statusText);
                throw new Error(errorData.detail || 'Error al marcar salida');
            }

            showStatusMessage('Salida marcada exitosamente.', 'success');
            await loadAccessRecords(fechaFilterInput.value, documentoFilterInput.value);
        } catch (error) {
            console.error('Error al marcar salida:', error);
            showStatusMessage(`Error al marcar salida: ${error.message}`, 'error');
        }
    }

    async function viewRecord(accessId) {
        showStatusMessage(`Ver registro ${accessId}`, 'info');
        console.log(`Función Ver Registro para ID: ${accessId}`);
    }

    async function editRecord(accessId) {
        showStatusMessage(`Editar registro ${accessId}`, 'info');
        console.log(`Función Editar Registro para ID: ${accessId}`);
    }

    async function confirmDeleteRecord(accessId) {
        if (window.confirm(`¿Estás seguro de eliminar el registro ${accessId}? Esta acción es irreversible.`)) {
            await deleteRecord(accessId);
        }
    }

    async function deleteRecord(accessId) {
        showStatusMessage('Eliminando registro...', 'info');
        try {
            const response = await fetch(`${API_BASE_URL}/access/${accessId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${accessToken}`
                }
            });

            if (response.status === 204) {
                showStatusMessage('Registro eliminado exitosamente.', 'success');
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

    const today = new Date();
    const year = today.getFullYear();
    const month = String(today.getMonth() + 1).padStart(2, '0');
    const day = String(today.getDate()).padStart(2, '0');
    fechaFilterInput.value = `${year}-${month}-${day}`;

    await loadAccessRecords(fechaFilterInput.value);

    searchDateBtn.addEventListener('click', () => {
        loadAccessRecords(fechaFilterInput.value, documentoFilterInput.value);
    });

    searchDocumentBtn.addEventListener('click', () => {
        loadAccessRecords(fechaFilterInput.value, documentoFilterInput.value);
    });

    clearFiltersBtn.addEventListener('click', () => {
        fechaFilterInput.value = '';
        documentoFilterInput.value = '';
        loadAccessRecords();
    });

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
