/* =====================================
   PHISHING CHECKER - FRONTEND MVP
===================================== */

const form = document.getElementById("phishingForm");

const resultCard = document.getElementById("resultCard");

const resultIcon = document.getElementById("resultIcon");

const resultTitle = document.getElementById("resultTitle");

const resultMessage = document.getElementById("resultMessage");

const riskLevel = document.getElementById("riskLevel");

const warningList = document.getElementById("warningList");


form.addEventListener("submit", async function(event) {
    event.preventDefault();

    const url = document.getElementById("urlInput").value.trim();
    if (!url) return;

    if (window.API && typeof API.checkPhishing === "function") {
        try {
            const res = await API.checkPhishing(url);
            if (res.success) {
                renderBackendResult(res);
                return;
            }
        } catch (err) {
            console.warn("Backend phishing API unavailable, using local rules fallback:", err);
        }
    }

    // Fallback to local heuristic checks
    analyzeURL(url);
});

function renderBackendResult(res) {
    resultCard.classList.remove("hidden");
    warningList.innerHTML = "";

    const level = (res.risk_level || "low").toLowerCase();
    if (level === "critical" || level === "high") {
        resultIcon.textContent = "🔴";
    } else if (level === "medium") {
        resultIcon.textContent = "🟡";
    } else {
        resultIcon.textContent = "🟢";
    }

    resultTitle.textContent = res.risk_classification || (res.risk_level + " Risk");
    resultMessage.textContent = res.recommended_action || "Review indicators carefully before interacting with this URL.";
    riskLevel.textContent = `${(res.risk_level || "UNKNOWN").toUpperCase()} (${res.risk_score || 0}/100)`;

    const indicators = res.indicators || [];
    if (indicators.length === 0) {
        const item = document.createElement("li");
        item.textContent = "✓ No major phishing indicators detected by heuristic rules.";
        warningList.appendChild(item);
    } else {
        indicators.forEach(ind => {
            const item = document.createElement("li");
            item.textContent = "⚠️ " + ind;
            warningList.appendChild(item);
        });
    }

    resultCard.scrollIntoView({ behavior: "smooth" });
}


function analyzeURL(url) {

    let risks = [];


    /* IP ADDRESS AS DOMAIN */

    const ipPattern =
        /^(https?:\/\/)?(\d{1,3}\.){3}\d{1,3}/;

    if (ipPattern.test(url)) {

        risks.push(
            "IP address is being used instead of a normal domain."
        );

    }


    /* @ SYMBOL */

    if (url.includes("@")) {

        risks.push(
            "URL contains an @ symbol, which can be suspicious."
        );

    }


    /* HTTPS */

    if (!url.toLowerCase().startsWith("https://")) {

        risks.push(
            "Website does not use HTTPS."
        );

    }


    /* TOO MANY SUBDOMAINS */

    try {

        let cleanURL = url
            .replace(/^https?:\/\//, "")
            .split("/")[0];

        let dots =
            (cleanURL.match(/\./g) || []).length;

        if (dots >= 3) {

            risks.push(
                "URL contains multiple subdomains."
            );

        }

    } catch (error) {

        risks.push(
            "URL structure could not be properly analyzed."
        );

    }


    /* SUSPICIOUS KEYWORDS */

    const suspiciousWords = [
        "login",
        "verify",
        "verification",
        "account",
        "password",
        "secure",
        "update",
        "confirm",
        "bank",
        "free",
        "winner"
    ];


    const lowerURL =
        url.toLowerCase();


    const foundWords =
        suspiciousWords.filter(word =>
            lowerURL.includes(word)
        );


    if (foundWords.length > 0) {

        risks.push(
            "URL contains potentially suspicious keywords: "
            + foundWords.join(", ")
        );

    }


    showResult(risks);

}


/* =====================================
   SHOW RESULT
===================================== */

function showResult(risks) {

    resultCard.classList.remove("hidden");

    warningList.innerHTML = "";


    if (risks.length === 0) {

        resultIcon.textContent = "🟢";

        resultTitle.textContent =
            "Low Risk";

        resultMessage.textContent =
            "No common phishing indicators were detected by this basic checker.";

        riskLevel.textContent =
            "LOW";


    } else if (risks.length <= 2) {

        resultIcon.textContent = "🟡";

        resultTitle.textContent =
            "Suspicious URL";

        resultMessage.textContent =
            "Some indicators were detected. Verify the website before continuing.";

        riskLevel.textContent =
            "MEDIUM";


    } else {

        resultIcon.textContent = "🔴";

        resultTitle.textContent =
            "High Risk URL";

        resultMessage.textContent =
            "Multiple phishing indicators were detected. Avoid opening or entering sensitive information.";

        riskLevel.textContent =
            "HIGH";

    }


    /* DISPLAY WARNINGS */

    if (risks.length === 0) {

        const item =
            document.createElement("li");

        item.textContent =
            "✓ No common red flags detected.";

        warningList.appendChild(item);

    } else {

        risks.forEach(risk => {

            const item =
                document.createElement("li");

            item.textContent =
                "⚠️ " + risk;

            warningList.appendChild(item);

        });

    }


    resultCard.scrollIntoView({
        behavior: "smooth"
    });

}