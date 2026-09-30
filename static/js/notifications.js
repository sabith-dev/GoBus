function checkUnreadNotifications() {
    fetch('/notifications/api/unread-count/')
        .then(response => response.json())
        .then(data => {
            const badge = document.getElementById('notificationBadge');
            if (badge) {
                if (data.count > 0) {
                    badge.textContent = data.count;
                    badge.style.display = 'inline-block';
                } else {
                    badge.style.display = 'none';
                }
            }
        });
}

function markAsRead(notificationId) {
    fetch(`/notifications/${notificationId}/read/`, {
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
    }).then(() => {
        checkUnreadNotifications();
    });
}

function markAllAsRead() {
    fetch('/notifications/read-all/', {
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
    }).then(() => {
        checkUnreadNotifications();
        location.reload();
    });
}

document.addEventListener('DOMContentLoaded', function() {
    checkUnreadNotifications();
    setInterval(checkUnreadNotifications, 60000);
});
