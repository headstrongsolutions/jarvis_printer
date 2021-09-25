"""jarvis_printer"""
import glob
import re
from os import read, stat_result
import urllib.parse
from dataclasses import dataclass, asdict
from typing import List
from flask import Flask, json, render_template, jsonify, request
#from catprinter.catprinter import CatPrinter

app = Flask(__name__)
MARKDOWN_DIR="catprinter/markdown"

@dataclass
class todo_item:
    text: str
    checked: bool

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
        self.name = ""
        self.urlencoded_path = ""
        self.markdown = ""
        if len(self.path) > 0:
            self.name = name_search.group(0).replace(".md", "")
            self.urlencoded_path = urllib.parse.quote(self.path)

    def from_friendly_name(self, friendly_name) -> None:
        """Rebuilds an instance when only the friendly name is known"""
        full_path = ("%s/%s.md" %(MARKDOWN_DIR, friendly_name))
        temp_markdown_file = MarkdownFile(path=full_path)
        self.name = temp_markdown_file.name
        self.path = temp_markdown_file.path
        self.urlencoded_path = temp_markdown_file.urlencoded_path
        self.markdown = temp_markdown_file.markdown

@dataclass
class PageValues:
    name: str
    markdown_dir: str
    markdown_files: List[MarkdownFile]

def get_project_readme_todos() -> List[todo_item]:
    """Reads the projects README.md file, extracts the todo list and
        returns it as a list of todo_item's
    Args:
        None,
    Returns:
        List[todo_item],
    """
    todo_items = []
    with open('README.md') as readme_file:
        readme_raw = readme_file.read()
        todo_raw = readme_raw.split("### To Do\n")
        todos = todo_raw[1].splitlines()
        for todo in todos:
            todo_item_new = todo_item("", False)
            if ' - [X] ' in todo or ' - [x] ' in todo:
                todo_item_new.checked = True
                todo_item_new.text = todo.replace(' - [x] ', "")
                todo_item_new.text = todo.replace(' - [X] ', "")
            else:
                todo_item_new.text = todo.replace(' - [ ] ', "")
            todo_items.append(todo_item_new)
    return todo_items

def get_markdown_file(urlencoded_path:str) -> str:
    """Returns text within a text file
    Args:
        urlencoded_path (str),
    Returns:
        markdown (str),
    """
    markdown = ""
    unencoded_path = urllib.parse.unquote(urlencoded_path)
    print(unencoded_path)
    with open(unencoded_path) as file:
        raw_content = file.readlines()
        if len(raw_content) > 0:
            markdown = raw_content
    return markdown

def get_markdown_files():
    """Returns all markdown files in a specified directory
    Args:
        None,
    Returns:
        markdown_files (List[str]),
    """
    markdown_file_paths = (glob.glob(("%s/*.md" % (MARKDOWN_DIR))))
    print("raw_paths: %s" % markdown_file_paths)
    markdown_files = []
    for path in markdown_file_paths:
        print("path: %s" %path)
        markdown_files.append(path)
    return markdown_files

def get_friendly_markdown_name(markdown_file_path: str) -> List[str]:
    markdown_file = MarkdownFile(markdown_file_path)
    return markdown_file.name
    
@app.route('/api/v1/resources/get_markdown_names', methods=['GET'])
def get_markdown_names():
    markdown_names = []
    markdown_files = get_markdown_files()
    for path in markdown_files:
        markdown_names.append(get_friendly_markdown_name(path))
    return jsonify(markdown_names=markdown_names)

@app.route('/api/v1/resources/get_markdown', methods=['GET'])
def api_get_markdown():
    print('so far..')
    markdown_name = request.args.get('markdown_name', default=1, type=str)
    print(markdown_name)
    markdown = MarkdownFile("")
    markdown.from_friendly_name(markdown_name)
    return jsonify(name=markdown.name, 
                   path=markdown.path, 
                   urlencoded_path=markdown.urlencoded_path, 
                   markdown=markdown.markdown)

@app.route('/', methods=['GET', 'POST'])
def index():
    markdown_files = get_markdown_files()
    todo_items = get_project_readme_todos()
    return render_template('index.html', todo_items=todo_items)

if __name__ == '__main__':
    app.run()

