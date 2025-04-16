/**
 * Authentication JavaScript file for Autêntica application
 */

document.addEventListener('DOMContentLoaded', function() {
    // Login form validation and submission
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const emailInput = document.getElementById('email');
            const passwordInput = document.getElementById('password');
            
            // Validate email
            if (!emailInput.value.trim()) {
                showError(emailInput, 'Email é obrigatório');
                return;
            } else if (!isValidEmail(emailInput.value.trim())) {
                showError(emailInput, 'Email inválido');
                return;
            } else {
                removeError(emailInput);
            }
            
            // Validate password
            if (!passwordInput.value) {
                showError(passwordInput, 'Senha é obrigatória');
                return;
            } else {
                removeError(passwordInput);
            }
            
            // Prepare form data
            const formData = {
                email: emailInput.value.trim(),
                password: passwordInput.value
            };
            
            // Submit form via AJAX
            submitLoginForm(formData);
        });
    }
    
    // Registration form validation and submission
    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const nomeInput = document.getElementById('nome');
            const telefoneInput = document.getElementById('telefone');
            const instagramInput = document.getElementById('instagram');
            const emailInput = document.getElementById('email');
            const passwordInput = document.getElementById('password');
            const confirmPasswordInput = document.getElementById('confirm-password');
            
            let isValid = true;
            
            // Validate nome
            if (!nomeInput.value.trim()) {
                showError(nomeInput, 'Nome é obrigatório');
                isValid = false;
            } else {
                removeError(nomeInput);
            }
            
            // Validate telefone
            if (!telefoneInput.value.trim()) {
                showError(telefoneInput, 'Telefone é obrigatório');
                isValid = false;
            } else {
                removeError(telefoneInput);
            }
            
            // Validate instagram
            if (!instagramInput.value.trim()) {
                showError(instagramInput, 'Instagram é obrigatório');
                isValid = false;
            } else {
                removeError(instagramInput);
            }
            
            // Validate email
            if (!emailInput.value.trim()) {
                showError(emailInput, 'Email é obrigatório');
                isValid = false;
            } else if (!isValidEmail(emailInput.value.trim())) {
                showError(emailInput, 'Email inválido');
                isValid = false;
            } else {
                removeError(emailInput);
            }
            
            // Validate password
            if (!passwordInput.value) {
                showError(passwordInput, 'Senha é obrigatória');
                isValid = false;
            } else if (!isValidPassword(passwordInput.value)) {
                showError(passwordInput, 'A senha deve ter pelo menos 8 caracteres');
                isValid = false;
            } else {
                removeError(passwordInput);
            }
            
            // Validate confirm password
            if (passwordInput.value !== confirmPasswordInput.value) {
                showError(confirmPasswordInput, 'As senhas não coincidem');
                isValid = false;
            } else {
                removeError(confirmPasswordInput);
            }
            
            if (!isValid) {
                return;
            }
            
            // Prepare form data
            const formData = {
                nome: nomeInput.value.trim(),
                telefone: telefoneInput.value.trim(),
                instagram: instagramInput.value.trim(),
                email: emailInput.value.trim(),
                password: passwordInput.value
            };
            
            // Submit form via AJAX
            submitRegisterForm(formData);
        });
    }
    
    // Input event listeners to clear errors on input
    const inputs = document.querySelectorAll('input');
    inputs.forEach(input => {
        input.addEventListener('input', function() {
            removeError(this);
        });
    });
});

/**
 * Form submission functions
 */

// Function to clear all form errors
function clearErrors() {
    // Remove error messages
    document.querySelectorAll('.error-message').forEach(el => el.remove());
    document.querySelector('.form-errors')?.remove();
    
    // Remove error class from fields
    document.querySelectorAll('.error').forEach(el => el.classList.remove('error'));
}

// Submit login form via AJAX
async function submitLoginForm(formData) {
    try {
        // Disable submit button to prevent multiple submissions
        const submitButton = document.querySelector('#login-form button[type="submit"]');
        submitButton.disabled = true;
        submitButton.textContent = 'Processando...';
        
        // Make API request
        const response = await fetch('/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (response.ok && data.success) {
            // Redirect on success
            window.location.href = data.redirect;
        } else {
            // Show error message
            const emailInput = document.getElementById('email');
            showError(emailInput, data.message || 'Credenciais inválidas');
            
            // Re-enable submit button
            submitButton.disabled = false;
            submitButton.textContent = 'Entrar';
        }
    } catch (error) {
        console.error('Login error:', error);
        
        // Show generic error message
        const emailInput = document.getElementById('email');
        showError(emailInput, 'Erro ao fazer login. Tente novamente.');
        
        // Re-enable submit button
        const submitButton = document.querySelector('#login-form button[type="submit"]');
        submitButton.disabled = false;
        submitButton.textContent = 'Entrar';
    }
}

// Submit registration form via AJAX
async function submitRegisterForm(formData) {
    try {
        // Disable submit button to prevent multiple submissions
        const submitButton = document.querySelector('#register-form button[type="submit"]');
        submitButton.disabled = true;
        submitButton.textContent = 'Processando...';
        
        // Make API request
        const response = await fetch('/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (response.ok && data.success) {
            // Check if email confirmation is required
            if (data.requireEmailConfirmation) {
                // Redirect to the email confirmation page
                window.location.href = data.redirect || '/register/success';
            } else {
                // Redirect to home or dashboard if no confirmation needed
                window.location.href = data.redirect || '/home';
            }
        } else {
            // Show error message
            const emailInput = document.getElementById('email');
            showError(emailInput, data.message || 'Erro ao registrar usuário');
            
            // Re-enable submit button
            submitButton.disabled = false;
            submitButton.textContent = 'Continuar';
        }
    } catch (error) {
        console.error('Registration error:', error);
        
        // Show generic error message
        const emailInput = document.getElementById('email');
        showError(emailInput, 'Erro ao registrar usuário. Tente novamente.');
        
        // Re-enable submit button
        const submitButton = document.querySelector('#register-form button[type="submit"]');
        submitButton.disabled = false;
        submitButton.textContent = 'Continuar';
    }
}
