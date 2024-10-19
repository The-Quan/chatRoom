const usernameInput = document.getElementById('username');
const messageInput = document.getElementById('message');
const sendButton = document.getElementById('send-btn');
const chatBox = document.getElementById('chat-box');

// Kết nối tới WebSocket server
const socket = new WebSocket('ws://localhost:6789');

// Khi nhận tin nhắn từ server
socket.onmessage = function(event) {
    const data = JSON.parse(event.data);
    const messageElement = document.createElement('div');
    messageElement.textContent = `${data.username}: ${data.message}`;
    chatBox.appendChild(messageElement);
    chatBox.scrollTop = chatBox.scrollHeight;  // Tự động cuộn xuống dưới
};

// Khi nhấn nút gửi
sendButton.addEventListener('click', function() {
    const username = usernameInput.value.trim();
    const message = messageInput.value.trim();
    
    if (username && message) {
        const data = {
            username: username,
            message: message
        };
        socket.send(JSON.stringify(data));
        messageInput.value = '';  // Xóa khung nhập tin nhắn sau khi gửi
    }
});
