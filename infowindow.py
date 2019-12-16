#!/usr/bin/env python2

import sys
import os.path
import json
import logging
from mod_infowindow import infowindow

# Select pluggable module for todo list, calendar and weather.
# Replace the mod_<name> with one of:
# TODO: mod_todoist, mod_teamwork
# CALENDAR: mod_google, mod_ical
# WEATHER: mod_owm, mod_wunderground
from mod_utils import iw_utils
from mod_todo import mod_google as modTodo  # TODO
from mod_calendar import mod_google as modCalendar  # CALENDAR
from mod_weather import mod_owm as modWeather  # WEATHER

# TODO: Create dictionaries for API args. so that they can be custom.

# Configuration ###############################################################
config_path = os.path.join(iw_utils.getCWD(), "config.json")
with open(config_path) as config_file:
    config_data = json.load(config_file)

# Rotation. 0 for desktop, 180 for hanging upside down
rotation = config_data["general"]["rotation"]
charset = config_data["general"]["charset"]
todo_opts = config_data["todo"]
calendar_opts = config_data["calendar"]
weather_opts = config_data["weather"]
# give the timeformat to all the modules needing it
calendar_opts["timeformat"] = config_data["general"]["timeformat"]
weather_opts["timeformat"] = config_data["general"]["timeformat"]

# END CONFIGURATION ###########################################################
###############################################################################

# Setup Logging -  change to logging.DEBUG if you are having issues.
logging.basicConfig(level=logging.DEBUG)
logging.info("Configuration Complete")


# Custom exception handler. Need to handle exceptions and send them to the
# display since this will run headless most of the time. This gives the user
# enough info to know that they need to troubleshoot.
def HandleException(et, val, tb):
    iw = infowindow.InfoWindow()
    iw.text(0, 10, "EXCEPTION IN PROGRAM", 'robotoBlack18', 'black')
    iw.text(0, 30, val.encode(charset).strip(), 'robotoBlack18', 'black')
    iw.text(0, 60, "Please run program from command line interactivly to resolve", 'robotoBlack18', 'black')
    print("EXCEPTION IN PROGRAM ==================================")
    print("error message: %s" % val)
    print("type:          %s" % et)
    print("traceback:     %s" % tb)
    print("line:          %s" % tb.lineno)
    print("END EXCEPTION =========================================")
    iw.display(rotation)


sys.excepthook = HandleException


