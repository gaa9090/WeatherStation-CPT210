# *****************************************************************************
# ***************************  Python Source Code  ****************************
# *****************************************************************************
#
#   DESIGNER NAME:  Gwen Antonio, Matt Bonfiglio, Mark Luskiewicz
#
#       FILE NAME:  210_final.py 
#
# DESCRIPTION
#   Weather‑station application for Raspberry Pi. A Bottle web server exposes
#   routes that return live readings (temperature, pressure, altitude, wind
#   speed, wind direction). A small password‑protected Tkinter GUI lets an
#   operator start the server and open the web interface locally. Hardware is
#   accessed via GPIO, ADS7830 ADC, and BMP085 sensors.
# *****************************************************************************
import sys
import tkinter as tk
from tkinter import *
import webbrowser
from bottle import route, run, template
from datetime import datetime
import RPi.GPIO as GPIO
import Freenove_DHT as DHT
import math
import time
import os
from ADCDevice import *
import Adafruit_BMP.BMP085 as BMP085
from weather_station import wind_direction
import threading

# Define global constants
ANEMOMETER_PIN     = 23
MPH_PER_SECOND     = 1.492
NINE_FIFTHS        = 1.8
RADIUS_F           = 3.5
WIND_INTERVAL      = 5
WIND_COUNT         = 17
CIRCUMFERENCE      = (2 * math.pi) * (RADIUS_F / 5280)
DIAMETER_IN_FEET   = 0.59
ROTATIONS_TO_MPH   = 1.49184
SECONDS_CALCULATED = 3
FEET_IN_MILE       = 5280
CONVERSION_FACTOR  = 3600
ADC_TO_VOLTAGE     = 255 * 3.3
PASCAL_CONVERSION  = 3386
URL = "https://0.0.0.0:8080/"
TKINTER_BG_COLOR   = "#26242f"
PASSWORD           = '123'

# Define global variables
bmp_handle         = BMP085
isFahrenheit       = True

# Create the ADCDevice object
adc = ADCDevice()
adc = ADS7830()

# -----------------------------------------------------------------------------
# DESCRIPTION
#   Serve the landing page with navigation buttons for every sensor read-out.
#
# INPUT PARAMETERS:
#   none
#
# OUTPUT PARAMETERS:
#   none
#
# RETURN:
#   str – HTML for the landing page
# -----------------------------------------------------------------------------
@route('/')
def get_time():
    html_string = '''
        <h1>
            <b>Welcome to the Weather Channel!</b>
        </h1>
        <form>
            <input type="button" value="Display Pressure" onclick="window.location.href='/display_pressure'" />
            <input type="button" value="Display Temperature" onclick="window.location.href='/display_temp'" />
            <input type="button" value="Display Wind Speed" onclick="window.location.href='/display_speed'" />
            <input type="button" value="Display Wind Direction" onclick="window.location.href='/display_direction'" />
            <input type="button" value="Display Altitude" onclick="window.location.href='/display_altitude'" />
        </form>
    '''
    return html_string

# -----------------------------------------------------------------------------
# DESCRIPTION
#   Read ambient temperature and humidity from the BMP085 sensor and report it in °F.
#
# INPUT PARAMETERS:
#   none
#
# OUTPUT PARAMETERS:
#   none
#
# RETURN:
#   str – Temperature string plus HTML “Back” button
# -----------------------------------------------------------------------------
@route('/display_temp')
def get_humidity_temp():
    html_string = '''
        <form>
            <input type="button" value="Back to Main Menu" onclick="window.location.href='/'" />
        </form>
    '''
    sensor = BMP085.BMP085()
    return "Temperature = {0:0.2f} °F".format(sensor.read_temperature()) + f"\n{html_string}"

