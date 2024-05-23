// If there is not everskill-token and everskill-username in the local storage
if (!localStorage.getItem("everskill-token") && !localStorage.getItem("everskill-username")) {
    window.location.href = '/signin';
}

// Get username and token from local storage
let username = localStorage.getItem('everskill-username');
let token = localStorage.getItem('everskill-token');

// Other stuff
var interestInput, interestTags, addInterestButton

function handleAddInterest() {
    const enteredInterest = interestInput.value.trim();

    const newTag = document.createElement('div');
    newTag.classList.add('tag');
    newTag.innerText = enteredInterest;

    const closeButton = document.createElement('span');
    closeButton.classList.add('close');
    closeButton.innerText = 'x';
    closeButton.addEventListener('click', () => {
        interestTags.removeChild(newTag);
    });
    newTag.appendChild(closeButton);

    interestTags.appendChild(newTag);

    interestInput.value = '';
}
function addInterest(enteredInterest) {
    const newTag = document.createElement('div');
    newTag.classList.add('tag');
    newTag.innerText = enteredInterest;

    const closeButton = document.createElement('span');
    closeButton.classList.add('close');
    closeButton.innerText = 'x';
    closeButton.addEventListener('click', () => {
        interestTags.removeChild(newTag);
    });
    newTag.appendChild(closeButton);

    interestTags.appendChild(newTag);

    interestInput.value = '';
}

let bio, interests, profilepic;
window.onload = () => {
    interestInput = document.getElementById('interests');
    interestTags = document.getElementById('interest-tags');
    addInterestButton = document.getElementById('add-interests');

    addInterestButton.addEventListener('click', handleAddInterest);
    interestInput.addEventListener('keyup', (event) => {
        if (event.keyCode === 13) {
            handleAddInterest();
        }
    });
    
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
            
            document.getElementById('bio').value           = bio;
            document.getElementById('url-enter-img').value = profilepic;
            document.getElementById('pfp-disp').src        = profilepic;

            for(let interest of interests) {
                addInterest(interest)
            }
        }
    })
}

function update() {
    fetch('/api/update-profile/', {
        method: 'POST',
        body: JSON.stringify({
            username: username,
            token: token,
            updates: {
                bio: document.getElementById('bio').value,
                interests: Array.from(document.getElementsByClassName('tag')).map(e => e.innerHTML.split('<span')[0]),
                profilepic: document.getElementById('url-enter-img').value
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
