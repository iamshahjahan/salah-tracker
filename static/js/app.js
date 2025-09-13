// Global variables
let currentUser = null;
let authToken = localStorage.getItem('authToken');

// API Base URL
const API_BASE = '';

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();

    // Clean up any existing user info elements first
    cleanupUserInfo();

    // Check for URL parameters (for password reset)
    checkURLParameters();

    // Load prayer times preview for home page
    loadPrayerTimesPreview();

    // Check if user is logged in
    if (authToken) {
        loadUserProfile().then(() => {
            showSection('prayers');
            updateUIForLoggedInUser();
        });
    } else {
        updateUIForLoggedOutUser();
    }

    // Set up automatic prayer status updates every minute for real-time updates
    setInterval(() => {
        if (authToken && document.getElementById('prayerTimes')) {
            loadPrayerTimes();
        }
    }, 1 * 60 * 1000); // 1 minute for real-time updates
});

function cleanupUserInfo() {
    // Remove all existing user info elements
    const existingUserInfos = document.querySelectorAll('.user-info');
    existingUserInfos.forEach(element => element.remove());
}

function checkURLParameters() {
    // Check for password reset code in URL
    const urlParams = new URLSearchParams(window.location.search);
    const resetCode = urlParams.get('code');

    if (resetCode) {
        // Show reset password modal
        showResetPassword(resetCode);
        // Clean up URL
        window.history.replaceState({}, document.title, window.location.pathname);
    }
}

function initializeApp() {
    // Setup navigation
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const sectionId = this.getAttribute('href').substring(1);
            showSection(sectionId);

            // Update active nav link
            navLinks.forEach(l => l.classList.remove('active'));
            this.classList.add('active');
        });
    });

    // Setup mobile menu toggle
    const navToggle = document.getElementById('nav-toggle');
    const navMenu = document.getElementById('nav-menu');

    navToggle.addEventListener('click', function() {
        navMenu.classList.toggle('active');
    });

    // Close mobile menu when clicking on a link
    navLinks.forEach(link => {
        link.addEventListener('click', function() {
            navMenu.classList.remove('active');
        });
    });
}

function setupEventListeners() {
    // Login form
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }

    // Register form
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', handleRegister);
    }

    // Add family form
    const addFamilyForm = document.getElementById('addFamilyForm');
    if (addFamilyForm) {
        addFamilyForm.addEventListener('submit', handleAddFamily);
    }

    // OTP login form
    const otpLoginForm = document.getElementById('otpLoginForm');
    if (otpLoginForm) {
        otpLoginForm.addEventListener('submit', handleOTPLogin);
    }

    // Email verification form
    const emailVerificationForm = document.getElementById('emailVerificationForm');
    if (emailVerificationForm) {
        emailVerificationForm.addEventListener('submit', handleEmailVerification);
    }

    // Forgot password form
    const forgotPasswordForm = document.getElementById('forgotPasswordForm');
    if (forgotPasswordForm) {
        forgotPasswordForm.addEventListener('submit', handleForgotPassword);
    }

    // Reset password form
    const resetPasswordForm = document.getElementById('resetPasswordForm');
    if (resetPasswordForm) {
        resetPasswordForm.addEventListener('submit', handleResetPassword);
    }
}

// Navigation functions
function showSection(sectionId) {
    // Hide all sections
    const sections = document.querySelectorAll('.section');
    sections.forEach(section => section.classList.remove('active'));

    // Show selected section
    const targetSection = document.getElementById(sectionId);
    if (targetSection) {
        targetSection.classList.add('active');

        // Load section data
        switch(sectionId) {
            case 'prayers':
                loadPrayerTimes();
                break;
            case 'dashboard':
                loadDashboard();
                break;
            case 'family':
                loadFamilyMembers();
                break;
            case 'profile':
                loadProfile();
                break;
        }
    }
}

// Modal functions
function showLogin() {
    closeModal('registerModal');
    document.getElementById('loginModal').style.display = 'block';
}

function showRegister() {
    closeModal('loginModal');
    document.getElementById('registerModal').style.display = 'block';
}

function showAddFamilyModal() {
    document.getElementById('addFamilyModal').style.display = 'block';
}

function showForgotPassword() {
    closeModal('loginModal');
    document.getElementById('forgotPasswordModal').style.display = 'block';
}

function showEmailVerification(email) {
    document.getElementById('verificationEmail').value = email;
    document.getElementById('emailVerificationModal').style.display = 'block';
}

function showResetPassword(code) {
    document.getElementById('resetCode').value = code;
    document.getElementById('resetPasswordModal').style.display = 'block';
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

// Login method switching
function switchLoginMethod(method) {
    const passwordForm = document.getElementById('loginForm');
    const otpForm = document.getElementById('otpLoginForm');
    const tabs = document.querySelectorAll('.method-tab');

    // Update tab states
    tabs.forEach(tab => tab.classList.remove('active'));
    event.target.classList.add('active');

    // Show/hide forms
    if (method === 'password') {
        passwordForm.classList.add('active');
        otpForm.classList.remove('active');
    } else {
        passwordForm.classList.remove('active');
        otpForm.classList.add('active');
    }
}

// Close modals when clicking outside
window.addEventListener('click', function(event) {
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
});

// Authentication functions
async function handleLogin(e) {
    e.preventDefault();

    const formData = new FormData(e.target);
    const loginData = {
        username: formData.get('username'),
        password: formData.get('password')
    };

    try {
        const response = await fetch(`${API_BASE}/api/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(loginData)
        });

        const data = await response.json();

        if (response.ok) {
            authToken = data.access_token;
            currentUser = data.user;
            localStorage.setItem('authToken', authToken);

            closeModal('loginModal');
            loadUserProfile().then(() => {
                updateUIForLoggedInUser();
                showSection('prayers');
            });
            showNotification('Login successful!', 'success');
        } else {
            showNotification(data.error || 'Login failed', 'error');
        }
    } catch (error) {
        showNotification('Network error. Please try again.', 'error');
    }
}

// Global variables for location selection
let detectedLocationData = {};
let selectedLocationData = {};

async function handleRegister(e) {
    e.preventDefault();

    const formData = new FormData(e.target);

    // Use selected location data if available, otherwise use detected or default
    let locationData = selectedLocationData;
    if (!locationData.lat || !locationData.lng) {
        locationData = detectedLocationData;
    }

    // If still no location, use default (Bangalore, India)
    if (!locationData.lat || !locationData.lng) {
        locationData = {
            lat: 12.9716,
            lng: 77.5946,
            timezone: 'Asia/Kolkata',
            city: 'Bangalore, India'
        };
    }

    const registerData = {
        username: formData.get('username'),
        email: formData.get('email'),
        password: formData.get('password'),
        first_name: formData.get('first_name'),
        last_name: formData.get('last_name'),
        phone_number: formData.get('phone_number'),
        location_lat: locationData.lat,
        location_lng: locationData.lng,
        timezone: locationData.timezone
    };

    try {
        const response = await fetch(`${API_BASE}/api/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(registerData)
        });

        const data = await response.json();

        if (response.ok) {
            authToken = data.access_token;
            currentUser = data.user;
            localStorage.setItem('authToken', authToken);

            closeModal('registerModal');
            loadUserProfile().then(() => {
                updateUIForLoggedInUser();
                showSection('prayers');
            });
            showNotification('Account created successfully!', 'success');

            // Show email verification modal for new users
            if (currentUser && !currentUser.email_verified) {
                setTimeout(() => {
                    showEmailVerification(currentUser.email);
                }, 1000);
            }
        } else {
            showNotification(data.error || 'Registration failed', 'error');
        }
    } catch (error) {
        showNotification('Network error. Please try again.', 'error');
    }
}

