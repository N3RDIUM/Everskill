// If there is not everskill-token and everskill-username in the local storage
if (!localStorage.getItem("everskill-token") && !localStorage.getItem("everskill-username")) {
    window.location.href = '/signin';
}

// Get username and token from local storage
let username = localStorage.getItem('everskill-username');
let token = localStorage.getItem('everskill-token');

// Add the username to #username-thing
window.onload = () => {
    document.getElementById('username-thing').innerHTML = `Welcome ${username}`;
}
