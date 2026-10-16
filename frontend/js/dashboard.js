/* =========================================
   CYBERGUARD DASHBOARD - Backend Connected
========================================= */


/* =========================================
   LOGIN CHECK
========================================= */

const isLoggedIn = localStorage.getItem("isLoggedIn");

if (isLoggedIn !== "true") {
    window.location.href = "login.html";
}


/* =========================================
   USER INFORMATION & LIVE METRICS
========================================= */

const userName = localStorage.getItem("userName");
const companyName = localStorage.getItem("companyName");
const userNameElement = document.getElementById("userName");

if (userNameElement && userName) {
    userNameElement.textContent = userName;
}


function animateScore(targetScore) {
    const scoreElement = document.getElementById("healthScore");
    if (!scoreElement) return;

    let currentScore = 0;
    scoreElement.textContent = "0";

    if (targetScore <= 0) {
        scoreElement.textContent = "0";
        return;
    }

    const intervalTime = Math.max(10, Math.floor(1000 / targetScore));
    const scoreAnimation = setInterval(() => {
        currentScore++;
        scoreElement.textContent = currentScore;
        if (currentScore >= targetScore) {
            clearInterval(scoreAnimation);
        }
    }, intervalTime);
}


/* Helper: safely set text for element by selector */
function setText(selector, value) {
    const el = document.querySelector(selector);
    if (el) el.textContent = value;
}


/* Helper: set progress bar width */
function setProgress(selector, pct) {
    const el = document.querySelector(selector);
    if (el) el.style.width = `${Math.min(Math.max(pct, 0), 100)}%`;
}


// Load real statistics from Flask backend
async function loadDashboardData() {
    let targetScore = 0;

    if (window.API && typeof API.getDashboardSummary === "function") {
        try {
            const res = await API.getDashboardSummary();
            if (res.success && res.stats) {

                // Update user greeting
                if (res.user && res.user.name && userNameElement) {
                    userNameElement.textContent = res.user.name;
                }

                const stats = res.stats;

                // Health score
                targetScore = stats.has_assessment ? stats.health_score : 0;

                // ---- Stat Cards ----
                // Assessment card
                const assessScore = stats.latest_assessment_score || 0;
                const assessRisk = stats.risk_level || "Not Assessed";
                setText(".stat-card.blue strong", assessScore > 0 ? `${assessScore}%` : "—");
                setText(".stat-card.blue p", `Risk: ${assessRisk}`);
                setProgress(".stat-card.blue .progress span", assessScore);

                // Phishing card — show scans count
                const scanCount = stats.total_phishing_scans || 0;
                const latestPhishScore = stats.latest_phishing_score || 0;
                const phishProtection = scanCount > 0
                    ? Math.max(0, 100 - latestPhishScore)
                    : 100;
                setText(".stat-card.red strong", `${scanCount} scan${scanCount !== 1 ? "s" : ""}`);
                setText(".stat-card.red p", scanCount > 0 ? `Last risk: ${stats.latest_phishing_level || "Low"}` : "No scans yet");
                setProgress(".stat-card.red .progress span", phishProtection);

                // Training card
                const quizCount = stats.completed_quizzes || 0;
                const avgScore = stats.average_quiz_score || 0;
                setText(".stat-card.purple strong", `${avgScore}%`);
                setText(".stat-card.purple p", `${quizCount} quiz${quizCount !== 1 ? "zes" : ""} completed`);
                setProgress(".stat-card.purple .progress span", avgScore);

                // Reports card — total activity count
                const totalActivity = (stats.total_assessments || 0)
                    + scanCount
                    + quizCount;
                setText(".stat-card.green strong", totalActivity);
                setText(".stat-card.green p", "Total security activities");
                setProgress(".stat-card.green .progress span",
                    Math.min(totalActivity * 8, 100));

                // ---- Recent Activity Feed ----
                const activities = res.recent_activities || [];
                renderRecentActivities(activities);

            }
        } catch (err) {
            console.warn("Could not reach backend dashboard summary, using local state:", err);
            const localAssessment = Number(localStorage.getItem("assessmentScore"));
            if (!isNaN(localAssessment) && localAssessment > 0) {
                targetScore = localAssessment;
            }
        }
    }

    animateScore(targetScore);
}


/* Render recent activities into the alerts panel */
function renderRecentActivities(activities) {
    if (!activities || activities.length === 0) return;

    // Find the panel that contains "Recent Security Alerts"
    const panels = document.querySelectorAll(".panel");
    let alertPanel = null;
    panels.forEach(p => {
        if (p.querySelector("h2") &&
            p.querySelector("h2").textContent.includes("Recent Security Alert")) {
            alertPanel = p;
        }
    });

    if (!alertPanel) return;

    // Clear existing static alerts
    const staticAlerts = alertPanel.querySelectorAll(".alert");
    staticAlerts.forEach(a => a.remove());

    if (activities.length === 0) return;

    const TYPE_ICONS = {
        assessment: "📊",
        phishing: "🔍",
        quiz: "🎓"
    };

    const TYPE_CSS = {
        assessment: "safe",
        phishing: "warning",
        quiz: "safe"
    };

    activities.forEach(act => {
        const icon = TYPE_ICONS[act.type] || "📋";
        const cls = TYPE_CSS[act.type] || "safe";
        const ts = act.created_at
            ? new Date(act.created_at).toLocaleString("en-IN", { dateStyle: "medium" })
            : "Recently";

        const div = document.createElement("div");
        div.className = `alert ${cls}`;
        div.innerHTML = `
            <div class="alert-icon">${icon}</div>
            <div>
                <strong>${escapeHtml(act.title)}</strong>
                <p>${escapeHtml(act.description)}</p>
                <small>${ts}</small>
            </div>`;
        alertPanel.appendChild(div);
    });
}


/* Helper: escape HTML */
function escapeHtml(text) {
    const div = document.createElement("div");
    div.appendChild(document.createTextNode(text || ""));
    return div.innerHTML;
}


loadDashboardData();


/* =========================================
   LOGOUT
========================================= */

async function logout() {
    const confirmLogout = confirm("Are you sure you want to logout?");
    if (!confirmLogout) return;

    if (window.API && typeof API.logout === "function") {
        try {
            await API.logout();
        } catch (_) {}
    }

    localStorage.removeItem("isLoggedIn");
    localStorage.removeItem("userName");
    localStorage.removeItem("userEmail");
    localStorage.removeItem("companyName");
    localStorage.removeItem("cyberGuardToken");

    window.location.href = "login.html";
}