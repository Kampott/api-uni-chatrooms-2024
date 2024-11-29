const usernameInput = document.getElementById("usernameInput");
const nicknameButton = document.getElementById("nicknameButton");
const auditoriumButtons = document.querySelectorAll(".auditorium-button");
const chatContainer = document.getElementById("chatContainer");
const nicknameForm = document.getElementsByClassName("nickname-form");

let username = "Аноним";
let currentRoom = null;
let currentChatWindow = null;
let socket = null;
let chatWindows = {};

// Устанавливаем никнейм
nicknameButton.addEventListener("click", () => {
    username = usernameInput.value.trim() || "Аноним";
    // Скрываем форму ввода никнейма и кнопки выбора аудитории
    nicknameForm.style.display = "none";
    auditoriumButtonsContainer.style.display = "none";
    
    // Показываем кнопки для выбора аудитории
    chatContainer.style.display = "block";
});

function createChatWindow(room) {
    const chatWindow = document.createElement("div");
    chatWindow.className = "chat-window";
    chatWindow.dataset.room = room;

    // Заголовок чата
    const chatHeader = document.createElement("div");
    chatHeader.className = "chat-header";
    chatHeader.textContent = `Чат комнаты: ${room}`;
    chatWindow.appendChild(chatHeader);


    // Сообщения
    const chatMessages = document.createElement("div");
    chatMessages.className = "chat-messages";
    chatMessages.id = `chat-messages-${room}`;
    chatWindow.appendChild(chatMessages);

        // Контейнер для ввода
        const messageInputContainer = document.createElement("div");
        messageInputContainer.className = "message-input-container";

    const chatInput = document.createElement("input");
    chatInput.className = "message-input";
    chatInput.placeholder = "Введите сообщение...";
    messageInputContainer.appendChild(chatInput);

    // Кнопка для эмодзи
    const emojiButton = document.createElement("button");   
    emojiButton.className = "emoji-button";
    emojiButton.textContent = "😊";
    messageInputContainer.appendChild(emojiButton);

    // Контейнер для эмодзи
    const emojiPicker = document.createElement("div");
    emojiPicker.className = "emoji-picker";
    emojiPicker.style.display = "none"; // Скрыт по умолчанию
    emojiButton.addEventListener("click", () => {
        emojiPicker.style.display = emojiPicker.style.display === "none" ? "block" : "none";
    });

    const emojis = ["😀", "😁", "😂", "😃", "😄", "😅", "😆", "😉", "😊", "😎"]; // Массив эмодзи
    emojis.forEach((emoji) => {
        const emojiSpan = document.createElement("span");
        emojiSpan.className = "emoji";
        emojiSpan.textContent = emoji;
        emojiSpan.addEventListener("click", () => {
            chatInput.value += emoji; // Добавляем эмодзи в поле ввода
            emojiPicker.style.display = "none"; // Скрываем список эмодзи после выбора
        });
        emojiPicker.appendChild(emojiSpan);
    });

    messageInputContainer.appendChild(emojiPicker);

    const sendButton = document.createElement("button");
    sendButton.textContent = "➤";
    sendButton.className = "send-button";
    sendButton.id = "sendButton";
    sendButton.addEventListener("click", () => {
        const message = chatInput.value.trim();
        if (message) {
            sendMessage(room, chatInput); // Отправляем сообщение
        }
    });
    messageInputContainer.appendChild(sendButton);
    chatWindow.appendChild(messageInputContainer);
    document.getElementById("chatContainer").appendChild(chatWindow);
    chatWindows[room] = chatWindow;
    return chatWindow;
}

// Отправляет сообщение на сервер
function sendMessage(room, messageInput) {
    const message = messageInput.value.trim();
    if (message && socket && socket.readyState === WebSocket.OPEN) {
        const payload = {
            action: "message",
            room: room,
            username: username,
            message: message,
        };

        socket.send(JSON.stringify(payload)); // Отправляем сообщение на сервер
        messageInput.value = ""; // Очищаем поле ввода
    }
}

// Добавление обработчика на кнопку отправки
const sendButton = document.querySelector("#send-button");
if (sendButton) {
    sendButton.addEventListener("click", sendMessage);
}

// Также добавляем отправку по Enter
const messageInput = document.querySelector("#message-input");
if (messageInput) {
    messageInput.addEventListener("keypress", (event) => {
        if (event.key === "Enter") {
            sendMessage(currentRoom, messageInput); // Передаем правильное поле ввода
        }
    });
};

// Добавляет сообщение в окно чата
function appendMessage(room, data) {
    const chatMessages = document.querySelector(`#chat-messages-${room}`);
    if (chatMessages) {
        const messageElement = document.createElement("div");
        messageElement.classList.add("chat-message");

        const senderUsername = data.username || "Аноним";
        const isMessageFromMe = senderUsername === username;

        if (senderUsername === "Аноним" || !isMessageFromMe) {
            messageElement.classList.add("other");
        } else {
            messageElement.classList.add("me");
        }

        const usernameElement = document.createElement("div");
        usernameElement.classList.add("username");
        usernameElement.textContent = senderUsername;
        messageElement.appendChild(usernameElement);

        const messageText = document.createElement("div");
        messageText.textContent = data.message;
        messageElement.appendChild(messageText);

        const timestamp = new Date(data.timestamp).toLocaleTimeString();
        const timestampElement = document.createElement("div");
        timestampElement.classList.add("timestamp");
        timestampElement.textContent = timestamp;
        messageElement.appendChild(timestampElement);

        chatMessages.appendChild(messageElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
}

// Подключение WebSocket
function connectWebSocket() {
    socket = new WebSocket("ws://127.0.0.1:8000/ws/chat");

    socket.onopen = () => {
        console.log("WebSocket соединение установлено.");
        if (currentRoom) {
            socket.send(JSON.stringify({ action: "join", room: currentRoom }));
        }
    };

    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log("Новое сообщение получено:", data);
        const room = data.room;

        appendMessage(room, data);
    };

    socket.onclose = () => {
        console.error("WebSocket закрыт. Переподключение...");
        setTimeout(connectWebSocket, 1000);
    };

    socket.onerror = (error) => {
        console.error("WebSocket ошибка:", error);
    };
}

// Переключение между чат-комнатами
auditoriumButtons.forEach((button) => {
    button.addEventListener("click", (e) => {
        const room = e.target.dataset.room;
        
        if (currentChatWindow) {
            chatContainer.removeChild(currentChatWindow);
        }

        currentRoom = room;
        document.getElementById("chatContainer").style.display = "flex";

        if (!chatWindows[room]) {
            currentChatWindow = createChatWindow(room);
            chatContainer.appendChild(currentChatWindow);

            fetch(`http://127.0.0.1:8000/api/chat/history/${room}`)
                .then((response) => response.json())
                .then((messages) => {
                    const chatMessages = document.querySelector(`#chat-messages-${room}`);
                    chatMessages.innerHTML = "";

                    messages.forEach((data) => {
                        appendMessage(room, data);
                    });
                });
        } else {
            currentChatWindow = chatWindows[room];
            chatContainer.appendChild(currentChatWindow);
        }

        if (socket && socket.readyState === WebSocket.OPEN) {
            socket.send(
                JSON.stringify({
                    action: "join",
                    room: currentRoom,
                })
            );
        }
    });
});

// Ожидание загрузки DOM
document.addEventListener('DOMContentLoaded', function () {
});

// Запуск WebSocket
connectWebSocket();
