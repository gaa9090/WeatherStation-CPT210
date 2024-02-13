# WeatherStation-CPT210




Weather Station
Gwen Antonio
Matthew Bonfiglio
Mark Luskiewicz
CPT-210: Operating Systems and Peripherals
Prof. Bruce Link
May 18, 2023


Summary:
A weather station is a system of peripherals that works together to collect current samples of a given climate. When constructing the weather station, common features implemented are temperature sensors, wind speed sensors (anemometer), wind direction sensors (wind vane), air humidity sensors, air pressure sensors (barometer), and altitude sensors. 

This program is a simplified version of a weather station that emulates similar functionality found in real-world weather channels. This project has provided valuable hands-on experience and foundational knowledge that aligns with practical weather monitoring and collection.
Upon opening the program, the user is prompted to enter a password in order to gain access to the web server. This was made by a GUI created with Tkinter. Then the program creates a webserver using the Python Bottle framework to give the user an online weather channel interface. 

The weather station provides a unique customization where users can view various weather choices such as temperature, pressure, wind speed, wind direction, and altitude. This feature provides a comprehensive overview of weather conditions, making the station more informative and useful in comparison to other projects with limited information and variety. Beside unique customizations, this project incorporates a Tkinter GUI which allows the program to be user-friendly and easy to navigate. By setting a password to start the webserver, the program ensures that the access to the weather data is secure. The intuitive design and interactive buttons enhance the user’s experience that sets it apart from projects with more complex and less intuitive designs.

Features include:
Web interface that allows users to access the weather information through the web browsers that allows users to navigate between the displays.
Temperature page on the website which displays the current temperature in the current environment measured by the BMP180 sensor
Barometric pressure page which displays the current pressure and the sea level pressure readings from the BMP180 sensor.
Altitude page which displays the current altitude of the user’s position measured by the BMP180.
Wind speed page which displays the current wind speed based on the rotation count measured by the anemometer.
Wind direction page displayed the wind direction based on the voltage read from the ADC.


External components include:
SparkFun Cup Anemometer to measure the wind speed in miles per hour.
SparkFun Wind Vane to measure the direction of the wind.
ADS7830 Analog-to-Digital converter that is used by the BMP180 and the wind vane to allow them to function.
BMP180 Barometric Pressure/Temperature/Altitude sensor that gathers various data that our weather system uses.

Python libraries include:
Math library for mathematical calculations that include measuring the wind speed.
Time library for time related functions such as calculating wind speed.
Threading library to create and manage threads such as the GUI and the server.

External python libraries include:
Bottle web framework to create the web server for users to see the weather channel.
ADCDevice library for reading voltage from the wind vane.
Adafruit_BMP.BMP085 library for interfacing the BMP180 sensor.
RPi.GPIO library to control the Raspberry Pi 4 GPIO pins.
Tkinter library for creating GUI to enter password and launch the web server.




















Design Details:
This diagram represents the connections of the system: 


SparkFun Wind Vane
The wind vane is connected with the black wire being put to ground, and the green wire is connected to a row on the breadboard that is ultimately connected to pin 0 of the ADS7830 ADC. The row for the green wire contains a 10k ohm resistor going from the row to 5 volts VCC, and a jumper wire connecting the row to the ADC. In total, this row contains a 10k ohm resistor, the green wire from the wind vane, and a jumper wire.



The above schematic shows the inner workings of the wind vane. The wind vane works by closing the circuit on different resistors in the wind vane. Every cardinal direction corresponds to a different combination of resistors, and therefore provides a way to turn the voltage reading into a user-friendly direction. From the table above, the direction is calculated based on the voltage reading from the ADC. Zero degrees would correspond to east, and the angle in degrees is the angle from east measured counterclockwise. Therefore, north would be 90 degrees, west would be 180, and south would be 270. Directly in the middle of those angles, would be corresponding to NE, NW, SW, and SE in that order from zero degrees. Again, going halfway between the four cardinal directions and the in-between directions would correspond to ENE, NNE, NNW, WNW, WSW, SSW, SSE, and ESE. With ENE being 22.5 degrees counterclockwise of east. These are all of the obtainable directions offered from the SparkFrom wind vane. The following pseudocode shows how the program handles the wind vane voltage reading: 


value = read_wind_vane()
voltage = value / ADC_TO_VOLTAGE    # ADC_TO_VOLTAGE = 255 * 3.3
voltage *= 1000
voltage = math.floor(voltage)

From here a simple if/else statement can return the correct value, reference the datasheet for discrete values to the voltages. 

SparkFun Cup Anemometer
The anemometer has 2 different wires, one of which is connected through a 10k ohm resistor (any resistor is fine, we are merely avoiding a short) to VCC, and the other is connected to GPIO port 23. It does not matter which wire is connected to which pin.



Each arm of the anemometer has a magnet that will close the switch connecting VCC to ground. The output to pin 1 is inverted such that for every switch closing a logic level 1 is sent to GPIO 23. The program uses the time module to track 3 seconds worth of total rising edges and divides it by 9 to get average rising edges per second (1 rotation = 3 rising edges, each arm has a switch closing magnet) the following pseudocode explains the process of finding and calculating wind speed:

ROTATIONS_TO_MPH = 1.49184              # wind speed in MPH if the anemometer is turning 1 time per second (leveraged from datasheet)
rotation_count = 0
while current time < current time + 3:  # for 3 seconds
    if pin input is high:
        rotation_count += 1 
        while pin input is high:        # wait for falling edge
            pass


mph = (rotation_count / 9) * ROTATIONS_TO_MPH




