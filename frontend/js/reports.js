/* =====================================
   CYBERGUARD REPORTS - Backend Connected
===================================== */

document.addEventListener("DOMContentLoaded", function () {

    /* Current Date */
    const dateElement = document.getElementById("reportDate");
    const today = new Date();
    const date = today.toLocaleDateString("en-IN", {
        day: "2-digit",
        month: "short",
        year: "numeric"
    });
    if (dateElement) dateElement.textContent = date;

    // Load report data from backend
    loadReportData();
});


async function loadReportData() {
    if (!window.API || !localStorage.getItem("cyberGuardToken")) {
        // Show local fallback values
        const name = localStorage.getItem("userName");
        if (name) console.log("Report generated for:", name);
        return;
    }

    try {
        const res = await API.getReportSummary();
        if (!res.success) return;

        // 1. Overall health score
        const overallScoreEl = document.getElementById("overallScore");
        if (overallScoreEl) {
            overallScoreEl.textContent = `${res.overall_health.score}%`;
        }

        // 2. Status badge and description
        const statusBadgeEl = document.querySelector(".status-badge");
        if (statusBadgeEl) {
            statusBadgeEl.textContent = res.overall_health.status.toUpperCase();
        }

        const statusDescEl = document.querySelector(".overall-info p");
        if (statusDescEl) {
            statusDescEl.textContent = res.overall_health.summary;
        }

        // 3. Score cards - Assessment
        const breakdown = res.breakdown || {};
        const assessmentScore = breakdown.assessment ? breakdown.assessment.latest_score : 0;
        const assessmentRisk = breakdown.assessment ? breakdown.assessment.risk_level : "Not assessed";
        const trainingScore = breakdown.training ? breakdown.training.average_score : 0;
        const phishingTotal = breakdown.phishing ? breakdown.phishing.total : 0;
        const phishingHigh = breakdown.phishing ? breakdown.phishing.high : 0;

        // Update score cards with real data
        const scoreCards = document.querySelectorAll(".score-card");
        if (scoreCards.length >= 3) {
            // Assessment card
            const aStrong = scoreCards[0].querySelector("strong");
            const aSmall = scoreCards[0].querySelector("small");
            const aBar = scoreCards[0].querySelector(".mini-progress div");
            if (aStrong) aStrong.textContent = `${assessmentScore}%`;
            if (aSmall) aSmall.textContent = assessmentRisk;
            if (aBar) aBar.style.width = `${assessmentScore}%`;

            // Phishing Protection card
            const phishScore = phishingTotal > 0
                ? Math.max(0, Math.round(100 - (phishingHigh / phishingTotal) * 100))
                : 100;
            const pStrong = scoreCards[1].querySelector("strong");
            const pSmall = scoreCards[1].querySelector("small");
            const pBar = scoreCards[1].querySelector(".mini-progress div");
            if (pStrong) pStrong.textContent = `${phishScore}%`;
            if (pSmall) pSmall.textContent = phishingHigh > 0 ? "Threats Detected" : "No Threats";
            if (pBar) pBar.style.width = `${phishScore}%`;

            // Training card
            const tStrong = scoreCards[2].querySelector("strong");
            const tSmall = scoreCards[2].querySelector("small");
            const tBar = scoreCards[2].querySelector(".mini-progress div");
            if (tStrong) tStrong.textContent = `${trainingScore}%`;
            if (tSmall) tSmall.textContent = trainingScore >= 70 ? "Good" : trainingScore >= 50 ? "Moderate" : "Needs Work";
            if (tBar) tBar.style.width = `${trainingScore}%`;
        }

        // 4. Performance table rows
        const tableRows = document.querySelectorAll(".performance-table .table-row:not(.table-head)");
        if (tableRows.length >= 4) {
            const getStatus = (score) => {
                if (score >= 80) return ["good-status", "Good"];
                if (score >= 60) return ["warning-status", "Moderate"];
                if (score > 0) return ["danger-status", "Needs Improvement"];
                return ["warning-status", "Not Assessed"];
            };

            // Assessment row
            const [aCls, aLbl] = getStatus(assessmentScore);
            tableRows[0].querySelector("strong").textContent = `${assessmentScore}%`;
            const aStatusEl = tableRows[0].querySelector("span:last-child");
            if (aStatusEl) { aStatusEl.className = aCls; aStatusEl.textContent = aLbl; }

            // Phishing row
            const phishPct = phishingTotal > 0
                ? Math.round(100 - (phishingHigh / phishingTotal) * 100)
                : 100;
            const [pCls, pLbl] = getStatus(phishPct);
            tableRows[1].querySelector("strong").textContent = `${phishPct}%`;
            const pStatusEl = tableRows[1].querySelector("span:last-child");
            if (pStatusEl) { pStatusEl.className = pCls; pStatusEl.textContent = pLbl; }

            // Training row
            const [tCls, tLbl] = getStatus(trainingScore);
            tableRows[2].querySelector("strong").textContent = `${trainingScore}%`;
            const tStatusEl = tableRows[2].querySelector("span:last-child");
            if (tStatusEl) { tStatusEl.className = tCls; tStatusEl.textContent = tLbl; }

            // Overall row
            const overallScore = res.overall_health.score;
            const [oCls, oLbl] = getStatus(overallScore);
            tableRows[3].querySelector("strong").textContent = `${overallScore}%`;
            const oStatusEl = tableRows[3].querySelector("span:last-child");
            if (oStatusEl) { oStatusEl.className = oCls; oStatusEl.textContent = oLbl; }
        }

        // 5. Recent scan history in key risks section
        const keyRisksEl = document.querySelector(".finding-card:first-child ul");
        if (keyRisksEl && res.recent_scans && res.recent_scans.length > 0) {
            const highRisk = res.recent_scans.filter(s =>
                s.risk_level === "High" || s.risk_level === "Critical"
            );
            if (highRisk.length > 0) {
                keyRisksEl.innerHTML = highRisk.slice(0, 3).map(s =>
                    `<li>⚠️ ${escapeHtml(s.risk_level)} risk URL scanned (Score: ${s.risk_score}/100)</li>`
                ).join("") + (highRisk.length === 0 ? "<li>No high-risk threats detected recently</li>" : "");
            }
        }

        // 6. Organization name from metadata
        const orgEl = document.querySelector(".overall-info h2");
        if (orgEl && res.metadata && res.metadata.organization !== "CyberGuard SME Enterprise") {
            orgEl.textContent = `${res.metadata.organization} — Security Report`;
        }

    } catch (err) {
        console.warn("Backend reports API unavailable:", err);
    }
}


/* PRINT REPORT */

function printReport() {
    window.print();
}


/* HELPER: escape HTML */

function escapeHtml(text) {
    const div = document.createElement("div");
    div.appendChild(document.createTextNode(text || ""));
    return div.innerHTML;
}