/**
 * DCTFd Avatar Cache Buster
 * 
 * This script clears the browser cache for avatar images
 * and forces a reload of all avatar images on the page.
 */

// Force reload all avatar images when the page loads
document.addEventListener('DOMContentLoaded', function() {
    console.log('Avatar cache buster active');
    
    // Add timestamp to all avatar images to force browser to reload them
    const allAvatarImages = document.querySelectorAll('img[src*="avatars"]');
    const timestamp = new Date().getTime();
    
    allAvatarImages.forEach(img => {
        const currentSrc = img.src;
        // Add timestamp parameter to force cache refresh
        img.src = currentSrc + (currentSrc.includes('?') ? '&' : '?') + '_t=' + timestamp;
        
        // Add a small timeout between each image to prevent server overload
        setTimeout(() => {
            console.log('Refreshed avatar: ' + img.src);
        }, 100);
    });
    
    // Set a flag in localStorage to refresh other pages in this session
    localStorage.setItem('refreshAvatars', 'true');
});
