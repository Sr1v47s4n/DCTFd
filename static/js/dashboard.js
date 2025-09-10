// Dashboard JavaScript functionality

document.addEventListener('DOMContentLoaded', function() {
    // Automatically dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            alert.style.opacity = '0';
            setTimeout(function() {
                alert.style.display = 'none';
            }, 500);
        }, 5000);
    });

    // Add smooth scrolling behavior
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });

    // Toggle mobile menu
    const menuToggle = document.querySelector('.menu-toggle');
    if (menuToggle) {
        menuToggle.addEventListener('click', function() {
            document.querySelector('.dashboard-nav').classList.toggle('mobile-open');
        });
    }

    // Mobile sidebar collapse behavior
    const handleMobileNav = () => {
        if (window.innerWidth <= 768) {
            const navItems = document.querySelectorAll('.dashboard-menu li a');
            navItems.forEach(item => {
                item.addEventListener('click', () => {
                    if (window.innerWidth <= 768) {
                        // Add a small delay to allow for page navigation
                        setTimeout(() => {
                            const nav = document.querySelector('.dashboard-nav');
                            if (nav.classList.contains('expanded')) {
                                nav.classList.remove('expanded');
                            }
                        }, 100);
                    }
                });
            });
            
            // Toggle expanded class for mobile hover simulation with click
            const dashboardNav = document.querySelector('.dashboard-nav');
            if (dashboardNav) {
                dashboardNav.addEventListener('click', function(e) {
                    if (window.innerWidth <= 768 && !this.classList.contains('expanded')) {
                        e.preventDefault();
                        this.classList.add('expanded');
                    }
                });
                
                // Add outside click detection to close the menu
                document.addEventListener('click', function(e) {
                    if (window.innerWidth <= 768 && !dashboardNav.contains(e.target)) {
                        dashboardNav.classList.remove('expanded');
                    }
                });
            }
        }
    };

    // Initialize any tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize any popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Confirm actions with a prompt
    document.querySelectorAll('.confirm-action').forEach(function(button) {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to perform this action?')) {
                e.preventDefault();
            }
        });
    });

    // Handle form validation
    document.querySelectorAll('form.needs-validation').forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
    
    // Initialize mobile nav handler
    handleMobileNav();
    
    // Re-initialize on resize
    window.addEventListener('resize', handleMobileNav);
});
