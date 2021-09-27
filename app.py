"""jarvis_printer"""
import glob
import os, sys
import urllib.parse
from enum import Enum
from pathlib import Path
from dataclasses import dataclass
from typing import List
from flask import Flask, render_template, jsonify, request
from CatPrinter import catprinter

app = Flask(__name__)
MARKDOWN_DIR="static/markdown"
IMAGES_DIR="images"
LOCAL_DIR=os.path.dirname(os.path.realpath(__file__))

class SuccessErrors(Enum):
    Success = 0
    FileExists = 1
    CreateFileError = 2
    UpdateFileError = 3
    FileDoesNotExist = 4
    UnableToDeleteFile = 5
    Undefined = 99

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
    markdown_file_mask = ("%s/*.md" % (MARKDOWN_DIR))
    markdown_file_paths = (glob.glob(markdown_file_mask))
    markdown_files = []
    for file_path in markdown_file_paths:
        markdown_files.append(file_path)
    return markdown_files

def get_image_file_paths():
    """Returns all image file paths in a specified directory
    Args:
        None,
    Returns:
        image_files (List[str]),
    """
    jpg_filemask = ("%s/%s/*.jpg" % (MARKDOWN_DIR, IMAGES_DIR))
    jpeg_filemask = ("%s/%s/*.jpg" % (MARKDOWN_DIR, IMAGES_DIR))
    png_filemask = ("%s/%s/*.png" % (MARKDOWN_DIR, IMAGES_DIR))
    print("%s/%s/*jpg" % (MARKDOWN_DIR, IMAGES_DIR))
    jpg_file_paths = (glob.glob(jpg_filemask))
    jpeg_file_paths = (glob.glob(jpeg_filemask))
    png_file_paths = (glob.glob(png_filemask))
    image_files = []
    for file_path in jpg_file_paths:
        image_files.append(file_path)
    for file_path in jpeg_file_paths:
        image_files.append(file_path)
    for file_path in png_file_paths:
        image_files.append(file_path)
    return image_files

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

def delete_markdown_file(markdown_name:str) -> SuccessErrors:
    """Deletes a markdown file
    Args:
        markdown_file (MarkdownFile),
    Returns:
        success (SuccessErrors),
    """
    success = SuccessErrors.Undefined
    markdown_file = MarkdownFile()
    print(markdown_name)
    print(markdown_file.name)
    print(markdown_file.file_path)
    print(markdown_file.urlencoded_path)
    print(markdown_file.markdown)
    markdown_file.from_friendly_name(markdown_name)
    if file_exists(markdown_file.file_path):
        os.remove(markdown_file.file_path)
        if file_exists(markdown_file.file_path):
            success = SuccessErrors.UnableToDeleteFile
        else:
            success = SuccessErrors.Success
    else:
        success = SuccessErrors.FileDoesNotExist

    return success


def delete_image_file(image_file_path:str) -> None:
    """Deletes a image file
    Args:
        image_file_path (str),
    Returns:
        None,
    """
    os.remove(image_file_path)

def get_friendly_markdown_name(markdown_file_path: str) -> str:
    """Returns a markdowns friendly name
    Args:
        markdown_file_path (str),
    Returns:
        markdown_file name (str),
    """
    markdown_file = MarkdownFile()
    markdown_file.file_path = markdown_file_path
    markdown_file.set_defaults()
    return markdown_file.name

def upload_file(file) -> SuccessErrors:
    """Uploads a file
    Args:
        file_data (str),
        file_name (str),
    Returns:
        None,
    """
    success = SuccessErrors.CreateFileError
    full_path = ("%s/%s/%s/%s" % (LOCAL_DIR, MARKDOWN_DIR, IMAGES_DIR, file.filename))
    file.save(full_path)
    if file_exists(full_path):
        success = SuccessErrors.Success
    return success

def file_exists(full_path:str) -> bool:
    """Returns if a file exists
    Args:
        full_path (str),
    Returns:
        file_exists (bool),
    """
    file_exists = Path(full_path).exists()
    return file_exists

