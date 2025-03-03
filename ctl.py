import argparse
import math
import subprocess
import sys
import time
from abc import ABC, abstractmethod

# TODO refactor to use a Point or something instead of raw x/y pairs

class Keys:
    ZL = 0x0C       # Q
    L = 0x0E        # E
    MINUS = 0x1b    # -

    ZR = 0x1F       # O
    R = 0x20        # U
    PLUS = 0x18     # =

    A_BTN = 0x06    # Z
    B_BTN = 0x07    # X
    X_BTN = 0x08    # C
    Y_BTN = 0x09    # V

    L_BTN = 0x03    # F
    L_LEFT = 0x0D   # W
    L_RIGHT = 0x00  # A
    L_DOWN = 0x01   # S
    L_UP = 0x02     # D

    R_BTN = 0x04    # H
    R_LEFT = 0x22   # I
    R_RIGHT = 0x28  # K
    R_DOWN = 0x26   # J
    L_UP = 0x25     # L

    D_LEFT = 0x7B   # left arrow
    D_RIGHT = 0x7C  # right arrow
    D_DOWN = 0x7D   # down arrow
    D_UP = 0x7E     # up arrow

class DvorakKeys:
    ZL = 0x07       # x
    L = 0x02        # d
    MINUS = 0x1B    # quote

    ZR = 0x01       # s
    R = 0x03        # f
    PLUS = 0x1E     # ]

    A_BTN = 0x2C    # slash
    B_BTN = 0x0B    # b
    X_BTN = 0x22    # i
    Y_BTN = 0x2F    # period

    L_BTN = 0x10    # y
    L_LEFT = 0x2B   # comma
    L_RIGHT = 0x00  # a
    L_DOWN = 0x29   # semicolon
    L_UP = 0x04     # h

    R_BTN = 0x27    # j
    R_LEFT = 0x05   # g
    R_RIGHT = 0x09  # v
    R_DOWN = 0x08   # c
    L_UP = 0x23     # p

    D_LEFT = 0x7B   # left arrow
    D_RIGHT = 0x7C  # right arrow
    D_DOWN = 0x7D   # down arrow
    D_UP = 0x7E     # up arrow

class Object:
    def __init__(self, name, category, list_index, index):
        self.name = name
        self.category = category
        self.list_index = list_index
        self.index = index

    def __repr__(self):
        return f"Object({self.name}, {self.category}, list={self.list_index}, index={self.index})"

class ObjectManager:
    def __init__(self):
        self.objects_by_name = {}
        self.current_list = 0
        self.list_indices = [0] * 11

        self.categories = {
            "Terrain": [
                ["Ground", "Steep Slope", "Gentle Slope", "Pipe", "Spike Trap", "Mushroom Platform", "Semisolid Platform", "Bridge"],
                ["Block", "? Block", "Hard Block", "Hidden Block", "Donut Block", "Note Block", "Cloud Block", "Ice Block"]
            ],
            "Items": [
                ["Coin", "10-Coin", "Pink Coin", "Super Mushroom", "Fire Flower", "Cape Feather", "Super Star", "1-Up Mushroom", "Yoshi's Egg"]
            ],
            "Enemies": [
                ["Galoomba", "Koopa Troopa", "Buzzy Beetle", "Spike Top", "Spiny", "Blooper", "Cheep Cheep"],
                ["Jumping Pirahna Plant", "Muncher", "Thwomp", "Monty Mole", "Rocky Wrench", "Hammer Bro", "Chain Comp"],
                ["Wiggler", "Boo", "Lava Bubble", "Bob-omp", "Dry Bones", "Fish Bone", "Magikoopa"],
                ["Bowser", "Bowser Jr.", "Boom Boom", "Angry Sun", "Lakitu", "Koopa Clown Car"]
            ],
            "Gizmos": [
                ["Burner", "Bill Blaster", "Banzai Bill", "Cannon", "Icicle", "Twister"],
                ["Key", "Warp Door", "P Switch", "POW Block", "Trampoline", "Vine", "Arrow Sign", "Checkpoint Flag"],
                ["Lift", "Lava Lift", "Seesaw", "Grinder", "Bumper", "Skewer", "Swinging Claw"],
                ["ON/OFF Switch", "Dotted-Line Block", "Snake Block", "Fire Bar", "One-Way Wall", "Conveyor Belt", "Track"]
            ]
        }

        list_index = 0
        for category, lists in self.categories.items():
            for item_list in lists:
                for index, name in enumerate(item_list):
                    self.objects_by_name[name] = Object(name, category, list_index, index)
                list_index += 1

    def get_object(self, name):
        if name not in self.objects_by_name:
            raise ValueError(f"Object '{name}' not found")
        return self.objects_by_name[name]

    def calculate_coordinates(self, list_index):
        cx = 457
        cy = 367
        r = cy - 250

        item_list = None
        current_index = 0

        for category in self.categories:
            for l in self.categories[category]:
                if current_index == list_index:
                    item_list = l
                    break
                current_index += 1
            if item_list:
                break

        if not item_list:
            raise ValueError(f"List index {list_index} not found")

        n = len(item_list)
        coordinates = []

        for i in range(n):
            xi = int(cx + r * math.cos(2 * math.pi * i / n - math.pi / 2))
            yi = int(cy + r * math.sin(2 * math.pi * i / n - math.pi / 2))
            coordinates.append((xi, yi))

        return coordinates

    def update_selection(self, list_index, item_index):
        self.current_list = list_index
        self.list_indices[list_index] = item_index

