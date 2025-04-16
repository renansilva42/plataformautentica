/**
 * Main JavaScript file for Autêntica application
 */

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Handle flash messages auto-dismiss
    const flashMessages = document.querySelectorAll('.flash-message');
    if (flashMessages.length > 0) {
        flashMessages.forEach(message => {
            setTimeout(() => {
                message.remove();
            }, 5000); // Remove after 5 seconds
        });
    }
    
    // Handle user menu dropdown
    const userMenu = document.querySelector('.user-info');
    const dropdownMenu = document.querySelector('.dropdown-menu');
    
    if (userMenu && dropdownMenu) {
        userMenu.addEventListener('click', function(e) {
            e.stopPropagation();
            dropdownMenu.classList.toggle('show');
        });
        
        // Close dropdown when clicking outside
        document.addEventListener('click', function() {
            if (dropdownMenu.classList.contains('show')) {
                dropdownMenu.classList.remove('show');
            }
        });
    }
    
    // Add CSS class for dropdown visibility
    const style = document.createElement('style');
    style.textContent = `
        .dropdown-menu.show {
            display: block;
        }
    `;
    document.head.appendChild(style);
});

/**
 * Utility functions
 */

// Function to validate email format
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Function to validate password strength
function isValidPassword(password) {
    // Password must be at least 8 characters
    return password.length >= 8;
}

// Function to show error message
function showError(element, message) {
    const parent = element.parentElement;
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    errorDiv.style.color = 'red';
    errorDiv.style.fontSize = '0.8rem';
    errorDiv.style.marginTop = '0.25rem';
    
    // Remove any existing error messages
    const existingError = parent.querySelector('.error-message');
    if (existingError) {
        parent.removeChild(existingError);
    }
    
    // Add new error message
    parent.appendChild(errorDiv);
}

// Function to remove error message
function removeError(element) {
    const parent = element.parentElement;
    const errorDiv = parent.querySelector('.error-message');
    if (errorDiv) {
        parent.removeChild(errorDiv);
    }
}

// Function to make API requests
async function apiRequest(url, method = 'GET', data = null) {
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json'
        }
    };
    
    if (data) {
        options.body = JSON.stringify(data);
    }
    
    try {
        const response = await fetch(url, options);
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.message || 'An error occurred');
        }
        
        return result;
    } catch (error) {
        console.error('API Request Error:', error);
        throw error;
    }
}