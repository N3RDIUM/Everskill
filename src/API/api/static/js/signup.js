// SHA256 hashing algo
var sha256 =  new Hashes.SHA256;

function submit() {
    let username = document.getElementById('username').value;
    let password = sha256.hex(document.getElementById('username').value);

    fetch('/new-user', {
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
        } else {
            console.log(response)
            alert(response.response);
        }
    })
}
