/* ============================================
   Base64URL Conversion Helpers
   ============================================ */

/**
 * Convert base64url string to Uint8Array
 * Used for WebAuthn credential handling
 */
function base64urlToUint8Array(base64url) {
    if (base64url === undefined || base64url === null) {
        throw new Error('base64url value is undefined or null');
    }
    
    // If it's already a Uint8Array, return it
    if (base64url instanceof Uint8Array) {
        return base64url;
    }
    
    // If it's an array, convert to Uint8Array
    if (Array.isArray(base64url)) {
        return new Uint8Array(base64url);
    }
    
    // Convert to string if it's not already
    const str = String(base64url);
    
    if (!str || str.length === 0) {
        throw new Error('base64url string is empty');
    }
    
    // Convert base64url to base64
    let base64 = str.replace(/-/g, '+').replace(/_/g, '/');
    // Add padding if needed
    while (base64.length % 4) {
        base64 += '=';
    }
    // Decode base64
    const binaryString = atob(base64);
    const bytes = new Uint8Array(binaryString.length);
    for (let i = 0; i < binaryString.length; i++) {
        bytes[i] = binaryString.charCodeAt(i);
    }
    return bytes;
}

/**
 * Convert Uint8Array to base64url string
 * Used for WebAuthn credential handling
 */
function uint8ArrayToBase64url(bytes) {
    let binary = '';
    for (let i = 0; i < bytes.length; i++) {
        binary += String.fromCharCode(bytes[i]);
    }
    let base64 = btoa(binary);
    // Convert base64 to base64url
    return base64.replace(/\+/g, '-').replace(/\//g, '_').replace(/=/g, '');
}

/* ============================================
   Message Display Helpers
   ============================================ */

/**
 * Show error message
 * Handles both 'show' class approach and 'hidden' class with display style
 */
function showError(message) {
    const errorEl = document.getElementById('error');
    if (errorEl) {
        errorEl.textContent = message;
        // Try 'show' class first (for elements using class-based visibility)
        if (errorEl.classList) {
            errorEl.classList.add('show');
            errorEl.classList.remove('hidden');
        }
        // Also set display style (for elements using style-based visibility)
        errorEl.style.display = 'block';
        
        const successEl = document.getElementById('success');
        if (successEl) {
            if (successEl.classList) {
                successEl.classList.remove('show');
                successEl.classList.add('hidden');
            }
            successEl.style.display = 'none';
        }
    }
}

/**
 * Show success message
 * Handles both 'show' class approach and 'hidden' class with display style
 */
function showSuccess(message) {
    const successEl = document.getElementById('success');
    if (successEl) {
        successEl.textContent = message;
        // Try 'show' class first (for elements using class-based visibility)
        if (successEl.classList) {
            successEl.classList.add('show');
            successEl.classList.remove('hidden');
        }
        // Also set display style (for elements using style-based visibility)
        successEl.style.display = 'block';
        
        const errorEl = document.getElementById('error');
        if (errorEl) {
            if (errorEl.classList) {
                errorEl.classList.remove('show');
                errorEl.classList.add('hidden');
            }
            errorEl.style.display = 'none';
        }
    }
}

/**
 * Hide all messages
 * Handles both 'show' class approach and 'hidden' class with display style
 */
function hideMessage() {
    const errorEl = document.getElementById('error');
    const successEl = document.getElementById('success');
    if (errorEl) {
        if (errorEl.classList) {
            errorEl.classList.remove('show');
            errorEl.classList.add('hidden');
        }
        errorEl.style.display = 'none';
    }
    if (successEl) {
        if (successEl.classList) {
            successEl.classList.remove('show');
            successEl.classList.add('hidden');
        }
        successEl.style.display = 'none';
    }
}

/* ============================================
   Theme Management
   ============================================ */
/**
 * Load theme based on browser preferences
 * Uses prefers-color-scheme media query to respect system settings
 */
function loadTheme() {
    // Check if user has a saved preference (for backwards compatibility)
    const savedTheme = localStorage.getItem('theme');
    
    if (savedTheme) {
        // If there's a saved theme, use it (but we'll respect browser preference going forward)
        document.documentElement.setAttribute('data-theme', savedTheme);
        // Clear the saved theme so browser preference takes over next time
        localStorage.removeItem('theme');
    } else {
        // Use browser preference
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        const theme = prefersDark ? 'dark' : 'light';
        document.documentElement.setAttribute('data-theme', theme);
    }
    
    // Listen for changes to browser preference
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    mediaQuery.addEventListener('change', (e) => {
        const theme = e.matches ? 'dark' : 'light';
        document.documentElement.setAttribute('data-theme', theme);
    });
}

/**
 * Toggle dark mode on/off
 * Saves preference to localStorage
 */
function toggleDarkMode() {
    const html = document.documentElement;
    const currentTheme = html.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    html.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    
    updateDarkModeIcon(newTheme);
}

/**
 * Update dark mode icon and text based on current theme
 * @param {string} theme - Current theme ('dark' or 'light')
 */
function updateDarkModeIcon(theme) {
    const icon = document.getElementById('darkModeIcon');
    const text = document.getElementById('darkModeText');
    
    if (icon && text) {
        if (theme === 'dark') {
            icon.innerHTML = '<path d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z" fill-rule="evenodd" clip-rule="evenodd"/>';
            text.textContent = 'Light Mode';
        } else {
            icon.innerHTML = '<path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z"/>';
            text.textContent = 'Dark Mode';
        }
    }
}

// Initialize theme from localStorage on page load
window.addEventListener('DOMContentLoaded', () => {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        document.documentElement.setAttribute('data-theme', savedTheme);
        updateDarkModeIcon(savedTheme);
    } else {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        updateDarkModeIcon(currentTheme || 'light');
    }
});

// Auto-load theme when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', loadTheme);
} else {
    loadTheme();
}

/* ============================================
   Modal Management
   ============================================ */

/**
 * Centralized ESC key handler for all modals
 * Closes any open modal when ESC is pressed
 */
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        // Handle custom modal-overlay modals
        // Check all modal overlays and find visible ones
        const allModals = document.querySelectorAll('.modal-overlay');
        const openModals = Array.from(allModals).filter(modal => {
            const style = window.getComputedStyle(modal);
            return style.display !== 'none' && style.visibility !== 'hidden';
        });
        
        if (openModals.length > 0) {
            // Get the topmost modal (last in DOM order, highest z-index)
            const topModal = openModals.reduce((top, modal) => {
                const topZ = parseInt(window.getComputedStyle(top).zIndex) || 0;
                const modalZ = parseInt(window.getComputedStyle(modal).zIndex) || 0;
                return modalZ > topZ ? modal : top;
            }, openModals[0]);
            
            // Get the close function from data attribute or find it
            const closeFunction = topModal.getAttribute('data-close-function');
            if (closeFunction && typeof window[closeFunction] === 'function') {
                window[closeFunction]();
            } else {
                // Fallback: try to find close button and click it
                const closeBtn = topModal.querySelector('.btn-close-modal');
                if (closeBtn && closeBtn.onclick) {
                    closeBtn.onclick();
                } else if (closeBtn) {
                    closeBtn.click();
                }
            }
        }
    }
});
