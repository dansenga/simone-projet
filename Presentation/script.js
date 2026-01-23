/**
 * SIMONE Presentation - JavaScript
 * Navigation et animations pour la présentation
 */

// ==================== ÉTAT DE L'APPLICATION ====================
const state = {
    currentSlide: 1,
    totalSlides: 0,
    isAnimating: false,
    isMenuOpen: false
};

// ==================== ÉLÉMENTS DOM ====================
const elements = {
    slidesContainer: null,
    slides: null,
    progressFill: null,
    currentSlideDisplay: null,
    totalSlidesDisplay: null,
    prevBtn: null,
    nextBtn: null,
    menuToggle: null,
    slideMenu: null,
    closeMenu: null,
    menuList: null,
    slideIndicators: null
};

// ==================== INITIALISATION ====================
document.addEventListener('DOMContentLoaded', () => {
    initElements();
    initSlides();
    initNavigation();
    initKeyboardNavigation();
    initTouchNavigation();
    initMenu();
    initIndicators();
    updateUI();
    
    console.log('🎤 SIMONE Presentation - Prêt !');
    console.log(`📊 ${state.totalSlides} slides chargées`);
});

/**
 * Initialise les références aux éléments DOM
 */
function initElements() {
    elements.slidesContainer = document.getElementById('slidesContainer');
    elements.slides = document.querySelectorAll('.slide');
    elements.progressFill = document.getElementById('progressFill');
    elements.currentSlideDisplay = document.getElementById('currentSlide');
    elements.totalSlidesDisplay = document.getElementById('totalSlides');
    elements.prevBtn = document.getElementById('prevBtn');
    elements.nextBtn = document.getElementById('nextBtn');
    elements.menuToggle = document.getElementById('menuToggle');
    elements.slideMenu = document.getElementById('slideMenu');
    elements.closeMenu = document.getElementById('closeMenu');
    elements.menuList = document.getElementById('menuList');
    elements.slideIndicators = document.getElementById('slideIndicators');
}

/**
 * Initialise les slides
 */
function initSlides() {
    state.totalSlides = elements.slides.length;
    elements.totalSlidesDisplay.textContent = state.totalSlides;
    
    // S'assurer que la première slide est active
    elements.slides.forEach((slide, index) => {
        if (index === 0) {
            slide.classList.add('active');
        } else {
            slide.classList.remove('active');
        }
    });
}

/**
 * Initialise les boutons de navigation
 */
function initNavigation() {
    elements.prevBtn.addEventListener('click', goToPrevSlide);
    elements.nextBtn.addEventListener('click', goToNextSlide);
    
    // Clic sur la slide pour avancer
    elements.slidesContainer.addEventListener('click', (e) => {
        // Ignorer les clics sur les boutons ou liens
        if (e.target.closest('button, a, .nav-controls, .slide-menu')) return;
        goToNextSlide();
    });
}

/**
 * Initialise la navigation au clavier
 */
function initKeyboardNavigation() {
    document.addEventListener('keydown', (e) => {
        switch (e.key) {
            case 'ArrowRight':
            case 'ArrowDown':
            case ' ':
            case 'Enter':
                e.preventDefault();
                goToNextSlide();
                break;
                
            case 'ArrowLeft':
            case 'ArrowUp':
                e.preventDefault();
                goToPrevSlide();
                break;
                
            case 'Home':
                e.preventDefault();
                goToSlide(1);
                break;
                
            case 'End':
                e.preventDefault();
                goToSlide(state.totalSlides);
                break;
                
            case 'f':
            case 'F':
                e.preventDefault();
                toggleFullscreen();
                break;
                
            case 'm':
            case 'M':
                e.preventDefault();
                toggleMenu();
                break;
                
            case 'Escape':
                if (state.isMenuOpen) {
                    toggleMenu();
                }
                break;
        }
    });
}

/**
 * Initialise la navigation tactile (swipe)
 */
function initTouchNavigation() {
    let touchStartX = 0;
    let touchStartY = 0;
    
    elements.slidesContainer.addEventListener('touchstart', (e) => {
        touchStartX = e.touches[0].clientX;
        touchStartY = e.touches[0].clientY;
    }, { passive: true });
    
    elements.slidesContainer.addEventListener('touchend', (e) => {
        const touchEndX = e.changedTouches[0].clientX;
        const touchEndY = e.changedTouches[0].clientY;
        
        const deltaX = touchEndX - touchStartX;
        const deltaY = touchEndY - touchStartY;
        
        // Swipe horizontal
        if (Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > 50) {
            if (deltaX < 0) {
                goToNextSlide();
            } else {
                goToPrevSlide();
            }
        }
    }, { passive: true });
}

/**
 * Initialise le menu des slides
 */
function initMenu() {
    // Générer la liste des slides
    elements.slides.forEach((slide, index) => {
        const title = slide.dataset.title || `Slide ${index + 1}`;
        const li = document.createElement('li');
        li.innerHTML = `
            <span class="num">${index + 1}</span>
            <span>${title}</span>
        `;
        li.addEventListener('click', () => {
            goToSlide(index + 1);
            toggleMenu();
        });
        elements.menuList.appendChild(li);
    });
    
    // Événements du menu
    elements.menuToggle.addEventListener('click', toggleMenu);
    elements.closeMenu.addEventListener('click', toggleMenu);
    
    // Fermer le menu en cliquant à l'extérieur
    document.addEventListener('click', (e) => {
        if (state.isMenuOpen && 
            !elements.slideMenu.contains(e.target) && 
            !elements.menuToggle.contains(e.target)) {
            toggleMenu();
        }
    });
}

