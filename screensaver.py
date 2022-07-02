#!/usr/bin/env python3

import logging
import os
from PIL import Image

from driver import epd7in5b_V2

# Setup Logging -  change to logging.DEBUG if you are having issues.
logging.basicConfig(level=logging.INFO)
logging.info("Screen saver starting")

def display_image(epd, image_data):
    rgb_image = image_data.convert('RGB')
    width, height = image_data.size
    no_red = Image.new('RGB', (width, height), (255, 255, 255))
    only_red = Image.new('RGB', (width, height), (255, 255, 255))

    for col in range(width):
        for row in range(height):

            r, g, b = rgb_image.getpixel((col, row))
            no_red.putpixel((col, row), (0, g, b))

            if r == 255 and g == 0 and b == 0:
                only_red.putpixel((col, row), (0, 0 ,0))
            else:
                only_red.putpixel((col, row), (255, 255, 255))

    epd.display(epd.getbuffer(no_red), epd.getbuffer(only_red))


def main():
    epd = epd7in5b_V2.EPD()
    epd.init()

    width = 800
    height = 480

    logging.info("Display black screen")
    display_image(epd, Image.new('RGB', (width, height), (0, 0, 0)))

    logging.info("Display red screen")
    display_image(epd, Image.new('RGB', (width, height), (255, 0, 0)))

    epd.Clear()
    epd.sleep()
    logging.info("Screen saver finished")


if __name__ == '__main__':
    main()
