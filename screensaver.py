#!/usr/bin/env python2

import logging
import os
from driver import epd7in5b

# Setup Logging -  change to logging.DEBUG if you are having issues.
logging.basicConfig(level=logging.DEBUG)
logging.info("Screensager starting")


def main():
    epd = epd7in5b.EPD()
    epd.init()
    logging.info("Display red")
    epd.display_frame(epd.get_frame_buffer(os.path.join("resources", "red.png")))
    logging.info("Display black")
    epd.display_frame(epd.get_frame_buffer(os.path.join("resources", "black.png")))
    logging.info("Display white")
    epd.display_frame(epd.get_frame_buffer(os.path.join("resources", "white.png")))
    logging.info("Screensaver finished")


if __name__ == '__main__':
    main()
