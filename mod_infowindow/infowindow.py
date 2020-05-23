from driver import epd7in5b
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from PIL import ImageChops
import os, sys
import logging
import tempfile


class InfoWindow:
    def __init__(self, options):
        self.epd = epd7in5b.EPD()
        self.epd.init()
        self.width = 640
        self.height = 384
        self.image = Image.new('L', (640, 384), 255)
        self.draw = ImageDraw.Draw(self.image)
        self.fonts = {}
        self.initFonts()
        self.tmpImagePath = os.path.join(tempfile.gettempdir(), "InfoWindow.png")
        self.timeformat = options['timeformat']
        if self.timeformat == "12h":
            self.calendar_text_length = 253
        else:
            self.calendar_text_length = 270

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
        self.draw.bitmap((x, y), bitmap)

    def getFont(self, font_name):
        return self.fonts[font_name]

    def initFonts(self):
        roboto = self.getCWD()+"/fonts/roboto/Roboto-"
        self.fonts = {

            'robotoBlack24': ImageFont.truetype(roboto+"Black.ttf", 24),
            'robotoBlack18': ImageFont.truetype(roboto+"Black.ttf", 18),
            'robotoRegular18': ImageFont.truetype(roboto+"Regular.ttf", 18),
            'robotoRegular14': ImageFont.truetype(roboto+"Regular.ttf", 14),
            'robotoBlack48': ImageFont.truetype(roboto+"Black.ttf", 48)
        }

    def truncate(self, string, font):
        num_chars = len(string)
        for char in string:
            (np_x, np_y) = self.getFont(font).getsize(string)
            if np_x >= self.calendar_text_length:
                string = string[:-1]

            if np_x <= self.calendar_text_length:
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
            self.epd.display_frame(self.epd.get_frame_buffer(self.image))
            self.epd.sleep()
        else:
            logging.info("No new information found. Not updating the screen.")
