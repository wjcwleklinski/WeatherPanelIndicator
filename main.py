#!/usr/bin/env python
from gi.repository import Gtk as gtk
from gi.repository import AppIndicator3 as appindicator
import signal
import requests

APPINDICATOR_ID = 'myappindicator'


def main():
    indicator = appindicator.Indicator.new(APPINDICATOR_ID, gtk.STOCK_GO_UP, appindicator.IndicatorCategory.SYSTEM_SERVICES)
    indicator.set_status(appindicator.IndicatorStatus.ACTIVE)

    city = 'Gliwice'
    attributes = weather_data(city)
    indicator.set_menu(build_menu(attributes))  # set created menu
    gtk.main()  # starts gtk endless loop


# new gtk menu object to obtain menu buttons functionality
# returns menu object
def build_menu(attributes):
    menu = gtk.Menu()

    for i in range(0, len(attributes)):
        new_item = gtk.MenuItem(attributes[i])
        menu.append(new_item)

    item_refresh = gtk.MenuItem('Refresh')

    item_quit = gtk.MenuItem('Quit')
    item_quit.connect('activate', quit)
    menu.append(item_quit)
    menu.show_all()
    return menu


def weather_data(city):
    api_adress = 'http://api.openweathermap.org/data/2.5/weather?appid=ca428a05cb62822c904d1abb2257ba16&q='
    url = api_adress + city
    raw_data_from_api = requests.get(url).json()
    weather = raw_data_from_api['weather'][0]['main']
    temperature = round(raw_data_from_api['main']['temp'] - 273.16, 2)
    temperature = 'Temperature: ' + str(temperature) + ' C'
    pressure = raw_data_from_api['main']['pressure']
    pressure = 'Pressure: ' + str(pressure) + ' hPa'
    humidity = raw_data_from_api['main']['humidity']
    humidity = 'Humidity: ' + str(humidity) + ' %'
    wind_speed = raw_data_from_api['wind']['speed']
    wind_speed = 'Wind Speed: ' + str(wind_speed) + ' m/s'
    weather_atributes = [city, weather, temperature, pressure, humidity, wind_speed]
    return weather_atributes


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)  # make ctrl + c work in terminal, must be before main
    main()

