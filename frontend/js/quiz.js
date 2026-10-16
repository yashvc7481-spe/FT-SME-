/* =====================================
   CYBERGUARD TRAINING & QUIZ
===================================== */


/* QUESTIONS */

const questions = [

    {
        topic: "Phishing",
        question: "What should you do if you receive a suspicious email link?",
        options: [
            "Click it immediately",
            "Verify the sender and link before clicking",
            "Forward it to everyone",
            "Enter your password"
        ],
        answer: 1
    },

    {
        topic: "Passwords",
        question: "Which password is the strongest?",
        options: [
            "password123",
            "company2026",
            "Yash123",
            "A9!kP#72zL@4"
        ],
        answer: 3
    },

    {
        topic: "Phishing",
        question: "Which is a common sign of phishing?",
        options: [
            "Urgent request for sensitive information",
            "Normal company newsletter",
            "Expected meeting invitation",
            "Known internal message"
        ],
        answer: 0
    },

    {
        topic: "Malware",
        question: "What is malware?",
        options: [
            "A security policy",
            "Malicious software",
            "A backup system",
            "A password manager"
        ],
        answer: 1
    },

    {
        topic: "Passwords",
        question: "What is MFA?",
        options: [
            "Multiple File Access",
            "Multi-Factor Authentication",
            "Managed File Application",
            "Malware Firewall Access"
        ],
        answer: 1
    },

    {
        topic: "Backups",
        question: "Why are regular backups important?",
        options: [
            "They increase internet speed",
            "They help recover lost or encrypted data",
            "They remove all malware automatically",
            "They replace antivirus software"
        ],
        answer: 1
    },

    {
        topic: "Ransomware",
        question: "What does ransomware typically do?",
        options: [
            "Improves computer performance",
            "Encrypts or blocks access to data",
            "Creates backups",
            "Updates software"
        ],
        answer: 1
    },

    {
        topic: "Phishing",
        question: "What should you check before entering credentials on a website?",
        options: [
            "The URL and website domain",
            "The screen brightness",
            "The computer wallpaper",
            "The browser color"
        ],
        answer: 0
    },

    {
        topic: "Malware",
        question: "Which action helps reduce malware risk?",
        options: [
            "Download software from unknown sites",
            "Keep software updated",
            "Disable security tools",
            "Open every attachment"
        ],
        answer: 1
    },

    {
        topic: "Security",
        question: "Why should software be updated regularly?",
        options: [
            "To fix security vulnerabilities",
            "To remove the keyboard",
            "To reduce storage",
            "To disable protection"
        ],
        answer: 0
    },

    {
        topic: "BEC",
        question: "What does BEC stand for?",
        options: [
            "Business Email Compromise",
            "Business Encryption Control",
            "Basic Email Connection",
            "Backup Email Center"
        ],
        answer: 0
    },

    {
        topic: "Insider Threat",
        question: "What is an insider threat?",
        options: [
            "A threat originating from someone with authorized access",
            "Only an internet virus",
            "A hardware failure",
            "A software update"
        ],
        answer: 0
    },

    {
        topic: "Phishing",
        question: "Why do attackers often create a sense of urgency?",
        options: [
            "To encourage careful thinking",
            "To pressure users into making quick decisions",
            "To improve security",
            "To reduce email traffic"
        ],
        answer: 1
    },

    {
        topic: "Passwords",
        question: "Should you reuse the same password for important accounts?",
        options: [
            "Yes, always",
            "Only for banking",
            "No, use unique passwords",
            "Only on weekends"
        ],
        answer: 2
    },

    {
        topic: "Backups",
        question: "Which data should businesses regularly back up?",
        options: [
            "Only images",
            "Only emails",
            "Important business data",
            "Nothing"
        ],
        answer: 2
    },

    {
        topic: "Security",
        question: "What is the safest response to an unknown attachment?",
        options: [
            "Open it immediately",
            "Verify it before opening",
            "Send it to customers",
            "Rename it and open it"
        ],
        answer: 1
    },

    {
        topic: "Ransomware",
        question: "What can help a business recover after ransomware?",
        options: [
            "Reliable backups",
            "Weak passwords",
            "Unknown downloads",
            "Disabling security"
        ],
        answer: 0
    },

    {
        topic: "Security",
        question: "What is the purpose of cybersecurity awareness training?",
        options: [
            "Teach users to recognize and reduce cyber risks",
            "Make computers slower",
            "Remove all software",
            "Disable passwords"
        ],
        answer: 0
    },

    {
        topic: "Phishing",
        question: "What should you do with a suspicious email?",
        options: [
            "Report it using the organization's process",
            "Reply with your password",
            "Click every link",
            "Forward it externally"
        ],
        answer: 0
    },

    {
        topic: "Security",
        question: "Who is responsible for cybersecurity in an organization?",
        options: [
            "Only the IT department",
            "Only the manager",
            "Everyone in the organization",
            "Only new employees"
        ],
        answer: 2
    }

];


/* VARIABLES */

let currentQuestion = 0;

let score = 0;

let selectedAnswer = null;

let correctCount = 0;

let wrongCount = 0;

// Track the user's actual selections (question index -> selected option text)
let userSelections = {};


/* ELEMENTS */

const quizIntro =
    document.getElementById("quizIntro");

