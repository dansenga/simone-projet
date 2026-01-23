/**
 * SIMONE v2.0 - Application de traduction vocale en temps réel
 * 
 * Ce fichier gère :
 * - La capture audio via Web Audio API
 * - La communication WebSocket avec le serveur
 * - L'interface utilisateur interactive
 * - La synthèse vocale (Text-to-Speech)
 */

// ============== Configuration ==============
const CONFIG = {
    API_BASE: window.location.origin,
    WS_BASE: `ws://${window.location.host}`,
    SAMPLE_RATE: 16000,
    BUFFER_SIZE: 4096,
    MIN_RECORDING_TIME: 2000, // 2 secondes minimum
};

// ============== État de l'application ==============
const state = {
    isRecording: false,
    websocket: null,
    sessionId: null,
    mediaStream: null,
    audioContext: null,
    audioProcessor: null,
    recordingStartTime: null,
    currentTranscription: '',
    currentTranslation: '',
    historyItems: [],
};

// ============== Utilitaires DOM ==============
const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => Array.from(document.querySelectorAll(sel));

// ============== Gestion des Toasts ==============
function showToast(message, type = 'info', duration = 3000) {
    const container = $('#toast-container');
    if (!container) return;
    
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <span class="toast-icon">${type === 'success' ? '✓' : type === 'error' ? '✗' : 'ℹ'}</span>
        <span class="toast-message">${message}</span>
    `;
    container.appendChild(toast);
    
    setTimeout(() => toast.classList.add('show'), 10);
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

// ============== Navigation ==============
function initNavigation() {
    $$('.nav-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const section = link.dataset.section;
            
            // Mettre à jour les liens actifs
            $$('.nav-link').forEach(l => l.classList.remove('active'));
            link.classList.add('active');
            
            // Afficher la section correspondante
            $$('.section').forEach(s => s.classList.remove('active'));
            const sectionEl = $(`#${section}`);
            if (sectionEl) sectionEl.classList.add('active');
            
            // Charger l'historique si nécessaire
            if (section === 'history') {
                loadHistory();
            }
        });
    });
}

// ============== Gestion des Langues ==============
function initLanguageSelectors() {
    const sourceLang = $('#source-lang');
    const targetLang = $('#target-lang');
    const swapBtn = $('#swap-langs');
    const sourceLangDisplay = $('#source-lang-display');
    const targetLangDisplay = $('#target-lang-display');
    
    if (!sourceLang || !targetLang) return;
    
    const langNames = {
        'fr': 'Français',
        'en': 'English',
        'es': 'Español',
        'de': 'Deutsch',
        'it': 'Italiano',
        'pt': 'Português'
    };
    
    function updateLangDisplays() {
        if (sourceLangDisplay) sourceLangDisplay.textContent = langNames[sourceLang.value] || sourceLang.value;
        if (targetLangDisplay) targetLangDisplay.textContent = langNames[targetLang.value] || targetLang.value;
        
        // Envoyer la config au serveur si connecté
        if (state.websocket && state.websocket.readyState === WebSocket.OPEN) {
            state.websocket.send(JSON.stringify({
                type: 'config',
                source: sourceLang.value,
                target: targetLang.value
            }));
        }
    }
    
    sourceLang.addEventListener('change', updateLangDisplays);
    targetLang.addEventListener('change', updateLangDisplays);
    
    if (swapBtn) {
        swapBtn.addEventListener('click', () => {
            const temp = sourceLang.value;
            sourceLang.value = targetLang.value;
            targetLang.value = temp;
            updateLangDisplays();
            showToast('Langues inversées', 'info');
        });
    }
    
    updateLangDisplays();
}

// ============== Génération d'ID de session ==============
function generateSessionId() {
    return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

// ============== Connexion WebSocket ==============
function connectWebSocket() {
    if (state.websocket && state.websocket.readyState === WebSocket.OPEN) {
        return Promise.resolve();
    }
    
    return new Promise((resolve, reject) => {
        state.sessionId = generateSessionId();
        const wsUrl = `${CONFIG.WS_BASE}/ws/realtime/${state.sessionId}`;
        
        console.log('Connexion WebSocket:', wsUrl);
        state.websocket = new WebSocket(wsUrl);
        
        state.websocket.onopen = () => {
            console.log('WebSocket connecté');
            const sourceLang = $('#source-lang');
            const targetLang = $('#target-lang');
            // Envoyer la configuration initiale
            state.websocket.send(JSON.stringify({
                type: 'config',
                source: sourceLang ? sourceLang.value : 'fr',
                target: targetLang ? targetLang.value : 'en'
            }));
            resolve();
        };
        
        state.websocket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            handleWebSocketMessage(data);
        };
        
        state.websocket.onerror = (error) => {
            console.error('Erreur WebSocket:', error);
            showToast('Erreur de connexion au serveur', 'error');
            reject(error);
        };
        
        state.websocket.onclose = () => {
            console.log('WebSocket fermé');
            state.websocket = null;
        };
    });
}

