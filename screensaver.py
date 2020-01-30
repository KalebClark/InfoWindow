#!/usr/bin/env python2

import logging
import os
from driver import epd7in5b
from PIL import Image

# Setup Logging -  change to logging.DEBUG if you are having issues.
logging.basicConfig(level=logging.INFO)
logging.info("Screen saver starting")


def main():
    epd = epd7in5b.EPD()
    epd.init()

    images = ["red.png", "black.png", "white.png"]
    for image in images:
        logging.info("Display %s" % image)
        image_data = Image.open(os.path.join("resources", image))
        epd.display_frame(epd.get_frame_buffer(image_data))

    logging.info("Screen saver finished")


if __name__ == '__main__':
    main()
