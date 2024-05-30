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

function search() {
    document.getElementById('results').innerHTML = '<div class="load-container"><img class="spinner" src="/static/assets/loading.gif"></div>';
    let input = document.getElementById('query').value;
    fetch('/api/course-search/', {
        method: 'POST',
        body: JSON.stringify({
            query: input
        }),
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(async res => {
        let response = await res.json();
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
            document.getElementById('results').innerHTML = html;
        })
    })
}