function handleWebSocketMessage(data) {
    console.log('Message reçu:', data);
    
    switch (data.type) {
        case 'status':
            updateStatus(data.message);
            break;
            
        case 'result':
        case 'final':
            displayResult(data);
            if (data.type === 'final') {
                addToHistory(data);
            }
            break;
            
        case 'error':
            showToast(data.message, 'error');
            updateStatus('Erreur');
            break;
    }
}

function displayResult(data) {
    const transcriptionOutput = $('#transcription-output');
    const translationOutput = $('#translation-output');
    
    state.currentTranscription = data.transcription;
    state.currentTranslation = data.translation;
    
    if (transcriptionOutput) transcriptionOutput.innerHTML = `<p class="result-text">${data.transcription}</p>`;
    if (translationOutput) translationOutput.innerHTML = `<p class="result-text">${data.translation}</p>`;
    
    // Activer les boutons d'action
    const speakBtn = $('#speak-translation');
    const copyBtn = $('#copy-translation');
    if (speakBtn) speakBtn.disabled = false;
    if (copyBtn) copyBtn.disabled = false;
    
    showToast('Traduction terminée !', 'success');
}

function updateStatus(message) {
    const statusText = $('.status-text');
    if (statusText) {
        statusText.textContent = message;
    }
}

// ============== Capture Audio ==============
async function initAudioCapture() {
    try {
        // Demander l'accès au microphone
        state.mediaStream = await navigator.mediaDevices.getUserMedia({
            audio: {
                channelCount: 1,
                sampleRate: CONFIG.SAMPLE_RATE,
                echoCancellation: true,
                noiseSuppression: true
            }
        });
        
        // Créer le contexte audio
        state.audioContext = new (window.AudioContext || window.webkitAudioContext)({
            sampleRate: CONFIG.SAMPLE_RATE
        });
        
        // Créer le processeur audio
        const source = state.audioContext.createMediaStreamSource(state.mediaStream);
        state.audioProcessor = state.audioContext.createScriptProcessor(CONFIG.BUFFER_SIZE, 1, 1);
        
        state.audioProcessor.onaudioprocess = (event) => {
            if (!state.isRecording) return;
            
            const inputData = event.inputBuffer.getChannelData(0);
            
            // Convertir en Int16 pour l'envoi
            const pcmData = new Int16Array(inputData.length);
            for (let i = 0; i < inputData.length; i++) {
                pcmData[i] = Math.max(-32768, Math.min(32767, inputData[i] * 32768));
            }
            
            // Envoyer via WebSocket
            if (state.websocket && state.websocket.readyState === WebSocket.OPEN) {
                const base64Data = btoa(String.fromCharCode.apply(null, new Uint8Array(pcmData.buffer)));
                const sourceLang = $('#source-lang');
                const targetLang = $('#target-lang');
                state.websocket.send(JSON.stringify({
                    type: 'audio',
                    data: base64Data,
                    source: sourceLang ? sourceLang.value : 'fr',
                    target: targetLang ? targetLang.value : 'en'
                }));
            }
            
            // Mettre à jour le visualiseur
            updateVisualizer(inputData);
        };
        
        source.connect(state.audioProcessor);
        state.audioProcessor.connect(state.audioContext.destination);
        
        return true;
    } catch (error) {
        console.error('Erreur d\'accès au microphone:', error);
        showToast('Impossible d\'accéder au microphone. Vérifiez les permissions.', 'error');
        return false;
    }
}

