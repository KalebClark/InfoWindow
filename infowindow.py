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
calendar_opts["sunday_first_dow"] = config_data["general"]["sunday_first_dow"]
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
    max_width = 0
    max_height = 0
    for char in chars:
        left, top, right, bottom = iw.getFont(font).getbbox(char)
        width, height = right - left, bottom - top
        if width > max_width:
            max_width = width
        if height > max_height:
            max_height = height
    return max_width, max_height


def render_centered_text(iw, text, font, color, center_position, y_position):
    length = iw.getFont(font).getlength(text)
    x_position = int(center_position - (length / 2))
    iw.text(x_position, y_position, text, font, color)


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

    # DISPLAY TO DO INFO
    # =========================================================================
    todo_items = todo.list()
    logging.debug("Todo Items")
    logging.debug("-----------------------------------------------------------------------")

    (text_width, text_height) = get_max_char_size(iw, string.printable, tasks_font)
    line_height = text_height + (2 * infowindow_opts["cell_spacing"])

    current_task_y = 92
    for todo_item in todo_items:
        color = 'black'
        current_font = tasks_font
        if 'today' in list(todo_item.keys()):
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

    (text_width, text_height) = get_max_char_size(iw, string.digits, calendar_date_font)
    if calendar_opts['timeformat'] == "12h":
        left, top, right, bottom = iw.getFont(calendar_date_font).getbbox(': pm')
    else:
        left, top, right, bottom = iw.getFont(calendar_date_font).getbbox('.')
    date_time_width, date_time_height = right - left, bottom - top
    date_time_width = date_time_width + (4 * text_width)
    if text_height > date_time_height:
        date_time_height = text_height

    (chars_max_width, chars_max_height) = get_max_char_size(iw, string.printable, calendar_entry_font)
    line_height = (2 * date_time_height) + (2 * infowindow_opts["cell_spacing"])

    def render_calendar(x_min, x_max, loop_start=0):
        current_index = 0
        current_calendar_y = 92
        current_days_away = -1
        current_weeks_away = -1
        current_week = -1
        loop_date_time_width = x_min + date_time_width
        first_loop = True
        new_week = False

        current_font = calendar_entry_font
        for cal_item in cal_items[loop_start:]:
            font_color = 'black'
            new_week = False

            if cal_item['today']:
                current_font = calendar_entry_font_highlited
                font_color = calendar_opts['today_text_color']
                iw.rectangle(x_min, current_calendar_y,
                             x_max, (current_calendar_y + line_height),
                             calendar_opts['today_background_color'])

            # draw horizontal line(s) at the top
            # on first run, initialize several vars with the first values from the first event
            if current_days_away < 0:
                current_days_away = cal_item['days_away']
            if current_weeks_away < 0:
                current_weeks_away = cal_item['weeks_away']
            if current_week < 0:
                current_week = cal_item['week']

            if first_loop:
                # don't draw a line at the top of the first event
                first_loop = False
                divider_str = "initial element"
            else:
                # per default, draw a dashed line (same day event)
                divider_str = "same day"
                for x in range(x_min, x_max, 8):
                    iw.line(x, current_calendar_y, x+3, current_calendar_y, 'black')
                    iw.line(x+4, current_calendar_y, x+7, current_calendar_y, 'white')

            # override the dotted line with a black line since the "days away" number changed
            if current_days_away != cal_item['days_away']:
                current_days_away = cal_item['days_away']
                divider_str = "new day"
                iw.line(x_min, current_calendar_y, x_max, current_calendar_y, 'black')

            # override the dotted line with a black rectangle ("thicker line") since the week changed number changed
            if current_week != cal_item['week']:
                current_week = cal_item['week']
                divider_str = "new week day"
                new_week = True
                iw.rectangle(x_min, (current_calendar_y - 1), x_max, current_calendar_y, 'black')

            # check if the new event is a week away  (the "weeks away" number changed)
            if current_weeks_away != cal_item['weeks_away']:
                # override the black line with a red a rectangle ("thicker line") the "weeks away" number changed
                current_weeks_away = cal_item['weeks_away']

                # decide on style depending on what the option above was
                if new_week:
                    divider_str = "in one week and the week changes"
                    for x in range(x_min, x_max, 32):
                        iw.rectangle(x, (current_calendar_y - 1), x + 15, current_calendar_y, 'black')
                        iw.rectangle(x + 16, (current_calendar_y - 1), x + 31, current_calendar_y, 'red')
                else:
                    divider_str = "in one week"
                    # iw.rectangle(x_min, (current_calendar_y - 1), x_max, current_calendar_y, 'red')
                    iw.line(x_min, current_calendar_y, x_max, current_calendar_y, 'red')

            # draw ending horizontal line, just to ensure that the last element is not hanging in the air
            # this gets overridden almost all the time
            iw.line(x_min, (current_calendar_y + line_height + 2), x_max, (current_calendar_y + line_height + 2),
                    'black')

            # draw vertical line
            iw.line((loop_date_time_width + (2 * infowindow_opts["cell_spacing"]) + 1), current_calendar_y,
                    (loop_date_time_width + (2 * infowindow_opts["cell_spacing"]) + 1),
                    (current_calendar_y + line_height), 'black')

            # draw event date
            iw.text((infowindow_opts["cell_spacing"]) + x_min,
                    current_calendar_y,
                    cal_item['date'].strip(), calendar_date_font, font_color)
            # draw event time
            iw.text((infowindow_opts["cell_spacing"]) + x_min,
                    current_calendar_y + 1 + date_time_height,
                    cal_item['time'].strip(), calendar_date_font, font_color)
            # draw event text
            calendar_event_text_start = loop_date_time_width + (3 * infowindow_opts["cell_spacing"]) + 1
            max_event_text_length = x_max - calendar_event_text_start - infowindow_opts["cell_spacing"]
            iw.text(calendar_event_text_start,
                    (current_calendar_y + ((line_height - chars_max_height) / 2)),
                    iw.truncate(cal_item['content'].strip(), current_font, max_event_text_length),
                    current_font, font_color)

            # set new line height for next round
            current_calendar_y = (current_calendar_y + line_height + 2)
            # logging.debug("ITEM: "+str(cal_item['date']), str(cal_item['time']), str(cal_item['content']))
            logging.debug("ITEM (%s): %s" % (divider_str, cal_item['content'].strip()))
            current_index = cal_items.index(cal_item)
            if current_calendar_y > 480:
                logging.debug("Max height detected, breaking loop")
                break

        return current_index

    last_item = render_calendar(0, 391)
    if current_task_y == 92:  # there are no tasks
        render_calendar(408, 800, last_item + 1)
        left_column_title = "CALENDAR 1/2"
        right_column_title = "CALENDAR 2/2"
    else:
        left_column_title = "CALENDAR"
        right_column_title = "TODO"
    render_centered_text(iw, left_column_title, 'robotoBlack24', 'white', 200, 64)
    render_centered_text(iw, right_column_title, 'robotoBlack24', 'white', 600, 64)

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
    left, top, right, bottom = iw.getFont(temperature_font).getbbox(temp_string)
    text_width, text_height = right - left, bottom - top
    temp_left = (iw.width / 2) - (text_width / 2)
    iw.text(temp_left, 2, temp_string, temperature_font, 'white')
    t_desc_posx = (temp_left + text_width) - 18
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
