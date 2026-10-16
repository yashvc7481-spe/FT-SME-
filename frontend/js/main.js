/**
 * CyberGuard SME - Main Frontend Utilities
 */

document.addEventListener("DOMContentLoaded", function () {
    // Check if backend API is active
    if (window.API && typeof API.request === "function") {
        fetch("http://127.0.0.1:5000/api/health")
            .then(res => res.json())
            .then(data => {
                if (data.status === "healthy") {
                    console.log("CyberGuard SME Backend connected: healthy");
                }
            })
            .catch(() => {
                console.log("CyberGuard SME Backend offline (operating in local fallback mode)");
            });
    }
});
