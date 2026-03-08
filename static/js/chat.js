async function sendMessage(){

    const input = document.getElementById("message");
    const message = input.value.trim();

    if(!message) return;

    const chat = document.getElementById("chat");
    const typing = document.getElementById("typing");

    // show user message
    chat.innerHTML += `
        <div class="user">
            <div class="bubble">${message}</div>
        </div>
    `;

    input.value = "";

    chat.scrollTop = chat.scrollHeight;

    // show typing indicator
    typing.style.display = "block";

    const response = await fetch("/api/chat",{
        method:"POST",
        headers:{
            "Content-Type":"application/json"
        },
        body: JSON.stringify({ message: message })
    });

    const data = await response.json();

    typing.style.display = "none";

    let reply = data.response;

    if(typeof reply === "object"){
        reply = JSON.stringify(reply);
    }

    // show AI message
    chat.innerHTML += `
        <div class="ai">
            <div class="bubble">${reply}</div>
        </div>
    `;

    chat.scrollTop = chat.scrollHeight;

}