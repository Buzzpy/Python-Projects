from tuya_connector import (
TuyaOpenAPI
)
import datetime
from tkinter import *
from tkinter import Tk, Canvas, Entry, Text, Button, PhotoImage, font



ACCESS_ID = "4sm4v5fyb6fkekonk8qi"
ACCESS_KEY = "c312c8724dd340d1ab3fb275cf8040fa"
API_ENDPOINT = "https://openapi.tuyain.com"
MQ_ENDPOINT = "wss://mqe.tuyain.com:8285/"

# Init OpenAPI and connect
openapi = TuyaOpenAPI(API_ENDPOINT, ACCESS_ID, ACCESS_KEY)
openapi.connect()

#192.168.1.4
weather = openapi.get("/v2.0/iot-03/weather/current?lat=7.040424985635364&lon=80.00000327776945")

print(weather)

current_weather_condition = (weather['result']['current_weather']['condition'])
temperature = (weather['result']['current_weather']['temp'])
wind_speed = (weather['result']['current_weather']['wind_speed'])
humidity = (weather['result']['current_weather']['humidity'])



window = Tk()
window.state('zoomed')
window.configure(bg = "#3eedd6")

window.title('Tuya Weather App')

photo = PhotoImage(file = "C:\\Users\\jaya\\Downloads\\tuya logo.png")
window.iconphoto(False, photo)

hour = int(datetime.datetime.now().hour)

wish = "Good Morning!"

if hour>=0 and hour<12:
    wish = "Good Morning!"

elif hour>=12 and hour<18:
    wish = "Good Afternoon!"

else:
    wish = "Good Evening!"


###########################################################

if current_weather_condition == 'Overcast':
    current_weather_condition = "Cloudy" #To be easy to understand. Optional

###########################################################

symbol = "�"

if current_weather_condition == 'Cloudy':
    symbol = "☁"

elif current_weather_condition == 'Sunny':
    symbol = "☀"

elif current_weather_condition == 'Windy':
    symbol = "💨"
elif current_weather_condition == 'Rainy':
    symbol = "🌧"
elif current_weather_condition == 'Partly Cloudy':
    symbol = "⛅"

canvas = Canvas(
    window,
    bg = "#3eedd6",
    height = 1024,
    width = 1440,
    bd = 0,
    highlightthickness = 0,
    relief = "ridge"
)

canvas.place(x = 0, y = 0)

canvas.create_text(
    651.0,
    30.0,
    anchor="nw",
    text="Hola!",
    fill="#000000",
    font=("Roboto Condensed", 80 * -1)
)

canvas.create_text(
    544.0,
    154.0,
    anchor="nw",
    text=wish,
    fill="#000000",
    font=("Roboto Condensed", 60 * -1)
)

canvas.create_text(
    370.0,
    354.0,
    anchor="nw",
    text="Current Weather Condition:  ",
    fill="#000000",
    font=("Roboto Condensed", 50 * -1)
)

canvas.create_text(
    99.0,
    521.0,
    anchor="nw",
    text="Temperature:",
    fill="#000000",
    font=("Roboto Condensed", 40 * -1)
)

canvas.create_text(
    103.0,
    588.0,
    anchor="nw",
    text="Humidity:",
    fill="#000000",
    font=("Roboto Condensed", 40 * -1)
)

canvas.create_text(
    99.0,
    657.0,
    anchor="nw",
    text="Wind Speed:",
    fill="#000000",
    font=("Roboto Condensed", 40 * -1)
)

canvas.create_text(
    269.0,
    589.0,
    anchor="nw",
    text=humidity +"%",
    fill="#000000",
    font=("Roboto Condensed", 40 * -1)
)

canvas.create_text(
    307.0,
    657.0,
    anchor="nw",
    text=wind_speed + "km/h",
    fill="#000000",
    font=("Roboto Condensed", 40 * -1)
)

canvas.create_text(
    323.0,
    522.0,
    anchor="nw",
    text=temperature + "°",
    fill="#000000",
    font=("Roboto Condensed", 40 * -1)
)

canvas.create_text(
    909.0,
    354.0,
    anchor="nw",
    text=current_weather_condition + "" + symbol,
    fill="#000000",
    font=("Roboto Condensed", 50 * -1)
)
window.resizable(False, False)
window.mainloop()