// OTP Login Functions
async function sendLoginOTP() {
    const email = document.getElementById('otpEmail').value;

    if (!email) {
        showNotification('Please enter your email address', 'error');
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/api/auth/send-login-otp`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email: email })
        });

        const data = await response.json();

        if (response.ok) {
            showNotification('Login code sent to your email!', 'success');
            // Show OTP input fields
            document.getElementById('otpCodeGroup').style.display = 'block';
            document.getElementById('otpLoginBtn').style.display = 'block';
        } else {
            showNotification(data.error || 'Failed to send login code', 'error');
        }
    } catch (error) {
        showNotification('Network error. Please try again.', 'error');
    }
}

async function handleOTPLogin(e) {
    e.preventDefault();

    const formData = new FormData(e.target);
    const loginData = {
        email: formData.get('email'),
        otp: formData.get('otp')
    };

    if (!loginData.email || !loginData.otp) {
        showNotification('Please enter email and OTP code', 'error');
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/api/auth/login-with-otp`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(loginData)
        });

        const data = await response.json();

        if (response.ok) {
            authToken = data.access_token;
            currentUser = data.user;
            localStorage.setItem('authToken', authToken);

            closeModal('loginModal');
            loadUserProfile().then(() => {
                updateUIForLoggedInUser();
                showSection('prayers');
            });
            showNotification('Login successful!', 'success');
        } else {
            showNotification(data.error || 'Login failed', 'error');
        }
    } catch (error) {
        showNotification('Network error. Please try again.', 'error');
    }
}

// Email Verification Functions
async function handleEmailVerification(e) {
    e.preventDefault();

    const formData = new FormData(e.target);
    const verificationData = {
        email: formData.get('email'),
        code: formData.get('code')
    };

    try {
        const response = await fetch(`${API_BASE}/api/auth/verify-email`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(verificationData)
        });

        const data = await response.json();

        if (response.ok) {
            showNotification('Email verified successfully!', 'success');
            closeModal('emailVerificationModal');
            // Update user profile to reflect verified status
            if (currentUser) {
                currentUser.email_verified = true;
            }
        } else {
            showNotification(data.error || 'Verification failed', 'error');
        }
    } catch (error) {
        showNotification('Network error. Please try again.', 'error');
    }
}

async function resendVerificationCode() {
    if (!authToken) {
        showNotification('Please login first', 'error');
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/api/auth/send-verification`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });

        const data = await response.json();

        if (response.ok) {
            showNotification('Verification code sent!', 'success');
        } else {
            showNotification(data.error || 'Failed to send verification code', 'error');
        }
    } catch (error) {
        showNotification('Network error. Please try again.', 'error');
    }
}

// Password Reset Functions
async function handleForgotPassword(e) {
    e.preventDefault();

    const formData = new FormData(e.target);
    const email = formData.get('email');

    try {
        const response = await fetch(`${API_BASE}/api/auth/forgot-password`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email: email })
        });

        const data = await response.json();

        if (response.ok) {
            showNotification('Password reset link sent to your email!', 'success');
            closeModal('forgotPasswordModal');
        } else {
            showNotification(data.error || 'Failed to send reset link', 'error');
        }
    } catch (error) {
        showNotification('Network error. Please try again.', 'error');
    }
}

async function handleResetPassword(e) {
    e.preventDefault();

    const formData = new FormData(e.target);
    const resetData = {
        code: formData.get('code'),
        new_password: formData.get('new_password'),
        confirm_password: formData.get('confirm_password')
    };

    if (resetData.new_password !== resetData.confirm_password) {
        showNotification('Passwords do not match', 'error');
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/api/auth/reset-password`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                code: resetData.code,
                new_password: resetData.new_password
            })
        });

        const data = await response.json();

        if (response.ok) {
            showNotification('Password reset successfully!', 'success');
            closeModal('resetPasswordModal');
            showLogin();
        } else {
            showNotification(data.error || 'Password reset failed', 'error');
        }
    } catch (error) {
        showNotification('Network error. Please try again.', 'error');
    }
}

async function loadUserProfile() {
    if (!authToken) return;

    try {
        const response = await fetch(`${API_BASE}/api/auth/profile`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });

        if (response.ok) {
            const data = await response.json();
            currentUser = data.user;
            // Store account creation date for calendar limits
            if (currentUser && currentUser.created_at) {
                accountCreationDate = new Date(currentUser.created_at);
            }
        }
    } catch (error) {
        console.error('Error loading user profile:', error);
    }
}

async function getUserLocation() {
    return new Promise((resolve, reject) => {
        if (!navigator.geolocation) {
            reject(new Error('Geolocation not supported'));
            return;
        }

        // Show location options UI
        showLocationOptions();

        navigator.geolocation.getCurrentPosition(
            async (position) => {
                try {
                    const lat = position.coords.latitude;
                    const lng = position.coords.longitude;

                    // Get timezone from coordinates
                    const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;

                    // Get city name from coordinates (simplified)
                    const city = await getCityFromCoordinates(lat, lng);

                    const locationData = {
                        lat: lat,
                        lng: lng,
                        timezone: timezone,
                        city: city
                    };

                    // Store detected location data
                    detectedLocationData = locationData;

                    // Show detected location in UI
                    showDetectedLocation(locationData);

                    resolve(locationData);
                } catch (error) {
                    reject(error);
                }
            },
            (error) => {
                // If location access is denied or fails, show city options
                console.log('Location detection failed:', error);
                showLocationOptions();
                reject(error);
            },
            {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 300000 // 5 minutes
            }
        );
    });
}

function showLocationOptions() {
    const locationOptions = document.getElementById('locationOptions');
    if (locationOptions) {
        locationOptions.style.display = 'block';
    }
}

function showDetectedLocation(locationData) {
    const locationDetails = document.getElementById('locationDetails');
    if (locationDetails) {
        locationDetails.innerHTML = `
            <div><strong>City:</strong> ${locationData.city}</div>
            <div><strong>Coordinates:</strong> ${locationData.lat.toFixed(4)}, ${locationData.lng.toFixed(4)}</div>
            <div><strong>Timezone:</strong> ${locationData.timezone}</div>
        `;
    }
}

function useDetectedLocation() {
    if (detectedLocationData.lat && detectedLocationData.lng) {
        selectedLocationData = detectedLocationData;
        showSelectedLocation(detectedLocationData);
    }
}

function selectCity(cityName, lat, lng, timezone) {
    const locationData = {
        lat: lat,
        lng: lng,
        timezone: timezone,
        city: cityName
    };

    selectedLocationData = locationData;
    showSelectedLocation(locationData);

    // Update button states
    document.querySelectorAll('.city-btn').forEach(btn => {
        btn.classList.remove('selected');
    });
    event.target.classList.add('selected');
}

function showSelectedLocation(locationData) {
    const selectedLocation = document.getElementById('selectedLocation');
    const selectedLocationDetails = document.getElementById('selectedLocationDetails');
    const locationOptions = document.getElementById('locationOptions');

    if (selectedLocation && selectedLocationDetails) {
        selectedLocationDetails.innerHTML = `
            <div><strong>City:</strong> ${locationData.city}</div>
            <div><strong>Coordinates:</strong> ${locationData.lat.toFixed(4)}, ${locationData.lng.toFixed(4)}</div>
            <div><strong>Timezone:</strong> ${locationData.timezone}</div>
        `;

        selectedLocation.style.display = 'block';
        if (locationOptions) {
            locationOptions.style.display = 'none';
        }
    }
}

