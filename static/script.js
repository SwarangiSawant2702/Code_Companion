class VoiceChatbot {
    constructor() {
        this.recordBtn = document.getElementById('recordBtn');
        this.stopBtn = document.getElementById('stopBtn');
        this.messageContainer = document.getElementById('messageContainer');
        this.statusIcon = document.getElementById('statusIcon');
        this.statusText = document.getElementById('statusText');
        
        this.recognition = null;
        this.isRecording = false;
        this.isProcessing = false;
        
        this.initSpeechRecognition();
        this.initEventListeners();
        this.initSpeechSynthesis();
    }
    
    initSpeechRecognition() {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            this.recognition = new SpeechRecognition();
            this.recognition.continuous = false;
            this.recognition.interimResults = false;
            this.recognition.lang = 'en-US';
            
            this.recognition.onstart = () => {
                this.setStatus('listening', 'Listening...');
                this.isRecording = true;
            };
            
            this.recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                this.addMessage(transcript, 'user');
                this.processMessage(transcript);
            };
            
            this.recognition.onerror = (event) => {
                console.error('Speech recognition error:', event.error);
                this.setStatus('ready', 'Error occurred. Ready to listen');
                this.resetButtons();
                this.addMessage('Sorry, I couldn\'t understand that. Please try again.', 'bot');
            };
            
            this.recognition.onend = () => {
                this.isRecording = false;
            };
        } else {
            this.showError('Speech Recognition is not supported in this browser. Please use Chrome or Firefox.');
        }
    }
    
    initSpeechSynthesis() {
        this.synth = window.speechSynthesis;
    }
    
    initEventListeners() {
        this.recordBtn.addEventListener('click', () => this.startRecording());
        this.stopBtn.addEventListener('click', () => this.stopRecording());
    }
    
    startRecording() {
        if (!this.recognition) {
            this.showError('Speech recognition not available');
            return;
        }
        
        if (this.isRecording || this.isProcessing) {
            return;
        }
        
        this.recordBtn.style.display = 'none';
        this.stopBtn.style.display = 'flex';
        
        try {
            this.recognition.start();
        } catch (error) {
            console.error('Error starting recognition:', error);
            this.resetButtons();
            this.setStatus('ready', 'Ready to listen');
        }
    }
    
    stopRecording() {
        if (this.recognition && this.isRecording) {
            this.recognition.stop();
        }
        this.resetButtons();
        this.setStatus('ready', 'Ready to listen');
    }
    
    resetButtons() {
        this.recordBtn.style.display = 'flex';
        this.stopBtn.style.display = 'none';
    }
    
    async processMessage(message) {
        this.setStatus('processing', 'Processing...');
        this.isProcessing = true;
        
        // Add a temporary processing message
        const processingMsg = this.addMessage('Thinking<span class="processing-dots"></span>', 'bot');
        
        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            // Remove processing message
            processingMsg.remove();
            
            if (data.error) {
                this.addMessage(`Error: ${data.error}`, 'bot');
            } else {
                this.addMessage(data.response, 'bot');
                this.speak(data.response);
            }
            
        } catch (error) {
            console.error('Error processing message:', error);
            processingMsg.remove();
            this.addMessage('Sorry, I encountered an error. Please try again.', 'bot');
        } finally {
            this.isProcessing = false;
            this.setStatus('ready', 'Ready to listen');
            this.resetButtons();
        }
    }
    
    addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        const headerDiv = document.createElement('div');
        headerDiv.className = 'message-header';
        headerDiv.innerHTML = sender === 'user' ? 
            '<i class="fas fa-user"></i> You:' : 
            '<i class="fas fa-robot"></i> Swarangi:';
        
        const contentDiv = document.createElement('div');
        contentDiv.innerHTML = text;
        
        messageDiv.appendChild(headerDiv);
        messageDiv.appendChild(contentDiv);
        
        // Remove welcome message if it exists
        const welcomeMessage = this.messageContainer.querySelector('.welcome-message');
        if (welcomeMessage) {
            welcomeMessage.remove();
        }
        
        this.messageContainer.appendChild(messageDiv);
        this.messageContainer.scrollTop = this.messageContainer.scrollHeight;
        
        return messageDiv;
    }
    
    speak(text) {
        if (this.synth && text) {
            // Cancel any ongoing speech
            this.synth.cancel();
            
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.rate = 0.9;
            utterance.pitch = 1.0;
            utterance.volume = 1.0;
            
            // Try to use a female voice if available
            const voices = this.synth.getVoices();
            const femaleVoice = voices.find(voice => 
                voice.name.includes('Female') || 
                voice.name.includes('female') ||
                voice.name.includes('Samantha') ||
                voice.name.includes('Karen') ||
                voice.name.includes('Moira')
            );
            
            if (femaleVoice) {
                utterance.voice = femaleVoice;
            }
            
            this.synth.speak(utterance);
        }
    }
    
    setStatus(status, text) {
        this.statusIcon.className = `status-${status}`;
        this.statusText.textContent = text;
        
        // Update icon based on status
        const icon = this.statusIcon.querySelector('i');
        switch (status) {
            case 'listening':
                icon.className = 'fas fa-microphone';
                break;
            case 'processing':
                icon.className = 'fas fa-cog';
                break;
            case 'ready':
            default:
                icon.className = 'fas fa-microphone';
                break;
        }
    }
    
    showError(message) {
        this.addMessage(message, 'bot');
        this.setStatus('ready', 'Ready to listen');
    }
}

// Initialize the chatbot when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new VoiceChatbot();
});

// Handle browser speech synthesis voices loading
window.speechSynthesis.onvoiceschanged = () => {
    // Voices are now loaded
    console.log('Speech synthesis voices loaded');
};
