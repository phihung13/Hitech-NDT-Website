// Simple notifications handler
$(document).ready(function() {
    // Check for notifications every 30 seconds
    setInterval(function() {
        $.ajax({
            url: '/api/notifications/',
            method: 'GET',
            success: function(data) {
                if (data.success && data.notifications.length > 0) {
                    // Update notification badge
                    $('.notification-badge').text(data.count);
                    $('.notification-badge').show();
                }
            },
            error: function(xhr, status, error) {
                console.log('Notifications API error:', error);
            }
        });
    }, 30000);
}); 