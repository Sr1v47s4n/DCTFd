/**
 * Avatar selection functionality
 */
document.addEventListener('DOMContentLoaded', function() {
    // Find all avatar option elements
    const avatarOptions = document.querySelectorAll('.avatar-option');
    
    // Add click handlers to each avatar option
    avatarOptions.forEach(option => {
        option.addEventListener('click', function() {
            // Get the radio input inside this option
            const radio = this.querySelector('input[type="radio"]');
            
            // Check the radio input
            radio.checked = true;
            
            // Trigger change event on the radio
            const event = new Event('change');
            radio.dispatchEvent(event);
            
            // Remove selected class from all options
            avatarOptions.forEach(opt => opt.classList.remove('selected'));
            
            // Add selected class to this option
            this.classList.add('selected');
            
            // Update current avatar preview in the profile edit form
            updateCurrentAvatarPreview(this);
            
            // Scroll the container to ensure the selected avatar is visible
            const container = this.closest('.avatar-options');
            if (container) {
                // Calculate the scroll position to center the selected avatar
                const optionTop = this.offsetTop;
                const containerHeight = container.clientHeight;
                const optionHeight = this.clientHeight;
                const scrollTo = optionTop - (containerHeight / 2) + (optionHeight / 2);
                
                // Smooth scroll to the selected avatar
                container.scrollTo({
                    top: Math.max(0, scrollTo),
                    behavior: 'smooth'
                });
            }
            
            // Update preview if it exists
            updateAvatarPreview(this);
        });
        
        // Also handle the radio change event
        const radio = option.querySelector('input[type="radio"]');
        radio.addEventListener('change', function() {
            // If this radio is checked
            if (this.checked) {
                // Remove selected class from all options
                avatarOptions.forEach(opt => opt.classList.remove('selected'));
                
                // Add selected class to the parent option
                const selectedOption = this.closest('.avatar-option');
                selectedOption.classList.add('selected');
                
                // Update preview
                updateAvatarPreview(selectedOption);
            }
        });
        
        // Set initial selected state based on radio checked state
        if (radio.checked) {
            option.classList.add('selected');
            // Update preview on page load
            updateAvatarPreview(option);
        }
    });
    
    // Add category navigation ONLY if the category tabs don't already exist
    if (!document.querySelector('.avatar-category-tabs')) {
        const categories = document.querySelectorAll('.avatar-category-title');
        if (categories.length > 0) {
            // Create category navigation
            const navContainer = document.createElement('div');
            navContainer.className = 'avatar-category-nav mb-3';
            navContainer.style.display = 'flex';
            navContainer.style.gap = '0.5rem';
            navContainer.style.flexWrap = 'wrap';
            
            categories.forEach((category, index) => {
                const btn = document.createElement('button');
                btn.type = 'button';
                btn.className = 'btn btn-sm btn-outline-primary';
                btn.textContent = category.textContent.trim();
                btn.dataset.category = index;
            
            btn.addEventListener('click', function() {
                // Scroll to category
                category.scrollIntoView({ behavior: 'smooth' });
                
                // Update active button
                document.querySelectorAll('.avatar-category-nav button').forEach(b => {
                    b.classList.remove('btn-primary');
                    b.classList.add('btn-outline-primary');
                });
                btn.classList.remove('btn-outline-primary');
                btn.classList.add('btn-primary');
            });
            
            navContainer.appendChild(btn);
        });
        
        // Insert navigation before the first category
        const firstCategory = categories[0].closest('.avatar-category');
        firstCategory.parentNode.insertBefore(navContainer, firstCategory);
        
        // Activate first button
        navContainer.querySelector('button').classList.remove('btn-outline-primary');
        navContainer.querySelector('button').classList.add('btn-primary');
    }
    
    // Function to update avatar preview
    function updateAvatarPreview(selectedOption) {
        const previewContainer = document.querySelector('.avatar-preview');
        if (previewContainer) {
            const previewImg = previewContainer.querySelector('img');
            const selectedImg = selectedOption.querySelector('img');
            
            if (previewImg && selectedImg) {
                // Add timestamp to prevent caching
                previewImg.src = selectedImg.src + '?t=' + new Date().getTime();
                previewImg.alt = selectedImg.alt || 'Selected avatar';
            }
        } else {
            // Create preview container if it doesn't exist
            const avatarSection = document.querySelector('.avatar-options-container').closest('.mb-3');
            
            if (avatarSection) {
                const preview = document.createElement('div');
                preview.className = 'avatar-preview text-center mb-3';
                
                const heading = document.createElement('p');
                heading.className = 'mb-2';
                heading.textContent = 'Selected Avatar:';
                
                const img = document.createElement('img');
                img.className = 'img-thumbnail';
                img.style.width = '120px';
                img.style.height = '120px';
                img.style.objectFit = 'cover';
                
                const selectedImg = selectedOption.querySelector('img');
                if (selectedImg) {
                    // Add timestamp to prevent caching
                    img.src = selectedImg.src + '?t=' + new Date().getTime();
                    img.alt = selectedImg.alt || 'Selected avatar';
                }
                
                preview.appendChild(heading);
                preview.appendChild(img);
                
                // Insert before the avatar options container
                const optionsContainer = document.querySelector('.avatar-options-container');
                optionsContainer.parentNode.insertBefore(preview, optionsContainer);
            }
        }
    }
    
    // Function to update the current avatar preview at the top of the form
    function updateCurrentAvatarPreview(selectedOption) {
        const currentAvatarContainer = document.querySelector('.current-avatar');
        if (currentAvatarContainer) {
            const currentAvatarImg = currentAvatarContainer.querySelector('img');
            const selectedImg = selectedOption.querySelector('img');
            
            if (currentAvatarImg && selectedImg) {
                // Add timestamp to prevent caching
                currentAvatarImg.src = selectedImg.src + '?t=' + new Date().getTime();
            }
        }
    }
    
    // Add anti-cache parameter to form submission
    const profileForm = document.querySelector('form');
    if (profileForm) {
        profileForm.addEventListener('submit', function() {
            // Force browser to reload avatar images after form submission
            localStorage.setItem('avatarUpdated', 'true');
        });
    }
    
    // Check if avatar was just updated
    if (localStorage.getItem('avatarUpdated') === 'true') {
        // Clear the flag
        localStorage.removeItem('avatarUpdated');
        
        // Force reload all avatar images
        const allAvatarImages = document.querySelectorAll('img[src*="avatars"]');
        allAvatarImages.forEach(img => {
            img.src = img.src + (img.src.includes('?') ? '&' : '?') + 't=' + new Date().getTime();
        });
    }
});
