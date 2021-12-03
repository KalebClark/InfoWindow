#!/usr/bin/env python3

import sys
import os.path
import json
import logging
import string
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
todo_opts = config_data["todo"]
calendar_opts = config_data["calendar"]
weather_opts = config_data["weather"]
infowindow_opts = {}
# give the timeformat to all the modules needing it
calendar_opts["timeformat"] = config_data["general"]["timeformat"]
weather_opts["timeformat"] = config_data["general"]["timeformat"]
infowindow_opts["timeformat"] = config_data["general"]["timeformat"]
infowindow_opts["cell_spacing"] = config_data["general"]["cell_spacing"]

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
    iw.text(0, 30, val.strip(), 'robotoBlack18', 'black')
    iw.text(0, 60, "Please run program from command line interactivly to resolve", 'robotoBlack18', 'black')
    print("EXCEPTION IN PROGRAM ==================================")
    print(("error message: %s" % val))
    print(("type:          %s" % et))
    print(("traceback:     %s" % tb))
    print(("line:          %s" % tb.lineno))
    print("END EXCEPTION =========================================")
    iw.display(rotation)


sys.excepthook = HandleException


# helper to calculate max char width and height
def get_max_char_size(iw, chars, font):
    max_x = 0
    max_y = 0
    for char in chars:
        (x, y) = iw.getFont(font).getsize(char)
        if x > max_x:
            max_x = x
        if y > max_y:
            max_y = y
    return max_x, max_y


# Main Program ################################################################
def main():
    # Instantiate API modules
    todo = modTodo.ToDo(todo_opts)
    cal = modCalendar.Cal(calendar_opts)
    weather = modWeather.Weather(weather_opts)

    # Setup e-ink initial drawings
    iw = infowindow.InfoWindow(infowindow_opts)

    # Set some things
    calendar_date_font = "robotoRegular14"
    calendar_entry_font = "robotoRegular18"
    tasks_font = "robotoRegular18"

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

    #(t_x, t_y) = iw.getFont(tasks_font).getsize('JgGj')
    (t_x, t_y) = get_max_char_size(iw, string.printable, tasks_font)
    line_height = t_y + (2 * infowindow_opts["cell_spacing"])

    current_task_y = 92
    for todo_item in todo_items:
        color = 'black'
        if 'today' in list(todo_item.keys()):
            if todo_item['today']:
                color = 'red'

        iw.text(333, (current_task_y + infowindow_opts["cell_spacing"]), todo_item['content'].strip(),
                tasks_font, color)
        iw.line(327, (current_task_y + line_height + 1), 640, (current_task_y + line_height + 1), 'black')

        # set next loop height
        current_task_y = (current_task_y + line_height + 2)
        logging.debug("ITEM: %s" % todo_item['content'].strip())

    # DISPLAY CALENDAR INFO
    # =========================================================================
    cal_items = cal.list()
    logging.debug("Calendar Items")
    logging.debug("-----------------------------------------------------------------------")

    if calendar_opts['timeformat'] == "12h":
        (t_x, t_y) = get_max_char_size(iw, string.digits, calendar_date_font)
        (dt_x, dt_y) = iw.getFont(calendar_date_font).getsize(': pm')
        dt_x = dt_x + (4 * t_x)
        if t_y > dt_y:
            dt_y = t_y

    else:
        (t_x, t_y) = get_max_char_size(iw, string.digits, calendar_date_font)
        (dt_x, dt_y) = iw.getFont(calendar_date_font).getsize('.')
        dt_x = dt_x + (4 * t_x)

    (it_x, it_y) = get_max_char_size(iw, string.printable, calendar_entry_font)

    line_height = (2 * dt_y) + (2 * infowindow_opts["cell_spacing"])

    current_calendar_y = 92
    for cal_item in cal_items:
        font_color = 'black'
        if cal_item['today']:
            font_color = calendar_opts['today_text_color']
            iw.rectangle(0, current_calendar_y,
                         313, (current_calendar_y + line_height),
                         calendar_opts['today_background_color'])

        # draw horizontal line
        iw.line(0, (current_calendar_y + line_height + 1),
                313, (current_calendar_y + line_height + 1),
                'black')
        # draw vertical line
        iw.line((dt_x + (2 * infowindow_opts["cell_spacing"]) + 1), current_calendar_y,
                (dt_x + (2 * infowindow_opts["cell_spacing"]) + 1), (current_calendar_y + line_height),
                'black')

        # draw event date
        iw.text((infowindow_opts["cell_spacing"]),
                (current_calendar_y + infowindow_opts["cell_spacing"]),
                cal_item['date'].strip(), calendar_date_font, font_color)
        # draw event time
        iw.text((infowindow_opts["cell_spacing"]),
                (current_calendar_y + ((line_height - 2 * infowindow_opts["cell_spacing"]) / 2)),
                cal_item['time'].strip(), calendar_date_font, font_color)
        # draw event text
        calendar_event_text_start = dt_x + (3 * infowindow_opts["cell_spacing"]) + 1
        max_event_text_length = 313 - calendar_event_text_start - infowindow_opts["cell_spacing"]
        iw.text(calendar_event_text_start,
                (current_calendar_y + ((line_height - it_y) / 2)),
                iw.truncate(cal_item['content'].strip(), calendar_entry_font, max_event_text_length),
                calendar_entry_font, font_color)

        # set new line height for next round
        current_calendar_y = (current_calendar_y + line_height + 2)
        # logging.debug("ITEM: "+str(cal_item['date']), str(cal_item['time']), str(cal_item['content']))
        logging.debug("ITEM: %s" % cal_item['content'].strip())

    # DISPLAY WEATHER INFO
    # =========================================================================
    weather = weather.list()
    logging.debug("Weather Info")
    logging.debug("-----------------------------------------------------------------------")
    # Set unit descriptors
    if weather_opts['units'] == 'imperial':
        u_speed = "mph"
        u_temp = "F"
    elif weather_opts['units'] == 'metric':
        u_speed = "m/sec"
        u_temp = "C"
    else:
        u_speed = "m/sec"
        u_temp = "K"

    deg_symbol = "°"
    iw.bitmap(2, 2, weather['icon'])
    iw.text(70, 2, weather['description'].title().strip(), 'robotoBlack24', 'black')
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
