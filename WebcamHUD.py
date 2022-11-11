# Copyright 2022 expenadableAnomaly
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the following conditions: The above copyright notice and
# this permission notice shall be included in all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import cv2
import numpy as np
import schedule
import requests
from bs4 import BeautifulSoup as bs
from PIL import ImageFont, ImageDraw, Image
import psutil


try:
    import httplib  # python < 3.0
except:
    import http.client as httplib


def have_internet():
    conn = httplib.HTTPSConnection("8.8.8.8", timeout=5)
    try:
        conn.request("HEAD", "/")
        return True
    except Exception:
        return False
    finally:
        conn.close()
guhBool = have_internet()

def convertTime(seconds):
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return "%d:%02d:%02d" % (hours, minutes, seconds)

def batcheck():
    global battery
    battery = psutil.sensors_battery()
    if battery != None:
        global plugged
        plugged = battery.power_plugged
        global batteryRemaining
        batteryRemaining = convertTime(battery.secsleft)
        global batteryPercentage
        batteryPercentage = str(battery.percent)


def job():
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36"
    # US english
    LANGUAGE = "en-US,en;q=0.5"

    def get_weather_data(url):
        session = requests.Session()
        session.headers['User-Agent'] = USER_AGENT
        session.headers['Accept-Language'] = LANGUAGE
        session.headers['Content-Language'] = LANGUAGE
        html = session.get(url)
        # create a new soup
        soup = bs(html.text, "html.parser")

        # store all results on this dictionary
        result = {}
        # extract region
        result['region'] = soup.find("div", attrs={"id": "wob_loc"}).text
        # extract temperature now
        result['temp_now'] = soup.find("span", attrs={"id": "wob_tm"}).text
        # get the actual weather
        result['weather_now'] = soup.find("span", attrs={"id": "wob_dc"}).text
        # get the precipitation
        result['precipitation'] = soup.find("span", attrs={"id": "wob_pp"}).text
        # get the % of humidity
        result['humidity'] = soup.find("span", attrs={"id": "wob_hm"}).text
        return result

    URL = "https://www.google.com/search?lr=lang_en&ie=UTF-8&q=weather"
    import argparse
    parser = argparse.ArgumentParser(description="Quick Script for Extracting Weather data using Google Weather")
    parser.add_argument("region", nargs="?", help="""Region to get weather for, must be available region.
                                            Default is your current location determined by your IP Address""",
                        default="")
    # parse arguments
    args = parser.parse_args()
    region = args.region
    URL += region
    # get data
    data = get_weather_data(URL)

    global displayTemp
    displayTemp = data['temp_now']
    global displayHumidity
    displayHumidity = data['humidity']
    global displayWeather
    displayWeather = data['weather_now']
    global displayPrecipitation
    displayPrecipitation = data['precipitation']


if guhBool:
    job()
    schedule.every(1).minutes.do(job)
else:
    global displayTemp
    displayTemp = 'N/A'
    global displayHumidity
    displayHumidity = 'N/A'
    global displayWeather
    displayWeather = 'N/A'
    global displayPrecipitation
    displayPrecipitation = 'N/A'

batcheck()
schedule.every(1).minutes.do(batcheck)
# declaring font
img = np.zeros((512, 512, 3), np.uint8)
font = cv2.FONT_HERSHEY_SIMPLEX
cv2.putText(img, 'Loading...', (175, 250), font, 1, (255, 255, 255), 2)

# initializing camera

camera = cv2.VideoCapture(0)

while True:
    schedule.run_pending()
    # making img a thing

    _, img = camera.read()

    # placing text

    # display and resize image

    cv2_im_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    pil_im = Image.fromarray(cv2_im_rgb)
    box = (5, 10, 100, 75)
    box2 = (565, 10, 635, 75)
    box3 = (300, 10, 450, 75)
    draw = ImageDraw.Draw(pil_im)
    draw.rectangle(box, fill="#FFFFFF", outline="#000")
    draw.rectangle(box2, fill="#FFFFFF", outline="#000")
    draw.rectangle(box3, fill="#FFFFFF", outline="#000")
    font = ImageFont.truetype("arial.ttf", 32, encoding="unic")
    if guhBool:
        draw.text((10, 10), displayTemp + '°', font=font, fill="#000")
        draw.text((10, 40), displayHumidity, font=font, fill="#000")
        draw.text((570, 10), displayPrecipitation, font=font, fill="#000")
    else:
        draw.text((10, 10), 'N/A', font=font, fill="#000")
        draw.text((10, 40), 'N/A', font=font, fill="#000")
        draw.text((570, 10), 'N/A', font=font, fill="#000")
    if battery != None:
        draw.text((305, 10), batteryPercentage, font=font, fill="#000")
        draw.text((305, 10), plugged, font=font, fill="#000")
        draw.text((305, 10), batteryRemaining, font=font, fill="#000")
    else:
        draw.text((305, 10), 'N/A', font=font, fill="#000")
        draw.text((305, 40), 'N/A', font=font, fill="#000")
        draw.text((375, 10), 'N/A', font=font, fill="#000")
    font = ImageFont.truetype("arial.ttf", 15, encoding="unic")
    if len(displayWeather.split()) > 1:
        topDisplayWeather, bottomDisplayWeather = displayWeather.split(' ', 1)
    else:
        topDisplayWeather = displayWeather
        bottomDisplayWeather = ' '
    draw.text((570, 40), topDisplayWeather, font=font, fill="#000")
    draw.text((570, 55), bottomDisplayWeather, font=font, fill="#000")
    cv2_im_processed = cv2.cvtColor(np.array(pil_im), cv2.COLOR_RGB2BGR)

    img = cv2.resize(cv2_im_processed, (835, 1015))
    cv2.imshow('Image thing', np.concatenate((img, img), axis=1))

    # waitkey
    cv2.waitKey(1)
