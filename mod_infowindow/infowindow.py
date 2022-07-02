from driver import epd7in5b_V2
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from PIL import ImageChops
import os, sys
import logging
import tempfile


def display_frame(epd, image_data):
    rgb_image = image_data.convert('RGB')
    width, height = image_data.size
    no_red = Image.new('RGB', (width, height), (255, 255, 255))
    only_red = Image.new('RGB', (width, height), (255, 255, 255))

    for col in range(width):
        for row in range(height):

            r, g, b = rgb_image.getpixel((col, row))
            if r == 255 and g == 255 and b == 255:
                no_red.putpixel((col, row), (255, 255, 255))
            elif r == 0 and g == 0 and b == 0:
                no_red.putpixel((col, row), (0, 0, 0))
            else:
                no_red.putpixel((col, row), (0, g, b))

            if r == 255 and g == 0 and b == 0:
                only_red.putpixel((col, row), (0, 0, 0))
            else:
                only_red.putpixel((col, row), (255, 255, 255))

    epd.display(epd.getbuffer(no_red), epd.getbuffer(only_red))
    epd.sleep()


class InfoWindow:
    def __init__(self, options):
        self.epd = epd7in5b_V2.EPD()
        self.epd.init()
        self.width = 800
        self.height = 480
        self.image = Image.new(mode="RGB", size=(800, 480), color=(255, 255, 255))
        self.draw = ImageDraw.Draw(self.image)
        self.fonts = {}
        self.initFonts()
        self.tmpImagePath = os.path.join(tempfile.gettempdir(), "InfoWindow.png")
        self.timeformat = options['timeformat']

    def getCWD(self):
        path = os.path.dirname(os.path.realpath(sys.argv[0]))
        return path

    def getImage(self):
        return self.image

    def getDraw(self):
        return self.draw

    def getEpd(self):
        return self.epd

    def line(self, left_1, top_1, left_2, top_2, fill, width=1):
        self.draw.line((left_1, top_1, left_2, top_2), fill=fill)

    def rectangle(self, tl, tr, bl, br, fill):
        self.draw.rectangle(((tl, tr), (bl, br)), fill=fill)

    def text(self, left, top, text, font, fill):
        font = self.fonts[font]
        self.draw.text((left, top), text, font=font, fill=fill)
        return self.draw.textsize(text, font=font)

    def rotate(self, angle):
        self.image.rotate(angle)

    # def chord(self, x, y, xx, yy, xxx, yyy, fill):
    #     self.draw.chord((x, y, xx, yy), xxx, yyy, fill)

    def bitmap(self, x, y, image_path):
        bitmap = Image.open(self.getCWD()+"/icons/"+image_path)
        # self.image.paste((0, 0), (x, y), 'black', bitmap)
        self.draw.bitmap((x, y), bitmap, fill=(0, 0, 0))

    def getFont(self, font_name):
        return self.fonts[font_name]

    def initFonts(self):
        roboto = self.getCWD()+"/fonts/roboto/Roboto-"
        self.fonts = {

            'robotoBlack18': ImageFont.truetype(roboto + "Black.ttf", 18),
            'robotoBlack24': ImageFont.truetype(roboto + "Black.ttf", 24),
            'robotoBlack54': ImageFont.truetype(roboto + "Black.ttf", 54),
            'robotoRegular18': ImageFont.truetype(roboto + "Regular.ttf", 18),
            'robotoRegular14': ImageFont.truetype(roboto + "Regular.ttf", 14),
            'robotoRegular22': ImageFont.truetype(roboto + "Regular.ttf", 22),
        }

    def truncate(self, string, font, max_size):
        num_chars = len(string)
        for char in string:
            (np_x, np_y) = self.getFont(font).getsize(string)
            if np_x >= max_size:
                string = string[:-1]

            if np_x <= max_size:
                return string

        return string

    def display(self, angle):
        self.image = self.image.rotate(angle)

        new_image_found = True
        if os.path.exists(self.tmpImagePath):
            old_image = Image.open(self.tmpImagePath)
            diff = ImageChops.difference(self.image, old_image)
            if not diff.getbbox():
                new_image_found = False

        if new_image_found:
            logging.info("New information in the image detected. Updating the screen.")
            self.image.save(self.tmpImagePath)
            display_frame(self.epd, self.image)
        else:
            logging.info("No new information found. Not updating the screen.")
