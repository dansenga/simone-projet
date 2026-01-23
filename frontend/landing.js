/**
 * SIMONE Landing Page - JavaScript
 * Animations et interactions modernes
 */

document.addEventListener('DOMContentLoaded', () => {
    // Initialisation
    initNavbar();
    initScrollAnimations();
    initDemoSection();
    initSmoothScroll();
    initMobileMenu();
    initTypingEffect();
});

/**
 * Navbar scroll effect
 */
function initNavbar() {
    const navbar = document.querySelector('.navbar');
    
    const handleScroll = () => {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    };
    
    window.addEventListener('scroll', handleScroll);
    handleScroll(); // Check initial state
}

/**
 * Scroll animations avec Intersection Observer
 */
function initScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animated');
                
                // Animate children with stagger
                const children = entry.target.querySelectorAll('.animate-child');
                children.forEach((child, index) => {
                    setTimeout(() => {
                        child.classList.add('animated');
                    }, index * 100);
                });
            }
        });
    }, observerOptions);
    
    // Observe all sections
    document.querySelectorAll('.section-header, .feature-card, .step-card, .language-card, .tech-item').forEach(el => {
        el.classList.add('observe-animate');
        observer.observe(el);
    });
}

/**
 * Demo section interactivity
 */
function initDemoSection() {
    const micBtn = document.querySelector('.demo-mic-btn');
    const waves = document.querySelector('.demo-waves');
    const waveBars = document.querySelectorAll('.demo-waves span');
    const sourcePanel = document.querySelector('.demo-panel .panel-text');
    const targetPanel = document.querySelector('.demo-panel.target .panel-text');
    
    if (!micBtn) return;
    
    let isRecording = false;
    let waveInterval = null;
    
    // Phrases de démonstration
    const demoPhrases = [
        {
            source: "Bonjour, comment allez-vous aujourd'hui?",
            target: "Hello, how are you today?",
            sourceLang: "Français",
            targetLang: "English"
        },
        {
            source: "Je suis développeur et j'adore la technologie",
            target: "I am a developer and I love technology",
            sourceLang: "Français",
            targetLang: "English"
        },
        {
            source: "La traduction en temps réel est incroyable",
            target: "Real-time translation is amazing",
            sourceLang: "Français",
            targetLang: "English"
        }
    ];
    
    let currentPhrase = 0;
    
    micBtn.addEventListener('click', () => {
        isRecording = !isRecording;
        
        if (isRecording) {
            // Start recording
            micBtn.classList.add('recording');
            waves.classList.add('active');
            
            // Animate waves
            waveInterval = setInterval(() => {
                waveBars.forEach(bar => {
                    const height = Math.random() * 20 + 4;
                    bar.style.height = `${height}px`;
                });
            }, 100);
            
            // Simulate transcription
            setTimeout(() => {
                const phrase = demoPhrases[currentPhrase];
                typeText(sourcePanel, phrase.source, 50).then(() => {
                    // Simulate translation delay
                    setTimeout(() => {
                        typeText(targetPanel, phrase.target, 40);
                    }, 300);
                });
                
                currentPhrase = (currentPhrase + 1) % demoPhrases.length;
            }, 500);
            
        } else {
            // Stop recording
            micBtn.classList.remove('recording');
            waves.classList.remove('active');
            
            if (waveInterval) {
                clearInterval(waveInterval);
                waveInterval = null;
            }
            
            // Reset wave heights
            waveBars.forEach(bar => {
                bar.style.height = '8px';
            });
        }
    });
    
    // Demo actions
    document.querySelectorAll('.demo-action').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const action = e.target.closest('.demo-action');
            const icon = action.querySelector('.btn-icon');
            
            if (action.textContent.includes('Export')) {
                // Simulate export
                const originalIcon = icon.textContent;
                icon.textContent = '✓';
                action.style.background = 'var(--secondary)';
                
                setTimeout(() => {
                    icon.textContent = originalIcon;
                    action.style.background = '';
                }, 1500);
            }
        });
    });
    
    // Swap languages button
    const swapBtn = document.querySelector('.swap-btn');
    if (swapBtn) {
        swapBtn.addEventListener('click', () => {
            swapBtn.style.transform = 'rotate(180deg)';
            setTimeout(() => {
                swapBtn.style.transform = '';
            }, 300);
            
            const selects = document.querySelectorAll('.demo-lang-select select');
            if (selects.length >= 2) {
                const temp = selects[0].value;
                selects[0].value = selects[1].value;
                selects[1].value = temp;
            }
        });
    }
}

/**
 * Typing effect for text
 */
async function typeText(element, text, speed = 50) {
    element.textContent = '';
    
    for (let i = 0; i < text.length; i++) {
        element.textContent += text[i];
        await sleep(speed);
    }
}

/**
 * Typing effect for hero title
 */
