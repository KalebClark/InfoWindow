from driver import epd7in5b_V2
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from PIL import ImageChops
import os, sys
import logging
import tempfile


class InfoWindow:
    def __init__(self, options):
        self.epd = epd7in5b_V2.EPD()
        self.epd.init()
        self.width = 800
        self.height = 480
        self.red_image = Image.new(mode="1", size=(800, 480), color=1)
        self.black_image = Image.new(mode="1", size=(800, 480), color=1)
        self.red_draw = ImageDraw.Draw(self.red_image)
        self.black_draw = ImageDraw.Draw(self.black_image)
        self.fonts = {}
        self.initFonts()
        self.tmpImagePathRed = os.path.join(tempfile.gettempdir(), "InfoWindowRed.png")
        self.tmpImagePathBlack = os.path.join(tempfile.gettempdir(), "InfoWindowBlack.png")
        self.timeformat = options['timeformat']

    def getCWD(self):
        path = os.path.dirname(os.path.realpath(sys.argv[0]))
        return path

    def line(self, left_1, top_1, left_2, top_2, fill):
        if fill == 'black':
            self.black_draw.line((left_1, top_1, left_2, top_2), fill=0)
        elif fill == 'red':
            self.red_draw.line((left_1, top_1, left_2, top_2), fill=0)
        elif fill == 'white':
            self.black_draw.line((left_1, top_1, left_2, top_2), fill=1)
            self.red_draw.line((left_1, top_1, left_2, top_2), fill=1)

    def rectangle(self, tl, tr, bl, br, fill):
        if fill == 'black':
            self.black_draw.rectangle(((tl, tr), (bl, br)), fill=0)
        elif fill == 'red':
            self.red_draw.rectangle(((tl, tr), (bl, br)), fill=0)
        elif fill == 'white':
            self.black_draw.rectangle(((tl, tr), (bl, br)), fill=1)
            self.red_draw.rectangle(((tl, tr), (bl, br)), fill=1)

    def text(self, left, top, text, font, fill):
        if fill == 'black':
            font = self.fonts[font]
            self.black_draw.text((left, top), text, font=font, fill=0)
            #return self.black_draw.textsize(text, font=font)
        elif fill == 'red':
            font = self.fonts[font]
            self.black_draw.text((left, top), text, font=font, fill=0)
            self.red_draw.text((left, top), text, font=font, fill=0)
            #return self.red_draw.textsize(text, font=font)
        elif fill == 'white':
            font = self.fonts[font]
            self.red_draw.text((left, top), text, font=font, fill=1)
            self.black_draw.text((left, top), text, font=font, fill=1)
            #return self.red_draw.textsize(text, font=font)

    def rotate(self, angle):
        self.red_image.rotate(angle)
        self.black_image.rotate(angle)

    def bitmap(self, x, y, image_path):
        bitmap = Image.open(self.getCWD()+"/icons/"+image_path)
        # self.image.paste((0, 0), (x, y), 'black', bitmap)
        # self.draw.bitmap((x, y), bitmap, fill=(0, 0, 0))
        self.black_draw.bitmap((x, y), bitmap, fill=0)

    def getFont(self, font_name):
        return self.fonts[font_name]

    def initFonts(self):
        roboto = self.getCWD()+"/fonts/roboto/Roboto-"
        self.fonts = {

            'robotoBlack14': ImageFont.truetype(roboto + "Black.ttf", 14),
            'robotoBlack18': ImageFont.truetype(roboto + "Black.ttf", 18),
            'robotoBold22': ImageFont.truetype(roboto + "Bold.ttf", 22),
            'robotoBlack22': ImageFont.truetype(roboto + "Black.ttf", 22),
            'robotoBlack24': ImageFont.truetype(roboto + "Black.ttf", 24),
            'robotoBlack54': ImageFont.truetype(roboto + "Black.ttf", 54),
        }

    def truncate(self, string, font, max_size):
        num_chars = len(string)
        for char in string:
            (a, b, np_x, np_y) = self.getFont(font).getbbox(string)
            if np_x >= max_size:
                string = string[:-1]

            if np_x <= max_size:
                return string

        return string

    def display(self, angle):
        self.black_image = self.black_image.rotate(angle)
        self.red_image = self.red_image.rotate(angle)

        new_image_found = False
        if os.path.exists(self.tmpImagePathRed):
            diff = ImageChops.difference(self.red_image, Image.open(self.tmpImagePathRed))
            if diff.getbbox():
                new_image_found = True
        else:
            new_image_found = True

        if os.path.exists(self.tmpImagePathBlack):
            diff = ImageChops.difference(self.black_image, Image.open(self.tmpImagePathBlack))
            if diff.getbbox():
                new_image_found = True
        else:
            new_image_found = True

        if new_image_found:
            logging.info("New information in the image detected. Updating the screen.")
            self.black_image.save(self.tmpImagePathBlack)
            self.red_image.save(self.tmpImagePathRed)
            self.epd.display(self.epd.getbuffer(self.black_image), self.epd.getbuffer(self.red_image))
            self.epd.sleep()

        else:
            logging.info("No new information found. Not updating the screen.")
