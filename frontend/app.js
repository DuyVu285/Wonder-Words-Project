import { SocketService } from './socketService.js';
import { UIService } from './uiService.js';
import { NotificationService } from './notificationService.js';

document.addEventListener('DOMContentLoaded', () => {
    const socketService = new SocketService();

    socketService.on('message', (data) => {
        UIService.addListItem('messageList', data.text);
        NotificationService.showToast('New message received!');
    });

    document.getElementById('sendMessageBtn').addEventListener('click', () => {
        const messageInput = document.getElementById('messageInput');
        if (messageInput.value.trim()) {
            socketService.emit('message', { text: messageInput.value });
            messageInput.value = '';
        }
    });
});