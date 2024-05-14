# Imports
import re
import json
import bleach
import requests
from html_sanitizer import Sanitizer
sanitizer = Sanitizer({
    "tags": {
        "a", "h1", "h2", "h3", "strong", "em", "p", "ul", "ol",
        "li", "br", "sub", "sup", "hr", "div", "pre"
    },
    "attributes": {"a": ("href", "name", "target", "title", "id", "rel"), "div": ("class", "data-quizid")},
    "empty": {"hr", "a", "br"},
    "separate": {"a", "p", "li"},
    "whitespace": {"br"},
    "is_mergeable": lambda e1, e2: True,
})

# Course class
class Course:
    def __init__(self, url: str) -> None:
        self.url = url
        self.details = json.loads(requests.get(self.url).text)

    def render_html(self, page: str = 'home') -> list:
        page = self.details['pages'][page]
        source = requests.get(page['html']).text
        ret = sanitizer.sanitize(source.strip()).strip()
        ret = bleach.linkify(ret)
        
        # Get all instances of comments in this html
        comments = re.findall('<!--.*?-->', ret)
        for comment in comments:
            c = comment.replace('<!--', '').replace('-->', '').strip()
            if c.startswith('QUIZ_EMBED'):
                quizid = c.split(':')[1].strip()
                ret = ret.replace(comment, f'<div id="quiz-embed" data-quizid="{quizid}"></div>')
        
        return page, ret