/* =====================================================
   HR SAARATHI AI
   FRONTEND APPLICATION
   ===================================================== */


// =====================================================
// GLOBAL VARIABLES
// =====================================================

let sessionId = null;

let mediaRecorder = null;

let audioChunks = [];

let recordingStartTime = null;

let recordingTimerInterval = null;

let isRecording = false;

let isProcessing = false;

let voiceResponseEnabled = true;


// =====================================================
// DOM ELEMENTS
// =====================================================

const micButton =
    document.getElementById("micButton");

const micIcon =
    document.getElementById("micIcon");

const clearButton =
    document.getElementById("clearButton");

const speakerButton =
    document.getElementById("speakerButton");

const speakerIcon =
    document.getElementById("speakerIcon");

const orb =
    document.getElementById("orb");

const statusText =
    document.getElementById("statusText");

const subStatus =
    document.getElementById("subStatus");

const recordingTimer =
    document.getElementById("recordingTimer");

const questionForm =
    document.getElementById("questionForm");

const questionInput =
    document.getElementById("questionInput");

const sendButton =
    document.getElementById("sendButton");

const conversation =
    document.getElementById("conversation");

const connection =
    document.querySelector(".connection");

const connectionText =
    document.getElementById("connectionText");


// =====================================================
// SESSION ID
// =====================================================

function createSession() {

    sessionId =
        localStorage.getItem(
            "hr_saarathi_session"
        );


    if (!sessionId) {

        sessionId =
            crypto.randomUUID();

        localStorage.setItem(
            "hr_saarathi_session",
            sessionId
        );

    }

}


// =====================================================
// INITIALIZATION
// =====================================================

document.addEventListener(
    "DOMContentLoaded",
    async function () {

        createSession();

        await checkBackend();

        setupEvents();

        updateReadyState();

    }
);


// =====================================================
// SETUP EVENTS
// =====================================================

function setupEvents() {


    // Microphone

    micButton.addEventListener(
        "click",
        toggleRecording
    );


    // Text form

    questionForm.addEventListener(
        "submit",
        function (event) {

            event.preventDefault();

            const question =
                questionInput.value.trim();

            if (!question) {

                return;

            }

            askTextQuestion(question);

        }
    );


    // Clear conversation

    clearButton.addEventListener(
        "click",
        clearConversation
    );


    // Speaker

    speakerButton.addEventListener(
        "click",
        toggleSpeaker
    );


    // Quick questions

    document
        .querySelectorAll(".quick-question")
        .forEach(button => {

            button.addEventListener(
                "click",
                function () {

                    const question =
                        this.dataset.question;

                    questionInput.value =
                        question;

                    askTextQuestion(
                        question
                    );

                }
            );

        });


    // Orb click

    orb.addEventListener(
        "click",
        function () {

            if (!isProcessing) {

                toggleRecording();

            }

        }
    );

}


// =====================================================
// CHECK BACKEND
// =====================================================

async function checkBackend() {

    try {

        const response =
            await fetch("/health");


        if (!response.ok) {

            throw new Error(
                "Backend unavailable"
            );

        }


        const data =
            await response.json();


        if (data.status === "ok") {

            connection.classList.add(
                "connected"
            );

            connectionText.textContent =
                "Connected";

        }

    }

    catch (error) {

        console.error(
            "Backend error:",
            error
        );

        connection.classList.add(
            "error"
        );

        connectionText.textContent =
            "Disconnected";

    }

}


// =====================================================
// READY STATE
// =====================================================

function updateReadyState() {

    statusText.textContent =
        "I'm ready to help...";

    subStatus.textContent =
        "Ask me about employee attendance";

}


// =====================================================
// RECORDING
// =====================================================

async function toggleRecording() {

    if (isProcessing) {

        return;

    }


    if (isRecording) {

        stopRecording();

    }

    else {

        await startRecording();

    }

}


// =====================================================
// START RECORDING
// =====================================================

async function startRecording() {

    try {

        if (
            !navigator.mediaDevices ||
            !navigator.mediaDevices.getUserMedia
        ) {

            alert(
                "Your browser does not support microphone access."
            );

            return;

        }


        const stream =
            await navigator.mediaDevices.getUserMedia({
                audio: true
            });


        audioChunks = [];


        let options = {};


        // Prefer WebM Opus

        if (
            MediaRecorder.isTypeSupported(
                "audio/webm;codecs=opus"
            )
        ) {

            options = {
                mimeType:
                    "audio/webm;codecs=opus"
            };

        }

        else if (
            MediaRecorder.isTypeSupported(
                "audio/webm"
            )
        ) {

            options = {
                mimeType:
                    "audio/webm"
            };

        }


        mediaRecorder =
            new MediaRecorder(
                stream,
                options
            );


        mediaRecorder.ondataavailable =
            function (event) {

                if (
                    event.data &&
                    event.data.size > 0
                ) {

                    audioChunks.push(
                        event.data
                    );

                }

            };


        mediaRecorder.onstop =
            async function () {

                stream
                    .getTracks()
                    .forEach(
                        track =>
                            track.stop()
                    );


                const mimeType =
                    mediaRecorder.mimeType ||
                    "audio/webm";


                const audioBlob =
                    new Blob(
                        audioChunks,
                        {
                            type: mimeType
                        }
                    );


                await sendVoiceQuestion(
                    audioBlob
                );

            };


        mediaRecorder.start(
            250
        );


        isRecording = true;

        recordingStartTime =
            Date.now();


        micButton.classList.add(
            "recording"
        );

        orb.classList.add(
            "listening"
        );

        recordingTimer.classList.add(
            "visible"
        );


        micIcon.textContent =
            "⏹";


        statusText.textContent =
            "I'm listening...";


        subStatus.textContent =
            "Speak your HR question";


        startRecordingTimer();

    }

    catch (error) {

        console.error(
            "Microphone error:",
            error
        );


        alert(
            "Microphone access was denied or unavailable."
        );

    }

}


