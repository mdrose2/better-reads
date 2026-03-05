/**
 * Better Reads - Global JavaScript Utilities
 * 
 * This module provides core functionality used across the entire site:
 * - Bootstrap tooltip initialization
 * - Auto-dismissing alerts
 * - Hover effects
 * - Mobile menu enhancements
 * - Back to top button
 * - Card height equalization
 * - Loading states and toast notifications
 */

const BetterReads = {
    // =========================================================================
    // INITIALIZATION
    // =========================================================================
    
    /**
     * Initialize all global features on page load.
     * Called once when DOM is ready.
     */
    init: function() {
        this.initTooltips();
        this.initAutoDismissAlerts();
        this.initHoverEffects();
        this.initMobileMenu();
        this.initBackToTop();
        this.initEqualHeights(); 
        this.initPasswordToggles();
        this.initPasswordFields();
    },
    
    // =========================================================================
    // BOOTSTRAP COMPONENTS
    // =========================================================================
    
    /**
     * Initialize Bootstrap tooltips for elements with data-bs-toggle="tooltip".
     */
    initTooltips: function() {
        const tooltipTriggerList = [].slice.call(
            document.querySelectorAll('[data-bs-toggle="tooltip"]')
        );
        tooltipTriggerList.map(function(tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    },
    
    /**
     * Auto-dismiss alert messages after 5 seconds.
     */
    initAutoDismissAlerts: function() {
        setTimeout(function() {
            document.querySelectorAll('.alert-dismissible').forEach(function(alert) {
                const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
                if (bsAlert) bsAlert.close();
            });
        }, 5000);
    },
    
    // =========================================================================
    // UI ENHANCEMENTS
    // =========================================================================
    
    /**
     * Add hover effects to elements with 'hoverable' class.
     * Applies shadow and lift effect on mouse enter.
     */
    initHoverEffects: function() {
        document.querySelectorAll('.hoverable').forEach(function(el) {
            el.addEventListener('mouseenter', function() {
                this.classList.add('shadow-lg');
                this.style.transform = 'translateY(-5px)';
            });
            el.addEventListener('mouseleave', function() {
                this.classList.remove('shadow-lg');
                this.style.transform = '';
            });
        });
    },
    
    /**
     * Enhance mobile menu with active state toggling.
     */
    initMobileMenu: function() {
        const navbarToggler = document.querySelector('.navbar-toggler');
        if (navbarToggler) {
            navbarToggler.addEventListener('click', function() {
                this.classList.toggle('active');
            });
        }
    },

    /**
     * Show/hide back to top button based on scroll position.
     * Button appears after scrolling 300px down.
     */
    initBackToTop: function() {
        const backToTop = document.getElementById('backToTop');
        if (!backToTop) return;
        
        window.addEventListener('scroll', function() {
            if (window.scrollY > 300) {
                backToTop.style.display = 'block';
            } else {
                backToTop.style.display = 'none';
            }
        });
    },

    /**
     * Equalize heights of cards within a container for consistent layout.
     * Useful for grid layouts where cards should match heights.
     */
    initEqualHeights: function() {
        /**
         * Calculate and set equal heights for all cards in container.
         * @param {HTMLElement} container - Container element holding the cards
         */
        function equalizeCardHeights(container) {
            const cards = container.querySelectorAll('.card');
            let maxHeight = 0;
            
            // Reset heights
            cards.forEach(card => {
                card.style.height = 'auto';
            });
            
            // Find max height
            cards.forEach(card => {
                const height = card.offsetHeight;
                maxHeight = Math.max(maxHeight, height);
            });
            
            // Set all cards to max height
            cards.forEach(card => {
                card.style.height = maxHeight + 'px';
            });
        }
        
        // Target containers
        const featuredContainer = document.querySelector('.featured-books .row');
        const reviewsContainer = document.querySelector('.recent-reviews .row');
        
        // Apply on load
        if (featuredContainer) {
            equalizeCardHeights(featuredContainer);
        }
        
        if (reviewsContainer) {
            equalizeCardHeights(reviewsContainer);
        }
        
        // Re-apply on window resize (debounced)
        let resizeTimer;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimer);
            resizeTimer = setTimeout(() => {
                if (featuredContainer) equalizeCardHeights(featuredContainer);
                if (reviewsContainer) equalizeCardHeights(reviewsContainer);
            }, 250);
        });
    },

        /**
     * Initialize password field enhancements
     * - Clears errors when user types
     * - Handles password toggling
     */
    initPasswordFields: function() {
        // Find all password fields
        document.querySelectorAll('input[type="password"]').forEach(passwordField => {
            
            // Clear errors on input
            passwordField.addEventListener('input', function() {
                this.classList.remove('is-invalid');
                
                // Find and hide any error feedback in the same form group
                const formGroup = this.closest('.mb-3, .form-group');
                if (formGroup) {
                    const errorDiv = formGroup.querySelector('.invalid-feedback, .alert-danger');
                    if (errorDiv) {
                        errorDiv.style.display = 'none';
                        errorDiv.textContent = '';
                    }
                }
            });
            
            // Remove error styling on focus
            passwordField.addEventListener('focus', function() {
                this.classList.remove('is-invalid');
            });
        });
        
        // Also handle Django messages (alerts) auto-dismiss
        this.initAutoDismissAlerts();
    },
    
    /**
     * Initialize password toggle buttons
     */
    initPasswordToggles: function() {
        document.querySelectorAll('[data-password-toggle]').forEach(button => {
            const targetId = button.getAttribute('data-password-toggle');
            const passwordField = document.getElementById(targetId);
            
            if (passwordField) {
                button.addEventListener('click', function() {
                    const type = passwordField.getAttribute('type') === 'password' ? 'text' : 'password';
                    passwordField.setAttribute('type', type);
                    
                    const icon = this.querySelector('i');
                    if (icon) {
                        icon.classList.toggle('bi-eye');
                        icon.classList.toggle('bi-eye-slash');
                    }
                    
                    // Keep focus on the password field after toggling
                    passwordField.focus();
                });
            }
        });
    },
    
    // =========================================================================
    // UTILITY METHODS
    // =========================================================================
    
    /**
     * Show loading spinner on a button and disable it.
     * @param {HTMLElement} button - The button element
     * @param {string} text - Loading text to display (default: 'Loading...')
     */
    showLoading: function(button, text = 'Loading...') {
        if (!button) return;
        button._originalText = button.innerHTML;
        button.disabled = true;
        button.innerHTML = `<span class="spinner-border spinner-border-sm me-2"></span>${text}`;
    },
    
    /**
     * Hide loading spinner and re-enable button.
     * @param {HTMLElement} button - The button element
     */
    hideLoading: function(button) {
        if (!button || !button._originalText) return;
        button.disabled = false;
        button.innerHTML = button._originalText;
    },
    
    /**
     * Show a toast notification message.
     * @param {string} message - Message to display
     * @param {string} type - Bootstrap color type (success, danger, warning, info)
     */
    showToast: function(message, type = 'success') {
        const toastContainer = document.getElementById('toast-container');
        if (!toastContainer) return;
        
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');
        
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        
        toastContainer.appendChild(toast);
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        // Remove from DOM after hiding
        toast.addEventListener('hidden.bs.toast', function() {
            toast.remove();
        });
    }
};

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    BetterReads.init();
});