def create_markdown_file_from_filename(markdown_filename:str) -> SuccessErrors:
    """Creates a markdown file based on incoming filename suggestion
        If already exists, returns false,
        If other os.file issue, returns false,
        If successful, returns true
    Args:
        markdown_filename (str),
    Returns:
        success (SuccessErrors),
    """
    success = SuccessErrors.Undefined
    full_path = ("%s/%s/%s" % (LOCAL_DIR, MARKDOWN_DIR, markdown_filename))

    if file_exists(full_path):
        success = SuccessErrors.FileExists
    else:
        open(full_path, 'a').close()
        if file_exists(full_path):
            success = SuccessErrors.Success

    return success

@app.route('/api/v1/resources/create_markdown_file', methods=['GET'])
def create_markdown_file():
    result_message = ""
    markdown_filename = request.args.get('markdown_filename', default="", type=str)
    success = create_markdown_file_from_filename(markdown_filename)
    if success == SuccessErrors.Undefined:
        result_message = "Something went wrong.. not sure what..."
    elif success == SuccessErrors.FileExists:
        result_message = "A file with that name already exists?"
    elif success == SuccessErrors.CreateFileError:
        result_message = "Something went wrong trying to create the new file."
    elif success == SuccessErrors.Success:
        result_message = "File successfully created."

    return jsonify(success=result_message)

@app.route('/api/v1/resources/upload_image', methods=['POST'])
def upload_image():
    success = False
    if request.method == 'POST':
        file = request.files['userfile']
        upload_file(file)
    else:
        print('why was this a GET?!?!')

    return jsonify(success=True)

@app.route('/api/v1/resources/delete_image', methods=['POST'])
def delete_image():
    image_file_path = request.form.get("image_file_path")
    delete_image_file(image_file_path)

    return jsonify(True)

@app.route('/api/v1/resources/delete_markdown', methods=['GET'])
def delete_markdown():
    result = "Something went terribly, terribly wrong.."
    friendly_file_path = request.args.get("markdown_name")
    delete_result = delete_markdown_file(friendly_file_path)

    if delete_result == SuccessErrors.Undefined:
        result = "Something went terribly, terribly wrong.."
    elif delete_result == SuccessErrors.UnableToDeleteFile:
        result = "We tried to, but were unable to delete the file"
    elif delete_result == SuccessErrors.FileDoesNotExist:
        result = "That... file... doesn't appear, to exist?... nope, no idea."
    elif delete_result == SuccessErrors.Success:
        result = "File deleted successfully."

    return jsonify(result)


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

@app.route('/api/v1/resources/get_image_filenames', methods=['GET'])
def get_image_filenames():
    image_files = get_image_file_paths()
    return jsonify(image_files=image_files)

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

    return markdown.markdown

@app.route('/api/v1/resources/print_markdown', methods=['GET'])
def print_markdown():
    markdown_name = request.args.get('markdown_name', default=1, type=str)
    markdown = MarkdownFile()
    markdown.from_friendly_name(friendly_name=markdown_name)
    cat_printer = catprinter.CatPrinter()
    cat_printer.add_markdown(LOCAL_DIR + "/" + markdown.file_path)
    cat_printer.add_feed(3)
    cat_printer.print()

    return jsonify(name=markdown.name,
                   path=markdown.file_path,
                   urlencoded_path=markdown.urlencoded_path,
                   markdown=markdown.markdown)

@app.route('/markdown_editor', methods=['GET', 'POST'])
def markdown_editor():

    images_path = ("%s/%s/" % (MARKDOWN_DIR, IMAGES_DIR))
    markdown_files = get_markdown_file_paths()
    imagepath_and_markdowns = []
    imagepath_and_markdowns.append(images_path)
    for file_path in markdown_files:
        friendly_markdown_name = get_friendly_markdown_name(file_path)
        imagepath_and_markdowns.append(friendly_markdown_name)
    global_api_host = request.host_url
    host_url_and_images_path = [global_api_host, images_path]
    return render_template('markdown_editor.html', host_url_and_images_path=host_url_and_images_path)

@app.route('/', methods=['GET', 'POST'])
def index():
    markdown_files = get_markdown_file_paths()
    todo_items = get_project_readme_todos()
    return render_template('index.html', todo_items=todo_items)

if __name__ == '__main__':
    app.run()

