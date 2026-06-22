async function sendMessage() {
    const message = document.getElementById("message").value;

    try {
        const response = await fetch("/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                message: message
            })
        });

        const data = await response.json();

        document.getElementById("response").innerText = data.reply;

        // Speak the reply
        const speech = new SpeechSynthesisUtterance(data.reply);
        speech.lang = "en-US";
        speech.volume = 1;
        speech.rate = 1;
        speech.pitch = 1;

        window.speechSynthesis.speak(speech);

    } catch (error) {
        document.getElementById("response").innerText =
            "Error: " + error.message;
    }
}

function startVoice() {
    if (!('webkitSpeechRecognition' in window)) {
        alert("Speech Recognition is not supported in this browser.");
        return;
    }

    const recognition = new webkitSpeechRecognition();

    recognition.lang = "en-US";
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onresult = function(event) {
        document.getElementById("message").value =
            event.results[0][0].transcript;
    };

    recognition.onerror = function(event) {
        alert("Speech Recognition Error: " + event.error);
    };

    recognition.start();
}
async function loadAnalytics() {
    const response = await fetch("/analytics");
    const data = await response.json();

    document.getElementById("response").innerText =
        JSON.stringify(data, null, 2);
}

async function loadCalls() {
    const response = await fetch("/calls");
    const data = await response.json();

    document.getElementById("response").innerText =
        JSON.stringify(data, null, 2);
}

async function loadCallResults() {
    const response = await fetch("/call-results");
    const data = await response.json();

    document.getElementById("response").innerText =
        JSON.stringify(data, null, 2);
}