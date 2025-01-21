document.addEventListener('DOMContentLoaded', function() {
    const sosButton = document.getElementById('sosButton');
    const locationStatus = document.getElementById('locationStatus');
    const messageStatus = document.getElementById('messageStatus');
    const errorStatus = document.getElementById('errorStatus');

    if (sosButton) {
        sosButton.addEventListener('click', handleSOS);
    }

    function handleSOS() {
        // Reset status messages
        hideAllStatus();
        showLocationStatus('Getting your location...');

        // Get user's location
        if (navigator.geolocation) {
            const options = {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 0
            };

            navigator.geolocation.getCurrentPosition(
                position => sendSOSAlert(position),
                error => handleLocationError(error),
                options
            );
        } else {
            showError("Geolocation is not supported by your browser.");
        }
    }

    function sendSOSAlert(position) {
        showLocationStatus('Sending SOS alert...');
        
        const location = {
            lat: position.coords.latitude,
            lng: position.coords.longitude
        };

        fetch('/send_sos', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify(location)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showSuccess('Emergency alert sent successfully! Help is on the way.');
                // Vibrate the device if supported
                if (navigator.vibrate) {
                    navigator.vibrate([200, 100, 200]);
                }
            } else {
                showError(data.error || "Failed to send SOS alert");
            }
        })
        .catch(error => {
            showError("Network error: " + error.message);
        });
    }

    function handleLocationError(error) {
        let errorMessage;
        switch(error.code) {
            case error.PERMISSION_DENIED:
                errorMessage = "Location access denied. Please enable location services in your browser settings.";
                break;
            case error.POSITION_UNAVAILABLE:
                errorMessage = "Location information unavailable. Please try again.";
                break;
            case error.TIMEOUT:
                errorMessage = "Location request timed out. Please try again.";
                break;
            default:
                errorMessage = "An unknown error occurred while getting location.";
        }
        showError(errorMessage);
    }

    function hideAllStatus() {
        locationStatus.classList.add('d-none');
        messageStatus.classList.add('d-none');
        errorStatus.classList.add('d-none');
    }

    function showLocationStatus(message) {
        hideAllStatus();
        locationStatus.textContent = message;
        locationStatus.classList.remove('d-none');
    }

    function showSuccess(message) {
        hideAllStatus();
        messageStatus.textContent = message;
        messageStatus.classList.remove('d-none');
        // Hide success message after 10 seconds
        setTimeout(() => {
            messageStatus.classList.add('d-none');
        }, 10000);
    }

    function showError(message) {
        hideAllStatus();
        errorStatus.textContent = message;
        errorStatus.classList.remove('d-none');
        // Hide error message after 10 seconds
        setTimeout(() => {
            errorStatus.classList.add('d-none');
        }, 10000);
    }
});
