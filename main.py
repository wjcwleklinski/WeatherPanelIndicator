#!/usr/bin/env python3
import signal
import os
import requests
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk as gtk
from gi.repository import AppIndicator3 as appindicator
from gi.repository import GLib as glib


# TODO: location of the client and autorefreshment
APPINDICATOR_ID = 'myappindicator'


def main():
    indicator = appindicator.Indicator.new(APPINDICATOR_ID,
                                           "/home/wojtek/PycharmProjects/WeatherPanelIndicator/icons/contrast.png",
                                           appindicator.IndicatorCategory.SYSTEM_SERVICES)
    indicator.set_status(appindicator.IndicatorStatus.ACTIVE)

    host_ip = get_ip()
    city, country = get_location(host_ip)

    attributes, temp = weather_data(city, country)  # getting attributes only to build menu
    indicator.set_menu(build_menu(attributes))
    indicator.set_label(temp, "")

    glib.timeout_add(600000, change_label, indicator, city, country)  # updating label every 10mins
    gtk.main()  # starts gtk endless loop


# new gtk menu object to obtain menu buttons functionality
# returns menu object
def build_menu(attributes):
    menu = gtk.Menu()

    for i in range(0, len(attributes)):
        new_item = gtk.MenuItem(attributes[i])
        menu.append(new_item)

    item_quit = gtk.MenuItem('Quit')
    item_quit.connect('activate', quit)
    menu.append(item_quit)
    menu.show_all()
    return menu


def weather_data(city, country):
    # TODO: exception handling
    api_address = 'http://api.openweathermap.org/data/2.5/weather?appid=ca428a05cb62822c904d1abb2257ba16&q='
    url = api_address + city
    location = city + ', ' + country
    raw_data_from_api = requests.get(url).json()
    weather = raw_data_from_api['weather'][0]['main']
    weather = 'Sky: ' + weather
    temperature = round(raw_data_from_api['main']['temp'] - 273.16, 2)
    temp_to_display = str(temperature) + ' °C'
    temperature = 'Temperature: ' + str(temperature) + ' °C'
    pressure = raw_data_from_api['main']['pressure']
    pressure = 'Pressure: ' + str(pressure) + ' hPa'
    humidity = raw_data_from_api['main']['humidity']
    humidity = 'Humidity: ' + str(humidity) + ' %'
    wind_speed = raw_data_from_api['wind']['speed']
    wind_speed = 'Wind Speed: ' + str(wind_speed) + ' m/s'
    weather_attributes = [location, weather, temperature, pressure, humidity, wind_speed]
    return weather_attributes, temp_to_display


def get_location(ip_address):
    api_address = 'http://api.ipstack.com/'
    personal_api_key = '8810a19a176c8c056a47d73fdd70e70f'
    url = api_address + ip_address + '?access_key=' + personal_api_key
    raw_json_data = requests.get(url).json()
    country = raw_json_data['country_name']
    city = raw_json_data['city']
    if city is None:
        city = raw_json_data['location']['capital']

    return city, country


def get_ip():
    raw_json = requests.get('https://ifconfig.co/json').json()
    ip = raw_json['ip']
    return ip


def change_label(indicator, city, country):
    attributes, temperature = weather_data(city, country)
    indicator.set_label(temperature, "")
    print(temperature)
    return True


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)  # make ctrl + c work in terminal, must be before main
    main()

