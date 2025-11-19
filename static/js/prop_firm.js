gsap.registerPlugin(ScrollTrigger);

document.addEventListener('DOMContentLoaded', () => {
    initNavbar();
    initMobileMenu();
    initScrollAnimations();
    initCounters();
    initCookieConsent();
    initVideoModal();
    initParallax();
    initFloatingElements();
});

function initNavbar() {
    const navbar = document.getElementById('navbar');
    let lastScroll = 0;

    window.addEventListener('scroll', () => {
        const currentScroll = window.pageYOffset;

        if (currentScroll > 100) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }

        lastScroll = currentScroll;
    });

    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            if (href === '#') return;
            
            e.preventDefault();
            const target = document.querySelector(href);
            if (target) {
                const offset = 80;
                const targetPosition = target.offsetTop - offset;
                
                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });

                const mobileMenu = document.getElementById('navMenu');
                const menuToggle = document.getElementById('mobileMenuToggle');
                mobileMenu.classList.remove('active');
                menuToggle.classList.remove('active');
            }
        });
    });
}

function initMobileMenu() {
    const menuToggle = document.getElementById('mobileMenuToggle');
    const navMenu = document.getElementById('navMenu');

    menuToggle.addEventListener('click', () => {
        menuToggle.classList.toggle('active');
        navMenu.classList.toggle('active');
    });

    document.addEventListener('click', (e) => {
        if (!navMenu.contains(e.target) && !menuToggle.contains(e.target)) {
            navMenu.classList.remove('active');
            menuToggle.classList.remove('active');
        }
    });
}

function initScrollAnimations() {
    gsap.from('.hero-content', {
        opacity: 0,
        y: 50,
        duration: 1,
        ease: 'power3.out'
    });

    const fadeUpElements = document.querySelectorAll('.glass-card, .stat-item, .section-title, .section-subtitle');
    fadeUpElements.forEach((element, index) => {
        gsap.from(element, {
            scrollTrigger: {
                trigger: element,
                start: 'top 85%',
                end: 'bottom 20%',
                toggleActions: 'play none none reverse'
            },
            opacity: 0,
            y: 50,
            duration: 0.8,
            delay: index * 0.1,
            ease: 'power3.out'
        });
    });

    gsap.to('.scroll-indicator', {
        scrollTrigger: {
            trigger: '.hero',
            start: 'top top',
            end: 'bottom top',
            scrub: true
        },
        opacity: 0,
        y: -50
    });

    const stepCards = document.querySelectorAll('.step-card');
    stepCards.forEach((card, index) => {
        gsap.from(card, {
            scrollTrigger: {
                trigger: card,
                start: 'top 80%',
                toggleActions: 'play none none reverse'
            },
            opacity: 0,
            y: 60,
            rotation: 5,
            duration: 0.8,
            delay: index * 0.2,
            ease: 'back.out(1.7)'
        });
    });

    const programCards = document.querySelectorAll('.program-card');
    programCards.forEach((card, index) => {
        gsap.from(card, {
            scrollTrigger: {
                trigger: card,
                start: 'top 80%',
                toggleActions: 'play none none reverse'
            },
            opacity: 0,
            scale: 0.9,
            y: 40,
            duration: 0.8,
            delay: index * 0.15,
            ease: 'power3.out'
        });

        card.addEventListener('mouseenter', () => {
            gsap.to(card, {
                scale: 1.05,
                duration: 0.3,
                ease: 'power2.out'
            });
        });

        card.addEventListener('mouseleave', () => {
            gsap.to(card, {
                scale: 1,
                duration: 0.3,
                ease: 'power2.out'
            });
        });
    });
}

function initCounters() {
    const counters = document.querySelectorAll('.stat-number');
    
    counters.forEach(counter => {
        const target = counter.dataset.target || counter.querySelector('[data-target]')?.dataset.target;
        if (!target) return;

        const targetValue = parseInt(target);
        let hasAnimated = false;

        ScrollTrigger.create({
            trigger: counter,
            start: 'top 80%',
            onEnter: () => {
                if (!hasAnimated) {
                    animateCounter(counter, targetValue);
                    hasAnimated = true;
                }
            }
        });
    });
}

function animateCounter(element, target) {
    let current = 0;
    const increment = target / 100;
    const duration = 2000;
    const stepTime = duration / 100;

    const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
            current = target;
            clearInterval(timer);
        }
        
        const span = element.querySelector('[data-target]');
        if (span) {
            span.textContent = Math.floor(current);
        } else {
            element.childNodes.forEach(node => {
                if (node.nodeType === 3) {
                    node.textContent = Math.floor(current);
                }
            });
        }
    }, stepTime);
}

