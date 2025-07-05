// Healthcare Chatbot JavaScript

// Global Variables
let chatHistory = [];
let isTyping = false;
let chatContainer = null;
let messageInput = null;

// Medical Knowledge Base
const medicalKnowledgeBase = {
    symptoms: {
        fever: {
            description: "Elevated body temperature, usually above 100.4°F (38°C)",
            causes: ["Infection", "Heat exhaustion", "Autoimmune conditions"],
            advice: "Rest, stay hydrated, and monitor temperature. Seek medical attention if fever persists over 3 days or exceeds 103°F."
        },
        headache: {
            description: "Pain or discomfort in the head or upper neck",
            causes: ["Tension", "Dehydration", "Stress", "Migraines"],
            advice: "Rest in a quiet, dark room. Apply cold or warm compress. Stay hydrated. Consult doctor if severe or persistent."
        },
        cough: {
            description: "Reflexive clearing of the throat and airways",
            causes: ["Cold", "Allergies", "Asthma", "Infections"],
            advice: "Stay hydrated, use humidifier, avoid irritants. See doctor if persistent or accompanied by fever."
        }
    },
    
    medications: {
        dosage: "Always follow your doctor's prescribed dosage. Never exceed recommended amounts.",
        interactions: "Inform your doctor about all medications you're taking to avoid dangerous interactions.",
        side_effects: "Contact your healthcare provider if you experience unexpected side effects."
    },
    
    emergency_signs: [
        "Difficulty breathing or shortness of breath",
        "Chest pain or pressure",
        "Severe bleeding",
        "Loss of consciousness",
        "Severe allergic reactions",
        "Signs of stroke (facial drooping, arm weakness, speech difficulty)"
    ]
};

// Initialize Chatbot
function initializeChatbot() {
    chatContainer = document.querySelector('.chat-container');
    messageInput = document.getElementById('message');
    
    if (!chatContainer) return;
    
    // Load chat history
    loadChatHistory();
    
    // Setup event listeners
    setupChatEventListeners();
    
    // Show welcome message
    if (chatHistory.length === 0) {
        addWelcomeMessage();
    }
    
    console.log('Chatbot initialized');
}

// Setup Event Listeners
function setupChatEventListeners() {
    // Enter key to send message
    if (messageInput) {
        messageInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
    }
    
    // Auto-resize textarea
    if (messageInput) {
        messageInput.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = this.scrollHeight + 'px';
        });
    }
}

// Add Welcome Message
function addWelcomeMessage() {
    const welcomeMessage = {
        type: 'bot',
        message: "Hello! I'm your AI medical assistant. I can help answer general medical questions, provide information about symptoms, medications, and appointment scheduling. How can I assist you today?",
        timestamp: new Date(),
        suggestions: [
            "Tell me about fever symptoms",
            "How do I schedule an appointment?",
            "What are emergency warning signs?",
            "Medication safety tips"
        ]
    };
    
    addMessageToChat(welcomeMessage);
}

// Send Message
function sendMessage() {
    if (!messageInput || isTyping) return;
    
    const message = messageInput.value.trim();
    if (!message) return;
    
    // Add user message
    const userMessage = {
        type: 'user',
        message: message,
        timestamp: new Date()
    };
    
    addMessageToChat(userMessage);
    chatHistory.push(userMessage);
    
    // Clear input
    messageInput.value = '';
    messageInput.style.height = 'auto';
    
    // Show typing indicator
    showTypingIndicator();
    
    // Process message and get response
    setTimeout(() => {
        const response = processMessage(message);
        hideTypingIndicator();
        addMessageToChat(response);
        chatHistory.push(response);
        saveChatHistory();
    }, 1000 + Math.random() * 2000); // Simulate thinking time
}

// Process Message
function processMessage(message) {
    const lowerMessage = message.toLowerCase();
    
    // Emergency keywords
    const emergencyKeywords = ['emergency', 'urgent', 'help', 'pain', 'bleeding', 'breathing'];
    if (emergencyKeywords.some(keyword => lowerMessage.includes(keyword))) {
        return createEmergencyResponse();
    }
    
    // Symptom queries
    if (lowerMessage.includes('symptom') || lowerMessage.includes('fever') || 
        lowerMessage.includes('headache') || lowerMessage.includes('cough')) {
        return createSymptomResponse(lowerMessage);
    }
    
    // Medication queries
    if (lowerMessage.includes('medication') || lowerMessage.includes('drug') || 
        lowerMessage.includes('medicine') || lowerMessage.includes('pill')) {
        return createMedicationResponse();
    }
    
    // Appointment queries
    if (lowerMessage.includes('appointment') || lowerMessage.includes('schedule') || 
        lowerMessage.includes('booking') || lowerMessage.includes('visit')) {
        return createAppointmentResponse();
    }
    
    // General health queries
    if (lowerMessage.includes('health') || lowerMessage.includes('wellness') || 
        lowerMessage.includes('prevention')) {
        return createHealthResponse();
    }
    
    // Default response
    return createDefaultResponse();
}

