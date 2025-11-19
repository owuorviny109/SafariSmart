/**
 * SafariSmart Kenya - Trip Planning Chat Widget
 * 
 * Hybrid chat system for custom destination planning.
 * Matches the Kenya-inspired design system.
 * 
 * @author SafariSmart Kenya Team
 * @date 2025-11-19
 */

class TripPlannerChat {
    constructor() {
        this.isOpen = false;
        this.sessionId = null;
        this.messages = [];
        this.extractedData = {};
        
        this.init();
    }
    
    /**
     * Initialize chat widget
     */
    init() {
        this.createChatWidget();
        this.attachEventListeners();
    }
    
    /**
     * Create chat widget HTML structure
     */
    createChatWidget() {
        const chatHTML = `
            <div id="chatWidget" class="chat-widget">
                <!-- Chat Button -->
                <button id="chatToggle" class="chat-toggle elevation-acacia">
                    <i class="bi bi-chat-dots-fill"></i>
                    <span class="chat-badge">Plan Custom Trip</span>
                </button>
                
                <!-- Chat Window -->
                <div id="chatWindow" class="chat-window elevation-kilimanjaro" style="display: none;">
                    <!-- Header -->
                    <div class="chat-header">
                        <div class="chat-header-content">
                            <div class="chat-avatar">
                                <i class="bi bi-robot"></i>
                            </div>
                            <div class="chat-header-text">
                                <h4>Safari Assistant</h4>
                                <p class="chat-status">
                                    <span class="status-dot"></span>
                                    Online
                                </p>
                            </div>
                        </div>
                        <button id="chatClose" class="chat-close-btn">
                            <i class="bi bi-x-lg"></i>
                        </button>
                    </div>
                    
                    <!-- Messages Container -->
                    <div id="chatMessages" class="chat-messages">
                        <!-- Messages will be added here -->
                    </div>
                    
                    <!-- Input Area -->
                    <div class="chat-input-container">
                        <input 
                            type="text" 
                            id="chatInput" 
                            class="chat-input" 
                            placeholder="Type your message..."
                            autocomplete="off"
                        />
                        <button id="chatSend" class="chat-send-btn">
                            <i class="bi bi-send-fill"></i>
                        </button>
                    </div>
                    
                    <!-- Loading Indicator -->
                    <div id="chatLoading" class="chat-loading" style="display: none;">
                        <div class="typing-indicator">
                            <span></span>
                            <span></span>
                            <span></span>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', chatHTML);
    }
    
    /**
     * Attach event listeners
     */
    attachEventListeners() {
        const toggleBtn = document.getElementById('chatToggle');
        const closeBtn = document.getElementById('chatClose');
        const sendBtn = document.getElementById('chatSend');
        const input = document.getElementById('chatInput');
        
        toggleBtn.addEventListener('click', () => this.toggleChat());
        closeBtn.addEventListener('click', () => this.closeChat());
        sendBtn.addEventListener('click', () => this.sendMessage());
        
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendMessage();
            }
        });
    }
    
    /**
     * Toggle chat window
     */
    async toggleChat() {
        const chatWindow = document.getElementById('chatWindow');
        const toggleBtn = document.getElementById('chatToggle');
        
        this.isOpen = !this.isOpen;
        
        if (this.isOpen) {
            chatWindow.style.display = 'flex';
            toggleBtn.style.display = 'none';
            
            // Start conversation if first time
            if (this.messages.length === 0) {
                await this.startConversation();
            }
            
            // Focus input
            document.getElementById('chatInput').focus();
        } else {
            chatWindow.style.display = 'none';
            toggleBtn.style.display = 'flex';
        }
    }
    
    /**
     * Close chat window
     */
    closeChat() {
        this.isOpen = false;
        document.getElementById('chatWindow').style.display = 'none';
        document.getElementById('chatToggle').style.display = 'flex';
    }
    
    /**
     * Start new conversation
     */
    async startConversation() {
        try {
            const response = await fetch('/api/chat/start/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                }
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                this.sessionId = data.session_id;
                this.addMessage('bot', data.message);
            }
        } catch (error) {
            console.error('Failed to start chat:', error);
            this.addMessage('bot', 'Sorry, I\'m having trouble connecting. Please try again.');
        }
    }
    
    /**
     * Send user message
     */
    async sendMessage() {
        const input = document.getElementById('chatInput');
        const message = input.value.trim();
        
        if (!message) return;
        
        // Add user message to UI
        this.addMessage('user', message);
        input.value = '';
        
        // Show loading
        this.showLoading(true);
        
        try {
            const response = await fetch('/api/chat/message/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({ message })
            });
            
            const data = await response.json();
            
            this.showLoading(false);
            
            if (data.status === 'success') {
                this.addMessage('bot', data.message);
                
                // Update extracted data
                if (data.extracted_data) {
                    this.extractedData = data.extracted_data;
                }
                
                // Check if completed
                if (data.completed) {
                    setTimeout(() => this.handleCompletion(), 1000);
                }
            } else {
                this.addMessage('bot', 'Sorry, I didn\'t understand that. Could you rephrase?');
            }
        } catch (error) {
            console.error('Failed to send message:', error);
            this.showLoading(false);
            this.addMessage('bot', 'Sorry, something went wrong. Please try again.');
        }
    }
    
    /**
     * Add message to chat
     */
    addMessage(role, content) {
        const messagesContainer = document.getElementById('chatMessages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message chat-message-${role}`;
        
        const avatar = role === 'bot' 
            ? '<div class="message-avatar"><i class="bi bi-robot"></i></div>'
            : '<div class="message-avatar"><i class="bi bi-person-fill"></i></div>';
        
        messageDiv.innerHTML = `
            ${avatar}
            <div class="message-bubble">
                <p>${this.escapeHtml(content)}</p>
            </div>
        `;
        
        messagesContainer.appendChild(messageDiv);
        
        // Scroll to bottom
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        
        // Store message
        this.messages.push({ role, content });
    }
    
    /**
     * Show/hide loading indicator
     */
    showLoading(show) {
        const loading = document.getElementById('chatLoading');
        loading.style.display = show ? 'flex' : 'none';
    }
    
    /**
     * Handle conversation completion
     */
    handleCompletion() {
        // Add custom destinations to the wizard
        if (this.extractedData.custom_destinations && this.extractedData.custom_destinations.length > 0) {
            // Use the global function to add destinations
            if (typeof window.addCustomDestinationFromChat === 'function') {
                this.extractedData.custom_destinations.forEach(dest => {
                    window.addCustomDestinationFromChat(dest);
                });
            } else {
                // Fallback: directly update hidden input
                const customInput = document.getElementById('customDestinationsData');
                if (customInput) {
                    customInput.value = JSON.stringify(this.extractedData.custom_destinations);
                }
            }
        }
        
        // Show success message
        this.addMessage('bot', 'Perfect! Your custom trip has been added. Click "Next" to continue! ✨');
        
        // Close chat after delay
        setTimeout(() => {
            this.closeChat();
        }, 2000);
    }
    
    /**
     * Get CSRF token
     */
    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
    }
    
    /**
     * Escape HTML to prevent XSS
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize chat when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.tripChat = new TripPlannerChat();
});
