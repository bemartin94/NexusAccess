const API_BASE_URL = 'http://127.0.0.1:8000/app/v1'; // Base URL de tu API
// Si elegiste Opción A para corregir la URL, este sería tu AUTH_ENDPOINT:
const AUTH_ENDPOINT = '/auth/token'; // Endpoint de autenticación (ya sin el doble /auth)

document.getElementById('loginForm').addEventListener('submit', async (event) => {
    event.preventDefault();

    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const loginStatusDiv = document.getElementById('loginStatus');

    loginStatusDiv.textContent = '';
    loginStatusDiv.style.color = 'red';

    const urlSearchParams = new URLSearchParams();
    urlSearchParams.append('username', username);
    urlSearchParams.append('password', password);
    urlSearchParams.append('grant_type', 'password'); // <--- ¡MUY IMPORTANTE AÑADIR ESTA LÍNEA!

    try {
        const response = await fetch(`${API_BASE_URL}${AUTH_ENDPOINT}`, { // Usa la URL corregida
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: urlSearchParams.toString()
        });

        console.log('Raw response:', response);
        console.log('Response status:', response.status);
        console.log('Response OK:', response.ok);

        if (!response.ok) {
            const errorData = await response.json(); // Intentamos leer JSON si no es OK
            console.error('Error response body:', errorData);
            loginStatusDiv.textContent = errorData.detail || `Error de autenticación: ${response.status}.`;
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json(); 
        console.log('Parsed JSON result:', result);

        if (result.access_token) {
            localStorage.setItem('access_token', result.access_token);
            if (result.user_id) {
                localStorage.setItem('user_id', result.user_id);
            }
            if (result.venue_id) {
                localStorage.setItem('user_venue_id', result.venue_id);
            }

            loginStatusDiv.textContent = 'Inicio de sesión exitoso. Redirigiendo...';
            loginStatusDiv.style.color = 'green';
            window.location.href = 'index.html';
        } else {
            loginStatusDiv.textContent = 'Respuesta inesperada del servidor: falta el token de acceso.';
        }

    } catch (error) {
        console.error('Error general durante el fetch o procesamiento:', error);
        if (!loginStatusDiv.textContent) {
            loginStatusDiv.textContent = `Error de conexión: ${error.message}`;
        }
    }
});