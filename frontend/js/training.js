/* =====================================================
   TRAINING & QUIZ
===================================================== */


const quizData = {

    phishing: {

        title: "Phishing Awareness",

        icon: "🎣",

        questions: [

            {
                q: "What is the main goal of a phishing attack?",

                options: [
                    "Improve internet speed",
                    "Steal sensitive information",
                    "Update software",
                    "Create backups"
                ],

                answer: 1,

                explanation:
                    "Phishing attempts to trick users into revealing sensitive information such as passwords or financial details."
            },

            {
                q: "Which is a common sign of a phishing email?",

                options: [
                    "Unexpected urgency",
                    "Normal company newsletter",
                    "Known colleague greeting",
                    "Regular meeting reminder"
                ],

                answer: 0,

                explanation:
                    "Phishing messages often create urgency or pressure the recipient to act quickly."
            },

            {
                q: "What should you do before clicking a suspicious link?",

                options: [
                    "Click immediately",
                    "Forward it to everyone",
                    "Verify the link and sender",
                    "Disable antivirus"
                ],

                answer: 2,

                explanation:
                    "Always verify the sender and destination before opening suspicious links."
            },

            {
                q: "Which URL should receive more attention?",

                options: [
                    "A familiar official domain",
                    "A suspicious IP-based URL",
                    "A bookmarked website",
                    "A known internal website"
                ],

                answer: 1,

                explanation:
                    "IP-based URLs can be a warning sign and should be carefully verified."
            },

            {
                q: "What is the safest response to a suspicious email?",

                options: [
                    "Reply with your password",
                    "Click the link",
                    "Verify through an official channel",
                    "Download the attachment"
                ],

                answer: 2,

                explanation:
                    "Use an official communication channel to verify unexpected requests."
            }

        ]

    },


    ransomware: {

        title: "Ransomware",

        icon: "🔒",

        questions: [

            {
                q: "What does ransomware typically do?",

                options: [
                    "Encrypts or blocks access to data",
                    "Improves performance",
                    "Creates user accounts",
                    "Updates browsers"
                ],

                answer: 0,

                explanation:
                    "Ransomware can encrypt files and demand payment for recovery."
            },

            {
                q: "Which practice helps reduce ransomware impact?",

                options: [
                    "Regular secure backups",
                    "Sharing passwords",
                    "Ignoring updates",
                    "Disabling security tools"
                ],

                answer: 0,

                explanation:
                    "Regular and properly protected backups can help organizations recover from ransomware incidents."
            },

            {
                q: "Why should backups be protected?",

                options: [
                    "To prevent attackers from deleting them",
                    "To make files public",
                    "To reduce storage",
                    "To remove security"
                ],

                answer: 0,

                explanation:
                    "Attackers may target backups, so they should have appropriate access controls and protection."
            },

            {
                q: "What is a useful security practice?",

                options: [
                    "Keep software updated",
                    "Use the same password everywhere",
                    "Open unknown attachments",
                    "Ignore security alerts"
                ],

                answer: 0,

                explanation:
                    "Keeping software updated helps reduce exposure to known vulnerabilities."
            },

            {
                q: "What should employees do with suspicious attachments?",

                options: [
                    "Open them",
                    "Share them",
                    "Verify before opening",
                    "Disable antivirus"
                ],

                answer: 2,

                explanation:
                    "Unexpected attachments should be verified before opening."
            }

        ]

    },


    malware: {

        title: "Malware Protection",

        icon: "🦠",

        questions: [

            {
                q: "What is malware?",

                options: [
                    "Malicious software",
                    "Backup software",
                    "Design software",
                    "Office software"
                ],

                answer: 0,

                explanation:
                    "Malware is software designed to perform malicious or harmful actions."
            },

            {
                q: "Which helps protect against malware?",

                options: [
                    "Updated security software",
                    "Unknown downloads",
                    "Weak passwords",
                    "Ignoring updates"
                ],

                answer: 0,

                explanation:
                    "Updated security software can help detect and block known threats."
            },

            {
                q: "Why are software updates important?",

                options: [
                    "They can fix security vulnerabilities",
                    "They remove all files",
                    "They disable security",
                    "They expose passwords"
                ],

                answer: 0,

                explanation:
                    "Security updates often address known vulnerabilities."
            },

            {
                q: "What should you do with unknown software?",

                options: [
                    "Install immediately",
                    "Verify its source",
                    "Share it",
                    "Disable security tools"
                ],

                answer: 1,

                explanation:
                    "Always verify software sources before installation."
            },

            {
                q: "Which is a good security habit?",

                options: [
                    "Download from trusted sources",
                    "Use random websites",
                    "Ignore warnings",
                    "Share login credentials"
                ],

                answer: 0,

                explanation:
                    "Trusted sources reduce the risk of downloading malicious software."
            }

        ]

    },


    bec: {

        title: "Business Email Compromise",

        icon: "💼",

        questions: [

            {
                q: "What is BEC?",

                options: [
                    "Business Email Compromise",
                    "Backup Encryption Control",
                    "Browser Error Check",
                    "Business Equipment Control"
                ],

                answer: 0,

                explanation:
                    "BEC stands for Business Email Compromise."
            },

            {
                q: "What can BEC attacks target?",

                options: [
                    "Financial transactions",
                    "Screen brightness",
                    "Printer settings",
                    "Keyboard layout"
                ],

                answer: 0,

                explanation:
                    "BEC attacks may attempt to manipulate financial transactions or sensitive business processes."
            },

            {
                q: "How should unusual payment requests be handled?",

                options: [
                    "Pay immediately",
                    "Verify through another channel",
                    "Forward to everyone",
                    "Ignore security procedures"
                ],

                answer: 1,

                explanation:
                    "Unexpected payment requests should be independently verified."
            },

            {
                q: "What is a warning sign of BEC?",

                options: [
                    "Unexpected request from an executive",
                    "Normal meeting invitation",
                    "Routine newsletter",
                    "Known company announcement"
                ],

                answer: 0,

                explanation:
                    "Unexpected requests that appear to come from executives should be carefully verified."
            },

            {
                q: "What is a good defense against BEC?",

                options: [
                    "Verification procedures",
                    "Password sharing",
                    "Ignoring unusual requests",
                    "Removing MFA"
                ],

                answer: 0,

                explanation:
                    "Clear verification procedures can help prevent fraudulent business requests."
            }

        ]

    },


    insider: {

        title: "Insider Threats",

        icon: "👤",

        questions: [

            {
                q: "What is an insider threat?",

                options: [
                    "Risk originating from someone with authorized access",
                    "A weather event",
                    "A hardware upgrade",
                    "A software update"
                ],

                answer: 0,

                explanation:
                    "Insider threats involve risks from people who have legitimate access to organizational resources."
            },

            {
                q: "Which principle limits unnecessary access?",

                options: [
                    "Least privilege",
                    "Open access",
                    "Password sharing",
                    "Public access"
                ],

                answer: 0,

                explanation:
                    "Least privilege provides users only the access needed for their responsibilities."
            },

            {
                q: "Why should access be reviewed?",

                options: [
                    "To remove unnecessary permissions",
                    "To increase risk",
                    "To share passwords",
                    "To disable backups"
                ],

                answer: 0,

                explanation:
                    "Regular access reviews can identify and remove unnecessary permissions."
            },

            {
                q: "What should happen when an employee leaves?",

                options: [
                    "Access should be reviewed and removed",
                    "Keep all access forever",
                    "Share their password",
                    "Publish their account"
                ],

                answer: 0,

                explanation:
                    "Former employees should no longer retain unnecessary access to organizational systems."
            },

            {
                q: "Which is a good access-control practice?",

                options: [
                    "Role-based access",
                    "Everyone gets administrator access",
                    "Shared accounts",
                    "Public passwords"
                ],

                answer: 0,

                explanation:
                    "Role-based access helps ensure permissions match job responsibilities."
            }

        ]

    },


    backup: {

        title: "Backup & Recovery",

        icon: "💾",

        questions: [

            {
                q: "Why are backups important?",

                options: [
                    "They help recover important data",
                    "They increase phishing",
                    "They remove security",
                    "They share passwords"
                ],

                answer: 0,

                explanation:
                    "Backups help organizations recover data after incidents or failures."
            },

            {
                q: "How often should important data be backed up?",

                options: [
                    "According to business requirements",
                    "Never",
                    "Only after an attack",
                    "Once every ten years"
                ],

                answer: 0,

                explanation:
                    "Backup frequency should match the organization's data and recovery requirements."
            },

            {
                q: "What should organizations do with backups?",

                options: [
                    "Protect them from unauthorized access",
                    "Make them public",
                    "Share passwords",
                    "Delete them"
                ],

                answer: 0,

                explanation:
                    "Backups contain valuable information and should be properly protected."
            },

            {
                q: "Why should backup recovery be tested?",

                options: [
                    "To verify data can actually be restored",
                    "To delete data",
                    "To disable security",
                    "To expose files"
                ],

                answer: 0,

                explanation:
                    "Testing helps verify that backups are usable when recovery is needed."
            },

            {
                q: "Which is a useful recovery practice?",

                options: [
                    "Maintain tested backups",
                    "Keep only one copy",
                    "Never test backups",
                    "Store passwords publicly"
                ],

                answer: 0,

                explanation:
                    "Maintaining and testing backups improves recovery readiness."
            }

        ]

    }

};