function updateVisualizer(audioData) {
    const bars = $$('#audio-visualizer .bar');
    if (!bars.length) return;
    
    const chunkSize = Math.floor(audioData.length / bars.length);
    
    bars.forEach((bar, index) => {
        let sum = 0;
        for (let i = 0; i < chunkSize; i++) {
            sum += Math.abs(audioData[index * chunkSize + i]);
        }
        const average = sum / chunkSize;
        const height = Math.min(100, average * 500);
        bar.style.height = `${Math.max(5, height)}%`;
    });
}

// ============== Contrôle de l'enregistrement ==============
async function startRecording() {
    console.log('Démarrage de l\'enregistrement...');
    
    // Connecter au WebSocket
    try {
        await connectWebSocket();
    } catch (error) {
        showToast('Impossible de se connecter au serveur', 'error');
        return;
    }
    
    // Initialiser la capture audio
    const audioReady = await initAudioCapture();
    if (!audioReady) return;
    
    // Démarrer l'enregistrement
    state.isRecording = true;
    state.recordingStartTime = Date.now();
    
    // Mettre à jour l'UI
    const micButton = $('#mic-button');
    if (micButton) micButton.classList.add('recording');
    const micInstruction = $('#mic-instruction');
    if (micInstruction) micInstruction.textContent = 'Parlez maintenant...';
    const visualizer = $('#audio-visualizer');
    if (visualizer) visualizer.classList.add('active');
    updateStatus('Enregistrement...');
    
    showToast('Enregistrement démarré', 'info');
}

async function stopRecording() {
    console.log('Arrêt de l\'enregistrement...');
    
    const recordingDuration = Date.now() - state.recordingStartTime;
    
    // Vérifier la durée minimale
    if (recordingDuration < CONFIG.MIN_RECORDING_TIME) {
        showToast(`Parlez au moins ${CONFIG.MIN_RECORDING_TIME / 1000} secondes`, 'error');
        return;
    }
    
    state.isRecording = false;
    
    // Mettre à jour l'UI
    const micButton = $('#mic-button');
    if (micButton) micButton.classList.remove('recording');
    const micInstruction = $('#mic-instruction');
    if (micInstruction) micInstruction.textContent = 'Traitement en cours...';
    const visualizer = $('#audio-visualizer');
    if (visualizer) visualizer.classList.remove('active');
    updateStatus('Traitement...');
    
    // Demander le traitement
    if (state.websocket && state.websocket.readyState === WebSocket.OPEN) {
        state.websocket.send(JSON.stringify({ type: 'process' }));
    }
    
    // Arrêter le flux audio
    if (state.mediaStream) {
        state.mediaStream.getTracks().forEach(track => track.stop());
        state.mediaStream = null;
    }
    
    // Fermer le contexte audio
    if (state.audioContext) {
        state.audioContext.close();
        state.audioContext = null;
    }
    
    setTimeout(() => {
        if (micInstruction) micInstruction.textContent = 'Appuyez pour parler';
    }, 3000);
}

function initMicButton() {
    const micButton = $('#mic-button');
    if (!micButton) return;
    
    micButton.addEventListener('click', async () => {
        if (state.isRecording) {
            await stopRecording();
        } else {
            await startRecording();
        }
    });
}

