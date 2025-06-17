document.addEventListener("DOMContentLoaded", () => {
    const recordBtn = document.getElementById("recordBtn");
    const stopBtn = document.getElementById("stopBtn");
    const messageContainer = document.getElementById("messageContainer");
    const statusIcon = document.getElementById("statusIcon");
    const statusText = document.getElementById("statusText");

    let recognition;
    let finalTranscript = "";
    let voices = [];
    let preferredVoice = null;

    // Load and filter available voices
    function loadVoices() {
        voices = window.speechSynthesis.getVoices();
        preferredVoice = voices.find(v =>
            v.lang === 'en-US' &&
            (v.name.toLowerCase().includes("female") || v.name.toLowerCase().includes("samantha") || v.name.toLowerCase().includes("zira"))
        ) || voices.find(v => v.lang === 'en-US'); // fallback
    }

    if ('speechSynthesis' in window) {
        loadVoices();
        window.speechSynthesis.onvoiceschanged = loadVoices;
    }

    // Initialize Speech Recognition
    if ('webkitSpeechRecognition' in window) {
        recognition = new webkitSpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = false;
        recognition.lang = 'en-US';

        recognition.onstart = () => {
            finalTranscript = "";
            updateStatus("Listening...", "status-listening");
        };

        recognition.onresult = (event) => {
            for (let i = event.resultIndex; i < event.results.length; ++i) {
                if (event.results[i].isFinal) {
                    finalTranscript += event.results[i][0].transcript;
                }
            }
        };

        recognition.onerror = (event) => {
            console.error("Speech recognition error:", event.error);
            updateStatus("Error occurred", "status-error");
            recordBtn.disabled = false;
            stopBtn.style.display = "none";
        };

        recognition.onend = () => {
            updateStatus("Processing...", "status-processing");

            if (finalTranscript.trim() !== "") {
                appendMessage("user", finalTranscript);
                sendMessageToServer(finalTranscript);
            } else {
                updateStatus("No speech detected", "status-ready");
                toggleButtons(false);
            }
        };
    } else {
        alert("Your browser does not support Web Speech API.");
    }

    // Button Event Listeners
    recordBtn.addEventListener("click", () => {
        toggleButtons(true);
        recognition.start();
    });

    stopBtn.addEventListener("click", () => {
        recognition.stop();
    });

    // Update Status UI
    function updateStatus(text, iconClass) {
        statusText.textContent = text;
        statusIcon.className = "";
        statusIcon.classList.add(iconClass);
    }

    // Toggle Recording Buttons
    function toggleButtons(isRecording) {
        recordBtn.style.display = isRecording ? "none" : "inline-block";
        stopBtn.style.display = isRecording ? "inline-block" : "none";
        recordBtn.disabled = isRecording;
    }

    // Append Messages to UI
    function appendMessage(sender, text) {
        const msgDiv = document.createElement("div");
        msgDiv.className = `message ${sender}`;
        msgDiv.innerHTML = `<p>${text}</p>`;
        messageContainer.appendChild(msgDiv);
        messageContainer.scrollTop = messageContainer.scrollHeight;
    }

    // Speak AI response
    function speakText(text) {
        if (!window.speechSynthesis) return;

        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = 'en-US';
        utterance.rate = 1;
        if (preferredVoice) {
            utterance.voice = preferredVoice;
        }
        window.speechSynthesis.speak(utterance);
    }

    // Send to Backend
    function sendMessageToServer(message) {
        fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: message })
        })
        .then(response => response.json())
        .then(data => {
            if (data.response) {
                appendMessage("ai", data.response);
                speakText(data.response);
            } else {
                appendMessage("ai", `Error: ${data.error || 'Unknown error'}`);
            }
        })
        .catch(err => {
            console.error("Error talking to AI:", err);
            appendMessage("ai", "An error occurred while talking to Swarangi.");
        })
        .finally(() => {
            updateStatus("Ready to listen", "status-ready");
            toggleButtons(false);
        });
    }
});