function changeLocation() {
    const selectedLocation = document.getElementById('selectedLocation');
    const locationOptions = document.getElementById('locationOptions');

    if (selectedLocation && locationOptions) {
        selectedLocation.style.display = 'none';
        locationOptions.style.display = 'block';
    }
}

async function getCityFromCoordinates(lat, lng) {
    try {
        // Use a simple reverse geocoding service
        const response = await fetch(`https://api.bigdatacloud.net/data/reverse-geocode-client?latitude=${lat}&longitude=${lng}&localityLanguage=en`);
        const data = await response.json();

        if (data.city && data.countryName) {
            return `${data.city}, ${data.countryName}`;
        } else if (data.locality && data.countryName) {
            return `${data.locality}, ${data.countryName}`;
        } else {
            return `Location (${lat.toFixed(2)}, ${lng.toFixed(2)})`;
        }
    } catch (error) {
        console.log('Reverse geocoding failed:', error);
        return `Location (${lat.toFixed(2)}, ${lng.toFixed(2)})`;
    }
}

async function markPrayerQada(prayerId) {
    if (!authToken) {
        showNotification('Please login to mark prayers as Qada', 'error');
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/api/prayers/mark-qada`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({
                prayer_id: prayerId,
                notes: 'Marked as Qada by user'
            })
        });

        const data = await response.json();

        if (response.ok) {
            showNotification('Prayer marked as Qada successfully!', 'success');
            // Refresh prayer times and calendar to show updated status
            setTimeout(() => {
                loadPrayerTimes();
                // If we're viewing a specific day, reload that day's prayers
                if (selectedDate) {
                    loadSelectedDayPrayers(selectedDate);
                }
                // Refresh calendar to update dots
                loadCalendar();
            }, 1000);
        } else {
            showNotification(data.error || 'Failed to mark prayer as Qada', 'error');
        }
    } catch (error) {
        showNotification('Network error. Please try again.', 'error');
    }
}

// Prayer functions
let lastPrayerStates = {}; // Store previous prayer states for comparison

async function loadPrayerTimes() {
    if (!authToken) {
        document.getElementById('prayerTimes').innerHTML = '<div class="loading">Please login to view prayer times</div>';
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/api/prayers/times`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });

        if (response.ok) {
            const data = await response.json();
            // console.log('API Response:', data);
            
            // Check for prayer status changes and show notifications
            checkPrayerStatusChanges(data.prayers);
            
            displayPrayerTimes(data.prayers);
        } else {
            document.getElementById('prayerTimes').innerHTML = '<div class="loading">Error loading prayer times</div>';
        }
    } catch (error) {
        document.getElementById('prayerTimes').innerHTML = '<div class="loading">Error loading prayer times</div>';
    }
}

function checkPrayerStatusChanges(prayers) {
    const currentStates = {};
    
    prayers.forEach(prayer => {
        const prayerType = prayer.prayer_type;
        const timeStatus = prayer.time_status || 'unknown';
        const canComplete = prayer.can_complete || false;
        const isCompleted = prayer.completed || false;
        
        currentStates[prayerType] = {
            timeStatus,
            canComplete,
            isCompleted,
            prayerTime: prayer.prayer_time
        };
    });
    
    // Check for changes and show notifications
    Object.keys(currentStates).forEach(prayerType => {
        const current = currentStates[prayerType];
        const previous = lastPrayerStates[prayerType];
        
        if (previous) {
            // Check if prayer just became available
            if (!previous.canComplete && current.canComplete && current.timeStatus === 'during') {
                showNotification(`🕌 ${prayerType} prayer time is now available! You can mark it as complete.`, 'success');
            }
            
            // Check if prayer was just completed
            if (!previous.isCompleted && current.isCompleted) {
                showNotification(`✅ ${prayerType} prayer marked as complete!`, 'success');
            }
            
            // Check if prayer window just closed
            if (previous.timeStatus === 'during' && current.timeStatus === 'after' && !current.isCompleted) {
                showNotification(`⏰ ${prayerType} prayer window has closed. You can still mark it as Qada.`, 'warning');
            }
        }
    });
    
    // Update stored states
    lastPrayerStates = currentStates;
}

function displayPrayerTimes(prayers) {
    const container = document.getElementById('prayerTimes');
    const dateElement = document.getElementById('prayerDate');

    if (!prayers || prayers.length === 0) {
        container.innerHTML = '<div class="loading">No prayer times available</div>';
        dateElement.textContent = 'No date available';
        return;
    }

    // Display today's date
    const today = new Date();
    const options = {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    };
    dateElement.textContent = today.toLocaleDateString('en-US', options);

        const prayerCards = prayers.map(prayer => {
        // Use the new three-state system from backend
        const prayerStatus = prayer.prayer_status || 'not_completed';
        const statusColor = prayer.status_color || 'red';
        const statusText = prayer.status_text || 'Not Completed';
        const canComplete = prayer.can_complete || false;
        const canMarkQada = prayer.can_mark_qada || false;
        const timeStatus = prayer.time_status || 'unknown';
        const timeWindow = prayer.time_window || {};
        const currentTime = prayer.current_time || '';

        // Debug logging (remove in production)
        console.log(`Prayer ${prayer.prayer_type}:`, {
            prayerStatus: prayerStatus,
            statusColor: statusColor,
            statusText: statusText,
            canComplete: canComplete,
            canMarkQada: canMarkQada,
            timeStatus: timeStatus,
            timeWindow: timeWindow,
            currentTime: currentTime,
            prayerData: prayer
        });

        // Determine card styling and button behavior based on three-state system
        let cardClass = '';
        let buttonText = '';
        let buttonDisabled = false;
        let buttonClass = 'complete-btn';

        switch (prayerStatus) {
            case 'future':
                cardClass = 'future'; // Gray - before prayer time
                buttonText = 'Future';
                buttonDisabled = true;
                break;
                
            case 'pending':
                cardClass = 'in-progress'; // Blue - can go to completed
                if (canComplete) {
                    buttonText = 'Mark as Complete';
                    buttonClass = 'complete-btn';
                    buttonDisabled = false;
                } else {
                    buttonText = 'In Progress';
                    buttonDisabled = true;
                }
                break;
                
            case 'missed':
                cardClass = 'missed'; // Red - can go to qada
                if (canMarkQada) {
                    buttonText = 'Mark as Qada';
                    buttonClass = 'qada-btn';
                    buttonDisabled = false;
                } else {
                    buttonText = 'Missed';
                    buttonDisabled = true;
                }
                break;
                
            case 'completed':
                cardClass = 'completed'; // Green - terminal state
                buttonText = 'Completed';
                buttonDisabled = true;
                break;
                
            case 'qada':
                cardClass = 'qada'; // Yellow - terminal state
                buttonText = 'Qada';
                buttonDisabled = true;
                break;
                
            default:
                cardClass = 'missed'; // Red - default to missed
                buttonText = 'Missed';
                buttonDisabled = true;
        }

        // Debug button state (remove in production)
        console.log(`Button for ${prayer.prayer_type}:`, {
            buttonClass,
            buttonText,
            buttonDisabled,
            canMarkQada,
            timeStatus
        });

        const buttonHTML = `
            <button class="${buttonClass}"
                    onclick="${buttonClass === 'qada-btn' ? 'markPrayerQada' : 'completePrayer'}(${prayer.id})"
                    ${buttonDisabled ? 'disabled' : ''}>
                ${buttonText}
            </button>
        `;

        // Add time window information to the prayer card
        const timeWindowInfo = timeWindow.start_time && timeWindow.end_time ? 
            `<div class="time-window-info">
                <small>Window: ${timeWindow.start_time} - ${timeWindow.end_time}</small>
                <small>Current: ${currentTime}</small>
            </div>` : '';

        return `
            <div class="prayer-card ${cardClass}">
                <div class="prayer-name">${prayer.prayer_type}</div>
                <div class="prayer-time">${prayer.prayer_time}</div>
                <div class="prayer-status">${statusText}</div>
                ${buttonHTML}
                ${timeWindowInfo}
            </div>
        `;
    }).join('');

    container.innerHTML = prayerCards;
}

