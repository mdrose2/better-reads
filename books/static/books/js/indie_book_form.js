/**
 * Indie Book Form Validation
 * Handles real-time validation for the indie book add/edit form.
 */

(function() {
    'use strict';
    
    // Initialize when DOM is ready
    document.addEventListener('DOMContentLoaded', function() {
        const form = document.querySelector('.indie-book-form');
        if (!form) return;
        
        // Form fields
        const title = form.querySelector('#id_title');
        const authors = form.querySelector('#id_authors');
        const description = form.querySelector('#id_description');
        
        // =====================================================================
        // UTILITY FUNCTIONS
        // =====================================================================
        
        /**
         * Show error state for a field
         * @param {HTMLElement} field - The input field
         * @param {string} message - Error message to display
         */
        function showError(field, message) {
            field.classList.add('is-invalid');
            field.classList.remove('is-valid');
            
            // Find or create error message div
            let errorDiv = field.parentElement.querySelector('.invalid-feedback');
            if (!errorDiv) {
                errorDiv = document.createElement('div');
                errorDiv.className = 'invalid-feedback';
                field.parentElement.appendChild(errorDiv);
            }
            errorDiv.textContent = message;
        }
        
        /**
         * Clear error state for a field
         * @param {HTMLElement} field - The input field
         */
        function clearError(field) {
            field.classList.remove('is-invalid');
            field.classList.add('is-valid');
            
            // Remove error message if it exists
            const errorDiv = field.parentElement.querySelector('.invalid-feedback');
            if (errorDiv) {
                errorDiv.remove();
            }
        }
        
        // =====================================================================
        // TITLE VALIDATION
        // =====================================================================
        
        if (title) {
            title.addEventListener('input', function() {
                const value = this.value.trim();
                
                if (value.length === 0) {
                    showError(this, 'Title is required');
                } else if (value.length < 2) {
                    showError(this, 'Title must be at least 2 characters');
                } else {
                    clearError(this);
                }
            });
        }
        
        // =====================================================================
        // AUTHORS VALIDATION - UPDATED FOR COMMA-SEPARATED INPUT
        // =====================================================================
        
        if (authors) {
            authors.addEventListener('input', function() {
                const value = this.value.trim();
                
                if (value.length === 0) {
                    showError(this, 'At least one author is required');
                } else {
                    // Split by commas and check each part
                    const authorList = value.split(',').map(a => a.trim()).filter(a => a.length > 0);
                    
                    if (authorList.length === 0) {
                        showError(this, 'Please enter at least one valid author name');
                    } else {
                        // Check each author name is reasonable
                        const hasValidAuthor = authorList.some(author => author.length >= 2);
                        if (!hasValidAuthor) {
                            showError(this, 'Each author name must be at least 2 characters');
                        } else {
                            clearError(this);
                            
                            // Optional: Show preview of how authors will be stored
                            let preview = this.parentElement.querySelector('.author-preview');
                            if (!preview) {
                                preview = document.createElement('small');
                                preview.className = 'author-preview text-success d-block mt-1';
                                this.parentElement.appendChild(preview);
                            }
                            preview.innerHTML = `<i class="bi bi-check-circle me-1"></i>Will be saved as: ${authorList.join(', ')}`;
                        }
                    }
                }
            });
        }
        
        // =====================================================================
        // DESCRIPTION VALIDATION WITH CHARACTER COUNTER
        // =====================================================================
        
        if (description) {
            // Create character counter
            const counter = document.createElement('small');
            counter.className = 'text-muted float-end';
            description.parentElement.appendChild(counter);
            
            description.addEventListener('input', function() {
                const len = this.value.length;
                counter.textContent = `${len} characters`;
                
                if (len === 0) {
                    showError(this, 'Description is required');
                } else if (len < 20) {
                    showError(this, 'Description must be at least 20 characters');
                } else {
                    clearError(this);
                    
                    // Visual feedback when minimum length is reached
                    if (len >= 20 && len < 50) {
                        counter.classList.add('text-success');
                    } else if (len >= 50) {
                        counter.classList.remove('text-success');
                    }
                }
            });
        }
        
        // =====================================================================
        // FORM SUBMIT VALIDATION
        // =====================================================================
        
        form.addEventListener('submit', function(e) {
            let isValid = true;
            
            // Validate title
            if (title) {
                const titleValue = title.value.trim();
                if (titleValue.length < 2) {
                    showError(title, 'Title must be at least 2 characters');
                    isValid = false;
                }
            }
            
            // Validate authors (comma-separated format)
            if (authors) {
                const authorsValue = authors.value.trim();
                if (authorsValue.length === 0) {
                    showError(authors, 'At least one author is required');
                    isValid = false;
                } else {
                    const authorList = authorsValue.split(',').map(a => a.trim()).filter(a => a.length > 0);
                    if (authorList.length === 0) {
                        showError(authors, 'Please enter at least one valid author name');
                        isValid = false;
                    }
                }
            }
            
            // Validate description
            if (description) {
                const descValue = description.value.trim();
                if (descValue.length < 20) {
                    showError(description, 'Description must be at least 20 characters');
                    isValid = false;
                }
            }
            
            // Prevent form submission if validation fails
            if (!isValid) {
                e.preventDefault();
                
                // Scroll to first error
                const firstError = form.querySelector('.is-invalid');
                if (firstError) {
                    firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
            }
        });
        
    }); // end DOMContentLoaded
    
})();