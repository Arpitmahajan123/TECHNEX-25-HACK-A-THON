document.addEventListener('DOMContentLoaded', function() {
    // Get location parameters from URL
    const urlParams = new URLSearchParams(window.location.search);
    const lat = urlParams.get('lat');
    const lng = urlParams.get('lng');

    // Sample emergency contact data (in a real app, this would come from an API)
    const emergencyContacts = {
        policeStations: [
            { name: "Central Police Station", phone: "100", distance: "1.2 km" },
            { name: "Women Police Station", phone: "1091", distance: "2.5 km" }
        ],
        hospitals: [
            { name: "City General Hospital", phone: "102", distance: "0.8 km" },
            { name: "Women's Health Center", phone: "1234567890", distance: "1.5 km" }
        ],
        organizations: [
            { name: "Women's Helpline", phone: "1091", distance: "N/A" },
            { name: "Women's Safety NGO", phone: "1098", distance: "3.0 km" }
        ]
    };

    // Function to create contact elements
    function displayContacts(contacts, containerId) {
        const container = document.getElementById(containerId);
        container.innerHTML = '';
        
        contacts.forEach(contact => {
            const contactElement = document.createElement('div');
            contactElement.className = 'contact-item';
            contactElement.innerHTML = `
                <div>
                    <strong>${contact.name}</strong><br>
                    Distance: ${contact.distance}<br>
                    <a href="tel:${contact.phone}">📞 ${contact.phone}</a>
                </div>
            `;
            container.appendChild(contactElement);
        });
    }

    // Display all contacts
    displayContacts(emergencyContacts.policeStations, 'policeStations');
    displayContacts(emergencyContacts.hospitals, 'hospitals');
    displayContacts(emergencyContacts.organizations, 'organizations');
});
