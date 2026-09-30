let map;
let marker;
let trackingSocket;

function initMap(latitude, longitude) {
    // Initialize map (using a placeholder - replace with actual map library)
    const mapDiv = document.getElementById('map');
    if (mapDiv) {
        mapDiv.innerHTML = `
            <div class="d-flex align-items-center justify-content-center h-100">
                <div class="text-center">
                    <i class="fas fa-map-marker-alt fa-3x text-danger mb-3"></i>
                    <p>Lat: ${latitude}, Lng: ${longitude}</p>
                    <p class="text-muted">Map integration pending</p>
                </div>
            </div>
        `;
    }
}

function connectTrackingSocket(busId) {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/tracking/${busId}/`;

    trackingSocket = new WebSocket(wsUrl);

    trackingSocket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        updateTrackingInfo(data);
    };

    trackingSocket.onclose = function(e) {
        console.log('Tracking socket closed. Reconnecting...');
        setTimeout(() => connectTrackingSocket(busId), 5000);
    };
}

function updateTrackingInfo(data) {
    const elements = {
        currentStop: document.getElementById('currentStop'),
        nextStop: document.getElementById('nextStop'),
        eta: document.getElementById('eta'),
        speed: document.getElementById('speed'),
        status: document.getElementById('trackingStatus')
    };

    if (elements.currentStop) elements.currentStop.textContent = data.current_stop || 'N/A';
    if (elements.nextStop) elements.nextStop.textContent = data.next_stop || 'N/A';
    if (elements.eta) elements.eta.textContent = data.estimated_arrival || 'N/A';
    if (elements.speed) elements.speed.textContent = (data.speed || 0) + ' km/h';
    if (elements.status) {
        elements.status.textContent = data.is_on_time ? 'On Time' : 'Delayed';
        elements.status.className = data.is_on_time ? 'badge bg-success' : 'badge bg-warning';
    }

    if (data.latitude && data.longitude) {
        initMap(data.latitude, data.longitude);
    }
}

document.addEventListener('DOMContentLoaded', function() {
    const busId = document.getElementById('trackingData')?.dataset.busId;
    if (busId) {
        connectTrackingSocket(busId);
    }
});
