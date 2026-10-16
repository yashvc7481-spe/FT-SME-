/**
 * CyberGuard SME - Global Client Configuration
 * Configure your live production backend URL here.
 * If deploying to Vercel, you can set your Render/Railway backend URL below,
 * or use Vercel rewrites to proxy /api to your backend.
 */
window.CYBERGUARD_CONFIG = {
    // Set this to your live Render/Railway backend URL after deploying backend:
    // e.g. "https://cyberguard-sme-backend.onrender.com/api"
    apiUrl: (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1")
        ? "http://127.0.0.1:5000/api"
        : "/api"
};
