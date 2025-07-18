// ===== Global Variables =====
let currentUser = null;
let currentChat = null;

// ===== API Functions =====
const API = {
    // User API
    createUser: async (userData) => {
        const response = await fetch('/api/create_user', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(userData)
        });
        return response.json();
    },

    selectUser: async (userId) => {
        const response = await fetch(`/api/select_user/${userId}`, {
            method: 'POST'
        });
        return response.json();
    },

    // Chat API
    createChat: async (chatData) => {
        const response = await fetch('/api/create_chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(chatData)
        });
        return response.json();
    },

    selectChat: async (chatId) => {
        const response = await fetch(`/api/select_chat/${chatId}`, {
            method: 'POST'
        });
        return response.json();
    },

    sendMessage: async (messageData) => {
        const response = await fetch('/api/send_message', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(messageData)
        });
        return response.json();
    },

    // Analysis API
    analyzeProfile: async (formData) => {
        const response = await fetch('/api/analyze_profile', {
            method: 'POST',
            body: formData
        });
        return response.json();
    },

    generateExamples: async (context) => {
        const response = await fetch('/api/generate_examples', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ context })
        });
        return response.json();
    },

    getPhotoAdvice: async () => {
        const response = await fetch('/api/photo_advice');
        return response.json();
    },

    checkGrammar: async (text) => {
        const response = await fetch('/api/check_grammar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text })
        });
        return response.json();
    }
};

// ===== UI Functions =====
const UI = {
    showLoading: (container) => {
        container.innerHTML = `
            <div class="spinner-container">
                <div class="spinner"></div>
            </div>
        `;
    },

    showError: (message) => {
        const alertHtml = `
            <div class="alert alert-danger alert-dismissible fade show" role="alert">
                <i class="fas fa-exclamation-circle"></i> ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        document.querySelector('.main-content').insertAdjacentHTML('afterbegin', alertHtml);
    },

    showSuccess: (message) => {
        const alertHtml = `
            <div class="alert alert-success alert-dismissible fade show" role="alert">
                <i class="fas fa-check-circle"></i> ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        document.querySelector('.main-content').insertAdjacentHTML('afterbegin', alertHtml);
    }
};

// ===== Profile Page Functions =====
if (document.getElementById('createUserForm')) {
    const form = document.getElementById('createUserForm');
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Создание...';
        
        const formData = new FormData(form);
        const userData = Object.fromEntries(formData);
        
        try {
            const result = await API.createUser(userData);
            if (result.success) {
                UI.showSuccess(result.message);
                setTimeout(() => window.location.reload(), 1000);
            } else {
                UI.showError(result.error);
            }
        } catch (error) {
            UI.showError('Ошибка при создании профиля');
        } finally {
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalText;
        }
    });
}

// User selection
if (document.getElementById('userSelect')) {
    document.getElementById('userSelect').addEventListener('change', async (e) => {
        const userId = e.target.value;
        if (userId && userId !== 'new') {
            const result = await API.selectUser(userId);
            if (result.success) {
                window.location.reload();
            }
        }
    });
}

// ===== Chat Page Functions =====
if (document.getElementById('createChatForm')) {
    const form = document.getElementById('createChatForm');
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const formData = new FormData(form);
        const chatData = Object.fromEntries(formData);
        
        try {
            const result = await API.createChat(chatData);
            if (result.success) {
                UI.showSuccess(result.message);
                setTimeout(() => window.location.reload(), 1000);
            } else {
                UI.showError(result.error);
            }
        } catch (error) {
            UI.showError('Ошибка при создании чата');
        }
    });
}

// Message sending
if (document.getElementById('sendMessageForm')) {
    const form = document.getElementById('sendMessageForm');
    const messageInput = document.getElementById('messageInput');
    const senderTypeInputs = document.querySelectorAll('input[name="sender_type"]');
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const messageText = messageInput.value.trim();
        const senderType = document.querySelector('input[name="sender_type"]:checked').value;
        
        if (!messageText) return;
        
        const submitBtn = form.querySelector('button[type="submit"]');
        submitBtn.disabled = true;
        
        try {
            const result = await API.sendMessage({
                message_text: messageText,
                sender_type: senderType
            });
            
            if (result.success) {
                messageInput.value = '';
                // Reload messages
                window.location.reload();
            } else {
                UI.showError(result.error);
            }
        } catch (error) {
            UI.showError('Ошибка при отправке сообщения');
        } finally {
            submitBtn.disabled = false;
        }
    });
}