// ============== Traduction de texte manuel ==============
function initManualTranslation() {
    const translateBtn = $('#translate-text');
    const manualText = $('#manual-text');
    
    if (!translateBtn || !manualText) return;
    
    translateBtn.addEventListener('click', async () => {
        const text = manualText.value.trim();
        if (!text) {
            showToast('Veuillez entrer du texte à traduire', 'error');
            return;
        }
        
        translateBtn.disabled = true;
        translateBtn.textContent = 'Traduction...';
        
        try {
            const sourceLang = $('#source-lang');
            const targetLang = $('#target-lang');
            
            const response = await fetch(`${CONFIG.API_BASE}/api/translate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    text: text,
                    source_lang: sourceLang ? sourceLang.value : 'fr',
                    target_lang: targetLang ? targetLang.value : 'en'
                })
            });
            
            if (!response.ok) throw new Error('Erreur de traduction');
            
            const data = await response.json();
            
            const transcriptionOutput = $('#transcription-output');
            const translationOutput = $('#translation-output');
            if (transcriptionOutput) transcriptionOutput.innerHTML = `<p class="result-text">${data.original_text}</p>`;
            if (translationOutput) translationOutput.innerHTML = `<p class="result-text">${data.translated_text}</p>`;
            
            state.currentTranscription = data.original_text;
            state.currentTranslation = data.translated_text;
            
            const speakBtn = $('#speak-translation');
            const copyBtn = $('#copy-translation');
            if (speakBtn) speakBtn.disabled = false;
            if (copyBtn) copyBtn.disabled = false;
            
            showToast('Traduction terminée !', 'success');
        } catch (error) {
            console.error('Erreur:', error);
            showToast('Erreur lors de la traduction', 'error');
        } finally {
            translateBtn.disabled = false;
            translateBtn.innerHTML = `
                Traduire
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <line x1="5" y1="12" x2="19" y2="12"/>
                    <polyline points="12 5 19 12 12 19"/>
                </svg>
            `;
        }
    });
}

// ============== Synthèse vocale (TTS) ==============
function initTextToSpeech() {
    const speakBtn = $('#speak-translation');
    if (!speakBtn) return;
    
    speakBtn.addEventListener('click', () => {
        if (!state.currentTranslation) return;
        
        // Utiliser l'API Web Speech
        const utterance = new SpeechSynthesisUtterance(state.currentTranslation);
        const targetLang = $('#target-lang');
        utterance.lang = targetLang ? targetLang.value : 'en';
        utterance.rate = 0.9;
        
        utterance.onstart = () => {
            speakBtn.classList.add('speaking');
        };
        
        utterance.onend = () => {
            speakBtn.classList.remove('speaking');
        };
        
        speechSynthesis.speak(utterance);
    });
}

// ============== Copie dans le presse-papier ==============
function initCopyButton() {
    const copyBtn = $('#copy-translation');
    if (!copyBtn) return;
    
    copyBtn.addEventListener('click', async () => {
        if (!state.currentTranslation) return;
        
        try {
            await navigator.clipboard.writeText(state.currentTranslation);
            showToast('Texte copié !', 'success');
        } catch (error) {
            // Fallback pour les navigateurs plus anciens
            const textarea = document.createElement('textarea');
            textarea.value = state.currentTranslation;
            document.body.appendChild(textarea);
            textarea.select();
            document.execCommand('copy');
            document.body.removeChild(textarea);
            showToast('Texte copié !', 'success');
        }
    });
}

// ============== Historique ==============
async function loadHistory() {
    const historyList = $('#history-list');
    if (!historyList) return;
    
    historyList.innerHTML = '<p class="loading">Chargement...</p>';
    
    try {
        const response = await fetch(`${CONFIG.API_BASE}/api/history`);
        if (!response.ok) throw new Error('Erreur de chargement');
        
        const items = await response.json();
        
        if (items.length === 0) {
            historyList.innerHTML = '<p class="placeholder">Aucune traduction enregistrée</p>';
            return;
        }
        
        historyList.innerHTML = items.map(item => `
            <div class="history-item" data-id="${item.id}">
                <div class="history-item-header">
                    <span class="history-id">#${item.id}</span>
                    <span class="history-date">${item.timestamp}</span>
                </div>
                <div class="history-item-content">
                    <span class="history-lang">${item.detected_lang || '?'}</span>
                    <span class="history-path">${item.audio_path || 'Texte manuel'}</span>
                </div>
                <div class="history-item-actions">
                    ${item.has_pdf ? '<button class="btn-small" data-format="pdf">PDF</button>' : ''}
                    ${item.has_docx ? '<button class="btn-small" data-format="docx">DOCX</button>' : ''}
                </div>
            </div>
        `).join('');
        
    } catch (error) {
        console.error('Erreur:', error);
        historyList.innerHTML = '<p class="error">Erreur lors du chargement</p>';
    }
}

function addToHistory(data) {
    state.historyItems.unshift({
        id: Date.now(),
        timestamp: new Date().toLocaleString(),
        transcription: data.transcription,
        translation: data.translation,
        source_lang: data.source_lang,
        target_lang: data.target_lang
    });
}

// ============== Initialisation ==============
document.addEventListener('DOMContentLoaded', () => {
    console.log('SIMONE v2.0 - Initialisation...');
    
    initNavigation();
    initLanguageSelectors();
    initMicButton();
    initManualTranslation();
    initTextToSpeech();
    initCopyButton();
    
    // Vérifier le support du navigateur
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        showToast('Votre navigateur ne supporte pas l\'enregistrement audio', 'error');
        const micButton = $('#mic-button');
        if (micButton) micButton.disabled = true;
    }
    
    console.log('SIMONE v2.0 - Prêt !');
});
