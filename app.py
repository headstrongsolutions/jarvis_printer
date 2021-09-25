"""jarvis_printer"""
import glob
import re
from os import stat_result
import urllib.parse
from dataclasses import dataclass, asdict
from typing import List
from flask import Flask, render_template, jsonify
#from catprinter.catprinter import CatPrinter

app = Flask(__name__)
MARKDOWN_DIR="markdown"

class MarkdownFile:
    def __init__(self, path:str) -> None:
        """Using the path to a markdown file, creates a MarkdownFile
        Args:
            path (str),
        Returns:
            None,
        """
        name_search = re.search("[\s\-\_a-z|A-Z|0-9]+[^I]\.md$", path)
        self.path = path
        self.name = name_search.group(0).replace(".md", "")
        self.urlencoded_path = urllib.parse.quote(self.path)
        self.markdown = ""

@dataclass
class PageValues:
    name: str
    markdown_dir: str
    markdown_files: List[MarkdownFile]


def get_markdown_file(urlencoded_path:str) -> str:
    """Returns text within a text file
    Args:
        urlencoded_path (str),
    Returns:
        markdown (str),
    """
    markdown = ""
    unencoded_path = urllib.parse.unquote(urlencoded_path)
    with open(unencoded_path) as file:
        raw_content = file.readlines()
        if len(raw_content) > 0:
            markdown = raw_content
    return markdown

def get_markdown_files(page_values: PageValues):
    # All files ending with .txt
    markdown_file_paths = (glob.glob(("%s/*.md" % (MARKDOWN_DIR))))
    page_values.markdown_files = None
    for path in markdown_file_paths:
        page_values.markdown_files.append(MarkdownFile(path=path))
    return page_values
    
@app.route('/api/v1/resources/get_markdowns', methods=['GET'])
def api_get_markdowns():
    books = [
        {'id': 0,
        'title': 'A Fire Upon the Deep',
        'author': 'Vernor Vinge',
        'first_sentence': 'The coldsleep itself was dreamless.',
        'year_published': '1992'},
        {'id': 1,
        'title': 'The Ones Who Walk Away From Omelas',
        'author': 'Ursula K. Le Guin',
        'first_sentence': 'With a clamor of bells that set the swallows soaring, the Festival of Summer came to the city Omelas, bright-towered by the sea.',
        'published': '1973'},
        {'id': 2,
        'title': 'Dhalgren',
        'author': 'Samuel R. Delany',
        'first_sentence': 'to wound the autumnal city.',
        'published': '1975'}
    ]
    page_values = PageValues
    page_values.name = "home"
    page_values.markdown_dir = MARKDOWN_DIR
    page_values.markdown_files = get_markdown_files()
    return jsonify(page_values)
@app.route('/api/v1/resources/get_markdown/{id}', methods=['GET'])
def api_get_markdown():
    

@app.route('/', methods=['GET', 'POST'])
def index():
    page_values = PageValues
    page_values.name = "home"
    page_values.markdown_dir = MARKDOWN_DIR
    page_values.markdown_files = get_markdown_files()
    return render_template('index.html', page_values=page_values)


if __name__ == '__main__':
    app.run()