const quizBox =
    document.getElementById("quizBox");

const quizResult =
    document.getElementById("quizResult");

const questionNumber =
    document.getElementById("questionNumber");

const currentScore =
    document.getElementById("currentScore");

const questionTopic =
    document.getElementById("questionTopic");

const questionText =
    document.getElementById("questionText");

const optionsContainer =
    document.getElementById("optionsContainer");

const progressBar =
    document.getElementById("progressBar");

const feedback =
    document.getElementById("feedback");

const nextBtn =
    document.getElementById("nextBtn");


/* =====================================
   START QUIZ
===================================== */

function startQuiz() {

    currentQuestion = 0;

    score = 0;

    correctCount = 0;

    wrongCount = 0;

    userSelections = {};

    quizIntro.classList.add("hidden");

    quizResult.classList.add("hidden");

    quizBox.classList.remove("hidden");

    showQuestion();
}


/* =====================================
   SHOW QUESTION
===================================== */

function showQuestion() {

    selectedAnswer = null;

    nextBtn.disabled = true;

    feedback.classList.add("hidden");

    const q =
        questions[currentQuestion];


    questionNumber.textContent =
        `Question ${currentQuestion + 1} of ${questions.length}`;

    currentScore.textContent =
        `Score: ${score}`;


    questionTopic.textContent =
        q.topic;

    questionText.textContent =
        q.question;


    progressBar.style.width =
        `${((currentQuestion + 1) / questions.length) * 100}%`;


    optionsContainer.innerHTML = "";


    q.options.forEach((option, index) => {

        const button =
            document.createElement("div");

        button.className =
            "option";

        button.textContent =
            `${String.fromCharCode(65 + index)}. ${option}`;

        button.onclick =
            () => selectAnswer(index, button);

        optionsContainer.appendChild(button);

    });

}


/* =====================================
   SELECT ANSWER
===================================== */

function selectAnswer(index, selectedButton) {

    if (selectedAnswer !== null) {
        return;
    }

    selectedAnswer = index;

    const q =
        questions[currentQuestion];

    // IMPORTANT: Record the actual option text the user selected
    userSelections[String(currentQuestion + 1)] = q.options[index];

    const allOptions =
        document.querySelectorAll(".option");


    allOptions.forEach(option => {

        option.style.pointerEvents = "none";

    });


    if (index === q.answer) {

        selectedButton.classList.add("correct");

        feedback.textContent =
            "✓ Correct! Good cybersecurity awareness.";

        feedback.style.background =
            "#dcfce7";

        feedback.style.color =
            "#166534";

        score += 5;

        correctCount++;

    } else {

        selectedButton.classList.add("wrong");

        allOptions[q.answer]
            .classList.add("correct");

        feedback.textContent =
            "✗ Incorrect. The highlighted answer is correct.";

        feedback.style.background =
            "#fee2e2";

        feedback.style.color =
            "#991b1b";

        wrongCount++;

    }


    feedback.classList.remove("hidden");

    currentScore.textContent =
        `Score: ${score}`;

    nextBtn.disabled = false;

}


/* =====================================
   NEXT QUESTION
===================================== */

function nextQuestion() {

    currentQuestion++;


    if (currentQuestion >= questions.length) {

        showFinalResult();

    } else {

        showQuestion();

    }

}


/* =====================================
   FINAL RESULT
===================================== */

function showFinalResult() {

    quizBox.classList.add("hidden");

    quizResult.classList.remove("hidden");


    const percentage =
        Math.round(
            (correctCount / questions.length) * 100
        );


    document.getElementById("finalScore")
        .textContent = percentage + "%";


    document.getElementById("correctAnswers")
        .textContent = correctCount;


    document.getElementById("wrongAnswers")
        .textContent = wrongCount;


    const badgeTitle =
        document.getElementById("badgeTitle");

    const badgeMessage =
        document.getElementById("badgeMessage");


    if (percentage >= 80) {

        badgeTitle.textContent =
            "🏆 Cyber Security Champion";

        badgeMessage.textContent =
            "Excellent! You demonstrate strong cybersecurity awareness.";

    } else if (percentage >= 60) {

        badgeTitle.textContent =
            "🥇 Security Defender";

        badgeMessage.textContent =
            "Good work! Continue learning to strengthen your skills.";

    } else if (percentage >= 40) {

        badgeTitle.textContent =
            "🥈 Security Learner";

        badgeMessage.textContent =
            "You have a good start. Keep improving your cybersecurity knowledge.";

    } else {

        badgeTitle.textContent =
            "🥉 Beginner Defender";

        badgeMessage.textContent =
            "Keep practicing and complete more cybersecurity training.";

    }


    /* SAVE QUIZ RESULT */

    localStorage.setItem(
        "quizScore",
        percentage
    );

    // Sync quiz completion with backend: send the user's ACTUAL selections
    // userSelections is built in selectAnswer() as { "1": "Option text", "2": ... }
    if (window.API && typeof API.submitQuiz === "function") {
        API.submitQuiz(userSelections).catch(err => {
            console.warn("Backend quiz sync failed, local progress preserved:", err);
        });
    }

}


/* =====================================
   RESTART
===================================== */

function restartQuiz() {

    quizResult.classList.add("hidden");

    quizBox.classList.remove("hidden");

    startQuiz();

}