function initCookieConsent() {
    const cookieConsent = document.getElementById('cookieConsent');
    const acceptBtn = document.getElementById('acceptCookies');
    const declineBtn = document.getElementById('declineCookies');

    const cookieChoice = localStorage.getItem('cookieConsent');
    
    if (!cookieChoice) {
        setTimeout(() => {
            cookieConsent.classList.add('show');
        }, 2000);
    }

    acceptBtn.addEventListener('click', () => {
        localStorage.setItem('cookieConsent', 'accepted');
        cookieConsent.classList.remove('show');
        
        gsap.to(cookieConsent, {
            opacity: 0,
            y: 50,
            duration: 0.5,
            onComplete: () => {
                cookieConsent.style.display = 'none';
            }
        });
    });

    declineBtn.addEventListener('click', () => {
        localStorage.setItem('cookieConsent', 'declined');
        cookieConsent.classList.remove('show');
        
        gsap.to(cookieConsent, {
            opacity: 0,
            y: 50,
            duration: 0.5,
            onComplete: () => {
                cookieConsent.style.display = 'none';
            }
        });
    });
}

function initVideoModal() {
    const playButton = document.getElementById('playButton');
    const videoModal = document.getElementById('videoModal');
    const modalClose = document.getElementById('modalClose');

    playButton.addEventListener('click', () => {
        videoModal.classList.add('active');
        document.body.style.overflow = 'hidden';
    });

    modalClose.addEventListener('click', closeModal);
    
    videoModal.addEventListener('click', (e) => {
        if (e.target === videoModal) {
            closeModal();
        }
    });

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && videoModal.classList.contains('active')) {
            closeModal();
        }
    });

    function closeModal() {
        videoModal.classList.remove('active');
        document.body.style.overflow = '';
        
        const iframe = videoModal.querySelector('iframe');
        const iframeSrc = iframe.src;
        iframe.src = iframeSrc;
    }
}

function initParallax() {
    const heroBackground = document.querySelector('.hero-background');
    
    window.addEventListener('mousemove', (e) => {
        const mouseX = e.clientX / window.innerWidth;
        const mouseY = e.clientY / window.innerHeight;
        
        gsap.to('.floating-element', {
            x: (i, el) => {
                const speed = el.dataset.speed || 1;
                return (mouseX - 0.5) * 50 * speed;
            },
            y: (i, el) => {
                const speed = el.dataset.speed || 1;
                return (mouseY - 0.5) * 50 * speed;
            },
            duration: 1,
            ease: 'power2.out'
        });
    });

    window.addEventListener('scroll', () => {
        const scrolled = window.pageYOffset;
        const parallaxElements = document.querySelectorAll('.floating-element');
        
        parallaxElements.forEach((element) => {
            const speed = element.dataset.speed || 1;
            const yPos = -(scrolled * speed * 0.1);
            element.style.transform = `translateY(${yPos}px)`;
        });
    });
}

function initFloatingElements() {
    const heroCTA = document.querySelectorAll('.btn-hero');
    
    heroCTA.forEach((btn, index) => {
        gsap.to(btn, {
            y: -10,
            duration: 2,
            repeat: -1,
            yoyo: true,
            ease: 'power1.inOut',
            delay: index * 0.2
        });
    });

    const glassCards = document.querySelectorAll('.glass-card');
    glassCards.forEach((card) => {
        card.addEventListener('mouseenter', (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            gsap.to(card, {
                '--mouse-x': `${x}px`,
                '--mouse-y': `${y}px`,
                duration: 0.3
            });
        });

        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = ((e.clientX - rect.left) / rect.width) * 100;
            const y = ((e.clientY - rect.top) / rect.height) * 100;
            
            card.style.background = `
                radial-gradient(circle at ${x}% ${y}%, rgba(0, 255, 136, 0.1) 0%, transparent 50%),
                rgba(255, 255, 255, 0.05)
            `;
        });

        card.addEventListener('mouseleave', () => {
            card.style.background = '';
        });
    });

    gsap.to('.step-icon', {
        rotation: 360,
        duration: 20,
        repeat: -1,
        ease: 'none'
    });

    const socialIcons = document.querySelectorAll('.social-icon, .social-fixed-icon');
    socialIcons.forEach((icon, index) => {
        gsap.to(icon, {
            y: -5,
            duration: 1.5,
            repeat: -1,
            yoyo: true,
            ease: 'power1.inOut',
            delay: index * 0.1
        });
    });
}

window.addEventListener('load', () => {
    gsap.from('body', {
        opacity: 0,
        duration: 0.5,
        ease: 'power2.out'
    });
});

if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    gsap.globalTimeline.timeScale(0);
    ScrollTrigger.refresh();
}
