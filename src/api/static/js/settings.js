// If there is not everskill-token and everskill-username in the local storage
if (!localStorage.getItem("everskill-token") && !localStorage.getItem("everskill-username")) {
    window.location.href = '/signin';
}

// Get username and token from local storage
let username = localStorage.getItem('everskill-username');
let token = localStorage.getItem('everskill-token');

let bio, interests, profilepic;
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
            
            bio          = data.bio;
            interests    = data.interests;
            profilepic   = data.profilepic;
            
            document.getElementById('settings-form').innerHTML = `Username: Username switcher coming soon!<br>
Password: Password switcher coming soon!<br>
Bio: <input type=text id=bio value=${bio}><br>
Interests: <div id=interests></div>
Add interests: <input type=text id=add-interest>
<button onclick="addInterest()">Add interest</button><br>
Profile picture: <img src="${profilepic}" alt="Profile picture" width=100 height=100><br>
Change pfp URL: <input type=text id=pfp value=${profilepic}><br> (Upload to imgur and add the link here)`;
            addInitialInterests(interests);
        }
    })
}

function addInitialInterests(interests) {
    for (let i = 0; i < interests.length; i++) {
        document.getElementById('interests').innerHTML += `<span class='interest'>${interests[i]}</span>`;
        // TODO! Add some way to remove interests
    }
}
function addInterest() {
    let interest = document.getElementById('add-interest').value;
    document.getElementById('add-interest').value = '';
    document.getElementById('interests').innerHTML += `<span class='interest'>${interest}</span>`;
}

function update() {
    fetch('/api/update-profile/', {
        method: 'POST',
        body: JSON.stringify({
            username: username,
            token: token,
            updates: {
                bio: document.getElementById('bio').value,
                interests: Array.from(document.getElementsByClassName('interest')).map(e => e.innerText),
                profilepic: document.getElementById('pfp').value
            }
        }),
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(async res => {
        const data = await res.json();
        if(data.success) {
            let ret = confirm('Update successful! Return to homepage?')
            if(ret) {
                window.location.href = '/app/';
            }
        }
    })
}