/**
 * Initialise les indicateurs de slides
 */
function initIndicators() {
    elements.slides.forEach((slide, index) => {
        const indicator = document.createElement('div');
        indicator.className = 'indicator';
        if (index === 0) indicator.classList.add('active');
        indicator.addEventListener('click', () => goToSlide(index + 1));
        elements.slideIndicators.appendChild(indicator);
    });
}

// ==================== NAVIGATION ====================

/**
 * Aller à la slide suivante
 */
function goToNextSlide() {
    if (state.isAnimating) return;
    
    if (state.currentSlide < state.totalSlides) {
        goToSlide(state.currentSlide + 1);
    }
}

/**
 * Aller à la slide précédente
 */
function goToPrevSlide() {
    if (state.isAnimating) return;
    
    if (state.currentSlide > 1) {
        goToSlide(state.currentSlide - 1);
    }
}

/**
 * Aller à une slide spécifique
 */
function goToSlide(slideNumber) {
    if (state.isAnimating) return;
    if (slideNumber < 1 || slideNumber > state.totalSlides) return;
    if (slideNumber === state.currentSlide) return;
    
    state.isAnimating = true;
    
    // Retirer la classe active de la slide actuelle
    const currentSlideElement = elements.slides[state.currentSlide - 1];
    currentSlideElement.classList.remove('active');
    
    // Mettre à jour l'état
    state.currentSlide = slideNumber;
    
    // Ajouter la classe active à la nouvelle slide
    const newSlideElement = elements.slides[state.currentSlide - 1];
    newSlideElement.classList.add('active');
    
    // Mettre à jour l'interface
    updateUI();
    
    // Animation terminée
    setTimeout(() => {
        state.isAnimating = false;
    }, 600);
    
    // Confetti sur la dernière slide
    if (slideNumber === state.totalSlides) {
        setTimeout(launchConfetti, 800);
    }
}

/**
 * Met à jour l'interface utilisateur
 */
function updateUI() {
    // Compteur de slides
    elements.currentSlideDisplay.textContent = state.currentSlide;
    
    // Barre de progression
    const progress = (state.currentSlide / state.totalSlides) * 100;
    elements.progressFill.style.width = `${progress}%`;
    
    // Boutons de navigation
    elements.prevBtn.disabled = state.currentSlide === 1;
    elements.nextBtn.disabled = state.currentSlide === state.totalSlides;
    elements.prevBtn.style.opacity = state.currentSlide === 1 ? '0.3' : '1';
    elements.nextBtn.style.opacity = state.currentSlide === state.totalSlides ? '0.3' : '1';
    
    // Indicateurs
    const indicators = elements.slideIndicators.querySelectorAll('.indicator');
    indicators.forEach((indicator, index) => {
        indicator.classList.toggle('active', index === state.currentSlide - 1);
    });
    
    // Menu
    const menuItems = elements.menuList.querySelectorAll('li');
    menuItems.forEach((item, index) => {
        item.classList.toggle('active', index === state.currentSlide - 1);
    });
}

// ==================== MENU ====================

/**
 * Ouvre/ferme le menu
 */
function toggleMenu() {
    state.isMenuOpen = !state.isMenuOpen;
    elements.slideMenu.classList.toggle('open', state.isMenuOpen);
}

// ==================== PLEIN ÉCRAN ====================

/**
 * Bascule le mode plein écran
 */
function toggleFullscreen() {
    if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen().catch(err => {
            console.log('Erreur plein écran:', err);
        });
    } else {
        document.exitFullscreen();
    }
}

// ==================== CONFETTI ====================

/**
 * Lance des confettis (dernière slide)
 */
function launchConfetti() {
    const container = document.getElementById('confetti');
    if (!container) return;
    
    const colors = ['#6366F1', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6'];
    
    for (let i = 0; i < 100; i++) {
        setTimeout(() => {
            const confetti = document.createElement('div');
            confetti.style.cssText = `
                position: absolute;
                width: ${Math.random() * 10 + 5}px;
                height: ${Math.random() * 10 + 5}px;
                background: ${colors[Math.floor(Math.random() * colors.length)]};
                left: ${Math.random() * 100}%;
                top: -20px;
                border-radius: ${Math.random() > 0.5 ? '50%' : '0'};
                animation: confetti-fall ${Math.random() * 3 + 2}s linear forwards;
                opacity: ${Math.random() * 0.5 + 0.5};
            `;
            container.appendChild(confetti);
            
            setTimeout(() => confetti.remove(), 5000);
        }, i * 30);
    }
}

// Ajouter l'animation CSS pour les confettis
const style = document.createElement('style');
style.textContent = `
    @keyframes confetti-fall {
        0% {
            transform: translateY(0) rotate(0deg);
            opacity: 1;
        }
        100% {
            transform: translateY(100vh) rotate(720deg);
            opacity: 0;
        }
    }
    
    .confetti-container {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        overflow: hidden;
    }
`;
document.head.appendChild(style);

// ==================== UTILITAIRES ====================

/**
 * Précharge les ressources
 */
function preloadResources() {
    // Les polices sont chargées via CSS
    console.log('📦 Ressources préchargées');
}

// Appeler au chargement
preloadResources();
