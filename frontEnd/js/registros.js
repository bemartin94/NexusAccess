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
            displayAccessRecords(records);

        } catch (error) {
            console.error('Error en la conexión o procesamiento:', error);
            showStatusMessage('Error en la conexión con el servidor. Intenta de nuevo.', 'error');
            recordsTableBody.innerHTML = '<tr><td colspan="10" class="text-center">No se pudieron cargar los registros (problema de red).</td></tr>';
        }
    }

    // --- Renderizado de la Tabla ---
    function displayAccessRecords(records) {
        recordsTableBody.innerHTML = '';
        if (records.length === 0) {
            recordsTableBody.innerHTML = '<tr><td colspan="10" class="text-center">No hay registros para mostrar con los filtros actuales.</td></tr>';
            return;
        }

        records.forEach(record => {
            const row = recordsTableBody.insertRow();
            
            // Formato de fecha y hora para mostrar
            // entry_date es la fecha y hora completa de entrada. De ahí sacamos fecha y hora.
            // exit_date es la fecha y hora completa de salida. De ahí sacamos solo la hora.
            const entryDateOnly = formatDate(record.entry_date); 
            const entryTimeOnly = formatTime(record.entry_date); 
            const exitTimeOnly = formatTime(record.exit_date);
            
            // HEADERS (Columna Index) -> Propiedad JSON
            // 0: Fecha Entrada    -> record.entry_date (solo fecha)
            // 1: Visitante        -> record.visitor_name
            // 2: Tipo Doc.        -> record.id_card_type_name
            // 3: Nro. Documento   -> record.visitor_id_card
            // 4: Sede             -> record.venue_name
            // 5: Responsable      -> record.supervisor_name
            // 6: Hora Entrada     -> record.entry_date (solo hora)
            // 7: Hora Salida      -> record.exit_date (solo hora, o PENDIENTE)
            // 8: Motivo           -> record.access_reason
            // 9: Acciones         -> Botones

            row.insertCell(0).textContent = entryDateOnly; // FECHA ENTRADA
            row.insertCell(1).textContent = record.visitor_name || 'N/A'; // VISITANTE
            row.insertCell(2).textContent = record.id_card_type_name || 'N/A'; // TIPO DOC.
            row.insertCell(3).textContent = record.visitor_id_card || 'N/A'; // NRO. DOCUMENTO
            row.insertCell(4).textContent = record.venue_name || 'N/A'; // SEDE
            row.insertCell(5).textContent = record.supervisor_name || 'N/A'; // RESPONSABLE
            row.insertCell(6).textContent = entryTimeOnly; // HORA ENTRADA
            
            const exitCell = row.insertCell(7); // HORA SALIDA
            if (record.exit_date === null) {
                exitCell.innerHTML = '<span class="pending">PENDIENTE</span>';
            } else {
                exitCell.textContent = exitTimeOnly;
            }
            
            row.insertCell(8).textContent = record.access_reason || 'N/A'; // MOTIVO

            // Columna de Acciones
            const actionsCell = row.insertCell(9);
            actionsCell.classList.add('action-buttons');

            if (record.exit_date === null) {
                const markExitBtn = document.createElement('button');
                markExitBtn.textContent = 'Marcar Salida';
                markExitBtn.classList.add('btn', 'btn-salida');
                markExitBtn.addEventListener('click', () => markExit(record.id));
                actionsCell.appendChild(markExitBtn);
            }

            const viewBtn = document.createElement('button');
            viewBtn.innerHTML = '<ph-eye-bold></ph-eye-bold>';
            viewBtn.classList.add('btn', 'btn-ver');
            viewBtn.title = 'Ver Detalles';
            viewBtn.addEventListener('click', () => viewRecord(record.id));
            actionsCell.appendChild(viewBtn);

            const editBtn = document.createElement('button');
            editBtn.innerHTML = '<ph-pencil-simple-bold></ph-pencil-simple-bold>';
            editBtn.classList.add('btn', 'btn-editar');
            editBtn.title = 'Editar Registro';
            editBtn.addEventListener('click', () => editRecord(record.id));
            actionsCell.appendChild(editBtn);

            const deleteBtn = document.createElement('button');
            deleteBtn.innerHTML = '<ph-trash-bold></ph-trash-bold>';
            deleteBtn.classList.add('btn', 'btn-eliminar');
            deleteBtn.title = 'Eliminar Registro';
            deleteBtn.addEventListener('click', () => confirmDeleteRecord(record.id));
            actionsCell.appendChild(deleteBtn);
        });
    }

    async function markExit(accessId) {
        showStatusMessage('Marcando salida...', 'info');
        try {
            const response = await fetch(`${API_BASE_URL}/access/${accessId}`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${accessToken}`
                },
                body: JSON.stringify({ exit_date: new Date().toISOString() })
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
    }

    async function editRecord(accessId) {
        showStatusMessage(`Editar registro ${accessId}`, 'info');
    }

    async function confirmDeleteRecord(accessId) {
        if (window.confirm(`¿Estás seguro de eliminar el registro ${accessId}?`)) {
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