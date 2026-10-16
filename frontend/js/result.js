/* =====================================
   CYBERGUARD ASSESSMENT RESULT - Backend Connected & Resilient
===================================== */

document.addEventListener("DOMContentLoaded", async function () {
    let score = Number(localStorage.getItem("assessmentScore")) || 0;
    let riskLevel = localStorage.getItem("assessmentRisk") || "";

    // If API is available, try fetching the latest recorded assessment from backend
    if (window.API && localStorage.getItem("cyberGuardToken")) {
        try {
            const res = await API.getAssessmentHistory();
            if (res.success && res.history && res.history.length > 0) {
                const latest = res.history[0];
                score = Number(latest.score) || score;
                riskLevel = latest.risk_level || riskLevel;
                localStorage.setItem("assessmentScore", score);
                localStorage.setItem("assessmentRisk", riskLevel);
            }
        } catch (err) {
            console.warn("Could not fetch remote assessment history, using local cache:", err);
        }
    }

    renderResult(score, riskLevel);
});

function renderResult(score, riskLevel) {
    const scoreElement = document.getElementById("score");
    const statusElement = document.getElementById("status");
    const riskLevelElement = document.getElementById("riskLevel");
    const descriptionElement = document.getElementById("description");
    const messageElement = document.getElementById("message");
    const strengthText = document.getElementById("strengthText");
    const improvementText = document.getElementById("improvementText");
    const recommendationsContainer = document.getElementById("recommendations");
    const scoreCircle = document.querySelector(".score-circle");

    // Display score
    if (scoreElement) {
        scoreElement.textContent = score + "%";
    }

    // Update gradient circle
    if (scoreCircle) {
        const degrees = Math.min(360, Math.max(0, score * 3.6));
        const color = score >= 80 ? "#10b981" : score >= 60 ? "#2563eb" : score >= 40 ? "#f59e0b" : "#ef4444";
        scoreCircle.style.background = `conic-gradient(${color} ${degrees}deg, #e2e8f0 ${degrees}deg)`;
    }

    let statusTitle = "";
    let descText = "";
    let strength = "";
    let improvement = "";
    let recs = [];

    if (score >= 80) {
        statusTitle = "Excellent Security Posture 🛡️";
        descText = "Your organization demonstrates strong cybersecurity practices and resilience.";
        strength = "Strong security awareness, solid authentication, and active protection controls.";
        improvement = "Continue proactive monitoring, maintain incident plans, and update configurations.";
        recs = [
            "Maintain regular multi-factor authentication (MFA) audits.",
            "Continue recurring employee phishing simulations.",
            "Schedule automated weekly backups and quarterly disaster recovery tests."
        ];
    } else if (score >= 60) {
        statusTitle = "Good Security Posture 👍";
        descText = "Your organization has a solid baseline, but several key vulnerabilities require attention.";
        strength = "Core security policies are active with moderate defense controls.";
        improvement = "Strengthen credential management, automate backups, and run regular staff training.";
        recs = [
            "Enable Multi-Factor Authentication (MFA) across all administrative accounts.",
            "Conduct monthly employee phishing simulation drills.",
            "Automate encrypted offsite backups for critical business databases."
        ];
    } else if (score >= 40) {
        statusTitle = "Needs Improvement ⚠️";
        descText = "Several critical cybersecurity practices require immediate remediation.";
        strength = "Basic awareness identified, but multiple threat vectors remain exposed.";
        improvement = "Prioritize perimeter defenses, password policies, and employee awareness.";
        recs = [
            "Mandate complex passwords with MFA for all company accounts.",
            "Audit and patch outdated software and operating system packages.",
            "Implement standardized cloud backup procedures.",
            "Enroll all team members in CyberGuard SME security training."
        ];
    } else {
        statusTitle = "Critical Security Risk 🚨";
        descText = "Your organization is at severe risk of data breaches, ransomware, and identity theft.";
        strength = "Urgent opportunity to establish foundational cybersecurity defenses.";
        improvement = "Immediate intervention needed across access controls, patching, and data retention.";
        recs = [
            "Enforce Multi-Factor Authentication (MFA) on all email and system logins immediately.",
            "Perform immediate scans and updates on all networked devices.",
            "Establish automated, immutable backups disconnected from local networks.",
            "Train employees to identify phishing emails, suspicious links, and pretexting."
        ];
    }

    if (statusElement) statusElement.textContent = statusTitle;
    if (riskLevelElement) riskLevelElement.textContent = riskLevel || statusTitle;
    if (descriptionElement) descriptionElement.textContent = descText;
    if (messageElement) messageElement.textContent = descText;
    if (strengthText) strengthText.textContent = strength;
    if (improvementText) improvementText.textContent = improvement;

    if (recommendationsContainer) {
        recommendationsContainer.innerHTML = "";
        recs.forEach(rec => {
            const item = document.createElement("div");
            item.className = "recommendation-item";
            item.textContent = "✓ " + rec;
            recommendationsContainer.appendChild(item);
        });
    }
}
