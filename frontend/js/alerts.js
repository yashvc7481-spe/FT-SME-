/* =====================================
   CYBERGUARD ALERTS - Backend Connected
===================================== */

let resolvedAlerts = 0;
let totalAlerts = 0;
let backendAlertsLoaded = false;

// Severity icon map
const SEVERITY_ICONS = {
    high: "🔴",
    warning: "🟠",
    medium: "🟡",
    info: "🟢",
    critical: "🔴"
};

const SEVERITY_LABELS = {
    high: "HIGH",
    warning: "HIGH",
    medium: "MEDIUM",
    info: "INFO",
    critical: "CRITICAL"
};

const SEVERITY_CLASSES = {
    high: "critical",
    warning: "high",
    medium: "medium",
    info: "safe",
    critical: "critical"
};


/* LOAD ALERTS FROM BACKEND */

async function loadAlertsFromBackend() {
    const alertList = document.getElementById("alertList");
    if (!alertList) return;

    if (!window.API || !localStorage.getItem("cyberGuardToken")) {
        // Not logged in — keep static fallback content
        updateCount();
        return;
    }

    try {
        const res = await API.getAlerts();
        if (!res.success) return;

        const alerts = res.alerts || [];
        totalAlerts = alerts.length;
        resolvedAlerts = alerts.filter(a => a.is_read).length;
        backendAlertsLoaded = true;

        // Count by severity for summary cards
        let critical = 0, high = 0, medium = 0, safe = 0;

        // Clear the static placeholder alerts and render real ones
        alertList.innerHTML = "";

        if (alerts.length === 0) {
            alertList.innerHTML = `
                <div class="alert-item safe" style="padding:2rem; text-align:center;">
                    <div class="alert-icon">✅</div>
                    <div class="alert-content">
                        <h3>No alerts at this time</h3>
                        <p>Your account has no pending security alerts. Keep up the good work!</p>
                    </div>
                </div>`;
        } else {
            alerts.forEach(alert => {
                const sev = (alert.severity || "info").toLowerCase();
                const icon = SEVERITY_ICONS[sev] || "🔵";
                const label = SEVERITY_LABELS[sev] || sev.toUpperCase();
                const cls = SEVERITY_CLASSES[sev] || "safe";
                const readClass = alert.is_read ? " read" : "";
                const btnText = alert.is_read ? "✓ Read" : "Mark Read";

                if (cls === "critical") critical++;
                else if (cls === "high") high++;
                else if (cls === "medium") medium++;
                else safe++;

                const ts = alert.created_at
                    ? new Date(alert.created_at).toLocaleString("en-IN", { dateStyle: "medium", timeStyle: "short" })
                    : "Recently";

                const div = document.createElement("div");
                div.className = `alert-item ${cls}${readClass}`;
                div.setAttribute("data-alert-id", alert.id);
                div.innerHTML = `
                    <div class="alert-icon">${icon}</div>
                    <div class="alert-content">
                        <span class="alert-level">${label}</span>
                        <h3>${escapeHtml(alert.title)}</h3>
                        <p>${escapeHtml(alert.message)}</p>
                        <small>${ts}</small>
                    </div>
                    <button class="read-btn" onclick="markReadById(this, ${alert.id})">${btnText}</button>`;
                alertList.appendChild(div);
            });
        }

        // Update summary counts from real data
        const critEl = document.getElementById("criticalCount");
        const highEl = document.getElementById("highCount");
        const medEl = document.getElementById("mediumCount");
        const safeEl = document.getElementById("resolvedCount");

        if (critEl) critEl.textContent = critical;
        if (highEl) highEl.textContent = high;
        if (medEl) medEl.textContent = medium;
        if (safeEl) safeEl.textContent = resolvedAlerts;

    } catch (err) {
        console.warn("Backend alerts unavailable, using static content:", err);
        updateCount();
    }
}


/* MARK SINGLE ALERT READ BY ID (backend) */

async function markReadById(button, alertId) {
    const alertEl = button.closest(".alert-item");

    if (alertEl && alertEl.classList.contains("read")) return;

    if (window.API && alertId) {
        try {
            await API.markAlertRead(alertId);
        } catch (err) {
            console.warn("Could not mark alert as read on backend:", err);
        }
    }

    if (alertEl) {
        alertEl.classList.add("read");
        button.textContent = "✓ Read";
        resolvedAlerts++;
        const safeEl = document.getElementById("resolvedCount");
        if (safeEl) safeEl.textContent = resolvedAlerts;
    }
}


/* MARK SINGLE ALERT AS READ (static fallback) */

function markRead(button) {
    const alert = button.closest(".alert-item");
    if (!alert || alert.classList.contains("read")) return;

    alert.classList.add("read");
    button.textContent = "✓ Read";
    resolvedAlerts++;
    updateCount();
}


/* MARK ALL AS READ */

async function markAllRead() {
    if (backendAlertsLoaded && window.API) {
        try {
            await API.markAllAlertsRead();
        } catch (err) {
            console.warn("Backend mark-all-read failed:", err);
        }
    }

    const alertItems = document.querySelectorAll(".alert-item");
    alertItems.forEach(alert => {
        if (!alert.classList.contains("safe") || backendAlertsLoaded) {
            alert.classList.add("read");
            const button = alert.querySelector(".read-btn");
            if (button) button.textContent = "✓ Read";
        }
    });

    resolvedAlerts = document.querySelectorAll(".alert-item.read").length;

    const safeEl = document.getElementById("resolvedCount");
    if (safeEl) safeEl.textContent = resolvedAlerts;

    updateCount();
}


/* UPDATE SUMMARY COUNT */

function updateCount() {
    const safeEl = document.getElementById("resolvedCount");
    if (safeEl) safeEl.textContent = resolvedAlerts;
}


/* HELPER: escape HTML to prevent XSS */

function escapeHtml(text) {
    const div = document.createElement("div");
    div.appendChild(document.createTextNode(text || ""));
    return div.innerHTML;
}


/* INIT */

window.addEventListener("DOMContentLoaded", () => {
    updateCount();
    loadAlertsFromBackend();
});