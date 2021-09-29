"""catprinter"""
import asyncio
from os import path

from bleak import BleakClient, BleakScanner
from bleak.exc import BleakError

import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont

from md2png import *
# import md2png

class CatPrinter:
    def __init__(self,
                    mac_address:str="",
                    packet_size:int=60,
                    scale_feed:bool=False,
                    contrast:int=1,
                    throttle_length:int=0,
                    debug:bool=False):
        """ gb01print constructor
        Args:
            mac_address (str): Can be unpopulated, as the application
                will seek for a GB01 named Bluetooth device,
                packet_size (int): Packet size to send to the printer,
                scale_feed (true): Proportionately adjust blank paper
                    feed when resizing image,
                contrast (Contrast enum, defaults to Medium): Contrast,
                throttle_length (int, defaults to 0): Delay between
                    command queue packets,
                debug (bool, defaults to False): Debug switch,
        Returns:
            None
        """
        self.mac_address = mac_address.replace(':', '').upper()
        self.packet_size = packet_size
        self.scale_feed = scale_feed
        self.contrast = contrast
        self.throttle_length = throttle_length
        self.debug = debug

        self.ENERGY = {
            0: self.printer_short(8000),
            1: self.printer_short(12000),
            2: self.printer_short(17500)
        }

        self.PRINTER_WIDTH = 384
        self.PACKET_SIZE = 60
        self.RETRACT_PAPER = 0xA0  # Data: Number of steps to go back
        self.FEED_PAPER = 0xA1  # Data: Number of steps to go forward
        self.DRAW_BITMAP = 0xA2  # Data: Line to draw. 0 bit -> don't draw pixel, 1 bit -> draw pixel
        self.GET_DEVICE_STATE = 0xA3  # Data: 0
        self.CONTROL_LATTICE = 0xA6  # Data: Eleven bytes, all constants. One set used before printing, one after.
        self.GET_DEVICE_INFO = 0xA8  # Data: 0
        self.OTHER_FEED_PAPER = 0xBD  # Data: one byte, set to a device-specific "Speed" value before printing
                                      # and to 0x19 before feeding blank paper
        self.DRAWING_MODE = 0xBE  # Data: 1 for Text, 0 for Images
        self.SET_ENERGY = 0xAF  # Data: 1 - 0xFFFF
        self.SET_QUALITY = 0xA4  # Data: 0x31 - 0x35. APK always sets 0x33 for GB01
        self.PRINT_LATTICE = [0xAA, 0x55, 0x17, 0x38, 0x44, 0x5F, 0x5F, 0x5F, 0x44, 0x38, 0x2C]
        self.FINISH_LATTICE = [0xAA, 0x55, 0x17, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x17]
        self.X_OFF = (0x51, 0x78, 0xAE, 0x01, 0x01, 0x00, 0x10, 0x70, 0xFF)
        self.X_ON = (0x51, 0x78, 0xAE, 0x01, 0x01, 0x00, 0x00, 0x00, 0xFF)
        self.IMG_PRINT_SPEED = [0x23]
        self.BLANK_SPEED = [0x19]
        self.PRINTER_CHARACTERISTIC = "0000AE01-0000-1000-8000-00805F9B34FB"
        self.NOTIFY_CHARACTERISTIC = "0000AE02-0000-1000-8000-00805F9B34FB"

        self.lines = 0
        self.contrast = 1
        self.feed_lines = 112
        self.header_lines = 0
        self.scale_feed = False
        self.packet_length = 60
        self.throttle = 0.01

        self.device = None

        self.initial_data = self.request_status()
        self.print_data = []

        # TODO -
        # self.printer = self.setup_printer(self)
        # if self.printer_setup:
        #     self.keep_alive_timer

    def get_or_create_eventloop(self):
        try:
            return asyncio.get_event_loop()
        except RuntimeError as ex:
            if "There is no current event loop in thread" in str(ex):
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                return asyncio.get_event_loop()

    def print(self):
        """In a async loop, send the self.print_data to the printer
        Args:
            print_data (I have no idea what this is yet),
        Returns:
            success (bool),
        """
        loop = self.get_or_create_eventloop()
        loop.run_until_complete(self.connect_and_send(self.initial_data + self.print_data))

    def add_markdown(self,
                     markdownfile_path:str):
        """Prints an image created from a markdown file
        Args:
            markdownfile_path (str): Path to a markdown file,
        Returns:
            None,
        """
        width = int(self.PRINTER_WIDTH)
        print("Reading %s" % markdownfile_path)
        f = open(markdownfile_path)
        image = md2png(f.read(), [(0, 0, width)], {
            "font_size": 20,
            "code_font_size": 20,
        })

        self.add_image(image)
        print("Added to self.print_data: add_markdown: %s" % markdownfile_path)

    def add_feed(self,
                 feed_lines:int):
        """Feeds (unprinted) paper
        Args:
            feed_lines (int): how many lines of blank paper to feed,
        Returns:
            None,
        """
        image = PIL.Image.new('RGBA', (10, feed_lines), (255, 255, 255))
        self.print_data = self.print_data + self.render_image(image)
        print("Added to self.print_data: add_feed: %s" % feed_lines)

    def add_image(self,
                    image:PIL.Image,
                    feed_pre:int=0,
                    feed_post:int=0):
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
        self.print_data = self.print_data + self.render_image(image)
        print("Added to self.print_data: add_image")

    def add_image_file(self,
                    imagefile_path:str,
                    feed_pre:int=0,
                    feed_post:int=0):
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
        image = PIL.Image.open(imagefile_path)
        self.print_data = self.print_data + self.render_image(image)
        print("Added to self.print_data: add_image_file: %s" % imagefile_path)


    def add_text_string(self,
                    text_string:str,
                    feed_pre:int=0,
                    feed_post:int=0,
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
        text_to_print = text_string
        image = self.drawText(text_to_print)
        self.print_data = self.print_data + self.render_image(image)
        print("Added to self.print_data: add_text_string: %s" % text_string)


    def add_text_file(self,
                    textfile_path:str,
                    feed_pre:int=0,
                    feed_post:int=0):
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
        self.print_data = self.print_data + self.render_image(image)
        print("Added to self.print_data: add_text_file: %s" % textfile_path)

    def setup_printer(self, detected=None, advertisement_data=None):
        """Sets up a GB01 Cat Printer
        Args:
            detected (I have no idea),
            advertisement_data (I have no idea),
        Returns:
            detected (BLEDevice): Bleak.BLE Device,
        """
        # detected = None
        # advertisement_data = None
        if self.mac_address and detected:
            cut_addr = detected.address.replace(":", "")[-(len(self.mac_address)):].upper()
            if cut_addr != self.mac_address:
                return
        if detected and detected.name == 'GB01':
            self.device = detected
            print("Device detected, Mac address: %s" % self.device.address)
            return detected

    crc8_table = (
        0x00, 0x07, 0x0e, 0x09, 0x1c, 0x1b, 0x12, 0x15, 0x38, 0x3f, 0x36, 0x31,
        0x24, 0x23, 0x2a, 0x2d, 0x70, 0x77, 0x7e, 0x79, 0x6c, 0x6b, 0x62, 0x65,
        0x48, 0x4f, 0x46, 0x41, 0x54, 0x53, 0x5a, 0x5d, 0xe0, 0xe7, 0xee, 0xe9,
        0xfc, 0xfb, 0xf2, 0xf5, 0xd8, 0xdf, 0xd6, 0xd1, 0xc4, 0xc3, 0xca, 0xcd,
        0x90, 0x97, 0x9e, 0x99, 0x8c, 0x8b, 0x82, 0x85, 0xa8, 0xaf, 0xa6, 0xa1,
        0xb4, 0xb3, 0xba, 0xbd, 0xc7, 0xc0, 0xc9, 0xce, 0xdb, 0xdc, 0xd5, 0xd2,
        0xff, 0xf8, 0xf1, 0xf6, 0xe3, 0xe4, 0xed, 0xea, 0xb7, 0xb0, 0xb9, 0xbe,
        0xab, 0xac, 0xa5, 0xa2, 0x8f, 0x88, 0x81, 0x86, 0x93, 0x94, 0x9d, 0x9a,
        0x27, 0x20, 0x29, 0x2e, 0x3b, 0x3c, 0x35, 0x32, 0x1f, 0x18, 0x11, 0x16,
        0x03, 0x04, 0x0d, 0x0a, 0x57, 0x50, 0x59, 0x5e, 0x4b, 0x4c, 0x45, 0x42,
        0x6f, 0x68, 0x61, 0x66, 0x73, 0x74, 0x7d, 0x7a, 0x89, 0x8e, 0x87, 0x80,
        0x95, 0x92, 0x9b, 0x9c, 0xb1, 0xb6, 0xbf, 0xb8, 0xad, 0xaa, 0xa3, 0xa4,
        0xf9, 0xfe, 0xf7, 0xf0, 0xe5, 0xe2, 0xeb, 0xec, 0xc1, 0xc6, 0xcf, 0xc8,
        0xdd, 0xda, 0xd3, 0xd4, 0x69, 0x6e, 0x67, 0x60, 0x75, 0x72, 0x7b, 0x7c,
        0x51, 0x56, 0x5f, 0x58, 0x4d, 0x4a, 0x43, 0x44, 0x19, 0x1e, 0x17, 0x10,
        0x05, 0x02, 0x0b, 0x0c, 0x21, 0x26, 0x2f, 0x28, 0x3d, 0x3a, 0x33, 0x34,
        0x4e, 0x49, 0x40, 0x47, 0x52, 0x55, 0x5c, 0x5b, 0x76, 0x71, 0x78, 0x7f,
        0x6a, 0x6d, 0x64, 0x63, 0x3e, 0x39, 0x30, 0x37, 0x22, 0x25, 0x2c, 0x2b,
        0x06, 0x01, 0x08, 0x0f, 0x1a, 0x1d, 0x14, 0x13, 0xae, 0xa9, 0xa0, 0xa7,
        0xb2, 0xb5, 0xbc, 0xbb, 0x96, 0x91, 0x98, 0x9f, 0x8a, 0x8d, 0x84, 0x83,
        0xde, 0xd9, 0xd0, 0xd7, 0xc2, 0xc5, 0xcc, 0xcb, 0xe6, 0xe1, 0xe8, 0xef,
        0xfa, 0xfd, 0xf4, 0xf3
    )


    def crc8(self, data):
        crc = 0
        for byte in data:
            crc = self.crc8_table[(crc ^ byte) & 0xFF]
        return crc & 0xFF

    def format_message(self, command, data):
        data = ([0x51, 0x78]
                + [command]
                + [0x00]
                + [len(data)]
                + [0x00]
                + data
                + [self.crc8(data)]
                + [0xFF])
        return data


    def printer_short(self, incoming_int:int) -> int:
        """ Returns a short int from an incoming int,
            (unsure if it's signed or not)
        Args:
            incoming_int (int),
        Returns:
            outgoing_shint (int, shorted),
        """
        outgoing_shint = [incoming_int & 0xFF, (incoming_int >> 8) & 0xFF]
        return outgoing_shint

    async def connect_and_send(self, data) -> None:
        """ Uses Bleak to call through BLE to:
             - detect a printer
                - sets up a client
                    - sleeps and sends data (looped)
        Args:
            data (no idea what type): data to be set to printer,
        Returns:
            None,,
        """
        scanner = BleakScanner()
        scanner.register_detection_callback(self.setup_printer)
        await scanner.start()
        for x in range(50):
            await asyncio.sleep(0.1)
            if self.device:
                break
        await scanner.stop()

        if not self.device:
            raise BleakError(f"The printer was not found.")
        async with BleakClient(self.device) as client:
            # Set up callback to handle messages from the printer
            await client.start_notify(self.NOTIFY_CHARACTERISTIC, self.notification_handler)

            while data:
                # Cut the command stream up into pieces small enough for the printer to handle
                await client.write_gatt_char(self.PRINTER_CHARACTERISTIC,
                                             bytearray(data[:self.packet_length]))
                data = data[self.packet_length:]
                if self.throttle is not None:
                    await asyncio.sleep(self.throttle)


    def request_status(self):
        """ Returns status of printer
        Args:
            None,
        Returns:
            status (no idea what type)
        """
        status = self.format_message(self.GET_DEVICE_STATE, [0x00])
        return status


    def blank_paper(self, lines:int):
        """ Creates an empty block of print_data
        Args:
            lines (int): How many blank lines to print,
        Returns:
            empty block of print_data (no idea what type)
        """
        # Feed extra paper for image to be visible
        blank_commands = self.format_message(self.OTHER_FEED_PAPER,
                                             self.BLANK_SPEED)
        count = self.lines
        while count:
            feed = min(count, 0xFF)
            blank_commands = (blank_commands
                               + self.format_message(
                                   lines,
                                   self.printer_short(feed)))
            count = count - feed
        return blank_commands

    def drawText(self,
                 text:str,
                 from_file:bool=False,
                 font=None)->PIL.Image:
        """ Creates an empty block of print_data
        Args:
            text (str),
            from_file (bool, defaults to False),
            font (no idea what type),
        Returns:
            text as an image (PIL.Image)
        """
        text_chunks = []
        if font is None:
            font = PIL.ImageFont.truetype("text/Sono-Regular.ttf", 20) # 38 chars max
            #font = PIL.ImageFont.truetype("text/Consolas.ttf", 20) # 34 chars max
            max_line_length = 38
        if len(text) > max_line_length and not from_file:
            text_chunks = [text[i:i+max_line_length]
                for i in range(0, len(text), max_line_length)]
            text = '\n'.join(text_chunks)

        img = PIL.Image.new(
            'RGBA',
            (10, self.PRINTER_WIDTH),
            (255, 255, 255, 0))
        draw = PIL.ImageDraw.Draw(img)

        text_size = draw.textsize(text, font)
        img = PIL.Image.new(
            'RGBA',
            text_size,
            (255, 255, 255, 0))

        draw = PIL.ImageDraw.Draw(img)
        draw.text((0,0), text, (0,0,0), font)

        return img


    def render_image(self, image:PIL.Image):
        """ Wraps an image in printer commands and printer image structure
            and returns print)data from it
        Args:
            image (PIL.Image),
        Returns:
            print_data (no idea what type)
        """
        command_queue = []
        # Set quality to standard
        command_queue += self.format_message(self.SET_QUALITY, [0x33])
        # start and/or set up the lattice, whatever that is
        command_queue += self.format_message(self.CONTROL_LATTICE, self.PRINT_LATTICE)
        # Set energy used
        command_queue += self.format_message(self.SET_ENERGY, self.ENERGY[self.contrast])
        # Set mode to image mode
        command_queue += self.format_message(self.DRAWING_MODE, [0])
        # not entirely sure what this does
        command_queue += self.format_message(self.OTHER_FEED_PAPER, self.IMG_PRINT_SPEED)

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
            image = image.resize((image.width * scale, image.height * scale), resample=PIL.Image.NEAREST)
        # convert image to black-and-white 1bpp color format
        image = image.convert("RGB")
        image = image.convert("1")
        if image.width < self.PRINTER_WIDTH:
            # image is narrower than printer resolution
            # pad it out with white pixels
            pad_amount = (self.PRINTER_WIDTH - image.width) // 2
            padded_image = PIL.Image.new("1", (self.PRINTER_WIDTH, image.height), 1)
            padded_image.paste(image, box=(pad_amount, 0))
            image = padded_image

        if self.header_lines:
            command_queue += self.blank_paper(self.header_lines)

        for y in range(0, image.height):
            bmp = []
            bit = 0
            # pack image data into 8 pixels per byte
            for x in range(0, image.width):
                if bit % 8 == 0:
                    bmp += [0x00]
                bmp[int(bit / 8)] >>= 1
                if not image.getpixel((x, y)):
                    bmp[int(bit / 8)] |= 0x80
                else:
                    bmp[int(bit / 8)] |= 0

                bit += 1

            command_queue += self.format_message(self.DRAW_BITMAP, bmp)

        # finish the lattice, whatever that means
        command_queue += self.format_message(self.CONTROL_LATTICE, self.FINISH_LATTICE)

        return command_queue

    def notification_handler(self, sender, data):
        """ Still trying to work out exactly what this does...
        Args:
            sender (no idea what type),
            data (might be print_data?),
        Returns:
            print_data (no idea what type)
        """
        if self.debug:
            print("{0}: [ {1} ]".format(sender, " ".join("{:02X}".format(x) for x in data)))
        if tuple(data) == self.X_OFF:
            print("ERROR: printer data overrun!")
            return
        if data[2] == self.GET_DEVICE_STATE:
            if data[6] & 0b1000:
                print("warning: low battery! print quality might be affected…")
            # print("printer status byte: {:08b}".format(data[6]))
            # xxxxxxx1 no_paper ("No paper.")
            # xxxxxx10 paper_positions_open ("Warehouse.")
            # xxxxx100 too_hot ("Too hot, please let me take a break.")
            # xxxx1000 no_power_please_charge ("I have no electricity, please charge")
            # I don't know if multiple status bits can be on at once, but if they are, then iPrint won't detect them.
            # In any case, I think the low battery flag is the only one the GB01 uses.
            # It also turns out this flag might not turn on, even when the battery's so low the printer shuts itself off…
            return

def main():
    cat_printer = CatPrinter()
    # cat_printer.add_text_string("Stardew Valley")
    # cat_printer.add_image("images/stardew.jpeg")
    # cat_printer.add_text_file("text/stardew.txt")
    # cat_printer.add_image("images/dogs.jpeg")
    # cat_printer.add_text_string("My dog is called 'Dan'.")
    cat_printer.add_markdown("static/markdown/test.md")
    cat_printer.add_feed(3)
    cat_printer.print()

if __name__ == "__main__":
    main()
