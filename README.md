# Jarvis Printer
## Python Flask website and script to connect to a Cat Printer (GB01)

To run the website in quick'n'dirty mode, run flask with the local machine's local network IP, ie: `flask run -h 192.168.0.35'

During development Flask can automatically reload the application when changed, use the following envar: `FLASK_ENV=development flask run....`


## Notes:

### Current behaviour
The core CatPrinter is working as expected, and passing a Markdown file to it works also as expected (including rendering and printing images).

### To Do

 - [ ] Flask Config for site props [markdown_dir,]
 - [ ] Some form of keep alive, probably within the flask application
 - [ ] WebAPI - Get all markdown files
 - [ ] WebAPI - Get a single markdown file
 - [ ] WebAPI - Update a single markdown file
 - [ ] WebAPI - Create a new markdown file
 - [ ] WebAPI - upload files (markdown and images)
 - [ ] WebAPI - file deletion (markdown and images)