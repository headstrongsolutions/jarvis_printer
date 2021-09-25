"""jarvis_printer"""
import glob
import re
from os import read, spawnve, stat_result, path, remove
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
    def __init__(self) -> None:
        """Using the file_path to a markdown file, creates a MarkdownFile
        Args:
            path (str),
        Returns:
            None,
        """
        self.file_path = ""
        self.name = ""
        self.urlencoded_path = ""
        self.markdown = ""
        self.set_defaults()
        

    def from_friendly_name(self, friendly_name) -> None:
        """Rebuilds an instance when only the friendly name is known"""
        full_path = ("%s/%s.md" %(MARKDOWN_DIR, friendly_name))
        temp_markdown_file = MarkdownFile()
        temp_markdown_file.file_path=full_path
        temp_markdown_file.set_defaults()
        self.name = temp_markdown_file.name
        self.file_path = temp_markdown_file.file_path
        self.urlencoded_path = temp_markdown_file.urlencoded_path
        self.markdown = temp_markdown_file.markdown

    def convert_urlencoded_path(self, urlencoded_path: str) -> None:
        """Converts a urlencoded path to unencoded"""
        self.file_path = urllib.parse.unquote(urlencoded_path)
        self.set_defaults()
    
    def set_defaults(self) -> None:
        """Sets default values"""
        if self.file_path and self.file_path > "":
            self.urlencoded_path = urllib.parse.quote(self.file_path)
            self.name = self.urlencoded_path.replace((MARKDOWN_DIR + "/"), "")
            self.name = self.name.replace(".md", "")

    
    def get_markdown_file_contents(self) -> None:
        """Gets markdown file contents"""
        file_path = ""
        if self.file_path > "":
            file_path = self.file_path
        elif self.urlencoded_path > "":
            file_path = self.convert_urlencoded_path(self.urlencoded_path)
        if file_path > "":
            with open(self.file_path) as file:
                raw_content = file.read()
                if raw_content > "":
                    self.markdown = raw_content

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
    with open(unencoded_path) as file:
        raw_content = file.readlines()
        if len(raw_content) > 0:
            markdown = raw_content
    return markdown

def get_markdown_file_paths():
    """Returns all markdown file paths in a specified directory
    Args:
        None,
    Returns:
        markdown_files (List[str]),
    """
    markdown_file_paths = (glob.glob(("%s/*.md" % (MARKDOWN_DIR))))
    markdown_files = []
    for file_path in markdown_file_paths:
        markdown_files.append(file_path)
    return markdown_files

def save_markdown_file(markdown:MarkdownFile) -> bool:
    """Saves a markdown file to location, creates a new file
        if one doesnt already exist
    Args:
        markdown (MarkdownFile),
    Returns:
        save_result (bool),
    """
    save_result = False
    result_count = 0
    if len(markdown.file_path) == 0  and len(markdown.urlencoded_path) > 0:
        markdown.convert_urlencoded_path()

    if len(markdown.file_path) > 0:
        with open(markdown.file_path, "w") as markdown_file:
            result_count = markdown_file.write(markdown.markdown)
    if result_count > 0:
        save_result = False
    return save_result

def delete_markdown_file(markdown_file:MarkdownFile) -> None:
    """Deletes a markdown file
    Args:
        markdown_file (MarkdownFile),
    Returns:
        None,
    """
    remove(markdown_file.file_path)

def delete_image_file(image_file_path:str) -> None:
    """Deletes a image file
    Args:
        image_file_path (str),
    Returns:
        None,
    """
    remove(image_file_path)

def upload_image(image) -> None:
    """Uploads a image file
    Args:
        image_file (),
    Returns:\
        None,
    """
    if hasattr(image, 'filename') and len(image.filename) > 0:
        image.save(path.join(MARKDOWN_DIR, image.filename))

def get_friendly_markdown_name(markdown_file_path: str) -> List[str]:
    markdown_file = MarkdownFile()
    markdown_file.file_path = markdown_file_path
    markdown_file.set_defaults()
    return markdown_file.name

@app.route('/api/v1/resources/upload_image', methods=['POST'])
def upload_image():
    if request.files['image'].filename != '':
        image = request.files['image']
        upload_image(image)


@app.route('/api/v1/resources/delete_image', methods=['POST'])
def delete_image():
    image_file_path = request.form.get("image_file_path")
    delete_image_file(image_file_path)


@app.route('/api/v1/resources/save_markdown', methods=['POST'])
def save_markdown():
    file_path = request.form.get("file_path")
    name = request.form.get("name")
    urencoded_path = request.form.get("urencoded_path")
    markdown = request.form.get("markdown")
    markdown_file = MarkdownFile(file_path=file_path,
                                 name=name,
                                 urlencoded_path=urencoded_path,
                                 markdown=markdown)

    save_result = save_markdown_file(markdown_file)
    return jsonify(save_result=save_result)

@app.route('/api/v1/resources/get_markdown_names', methods=['GET'])
def get_markdown_names():
    markdown_names = []
    markdown_files = get_markdown_file_paths()
    for file_path in markdown_files:
        friendly_markdown_name = get_friendly_markdown_name(file_path)
        markdown_names.append(friendly_markdown_name)
    return jsonify(markdown_names=markdown_names)

@app.route('/api/v1/resources/get_markdown', methods=['GET'])
def api_get_markdown():
    markdown_name = request.args.get('markdown_name', default=1, type=str)
    markdown = MarkdownFile()
    markdown.from_friendly_name(friendly_name=markdown_name)
    markdown.get_markdown_file_contents()
    return jsonify(name=markdown.name, 
                   path=markdown.file_path, 
                   urlencoded_path=markdown.urlencoded_path, 
                   markdown=markdown.markdown)

@app.route('/', methods=['GET', 'POST'])
def index():
    markdown_files = get_markdown_file_paths()
    todo_items = get_project_readme_todos()
    return render_template('index.html', todo_items=todo_items)

if __name__ == '__main__':
    app.run()

