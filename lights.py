from nanoleafapi import discovery, Nanoleaf, NanoleafDigitalTwin
import requests
from random import choice
import time
import sys
from datetime import datetime

IP_ADDRESS = "192.168.42.8"
URL = "https://kctbh9vrtdwd.statuspage.io/api/v2/components.json"

def find():
    nanoleaf_dict = discovery.discover_devices(debug=True)
    print(nanoleaf_dict)
    for ip in range(8, 9):
        full = "192.168.42.{ip}".format(ip=ip)
        try:
            res = requests.get("http://{full}:16021".format(full=full))
            print(res.status_code)
        except (requests.ConnectionError):
            print(full, "error")

class Nano:
    RED = (255, 0, 0)
    ORANGE = (255, 165, 0)
    YELLOW = (255, 255, 0)
    GREEN = (0, 255, 0)
    LIGHT_BLUE = (173, 216, 230)
    BLUE = (0, 0, 255)
    PINK = (255, 192, 203)
    PURPLE = (128, 0, 128)
    WHITE = (255, 255, 255)

    COLOURS = [
        RED, ORANGE, YELLOW, GREEN,
        LIGHT_BLUE, BLUE, PINK, PURPLE, WHITE
    ]

    BOTTOM = 56389
    BOTTOM_PLUS_ONE = 50177
    BOTTOM_PLUS_TWO = 14752
    LEFT = 10466
    RIGHT = 20388
    TOP = 9386
    TOP_MINUS_ONE = 34437

    LIGHTS = [
        BOTTOM, BOTTOM_PLUS_ONE, BOTTOM_PLUS_TWO,
        LEFT, RIGHT, TOP_MINUS_ONE, TOP
    ]

    MAPPING = {
        "GitHub Actions": BOTTOM,
        "GitHub Pages": BOTTOM_PLUS_ONE,
        "API Requests": BOTTOM_PLUS_TWO,
        "GitHub Packages": LEFT,
        "Codespaces": RIGHT,
        "Git Operations": TOP_MINUS_ONE,
        "Issues": TOP,
    }

    def __init__(self, ip):
        self.nl = Nanoleaf(ip)
        self.twin = NanoleafDigitalTwin(self.nl)
        self.last = {}
        self.nl.set_brightness(15)
        self.needs_syncing = False

    def turn_on(self):
        if not self.nl.get_power():
            self.nl.toggle_power()

    def turn_off(self):
        if self.nl.get_power():
            self.nl.toggle_power()

    def set(self, light, colour):
        if (self.last.get(light, None) != colour):
            self.twin.set_color(light, colour)
            self.last[light] = colour
            self.needs_syncing = True

    def sync(self):
        if self.needs_syncing:
            self.twin.sync()
            self.needs_syncing = False

    def set_all(self):
        for light in self.LIGHTS:
            self.twin.set_color(light, choice(self.COLOURS))
        self.needs_syncing = True


class GitHubStatus:
    def __init__(self):
        self.url = URL
        self.lookup = {
            "operational": Nano.GREEN,
            "partial_outage": Nano.YELLOW,
        }

    def get(self):
        res = requests.get(self.url)
        res.raise_for_status()
        result = {}
        print(datetime.now())
        for component in res.json()["components"]:
            if "Visit" in component["name"]:
                continue
            print(component["name"], "is", component["status"])
            result[component["name"]] = self.lookup.get(component["status"], Nano.RED)

        return result

def set_status():
    for key, value in status.get().items():
        if key in nl.MAPPING:
            nl.set(nl.MAPPING[key], value)
    nl.sync()

if __name__ == '__main__':
    nl = Nano(IP_ADDRESS)
    status = GitHubStatus()

    if "--loop" in sys.argv:
        while 1:
            set_status()
            time.sleep(120)
    else:
        set_status()
