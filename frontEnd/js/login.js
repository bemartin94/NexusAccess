const API_BASE_URL = 'http://127.0.0.1:8000/app/v1'; // Asegúrate de que esta URL sea la correcta de tu backend
const AUTH_ENDPOINT = '/auth/token'; // Endpoint de autenticación

document.getElementById('loginForm').addEventListener('submit', async (event) => {
    event.preventDefault(); // Previene el envío tradicional del formulario

    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const loginStatusDiv = document.getElementById('loginStatus');

    loginStatusDiv.textContent = ''; // Limpiar mensajes anteriores
    loginStatusDiv.style.color = 'red'; // Color por defecto para errores

    const urlSearchParams = new URLSearchParams();
    urlSearchParams.append('username', username);
    urlSearchParams.append('password', password);

    try {
        const response = await fetch(`${API_BASE_URL}${AUTH_ENDPOINT}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: urlSearchParams.toString()
        });

        // --- Logs de depuración de la respuesta HTTP ---
        console.log('Raw response:', response);
        console.log('Response status:', response.status);
        console.log('Response OK:', response.ok);

        // Manejo de errores de respuesta HTTP (si el status no es 2xx)
        if (!response.ok) {
            const errorText = await response.text(); // Lee el cuerpo como texto para depurar errores
            console.error('Error response body (text):', errorText);
            loginStatusDiv.textContent = errorText || `Error de autenticación: ${response.status}.`;
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        // --- Intento de parsear la respuesta como JSON ---
        let result;
        try {
            result = await response.json(); // Intentar parsear la respuesta a JSON
            console.log('Parsed JSON result:', result); // Muestra el objeto JSON completo si tiene éxito
        } catch (jsonError) {
            // Si falla el parseo a JSON, es porque la respuesta no es JSON válido o está vacía
            console.error('Error parsing JSON response:', jsonError);
            const rawResponseText = await response.text(); // Vuelve a leer el cuerpo (ya que response.json() lo consumió parcialmente)
            console.error('Raw response text (if JSON parse failed):', rawResponseText);
            loginStatusDiv.textContent = 'Error: Respuesta inesperada del servidor (no es JSON válido o está vacía).';
            return; // Detener la ejecución del script aquí si el JSON no es válido
        }
        // ************************************************

        // Si el JSON se parseó correctamente, verificar el token y redirigir
        if (result.access_token) {
            localStorage.setItem('access_token', result.access_token);

            // Guardar los nuevos campos user_id y venue_id si están presentes
            if (result.user_id) {
                localStorage.setItem('user_id', result.user_id);
            }
            if (result.venue_id) {
                localStorage.setItem('user_venue_id', result.venue_id);
            }

            loginStatusDiv.textContent = 'Inicio de sesión exitoso. Redirigiendo...';
            loginStatusDiv.style.color = 'green';
            window.location.href = 'index.html'; // Redirigir a la página principal
        } else {
            loginStatusDiv.textContent = 'Respuesta inesperada del servidor: falta el token de acceso.';
        }

    } catch (error) {
        // Captura errores de red, errores de HTTP lanzados por 'throw new Error', o errores de JSON parseo
        console.error('Error general durante el fetch o procesamiento:', error);
        // Si el error ya fue manejado y se puso un mensaje específico, no sobrescribir
        if (!loginStatusDiv.textContent) { // Solo si no hay un mensaje anterior
            loginStatusDiv.textContent = `Error de conexión: ${error.message}`;
        }
    }
});