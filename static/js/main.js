// Main JavaScript file for Ecycle

document.addEventListener('DOMContentLoaded', function() {
    // Theme Toggle Handler (Dark / Light Mode)
    const themeToggleBtn = document.getElementById('theme-toggle');
    const themeIcon = document.getElementById('theme-icon');
    const htmlEl = document.documentElement;

    function applyTheme(theme) {
        htmlEl.setAttribute('data-bs-theme', theme);
        localStorage.setItem('theme', theme);

        if (themeIcon) {
            if (theme === 'light') {
                themeIcon.className = 'fas fa-moon text-primary';
                if (themeToggleBtn) themeToggleBtn.title = 'Switch to Dark Mode';
            } else {
                themeIcon.className = 'fas fa-sun text-warning';
                if (themeToggleBtn) themeToggleBtn.title = 'Switch to Bright/Light Mode';
            }
        }
    }

    // Set initial icon state
    const currentTheme = localStorage.getItem('theme') || 'dark';
    applyTheme(currentTheme);

    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', function() {
            const activeTheme = htmlEl.getAttribute('data-bs-theme') || 'dark';
            const nextTheme = activeTheme === 'dark' ? 'light' : 'dark';
            applyTheme(nextTheme);
        });
    }

    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'))
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl)
    });

    // Show spinner when submitting forms
    const forms = document.querySelectorAll('form:not(.no-spinner)');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            showSpinner();
        });
    });

    // Handle flash messages auto-dismissal
    setTimeout(function() {
        const flashMessages = document.querySelectorAll('.alert-dismissible');
        flashMessages.forEach(message => {
            const bsAlert = new bootstrap.Alert(message);
            bsAlert.close();
        });
    }, 5000);

    // Show/hide reward details
    const detailButtons = document.querySelectorAll('.show-details-btn');
    detailButtons.forEach(button => {
        button.addEventListener('click', function() {
            const detailsId = this.getAttribute('data-details-id');
            const detailsEl = document.getElementById(detailsId);
            
            if (detailsEl.classList.contains('d-none')) {
                detailsEl.classList.remove('d-none');
                this.textContent = 'Hide Details';
            } else {
                detailsEl.classList.add('d-none');
                this.textContent = 'Show Details';
            }
        });
    });

    // Update eco points in UI
    const ecoPointsEl = document.getElementById('ecoPointsDisplay');
    if (ecoPointsEl) {
        const ecoPoints = ecoPointsEl.getAttribute('data-points');
        ecoPointsEl.textContent = ecoPoints;
    }
});

// Show loading spinner
function showSpinner() {
    const spinner = document.createElement('div');
    spinner.className = 'spinner-overlay';
    spinner.innerHTML = `
        <div class="spinner-border text-light" role="status" style="width: 3rem; height: 3rem;">
            <span class="visually-hidden">Loading...</span>
        </div>
    `;
    document.body.appendChild(spinner);
}

// Hide loading spinner
function hideSpinner() {
    const spinner = document.querySelector('.spinner-overlay');
    if (spinner) {
        spinner.remove();
    }
}

// Confirm form submission
function confirmAction(message) {
    return confirm(message || 'Are you sure you want to perform this action?');
}

// Countdown timer for session expiration (if needed)
function startSessionTimer(expiryMinutes) {
    const expiryTime = new Date().getTime() + (expiryMinutes * 60 * 1000);
    
    const timerInterval = setInterval(function() {
        const now = new Date().getTime();
        const timeLeft = expiryTime - now;
        
        if (timeLeft < 0) {
            clearInterval(timerInterval);
            alert('Your session has expired. Please login again.');
            window.location.href = '/logout';
        } else if (timeLeft < 60000) { // Less than 1 minute
            const timerEl = document.getElementById('sessionTimer');
            if (timerEl) {
                timerEl.classList.remove('d-none');
                timerEl.textContent = `Session expires in ${Math.ceil(timeLeft / 1000)} seconds`;
            }
        }
    }, 1000);
}
