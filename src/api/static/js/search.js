function search() {
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
        let data = await res.json();
        data = data.results
        let html = `<tr>
    <th>id</th>
    <th>url</th>
</tr>`;
        for (let i of data) {
            html += `<tr>
    <td>${i.id}</td>
    <td><a href="${i.url}" target="_blank">${i.url}</a></td>
</tr>`;
        }
        document.getElementById('results').innerHTML = html;
    })
}