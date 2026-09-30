document.addEventListener('DOMContentLoaded', function() {
    const searchForm = document.getElementById('searchForm');
    if (!searchForm) return;

    // Date picker min date
    const dateInput = searchForm.querySelector('input[name="date"]');
    if (dateInput) {
        const today = new Date().toISOString().split('T')[0];
        dateInput.setAttribute('min', today);
    }

    // Swap source and destination
    const swapBtn = document.getElementById('swapBtn');
    if (swapBtn) {
        swapBtn.addEventListener('click', function() {
            const source = searchForm.querySelector('input[name="source"]');
            const dest = searchForm.querySelector('input[name="destination"]');
            const temp = source.value;
            source.value = dest.value;
            dest.value = temp;
        });
    }

    // Auto-suggest cities
    const cityInputs = searchForm.querySelectorAll('input[name="source"], input[name="destination"]');
    const cities = ['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Kolkata', 'Hyderabad', 'Pune', 'Ahmedabad', 'Jaipur', 'Lucknow'];

    cityInputs.forEach(input => {
        input.addEventListener('input', function() {
            const value = this.value.toLowerCase();
            const suggestions = cities.filter(city => city.toLowerCase().includes(value));
            // Can implement dropdown suggestions here
        });
    });
});