// =====================================================
// STOP RECORDING
// =====================================================

function stopRecording() {

    if (
        !mediaRecorder ||
        mediaRecorder.state === "inactive"
    ) {

        return;

    }


    isRecording = false;


    micButton.classList.remove(
        "recording"
    );

    orb.classList.remove(
        "listening"
    );


    micIcon.textContent =
        "🎙";


    stopRecordingTimer();


    statusText.textContent =
        "Processing...";


    subStatus.textContent =
        "Understanding your question";


    mediaRecorder.stop();

}


// =====================================================
// RECORDING TIMER
// =====================================================

function startRecordingTimer() {

    recordingTimerInterval =
        setInterval(
            function () {

                if (!recordingStartTime) {

                    return;

                }


                const elapsed =
                    Math.floor(
                        (
                            Date.now() -
                            recordingStartTime
                        ) / 1000
                    );


                const minutes =
                    String(
                        Math.floor(
                            elapsed / 60
                        )
                    ).padStart(
                        2,
                        "0"
                    );


                const seconds =
                    String(
                        elapsed % 60
                    ).padStart(
                        2,
                        "0"
                    );


                recordingTimer.textContent =
                    `${minutes}:${seconds}`;

            },
            500
        );

}


function stopRecordingTimer() {

    clearInterval(
        recordingTimerInterval
    );

    recordingTimerInterval =
        null;

    recordingStartTime =
        null;

    recordingTimer.textContent =
        "00:00";

    recordingTimer.classList.remove(
        "visible"
    );

}


// =====================================================
// SEND VOICE QUESTION
// =====================================================

async function sendVoiceQuestion(
    audioBlob
) {

    isProcessing = true;

    setProcessingState();


    try {

        const formData =
            new FormData();


        // Determine extension

        let filename =
            "question.webm";


        if (
            audioBlob.type.includes(
                "ogg"
            )
        ) {

            filename =
                "question.ogg";

        }

        else if (
            audioBlob.type.includes(
                "wav"
            )
        ) {

            filename =
                "question.wav";

        }


        formData.append(
            "audio",
            audioBlob,
            filename
        );


        const url =
            "/ask-voice?session_id=" +
            encodeURIComponent(
                sessionId
            );


        const response =
            await fetch(
                url,
                {
                    method: "POST",
                    body: formData
                }
            );


        const data =
            await parseResponse(
                response
            );


        if (!response.ok) {

            throw new Error(
                data.detail ||
                data.error ||
                "Voice request failed."
            );

        }


        // Show transcription

        if (data.transcription) {

            addMessage(
                "user",
                data.transcription
            );

        }


        // Show answer

        if (data.answer) {

            addMessage(
                "assistant",
                data.answer
            );


            if (
                voiceResponseEnabled
            ) {

                speakAnswer(
                    data.answer,
                    data.transcription
                );

            }

        }


        statusText.textContent =
            "I'm ready for your next question.";

        subStatus.textContent =
            "Tap the microphone to speak";


    }

    catch (error) {

        console.error(
            "Voice request error:",
            error
        );


        addMessage(
            "assistant",
            "Sorry, I couldn't process your voice question. Please try again."
        );


        statusText.textContent =
            "Something went wrong";

        subStatus.textContent =
            "Please try again";

    }

    finally {

        isProcessing = false;

        updateMicReady();

    }

}


// =====================================================
// SEND TEXT QUESTION
// =====================================================

async function askTextQuestion(
    question
) {

    if (isProcessing) {

        return;

    }


    if (!question.trim()) {

        return;

    }


    isProcessing = true;

    setProcessingState();


    addMessage(
        "user",
        question
    );


    questionInput.value =
        "";


    try {

        const response =
            await fetch(
                "/ask",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({

                        question:
                            question,

                        session_id:
                            sessionId

                    })

                }
            );


        const data =
            await parseResponse(
                response
            );


        if (!response.ok) {

            throw new Error(
                data.detail ||
                data.error ||
                "Question failed."
            );

        }


        if (data.answer) {

            addMessage(
                "assistant",
                data.answer
            );


            if (
                voiceResponseEnabled
            ) {

                speakAnswer(
                    data.answer,
                    question
                );

            }

        }


        statusText.textContent =
            "I'm ready for your next question.";

        subStatus.textContent =
            "Ask another attendance question";


    }

    catch (error) {

        console.error(
            "Text request error:",
            error
        );


        addMessage(
            "assistant",
            "Sorry, I couldn't process that question."
        );


        statusText.textContent =
            "Something went wrong";

        subStatus.textContent =
            "Please try again";

    }

    finally {

        isProcessing = false;

        updateMicReady();

    }

}


