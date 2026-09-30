document.addEventListener('DOMContentLoaded', function() {
    // Booking confirmation dialog
    const confirmBtn = document.getElementById('confirmBooking');
    if (confirmBtn) {
        confirmBtn.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to confirm this booking?')) {
                e.preventDefault();
            }
        });
    }

    // Auto-fill passenger details
    const useProfileBtn = document.getElementById('useProfile');
    if (useProfileBtn) {
        useProfileBtn.addEventListener('click', function() {
            // Fetch user profile data via AJAX
            fetch('/api/profile/')
                .then(response => response.json())
                .then(data => {
                    document.querySelector('input[name="name"]').value = data.name || '';
                    document.querySelector('input[name="email"]').value = data.email || '';
                    document.querySelector('input[name="phone"]').value = data.phone || '';
                });
        });
    }
});
