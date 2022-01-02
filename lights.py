from nanoleafapi import discovery, Nanoleaf, NanoleafDigitalTwin
import requests
from random import choice

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
        "Codespaces": RIGHT
    }

    def __init__(self, ip):
        self.nl = Nanoleaf(ip)
        self.twin = NanoleafDigitalTwin(self.nl)
    
    def turn_on(self):
        if not self.nl.get_power():
            self.nl.toggle_power()
    
    def turn_off(self):
        if self.nl.get_power():
            self.nl.toggle_power()

    def set(self, light, colour):
        self.twin.set_color(light, colour)
        self.twin.sync()

    def set_all(self):
        for light in self.LIGHTS:
            self.twin.set_color(light, choice(self.COLOURS))
        self.twin.sync()


class GitHubStatus:
    def __init__(self):
        self.url = URL
        self.lookup = {
            "operational": Nano.GREEN,
        }

    def get(self):
        res = requests.get(self.url)
        res.raise_for_status()
        result = {}
        for component in res.json()["components"]:
            result[component["name"]] = self.lookup.get(component["status"], Nano.RED)
        return result

if __name__ == '__main__':
    nl = Nano(IP_ADDRESS)
    status = GitHubStatus()
    for key, value in status.get().items():
        if key in nl.MAPPING:
            nl.set(nl.MAPPING[key], value)