/* =====================================================
   VARIABLES
===================================================== */

let currentQuiz = null;

let currentQuestionIndex = 0;

let selectedAnswer = null;

let score = 0;


/* =====================================================
   START QUIZ
===================================================== */

function startQuiz(category) {

    currentQuiz =
        quizData[category];

    currentQuestionIndex = 0;

    selectedAnswer = null;

    score = 0;


    document.getElementById("quizModal")
        .classList.remove("hidden");


    document.getElementById("quizCategory")
        .textContent =
        currentQuiz.title.toUpperCase();


    document.getElementById("quizTitle")
        .textContent =
        currentQuiz.title;


    loadQuestion();

}


/* =====================================================
   LOAD QUESTION
===================================================== */

function loadQuestion() {

    const question =
        currentQuiz.questions[
            currentQuestionIndex
        ];


    selectedAnswer = null;


    document.getElementById("quizQuestion")
        .textContent =
        question.q;


    document.getElementById("questionIcon")
        .textContent =
        currentQuiz.icon;


    document.getElementById("quizNumber")
        .textContent =
        currentQuestionIndex + 1;


    const percent =
        ((currentQuestionIndex + 1) /
        currentQuiz.questions.length) * 100;


    document.getElementById("quizPercent")
        .textContent =
        `${Math.round(percent)}%`;


    document.getElementById("quizProgressFill")
        .style.width =
        `${percent}%`;


    const optionsContainer =
        document.getElementById("quizOptions");


    optionsContainer.innerHTML = "";


    question.options.forEach(
        (option, index) => {

            const element =
                document.createElement("div");


            element.className =
                "quiz-option";


            element.innerHTML = `

                <span class="option-letter">
                    ${String.fromCharCode(65 + index)}
                </span>

                <span>
                    ${option}
                </span>

            `;


            element.addEventListener(
                "click",
                () => selectAnswer(
                    element,
                    index
                )
            );


            optionsContainer.appendChild(
                element
            );

        }
    );


    const feedback =
        document.getElementById(
            "quizFeedback"
        );


    feedback.classList.add("hidden");


    const nextButton =
        document.getElementById(
            "nextQuizBtn"
        );


    nextButton.disabled = true;

    nextButton.textContent =
        "Select an Answer";

}


