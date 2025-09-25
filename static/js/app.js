// Global variables
let isSubmitting = false;
let currentLanguage = 'english'; // 默认英文

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    // Check if we need to scroll to top after page reload
    if (sessionStorage.getItem('scrollToTop') === 'true') {
        sessionStorage.removeItem('scrollToTop');
        // Smooth scroll to top
        setTimeout(() => {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }, 100);
    }
    
    // Initialize rating form
    const ratingForm = document.getElementById('rating-form');
    if (ratingForm) {
        ratingForm.addEventListener('submit', handleRatingSubmission);
    }
    
    // Initialize comment form
    const commentForm = document.getElementById('comment-form');
    if (commentForm) {
        commentForm.addEventListener('submit', handleCommentSubmission);
    }
    
    // Initialize language toggle button
    const translateBtn = document.getElementById('translateBtn');
    if (translateBtn) {
        translateBtn.addEventListener('click', toggleLanguage);
    }
});

// Handle rating submission
async function handleRatingSubmission(event) {
    event.preventDefault();
    
    if (isSubmitting) {
        return;
    }
    
    isSubmitting = true;
    
    // Get form data
    const formData = new FormData(event.target);
    const ratingData = {
        comparison_number: parseInt(formData.get('comparison_number')),
        hypothesis_A_id: parseInt(formData.get('hypothesis_A_id')),
        hypothesis_B_id: parseInt(formData.get('hypothesis_B_id')),
        novelty_score: parseInt(formData.get('novelty_score')),
        soundness_score: parseInt(formData.get('soundness_score')),
        feasibility_score: parseInt(formData.get('feasibility_score')),
        significance_score: parseInt(formData.get('significance_score')),
        overall_score: parseInt(formData.get('overall_score'))
    };
    
    // Validate all ratings are filled
    if (!validateRatingData(ratingData)) {
        showError('Please complete all rating dimensions before submitting.');
        isSubmitting = false;
        return;
    }
    
    // Show loading state
    const submitBtn = event.target.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    submitBtn.textContent = 'Submitting...';
    submitBtn.disabled = true;
    
    try {
        // Send rating data
        const response = await fetch('/api/submit-rating', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(ratingData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showSuccess('Rating submitted successfully!');
            
            // Check if all comparisons are completed
            if (ratingData.comparison_number >= 8) {
                // Redirect to thank you page
                setTimeout(() => {
                    window.location.href = '/thank-you';
                }, 1000);
            } else {
                // Refresh page to show next comparison
                setTimeout(() => {
                    // Store scroll position in sessionStorage before reload
                    sessionStorage.setItem('scrollToTop', 'true');
                    window.location.reload();
                }, 1000);
            }
        } else {
            showError('Failed to submit rating. Please try again.');
        }
    } catch (error) {
        console.error('Error:', error);
        showError('Network error. Please check your connection and try again.');
    } finally {
        // Restore button state
        submitBtn.textContent = originalText;
        submitBtn.disabled = false;
        isSubmitting = false;
    }
}

// Handle comment submission
async function handleCommentSubmission(event) {
    event.preventDefault();
    
    if (isSubmitting) {
        return;
    }
    
    isSubmitting = true;
    
    const formData = new FormData(event.target);
    const commentData = {
        comment: formData.get('comment')
    };
    
    // Show loading state
    const submitBtn = event.target.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    submitBtn.textContent = 'Submitting...';
    submitBtn.disabled = true;
    
    try {
        // Send comment data
        const response = await fetch('/api/submit-comment', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(commentData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showSuccess('Feedback submitted successfully! Thank you for your participation.');
            
            // Clear form
            event.target.reset();
            
            // Disable form
            submitBtn.textContent = 'Submitted';
            submitBtn.disabled = true;
            document.getElementById('comment-text').disabled = true;
        } else {
            showError('Failed to submit feedback. Please try again.');
        }
    } catch (error) {
        console.error('Error:', error);
        showError('Network error. Please check your connection and try again.');
    } finally {
        // Restore button state
        if (submitBtn.textContent !== 'Submitted') {
            submitBtn.textContent = originalText;
            submitBtn.disabled = false;
        }
        isSubmitting = false;
    }
}

// Validate rating data
function validateRatingData(data) {
    const requiredFields = ['novelty_score', 'soundness_score', 'feasibility_score', 'significance_score', 'overall_score'];
    
    for (const field of requiredFields) {
        if (!data[field] || data[field] < 1 || data[field] > 5) {
            return false;
        }
    }
    
    return true;
}

// Toggle hypothesis full content display
function toggleFullContent(hypothesisId) {
    const fullContent = document.getElementById(`${hypothesisId}-full`);
    const button = document.querySelector(`#${hypothesisId}-content button`);
    
    if (fullContent.style.display === 'none') {
        fullContent.style.display = 'block';
        button.textContent = 'Collapse Content';
    } else {
        fullContent.style.display = 'none';
        button.textContent = 'View Full Content';
    }
}

// Show success message
function showSuccess(message) {
    // Remove existing messages
    removeExistingMessages();
    
    const successDiv = document.createElement('div');
    successDiv.className = 'alert alert-success alert-dismissible fade show';
    successDiv.innerHTML = `
        <strong>Success!</strong> ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Insert at top of page
    const main = document.querySelector('main');
    main.insertBefore(successDiv, main.firstChild);
    
    // Auto hide
    setTimeout(() => {
        if (successDiv.parentNode) {
            successDiv.remove();
        }
    }, 5000);
}

// Show error message
function showError(message) {
    // Remove existing messages
    removeExistingMessages();
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'alert alert-danger alert-dismissible fade show';
    errorDiv.innerHTML = `
        <strong>Error!</strong> ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Insert at top of page
    const main = document.querySelector('main');
    main.insertBefore(errorDiv, main.firstChild);
    
    // Auto hide
    setTimeout(() => {
        if (errorDiv.parentNode) {
            errorDiv.remove();
        }
    }, 5000);
}

// Remove existing messages
function removeExistingMessages() {
    const existingAlerts = document.querySelectorAll('.alert');
    existingAlerts.forEach(alert => {
        if (alert.classList.contains('alert-success') || alert.classList.contains('alert-danger')) {
            alert.remove();
        }
    });
}

// Page leave confirmation
window.addEventListener('beforeunload', function(event) {
    const ratingForm = document.getElementById('rating-form');
    if (ratingForm && !isSubmitting) {
        // Check if there are incomplete ratings
        const inputs = ratingForm.querySelectorAll('input[type="radio"]:checked');
        if (inputs.length > 0 && inputs.length < 5) {
            event.preventDefault();
            event.returnValue = 'You have incomplete ratings. Are you sure you want to leave?';
            return event.returnValue;
        }
    }
});

// Prevent duplicate submissions
document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            if (isSubmitting) {
                event.preventDefault();
                return false;
            }
        });
    });
});

// Language switching functionality
function toggleLanguage() {
    // Get current URL and parameters
    const currentUrl = new URL(window.location);
    const currentLang = currentUrl.searchParams.get('lang') || 'english';
    
    // Toggle language
    const newLang = currentLang === 'english' ? 'chinese' : 'english';
    
    // Update URL parameter
    currentUrl.searchParams.set('lang', newLang);
    
    // Reload page with new language
    window.location.href = currentUrl.toString();
}