# TODO factor into a module maybe
class AutomationManager(ABC):
    # source: /Library/Developer/CommandLineTools/SDKs/MacOSX14.5.sdk/System/Library/Frameworks/
    # Carbon.framework/Versions/A/Frameworks/HIToolbox.framework/Versions/A/Headers/Events.h

    def __init__(self, x, y, width, height, dvorak=False):
        self.win_x = x
        self.win_y = y
        self.win_width = width
        self.win_height = height

        self.keys = DvorakKeys if dvorak else Keys
        self.object_manager = ObjectManager()
        self.current_object = ""

        self._activate()
        self._resize_and_move(x, y, width, height)

    @abstractmethod
    def _activate(self):
        pass

    @abstractmethod
    def _resize_and_move(self, x, y, w, h):
        pass

    @abstractmethod
    def click(self, x, y):
        pass

    @abstractmethod
    def keystroke(self, key):
        pass

    @abstractmethod
    def select_object(self, object_name):
        pass

    @abstractmethod
    def place_object(self, object_name, x, y):
        pass

class MacOSAutomationManager(AutomationManager):
    def _script(self, code):
        subprocess.run(["osascript", "-e", code])

    def _activate(self):
        self._script('activate application "Ryujinx"')

    def _tell_ryujinx(self, *cmds):
        code = '\n'.join(cmds)
        self._script(f'tell application "System Events" to tell process "Ryujinx"\n{code}\nend tell')

    def _resize_and_move(self, x, y, width, height):
        self._tell_ryujinx(
            f"set position of window 1 to {{{x}, {y}}}",
            f"set size of window 1 to {{{width}, {height}}}"
        )
        time.sleep(0.1)

    def click(self, x, y):
        subprocess.run(["./sim", "click", str(x + self.win_x), str(y + self.win_y)])

    def keystroke(self, key):
        subprocess.run(["./sim", "keystroke", str(key)])

    def erase(self, x, y):
        self.keystroke(self.keys.L)
        self.click(x, y)
        self.keystroke(self.keys.L)

    def select_object(self, object_name):
        try:
            obj = self.object_manager.get_object(object_name)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            return

        self.keystroke(self.keys.D_UP)
        self.keystroke(self.keys.Y_BTN)
        time.sleep(0.5)

        current_list = self.object_manager.current_list
        delta = obj.list_index - current_list
        key = self.keys.R if delta > 0 else self.keys.L
        for i in range(abs(delta)):
            self.keystroke(key)

        current_item = self.object_manager.list_indices[obj.list_index]
        delta = obj.index - current_item
        key = self.keys.D_RIGHT if delta > 0 else self.keys.D_LEFT
        for i in range(abs(delta)):
            self.keystroke(key)

        self.keystroke(self.keys.A_BTN)
        time.sleep(0.2)

        self.object_manager.update_selection(obj.list_index, obj.index)

    def place_object(self, object_name, x, y):
        self.select_object(object_name)

        # TODO flesh out grid management
        self.erase(x, y)
        self.click(x, y)

def get_automation_manager(x, y, width, height, dvorak=False):
    if sys.platform == "darwin":
        return MacOSAutomationManager(x, y, width, height, dvorak=dvorak)
    else:
        raise NotImplementedError(f"Unsupported platform '{sys.platform}'")

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--dvorak", action='store_true')
    return parser.parse_args()

def main():
    args = parse_args()

    am = get_automation_manager(100, 100, 915, 600, dvorak=args.dvorak)

    am.place_object("Koopa Troopa", 550, 250) # random square on grid
    time.sleep(2)
    am.place_object("Bowser Jr.", 550, 250)

if __name__ == "__main__":
    main()