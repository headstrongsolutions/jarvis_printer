# Jarvis Printer
## Python Flask website and script to connect to a Cat Printer (GB01)

To run the website in quick'n'dirty mode, run flask with the local machine's local network IP, ie: `flask run -h 192.168.0.35'

During development Flask can automatically reload the application when changed, use the following envar: `FLASK_ENV=development flask run....`


## Notes:

### Current behaviour
The core CatPrinter is working as expected, and passing a Markdown file to it works also as expected (including rendering and printing images).

### To Do
 - [X] 1 - Load markdown data into markdown-editor
 - [X] 2 - HTML form functionality for loading markdown files
 - [X] 2 - HTML form functionality for creating new markdown files
 - [ ] 2 - HTML form functionality for deleting markdown files
 - [ ] 3 - HTML form functionality for listing image files
 - [ ] 3 - Flask API functionality for listing image files
 - [ ] 3 - HTML form functionality for deleting image files
 - [ ] 4 - Some form of keep alive, probably within the flask application
 - [ ] 9 - Fix intermittent drag'n'drop error on markdown-editor
 - [X] 1 - Correct pathing for images in markdown docs
 - [X] HTML forms for markdown editing/preview
 - [X] WebAPI - Get all markdown files
 - [X] WebAPI - Get a single markdown file
 - [X] WebAPI - Update a single markdown file
 - [X] WebAPI - Create a new markdown file
 - [X] WebAPI - upload files (markdown and images)
 - [X] WebAPI - file deletion (markdown and images)
 - [X] To Do's on homepage
