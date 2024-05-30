// If there is not everskill-token and everskill-username in the local storage
if (!localStorage.getItem("everskill-token") && !localStorage.getItem("everskill-username")) {
    window.location.href = '/signin/';
}

// Get username and token from local storage
let username = localStorage.getItem('everskill-username');
let token = localStorage.getItem('everskill-token');

function buildCourseHTML(image, title, description, id) {
    return `<div class="course-card" onclick='window.location.href="/course/${id}/home/"'>
    <img class="cover-img" src=${image}></img>
    <div class="coursetxt">
      <span class="course-title">${title}</span
      ><br><span class="course-desc"
        >${description}</span
      ></div>
    </div>`
}

// Get course recommendations
window.onload = () => {
    document.getElementById('username').innerHTML = `${username}`;
    fetch('/api/course-recommend/', {
        method: 'POST',
        body: JSON.stringify({
            username: username
        }),
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(async res => {
        const response = await res.json();
        let ids = [];
        for(let item of response.results) {
            ids.push(item.id);
        }
        fetch('/api/course-details-batch/', {
            method: 'POST',
            body: JSON.stringify(ids),
            headers: {
                'Content-Type': 'application/json'
            }
        }).then(async res => {
            const response = await res.json();
            let html = '';
            for(let item of response.courses) {
                html += buildCourseHTML(item.coverart, item.title, item.description, item.id);
            }
            document.getElementById('recommended').innerHTML = html;
        })
    })
    fetch('/api/my-courses/', {
        method: 'POST',
        body: JSON.stringify({
            username: username
        }),
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(async res => {
        const results = await res.json();
        fetch('/api/course-details-batch/', {
            method: 'POST',
            body: JSON.stringify(results.results),
            headers: {
                'Content-Type': 'application/json'
            }
        }).then(async res => {
            const response = await res.json();
            let html = '';
            for(let item of response.courses) {
                html += buildCourseHTML(item.coverart, item.title, item.description, item.id);
            }
            document.getElementById('mine').innerHTML = html;
        })
    })
}
