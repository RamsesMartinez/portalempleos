// Portal Empleos - JavaScript Functionality

document.addEventListener('DOMContentLoaded', function() {
    // Mobile navbar toggle
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    
    if (navbarToggler && navbarCollapse) {
        navbarToggler.addEventListener('click', function() {
            navbarCollapse.classList.toggle('show');
        });
        
        // Close navbar when clicking outside
        document.addEventListener('click', function(event) {
            if (!navbarToggler.contains(event.target) && !navbarCollapse.contains(event.target)) {
                navbarCollapse.classList.remove('show');
            }
        });
    }
    
    // Smooth scrolling for anchor links
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
                
                // Close mobile navbar if open
                if (navbarCollapse) {
                    navbarCollapse.classList.remove('show');
                }
            }
        });
    });
    
    // Intersection Observer for fade-in animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);
    
    // Observe all fade-in elements
    const fadeElements = document.querySelectorAll('.fade-in');
    fadeElements.forEach(element => {
        observer.observe(element);
    });
    
    // Progress bar animation on scroll
    const progressBar = document.querySelector('.progress-fill');
    if (progressBar) {
        const progressObserver = new IntersectionObserver(function(entries) {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    progressBar.style.width = '65%';
                }
            });
        }, { threshold: 0.5 });
        
        const progressSection = document.querySelector('#progress');
        if (progressSection) {
            progressObserver.observe(progressSection);
        }
    }
    
    // Add loading animation to buttons
    const buttons = document.querySelectorAll('.btn-primary, .btn-secondary');
    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            // Add loading state
            const originalText = this.textContent;
            this.textContent = 'Cargando...';
            this.style.pointerEvents = 'none';
            
            // Simulate loading (remove this in production)
            setTimeout(() => {
                this.textContent = originalText;
                this.style.pointerEvents = 'auto';
            }, 1000);
        });
    });
});

// Utility function for smooth scrolling
function smoothScrollTo(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
}
