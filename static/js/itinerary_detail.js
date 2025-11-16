/**
 * Module: itinerary_detail.js
 * Purpose: Client-side functionality for itinerary detail page
 * 
 * This module handles all interactive features on the itinerary detail page
 * including sharing, saving, and UI enhancements.
 * 
 * Author: SafariSmart Kenya Team
 * Date: 2025-11-16
 */

/**
 * ShareManager class
 * Handles all sharing-related functionality
 */
class ShareManager {
    /**
     * Initialize ShareManager
     * @param {Object} shareData - Share data from server
     */
    constructor(shareData) {
        this.shareData = shareData;
        this.notificationManager = new NotificationManager();
    }
    
    /**
     * Share itinerary using native share API or fallback
     */
    async share() {
        const { title, text, url } = this.shareData;
        
        // Try native share API (mobile)
        if (navigator.share) {
            try {
                await navigator.share({ title, text, url });
                this.notificationManager.show('Shared successfully!', 'success');
                this._trackShare('native');
            } catch (error) {
                // User cancelled or error occurred
                if (error.name !== 'AbortError') {
                    this._fallbackToCopy(url);
                }
            }
        } else {
            // Fallback to copy (desktop)
            this._fallbackToCopy(url);
        }
    }
    
    /**
     * Fallback to copying URL to clipboard
     * @param {string} url - URL to copy
     * @private
     */
    _fallbackToCopy(url) {
        this._copyToClipboard(url);
    }
    
    /**
     * Copy text to clipboard
     * @param {string} text - Text to copy
     * @private
     */
    async _copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
            this.notificationManager.show('Link copied to clipboard! 📋', 'success');
            this._trackShare('clipboard');
        } catch (error) {
            // Fallback for older browsers
            this._legacyCopy(text);
        }
    }
    
    /**
     * Legacy copy method for older browsers
     * @param {string} text - Text to copy
     * @private
     */
    _legacyCopy(text) {
        const textarea = document.createElement('textarea');
        textarea.value = text;
        textarea.style.position = 'fixed';
        textarea.style.opacity = '0';
        document.body.appendChild(textarea);
        textarea.select();
        
        try {
            document.execCommand('copy');
            this.notificationManager.show('Link copied! 📋', 'success');
            this._trackShare('clipboard-legacy');
        } catch (error) {
            this.notificationManager.show('Failed to copy link', 'error');
        } finally {
            document.body.removeChild(textarea);
        }
    }
    
    /**
     * Track share event
     * @param {string} method - Share method used
     * @private
     */
    _trackShare(method) {
        console.log(`Share tracked: ${method}`);
        // Future: Send to analytics
    }
}

/**
 * SaveManager class
 * Handles itinerary save functionality
 */
class SaveManager {
    /**
     * Initialize SaveManager
     * @param {boolean} isAuthenticated - Whether user is logged in
     * @param {string} loginUrl - URL for login page
     */
    constructor(isAuthenticated, loginUrl) {
        this.isAuthenticated = isAuthenticated;
        this.loginUrl = loginUrl;
        this.notificationManager = new NotificationManager();
    }
    
    /**
     * Save itinerary
     */
    save() {
        if (!this.isAuthenticated) {
            this.notificationManager.show(
                'Please login to save itineraries',
                'info'
            );
            setTimeout(() => {
                window.location.href = this.loginUrl;
            }, 1500);
            return;
        }
        
        // TODO: Implement actual save functionality
        this.notificationManager.show('Itinerary saved! ✓', 'success');
    }
}

/**
 * NotificationManager class
 * Handles toast notifications
 */
class NotificationManager {
    /**
     * Show notification toast
     * @param {string} message - Message to display
     * @param {string} type - Notification type (success, info, error)
     */
    show(message, type = 'info') {
        const toast = this._createToast(message, type);
        document.body.appendChild(toast);
        
        // Trigger animation
        setTimeout(() => toast.classList.add('show'), 10);
        
        // Auto-remove after 3 seconds
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
    
    /**
     * Create toast element
     * @param {string} message - Message text
     * @param {string} type - Toast type
     * @returns {HTMLElement} Toast element
     * @private
     */
    _createToast(message, type) {
        const toast = document.createElement('div');
        toast.className = `toast-notification toast-${type}`;
        toast.textContent = message;
        
        const colors = {
            success: '#28a745',
            info: '#17a2b8',
            error: '#dc3545',
            warning: '#ffc107'
        };
        
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${colors[type] || colors.info};
            color: white;
            padding: 15px 25px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 9999;
            font-weight: 500;
            transform: translateX(400px);
            opacity: 0;
            transition: all 0.3s ease-out;
        `;
        
        return toast;
    }
}

/**
 * ScrollManager class
 * Handles scroll-related functionality
 */
class ScrollManager {
    /**
     * Initialize ScrollManager
     * @param {HTMLElement} backToTopButton - Back to top button element
     */
    constructor(backToTopButton) {
        this.button = backToTopButton;
        this.threshold = 300;
        this._init();
    }
    
    /**
     * Initialize scroll listener
     * @private
     */
    _init() {
        window.addEventListener('scroll', () => this._handleScroll());
    }
    
    /**
     * Handle scroll event
     * @private
     */
    _handleScroll() {
        if (window.pageYOffset > this.threshold) {
            this.button.style.display = 'flex';
        } else {
            this.button.style.display = 'none';
        }
    }
    
    /**
     * Scroll to top smoothly
     */
    scrollToTop() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    }
}

/**
 * ItineraryDetailApp class
 * Main application controller
 */
class ItineraryDetailApp {
    /**
     * Initialize application
     * @param {Object} config - Configuration object
     */
    constructor(config) {
        this.config = config;
        this.shareManager = new ShareManager(config.shareData);
        this.saveManager = new SaveManager(
            config.isAuthenticated,
            config.loginUrl
        );
        this.scrollManager = null;
        
        this._init();
    }
    
    /**
     * Initialize application
     * @private
     */
    _init() {
        // Initialize scroll manager
        const backToTopButton = document.getElementById('backToTop');
        if (backToTopButton) {
            this.scrollManager = new ScrollManager(backToTopButton);
            backToTopButton.addEventListener('click', () => {
                this.scrollManager.scrollToTop();
            });
        }
        
        // Add print styles
        this._addPrintStyles();
    }
    
    /**
     * Handle share button click
     */
    handleShare() {
        this.shareManager.share();
    }
    
    /**
     * Handle save button click
     */
    handleSave() {
        this.saveManager.save();
    }
    
    /**
     * Add print-specific styles
     * @private
     */
    _addPrintStyles() {
        const style = document.createElement('style');
        style.textContent = `
            @media print {
                .action-buttons,
                .card:has(.bi-map),
                button,
                .badge-ai,
                .badge-template,
                #backToTop {
                    display: none !important;
                }
                
                .itinerary-header {
                    background: white !important;
                    color: black !important;
                    padding: 20px 0 !important;
                }
                
                .itinerary-content {
                    box-shadow: none !important;
                    border: 1px solid #ddd;
                }
            }
        `;
        document.head.appendChild(style);
    }
}

// Export for use in templates
window.ItineraryDetailApp = ItineraryDetailApp;
