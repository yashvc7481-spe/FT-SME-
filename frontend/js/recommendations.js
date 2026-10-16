/* =====================================
   RECOMMENDATIONS - Backend Connected
===================================== */

let completed = 0;
let totalRecs = 0;
let backendRecsLoaded = false;

const PRIORITY_ICONS = {
    "High": "🔴",
    "Medium": "🟡",
    "Low": "🟢"
};

const PRIORITY_CSS = {
    "High": "high",
    "Medium": "medium",
    "Low": "good"
};

const PRIORITY_LABEL_CSS = {
    "High": "high-label",
    "Medium": "medium-label",
    "Low": "good-label"
};

const CATEGORY_ICONS = {
    "Access Control": "🔐",
    "Credentials": "🔑",
    "Disaster Recovery": "💾",
    "Vulnerability Management": "🔄",
    "Human Defense": "🎣",
    "Preparedness": "📋",
    "Baseline Assessment": "📊",
    "Employee Awareness": "🎓"
};


/* LOAD RECOMMENDATIONS FROM BACKEND */

async function loadRecommendationsFromBackend() {
    const recList = document.getElementById("recommendationList");
    if (!recList) return;

    if (!window.API || !localStorage.getItem("cyberGuardToken")) {
        // Not logged in — restore saved progress from localStorage
        restoreLocalProgress();
        return;
    }

    try {
        const res = await API.getRecommendations();
        if (!res.success || !res.recommendations) {
            restoreLocalProgress();
            return;
        }

        const recs = res.recommendations;
        totalRecs = recs.length;
        backendRecsLoaded = true;

        let highCount = 0;
        let mediumCount = 0;

        // Clear static placeholder cards
        recList.innerHTML = "";

        recs.forEach((rec, idx) => {
            const priority = rec.priority || "Medium";
            const cls = PRIORITY_CSS[priority] || "medium";
            const labelCls = PRIORITY_LABEL_CSS[priority] || "medium-label";
            const icon = CATEGORY_ICONS[rec.category] || "🛡️";
            const prioIcon = PRIORITY_ICONS[priority] || "🟡";

            if (priority === "High") highCount++;
            else if (priority === "Medium") mediumCount++;

            const div = document.createElement("div");
            div.className = `recommendation-card ${cls}`;
            div.setAttribute("data-rec-idx", idx);
            div.innerHTML = `
                <div class="rec-icon">${icon}</div>
                <div class="rec-content">
                    <span class="priority ${labelCls}">${prioIcon} ${priority.toUpperCase()} PRIORITY</span>
                    <h3>${escapeHtml(rec.title)}</h3>
                    <p>${escapeHtml(rec.issue || "")}</p>
                    ${rec.why_it_matters ? `<p class="rec-why"><em>Why it matters: ${escapeHtml(rec.why_it_matters)}</em></p>` : ""}
                    ${rec.recommended_action ? `<p class="rec-action"><strong>Action: </strong>${escapeHtml(rec.recommended_action)}</p>` : ""}
                    <button onclick="completeRecommendation(this)">✓ Mark as Completed</button>
                </div>`;
            recList.appendChild(div);
        });

        // Update summary counts
        const highEl = document.getElementById("highCount");
        const medEl = document.getElementById("mediumCount");
        const healthEl = document.getElementById("healthScore");

        if (highEl) highEl.textContent = highCount;
        if (medEl) medEl.textContent = mediumCount;

        // Show health score from assessment if available
        if (healthEl) {
            try {
                const dashRes = await API.getDashboardSummary();
                if (dashRes.success && dashRes.stats) {
                    const score = dashRes.stats.has_assessment
                        ? dashRes.stats.health_score
                        : 0;
                    healthEl.textContent = `${score}%`;
                }
            } catch (_) {}
        }

        // Restore any locally saved completed state
        restoreLocalProgress();
        updateProgress();

    } catch (err) {
        console.warn("Backend recommendations unavailable, using static content:", err);
        restoreLocalProgress();
    }
}


/* COMPLETE RECOMMENDATION */

function completeRecommendation(button) {
    const card = button.closest(".recommendation-card");
    if (!card || card.classList.contains("completed")) return;

    card.classList.add("completed");
    button.textContent = "✓ Completed";

    completed++;
    updateProgress();

    localStorage.setItem("completedRecommendations", completed);
}


/* UPDATE PROGRESS BAR */

function updateProgress() {
    const total = backendRecsLoaded
        ? totalRecs
        : document.querySelectorAll(".recommendation-card").length;

    const percentage = total > 0 ? Math.round((completed / total) * 100) : 0;

    const countEl = document.getElementById("completedCount");
    const pctEl = document.getElementById("progressPercent");
    const fillEl = document.getElementById("progressFill");

    if (countEl) countEl.textContent = completed;
    if (pctEl) pctEl.textContent = `${percentage}%`;
    if (fillEl) fillEl.style.width = `${percentage}%`;
}


/* RESTORE LOCALLY SAVED PROGRESS */

function restoreLocalProgress() {
    const saved = parseInt(localStorage.getItem("completedRecommendations")) || 0;
    completed = saved;

    const cards = document.querySelectorAll(".recommendation-card");
    for (let i = 0; i < saved && i < cards.length; i++) {
        cards[i].classList.add("completed");
        const button = cards[i].querySelector("button");
        if (button) button.textContent = "✓ Completed";
    }

    updateProgress();
}


/* HELPER: escape HTML */

function escapeHtml(text) {
    const div = document.createElement("div");
    div.appendChild(document.createTextNode(text || ""));
    return div.innerHTML;
}


/* INIT */

window.addEventListener("DOMContentLoaded", () => {
    loadRecommendationsFromBackend();
});