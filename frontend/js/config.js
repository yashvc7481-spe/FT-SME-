/**
 * CyberGuard SME - Global Client Configuration
 * Connected to live production Render backend: https://cyberguard-backend-do37.onrender.com/api
 */
window.CYBERGUARD_CONFIG = {
    apiUrl: (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1")
        ? "http://127.0.0.1:5000/api"
        : "https://cyberguard-backend-do37.onrender.com/api"
};