async function completePrayer(prayerId) {
    if (!authToken) return;

    try {
        const response = await fetch(`${API_BASE}/api/prayers/complete`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({ prayer_id: prayerId })
        });

        if (response.ok) {
            showNotification('Prayer marked as completed!', 'success');
            // Small delay to ensure database is updated
            setTimeout(() => {
                loadPrayerTimes(); // Refresh the prayer times
            }, 100);
        } else {
            const data = await response.json();
            showNotification(data.error || 'Failed to complete prayer', 'error');
        }
    } catch (error) {
        showNotification('Network error. Please try again.', 'error');
    }
}

// Dashboard functions
async function loadDashboard() {
    if (!authToken) {
        // Hide calendar and show login message
        document.querySelector('.weekly-calendar-header').style.display = 'none';
        document.querySelector('.weekly-calendar-container').style.display = 'none';
        document.querySelector('.selected-day-prayers').style.display = 'none';
        document.getElementById('dashboardStats').innerHTML = '<div class="loading">Please login to view dashboard</div>';
        return;
    }

    // Show calendar for logged-in users
    document.querySelector('.weekly-calendar-header').style.display = 'flex';
    document.querySelector('.weekly-calendar-container').style.display = 'block';

    try {
        const response = await fetch(`${API_BASE}/api/dashboard/stats`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });

        if (response.ok) {
            const data = await response.json();
            displayDashboardStats(data);
        } else {
            document.getElementById('dashboardStats').innerHTML = '<div class="loading">Error loading dashboard</div>';
        }
    } catch (error) {
        document.getElementById('dashboardStats').innerHTML = '<div class="loading">Error loading dashboard</div>';
    }

    // Load weekly calendar
    loadWeeklyCalendar();
}

function displayDashboardStats(stats) {
    const container = document.getElementById('dashboardStats');

    const statsHTML = `
        <div class="stat-card">
            <div class="stat-number">${stats.overall.completion_rate}%</div>
            <div class="stat-label">Completion Rate</div>
            <div class="stat-description">Since account creation (${stats.period.days} days)</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">${stats.overall.completed_prayers}</div>
            <div class="stat-label">Prayers Completed</div>
            <div class="stat-description">Out of ${stats.overall.total_prayers} total</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">${stats.current_streak}</div>
            <div class="stat-label">Current Streak</div>
            <div class="stat-description">Consecutive days</div>
        </div>
    `;

    container.innerHTML = statsHTML;
}

// Weekly Calendar functions
let currentWeekStart = new Date();
let selectedDate = null;
let accountCreationDate = null;
let currentMobileDayIndex = 0; // For mobile day navigation
let isMobileView = false;

function loadWeeklyCalendar() {
    if (!authToken) {
        // Calendar should be hidden by loadDashboard, but just in case
        const calendarGrid = document.getElementById('weeklyCalendarGrid');
        if (calendarGrid) {
            calendarGrid.innerHTML = '<div class="loading">Please login to view calendar</div>';
        }
        return;
    }

    // Set current week start to Monday of current week
    const today = new Date();
    const dayOfWeek = today.getDay();
    const daysToMonday = dayOfWeek === 0 ? -6 : 1 - dayOfWeek; // Sunday = 0, so go back 6 days
    currentWeekStart = new Date(today);
    currentWeekStart.setDate(today.getDate() + daysToMonday);
    currentWeekStart.setHours(0, 0, 0, 0);

    // If account creation date is set and current week is before it,
    // set week to account creation week
    if (accountCreationDate && currentWeekStart < accountCreationDate) {
        const accountDay = accountCreationDate.getDay();
        const accountDaysToMonday = accountDay === 0 ? -6 : 1 - accountDay;
        currentWeekStart = new Date(accountCreationDate);
        currentWeekStart.setDate(accountCreationDate.getDate() + accountDaysToMonday);
        currentWeekStart.setHours(0, 0, 0, 0);
    }

    updateWeekDisplay();
    generateWeeklyCalendar();
    
    // Set today as default selected date if no date is selected
    if (!selectedDate) {
        const today = new Date();
        selectedDate = formatDateString(today);
        loadSelectedDayPrayers(selectedDate);
    }
}

function generateCalendar(year, month) {
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const daysInMonth = lastDay.getDate();
    const startingDayOfWeek = firstDay.getDay();

    const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

    let calendarHTML = '';

    // Add day headers
    dayNames.forEach(day => {
        calendarHTML += `<div class="calendar-day-header">${day}</div>`;
    });

    // Add empty cells for days before the first day of the month
    for (let i = 0; i < startingDayOfWeek; i++) {
        const prevMonth = new Date(year, month, 0);
        const dayNumber = prevMonth.getDate() - startingDayOfWeek + i + 1;
        calendarHTML += `<div class="calendar-day other-month">${dayNumber}</div>`;
    }

    // Add days of the month
    for (let day = 1; day <= daysInMonth; day++) {
        const date = new Date(year, month, day);
        const isToday = isSameDate(date, new Date());
        const isSelected = selectedDate && isSameDate(date, selectedDate);

        // Check if this date is before account creation
        const isBeforeAccountCreation = accountCreationDate && date < accountCreationDate;

        calendarHTML += `
            <div class="calendar-day ${isToday ? 'today' : ''} ${isSelected ? 'selected' : ''} ${isBeforeAccountCreation ? 'disabled' : ''}"
                 ${isBeforeAccountCreation ? '' : `onclick="selectDate('${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}')"`}>
                <div class="calendar-day-number">${day}</div>
                <div class="calendar-day-prayers" id="prayers-${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}">
                    ${isBeforeAccountCreation ? '<div class="prayer-dot disabled"></div>' : '<!-- Prayer dots will be loaded here -->'}
                </div>
            </div>
        `;
    }

    // Add empty cells for days after the last day of the month
    const remainingCells = 42 - (startingDayOfWeek + daysInMonth);
    for (let i = 1; i <= remainingCells; i++) {
        calendarHTML += `<div class="calendar-day other-month">${i}</div>`;
    }

    document.getElementById('weeklyCalendarGrid').innerHTML = calendarHTML;
    loadPrayerDataForWeek();
}

function updateWeekDisplay() {
    const weekEnd = new Date(currentWeekStart);
    weekEnd.setDate(currentWeekStart.getDate() + 6);
    
    const monthNames = ['January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'];
    
    const startMonth = monthNames[currentWeekStart.getMonth()];
    const startDay = currentWeekStart.getDate();
    const startYear = currentWeekStart.getFullYear();
    
    const endMonth = monthNames[weekEnd.getMonth()];
    const endDay = weekEnd.getDate();
    const endYear = weekEnd.getFullYear();
    
    let weekTitle;
    if (startMonth === endMonth && startYear === endYear) {
        weekTitle = `Week of ${startMonth} ${startDay}, ${startYear}`;
    } else if (startYear === endYear) {
        weekTitle = `Week of ${startMonth} ${startDay} - ${endMonth} ${endDay}, ${startYear}`;
    } else {
        weekTitle = `Week of ${startMonth} ${startDay}, ${startYear} - ${endMonth} ${endDay}, ${endYear}`;
    }
    
    document.getElementById('weekTitle').textContent = weekTitle;
    
    // Update subtitle based on current week
    const today = new Date();
    const isCurrentWeek = currentWeekStart <= today && weekEnd >= today;
    document.getElementById('weekSubtitle').textContent = isCurrentWeek ? 
        'Track your daily prayers' : 'View past prayer history';
}

