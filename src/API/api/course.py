# Imports
import json
import bleach
import requests

# Course class
# TODO! Use the html sanitizer!
class Course:
    def __init__(self, url: str) -> None:
        self.url = url
        self.details = json.loads(requests.get(self.url).text)

    def render_html(self, page: str = 'home') -> list:
        page = self.details['pages'][page]
        source = requests.get(page['html']).text
        ret = bleach.linkify(source)
        
        return page, ret
    
c = Course("https://raw.githubusercontent.com/N3RDIUM/everskill-course-template/main/course.json")
r = c.render_html()
print(r)
