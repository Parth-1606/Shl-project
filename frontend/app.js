const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
const chatBox = document.getElementById('chat-box');

// This maintains the stateless conversation array required by our API
let conversationHistory = [];

// Helper to convert Markdown/Newlines to HTML
function formatText(text) {
    return text.replace(/\n/g, '<br>').replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
}

// Function to add a message to the UI
function appendMessage(role, content, recommendations = []) {
    const isUser = role === 'user';
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${role}`;
    
    const icon = isUser ? 'ri-user-line' : 'ri-robot-2-line';
    
    let recsHTML = '';
    if (recommendations && recommendations.length > 0) {
        recsHTML = '<div class="recommendations">';
        recommendations.forEach(rec => {
            recsHTML += `
                <div class="rec-card">
                    <a href="${rec.url}" target="_blank"><i class="ri-external-link-line"></i> ${rec.name}</a>
                    <p>Type: ${rec.test_type}</p>
                </div>
            `;
        });
        recsHTML += '</div>';
    }

    msgDiv.innerHTML = `
        <div class="avatar"><i class="${icon}"></i></div>
        <div class="content">
            <p>${formatText(content)}</p>
            ${recsHTML}
        </div>
    `;
    
    chatBox.appendChild(msgDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

// Function to show/hide loading indicator
function toggleLoading(show) {
    if (show) {
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'message bot loading';
        loadingDiv.id = 'loading-indicator';
        loadingDiv.innerHTML = `
            <div class="avatar"><i class="ri-robot-2-line"></i></div>
            <div class="content">
                <div class="typing-indicator">
                    <span></span><span></span><span></span>
                </div>
            </div>
        `;
        chatBox.appendChild(loadingDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
    } else {
        const loader = document.getElementById('loading-indicator');
        if (loader) loader.remove();
    }
}

// Form Submission
chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const text = userInput.value.trim();
    if (!text) return;

    // Add user message to UI and history
    appendMessage('user', text);
    conversationHistory.push({ role: 'user', content: text });
    userInput.value = '';

    toggleLoading(true);

    try {
        // Send request to our FastAPI backend
        const response = await fetch('http://localhost:8000/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ conversation: conversationHistory })
        });

        if (!response.ok) {
            throw new Error(`API Error: ${response.status}`);
        }

        const data = await response.json();
        toggleLoading(false);

        // Add bot message to UI and history
        appendMessage('assistant', data.message, data.recommendations);
        conversationHistory.push({ role: 'assistant', content: data.message });

    } catch (error) {
        console.error(error);
        toggleLoading(false);
        appendMessage('assistant', 'Sorry, I encountered an error connecting to the server. Make sure the FastAPI server is running on port 8000.');
    }
});
