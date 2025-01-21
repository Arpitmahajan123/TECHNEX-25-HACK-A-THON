document.addEventListener('DOMContentLoaded', function() {
    const shareButton = document.getElementById('shareButton');
    
    shareButton.addEventListener('click', function() {
        // Check if geolocation is supported
        if ("geolocation" in navigator) {
            navigator.geolocation.getCurrentPosition(function(position) {
                // Redirect to emergency page with location parameters
                window.location.href = `/emergency?lat=${position.coords.latitude}&lng=${position.coords.longitude}`;
            }, function(error) {
                console.error("Error getting location:", error);
                alert("Unable to get your location. Please enable location services and try again.");
            });
        } else {
            alert("Geolocation is not supported by your browser");
        }
    });
});