# -----------------------------------------------------------------------------
# DESCRIPTION
#   Calculate wind speed by counting anemometer rotations during a fixed window
#   and converting the count to miles per hour (MPH).
#
# INPUT PARAMETERS:
#   none
#
# OUTPUT PARAMETERS:
#   none
#
# RETURN:
#   str – Wind‑speed string plus HTML “Back” button
# -----------------------------------------------------------------------------
@route('/display_speed')
def get_wind_speed():
    html_string = '''
        <form>
            <input type="button" value="Back to Main Menu" onclick="window.location.href='/'" />
        </form>
    '''
    rotation_count = 0
    end_time = time.time() + SECONDS_CALCULATED
    while time.time() < end_time:
        if GPIO.input(ANEMOMETER_PIN) == GPIO.HIGH:
            rotation_count += 1
            print(f"Rotation detected; total: {rotation_count}")
            while (GPIO.input(ANEMOMETER_PIN) == GPIO.HIGH) and (time.time() < end_time):
                pass
    print(rotation_count)
    mph = (rotation_count / 3) * (18 * math.pi) * 3600 * 6.21371E-6
    
    return f"Wind Speed: {mph:.2f} MPH\n{html_string}"
    

# -----------------------------------------------------------------------------
# DESCRIPTION
#   Convert the ADC reading from the wind vane to the nearest cardinal
#   direction.
#
# INPUT PARAMETERS:
#   none
#
# OUTPUT PARAMETERS:
#   none
#
# RETURN:
#   str – Wind direction plus HTML “Back” button
# -----------------------------------------------------------------------------
@route('/display_direction')
def get_wind_direction():
    html_string = '''
        <form>
            <input type="button" value="Back to Main Menu" onclick="window.location.href='/'" />
        </form>
    '''
    value = adc.analogRead(0)
    voltage = value / ADC_TO_VOLTAGE
    voltage *= 1000 # Make the value easier to use by placing it in the 100s place
    voltage = math.floor(voltage)
    if voltage == 241:
        direction = "North"
    elif voltage == 207:
        direction = "Northwest"
    elif voltage == 150:
        direction = "West"
    elif voltage == 269:
        direction = "Southwest"
    elif voltage == 298:
        direction = "Southeast"   
    elif 299 <= voltage <= 300:
        direction = "East"
    elif voltage == 285:
        direction = "Northeast"
    elif voltage == 293:
        direction = "South"
    else:
        direction = "Not Detected"
    return f"{direction}\n{html_string}"

# -----------------------------------------------------------------------------
# DESCRIPTION
#   Read barometric and sea‑level pressure, convert to inches of mercury, and
#   display both values.
#
# INPUT PARAMETERS:
#   none
#
# OUTPUT PARAMETERS:
#   none
#
# RETURN:
#   str – Pressure readings plus HTML “Back” button
# -----------------------------------------------------------------------------
def get_pressure():
    html_string = '''
        <form>
            <input type="button" value="Back to Main Menu" onclick="window.location.href='/'" />
        </form>
    '''
    sensor = BMP085.BMP085()
    pressure_read = (sensor.read_pressure()) / PASCAL_CONVERSION 
    sealevel_pressure = (sensor.read_sealevel_pressure()) / PASCAL_CONVERSION
    return f"Pressure = {pressure_read:,.2f} Hg               Sealevel Pressure = {sealevel_pressure:,.2f} Hg\n{html_string}"
     
# -----------------------------------------------------------------------------
# DESCRIPTION
#   Report altitude above sea level from the BMP085 sensor.
#
# INPUT PARAMETERS:
#   none
#
# OUTPUT PARAMETERS:
#   none
#
# RETURN:
#   str – Altitude string plus HTML “Back” button
# -----------------------------------------------------------------------------
@route('/display_altitude')
def get_altitude():
    html_string = '''
        <form>
            <input type="button" value="Back to Main Menu" onclick="window.location.href='/'" />
        </form>
    '''
    sensor = BMP085.BMP085()
    return "Altitude = {0:0.2f} m".format(sensor.read_altitude()) + f"\n{html_string}" 



# -----------------------------------------------------------------------------
# DESCRIPTION
#   Start the Bottle web server on port 8080 (blocking call).
#
# INPUT PARAMETERS:
#   none
#
# OUTPUT PARAMETERS:
#   none
#
# RETURN:
#   none
# -----------------------------------------------------------------------------
def start_server():
    run(host='0.0.0.0', port=8080)

