"""serialprinter"""
from os import path
from escpos.printer import Serial

from PIL import Image, ImageDraw, ImageFont

from md2png import *
from markdown_file import MarkdownFile

# import md2png


class SerialPrinter:
    def __init__(
        self,
        dev_port: str = "/dev/ttyUSB0",
        baud_rate: int = 9600,
        scale_feed: bool = False,
        contrast: int = 1,
        throttle_length: int = 0,
        debug: bool = False,
    ):
        """gb01print constructor
        Args:
            dev_port (str): Hardware device path, defaults to `/dev/ttyUSB0`,
            baud_rate (int): Baud of the serial connection, defaults to `9600`,
            scale_feed (true): Proportionately adjust blank paper
                feed when resizing image,
            contrast (Contrast enum, defaults to Medium): Contrast,
            throttle_length (int, defaults to 0): Delay between
                command queue packets,
            debug (bool, defaults to False): Debug switch,
        Returns:
            None
        """
        self.dev_port = dev_port
        self.baud_rate = baud_rate
        self.scale_feed = scale_feed
        self.contrast = contrast
        self.throttle_length = throttle_length
        self.debug = debug
        self.print_data = Image.new("RGBA", (384, 1), (255, 255, 255, 0))
        self.PRINTER_WIDTH = 384
        self.setup_printer()

    def print(self):
        """Send the self.print_data to the printer
        Args:
            None,
        Returns:
            None,
        """
        self.device.image(self.print_data)

    def add_markdown(self, markdownfile_path: str):
        """Prints an image created from a markdown file
        Args:
            markdownfile_path (str): Path to a markdown file,
        Returns:
            None,
        """
        width = int(self.PRINTER_WIDTH)
        print("Reading %s" % markdownfile_path)
        f = open(markdownfile_path)
        image = md2png(
            f.read(),
            [(0, 0, width)],
            {
                "font_size": 20,
                "code_font_size": 20,
            },
        )

        self.add_image(image)
        print("Added to self.print_data: add_markdown: %s" % markdownfile_path)

    def add_feed(self, feed_lines: int):
        """Adds white space by feed_lines X 10
        Args:
            feed_lines (int): how many lines of blank paper to feed,
        Returns:
            None,
        """
        image = Image.new("RGBA", (10, feed_lines), (255, 255, 255))
        self.render_image(image)
        print("Added to self.print_data: add_feed: %s" % feed_lines)

    def add_image(self, image: Image, feed_pre: int = 0, feed_post: int = 0):
        """Prints a image from a Pillow Image
        Args:
            image (Pillow.Image): Image object,
            feed_pre (int, defaults to 0): before printing printer
                will auto feed multiple blank lines,
            feed_post (int, defaults to 0): after printing printer
                will auto feed multiple blank lines,
        Returns:
            None,
        """
        self.render_image(image)
        print("Added to self.print_data: add_image")

    def add_image_file(
        self, imagefile_path: str, feed_pre: int = 0, feed_post: int = 0
    ):
        """Prints a image from a file path
        Args:
            imagefile_path (str): Path to a image file,
            feed_pre (int, defaults to 0): before printing printer
                will auto feed multiple blank lines,
            feed_post (int, defaults to 0): after printing printer
                will auto feed multiple blank lines,
        Returns:
            None,
        """
        image = Image.open(imagefile_path)
        self.render_image(image)
        print("Added to self.print_data: add_image_file: %s" % imagefile_path)

    def add_text_string(
        self,
        text_string: str,
        feed_pre: int = 0,
        feed_post: int = 0,
    ):
        """Prints a text string
        Args:
            text_string (str): string of text to print,
            print_data (I have no idea what this is yet...),
            feed_pre (int, defaults to 0): before printing printer
                will auto feed multiple blank lines,
            feed_post (int, defaults to 0): after printing printer
                will auto feed multiple blank lines,
        Returns:
            None,
        """
        image = self.drawText(text_string)
        self.render_image(image)
        print("Added to self.print_data: add_text_string: %s" % text_string)

    def add_text_file(self, textfile_path: str, feed_pre: int = 0, feed_post: int = 0):
        """Prints the text in a file
        Args:
            textfile_path (str): Path to a text file,
            feed_pre (int, defaults to 0): before printing printer
                will auto feed multiple blank lines,
            feed_post (int, defaults to 0): after printing printer
                will auto feed multiple blank lines,
        Returns:
            None,
        """
        text_file = open(textfile_path)
        text_to_print = text_file.read()
        image = self.drawText(text_to_print, from_file=True)
        self.render_image(image)
        print("Added to self.print_data: add_text_file: %s" % textfile_path)

    def setup_printer(self):
        """Sets up a Serial Printer
        Args:
            None,
        Returns:
            None
        """

        self.device = Serial(
            devfile=self.dev_port,
            baudrate=self.baud_rate,
            bytesize=8,
            parity="N",
            stopbits=1,
            timeout=1.00,
            dsrdtr=True,
        )

    def drawText(self, text: str, from_file: bool = False, font=None) -> Image:
        """Creates an empty block of print_data
        Args:
            text (str),
            from_file (bool, defaults to False),
            font (no idea what type),
        Returns:
            text as an image (Image)
        """
        text_chunks = []
        if font is None:
            font = ImageFont.truetype("text/Sono-Regular.ttf", 20)  # 38 chars max
            # font = ImageFont.truetype("text/Consolas.ttf", 20) # 34 chars max
            max_line_length = 38
        if len(text) > max_line_length and not from_file:
            text_chunks = [
                text[i : i + max_line_length]
                for i in range(0, len(text), max_line_length)
            ]
            text = "\n".join(text_chunks)

        image = Image.new("RGBA", (10, self.PRINTER_WIDTH), (255, 255, 255, 0))
        draw = ImageDraw.Draw(image)

        text_size = draw.textsize(text, font)
        image = Image.new("RGBA", text_size, (255, 255, 255, 0))

        draw = ImageDraw.Draw(image)
        draw.text((0, 0), text, (0, 0, 0), font)

        return image

    def render_image(self, image: Image):
        """Adds an image to the buffer
        Args:
            image (Image),
        Returns:
            None
        """

        if image.width > self.PRINTER_WIDTH:
            # image is wider than printer resolution; scale it down proportionately
            scale = self.PRINTER_WIDTH / image.width
            if self.scale_feed:
                header_lines = int(self.HEADER_LINES * scale)
                feed_lines = int(self.FEED_LINES * scale)
            image = image.resize((self.PRINTER_WIDTH, int(image.height * scale)))
        if image.width < (self.PRINTER_WIDTH // 2):
            # scale up to largest whole multiple
            scale = self.PRINTER_WIDTH // image.width
            if self.scale_feed:
                header_lines = int(header_lines * scale)
                feed_lines = int(feed_lines * scale)
            image = image.resize(
                (image.width * scale, image.height * scale), resample=Image.NEAREST
            )
        # convert image to black-and-white 1bpp color format
        image = image.convert("RGB")
        image = image.convert("1")
        if image.width < self.PRINTER_WIDTH:
            # image is narrower than printer resolution
            # pad it out with white pixels
            pad_amount = (self.PRINTER_WIDTH - image.width) // 2
            padded_image = Image.new(
                "RGBA", (self.PRINTER_WIDTH, image.height), (255, 255, 255, 0)
            )
            padded_image.paste(image, box=(pad_amount, 0))
            image = padded_image

        new_image = Image.new(
            "RGBA",
            (self.print_data.width, image.height + self.print_data.height),
            (255, 255, 255, 0),
        )
        new_image.paste(self.print_data, (0, 0))
        new_image.paste(image, (0, self.print_data.height))

        self.print_data = new_image


def main():
    markdown_name = "test"
    markdown = MarkdownFile()
    markdown.from_friendly_name(friendly_name=markdown_name)
    serial_printer = SerialPrinter()
    serial_printer.add_markdown(markdown.file_path)
    serial_printer.add_feed(2)
    serial_printer.print()


if __name__ == "__main__":
    main()
