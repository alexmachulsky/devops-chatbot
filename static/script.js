// Chat state
let conversationHistory = [];

// DOM Elements
const messagesContainer = document.getElementById('messages');
const userInput = document.getElementById('userInput');
const sendButton = document.getElementById('sendButton');
const clearButton = document.getElementById('clearButton');
const loadingIndicator = document.getElementById('loading');

// Auto-resize textarea
userInput.addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = this.scrollHeight + 'px';
});

// Send message on Enter (Shift+Enter for new line)
userInput.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// Send button click
sendButton.addEventListener('click', sendMessage);

// Clear chat button
clearButton.addEventListener('click', clearChat);

// Send message function
async function sendMessage() {
    const message = userInput.value.trim();
    
    if (!message) return;
    
    // Disable input while processing
    userInput.disabled = true;
    sendButton.disabled = true;
    loadingIndicator.style.display = 'block';
    
    // Add user message to UI
    addMessage(message, 'user');
    
    // Add to conversation history
    conversationHistory.push({
        role: 'user',
        content: message
    });
    
    // Clear input
    userInput.value = '';
    userInput.style.height = 'auto';
    
    try {
        // Call API
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                history: conversationHistory.slice(-10) // Keep last 10 messages for context
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Add bot response to UI
            addMessage(data.message, 'bot');
            
            // Add to conversation history
            conversationHistory.push({
                role: 'assistant',
                content: data.message
            });
        } else {
            addMessage('Sorry, I encountered an error. Please try again.', 'bot');
        }
    } catch (error) {
        console.error('Error:', error);
        addMessage('Sorry, I couldn\'t connect to the server. Please try again.', 'bot');
    } finally {
        // Re-enable input
        userInput.disabled = false;
        sendButton.disabled = false;
        loadingIndicator.style.display = 'none';
        userInput.focus();
    }
}

// Add message to UI
function addMessage(text, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    
    const avatarDiv = document.createElement('div');
    avatarDiv.className = `message-avatar ${sender}-avatar`;
    avatarDiv.innerHTML = sender === 'bot' 
        ? '<i class="fas fa-robot"></i>' 
        : '<i class="fas fa-user"></i>';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    const textDiv = document.createElement('div');
    textDiv.className = 'message-text';
    
    // Format text with markdown-like syntax
    textDiv.innerHTML = formatMessage(text);
    
    contentDiv.appendChild(textDiv);
    messageDiv.appendChild(avatarDiv);
    messageDiv.appendChild(contentDiv);
    
    messagesContainer.appendChild(messageDiv);
    
    // Scroll to bottom
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Format message text
function formatMessage(text) {
    // Convert markdown-style code blocks
    text = text.replace(/```(\w+)?\n([\s\S]*?)```/g, '<pre><code>$2</code></pre>');
    
    // Convert inline code
    text = text.replace(/`([^`]+)`/g, '<code>$1</code>');
    
    // Convert bold
    text = text.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    
    // Convert line breaks
    text = text.replace(/\n/g, '<br>');
    
    return text;
}

// Clear chat
function clearChat() {
    if (confirm('Are you sure you want to clear the chat history?')) {
        conversationHistory = [];
        messagesContainer.innerHTML = '';
        
        // Add welcome message back
        const welcomeMessage = `👋 Hello! I'm your DevOps assistant. I can help you with:
        <ul>
            <li>Docker & Kubernetes</li>
            <li>CI/CD Pipelines</li>
            <li>Infrastructure as Code (Terraform, Ansible)</li>
            <li>Cloud Platforms (AWS, Azure, GCP)</li>
            <li>Monitoring & Logging</li>
            <li>Best Practices & Troubleshooting</li>
        </ul>
        Ask me anything! 🚀`;
        
        addMessage(welcomeMessage, 'bot');
    }
}

// Focus input on load
window.addEventListener('load', () => {
    userInput.focus();
});
