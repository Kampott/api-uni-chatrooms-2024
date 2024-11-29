const socket = new WebSocket("ws://127.0.0.1:8000/ws/chat");

const chatMessages = document.getElementById("chatMessages");
const messageInput = document.getElementById("messageInput");
const sendButton = document.getElementById("sendButton");
const usernameInput = document.getElementById("usernameInput");

socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    const newMessage = document.createElement("div");
    const timestamp = new Date(data.timestamp).toLocaleTimeString();
    newMessage.innerHTML = `<strong>${data.username}:</strong> ${data.message} <em style="font-size: 0.8em; color: gray;">(${timestamp})</em>`;
    chatMessages.appendChild(newMessage);
};

sendButton.addEventListener("click", () => {
    const message = messageInput.value;
    const username = usernameInput.value || "Аноним";
    if (message.trim()) {
        socket.send(JSON.stringify({ username, message }));
        messageInput.value = "";
    }
});

window.addEventListener("load", () => {
    fetch("http://127.0.0.1:8000/api/chat/history")
        .then((response) => response.json())
        .then((messages) => {
            messages.forEach((data) => {
                const newMessage = document.createElement("div");
                const timestamp = new Date(data.timestamp).toLocaleTimeString();
                newMessage.innerHTML = `<strong>${data.username}:</strong> ${data.message} <em style="font-size: 0.8em; color: gray;">(${timestamp})</em>`;
                chatMessages.appendChild(newMessage);
            });
        })
        .catch((error) => console.error("Ошибка загрузки истории:", error));
});
