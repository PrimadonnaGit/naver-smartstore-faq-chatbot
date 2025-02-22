class ChatUI {
    constructor() {
        this.chatApiUrl = '/api/v1/chat/';
        this.welcomeApiUrl = '/api/v1/chat/welcome';
        this.chatContainer = document.getElementById('chat-container');
        this.messageInput = document.getElementById('message-input');
        this.sendButton = document.getElementById('send-button');

        this.sessionId = null;
        this.isLoading = false;

        this.setupEventListeners();
        this.loadWelcomeMessage();
    }

    setupEventListeners() {
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendMessage();
            }
        });
        this.sendButton.onclick = () => this.sendMessage();

    }

    createMessageElement(message, isUser = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `flex gap-2 message-fade-in ${isUser ? 'flex-row-reverse' : 'flex-row'}`;

        const avatarDiv = document.createElement('div');
        avatarDiv.className = `user-avatar ${isUser ? 'human' : 'bot-avatar'}`;
        const avatarIcon = document.createElement('i');
        avatarIcon.className = isUser ? 'fas fa-user' : 'fas fa-robot';
        avatarDiv.appendChild(avatarIcon);

        const messageContent = document.createElement('div');
        messageContent.className = `max-w-[80%] rounded-2xl px-4 py-2 ${
            isUser 
                ? 'bg-primary-500 text-white rounded-br-none' 
                : 'bg-gray-100 text-gray-900 rounded-bl-none'
        }`;

        const messageText = document.createElement('p');
        messageText.className = 'whitespace-pre-wrap text-sm';
        messageText.textContent = message;

        messageContent.appendChild(messageText);
        messageDiv.appendChild(avatarDiv);
        messageDiv.appendChild(messageContent);
        return messageDiv;
    }

    createFollowUpElement(question) {
        const followUpDiv = document.createElement('div');
        followUpDiv.className = 'flex justify-start mt-2 ml-12';

        const content = document.createElement('div');
        content.className = 'bg-primary-50 text-primary-600 rounded-lg px-4 py-2 text-sm cursor-pointer hover:bg-primary-100 transition-colors duration-200';
        content.innerHTML = `
            <i class="fas fa-question-circle mr-2"></i>
            <span>${question}</span>
        `;

        content.onclick = () => {
            this.messageInput.value = question;
            this.sendMessage();
        };

        followUpDiv.appendChild(content);
        return followUpDiv;
    }

    createLoadingElement() {
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'flex gap-2 message-fade-in';

        const avatarDiv = document.createElement('div');
        avatarDiv.className = 'user-avatar bot-avatar';
        const avatarIcon = document.createElement('i');
        avatarIcon.className = 'fas fa-robot';
        avatarDiv.appendChild(avatarIcon);

        const loadingContent = document.createElement('div');
        loadingContent.className = 'bg-gray-100 text-gray-900 rounded-2xl rounded-bl-none px-4 py-2';

        const dots = document.createElement('div');
        dots.className = 'typing-indicator';

        for (let i = 0; i < 3; i++) {
            const dot = document.createElement('span');
            dot.className = 'typing-dot';
            dots.appendChild(dot);
        }

        loadingContent.appendChild(dots);
        loadingDiv.appendChild(avatarDiv);
        loadingDiv.appendChild(loadingContent);
        return loadingDiv;
    }

    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message || this.isLoading) return;

        this.isLoading = true;
        this.sendButton.disabled = true;
        this.messageInput.disabled = true;

        this.appendMessage(message, true);
        this.messageInput.value = '';

        const loadingElement = this.createLoadingElement();
        this.chatContainer.appendChild(loadingElement);
        this.scrollToBottom();

        try {
            const response = await fetch(this.chatApiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Session-ID': this.sessionId
                },
                body: JSON.stringify({ message })
            });

            let currentBotMessage = null;
            let currentMessageText = null;
            let firstResponseReceived = false;

            const reader = response.body.getReader();
            const decoder = new TextDecoder();

            while (true) {
                const { value, done } = await reader.read();
                if (done) break;

                const text = decoder.decode(value);
                const lines = text.split('\n');

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        const data = JSON.parse(line.slice(6));

                        if (!firstResponseReceived && data.type !== 'follow_up') {
                            firstResponseReceived = true;
                            loadingElement.remove();
                        }

                        if (!currentBotMessage && data.type !== 'follow_up') {
                            currentBotMessage = this.createMessageElement('', false);
                            currentMessageText = currentBotMessage.querySelector('p');
                            this.chatContainer.appendChild(currentBotMessage);
                        }

                        if (data.type === 'follow_up') {
                            const followUpElement = this.createFollowUpElement(data.content);
                            this.chatContainer.appendChild(followUpElement);
                            this.scrollToBottom();
                        } else if (data.type === 'done') {
                            currentBotMessage = null;
                            currentMessageText = null;
                        } else {
                            await new Promise(resolve => setTimeout(resolve, 20));
                            currentMessageText.textContent += data.content;
                            this.scrollToBottom();
                        }
                    }
                }
            }
        } catch (error) {
            console.error('Error:', error);
            loadingElement.remove();
            this.appendMessage('오류가 발생했습니다. 다시 시도해주세요.', false);
        } finally {
            this.isLoading = false;
            this.sendButton.disabled = false;
            this.messageInput.disabled = false;
            this.messageInput.focus();
        }
    }

    appendMessage(message, isUser = false) {
        const messageElement = this.createMessageElement(message, isUser);
        this.chatContainer.appendChild(messageElement);
        this.scrollToBottom();
    }

    scrollToBottom() {
        this.chatContainer.scrollTop = this.chatContainer.scrollHeight;
    }

    async loadWelcomeMessage() {
        try {
            const response = await fetch(this.welcomeApiUrl);
            if (!response.ok) {
                throw new Error('Welcome message request failed');
            }

            const data = await response.json();
            this.sessionId = data.session_id;
            this.appendMessage(data.content, false);
        } catch (error) {
            console.error('Error:', error);
            this.appendMessage('웰컴 메시지를 불러오는데 실패했습니다.', false);
        }
    }

}

document.addEventListener('DOMContentLoaded', () => {
    window.chatUI = new ChatUI();
});