Adafruit BMP180
The BMP180 chip is wired to the ADC. In this project, 3.3V was used to connect the BMP180 to power but if needed, VCC (or VIN) can be connected to 5V depending on the programmer’s specific needs. SCL was wired to SCL1 and SDA was wired to SDA1. The image below shows a simple schematic to show how to properly hook up the BMP180.


After the hardware is set up, you need to check if the Raspberry Pi sees the BMP180. Open the Linux terminal and type:
	sudo i2c detect -y 1

If the BMP180 is hooked up properly then an 8x16 grid will be returned with number 77 in one of the rows and columns as shown below. This shows that the BMP180 is connected to channel 77 on the Raspberry Pi.



In order to attain and read the data being collected by the BMP180, a library written by Adafruit was installed from GitHub. In order to use and install libraries from github, updating the package manager using the command is required:	
sudo apt-get update













Then, the GIT application will be installed in order to retrieve the code from Adafruit using the following command:
sudo apt-get install git build-essential python-dev python-smbus


Next, cd to the folder where the main code is stored and download the GIT repository for the BMP180 by entering the command:
git clone https://github.com/adafruit/Adafruit_Python_BMP.git



Now that the contents of the Adafruit Python library is downloaded in the correct location, the BMP is ready to be used on the Raspberry Pi.

The code that is provided by Adafruit returns temperature (in Celsius), pressure and sea level pressure (in Pascal), and altitude (in meters). The units of measurement were changed for pressure from Pascal to Inches in Mercury (Hg) and Celsius to Farenheight to make the interface readable for the user.

The code below was used to display the pressure and sea level pressure on the website:


The pressure_read variable and sealevel_pressure variable calls the Adafruit code and reads from the read_pressure and read_sealevel_pressure function to calculate the pressure in Pascal that is being read from the BMP180.

For temperature and altitude, a similar process is needed. But note that in order to change the units from Celsius to Fahrenheit, the programmer must open the source code and find the function that the temperature is being read from, and add the math accordingly.

ADS7830 ADC
The ADS7830 ADC is a component to convert the raw voltage data from our peripherals into usable, digital values. The ADC for the Raspberry Pi also requires proper I2C configuration in order to operate. For use in our weather system, we are utilizing pin A0, VCC, SDA, SCL, and GND. Pin A0 is connected to the SparkFun wind vane, VCC is connected to +5 volts, and GND is connected to the ground rail on the breadboard. However, the SDA and SCL pins have 2 connections each. The SDA pin on the ADC connects to SDA1 on the GPIO extension board, and it also connects to the SDA pin on the BMP180. The SCL pin on the ADC connects to SCL1 on the GPIO extension board, and it also connects to the SCL pin on the BMP180. On our ADC, the SDA and SCL lines are used to transmit data from the BMP180 to the Raspberry Pi while the A0 pin is used to retrieve a voltage reading from the SparkFun wind vane.










Operation Details:
The file must be run in the terminal to allow the bottle framework to have the adequate level of access to start the web server. Upon running the server, the user will have full access to all features of the program.
Open the Linux command terminal and cd (change directory) into the location of the program file. In order to start the program, run the command “sudo python3 210_final.py”.



Once the program is running, a tkinter window will launch and request a password from the user. The password is located in the global variables in the 210_final.py file and is defaulted as ‘123’.








After entering the correct password, the bottle framework will activate the server and a message will confirm the server is active. The user may enter the website's URL into a web browser to view the weather channel.



Once the website is launched, the user may navigate the website and view any variety of weather information by clicking on the hyperlink buttons.















Future work needed:
The Sparkfun weather station kit comes with a rain meter that can be used to detect the level of rainfall in a given moment that has not been implemented. 

There is still not a complete “exit” button that will close the Tkinter window and shut down the server. Currently the KeyboardInterrupt python exception (ctrl + c) will close the bottle server but the Tkinter window will remain open.

The current program is currently utilizing 3 threads with our program to be able to use the Tkinter GUI and bottle web server together. Currently, the threads consist of a server thread, Tkinter thread, and the main thread. However, this created unnecessary complications with the control of the program as it had multiple threads to track. This prevented the computer from closing the program smoothly in its current state as it could not get the threads to end with each other. Instead, remove one of the threads and utilize the main thread to execute either the GUI or the web server instead of the current 3 thread system.

Although not functionally important, including HTML and or introducing CSS to provide a more user-friendly experience.

Lastly, another feature that was not finished was opening up a web browser either from a Tkinter GUI or just straight from a function call in the code. Bringing the user directly to the website by opening up a browser with the URL, would provide an easy access to the website. 


















References

Adafruit. (n.d.). GitHub - adafruit/Adafruit-BMP085-Library: A powerful but easy to use BMP085/BMP180 Arduino library. GitHub. https://github.com/adafruit/Adafruit-BMP085-Library
Argent Data Systems. (n.d.). Weather Sensor Assembly p/n 80422. Retrieved May 18, 2023, from https://cdn.sparkfun.com/assets/8/4/c/d/6/Weather_Sensor_Assembly_Updated.pdf
Freenove. (n.d.). GitHub - Freenove/Freenove_RFID_Starter_Kit_for_Raspberry_Pi: Apply to FNK0025. GitHub. https://github.com/Freenove/Freenove_RFID_Starter_Kit_for_Raspberry_Pi
Hut, P. (2015). Sensors - Pressure, Temperature and Altitude with the BMP180. The Pi Hut. https://thepihut.com/blogs/raspberry-pi-tutorials/18025084-sensors-pressure-temperature-and-altitude-with-the-bmp180
Shedboy, & Shedboy. (2016). Pi and BMP180 sensor | Pi bits. Pi Bits. http://www.pibits.net/amp/learning/pi-and-bmp180-sensor.php



