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
    weather_font = "robotoBlack18"
    temperature_font = "robotoBlack54"
    calendar_date_font = "robotoBlack14"
    calendar_entry_font = "robotoBlack22"
    calendar_entry_font_highlited = "robotoBlack22"
    tasks_font = "robotoBlack22"
    tasks_font_highlited = "robotoBlack22"

    # Weather Grid
    temp_rect_width = 128
    temp_rect_left = (iw.width / 2) - (temp_rect_width / 2)
    temp_rect_right = (iw.width / 2) + (temp_rect_width / 2)

    iw.line(335, 0, 335, 64, 'black')  # First Vertical Line
    iw.rectangle(temp_rect_left, 0, temp_rect_right, 64, 'red')
    iw.line(465, 0, 465, 64, 'black')  # Second Vertical Line

    # Center cal
    iw.line(392, 90, 392, 480, 'black')  # Left Black line
    iw.rectangle(393, 64, 406, 480, 'red')  # Red Rectangle
    iw.line(407, 90, 407, 480, 'black')  # Right Black line

    # Calendar
    iw.line(0, 64, 800, 64, 'black')  # Top Line
    iw.rectangle(0, 65, 800, 90, 'red')  # Red Rectangle
    iw.line(0, 91, 800, 91, 'black')  # Bottom Black Line

    # Weather Titles
    iw.text(550, 64, "TODO", 'robotoBlack24', 'white')
    iw.text(118, 64, "CALENDAR", 'robotoBlack24', 'white')

    # DISPLAY TO DO INFO
    # =========================================================================
    todo_items = todo.list()
    logging.debug("Todo Items")
    logging.debug("-----------------------------------------------------------------------")

    (t_x, t_y) = get_max_char_size(iw, string.printable, tasks_font)
    line_height = t_y + (2 * infowindow_opts["cell_spacing"])

    current_task_y = 92
    for todo_item in todo_items:
        color = 'black'
        if 'today' in list(todo_item.keys()):
            current_font = tasks_font
            if todo_item['today']:
                color = 'red'
                current_font = tasks_font_highlited

        iw.text(416, (current_task_y + infowindow_opts["cell_spacing"]), todo_item['content'].strip(),
                current_font, color)
        iw.line(408, (current_task_y + line_height + 1), 800, (current_task_y + line_height + 1), 'black')

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
        current_font = calendar_entry_font
        font_color = 'black'
        if cal_item['today']:
            current_font = calendar_entry_font_highlited
            font_color = calendar_opts['today_text_color']
            iw.rectangle(0, current_calendar_y,
                         391, (current_calendar_y + line_height),
                         calendar_opts['today_background_color'])

        # draw horizontal line
        iw.line(0, (current_calendar_y + line_height + 1),
                391, (current_calendar_y + line_height + 1),
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
        max_event_text_length = 391 - calendar_event_text_start - infowindow_opts["cell_spacing"]
        iw.text(calendar_event_text_start,
                (current_calendar_y + ((line_height - it_y) / 2)),
                iw.truncate(cal_item['content'].strip(), current_font, max_event_text_length),
                current_font, font_color)

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

    # Weather left box
    deg_symbol = "°"
    iw.bitmap(2, 2, weather['icon'])
    iw.text(90, 2, weather['description'].title().strip(), 'robotoBlack24', 'black')
    iw.text(90, 35, weather['sunrise'], weather_font, 'black')
    iw.text(192, 35, weather['sunset'], weather_font, 'black')

    # Temp ( adjust for str length )
    temp_string = str(weather['temp_cur']) + deg_symbol
    (t_x, t_y) = iw.getFont(temperature_font).getsize(temp_string)
    temp_left = (iw.width / 2) - (t_x / 2)
    iw.text(temp_left, 2, temp_string, temperature_font, 'white')
    t_desc_posx = (temp_left + t_x) - 18
    iw.text(t_desc_posx, 28, u_temp, 'robotoBlack24', 'white')

    # Wind
    iw.bitmap(480, 0, "windSmall.bmp")  # Wind Icon
    iw.text(520, 5, weather['wind']['dir'], weather_font, 'black')
    iw.text(480, 35, str(weather['wind']['speed']) + u_speed, weather_font, 'black')
    iw.line(576, 0, 576, 64, 'black')  # Third Vertical Line

    # Rain
    iw.bitmap(616, 0, "rainSmall.bmp")  # Rain Icon
    iw.text(601, 29, "1hr: " + str(weather['rain']['1h']), weather_font, 'black')
    iw.text(601, 44, "3hr: " + str(weather['rain']['3h']), weather_font, 'black')
    iw.line(687, 0, 687, 64, 'black')  # Fourth Vertical Line

    # Snow
    iw.bitmap(728, 0, "snowSmall.bmp")  # Snow Icon
    iw.text(716, 29, "1hr: " + str(weather['snow']['1h']), weather_font, 'black')
    iw.text(716, 44, "3hr: " + str(weather['snow']['3h']), weather_font, 'black')

    # Write to screen
    # =========================================================================
    iw.display(rotation)


if __name__ == '__main__':
    main()
