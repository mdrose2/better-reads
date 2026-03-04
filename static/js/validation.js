/**
 * Better Reads - Form Validation
 * 
 * Provides client-side validation for all forms:
 * - Registration form
 * - Review form
 * - Profile edit form
 * 
 * Features real-time validation, character counters,
 * and prevents form submission with invalid data.
 */

console.log('✓ Validation.js loaded');

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Display an error message for an input field.
 * @param {HTMLElement} input - The input field with error
 * @param {string} message - Error message to display
 */
function showError(input, message) {
    const formGroup = input.closest('.mb-3') || input.parentElement;
    let errorDiv = formGroup.querySelector('.invalid-feedback');
    
    if (!errorDiv) {
        errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback';
        errorDiv.style.display = 'block';
        formGroup.appendChild(errorDiv);
    }
    
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
    input.classList.add('is-invalid');
    input.classList.remove('is-valid');
}

/**
 * Clear error state for an input field.
 * @param {HTMLElement} input - The input field to clear
 */
function clearError(input) {
    const formGroup = input.closest('.mb-3') || input.parentElement;
    const errorDiv = formGroup.querySelector('.invalid-feedback');
    
    if (errorDiv) {
        errorDiv.textContent = ''; 
        errorDiv.style.display = 'none';
    }
    
    input.classList.remove('is-invalid');
    input.classList.add('is-valid');
}

/**
 * Validate email format using regex.
 * @param {string} email - Email address to validate
 * @returns {boolean} True if email format is valid
 */
function isValidEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(String(email).toLowerCase());
}

/**
 * Validate password strength.
 * Requirements: at least 8 chars, one uppercase, one lowercase, one number.
 * @param {string} password - Password to validate
 * @returns {boolean} True if password meets requirements
 */
function isStrongPassword(password) {
    const re = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$/;
    return re.test(password);
}

// ============================================================================
// REGISTRATION FORM VALIDATION
// ============================================================================

