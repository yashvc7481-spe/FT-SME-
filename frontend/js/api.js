/**
 * CyberGuard SME - Frontend API Service Client
 * Handles communication with Flask backend at http://127.0.0.1:5000/api
 * Features automatic bearer token injection and transparent offline fallback.
 */

const API_BASE_URL = 
    (window.CYBERGUARD_CONFIG && window.CYBERGUARD_CONFIG.apiUrl)
    || window.CYBERGUARD_API_URL
    || localStorage.getItem("cyberGuardApiUrl")
    || ((window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1")
        ? "http://127.0.0.1:5000/api"
        : "/api");

const API = {
    getToken() {
        return localStorage.getItem("cyberGuardToken") || "";
    },

    setToken(token) {
        if (token) {
            localStorage.setItem("cyberGuardToken", token);
        } else {
            localStorage.removeItem("cyberGuardToken");
        }
    },

    async request(endpoint, options = {}) {
        const url = `${API_BASE_URL}${endpoint}`;
        const headers = {
            "Content-Type": "application/json",
            ...(options.headers || {})
        };

        const token = this.getToken();
        if (token) {
            headers["Authorization"] = `Bearer ${token}`;
        }

        const config = {
            ...options,
            headers
        };

        try {
            const response = await fetch(url, config);
            const data = await response.json().catch(() => ({}));

            if (!response.ok) {
                const error = new Error(data.message || `Request failed with status ${response.status}`);
                error.status = response.status;
                error.data = data;
                throw error;
            }

            return data;
        } catch (err) {
            // Re-throw with helpful message
            throw err;
        }
    },

    // ----------------------------------------------------
    // AUTHENTICATION
    // ----------------------------------------------------
    async register(name, email, password, company = "") {
        const res = await this.request("/auth/register", {
            method: "POST",
            body: JSON.stringify({ name, email, password, company })
        });
        if (res.token) {
            this.setToken(res.token);
        }
        return res;
    },

    async login(email, password) {
        const res = await this.request("/auth/login", {
            method: "POST",
            body: JSON.stringify({ email, password })
        });
        if (res.token) {
            this.setToken(res.token);
        }
        return res;
    },

    async logout() {
        try {
            await this.request("/auth/logout", { method: "POST" });
        } catch (_) {}
        this.setToken(null);
        localStorage.removeItem("isLoggedIn");
        localStorage.removeItem("userName");
        localStorage.removeItem("userEmail");
        localStorage.removeItem("companyName");
    },

    async getCurrentUser() {
        return await this.request("/auth/me", { method: "GET" });
    },

    // ----------------------------------------------------
    // PROFILE
    // ----------------------------------------------------
    async getProfile() {
        return await this.request("/profile", { method: "GET" });
    },

    async updateProfile(profileData) {
        return await this.request("/profile", {
            method: "PUT",
            body: JSON.stringify(profileData)
        });
    },

    // ----------------------------------------------------
    // PHISHING DETECTION
    // ----------------------------------------------------
    async checkPhishing(url) {
        return await this.request("/phishing/check", {
            method: "POST",
            body: JSON.stringify({ url })
        });
    },

    async getPhishingHistory() {
        return await this.request("/phishing/history", { method: "GET" });
    },

    // ----------------------------------------------------
    // ASSESSMENT
    // ----------------------------------------------------
    async getAssessmentQuestions() {
        return await this.request("/assessment/questions", { method: "GET" });
    },

    async submitAssessment(answers) {
        return await this.request("/assessment/submit", {
            method: "POST",
            body: JSON.stringify({ answers })
        });
    },

    async getAssessmentHistory() {
        return await this.request("/assessment/history", { method: "GET" });
    },

    async getLatestAssessment() {
        return await this.request("/assessment/latest", { method: "GET" });
    },

    // ----------------------------------------------------
    // TRAINING & QUIZZES
    // ----------------------------------------------------
    async getTrainingQuestions() {
        return await this.request("/training/questions", { method: "GET" });
    },

    async submitQuiz(answers) {
        return await this.request("/training/submit", {
            method: "POST",
            body: JSON.stringify({ answers })
        });
    },

    async getTrainingHistory() {
        return await this.request("/training/history", { method: "GET" });
    },

    // ----------------------------------------------------
    // DASHBOARD & SUMMARY
    // ----------------------------------------------------
    async getDashboardSummary() {
        return await this.request("/dashboard/summary", { method: "GET" });
    },

    // ----------------------------------------------------
    // RECOMMENDATIONS
    // ----------------------------------------------------
    async getRecommendations() {
        return await this.request("/recommendations", { method: "GET" });
    },

    // ----------------------------------------------------
    // ALERTS
    // ----------------------------------------------------
    async getAlerts() {
        return await this.request("/alerts", { method: "GET" });
    },

    async markAlertRead(alertId) {
        return await this.request(`/alerts/${alertId}/read`, { method: "PUT" });
    },

    async markAllAlertsRead() {
        return await this.request("/alerts/read-all", { method: "PUT" });
    },

    // ----------------------------------------------------
    // REPORTS
    // ----------------------------------------------------
    async getReportSummary() {
        return await this.request("/reports/summary", { method: "GET" });
    }
};

window.CyberGuardAPI = API;
