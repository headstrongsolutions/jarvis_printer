import urllib.parse


class MarkdownFile:
    MARKDOWN_DIR = "static/markdown"

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
        full_path = "%s/%s.md" % (self.MARKDOWN_DIR, friendly_name)
        temp_markdown_file = MarkdownFile()
        temp_markdown_file.file_path = full_path
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
            self.name = self.urlencoded_path.replace((self.MARKDOWN_DIR + "/"), "")
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
