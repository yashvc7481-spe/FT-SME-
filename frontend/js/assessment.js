const questions = [

    {
        question: "Does your organization use strong passwords?",
        options: ["Yes", "No", "Partially"]
    },

    {
        question: "Is Multi-Factor Authentication (MFA) enabled?",
        options: ["Yes", "No", "Partially"]
    },

    {
        question: "Are operating systems and software regularly updated?",
        options: ["Yes", "No", "Sometimes"]
    },

    {
        question: "Does your organization maintain regular backups?",
        options: ["Yes", "No", "Sometimes"]
    },

    {
        question: "Are employees trained to identify phishing attacks?",
        options: ["Yes", "No", "Partially"]
    },

    {
        question: "Is antivirus or endpoint protection installed?",
        options: ["Yes", "No", "Partially"]
    },

    {
        question: "Does your organization have an incident response plan?",
        options: ["Yes", "No", "In Progress"]
    },

    {
        question: "Are sensitive company files access-controlled?",
        options: ["Yes", "No", "Partially"]
    },

    {
        question: "Is employee cybersecurity awareness regularly tested?",
        options: ["Yes", "No", "Sometimes"]
    },

    {
        question: "Does your organization monitor suspicious security activity?",
        options: ["Yes", "No", "Partially"]
    }

];


const container =
    document.getElementById("questionsContainer");


/* CREATE QUESTIONS */

questions.forEach((item, index) => {

    const card = document.createElement("div");

    card.className = "question-card";

    let optionsHTML = "";

    item.options.forEach(option => {

        optionsHTML += `
            <label class="option">

                <input
                    type="radio"
                    name="question${index}"
                    value="${option}"
                    onchange="updateProgress()"
                    required
                >

                <span>${option}</span>

            </label>
        `;

    });


    card.innerHTML = `

        <div class="question-number">
            QUESTION ${index + 1}
        </div>

        <h3>${item.question}</h3>

        ${optionsHTML}

    `;


    container.appendChild(card);

});


/* PROGRESS */

function updateProgress() {

    let answered = 0;

    questions.forEach((_, index) => {

        const selected =
            document.querySelector(
                `input[name="question${index}"]:checked`
            );

        if (selected) {
            answered++;
        }

    });


    const percentage =
        (answered / questions.length) * 100;


    document.getElementById("progressFill")
        .style.width = percentage + "%";


    document.getElementById("progressText")
        .textContent =
        `${answered} / ${questions.length}`;

}


/* SUBMIT */

document.getElementById("assessmentForm").addEventListener("submit", async function(event) {
    event.preventDefault();

    const answers = {};
    let score = 0;

    questions.forEach((_, index) => {
        const selected = document.querySelector(`input[name="question${index}"]:checked`);
        if (selected) {
            answers[`question${index}`] = selected.value;
            if (selected.value === "Yes") {
                score++;
            }
        }
    });

    let percentage = Math.round((score / questions.length) * 100);

    if (window.API && typeof API.submitAssessment === "function") {
        try {
            const res = await API.submitAssessment(answers);
            if (res.success && typeof res.score === "number") {
                percentage = res.score;
            }
        } catch (err) {
            console.warn("Backend assessment submission failed, using local score:", err);
        }
    }

    localStorage.setItem("assessmentScore", percentage);
    window.location.href = "assessment-result.html";
});