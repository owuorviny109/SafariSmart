/**
 * Animation Controller
 * Centralized animation management with accessibility support
 */

(function() {
  'use strict';

  // Check for reduced motion preference
  const prefersReducedMotion = window.matchMedia && 
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Animation Controller Class
  class AnimationController {
    constructor() {
      this.initialized = false;
      this.observers = new Map();
      
      if (!prefersReducedMotion) {
        this.init();
      }
    }

    init() {
      if (this.initialized) return;
      
      // Initialize AOS if available and motion is allowed
      if (typeof AOS !== 'undefined') {
        AOS.init({
          duration: 800,
          easing: 'ease-out',
          once: true,
          offset: 100,
          disable: prefersReducedMotion
        });
      }

      // Initialize declarative animations
      this.initDeclarativeAnimations();
      
      // Initialize navbar scroll effect
      this.initNavbarScrollEffect();
      
      // Initialize smooth scroll
      this.initSmoothScroll();
      
      this.initialized = true;
    }

    initDeclarativeAnimations() {
      // Simple declarative reveal animations
      const revealElements = document.querySelectorAll('[data-reveal]');
      
      if (revealElements.length === 0) return;

      const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            entry.target.classList.add('is-inview');
            observer.unobserve(entry.target);
          }
        });
      }, {
        threshold: 0.15,
        rootMargin: '0px 0px -50px 0px'
      });

      revealElements.forEach(el => {
        observer.observe(el);
      });

      this.observers.set('reveal', observer);
    }

    initNavbarScrollEffect() {
      const navbar = document.getElementById('mainNavbar');
      if (!navbar) return;

      let ticking = false;

      const updateNavbar = () => {
        if (window.scrollY > 50) {
          navbar.classList.add('scrolled');
        } else {
          navbar.classList.remove('scrolled');
        }
        ticking = false;
      };

      const onScroll = () => {
        if (!ticking) {
          requestAnimationFrame(updateNavbar);
          ticking = true;
        }
      };

      window.addEventListener('scroll', onScroll, { passive: true });
    }

    initSmoothScroll() {
      // Only enable smooth scroll if motion is not reduced
      if (prefersReducedMotion) return;

      document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
          const href = this.getAttribute('href');
          if (href === '#') return;
          
          const target = document.querySelector(href);
          if (target) {
            e.preventDefault();
            target.scrollIntoView({
              behavior: 'smooth',
              block: 'start'
            });
          }
        });
      });
    }

    // Method to safely add animations after page load
    addAnimation(element, animationType, options = {}) {
      if (prefersReducedMotion) return;
      
      // Add animation logic here for dynamic content
      element.setAttribute('data-reveal', animationType);
      
      // Re-initialize observer for new elements
      const observer = this.observers.get('reveal');
      if (observer) {
        observer.observe(element);
      }
    }

    // Cleanup method
    destroy() {
      this.observers.forEach(observer => observer.disconnect());
      this.observers.clear();
      this.initialized = false;
    }
  }

  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      window.AnimationController = new AnimationController();
    });
  } else {
    window.AnimationController = new AnimationController();
  }

  // Handle dynamic preference changes
  if (window.matchMedia) {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    mediaQuery.addEventListener('change', (e) => {
      if (e.matches && window.AnimationController) {
        // User enabled reduced motion
        window.AnimationController.destroy();
      } else if (!e.matches && !window.AnimationController.initialized) {
        // User disabled reduced motion
        window.AnimationController.init();
      }
    });
  }

})();