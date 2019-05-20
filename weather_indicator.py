#!/usr/bin/env python3
import signal
import os
import requests
import gi
import socket
import fcntl
import struct
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk as gtk
from gi.repository import AppIndicator3 as appindicator
from gi.repository import GLib as glib


APPINDICATOR_ID = 'myappindicator'
# REPEAT_TIME_MS = 120000
REPEAT_TIME_MS = 30000


class WeatherIndicator:
    attributes_prefix = ['', 'Sky: ', 'Temperature: ', 'Pressure:', 'Humidity: ', 'Wind Speed: ']

    def __init__(self, name=None, icon=None):
        self.path = os.path.abspath(os.path.dirname(__file__))

        signal.signal(signal.SIGINT, signal.SIG_DFL)

        if name is None:
            self.name = "WeatherIndicator"
        else:
            self.name = name

        if icon is None:
            self.icon = gtk.STOCK_INFO
        else:
            self.icon = icon

        self.indicator = appindicator.Indicator.new(
            self.name, self.icon,
            appindicator.IndicatorCategory.SYSTEM_SERVICES
        )
        self.indicator.set_status(appindicator.IndicatorStatus.ACTIVE)

        weather_data, icon_path = self.get_weather_data_from_request()
        menu, menu_items_to_update = self.build_menu(weather_data)

        self.indicator.set_menu(menu)
        self.indicator.set_label(weather_data[2], "")
        self.indicator.set_icon(icon_path)

        glib.timeout_add(REPEAT_TIME_MS, self.update_indicator, menu_items_to_update)
        gtk.main()

    @staticmethod
    def get_ip_from_request():
        raw_json = requests.get('https://ifconfig.co/json').json()
        ip = raw_json['ip']
        return ip

    @staticmethod
    def get_location_from_request(ip_address):
        api_address = 'http://api.ipstack.com/'
        personal_api_key = '8810a19a176c8c056a47d73fdd70e70f'
        url = api_address + ip_address + '?access_key=' + personal_api_key
        raw_json_data = requests.get(url).json()
        country = raw_json_data['country_name']
        city = raw_json_data['city']
        if city is None:
            city = raw_json_data['location']['capital']

        return city, country

    def get_weather_data_from_request(self):
        host_ip = self.get_ip_from_request()
        city, country = self.get_location_from_request(host_ip)
        api_address = 'http://api.openweathermap.org/data/2.5/weather?appid=ca428a05cb62822c904d1abb2257ba16&q='
        url = api_address + city
        location = city + ', ' + country
        raw_data_from_api = requests.get(url).json()
        sky = raw_data_from_api['weather'][0]['main']
        temperature = round(raw_data_from_api['main']['temp'] - 273.16, 1)
        temperature = str(temperature) + ' °C'
        pressure = raw_data_from_api['main']['pressure']
        pressure = str(pressure) + ' hPa'
        humidity = raw_data_from_api['main']['humidity']
        humidity = str(humidity) + ' %'
        wind_speed = raw_data_from_api['wind']['speed']
        wind_speed = str(wind_speed) + ' m/s'
        icon_path = os.path.dirname(os.path.realpath(__file__)) + "/icons/" + raw_data_from_api['weather'][0][
            'icon'] + ".png"
        weather_data = [location, sky, temperature, pressure, humidity, wind_speed]
        return weather_data, icon_path

    def build_menu(self, attributes):
        menu = gtk.Menu()

        menu_items = []
        for i in range(0, len(attributes)):
            new_item = gtk.MenuItem(self.attributes_prefix[i] + attributes[i])
            menu.append(new_item)
            menu_items.append(new_item)

        item_quit = gtk.MenuItem('Quit')
        item_quit.connect('activate', quit)
        menu.append(item_quit)
        menu.show_all()

        return menu, menu_items

    def update_indicator(self, menu_items):
        try:
            weather_data, icon_path = self.get_weather_data_from_request()
            print(city + ", " + country + ", IP: " + str(host_ip))
            self.indicator.set_label(weather_data[2], "")
            self.indicator.set_icon(icon_path)
            for i in range(0, len(weather_data)):
                menu_items[i].set_label(self.attributes_prefix[i] + weather_data[i])
        except:
            print("Update oopsy.")

        return True


if __name__ == "__main__":
    weatherIndicator = WeatherIndicator('Weather indicator', os.path.dirname(os.path.realpath(__file__)) + "/icons/contrast.png")