/* =====================================================
   SELECT ANSWER
===================================================== */

function selectAnswer(
    element,
    index
) {

    if (selectedAnswer !== null) {
        return;
    }


    selectedAnswer = index;


    document
        .querySelectorAll(".quiz-option")
        .forEach(option => {

            option.classList.remove(
                "selected"
            );

        });


    element.classList.add(
        "selected"
    );


    const question =
        currentQuiz.questions[
            currentQuestionIndex
        ];


    const feedback =
        document.getElementById(
            "quizFeedback"
        );


    feedback.classList.remove(
        "hidden"
    );


    if (index === question.answer) {

        score++;


        feedback.className =
            "quiz-feedback correct";


        feedback.innerHTML = `

            <strong>✅ Correct!</strong><br>

            ${question.explanation}

        `;

    }

    else {

        feedback.className =
            "quiz-feedback wrong";


        feedback.innerHTML = `

            <strong>❌ Not quite.</strong><br>

            ${question.explanation}

        `;

    }


    document
        .querySelectorAll(".quiz-option")
        .forEach(
            (option, optionIndex) => {

                if (
                    optionIndex ===
                    question.answer
                ) {

                    option.classList.add(
                        "selected"
                    );

                }

            }
        );


    const nextButton =
        document.getElementById(
            "nextQuizBtn"
        );


    nextButton.disabled = false;


    if (
        currentQuestionIndex ===
        currentQuiz.questions.length - 1
    ) {

        nextButton.textContent =
            "Finish Quiz 🏆";

    }

    else {

        nextButton.textContent =
            "Next Question →";

    }

}


