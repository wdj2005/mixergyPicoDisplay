import sys
import requests
import json
import secrets
import network
import time


username = secrets.MIXERGY_USER
password = secrets.MIXERGY_PASSWORD
serial_number = secrets.TANK

from picographics import PicoGraphics, DISPLAY_PICO_DISPLAY
from pimoroni import RGBLED

# set up the hardware
display = PicoGraphics(display=DISPLAY_PICO_DISPLAY, rotate=270)

# set the display backlight to 20%
display.set_backlight(0.5)
display.set_font("sans")
display.set_thickness(2)

# turn off the RGB LED
led = RGBLED(6, 7, 8)
led.set_rgb(0,0,0)

# set up constants for drawing
WIDTH, HEIGHT = display.get_bounds()
# setup some colours
RED = display.create_pen(209, 34, 41)
YELLOW = display.create_pen(255, 216, 0)
GREEN = display.create_pen(0, 216, 0)
WHITE = display.create_pen(255, 255, 255)
BLUE = display.create_pen(116, 215, 238)
BLACK = display.create_pen(0, 0, 0)


# Connect to WLAN
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(secrets.SSID, secrets.PASSWORD)
while not wlan.isconnected():
    pass
print('Connected to WLAN')


# Get login URL

result = requests.get("https://www.mixergy.io/api/v2")

root_result = result.json()

account_url = root_result["_links"]["account"]["href"]

result = requests.get(account_url)

account_result = result.json()

login_url = account_result["_links"]["login"]["href"]

result = requests.post(login_url, json = {'username': username, 'password': password})

if result.status_code != 201:
    print("Mixergy authentication failure. Check your credentials and try again!")
    exit()

print("Mixergy authentication successful!")

login_result = result.json()

login_token = login_result["token"]

headers = {'Authorization': f'Bearer {login_token}'}

result = requests.get("https://www.mixergy.io/api/v2", headers=headers)

root_result = result.json()

tanks_url = root_result["_links"]["tanks"]["href"]

result = requests.get(tanks_url, headers=headers)

tanks_result = result.json()

tanks = tanks_result['_embedded']['tankList']



for i, subjobj in enumerate(tanks):
    if serial_number == subjobj['serialNumber']:
        print("Found tanks serial number", subjobj['serialNumber'])

        tank_url = subjobj["_links"]["self"]["href"]
        print("Tank Url:", tank_url)
        
        print("Fetching details...")

        result = requests.get(tank_url, headers=headers)

        tank_result = result.json()

        latest_measurement_url = tank_result["_links"]["latest_measurement"]["href"]
        control_url = tank_result["_links"]["control"]["href"]
        modelCode = tank_result["tankModelCode"]


        result = requests.get(latest_measurement_url, headers=headers)

        latest_measurement_result = result.json()
        charge = latest_measurement_result["charge"]
        print("Charge:",charge)

        state = json.loads(latest_measurement_result["state"])

        current = state["current"]
        heat_source = current["heat_source"]
        heat_source_on = current["immersion"] == "On"

        print("Heat Source:", heat_source)
        print("Heat Source On:", heat_source_on)

        # fills the screen with white
        display.set_pen(WHITE)
        display.clear()
    
        # writes the charge level as text 
        display.set_pen(BLACK)
        display.text("MIXERGY", 3, 20, 0, 1)
    
        display.text("{:.2f}".format(charge) + "%", 3, 60, 0, 2)
        
        display.text(heat_source, 3, 100, 0, 1)
        
        if heat_source_on:
            display.text("HEATING", 3, 140, 0, 1)
        else:
            display.text("       ", 3, 140, 0, 1)            
        
        # time to update the display
        display.update()
        time.sleep(30)
        
