// socketService.js
export class SocketService {
    constructor() {
        this.socket = io();
    }

    on(event, callback) {
        this.socket.on(event, callback);
    }

    emit(event, data) {
        this.socket.emit(event, data);
    }
}

// uiService.js
export class UIService {
    static updateElement(id, content) {
        const element = document.getElementById(id);
        if (element) {
            element.innerHTML = content;
        }
    }

    static addListItem(listId, content) {
        const list = document.getElementById(listId);
        if (list) {
            const listItem = document.createElement('li');
            listItem.textContent = content;
            list.appendChild(listItem);
        }
    }
}

// notificationService.js
export class NotificationService {
    static showToast(message) {
        alert(message); // Replace with a better toast notification if needed
    }
}

// app.js
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
