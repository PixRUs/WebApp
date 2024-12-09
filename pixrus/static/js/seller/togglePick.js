function getCSRFToken() {
    const cookies = document.cookie.split(';');
    for (const cookie of cookies) {
        const [key, value] = cookie.trim().split('=');
        if (key === 'csrftoken') {
            return value;
        }
    }
    return null;
}

const csrfToken = getCSRFToken();

function togglePick(checkbox) {
    const pickId = checkbox.getAttribute('data-pick-id');
    const newState = checkbox.checked;

    fetch(`/seller/update-pick/${pickId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken, // Ensure this token is rendered in the template
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ new_state: newState }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log('Pick updated successfully.');
        } else {
            console.error('Failed to update pick.');
            checkbox.checked = !newState; // Revert the checkbox if the update failed
        }
    })
}