# Main Program ################################################################
def main():
    # Instantiate API modules
    todo = modTodo.ToDo(todo_opts)
    cal = modCalendar.Cal(calendar_opts)
    weather = modWeather.Weather(weather_opts)

    # Setup e-ink initial drawings
    iw = infowindow.InfoWindow()

    # Weather Grid
    temp_rect_width = 102
    temp_rect_left = (iw.width / 2) - (temp_rect_width / 2)
    temp_rect_right = (iw.width / 2) + (temp_rect_width / 2)

    iw.line(268, 0, 268, 64, 'black')  # First Vertical Line
    iw.rectangle(temp_rect_left, 0, temp_rect_right, 64, 'red')
    iw.line(372, 0, 372, 64, 'black')  # Second Vertical Line

    iw.bitmap(375, 0, "windSmall.bmp")  # Wind Icon
    iw.line(461, 0, 461, 64, 'black')  # Third Vertical Line

    iw.bitmap(464, 0, "rainSmall.bmp")  # Rain Icon
    iw.line(550, 0, 550, 64, 'black')  # Fourth Vertical Line

    iw.bitmap(554, 0, "snowSmall.bmp")  # Snow Icon

    # Center cal/todo divider line
    iw.line(314, 90, 314, 384, 'black')  # Left Black line
    iw.rectangle(315, 64, 325, 384, 'red')  # Red Rectangle
    iw.line(326, 90, 326, 384, 'black')  # Right Black line

    # Calendar / Todo Title Line
    iw.line(0, 64, 640, 64, 'black')  # Top Line
    iw.rectangle(0, 65, 640, 90, 'red')  # Red Rectangle
    iw.line(0, 91, 640, 91, 'black')  # Bottom Black Line

    # Todo / Weather Titles
    iw.text(440, 64, "TODO", 'robotoBlack24', 'white')
    iw.text(95, 64, "CALENDAR", 'robotoBlack24', 'white')

    # DISPLAY TODO INFO
    # =========================================================================
    todo_items = todo.list()
    logging.debug("Todo Items")
    logging.debug("-----------------------------------------------------------------------")
    t_y = 94
    for todo_item in todo_items:
        iw.text(333, t_y, todo_item['content'].encode(charset).strip(), 'robotoRegular18', 'black')
        t_y = (t_y + 34)
        iw.line(325, (t_y - 2), 640, (t_y - 2), 'black')
        logging.debug("ITEM: %s" % todo_item['content'].encode(charset).strip())

    # DISPLAY CALENDAR INFO
    # =========================================================================
    cal_items = cal.list()
    logging.debug("Calendar Items")
    logging.debug("-----------------------------------------------------------------------")
    c_y = 94

    # Time and date divider line
    (dt_x, dt_y) = iw.getFont('robotoRegular14').getsize('12-99-2000')

    for cal_item in cal_items:
        (x, y) = iw.text(3, c_y, cal_item['date'].encode(charset).strip(), 'robotoRegular14', 'black')
        iw.line((dt_x + 5), c_y, (dt_x + 5), (c_y + 32), 'black')
        iw.text(3, (c_y + 15), cal_item['time'].encode(charset).strip(), 'robotoRegular14', 'black')
        iw.text((dt_x + 7), (c_y + 5), iw.truncate(cal_item['content'].encode(charset).strip(), 'robotoRegular18'),
                'robotoRegular18', 'black')
        c_y = (c_y + 32)
        iw.line(0, (c_y - 2), 313, (c_y - 2), 'black')
        # logging.debug("ITEM: "+str(cal_item['date']), str(cal_item['time']), str(cal_item['content']))
        logging.debug("ITEM: %s" % cal_item['content'].encode(charset).strip())

    # DISPLAY WEATHER INFO
    # =========================================================================
    weather = weather.list()
    logging.debug("Weather Info")
    logging.debug("-----------------------------------------------------------------------")
    # Set unit descriptors
    if weather_opts['units'] == 'imperial':
        u_speed = u"mph"
        u_temp = u"F"
    elif weather_opts['units'] == 'metric':
        u_speed = u"m/sec"
        u_temp = u"C"
    else:
        u_speed = u"m/sec"
        u_temp = u"K"

    deg_symbol = u"\u00b0"
    iw.bitmap(2, 2, weather['icon'])
    iw.text(70, 2, weather['description'].title().encode(charset).strip(), 'robotoBlack24', 'black')
    iw.text(70, 35, weather['sunrise'], 'robotoRegular18', 'black')
    iw.text(154, 35, weather['sunset'], 'robotoRegular18', 'black')

    # Temp ( adjust for str length )
    (t_x, t_y) = iw.getFont('robotoBlack48').getsize(str(weather['temp_cur']) + deg_symbol)
    temp_left = (iw.width / 2) - (t_x / 2)
    iw.text(temp_left, 2, str(weather['temp_cur']) + deg_symbol, 'robotoBlack48', 'white')
    t_desc_posx = (temp_left + t_x) - 15
    iw.text(t_desc_posx, 25, u_temp, 'robotoBlack18', 'white')

    # Wind 
    iw.text(405, 5, weather['wind']['dir'], 'robotoBlack18', 'black')
    iw.text(380, 35, str(weather['wind']['speed']) + u_speed, 'robotoRegular18', 'black')

    # Rain
    iw.text(481, 29, "1hr: " + str(weather['rain']['1h']), 'robotoRegular18', 'black')
    iw.text(481, 44, "3hr: " + str(weather['rain']['3h']), 'robotoRegular18', 'black')

    # Snow
    iw.text(573, 29, "1hr: " + str(weather['snow']['1h']), 'robotoRegular18', 'black')
    iw.text(573, 44, "3hr: " + str(weather['snow']['3h']), 'robotoRegular18', 'black')

    # Write to screen
    # =========================================================================
    iw.display(rotation)


if __name__ == '__main__':
    main()
