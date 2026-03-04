// books/static/books/js/book_form.js
/**
 * Book form enhancements for the Better Reads platform.
 * Provides image preview and auto-resizing textarea functionality.
 */

(function() {
    'use strict';
    
    // Only initialize on book form pages
    const bookForm = document.querySelector('.book-form');
    if (!bookForm) return;
    
    console.log('✓ Book form enhanced');
    
    // =========================================================================
    // IMAGE PREVIEW
    // =========================================================================
    
    /**
     * Set up live preview for cover image URLs.
     * When a user enters a URL, show a preview of the image.
     */
    function setupImagePreview() {
        const coverUrlField = bookForm.querySelector('#id_cover_image_url');
        const thumbnailField = bookForm.querySelector('#id_thumbnail_url');
        
        /**
         * Create or update image preview for a given field.
         * @param {HTMLElement} field - The input field containing the image URL
         * @param {string} previewId - Unique ID for the preview container
         */
        function createPreview(field, previewId) {
            if (!field) return;
            
            // Create preview container if it doesn't exist
            let preview = document.getElementById(previewId);
            if (!preview) {
                preview = document.createElement('div');
                preview.id = previewId;
                preview.className = 'mt-2 text-center image-preview';
                field.parentElement.appendChild(preview);
            }
            
            // Update preview on URL change
            field.addEventListener('blur', function() {
                const url = this.value.trim();
                if (!url) {
                    preview.innerHTML = '';
                    return;
                }
                
                preview.innerHTML = `
                    <img src="${url}" 
                         class="img-fluid rounded border p-2" 
                         style="max-height: 150px; max-width: 100%;"
                         onerror="this.style.display='none'; this.parentElement.innerHTML='<small class=\'text-muted\'>Invalid image URL</small>';"
                         onload="this.style.display='inline-block';">
                `;
            });
        }
        
        createPreview(coverUrlField, 'cover-preview');
        createPreview(thumbnailField, 'thumbnail-preview');
    }
    
    // =========================================================================
    // AUTO-RESIZE TEXTAREA
    // =========================================================================
    
    /**
     * Set up auto-resizing for the description textarea.
     * The textarea grows vertically as the user types.
     */
    function setupDescriptionAutoResize() {
        const description = bookForm.querySelector('#id_description');
        if (!description) return;
        
        /**
         * Adjust textarea height to fit content.
         * Uses scrollHeight to determine optimal height.
         */
        function resizeTextarea() {
            // Reset height to auto to get the correct scrollHeight
            this.style.height = 'auto';
            // Set new height based on content
            this.style.height = (this.scrollHeight) + 'px';
        }
        
        // Initial resize
        resizeTextarea.call(description);
        
        // Resize on input
        description.addEventListener('input', resizeTextarea);
        
        // Also resize on window resize (in case container width changes)
        window.addEventListener('resize', function() {
            resizeTextarea.call(description);
        });
    }
    
    // =========================================================================
    // INITIALIZATION
    // =========================================================================
    
    // Initialize all features
    setupImagePreview();
    setupDescriptionAutoResize();
    
})();