// Create Emergency Response
function createEmergencyResponse() {
    return {
        type: 'bot',
        message: "🚨 For medical emergencies, please call 911 or go to the nearest emergency room immediately. Don't delay seeking professional medical help.",
        timestamp: new Date(),
        isEmergency: true,
        suggestions: [
            "Call 911",
            "Find nearest hospital",
            "Emergency contact information"
        ]
    };
}

// Create Symptom Response
function createSymptomResponse(message) {
    let response = "I understand you're asking about symptoms. ";
    
    if (message.includes('fever')) {
        const fever = medicalKnowledgeBase.symptoms.fever;
        response += `Fever is ${fever.description}. Common causes include: ${fever.causes.join(', ')}. 
                    Advice: ${fever.advice}`;
    } else if (message.includes('headache')) {
        const headache = medicalKnowledgeBase.symptoms.headache;
        response += `Headaches are ${headache.description}. Common causes include: ${headache.causes.join(', ')}. 
                    Advice: ${headache.advice}`;
    } else if (message.includes('cough')) {
        const cough = medicalKnowledgeBase.symptoms.cough;
        response += `A cough is ${cough.description}. Common causes include: ${cough.causes.join(', ')}. 
                    Advice: ${cough.advice}`;
    } else {
        response += "For proper symptom evaluation, please schedule an appointment with your healthcare provider. They can provide personalized advice based on your specific situation.";
    }
    
    return {
        type: 'bot',
        message: response,
        timestamp: new Date(),
        suggestions: [
            "Schedule appointment",
            "Emergency warning signs",
            "Other symptoms"
        ]
    };
}

// Create Medication Response
function createMedicationResponse() {
    return {
        type: 'bot',
        message: `Here's important information about medications:
        
        📋 ${medicalKnowledgeBase.medications.dosage}
        
        ⚠️ ${medicalKnowledgeBase.medications.interactions}
        
        🔔 ${medicalKnowledgeBase.medications.side_effects}
        
        Always consult with your healthcare provider before starting, stopping, or changing any medication.`,
        timestamp: new Date(),
        suggestions: [
            "Talk to pharmacist",
            "Schedule medication review",
            "Report side effects"
        ]
    };
}

// Create Appointment Response
function createAppointmentResponse() {
    return {
        type: 'bot',
        message: `To schedule an appointment:
        
        1. 📅 Use the 'Schedule Appointment' feature in your patient portal
        2. 📞 Call our office during business hours
        3. 💻 Use online scheduling system
        
        Our hours:
        • Monday-Friday: 8:00 AM - 6:00 PM
        • Saturday: 9:00 AM - 2:00 PM
        • Sunday: Emergency only
        
        Please have your insurance information ready when scheduling.`,
        timestamp: new Date(),
        suggestions: [
            "Schedule now",
            "View available times",
            "Contact information"
        ]
    };
}

// Create Health Response
function createHealthResponse() {
    const healthTips = [
        "Stay physically active with regular exercise",
        "Maintain a balanced diet rich in fruits and vegetables",
        "Get adequate sleep (7-9 hours per night)",
        "Stay hydrated by drinking plenty of water",
        "Manage stress through relaxation techniques",
        "Keep up with regular medical checkups"
    ];
    
    return {
        type: 'bot',
        message: `Here are some general health and wellness tips:
        
        ${healthTips.map(tip => `• ${tip}`).join('\n')}
        
        Remember, these are general guidelines. Always consult with your healthcare provider for personalized advice.`,
        timestamp: new Date(),
        suggestions: [
            "Nutrition advice",
            "Exercise recommendations",
            "Stress management"
        ]
    };
}

// Create Default Response
function createDefaultResponse() {
    const responses = [
        "I understand you have a medical question. For the best care, please schedule an appointment with your healthcare provider.",
        "I'm here to provide general medical information. For specific health concerns, please consult with a qualified healthcare professional.",
        "Your health is important. While I can provide general information, a healthcare provider can give you personalized advice.",
        "For specific medical advice tailored to your situation, please speak with your doctor or healthcare provider."
    ];
    
    return {
        type: 'bot',
        message: responses[Math.floor(Math.random() * responses.length)],
        timestamp: new Date(),
        suggestions: [
            "Schedule appointment",
            "Common symptoms",
            "Emergency information",
            "Medication questions"
        ]
    };
}