document.addEventListener('DOMContentLoaded', function() {
    const registerForm = document.querySelector('.register-form');
    
    if (registerForm) {
        console.log('  ✓ Registration form found');
        
        const username = registerForm.querySelector('#id_username');
        const email = registerForm.querySelector('#id_email');
        const password1 = registerForm.querySelector('#id_password1');
        const password2 = registerForm.querySelector('#id_password2');
        
        // Username validation
        if (username) {
            username.addEventListener('input', function() {
                const value = this.value.trim();
                
                if (value.length === 0) {
                    showError(this, 'Username is required');
                } else if (value.length < 3) {
                    showError(this, 'Username must be at least 3 characters');
                } else if (!/^[a-zA-Z0-9_]+$/.test(value)) {
                    showError(this, 'Only letters, numbers, and underscores allowed');
                } else {
                    clearError(this);
                }
            });
        }
        
        // Email validation
        if (email) {
            email.addEventListener('input', function() {
                const value = this.value.trim();
                
                if (value.length === 0) {
                    showError(this, 'Email is required');
                } else if (!isValidEmail(value)) {
                    showError(this, 'Please enter a valid email address');
                } else {
                    clearError(this);
                }
            });
        }
        
        // Password validation
        if (password1) {
            password1.addEventListener('input', function() {
                const value = this.value;
                
                if (value.length === 0) {
                    showError(this, 'Password is required');
                } else if (value.length < 8) {
                    showError(this, 'Password must be at least 8 characters');
                } else if (!isStrongPassword(value)) {
                    showError(this, 'Must contain uppercase, lowercase, and number');
                } else {
                    clearError(this);
                }
                
                // Check password match if confirm field has value
                if (password2 && password2.value) {
                    if (value !== password2.value) {
                        showError(password2, 'Passwords do not match');
                    } else {
                        clearError(password2);
                    }
                }
            });
        }
        
        // Confirm password validation
        if (password2) {
            password2.addEventListener('input', function() {
                if (this.value !== password1.value) {
                    showError(this, 'Passwords do not match');
                } else {
                    clearError(this);
                }
            });
        }
        
        // Form submit validation
        registerForm.addEventListener('submit', function(e) {
            let isValid = true;
            
            // Validate all fields on submit
            if (username && username.value.trim().length < 3) {
                showError(username, 'Username must be at least 3 characters');
                isValid = false;
            }
            
            if (email && !isValidEmail(email.value.trim())) {
                showError(email, 'Valid email is required');
                isValid = false;
            }
            
            if (password1 && !isStrongPassword(password1.value)) {
                showError(password1, 'Strong password required');
                isValid = false;
            }
            
            if (password2 && password2.value !== password1.value) {
                showError(password2, 'Passwords must match');
                isValid = false;
            }
            
            if (!isValid) {
                e.preventDefault();
                // Scroll to first error
                const firstError = registerForm.querySelector('.is-invalid');
                if (firstError) {
                    firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
            }
        });
    }
});

// ============================================================================
// REVIEW FORM VALIDATION
// ============================================================================

document.addEventListener('DOMContentLoaded', function() {
    const reviewForm = document.querySelector('.review-form');
    
    if (reviewForm) {
        console.log('  ✓ Review form found');
        
        const rating = reviewForm.querySelector('#id_rating');
        const title = reviewForm.querySelector('#id_title');
        const content = reviewForm.querySelector('#id_content');
        
        // Rating validation
        if (rating) {
            rating.addEventListener('change', function() {
                const val = parseFloat(this.value);
                if (isNaN(val) || val < 0 || val > 5) {
                    showError(this, 'Rating must be between 0 and 5');
                } else {
                    clearError(this);
                }
            });
        }
        
        // Title validation
        if (title) {
            title.addEventListener('input', function() {
                const value = this.value.trim();
                
                if (value.length === 0) {
                    showError(this, 'Review title is required');
                } else if (value.length < 3) {
                    showError(this, 'Title must be at least 3 characters');
                } else if (value.length > 200) {
                    showError(this, 'Title cannot exceed 200 characters');
                } else {
                    clearError(this);
                }
            });
        }
        
        // Content validation with character counter
        if (content) {
            // Create character counter
            const counter = document.createElement('small');
            counter.className = 'text-muted float-end';
            content.parentElement.appendChild(counter);
            
            content.addEventListener('input', function() {
                const len = this.value.length;
                counter.textContent = `${len} characters`;
                
                // Find or create error div
                const formGroup = this.closest('.mb-3');
                let errorDiv = formGroup.querySelector('.invalid-feedback');
                
                if (!errorDiv) {
                    errorDiv = document.createElement('div');
                    errorDiv.className = 'invalid-feedback';
                    formGroup.appendChild(errorDiv);
                }
                
                // Validate length
                if (len === 0) {
                    errorDiv.textContent = 'Review content is required';
                    errorDiv.style.display = 'block';
                    this.classList.add('is-invalid');
                    this.classList.remove('is-valid');
                } else if (len < 10) {
                    errorDiv.textContent = 'Review must be at least 10 characters';
                    errorDiv.style.display = 'block';
                    this.classList.add('is-invalid');
                    this.classList.remove('is-valid');
                } else {
                    errorDiv.textContent = '';
                    errorDiv.style.display = 'none';
                    this.classList.remove('is-invalid');
                    this.classList.add('is-valid');
                }
            });
        }
        
        // Form submit validation
        reviewForm.addEventListener('submit', function(e) {
            let isValid = true;
            
            // Validate rating
            if (rating) {
                const ratingVal = parseFloat(rating.value);
                if (isNaN(ratingVal) || ratingVal < 0 || ratingVal > 5) {
                    showError(rating, 'Please select a valid rating');
                    isValid = false;
                }
            }
            
            // Validate title
            if (title && title.value.trim().length < 3) {
                showError(title, 'Title must be at least 3 characters');
                isValid = false;
            }
            
            // Validate content
            if (content && content.value.length < 10) {
                showError(content, 'Review must be at least 10 characters');
                isValid = false;
            }
            
            if (!isValid) {
                e.preventDefault();
                const firstError = reviewForm.querySelector('.is-invalid');
                if (firstError) {
                    firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
            }
        });
    }
});

// ============================================================================
// PROFILE FORM VALIDATION
// ============================================================================

document.addEventListener('DOMContentLoaded', function() {
    const profileForm = document.querySelector('.profile-form');
    
    if (profileForm) {
        console.log('  ✓ Profile form found');
        
        const username = profileForm.querySelector('#id_username');
        const bio = profileForm.querySelector('#id_bio');
        const bioCounter = document.getElementById('bio-counter');
        
        // Username validation
        if (username) {
            username.addEventListener('input', function() {
                const value = this.value.trim();
                
                if (value.length === 0) {
                    showError(this, 'Username is required');
                } else if (value.length < 3) {
                    showError(this, 'Username must be at least 3 characters');
                } else if (!/^[a-zA-Z0-9_]+$/.test(value)) {
                    showError(this, 'Only letters, numbers, and underscores allowed');
                } else {
                    clearError(this);
                }
            });
        }
        
        // Bio validation with character counter
        if (bio && bioCounter) {
            bio.addEventListener('input', function() {
                const remaining = 500 - this.value.length;
                bioCounter.textContent = `${remaining}/500 characters remaining`;
                
                if (remaining < 0) {
                    showError(this, 'Bio cannot exceed 500 characters');
                } else if (this.value.length > 0 && this.value.length < 10) {
                    // Optional: info message without error styling
                    bioCounter.classList.add('text-warning');
                } else {
                    clearError(this);
                    bioCounter.classList.remove('text-warning');
                }
            });
            
            // Trigger initial count
            bio.dispatchEvent(new Event('input'));
        }
        
        // Profile picture preview
        const pictureInput = profileForm.querySelector('#id_profile_picture');
        if (pictureInput) {
            pictureInput.addEventListener('change', function() {
                if (this.files && this.files[0]) {
                    const file = this.files[0];
                    const validTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
                    
                    if (!validTypes.includes(file.type)) {
                        showError(this, 'Please select a valid image file (JPEG, PNG, GIF, WEBP)');
                    } else if (file.size > 5 * 1024 * 1024) { // 5MB limit
                        showError(this, 'Image size must be less than 5MB');
                    } else {
                        clearError(this);
                        
                        // Show image preview
                        const reader = new FileReader();
                        reader.onload = function(e) {
                            let preview = profileForm.querySelector('.image-preview');
                            if (!preview) {
                                preview = document.createElement('img');
                                preview.className = 'image-preview rounded-circle mt-2';
                                preview.style.width = '100px';
                                preview.style.height = '100px';
                                preview.style.objectFit = 'cover';
                                pictureInput.parentElement.appendChild(preview);
                            }
                            preview.src = e.target.result;
                        };
                        reader.readAsDataURL(file);
                    }
                }
            });
        }
        
        // Form submit validation
        profileForm.addEventListener('submit', function(e) {
            let isValid = true;
            
            if (username && username.value.trim().length < 3) {
                showError(username, 'Username must be at least 3 characters');
                isValid = false;
            }
            
            if (bio && bio.value.length > 500) {
                showError(bio, 'Bio cannot exceed 500 characters');
                isValid = false;
            }
            
            if (!isValid) {
                e.preventDefault();
                const firstError = profileForm.querySelector('.is-invalid');
                if (firstError) {
                    firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
            }
        });
    }
});