function generateWeeklyCalendar() {
    const dayNames = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    const dayNamesFull = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
    const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    
    // Check if mobile view
    isMobileView = window.innerWidth <= 480;
    
    let calendarHTML = '';
    
    for (let i = 0; i < 7; i++) {
        const currentDate = new Date(currentWeekStart);
        currentDate.setDate(currentWeekStart.getDate() + i);
        
        const dateString = formatDateString(currentDate);
        const isToday = isSameDate(currentDate, new Date());
        const isSelected = selectedDate && (selectedDate === dateString || isSameDate(currentDate, new Date(selectedDate)));
        const isBeforeAccountCreation = accountCreationDate && currentDate < accountCreationDate;
        const isFuture = currentDate > new Date();
        
        // Determine base classes
        let cardClasses = 'weekly-day-card';
        if (isToday) cardClasses += ' today';
        if (isSelected) cardClasses += ' selected';
        if (isBeforeAccountCreation) cardClasses += ' disabled';
        if (isFuture) cardClasses += ' pending';
        
        // For mobile, only show the current day
        const shouldShow = !isMobileView || i === currentMobileDayIndex;
        const displayStyle = shouldShow ? '' : 'style="display: none;"';
        
        calendarHTML += `
            <div class="${cardClasses}" id="card-${dateString}" ${displayStyle}
                 ${isBeforeAccountCreation ? '' : `onclick="selectDate('${dateString}')"`}>
                <div class="weekly-day-header">
                    <div class="weekly-day-name">${dayNames[i]}</div>
                    <div class="weekly-day-number">${currentDate.getDate()}</div>
                </div>
                <div class="weekly-day-prayers" id="prayers-${dateString}">
                    ${isBeforeAccountCreation ? 
                        '<div class="prayer-status-indicator future">Before Account</div>' :
                        isFuture ?
                        '<div class="prayer-status-indicator future">Future</div>' :
                        '<!-- Prayer status will be loaded here -->'
                    }
                </div>
                <div class="weekly-day-summary" id="summary-${dateString}">
                    <!-- Summary will be loaded here -->
                </div>
            </div>
        `;
    }
    
    document.getElementById('weeklyCalendarGrid').innerHTML = calendarHTML;
    
    // Show/hide mobile navigation
    const mobileNav = document.getElementById('mobileDayNav');
    if (isMobileView) {
        mobileNav.style.display = 'flex';
        updateMobileDayNavigation();
    } else {
        mobileNav.style.display = 'none';
    }
    
    loadPrayerDataForWeek();
}

function isSameDate(date1, date2) {
    return date1.getFullYear() === date2.getFullYear() &&
           date1.getMonth() === date2.getMonth() &&
           date1.getDate() === date2.getDate();
}

function formatDateString(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}

function previousWeek() {
    currentWeekStart.setDate(currentWeekStart.getDate() - 7);
    updateWeekDisplay();
    generateWeeklyCalendar();
    // Reset mobile day index to first day of new week
    currentMobileDayIndex = 0;
    // Clear selected date to avoid showing old prayer times
    selectedDate = null;
    hideSelectedDayPrayers();
}

function nextWeek() {
    currentWeekStart.setDate(currentWeekStart.getDate() + 7);
    updateWeekDisplay();
    generateWeeklyCalendar();
    // Reset mobile day index to first day of new week
    currentMobileDayIndex = 0;
    // Clear selected date to avoid showing old prayer times
    selectedDate = null;
    hideSelectedDayPrayers();
}

// Mobile day navigation functions
function previousDay() {
    if (currentMobileDayIndex > 0) {
        currentMobileDayIndex--;
        showMobileDay(currentMobileDayIndex);
        updateMobileDayNavigation();
    }
}

function nextDay() {
    if (currentMobileDayIndex < 6) {
        currentMobileDayIndex++;
        showMobileDay(currentMobileDayIndex);
        updateMobileDayNavigation();
    }
}

function showMobileDay(dayIndex) {
    // Hide all day cards
    const allCards = document.querySelectorAll('.weekly-day-card');
    allCards.forEach(card => card.style.display = 'none');
    
    // Show the selected day card
    const targetDate = new Date(currentWeekStart);
    targetDate.setDate(currentWeekStart.getDate() + dayIndex);
    const dateString = formatDateString(targetDate);
    const targetCard = document.getElementById(`card-${dateString}`);
    if (targetCard) {
        targetCard.style.display = 'block';
    }
    
    // Update selected date and load prayer times
    selectedDate = dateString;
    loadSelectedDayPrayers(dateString);
}

function updateMobileDayNavigation() {
    const dayNamesFull = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
    const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    
    const currentDate = new Date(currentWeekStart);
    currentDate.setDate(currentWeekStart.getDate() + currentMobileDayIndex);
    
    const dayName = dayNamesFull[currentMobileDayIndex];
    const monthName = monthNames[currentDate.getMonth()];
    const dayNumber = currentDate.getDate();
    
    document.getElementById('mobileDayTitle').textContent = `${dayName}, ${monthName} ${dayNumber}`;
    
    // Update navigation buttons
    const prevBtn = document.getElementById('prevDayBtn');
    const nextBtn = document.getElementById('nextDayBtn');
    
    prevBtn.disabled = currentMobileDayIndex === 0;
    nextBtn.disabled = currentMobileDayIndex === 6;
    
    // Update subtitle with prayer status
    const dateString = formatDateString(currentDate);
    const summaryElement = document.getElementById(`summary-${dateString}`);
    if (summaryElement && summaryElement.textContent) {
        document.getElementById('mobileDaySubtitle').textContent = summaryElement.textContent;
    } else {
        document.getElementById('mobileDaySubtitle').textContent = 'Loading...';
    }
}

function loadPrayerDataForWeek() {
    // Load prayer data for the current week
    for (let i = 0; i < 7; i++) {
        const currentDate = new Date(currentWeekStart);
        currentDate.setDate(currentWeekStart.getDate() + i);
        const dateString = formatDateString(currentDate);
        
        // Skip if before account creation or future
        if (accountCreationDate && currentDate < accountCreationDate) continue;
        if (currentDate > new Date()) continue;
        
        loadPrayerDataForDate(dateString);
    }
}

function loadPrayerDataForDate(dateString) {
    if (!authToken) return;
    
    console.log(`Loading prayer data for ${dateString}`);
    
    fetch(`${API_BASE}/api/prayers/times/${dateString}`, {
        headers: {
            'Authorization': `Bearer ${authToken}`
        }
    })
    .then(response => {
        console.log(`Response status for ${dateString}:`, response.status);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log(`API response for ${dateString}:`, data);
        if (data.prayers) {
            updatePrayerStatusForDate(dateString, data.prayers);
        } else {
            console.log(`No prayers data for ${dateString}:`, data);
        }
    })
    .catch(error => {
        console.error('Error loading prayer data:', error);
    });
}

