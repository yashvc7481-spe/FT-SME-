/* =====================================
   CYBERGUARD AUTH - Backend Connected
===================================== */

document.addEventListener("DOMContentLoaded", function () {
    const loginForm = document.getElementById("loginForm");
    if (loginForm && !loginForm.dataset.listenerAttached) {
        loginForm.dataset.listenerAttached = "true";
        loginForm.addEventListener("submit", async function(event) {
            event.preventDefault();

            const emailInput = document.getElementById("email");
            const passwordInput = document.getElementById("password");

            const email = emailInput ? emailInput.value.trim() : "";
            const password = passwordInput ? passwordInput.value : "";

            if (!email || !password) {
                alert("Please fill in both email and password.");
                return;
            }

            if (window.API && typeof API.login === "function") {
                try {
                    const res = await API.login(email, password);
                    if (res.success) {
                        localStorage.setItem("isLoggedIn", "true");
                        localStorage.setItem("userName", res.user?.name || "User");
                        localStorage.setItem("userEmail", res.user?.email || email);
                        localStorage.setItem("companyName", res.user?.company || "");
                        alert("Login successful!");
                        window.location.href = "dashboard.html";
                        return;
                    } else {
                        alert(res.message || "Invalid email or password.");
                        return;
                    }
                } catch (err) {
                    console.warn("Backend login failed, using local fallback:", err);
                }
            }

            // Fallback for standalone demo mode
            localStorage.setItem("userEmail", email);
            localStorage.setItem("userName", email.split("@")[0]);
            localStorage.setItem("isLoggedIn", "true");
            alert("Login successful!");
            window.location.href = "dashboard.html";
        });
    }
});