![alt text](infowindow.jpg)


# Infowindow
Rapsberry pi powered e-ink display for displaying information in an always on state. There are several other iterations
of this project online, but they didnt do quite what I wanted them to. This is my version. Also keeping up my python
skills as they dont get used as much as they used to!

The functionality is not meant to be an "end all solution for calendaring and Todo lists" The intent is to provide an
*always  on* display to show me what is coming up next. I can then check in browser, phone, etc for details and updates
to the data. In your face reminder.
<div align="center">
  <a href="#features">Features</a> |
  <a href="#installation">Installation</a> | 
  <a href="#configuration">Configuration</a> | 
  <a href="#running">Running</a> | 
</div>

## Features
* **Calendar**
  * Google Calendar is the only calendar currently supported
* **Todo List**
  * Todoist
  * Teamwork.com
* **Weather**
  * Open Weather Map current data only. Future plan for forecast data.

## Installation
### Raspberry Pi setup
Activate SPI on your Raspberry Pi by using the `raspi-config` tool under Interface Options and reboot.

### Get software
Clone this repo onto your raspberry pi. Does not really matter where it is, but good option is in the `pi` users home
directory: `/home/pi/InfoWindow`

### Setup python modules
Run `pip install -r requirements.txt`. This should install all required modules. I stuck to basic standard modules for
ease of installation.

## Configuration
You will need to configure a few things such as API Keys and location. Copy config.json-sample to config.json. Edit
config.json to add your api keys and other information.

## Optional: Increase lifetime of your SD-Card
If you want to increase the lifetime of the SD-Card, add the following line to `/etc/fstab` and reboot: 

`tmpfs    /tmp    tmpfs    defaults,noatime,nosuid,size=100m    0 0`

With this line, the `/tmp` folder will be held in RAM and will not be written to the SD-Card.


### General
* rotation: 0 - This is the rotation of the display in degrees. Leave at zero if you use it as a desktop display. Change
to 180 if you have it mounted and hanging from a shelf.
* timeformat: 12h / 24h
* charset: utf-8 (or something else). I.e. to get äöü working, use latin1

### Todo (Module)
Todoist is the current active module in this code. It only requires `api_key`. Teamwork also requires a 'site' key. If
using google tasks, leave this as null `todo: null`
* api_key: Enter your todoist API key.

### Weather (Module)
Open Weather Map is where the data is coming from in the default module. This requires a few keys.
* api_key: Get your api key from OWM website.
* city: Look at OWM docs to figure what your city name is. Mine is "Sacramento,US"
* units: This can either be `imperial` or `metric`

### Google calendar and ToDo list (Modules)
To use the google APIs, you first have to login to the [google cloud console](https://console.cloud.google.com/apis/).
In the google cloud console, do the following things:
1) Create a project and give it a name, i.e. `infowindow` and switch to the context of this project if not already
   active.
2) Create a [new oauth consent screen](https://console.cloud.google.com/apis/credentials/consent) (just enter a name
   should be enough).
3) Create a [new oauth 2.0 client id](https://console.cloud.google.com/apis/credentials). Choosing type `other` should
   work just fine. Finally, download the json file provided by the google cloud console and store it in the repo
   directory (i.e. `/home/pi/InfoWindow/google_secret.json`) on the Raspberry Pi.  

#### Calendar
There are are additional sections in the config for this module:
* additional: A list of additional calendar names (summary) to fetch. To use i.e. birthdays, add "Contacts" (also if
              you use google in german.
* ignored: A list of events to be removed from the calendar display.
        
## Running
### First Run
You should run the script manually the first time so that Googles auth modules can run interactivly. Once that has
completed you will want to add this to CRON so it runs every few minutes automatically.

### Cron Run (Normal use)
* Run `crontab -e`
* insert `*/6 * * * * /usr/bin/python /home/pi/InfoWindow/infowindow.py --cron` 