# -----------------------------------------------------------------------------
# DESCRIPTION
#   Open the default web browser to the locally hosted server URL.
#
# INPUT PARAMETERS:
#   none
#
# OUTPUT PARAMETERS:
#   none
#
# RETURN:
#   none
# -----------------------------------------------------------------------------
def launch_website():
    webbrowser.open_new_tab(URL)

# -----------------------------------------------------------------------------
# DESCRIPTION
#   Build a minimal password‑protected Tkinter GUI for launching the web
#   server.
#
# INPUT PARAMETERS:
#   none
#
# OUTPUT PARAMETERS:
#   none
#
# RETURN:
#   none
# -----------------------------------------------------------------------------
def create_gui():
    # -----------------------------------------------------------------------------
    # DESCRIPTION
    #   ...
    #
    # INPUT PARAMETERS:
    #   none
    #
    # OUTPUT PARAMETERS:
    #   none
    #
    # RETURN:
    #   none
    # -----------------------------------------------------------------------------
    def end_program():
        threading.Thread(target=start_server).join
        threading.Thread(target=create_gui).join
        sys.exit()
        quit()

    # -----------------------------------------------------------------------------
    # DESCRIPTION
    #   ...
    #
    # INPUT PARAMETERS:
    #   none
    #
    # OUTPUT PARAMETERS:
    #   none
    #
    # RETURN:
    #   none
    # -----------------------------------------------------------------------------
    def open_webserver(password_entry):
        password = password_entry.get()
        if password == PASSWORD:
            webserver_label.config(text="Web Server URL: " + URL)
            launch_label.config(state=tk.NORMAL)
            threading.Thread(target=start_server).start()
        else:
            webserver_label.config(text="Invalid password. Try again.")
            launch_label.config(state=tk.DISABLED)

    root = tk.Tk()
    root.title("Web Server Launcher")

    password_label = tk.Label(root, text="Enter password:")
    password_label.grid(row=0, column=0)

    password_entry = tk.Entry(root, show="*")
    password_entry.grid(row=0, column=2)

    open_button = tk.Button(root, text="Open Web Server", command=lambda: open_webserver(password_entry))
    open_button.grid(row=1, column=1)

    webserver_label = tk.Label(root, text="")
    webserver_label.grid(row=2, column=1)

    launch_label = tk.Label(root, text="The webserver is now accessible.", state=tk.DISABLED)
    launch_label.grid(row=3, column=1)

    quit_button = tk.Button(root, text="Quit", command=end_program)
    quit_button.grid(row=4, column=1)

    root.mainloop()


# -----------------------------------------------------------------------------
# DESCRIPTION
#   This function sets up the RPi GPIO pins using the GPIO library. 
#
# INPUT PARAMETERS:
#   none
#
# OUTPUT PARAMETERS:
#   none
#
# RETURN:
#   Handle or instance of the PWM object
# -----------------------------------------------------------------------------
def setup_gpio():
    # use BCM GPIO numbering scheme
    GPIO.setmode(GPIO.BCM)
    # set ANEMOMETER pin to INPUT mode
    GPIO.setup(ANEMOMETER_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)


# -----------------------------------------------------------------------------
# DESCRIPTION
#   This function runs the webserver 
#
# INPUT PARAMETERS:
#   none
#
# OUTPUT PARAMETERS:
#   none
#
# RETURN:
#   none
# -----------------------------------------------------------------------------
def start_server():
    run(host='0.0.0.0', port=8080)


# ---------------------------------------------------------------------
#  main() function
# ---------------------------------------------------------------------
def main():
    # -------------------------------------
    # Variables local to this function
    # -------------------------------------
    print()
    print("************ PROGRAM IS RUNNING ************")
    print()

    try:
        gui_thread = threading.Thread(target=create_gui)
        gui_thread.start()
        
        setup_gpio()

    except Exception as Error:
        # An unknown exception was detected, so print the error out message
        print(f"Unexpected error detected: {Error}")

        


# if file execute standalone then call the main function.
if __name__ == '__main__':
    main()