function updatePrayerStatusForDate(dateString, prayers) {
    const prayersContainer = document.getElementById(`prayers-${dateString}`);
    const summaryContainer = document.getElementById(`summary-${dateString}`);
    const cardElement = document.getElementById(`card-${dateString}`);
    
    if (!prayersContainer || !prayers || !cardElement) return;
    
    // Debug logging
    console.log(`Prayer data for ${dateString}:`, prayers);
    
    // Use the new 5-status system from backend
    const totalCount = prayers.length;
    const futureCount = prayers.filter(prayer => prayer.prayer_status === 'future').length;
    const pendingCount = prayers.filter(prayer => prayer.prayer_status === 'pending').length;
    const missedCount = prayers.filter(prayer => prayer.prayer_status === 'missed').length;
    const completedCount = prayers.filter(prayer => prayer.prayer_status === 'completed').length;
    const qadaCount = prayers.filter(prayer => prayer.prayer_status === 'qada').length;
    
    // Debug logging
    console.log(`Status for ${dateString}: future=${futureCount}, pending=${pendingCount}, missed=${missedCount}, completed=${completedCount}, qada=${qadaCount}, total=${totalCount}`);
    
    // Remove existing status classes
    cardElement.classList.remove('all-complete', 'has-qada', 'all-missed', 'pending', 'future', 'mixed');
    
    let statusClass, statusText, summaryText, cardStatusClass;
    
    // Determine overall day status based on the 5-status system
    if (futureCount === totalCount) {
        // All prayers are future (before prayer times)
        statusClass = 'future';
        statusText = 'Future';
        summaryText = 'Prayers not started';
        cardStatusClass = 'future';
    } else if (completedCount === totalCount) {
        // All prayers completed
        statusClass = 'completed';
        statusText = 'All Complete';
        summaryText = `${completedCount}/${totalCount} prayers`;
        cardStatusClass = 'all-complete';
    } else if (qadaCount === totalCount) {
        // All prayers are Qada
        statusClass = 'qada';
        statusText = 'All Qada';
        summaryText = `${qadaCount} Qada prayers`;
        cardStatusClass = 'has-qada';
    } else if (missedCount === totalCount) {
        // All prayers missed
        statusClass = 'missed';
        statusText = 'All Missed';
        summaryText = `${missedCount} missed prayers`;
        cardStatusClass = 'all-missed';
    } else if (pendingCount > 0) {
        // Some prayers are pending (in progress)
        statusClass = 'pending';
        statusText = 'In Progress';
        summaryText = `${pendingCount} pending prayers`;
        cardStatusClass = 'pending';
    } else {
        // Mixed status
        const completedTotal = completedCount + qadaCount;
        statusClass = 'mixed';
        statusText = `${completedTotal}/${totalCount} Complete`;
        summaryText = `${completedCount} completed, ${qadaCount} qada, ${missedCount} missed`;
        cardStatusClass = 'has-qada';
    }
    
    // Debug logging
    console.log(`Applied status for ${dateString}: ${cardStatusClass}`);
    
    // Apply the card status class
    if (cardStatusClass) {
        cardElement.classList.add(cardStatusClass);
    }
    
    prayersContainer.innerHTML = `<div class="prayer-status-indicator ${statusClass}">${statusText}</div>`;
    summaryContainer.innerHTML = summaryText;
    
    // Update mobile navigation if in mobile view
    if (isMobileView) {
        updateMobileDayNavigation();
    }
}

// Handle window resize for mobile/desktop switching
window.addEventListener('resize', function() {
    if (typeof generateWeeklyCalendar === 'function') {
        generateWeeklyCalendar();
    }
});

async function loadPrayerDataForMonth(year, month) {
    if (!authToken) return;

    const daysInMonth = new Date(year, month + 1, 0).getDate();

    for (let day = 1; day <= daysInMonth; day++) {
        const date = new Date(year, month, day);

        // Skip dates before account creation
        if (accountCreationDate && date < accountCreationDate) {
            continue;
        }

        const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;

        try {
            const response = await fetch(`${API_BASE}/api/prayers/times/${dateStr}`, {
                headers: {
                    'Authorization': `Bearer ${authToken}`
                }
            });

            if (response.ok) {
                const data = await response.json();
                updatePrayerDots(dateStr, data.prayers);
            }
        } catch (error) {
            console.error(`Error loading prayer data for ${dateStr}:`, error);
        }
    }
}

function updatePrayerDots(dateStr, prayers) {
    const container = document.getElementById(`prayers-${dateStr}`);
    if (!container) return;

    let dotsHTML = '';
    prayers.forEach(prayer => {
        let status = 'pending'; // Default orange for pending

        if (prayer.completed) {
            if (prayer.completion && prayer.completion.is_qada) {
                status = 'qada'; // Yellow for Qada
            } else {
                status = 'completed'; // Green for completed
            }
        } else if (prayer.is_missed) {
            status = 'missed'; // Red for missed
        }

        dotsHTML += `<div class="prayer-dot ${status}"></div>`;
    });

    container.innerHTML = dotsHTML;
}

function previousMonth() {
    const newDate = new Date(currentCalendarDate);
    newDate.setMonth(newDate.getMonth() - 1);

    // Don't go before account creation date
    if (accountCreationDate && newDate < accountCreationDate) {
        return;
    }

    currentCalendarDate = newDate;
    loadCalendar();
}

function nextMonth() {
    const newDate = new Date(currentCalendarDate);
    newDate.setMonth(newDate.getMonth() + 1);

    // Don't go beyond current month
    const today = new Date();
    if (newDate > today) {
        return;
    }

    currentCalendarDate = newDate;
    loadCalendar();
}

async function selectDate(dateStr) {
    const selectedDateObj = new Date(dateStr);

    // Don't allow selection of dates before account creation
    if (accountCreationDate && selectedDateObj < accountCreationDate) {
        return;
    }

    // Store the date string, not the Date object
    selectedDate = dateStr;

    // Update calendar display
    document.querySelectorAll('.calendar-day').forEach(day => {
        day.classList.remove('selected');
    });

    // Highlight selected day
    const selectedDayElement = document.querySelector(`[onclick="selectDate('${dateStr}')"]`);
    if (selectedDayElement) {
        selectedDayElement.classList.add('selected');
    }

    // Show selected day prayers
    await loadSelectedDayPrayers(dateStr);
}

function hideSelectedDayPrayers() {
    const selectedDayPrayers = document.getElementById('selectedDayPrayers');
    if (selectedDayPrayers) {
        selectedDayPrayers.style.display = 'none';
    }
}

async function loadSelectedDayPrayers(dateStr) {
    if (!authToken) {
        return;
    }

    const selectedDayPrayers = document.getElementById('selectedDayPrayers');
    const selectedDayTitle = document.getElementById('selectedDayTitle');
    const selectedDayContent = document.getElementById('selectedDayContent');

    if (selectedDayPrayers) {
        selectedDayPrayers.style.display = 'block';
    }

    if (selectedDayTitle) {
        selectedDayTitle.textContent = `Prayer Times for ${formatDate(dateStr)}`;
    }

    if (selectedDayContent) {
        selectedDayContent.innerHTML = '<div class="loading">Loading prayer times...</div>';
    }

    try {
        const response = await fetch(`${API_BASE}/api/prayers/times/${dateStr}`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });

        if (response.ok) {
            const data = await response.json();
            displaySelectedDayPrayers(data.prayers);
        } else {
            selectedDayContent.innerHTML = '<div class="loading">Error loading prayer times</div>';
        }
    } catch (error) {
        selectedDayContent.innerHTML = '<div class="loading">Error loading prayer times</div>';
    }
}