/* =====================================================
   NEXT QUESTION
===================================================== */

function nextQuestion() {

    if (selectedAnswer === null) {
        return;
    }


    if (
        currentQuestionIndex <
        currentQuiz.questions.length - 1
    ) {

        currentQuestionIndex++;

        loadQuestion();

    }

    else {

        finishQuiz();

    }

}


/* =====================================================
   FINISH
===================================================== */

function finishQuiz() {

    const total =
        currentQuiz.questions.length;


    const percentage =
        Math.round(
            (score / total) * 100
        );


    /* SAVE QUIZ RESULT */

    localStorage.setItem(
        "lastQuizScore",
        percentage
    );


    localStorage.setItem(
        "quizCompleted",
        "true"
    );


    /* BADGE */

    let badge;


    if (percentage >= 80) {

        badge =
            "🏆 Cyber Security Champion";

    }

    else if (percentage >= 60) {

        badge =
            "🥇 Security Defender";

    }

    else {

        badge =
            "🎖️ Security Starter";

    }


    document.getElementById(
        "finalScore"
    ).textContent =
        `${percentage}%`;


    document.getElementById(
        "earnedBadge"
    ).textContent =
        badge;


    document.getElementById(
        "completionModal"
    ).classList.remove(
        "hidden"
    );


    document.getElementById(
        "quizModal"
    ).classList.add(
        "hidden"
    );


    updateStats();

}


/* =====================================================
   CLOSE QUIZ
===================================================== */

function closeQuiz() {

    document.getElementById(
        "quizModal"
    ).classList.add(
        "hidden"
    );

}


/* =====================================================
   CLOSE COMPLETION
===================================================== */

function closeCompletion() {

    document.getElementById(
        "completionModal"
    ).classList.add(
        "hidden"
    );

}


/* =====================================================
   UPDATE STATS
===================================================== */

function updateStats() {

    const completed =
        localStorage.getItem(
            "quizCompleted"
        );


    if (completed === "true") {

        document.getElementById(
            "badgeCount"
        ).textContent = "1";

    }

}


/* =====================================================
   INITIAL LOAD
===================================================== */

updateStats();
