/**
 * Telehealth Authentication Logic
 * Provides smooth transitions between Sign In and Registration forms
 * similar to iOS/macOS experiences.
 */

document.addEventListener('DOMContentLoaded', () => {
    // Splash Screen Logic
    const splashScreen = document.getElementById('splashScreen');
    if (splashScreen) {
        setTimeout(() => {
            splashScreen.classList.add('fade-out');
            // Remove from DOM after fade animation to keep things clean
            setTimeout(() => {
                splashScreen.remove();
            }, 500);
        }, 1500); // 1.5 seconds as requested
    }

    // DOM Elements
    const btnSignIn = document.getElementById('btnSignIn');
    const btnSignUp = document.getElementById('btnSignUp');
    const toggleSlider = document.getElementById('toggleSlider');
    
    const signInForm = document.getElementById('signInForm');
    const signUpForm = document.getElementById('signUpForm');
    const formsWrapper = document.getElementById('formsWrapper');
    
    // Password Strength
    const passwordInput = document.getElementById('signup-password');
    const strengthBar = document.getElementById('strengthBar');

    // Initialize forms to correct heights
    function initializeForms() {
        // Set sign-in as active initially
        signInForm.classList.add('active');
        
        // Wait a tick for styles to compute
        setTimeout(() => {
            adjustWrapperHeight(signInForm);
        }, 50);
    }

    // Toggle Form Function
    window.toggleForm = (type) => {
        if (type === 'signin' && !btnSignIn.classList.contains('active')) {
            // Activate Sign In Button
            btnSignIn.classList.add('active');
            btnSignUp.classList.remove('active');
            toggleSlider.style.transform = 'translateX(0)';
            
            // Animation logic
            signUpForm.classList.remove('active');
            signUpForm.classList.add('exit-right');
            
            signInForm.classList.remove('exit-left', 'exit-right');
            
            // Small delay to allow exit animation to start before entrance
            setTimeout(() => {
                signInForm.classList.add('active');
                adjustWrapperHeight(signInForm);
            }, 50);

        } else if (type === 'signup' && !btnSignUp.classList.contains('active')) {
            // Activate Sign Up Button
            btnSignUp.classList.add('active');
            btnSignIn.classList.remove('active');
            toggleSlider.style.transform = 'translateX(100%)';
            
            // Animation logic
            signInForm.classList.remove('active');
            signInForm.classList.add('exit-left');
            
            signUpForm.classList.remove('exit-left', 'exit-right');
            
            // Small delay to allow exit animation to start before entrance
            setTimeout(() => {
                signUpForm.classList.add('active');
                adjustWrapperHeight(signUpForm);
            }, 50);
        }
    };

    // Adjust wrapper height to fit active form content smoothly
    function adjustWrapperHeight(activeForm) {
        const height = activeForm.offsetHeight;
        formsWrapper.style.height = `${height}px`;
    }

    // Window resize handler to maintain correct wrapper height
    window.addEventListener('resize', () => {
        const activeForm = document.querySelector('.auth-form.active');
        if (activeForm) {
            adjustWrapperHeight(activeForm);
        }
    });

    // Handle Password Strength Indicator
    if (passwordInput && strengthBar) {
        passwordInput.addEventListener('input', (e) => {
            const val = e.target.value;
            let strength = 0;
            
            if (val.length > 0) strength += 1;
            if (val.length >= 8) strength += 1;
            if (/[A-Z]/.test(val)) strength += 1;
            if (/[0-9]/.test(val)) strength += 1;
            if (/[^A-Za-z0-9]/.test(val)) strength += 1;

            // Update UI based on strength
            switch (strength) {
                case 0:
                    strengthBar.style.width = '0%';
                    strengthBar.style.backgroundColor = 'var(--apple-red)';
                    break;
                case 1:
                case 2:
                    strengthBar.style.width = '33%';
                    strengthBar.style.backgroundColor = 'var(--apple-red)';
                    break;
                case 3:
                case 4:
                    strengthBar.style.width = '66%';
                    strengthBar.style.backgroundColor = 'var(--apple-orange)';
                    break;
                case 5:
                    strengthBar.style.width = '100%';
                    strengthBar.style.backgroundColor = 'var(--apple-green)';
                    break;
            }
        });
    }

    // Form Submission Logs (Console Only for Demo)
    // Form Submission: Login
    signInForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const contact = document.getElementById('signin-contact').value;
        const password = document.getElementById('signin-password').value;
        const btn = e.target.querySelector('button[type="submit"]');
        const originalText = btn.innerHTML;
        
        btn.innerHTML = 'Signing In...';
        btn.style.opacity = '0.8';
        
        try {
            const response = await fetch('/api/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ contact, password })
            });
            const result = await response.json();
            
            if (response.ok) {
                window.location.href = result.redirect;
            } else {
                alert(result.error || 'Login failed');
                btn.innerHTML = originalText;
                btn.style.opacity = '1';
            }
        } catch (error) {
            alert('Navigation error: Make sure the Python server is running.');
            btn.innerHTML = originalText;
            btn.style.opacity = '1';
        }
    });

    // Form Submission: Registration
    signUpForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const firstName = document.getElementById('signup-fname').value;
        const lastName = document.getElementById('signup-lname').value;
        const contact = document.getElementById('signup-contact').value;
        const password = document.getElementById('signup-password').value;
        const role = document.querySelector('input[name="role"]:checked').value;
        
        const btn = e.target.querySelector('button[type="submit"]');
        const originalText = btn.innerHTML;
        
        btn.innerHTML = 'Creating Account...';
        btn.style.opacity = '0.8';
        
        try {
            const response = await fetch('/api/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ firstName, lastName, contact, role, password })
            });
            const result = await response.json();
            
            if (response.ok) {
                window.location.href = result.redirect;
            } else {
                alert(result.error || 'Registration failed');
                btn.innerHTML = originalText;
                btn.style.opacity = '1';
            }
        } catch (error) {
            alert('Navigation error: Make sure the Python server is running.');
            btn.innerHTML = originalText;
            btn.style.opacity = '1';
        }
    });

    // Run initialization
    initializeForms();
});
