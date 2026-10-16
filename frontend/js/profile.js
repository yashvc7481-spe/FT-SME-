/* =====================================
   CYBERGUARD PROFILE
===================================== */

document.addEventListener("DOMContentLoaded", async function () {
    let name = localStorage.getItem("userName") || "User";
    let email = localStorage.getItem("userEmail") || "user@example.com";
    let company = localStorage.getItem("companyName") || localStorage.getItem("company") || "My Company";

    if (window.API && typeof API.getProfile === "function") {
        try {
            const res = await API.getProfile();
            if (res.success && res.user) {
                name = res.user.name || name;
                email = res.user.email || email;
                company = res.user.company || company;
                localStorage.setItem("userName", name);
                localStorage.setItem("userEmail", email);
                localStorage.setItem("companyName", company);
            }
        } catch (err) {
            console.warn("Backend profile endpoint unavailable, using local state:", err);
        }
    }

    const displayName = document.getElementById("displayName");
    const displayEmail = document.getElementById("displayEmail");
    const nameInfo = document.getElementById("nameInfo");
    const emailInfo = document.getElementById("emailInfo");
    const companyInfo = document.getElementById("companyInfo");
    const avatar = document.getElementById("avatar");

    if (displayName) displayName.textContent = name;
    if (displayEmail) displayEmail.textContent = email;
    if (nameInfo) nameInfo.textContent = name;
    if (emailInfo) emailInfo.textContent = email;
    if (companyInfo) companyInfo.textContent = company;
    if (avatar) avatar.textContent = name.charAt(0).toUpperCase();
});

/* LOGOUT */
async function logout() {
    if (window.API && typeof API.logout === "function") {
        try {
            await API.logout();
        } catch (_) {}
    }

    localStorage.removeItem("userName");
    localStorage.removeItem("userEmail");
    localStorage.removeItem("companyName");
    localStorage.removeItem("isLoggedIn");
    localStorage.removeItem("cyberGuardToken");

    alert("You have been logged out.");
    window.location.href = "login.html";
}