function initTypingEffect() {
    const heroSubtitle = document.querySelector('.hero-subtitle');
    if (!heroSubtitle) return;
    
    const phrases = [
        "Parlez. Traduisez. Communiquez sans frontières.",
        "La traduction vocale propulsée par l'IA.",
        "Connectez-vous avec le monde entier."
    ];
    
    let phraseIndex = 0;
    
    // After initial page load, cycle through phrases
    setTimeout(() => {
        setInterval(() => {
            phraseIndex = (phraseIndex + 1) % phrases.length;
            heroSubtitle.style.opacity = 0;
            
            setTimeout(() => {
                heroSubtitle.textContent = phrases[phraseIndex];
                heroSubtitle.style.opacity = 1;
            }, 500);
        }, 5000);
    }, 3000);
}

/**
 * Smooth scrolling for anchor links
 */
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            
            if (target) {
                const offset = 80; // Navbar height
                const position = target.offsetTop - offset;
                
                window.scrollTo({
                    top: position,
                    behavior: 'smooth'
                });
            }
        });
    });
}

/**
 * Mobile menu toggle
 */
function initMobileMenu() {
    const toggle = document.querySelector('.nav-toggle');
    const menu = document.querySelector('.nav-menu');
    
    if (!toggle || !menu) return;
    
    toggle.addEventListener('click', () => {
        toggle.classList.toggle('active');
        menu.classList.toggle('active');
        
        // Animate toggle bars
        if (toggle.classList.contains('active')) {
            toggle.children[0].style.transform = 'rotate(45deg) translate(5px, 5px)';
            toggle.children[1].style.opacity = '0';
            toggle.children[2].style.transform = 'rotate(-45deg) translate(5px, -5px)';
        } else {
            toggle.children[0].style.transform = '';
            toggle.children[1].style.opacity = '';
            toggle.children[2].style.transform = '';
        }
    });
    
    // Close menu when clicking a link
    menu.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', () => {
            toggle.classList.remove('active');
            menu.classList.remove('active');
            toggle.children[0].style.transform = '';
            toggle.children[1].style.opacity = '';
            toggle.children[2].style.transform = '';
        });
    });
}

/**
 * Utility: Sleep function for async/await
 */
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Stats counter animation
 */
function animateCounter(element, target, duration = 2000) {
    const start = 0;
    const increment = target / (duration / 16);
    let current = start;
    
    const updateCounter = () => {
        current += increment;
        if (current < target) {
            element.textContent = Math.floor(current);
            requestAnimationFrame(updateCounter);
        } else {
            element.textContent = target;
        }
    };
    
    updateCounter();
}

/**
 * Initialize counters when stats section is visible
 */
const statsObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const statValue = entry.target.querySelector('.stat-value');
            if (statValue && !statValue.classList.contains('counted')) {
                const value = statValue.textContent;
                const numericValue = parseInt(value.replace(/[^0-9]/g, ''));
                
                if (!isNaN(numericValue) && numericValue > 0) {
                    const suffix = value.replace(/[0-9]/g, '');
                    statValue.classList.add('counted');
                    
                    let current = 0;
                    const increment = numericValue / 60;
                    
                    const timer = setInterval(() => {
                        current += increment;
                        if (current >= numericValue) {
                            statValue.textContent = numericValue + suffix;
                            clearInterval(timer);
                        } else {
                            statValue.textContent = Math.floor(current) + suffix;
                        }
                    }, 30);
                }
            }
            statsObserver.unobserve(entry.target);
        }
    });
}, { threshold: 0.5 });

// Observe stats
document.querySelectorAll('.stat-item').forEach(stat => {
    statsObserver.observe(stat);
});

/**
 * Parallax effect for floating elements
 */
document.addEventListener('mousemove', (e) => {
    const floatItems = document.querySelectorAll('.float-item');
    const mouseX = e.clientX / window.innerWidth - 0.5;
    const mouseY = e.clientY / window.innerHeight - 0.5;
    
    floatItems.forEach((item, index) => {
        const speed = (index + 1) * 10;
        const x = mouseX * speed;
        const y = mouseY * speed;
        item.style.transform = `translate(${x}px, ${y}px)`;
    });
});

/**
 * Add CSS for mobile menu
 */
const mobileStyles = document.createElement('style');
mobileStyles.textContent = `
    @media (max-width: 768px) {
        .nav-menu {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(15, 23, 42, 0.98);
            flex-direction: column;
            justify-content: center;
            align-items: center;
            gap: 40px;
            opacity: 0;
            visibility: hidden;
            transition: all 0.3s ease;
        }
        
        .nav-menu.active {
            display: flex;
            opacity: 1;
            visibility: visible;
        }
        
        .nav-menu .nav-link {
            font-size: 1.5rem;
        }
        
        .observe-animate {
            opacity: 0;
            transform: translateY(30px);
            transition: all 0.6s ease;
        }
        
        .observe-animate.animated {
            opacity: 1;
            transform: translateY(0);
        }
    }
`;
document.head.appendChild(mobileStyles);

// Add general animation styles
const animationStyles = document.createElement('style');
animationStyles.textContent = `
    .observe-animate {
        opacity: 0;
        transform: translateY(30px);
        transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .observe-animate.animated {
        opacity: 1;
        transform: translateY(0);
    }
    
    .hero-subtitle {
        transition: opacity 0.5s ease;
    }
    
    .swap-btn {
        transition: transform 0.3s ease;
    }
`;
document.head.appendChild(animationStyles);

console.log('🎙️ SIMONE Landing Page Loaded');