function displaySelectedDayPrayers(prayers) {
    const container = document.getElementById('selectedDayContent');

    const prayersHTML = prayers.map(prayer => {
        // Use the new 5-status system from backend
        const prayerStatus = prayer.prayer_status || 'not_completed';
        const canMarkQada = prayer.can_mark_qada || false;
        const canComplete = prayer.can_complete || false;
        const timeWindow = prayer.time_window || {};
        const currentTime = prayer.current_time || '';

        let status = prayerStatus;
        let statusText = '';

        // Map status to display text
        switch (prayerStatus) {
            case 'future':
                statusText = '⏳ Future';
                break;
            case 'pending':
                statusText = '⏰ Available Now';
                break;
            case 'missed':
                statusText = '❌ Missed';
                break;
            case 'completed':
                statusText = '✅ Completed';
                break;
            case 'qada':
                statusText = '🔄 Qada';
                break;
            default:
                statusText = '❓ Unknown';
        }

        let buttonHTML = '';
        // Show appropriate button based on prayer status
        if (prayerStatus === 'pending' && canComplete) {
            buttonHTML = `
                <button class="complete-btn-small" onclick="completePrayer(${prayer.id})">
                    <i class="fas fa-check"></i> Mark as Complete
                </button>
            `;
        } else if (prayerStatus === 'missed' && canMarkQada) {
            buttonHTML = `
                <button class="qada-btn-small" onclick="markPrayerQada(${prayer.id})">
                    <i class="fas fa-redo"></i> Mark as Qada
                </button>
            `;
        }

        // Add time window information
        const timeWindowInfo = timeWindow.start_time && timeWindow.end_time ? 
            `<div class="time-window-info-small">
                <small>Window: ${timeWindow.start_time} - ${timeWindow.end_time}</small>
                <small>Current: ${currentTime}</small>
            </div>` : '';

        return `
            <div class="selected-day-prayer ${status}">
                <div class="selected-day-prayer-name">${prayer.prayer_type}</div>
                <div class="selected-day-prayer-time">${prayer.prayer_time}</div>
                <div class="selected-day-prayer-status">${statusText}</div>
                ${buttonHTML}
                ${timeWindowInfo}
            </div>
        `;
    }).join('');

    container.innerHTML = prayersHTML;
}

function formatDate(dateStr) {
    const date = new Date(dateStr);
    const options = {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    };
    return date.toLocaleDateString('en-US', options);
}

// Family functions
async function loadFamilyMembers() {
    if (!authToken) {
        document.getElementById('familyMembers').innerHTML = '<div class="loading">Please login to view family members</div>';
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/api/social/family`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });

        if (response.ok) {
            const data = await response.json();
            displayFamilyMembers(data.family_members);
        } else {
            document.getElementById('familyMembers').innerHTML = '<div class="loading">Error loading family members</div>';
        }
    } catch (error) {
        document.getElementById('familyMembers').innerHTML = '<div class="loading">Error loading family members</div>';
    }
}

function displayFamilyMembers(members) {
    const container = document.getElementById('familyMembers');

    if (!members || members.length === 0) {
        container.innerHTML = '<div class="loading">No family members added yet</div>';
        return;
    }

    const membersHTML = members.map(member => `
        <div class="family-card">
            <div class="family-info">
                <h3>${member.name}</h3>
                <p>${member.relationship}</p>
                ${member.email ? `<p>${member.email}</p>` : ''}
                ${member.phone_number ? `<p>${member.phone_number}</p>` : ''}
            </div>
            <div class="family-actions">
                <button onclick="editFamilyMember(${member.id})" title="Edit">
                    <i class="fas fa-edit"></i>
                </button>
                <button onclick="deleteFamilyMember(${member.id})" title="Delete">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        </div>
    `).join('');

    container.innerHTML = membersHTML;
}

async function handleAddFamily(e) {
    e.preventDefault();

    if (!authToken) {
        showNotification('Please login to add family members', 'error');
        return;
    }

    const formData = new FormData(e.target);
    const familyData = {
        name: formData.get('name'),
        relationship: formData.get('relationship'),
        email: formData.get('email'),
        phone_number: formData.get('phone_number'),
        reminder_enabled: formData.get('reminder_enabled') === 'on'
    };

    try {
        const response = await fetch(`${API_BASE}/api/social/family`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify(familyData)
        });

        if (response.ok) {
            showNotification('Family member added successfully!', 'success');
            closeModal('addFamilyModal');
            e.target.reset();
            loadFamilyMembers();
        } else {
            const data = await response.json();
            showNotification(data.error || 'Failed to add family member', 'error');
        }
    } catch (error) {
        showNotification('Network error. Please try again.', 'error');
    }
}

async function deleteFamilyMember(memberId) {
    if (!authToken) return;

    if (!confirm('Are you sure you want to delete this family member?')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/api/social/family/${memberId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });

        if (response.ok) {
            showNotification('Family member deleted successfully!', 'success');
            loadFamilyMembers();
        } else {
            const data = await response.json();
            showNotification(data.error || 'Failed to delete family member', 'error');
        }
    } catch (error) {
        showNotification('Network error. Please try again.', 'error');
    }
}

// Profile functions
async function loadProfile() {
    if (!authToken) {
        document.getElementById('profileContent').innerHTML = '<div class="loading">Please login to view profile</div>';
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/api/auth/profile`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });

        if (response.ok) {
            const data = await response.json();
            displayProfile(data.user);
        } else {
            document.getElementById('profileContent').innerHTML = '<div class="loading">Error loading profile</div>';
        }
    } catch (error) {
        document.getElementById('profileContent').innerHTML = '<div class="loading">Error loading profile</div>';
    }
}

function displayProfile(user) {
    const container = document.getElementById('profileContent');

    const profileHTML = `
        <div class="profile-form">
            <div class="form-group">
                <label>Username</label>
                <input type="text" value="${user.username}" readonly>
            </div>
            <div class="form-group">
                <label>Email</label>
                <input type="email" value="${user.email}" readonly>
            </div>
            <div class="form-group">
                <label>First Name</label>
                <input type="text" value="${user.first_name}" readonly>
            </div>
            <div class="form-group">
                <label>Last Name</label>
                <input type="text" value="${user.last_name}" readonly>
            </div>
            <div class="form-group">
                <label>Phone Number</label>
                <input type="tel" value="${user.phone_number || ''}" readonly>
            </div>
            <div class="form-group">
                <label>Location (Latitude)</label>
                <input type="number" id="locationLat" value="${user.location_lat || ''}" step="0.0001" placeholder="e.g., 12.9716">
            </div>
            <div class="form-group">
                <label>Location (Longitude)</label>
                <input type="number" id="locationLng" value="${user.location_lng || ''}" step="0.0001" placeholder="e.g., 77.5946">
            </div>
            <div class="form-group">
                <label>Timezone</label>
                <input type="text" id="timezone" value="${user.timezone || 'Asia/Kolkata'}" placeholder="e.g., Asia/Kolkata">
            </div>
            <div class="form-group">
                <label>City</label>
                <input type="text" id="city" value="${user.city || ''}" placeholder="e.g., Bangalore">
            </div>
            <div class="form-group">
                <label>Country</label>
                <input type="text" id="country" value="${user.country || ''}" placeholder="e.g., India">
            </div>
            <div class="form-group">
                <label>Language</label>
                <select id="language">
                    <option value="ar" ${user.language === 'ar' ? 'selected' : ''}>العربية (Arabic)</option>
                    <option value="en" ${user.language === 'en' ? 'selected' : ''}>English</option>
                </select>
            </div>
            <div class="form-group">
                <label>Fiqh Method</label>
                <select id="fiqh_method">
                    <option value="shafi" ${user.fiqh_method === 'shafi' ? 'selected' : ''}>Shafi'i</option>
                    <option value="hanafi" ${user.fiqh_method === 'hanafi' ? 'selected' : ''}>Hanafi</option>
                    <option value="maliki" ${user.fiqh_method === 'maliki' ? 'selected' : ''}>Maliki</option>
                    <option value="hanbali" ${user.fiqh_method === 'hanbali' ? 'selected' : ''}>Hanbali</option>
                </select>
            </div>
            <div class="form-group">
                <label>
                    <input type="checkbox" id="email_notifications" ${user.email_notifications ? 'checked' : ''}>
                    Email Notifications
                </label>
            </div>
            <div class="form-group">
                <button class="btn btn-secondary" onclick="setBangaloreLocation()">Set to Bangalore, India</button>
                <button class="btn btn-primary" onclick="updateProfile()">Update Profile</button>
            </div>
        </div>
        <div class="text-center mt-20">
            <button class="btn btn-primary" onclick="logout()">Logout</button>
        </div>
    `;

    container.innerHTML = profileHTML;
}

