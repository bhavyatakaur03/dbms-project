document.getElementById('loginForm').addEventListener('submit', function(event) {
    event.preventDefault();  // Prevent default form submission
    sendLoginData();         // Send data using AJAX (fetch)
});

function sendLoginData() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const role = document.getElementById('role').value;  // Correct role value capture

    const loginData = {
        username: username,
        password: password,
        role: role
    };

    // Send login data to the Flask server (via AJAX)
    fetch('/process_login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(loginData)  // Send data as JSON
    })
    .then(response => response.json())
    .then(data => {
        handleLoginResponse(data); // Handle the server's response
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function handleLoginResponse(data) {
    if (data.success) {
        if (data.role === 'government') {
            window.location.href = '/government_dashboard';  // Redirect to company dashboard
        } else if (data.role === 'individual') {
            window.location.href = '/individual_dashboard';    // Redirect to user dashboard
        }
    } else {
        alert('Invalid username or password');
    }
}
