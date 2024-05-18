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
            
            // TODO! This part of the code deserves attention from a frontend person
            let achievements = data.achievements;
            let bio          = data.bio;
            let coins        = data.coins;
            let courses      = data.courses;
            let gems         = data.gems;
            let interests    = data.interests;
            let lastActive   = data.lastActive;
            let level        = data.level;
            let patches      = data.patches;
            let profilepic   = data.profilepic;
            let streak       = data.streak;
            
            document.getElementById('data').innerHTML = JSON.stringify(data, null, 4)
        }
    })
}