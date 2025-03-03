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

objects = {
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

def object_coords(group, i):
    cx = 457
    cy = 367
    r = cy - 250
    n = len(group)

    xi = int(cx + r * math.cos(2 * math.pi * i / n - math.pi / 2))
    yi = int(cy + r * math.sin(2 * math.pi * i / n - math.pi / 2))

    return xi, yi

def find_object(obj):
    group_index = 0
    for category in objects:
        for group in objects[category]:
            try:
                index = group.index(obj)
                return index, group_index
            except ValueError:
                pass
            group_index += 1

    raise ValueError(f"Object '{obj}' not in 'objects'")

objects_state = {
    "current_group": 0,
    "indices": [0] * 11
}

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
    def select_object(self, object):
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
        time.sleep(0.4) # minimum time that seems to work. Might need to be raised.

    def keystroke(self, key):
        subprocess.run(["./sim", "keystroke", str(key)])
        # time.sleep(0.1)

    def erase(self, x, y):
        self.keystroke(self.keys.L)
        self.click(x, y)
        self.keystroke(self.keys.L)

    def select_object(self, obj):
        search_btn = (880, 110)
        next_btn = (760, 360)
        prev_btn = (160, 360)
        prev_section = (270, 120)

        try:
            item_index, group_index = find_object(obj)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            return

        self.click(*search_btn)

        current_group_index = objects_state["current_group"]
        group_delta = group_index - current_group_index
        if group_delta > 0:
            for i in range(group_delta):
                self.keystroke(self.keys.R)
        elif group_delta < 0:
            for i in range(-group_delta):
                self.keystroke(self.keys.L)

        current_item_index = objects_state["indices"][group_index]
        item_delta = item_index - current_item_index
        if item_delta > 0:
            for i in range(item_delta):
                self.keystroke(self.keys.D_RIGHT)
        elif item_delta < 0:
            for i in range(-item_delta):
                self.keystroke(self.keys.D_LEFT)

        self.keystroke(self.keys.A_BTN)

        objects_state["current_group"] = group_index
        objects_state["indices"][group_index] = item_index

    def place_object(self, obj, x, y):
        self.select_object(obj)
        time.sleep(0.5)

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