// =====================================================
// RESPONSE PARSER
// =====================================================

async function parseResponse(
    response
) {

    const text =
        await response.text();


    try {

        return JSON.parse(
            text
        );

    }

    catch {

        console.error(
            "Invalid JSON:",
            text
        );


        throw new Error(
            "Server returned an invalid response."
        );

    }

}


// =====================================================
// ADD MESSAGE
// =====================================================

function addMessage(
    role,
    text
) {

    if (!text) {

        return;

    }


    const message =
        document.createElement(
            "div"
        );


    message.className =
        "message " + role;


    const bubble =
        document.createElement(
            "div"
        );


    bubble.className =
        "message-bubble";


    // Convert newlines

    bubble.innerHTML =
        escapeHtml(
            text
        ).replace(
            /\n/g,
            "<br>"
        );


    message.appendChild(
        bubble
    );


    conversation.appendChild(
        message
    );


    conversation.scrollTop =
        conversation.scrollHeight;

}


// =====================================================
// HTML ESCAPE
// =====================================================

function escapeHtml(
    text
) {

    const div =
        document.createElement(
            "div"
        );

    div.textContent =
        text;

    return div.innerHTML;

}


// =====================================================
// PROCESSING STATE
// =====================================================

function setProcessingState() {

    statusText.textContent =
        "Thinking...";


    subStatus.textContent =
        "Checking attendance data";


    sendButton.disabled =
        true;


    micButton.disabled =
        true;


    orb.classList.remove(
        "listening"
    );


    orb.classList.add(
        "listening"
    );


    micIcon.textContent =
        "⏳";

}


// =====================================================
// MIC READY
// =====================================================

function updateMicReady() {

    sendButton.disabled =
        false;


    micButton.disabled =
        false;


    micIcon.textContent =
        "🎙";


    orb.classList.remove(
        "listening"
    );

}


// =====================================================
// SPEAKER TOGGLE
// =====================================================

function toggleSpeaker() {

    voiceResponseEnabled =
        !voiceResponseEnabled;


    if (
        voiceResponseEnabled
    ) {

        speakerIcon.textContent =
            "🔊";

        speakerButton.title =
            "Voice response enabled";

    }

    else {

        speakerIcon.textContent =
            "🔇";

        speakerButton.title =
            "Voice response disabled";


        window.speechSynthesis.cancel();

    }

}


// =====================================================
// TEXT TO SPEECH
// =====================================================

function speakAnswer(
    answer,
    originalQuestion
) {

    if (
        !("speechSynthesis" in window)
    ) {

        return;

    }


    window.speechSynthesis.cancel();


    const utterance =
        new SpeechSynthesisUtterance(
            answer
        );


    // Detect Malayalam

    const hasMalayalam =
        /[\u0D00-\u0D7F]/.test(
            answer
        ) ||
        /[\u0D00-\u0D7F]/.test(
            originalQuestion || ""
        );


    if (hasMalayalam) {

        utterance.lang =
            "ml-IN";

    }

    else {

        utterance.lang =
            "en-IN";

    }


    utterance.rate =
        0.95;


    utterance.pitch =
        1.0;


    utterance.volume =
        1.0;


    utterance.onstart =
        function () {

            statusText.textContent =
                "Speaking...";

            subStatus.textContent =
                "HR Saarathi is responding";


            orb.classList.add(
                "listening"
            );

        };


    utterance.onend =
        function () {

            orb.classList.remove(
                "listening"
            );


            statusText.textContent =
                "I'm ready for your next question.";

            subStatus.textContent =
                "Tap the microphone to speak";

        };


    utterance.onerror =
        function (error) {

            console.error(
                "Speech error:",
                error
            );

            orb.classList.remove(
                "listening"
            );

        };


    window.speechSynthesis.speak(
        utterance
    );

}


// =====================================================
// CLEAR CONVERSATION
// =====================================================

async function clearConversation() {

    if (isProcessing) {

        return;

    }


    try {

        await fetch(
            "/conversation/" +
            encodeURIComponent(
                sessionId
            ),
            {
                method: "DELETE"
            }
        );

    }

    catch (error) {

        console.error(
            "Clear error:",
            error
        );

    }


    conversation.innerHTML =
        "";


    window.speechSynthesis.cancel();


    // Create new session

    sessionId =
        crypto.randomUUID();


    localStorage.setItem(
        "hr_saarathi_session",
        sessionId
    );


    updateReadyState();

}


// =====================================================
// KEYBOARD SHORTCUT
// =====================================================

document.addEventListener(
    "keydown",
    function (event) {

        // Space = microphone

        if (
            event.code === "Space" &&
            document.activeElement !==
            questionInput
        ) {

            event.preventDefault();

            if (!isProcessing) {

                toggleRecording();

            }

        }

    }
);