// Add Message to Chat
function addMessageToChat(messageData) {
    if (!chatContainer) return;
    
    const messageElement = document.createElement('div');
    messageElement.className = `chat-message ${messageData.type}-message mb-3`;
    
    const timestamp = formatTime(messageData.timestamp);
    
    if (messageData.type === 'user') {
        messageElement.innerHTML = `
            <div class="d-flex justify-content-end">
                <div class="message-content">
                    <div class="message-bubble bg-primary text-white p-3 rounded">
                        <p class="mb-0">${escapeHtml(messageData.message)}</p>
                    </div>
                    <small class="text-muted">You - ${timestamp}</small>
                </div>
                <div class="avatar bg-secondary text-white rounded-circle d-flex align-items-center justify-content-center ms-3" style="width: 40px; height: 40px;">
                    <i class="fas fa-user"></i>
                </div>
            </div>
        `;
    } else {
        messageElement.innerHTML = `
            <div class="d-flex">
                <div class="avatar bg-primary text-white rounded-circle d-flex align-items-center justify-content-center me-3" style="width: 40px; height: 40px;">
                    <i class="fas fa-robot"></i>
                </div>
                <div class="message-content">
                    <div class="message-bubble ${messageData.isEmergency ? 'bg-danger text-white' : 'bg-light'} p-3 rounded">
                        <p class="mb-0">${formatMessage(messageData.message)}</p>
                    </div>
                    <small class="text-muted">AI Assistant - ${timestamp}</small>
                    ${messageData.suggestions ? createSuggestions(messageData.suggestions) : ''}
                </div>
            </div>
        `;
    }
    
    chatContainer.appendChild(messageElement);
    scrollToBottom();
}

// Create Suggestions
function createSuggestions(suggestions) {
    if (!suggestions || suggestions.length === 0) return '';
    
    return `
        <div class="suggestions mt-2">
            <small class="text-muted">Suggested topics:</small>
            <div class="d-flex flex-wrap gap-1 mt-1">
                ${suggestions.map(suggestion => 
                    `<button class="btn btn-sm btn-outline-secondary suggestion-btn" onclick="selectSuggestion('${escapeHtml(suggestion)}')">
                        ${escapeHtml(suggestion)}
                    </button>`
                ).join('')}
            </div>
        </div>
    `;
}

// Select Suggestion
function selectSuggestion(suggestion) {
    if (messageInput) {
        messageInput.value = suggestion;
        messageInput.focus();
    }
}

// Show Typing Indicator
function showTypingIndicator() {
    if (!chatContainer) return;
    
    isTyping = true;
    const typingElement = document.createElement('div');
    typingElement.className = 'chat-message bot-message mb-3 typing-indicator';
    typingElement.innerHTML = `
        <div class="d-flex">
            <div class="avatar bg-primary text-white rounded-circle d-flex align-items-center justify-content-center me-3" style="width: 40px; height: 40px;">
                <i class="fas fa-robot"></i>
            </div>
            <div class="message-content">
                <div class="message-bubble bg-light p-3 rounded">
                    <div class="typing-animation">
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                </div>
                <small class="text-muted">AI Assistant is typing...</small>
            </div>
        </div>
    `;
    
    chatContainer.appendChild(typingElement);
    scrollToBottom();
}

// Hide Typing Indicator
function hideTypingIndicator() {
    isTyping = false;
    const typingIndicator = document.querySelector('.typing-indicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

// Format Message
function formatMessage(message) {
    // Convert line breaks to <br>
    return message.replace(/\n/g, '<br>');
}

// Format Time
function formatTime(date) {
    return new Date(date).toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Escape HTML
function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// Scroll to Bottom
function scrollToBottom() {
    if (chatContainer) {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
}

// Load Chat History
function loadChatHistory() {
    const saved = localStorage.getItem('healthcare_chat_history');
    if (saved) {
        try {
            chatHistory = JSON.parse(saved);
            chatHistory.forEach(message => addMessageToChat(message));
        } catch (e) {
            console.error('Error loading chat history:', e);
            chatHistory = [];
        }
    }
}

// Save Chat History
function saveChatHistory() {
    try {
        localStorage.setItem('healthcare_chat_history', JSON.stringify(chatHistory));
    } catch (e) {
        console.error('Error saving chat history:', e);
    }
}

// Clear Chat History
function clearChatHistory() {
    chatHistory = [];
    localStorage.removeItem('healthcare_chat_history');
    if (chatContainer) {
        chatContainer.innerHTML = '';
    }
    addWelcomeMessage();
}

// Add typing animation CSS
const style = document.createElement('style');
style.textContent = `
    .typing-animation {
        display: inline-flex;
        align-items: center;
        gap: 4px;
    }
    
    .typing-animation span {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: #6c757d;
        animation: typing 1.4s infinite ease-in-out;
    }
    
    .typing-animation span:nth-child(1) {
        animation-delay: -0.32s;
    }
    
    .typing-animation span:nth-child(2) {
        animation-delay: -0.16s;
    }
    
    @keyframes typing {
        0%, 80%, 100% {
            transform: scale(0);
        }
        40% {
            transform: scale(1);
        }
    }
    
    .suggestion-btn {
        font-size: 0.75rem;
        padding: 0.25rem 0.5rem;
    }
`;
document.head.appendChild(style);

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', initializeChatbot);
