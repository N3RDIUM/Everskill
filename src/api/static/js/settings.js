// If there is not everskill-token and everskill-username in the local storage
if (!localStorage.getItem("everskill-token") && !localStorage.getItem("everskill-username")) {
    window.location.href = '/signin';
}

// Get username and token from local storage
let username = localStorage.getItem('everskill-username');
let token = localStorage.getItem('everskill-token');

window.onload = () => {
    fetch('/api/user-profile/', {
        method: 'POST',
        body: JSON.stringify({
            username: username
        }),
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(async res => {
        let data = await res.json();

        if(data.success) {
            data = data.profile;
            
            let bio          = data.bio;
            let interests    = data.interests;
            let profilepic   = data.profilepic;
            
            document.getElementById('settings-form').innerHTML = `Username: <input type=text id=username value=${username} disabled><br>
Password: <a href="/change-password/">Click here to change password!</a><br>
Bio: <input type=text id=bio value=${bio}><br>
Interests: <div id=interests></div>
Add interests: <input type=text id=add-interest>
<button onclick="addInterest()">Add interest</button><br>
Profile picture: <img src="${profilepic}" alt="Profile picture" width=100 height=100><br>
Change pfp: Coming soon!`;
        }
    })
}