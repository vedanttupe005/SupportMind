async function sendMessage() {
    const input = document.getElementById("message");
    const message = input.value.trim();

    if (!message) return;

    const chat = document.getElementById("chat");
    const typing = document.getElementById("typing");

    // Show user message
    chat.innerHTML += `
        <div class="user">
            <div class="bubble">${message}</div>
        </div>
    `;

    input.value = "";
    chat.scrollTop = chat.scrollHeight;

    // Show typing
    typing.style.display = "block";

    try {
        const controller = new AbortController();
        const timeout = setTimeout(() => controller.abort(), 50000); // 20s timeout

        const response = await fetch("/api/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ message }),
            signal: controller.signal
        });

        clearTimeout(timeout);

        const data = await response.json();

        typing.style.display = "none";

        let reply = data.response || "⚠️ No response from server.";

        if (data.status === "error") {
            reply = "⚠️ " + reply;
        }

        if (typeof reply === "object") {
            reply = JSON.stringify(reply);
        }

        chat.innerHTML += `
            <div class="ai ${data.status === "error" ? "error" : ""}">
                <div class="bubble">${reply}</div>
            </div>
        `;

    } catch (error) {
        typing.style.display = "none";

        let errorMsg = "⚠️ Something went wrong.";

        if (error.name === "AbortError") {
            errorMsg = "⚠️ Request timed out. Please try again.";
        } else {
            errorMsg = "⚠️ Network error. Check your connection.";
        }

        chat.innerHTML += `
            <div class="ai error">
                <div class="bubble">${errorMsg}</div>
            </div>
        `;
    }

    chat.scrollTop = chat.scrollHeight;
}