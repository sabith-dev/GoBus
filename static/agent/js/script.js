// BusGo Agent Portal - Frontend Interactions

document.addEventListener('DOMContentLoaded', function() {
    // 1. Dynamic List Editor (for Boarding Points, Dropping Points, and Stops)
    setupDynamicLists();

    // 2. Interactive Seat Selection
    setupSeatSelection();
});

// Dynamic List Builder
function setupDynamicLists() {
    const listContainers = document.querySelectorAll('[data-dynamic-list]');
    
    listContainers.forEach(container => {
        const listId = container.dataset.dynamicList;
        const addBtn = document.getElementById(`add-${listId}-btn`);
        const itemsWrapper = container.querySelector('.dynamic-items');
        const inputName = container.dataset.inputName;
        
        if (!addBtn || !itemsWrapper) return;
        
        addBtn.addEventListener('click', function(e) {
            e.preventDefault();
            const index = itemsWrapper.children.length + 1;
            
            const itemRow = document.createElement('div');
            itemRow.className = 'd-flex align-items-center gap-2 mb-2 dynamic-item';
            itemRow.innerHTML = `
                <span class="text-muted fs-7">${index}.</span>
                <input type="text" name="${inputName}" class="form-control" placeholder="Enter point name" required>
                <button type="button" class="btn btn-outline-danger btn-sm remove-item-btn">
                    <i class="bi bi-trash"></i>
                </button>
            `;
            
            itemsWrapper.appendChild(itemRow);
            updateIndices(itemsWrapper);
        });
        
        itemsWrapper.addEventListener('click', function(e) {
            const removeBtn = e.target.closest('.remove-item-btn');
            if (removeBtn) {
                e.preventDefault();
                removeBtn.closest('.dynamic-item').remove();
                updateIndices(itemsWrapper);
            }
        });
    });
}

function updateIndices(wrapper) {
    const items = wrapper.querySelectorAll('.dynamic-item');
    items.forEach((item, idx) => {
        const span = item.querySelector('span');
        if (span) span.textContent = `${idx + 1}.`;
    });
}

// Seat Selection logic
function setupSeatSelection() {
    const seatGrid = document.getElementById('interactive-seat-grid');
    if (!seatGrid) return;

    const totalSeatsVal = document.getElementById('total-seats-count');
    const bookedSeatsVal = document.getElementById('booked-seats-count');
    const availSeatsVal = document.getElementById('available-seats-count');
    const selectedSeatsInput = document.getElementById('selected-seats-input');

    if (!seatGrid) return;

    let selectedSeats = [];

    seatGrid.addEventListener('click', function(e) {
        const seat = e.target.closest('.seat');
        if (!seat) return;

        // Skip booked or driver seat
        if (seat.classList.contains('booked') || seat.classList.contains('driver')) {
            return;
        }

        const seatId = seat.dataset.seatId;

        if (seat.classList.contains('selected')) {
            seat.classList.remove('selected');
            selectedSeats = selectedSeats.filter(id => id !== seatId);
        } else {
            seat.classList.add('selected');
            selectedSeats.push(seatId);
        }

        // Update hidden input
        if (selectedSeatsInput) {
            selectedSeatsInput.value = JSON.stringify(selectedSeats);
        }

        // Optional UI counter updates
        const activeCountElement = document.getElementById('active-selected-count');
        if (activeCountElement) {
            activeCountElement.textContent = selectedSeats.length;
        }
    });
}

// Chart Initializer helpers (called directly from dashboard template)
function initDashboardCharts(earningsData, bookingsData) {
    // Earnings Chart (Line Chart)
    const earningsCtx = document.getElementById('earningsChart');
    if (earningsCtx) {
        new Chart(earningsCtx, {
            type: 'line',
            data: {
                labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                datasets: [{
                    label: 'Earnings (₹)',
                    data: earningsData,
                    borderColor: '#E11D48',
                    backgroundColor: 'rgba(225, 29, 72, 0.05)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: {
                        grid: { color: '#f1f5f9' },
                        ticks: {
                            callback: function(value) { return '₹' + value.toLocaleString(); }
                        }
                    },
                    x: { grid: { display: false } }
                }
            }
        });
    }

    // Bookings Chart (Doughnut Chart)
    const bookingsCtx = document.getElementById('bookingsChart');
    if (bookingsCtx) {
        new Chart(bookingsCtx, {
            type: 'doughnut',
            data: {
                labels: ['Confirmed', 'Cancelled', 'Completed'],
                datasets: [{
                    data: bookingsData, // e.g. [55, 20, 15]
                    backgroundColor: ['#10b981', '#ef4444', '#E11D48'],
                    borderWidth: 2,
                    hoverOffset: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                cutout: '70%'
            }
        });
    }
}