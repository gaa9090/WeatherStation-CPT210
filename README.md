# WeatherStation‑CPT210

> **Course:** CPT‑210 — Operating Systems & Peripherals  
> **Authors:** Gwen Antonio · Matthew Bonfiglio · Mark Luskiewicz  
> **Instructor:** Prof. Bruce Link  
> **Date:** May 18 2023

A Raspberry Pi‑based weather station that serves live climate data to any web browser via a Bottle web‑server, secured behind a Tkinter password prompt.

---

## Table of Contents
1. [System Overview](#system-overview)  
2. [Hardware](#hardware)  
3. [Software Stack](#software-stack)  
4. [Features & User Flow](#features--user-flow)  
5. [Wiring Diagrams](#wiring-diagrams)  
6. [Setup & Operation](#setup--operation)  
7. [Future Work](#future-work)  
8. [References](#references)

---

## System Overview
A collection of sensors—temperature/pressure/altitude (BMP180), wind speed (cup anemometer), and wind direction (wind vane)—stream raw data into a Raspberry Pi 4.  
Key points:

* **Realtime Web UI :** Bottle framework hosts a lightweight "weather channel" site.  
* **Secure Launch :** A Tkinter GUI prompts for a password (`123` by default) before the server starts.  
* **Multithreaded Design :** Separate threads keep the GUI responsive while the web server runs.

---

## Hardware
| Component | Purpose | Interface | Notes |
|-----------|---------|-----------|-------|
| **BMP180** | Temp / Pressure / Altitude | I²C (SDA1/SCL1) | Powered at 3.3 V (5 V ok) |
| **SparkFun Cup Anemometer** | Wind speed | GPIO 23 + 10 kΩ pull‑up | 1 rotation = 3 rising edges |
| **SparkFun Wind Vane** | Wind direction (16 pt) | ADS7830 A0 | 10 kΩ pull‑up to 5 V |
| **ADS7830 ADC** | 8‑ch I²C ADC | I²C (same bus as BMP180) | Converts vane voltage |
| **Raspberry Pi 4** | Host computer | 40‑pin GPIO header | Runs Python 3 app |

> *All schematics are in `docs/`.*

---

## Software Stack
| Layer | Library / Tool | Role |
|-------|----------------|------|
| **Back‑end** | `bottle` | REST‑less micro‑framework serving HTML pages |
|            | `threading` | Separate GUI / server threads |
|            | `time` · `math` | Wind‑speed timing, unit conversions |
| **Hardware I/O** | `RPi.GPIO` | Edge detection for anemometer |
|                 | `ADCDevice` | Reads wind‑vane voltage via ADS7830 |
|                 | `Adafruit_BMP.BMP085` | Reads BMP180 sensor |
| **Front‑end** | Plain HTML (+ inline CSS) | Simple, hyperlink‑driven site |
| **Launcher GUI** | `tkinter` | Password prompt & start button |

---

## Features & User Flow
1. **Launch** the application: `sudo python3 210_final.py`  
2. **Authenticate** in the Tkinter dialog → enter password `123`.  
3. **Server online** – console prints `Bottle server running @ http://<pi‑ip>:8080`.  
4. **Browse** to that URL on any device in the same network and pick a data page:
   * **/temperature** – Current °F (BMP180)
   * **/pressure** – Current & sea‑level pressure (in Hg)
   * **/altitude** – Derived altitude (ft)
   * **/wind_speed** – 3 s rolling average MPH
   * **/wind_direction** – Compass heading (e.g., *WSW*)

### Key Algorithms
```python
# --- wind speed ---
ROTATIONS_TO_MPH = 1.49184  # 1 rps → ~1.49 mph
rotation_count = 0
start = time.time()
while time.time() - start < 3:
    if GPIO.input(23):
        rotation_count += 1
        while GPIO.input(23):  # wait for falling edge
            pass
mph = (rotation_count / 9) * ROTATIONS_TO_MPH
```
```python
# --- wind direction ---
raw = adc.read(0)                 # 0‑255
voltage = (raw / 255.0) * 3.3     # V
heading = voltage_to_compass(voltage)  # map via datasheet
```

---

## Wiring Diagrams
> Detailed Fritzing / KiCad drawings can be found in `docs/`.

```text
 RasPi 4          ADS7830            Wind Vane
 --------  I2C  -------------  A0 ───┐
 3.3 V  ───────── VCC                │ 10 kΩ
 GND   ───────── GND                │
 SDA1  ───────── SDA      ──────────┘
 SCL1  ───────── SCL
```

```text
 RasPi 4          Anemometer
 --------  GPIO  ------------
 3.3 V ──┬─┐
         │10 kΩ
 GPIO23 ─┘─●─── sensor wire
 GND    ─────── sensor wire
```

---

## Setup & Operation
```bash
# Enable I²C & install deps (one‑time)
sudo raspi‑config nonint do_i2c 0
sudo apt‑get update
sudo apt‑get install git build‑essential python3‑dev python3‑smbus

# Clone libraries
cd ~/projects
git clone https://github.com/adafruit/Adafruit_Python_BMP.git
cd Adafruit_Python_BMP && sudo python3 setup.py install

# Run the station
cd ~/projects/WeatherStation‑CPT210
sudo python3 210_final.py
```
Use **Ctrl +C** in the terminal to stop the Bottle server (GUI remains—planned fix).

---

## Future Work
- **Rain gauge** integration (kit component not yet used).
- **One‑click shutdown** – close Tkinter & server gracefully.
- **Thread refactor** – drop to two threads (GUI *or* server in main thread).
- **UI polish** – external CSS, nicer layouts, auto‑launch default browser.

---

## References
- [Adafruit BMP085/BMP180 Library](https://github.com/adafruit/Adafruit-BMP085-Library)  
- Argent Data Systems — *Weather Sensor Assembly* p/n 80422  
- [Freenove RFID Starter Kit](https://github.com/Freenove/Freenove_RFID_Starter_Kit_for_Raspberry_Pi)  
- Pi Hut – *Sensors: Pressure, Temperature & Altitude with the BMP180*  
- **Shedboy** – *Pi and BMP180 Sensor* (Pi Bits blog)

---

MIT License © 2023 Gwen Antonio et al.