// ===== Analysis Page Functions =====
if (document.getElementById('profileAnalysisForm')) {
    const form = document.getElementById('profileAnalysisForm');
    const fileInput = document.getElementById('profileImage');
    const textInput = document.getElementById('profileText');
    const fileUploadArea = document.querySelector('.file-upload-area');
    const resultsContainer = document.getElementById('analysisResults');
    
    // File upload drag & drop
    if (fileUploadArea) {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            fileUploadArea.addEventListener(eventName, preventDefaults, false);
        });
        
        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }
        
        ['dragenter', 'dragover'].forEach(eventName => {
            fileUploadArea.addEventListener(eventName, () => {
                fileUploadArea.classList.add('drag-over');
            }, false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            fileUploadArea.addEventListener(eventName, () => {
                fileUploadArea.classList.remove('drag-over');
            }, false);
        });
        
        fileUploadArea.addEventListener('drop', (e) => {
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                fileInput.files = files;
                updateFileInfo(files[0]);
            }
        });
        
        fileUploadArea.addEventListener('click', () => {
            fileInput.click();
        });
        
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                updateFileInfo(e.target.files[0]);
            }
        });
    }
    
    function updateFileInfo(file) {
        const fileInfo = document.getElementById('fileInfo');
        if (fileInfo) {
            fileInfo.innerHTML = `
                <div class="alert alert-info">
                    <i class="fas fa-file-image"></i> ${file.name} (${(file.size / 1024).toFixed(2)} KB)
                </div>
            `;
        }
    }
    
    // Form submission
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const formData = new FormData(form);
        
        if (!formData.get('file').size && !formData.get('text').trim()) {
            UI.showError('Загрузите изображение или введите текст анкеты');
            return;
        }
        
        UI.showLoading(resultsContainer);
        
        try {
            const result = await API.analyzeProfile(formData);
            if (result.success) {
                if (result.extracted_text) {
                    textInput.value = result.extracted_text;
                }
                resultsContainer.innerHTML = result.analysis;
            } else {
                resultsContainer.innerHTML = `
                    <div class="alert alert-danger">
                        <i class="fas fa-exclamation-circle"></i> ${result.error}
                    </div>
                `;
            }
        } catch (error) {
            resultsContainer.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-circle"></i> Ошибка при анализе анкеты
                </div>
            `;
        }
    });
}

// Generate examples
if (document.getElementById('generateExamplesBtn')) {
    const btn = document.getElementById('generateExamplesBtn');
    const contextSelect = document.getElementById('exampleContext');
    const resultsContainer = document.getElementById('examplesResults');
    
    btn.addEventListener('click', async () => {
        const context = contextSelect.value;
        
        btn.disabled = true;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Генерация...';
        UI.showLoading(resultsContainer);
        
        try {
            const result = await API.generateExamples(context);
            if (result.success) {
                resultsContainer.innerHTML = result.examples;
            } else {
                resultsContainer.innerHTML = `
                    <div class="alert alert-danger">
                        <i class="fas fa-exclamation-circle"></i> ${result.error}
                    </div>
                `;
            }
        } catch (error) {
            resultsContainer.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-circle"></i> Ошибка при генерации примеров
                </div>
            `;
        } finally {
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-magic"></i> Сгенерировать примеры';
        }
    });
}

// Grammar check
if (document.getElementById('checkGrammarBtn')) {
    const btn = document.getElementById('checkGrammarBtn');
    const textInput = document.getElementById('grammarText');
    const resultsContainer = document.getElementById('grammarResults');
    
    btn.addEventListener('click', async () => {
        const text = textInput.value.trim();
        
        if (!text) {
            UI.showError('Введите текст для проверки');
            return;
        }
        
        btn.disabled = true;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Проверка...';
        UI.showLoading(resultsContainer);
        
        try {
            const result = await API.checkGrammar(text);
            if (result.success) {
                if (result.corrections.length === 0) {
                    resultsContainer.innerHTML = `
                        <div class="alert alert-success">
                            <i class="fas fa-check-circle"></i> Ошибок не найдено!
                        </div>
                    `;
                } else {
                    let html = '<div class="grammar-results">';
                    html += `<h5>Найдено ошибок: ${result.total}</h5>`;
                    result.corrections.forEach(correction => {
                        html += `
                            <div class="correction-item">
                                <p><strong>Ошибка:</strong> ${correction.message}</p>
                                <p><strong>Варианты исправления:</strong> ${correction.replacements.join(', ')}</p>
                            </div>
                        `;
                    });
                    html += '</div>';
                    resultsContainer.innerHTML = html;
                }
            } else {
                resultsContainer.innerHTML = `
                    <div class="alert alert-warning">
                        <i class="fas fa-info-circle"></i> ${result.message || result.error}
                    </div>
                `;
            }
        } catch (error) {
            resultsContainer.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-circle"></i> Ошибка при проверке грамматики
                </div>
            `;
        } finally {
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-spell-check"></i> Проверить';
        }
    });
}

// ===== Chat Auto-scroll =====
if (document.querySelector('.chat-messages')) {
    const chatMessages = document.querySelector('.chat-messages');
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// ===== Initialize tooltips =====
const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
});