function setBangaloreLocation() {
    document.getElementById('locationLat').value = '12.9716';
    document.getElementById('locationLng').value = '77.5946';
    document.getElementById('timezone').value = 'Asia/Kolkata';
    showNotification('Location set to Bangalore, India', 'success');
}

async function updateProfile() {
    if (!authToken) {
        showNotification('Please login to update profile', 'error');
        return;
    }

    const locationLat = parseFloat(document.getElementById('locationLat').value);
    const locationLng = parseFloat(document.getElementById('locationLng').value);
    const timezone = document.getElementById('timezone').value;
    const city = document.getElementById('city').value;
    const country = document.getElementById('country').value;
    const language = document.getElementById('language').value;
    const fiqh_method = document.getElementById('fiqh_method').value;
    const email_notifications = document.getElementById('email_notifications').checked;

    if (!locationLat || !locationLng) {
        showNotification('Please enter valid latitude and longitude', 'error');
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/api/auth/profile`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({
                location_lat: locationLat,
                location_lng: locationLng,
                timezone: timezone,
                city: city,
                country: country,
                language: language,
                fiqh_method: fiqh_method,
                email_notifications: email_notifications
            })
        });

        if (response.ok) {
            showNotification('Profile updated successfully!', 'success');
            // Update current user data
            if (currentUser) {
                currentUser.location_lat = locationLat;
                currentUser.location_lng = locationLng;
                currentUser.timezone = timezone;
                currentUser.city = city;
                currentUser.country = country;
                currentUser.language = language;
                currentUser.fiqh_method = fiqh_method;
                currentUser.email_notifications = email_notifications;
            }
            // Reload prayer times
            loadPrayerTimes();
        } else {
            const data = await response.json();
            showNotification(data.error || 'Failed to update profile', 'error');
        }
    } catch (error) {
        showNotification('Network error. Please try again.', 'error');
    }
}

// Keep the old function for backward compatibility
async function updateLocation() {
    await updateProfile();
}

function logout() {
    authToken = null;
    currentUser = null;
    localStorage.removeItem('authToken');
    updateUIForLoggedOutUser();
    showSection('home');
    showNotification('Logged out successfully', 'success');
}

function updateUIForLoggedInUser() {
    // Hide login/register buttons and show user-specific content
    const heroButtons = document.querySelector('.hero-buttons');
    if (heroButtons) {
        heroButtons.innerHTML = `
            <button class="btn btn-primary" onclick="showSection('prayers')">View Prayers</button>
            <button class="btn btn-secondary" onclick="showSection('dashboard')">Dashboard</button>
        `;
    }

    // Hide call-to-action section for logged-in users
    const ctaSection = document.querySelector('.cta-section');
    if (ctaSection) {
        ctaSection.style.display = 'none';
    }

    // Update navigation to show user is logged in
    const navMenu = document.querySelector('.nav-menu');
    if (navMenu) {
        // Remove existing user info if any
        const existingUserInfo = navMenu.querySelector('.user-info');
        if (existingUserInfo) {
            existingUserInfo.remove();
        }

        // Add user info to navigation
        const userInfo = document.createElement('div');
        userInfo.className = 'user-info';
        userInfo.innerHTML = `
            <span style="color: #667eea; margin-right: 20px;">
                Welcome, ${currentUser ? currentUser.first_name : 'User'}!
            </span>
            <button class="btn btn-secondary" onclick="logout()" style="padding: 5px 15px; font-size: 0.9rem;">Logout</button>
        `;
        navMenu.appendChild(userInfo);
    }
}

function updateUIForLoggedOutUser() {
    // Show login/register buttons
    const heroButtons = document.querySelector('.hero-buttons');
    if (heroButtons) {
        heroButtons.innerHTML = `
            <button class="btn btn-primary" onclick="showLogin()">Get Started</button>
            <button class="btn btn-secondary" onclick="showRegister()">Create Account</button>
        `;
    }

    // Show call-to-action section for logged-out users
    const ctaSection = document.querySelector('.cta-section');
    if (ctaSection) {
        ctaSection.style.display = 'block';
    }

    // Remove user info from navigation
    const userInfo = document.querySelector('.user-info');
    if (userInfo) {
        userInfo.remove();
    }

    // Hide calendar elements if they exist
    const calendarHeader = document.querySelector('.calendar-header');
    const calendarContainer = document.querySelector('.calendar-container');
    const selectedDayPrayers = document.querySelector('.selected-day-prayers');

    if (calendarHeader) calendarHeader.style.display = 'none';
    if (calendarContainer) calendarContainer.style.display = 'none';
    if (selectedDayPrayers) selectedDayPrayers.style.display = 'none';
}

// Utility functions
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;

    // Style the notification
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        border-radius: 10px;
        color: white;
        font-weight: 500;
        z-index: 3000;
        animation: slideIn 0.3s ease;
        max-width: 300px;
    `;

    // Set background color based on type
    switch(type) {
        case 'success':
            notification.style.background = 'linear-gradient(135deg, #4CAF50 0%, #45a049 100%)';
            break;
        case 'error':
            notification.style.background = 'linear-gradient(135deg, #f44336 0%, #d32f2f 100%)';
            break;
        case 'warning':
            notification.style.background = 'linear-gradient(135deg, #ff9800 0%, #f57c00 100%)';
            break;
        default:
            notification.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
    }

    // Add to page
    document.body.appendChild(notification);

    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

// Add CSS for notifications
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;
document.head.appendChild(style);

// Load prayer times preview for home page
async function loadPrayerTimesPreview() {
    const prayerTimesGrid = document.getElementById('prayerTimesPreview');
    if (!prayerTimesGrid) return;

    try {
        // Use a default location (Bangalore, India) for preview
        const response = await fetch('https://api.aladhan.com/v1/timingsByCity?city=Bangalore&country=India&method=2');
        const data = await response.json();
        
        if (data.code === 200) {
            const timings = data.data.timings;
            const prayerCards = prayerTimesGrid.querySelectorAll('.prayer-time-card');
            
            const prayerMapping = {
                0: 'Fajr',
                1: 'Dhuhr', 
                2: 'Asr',
                3: 'Maghrib',
                4: 'Isha'
            };
            
            const prayerKeys = ['Fajr', 'Dhuhr', 'Asr', 'Maghrib', 'Isha'];
            
            prayerCards.forEach((card, index) => {
                const prayerName = card.querySelector('.prayer-name');
                const prayerTime = card.querySelector('.prayer-time');
                
                if (prayerName && prayerTime && prayerKeys[index]) {
                    const time = timings[prayerKeys[index]];
                    if (time) {
                        // Format time to HH:MM
                        const [hours, minutes] = time.split(':');
                        prayerTime.textContent = `${hours}:${minutes}`;
                    }
                }
            });
        }
    } catch (error) {
        console.log('Could not load prayer times for preview:', error);
        // Keep default times if API fails
    }
}

// Add smooth scrolling for anchor links
document.addEventListener('DOMContentLoaded', function() {
    // Add smooth scrolling to all anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Add animation on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);
    
    // Observe feature cards and other elements
    document.querySelectorAll('.feature-card, .prayer-time-card, .quote-card').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });
});
