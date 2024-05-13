// SHA256 hashing algo
var sha256 =  new Hashes.SHA256;

// If there is already everskill-token and everskill-username in the local storage
if (localStorage.getItem("everskill-token") && localStorage.getItem("everskill-username")) {
    alert("You're already signed in!");
    window.location.href = '/';
}

// Submit button clicked.
function submit() {
    let username = document.getElementById('username').value;
    let password = sha256.hex(document.getElementById('username').value);

    fetch('/signin-upass', {
        method: 'POST',
        body: JSON.stringify({
            username: username,
            password: password
        }),
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(async res => {
        let response = await res.json();
        if(response.success) {
            window.localStorage.setItem('everskill-token', response.token);
            window.localStorage.setItem('everskill-username', username);
            window.location.href = '/';
        } else {
            console.log(response)
            alert(response.response);
        }
    })
}
