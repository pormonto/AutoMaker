import math
import subprocess
import sys
import time
import json
from abc import ABC, abstractmethod

# source: /Library/Developer/CommandLineTools/SDKs/MacOSX14.5.sdk/System/Library/Frameworks/
# Carbon.framework/Versions/A/Frameworks/HIToolbox.framework/Versions/A/Headers/Events.h

class Keys:
    ZL      = 0x0C    # Q
    L       = 0x0E    # E
    MINUS   = 0x1B    # -

    ZR      = 0x1F    # O
    R       = 0x20    # U
    PLUS    = 0x18    # =

    A_BTN   = 0x06    # Z
    B_BTN   = 0x07    # X
    X_BTN   = 0x08    # C
    Y_BTN   = 0x09    # V

    L_BTN   = 0x03    # F
    L_LEFT  = 0x0D    # W
    L_RIGHT = 0x00    # A
    L_DOWN  = 0x01    # S
    L_UP    = 0x02    # D

    R_BTN   = 0x04    # H
    R_LEFT  = 0x22    # I
    R_RIGHT = 0x28    # K
    R_DOWN  = 0x26    # J
    R_UP    = 0x25    # L

    D_LEFT  = 0x7B    # Left arrow
    D_RIGHT = 0x7C    # Right arrow
    D_DOWN  = 0x7D    # Down arrow
    D_UP    = 0x7E    # Up arrow

class Object:
    def __init__(self, name, category, list_index, index):
        self.name = name
        self.category = category
        self.list_index = list_index
        self.index = index

    def __repr__(self):
        return f"Object({self.name}, {self.category}, list={self.list_index}, index={self.index})"

# TODO: store object size, validate json on load to make sure there are no overlapping units
class ObjectManager:
    def __init__(self, style):
        self.objects_by_name = {}
        self.style = style
        self.current_list = 0
        self.list_indices = [0] * 11

        self.styles = {
            "Super Mario Bros": {
                "Terrain": [
                    ["Ground", "Steep Slope", "Gentle Slope", "Pipe", "Spike Trap", "Mushroom Platform", "Semisolid Platform", "Bridge"],
                    ["Block", "? Block", "Hard Block", "Hidden Block", "Donut Block", "Note Block", "Cloud Block", "Ice Block"]
                ],
                "Items": [
                    ["Coin", "10-Coin", "Pink Coin", "Super Mushroom", "Big Mushroom", "Cape Feather", "Super Star", "1-Up Mushroom", "Shoe Goomba"]
                ],
                "Enemies": [
                    ["Goomba", "Koopa Troopa", "Buzzy Beetle", "Spike Top", "Spiny", "Blooper", "Cheep Cheep"],
                    ["Pirahna Plant", "Muncher", "Thwomp", "Monty Mole", "Rocky Wrench", "Hammer Bro", "Chain Comp"],
                    ["Wiggler", "Boo", "Lava Bubble", "Bob-omb", "Dry Bones", "Fish Bone", "Magikoopa"],
                    ["Bowser", "Bowser Jr.", "Boom Boom", "Angry Sun", "Lakitu", "Koopa Clown Car"]
                ],
                "Gizmos": [
                    ["Burner", "Bill Blaster", "Banzai Bill", "Cannon", "Icicle", "Twister"],
                    ["Key", "Warp Door", "P Switch", "POW Block", "Trampoline", "Vine", "Arrow Sign", "Checkpoint Flag"],
                    ["Lift", "Lava Lift", "Seesaw", "Grinder", "Bumper", "Skewer", "Swinging Claw"],
                    ["ON/OFF Switch", "Dotted-Line Block", "Snake Block", "Fire Bar", "One-Way Wall", "Conveyor Belt", "Track"]
                ]
            },

            "Super Mario Bros 3": {
                "Terrain": [
                    ["Ground", "Steep Slope", "Gentle Slope", "Pipe", "Spike Trap", "Mushroom Platform", "Semisolid Platform", "Bridge"],
                    ["Block", "? Block", "Hard Block", "Hidden Block", "Donut Block", "Note Block", "Cloud Block", "Ice Block"]
                ],
                "Items": [
                    ["Coin", "10-Coin", "Pink Coin", "Super Mushroom", "Fire Flower", "Super Leaf", "Super Star", "1-Up Mushroom", "Shoe Goomba"]
                ],
                "Enemies": [
                    ["Goomba", "Koopa Troopa", "Buzzy Beetle", "Spike Top", "Spiny", "Blooper", "Cheep Cheep"],
                    ["Pirahna Plant", "Muncher", "Thwomp", "Monty Mole", "Rocky Wrench", "Hammer Bro", "Chain Comp"],
                    ["Wiggler", "Boo", "Lava Bubble", "Bob-omb", "Dry Bones", "Fish Bone", "Magikoopa"],
                    ["Bowser", "Bowser Jr.", "Boom Boom", "Angry Sun", "Lakitu", "Koopa Clown Car"]
                ],
                "Gizmos": [
                    ["Burner", "Bill Blaster", "Banzai Bill", "Cannon", "Icicle", "Twister"],
                    ["Key", "Warp Door", "P Switch", "POW Block", "Trampoline", "Vine", "Arrow Sign", "Checkpoint Flag"],
                    ["Lift", "Lava Lift", "Seesaw", "Grinder", "Bumper", "Skewer", "Swinging Claw"],
                    ["ON/OFF Switch", "Dotted-Line Block", "Snake Block", "Fire Bar", "One-Way Wall", "Conveyor Belt", "Track"]
                ]
            },

            "Super Mario World": {
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
                    ["Wiggler", "Boo", "Lava Bubble", "Bob-omb", "Dry Bones", "Fish Bone", "Magikoopa"],
                    ["Bowser", "Bowser Jr.", "Boom Boom", "Angry Sun", "Lakitu", "Koopa Clown Car"]
                ],
                "Gizmos": [
                    ["Burner", "Bill Blaster", "Banzai Bill", "Cannon", "Icicle", "Twister"],
                    ["Key", "Warp Door", "P Switch", "POW Block", "Trampoline", "Vine", "Arrow Sign", "Checkpoint Flag"],
                    ["Lift", "Lava Lift", "Seesaw", "Grinder", "Bumper", "Skewer", "Swinging Claw"],
                    ["ON/OFF Switch", "Dotted-Line Block", "Snake Block", "Fire Bar", "One-Way Wall", "Conveyor Belt", "Track"]
                ]
            },

            "Super Mario Bros U": {
                "Terrain": [
                    ["Ground", "Steep Slope", "Gentle Slope", "Pipe", "Spike Trap", "Mushroom Platform", "Semisolid Platform", "Bridge"],
                    ["Block", "? Block", "Hard Block", "Hidden Block", "Donut Block", "Note Block", "Cloud Block", "Ice Block"]
                ],
                "Items": [
                    ["Coin", "10-Coin", "Pink Coin", "Super Mushroom", "Fire Flower", "Propeller Mushroom", "Super Star", "1-Up Mushroom", "Yoshi's Egg"]
                ],
                "Enemies": [
                    ["Goomba", "Koopa Troopa", "Buzzy Beetle", "Spike Top", "Spiny", "Blooper", "Cheep Cheep"],
                    ["Pirahna Plant", "Muncher", "Thwomp", "Monty Mole", "Rocky Wrench", "Hammer Bro", "Chain Comp"],
                    ["Wiggler", "Boo", "Lava Bubble", "Bob-omb", "Dry Bones", "Fish Bone", "Magikoopa"],
                    ["Bowser", "Bowser Jr.", "Boom Boom", "Angry Sun", "Lakitu", "Junior Clown Car"]
                ],
                "Gizmos": [
                    ["Burner", "Bill Blaster", "Banzai Bill", "Cannon", "Icicle", "Twister"],
                    ["Key", "Warp Door", "P Switch", "POW Block", "Trampoline", "Vine", "Arrow Sign", "Checkpoint Flag"],
                    ["Lift", "Lava Lift", "Seesaw", "Grinder", "Bumper", "Skewer", "Swinging Claw"],
                    ["ON/OFF Switch", "Dotted-Line Block", "Snake Block", "Fire Bar", "One-Way Wall", "Conveyor Belt", "Track"]
                ]
            },

            "Super Mario 3D Worlds": {
                "Terrain": [
                    ["Ground", "Steep Slope", "Gentle Slope", "Pipe", "Clear Pipe", "Spike Block", "Semisolid Platform"],
                    ["Block", "? Block", "Hard Block", "Hidden Block", "Donut Block", "Note Block", "Cloud Block", "Ice Block"]
                ],
                "Items": [
                    ["Coin", "10-Coin", "Pink Coin", "Super Mushroom", "Super Bell", "Fire Flower", "Super Star", "1-Up Mushroom"]
                ],
                "Enemies": [
                    ["Goomba", "Koopa Troopa", "Ant Trooper", "Spiny", "Spiny", "Blooper", "Cheep Cheep"],
                    ["Skipsqueak", "Stingby", "Piranha Plant", "Pirahna Creeper", "Thwomp", "Hammer Bro", "Hop-Chops"],
                    ["Boo", "Lava Bubble", "Bob-omb", "Dry Bones", "Fish Bone", "Magikoopa"],
                    ["Meowser", "Boom Boom", "Charvaargh", "Bully", "Porcupuffer", "Koopa Troopa Car"]
                ],
                "Gizmos": [
                    ["Bill Blaster", "Banzai Bill", "Icicle", "Twister", "ON/OFF Switch", "Conveyor Belt", "Crate"],
                    ["Key", "Warp Door", "Warp Box", "P Switch", "POW Block", "Trampoline", "Arrow Sign", "Checkpoint Flag"],
                    ["Cloud Lift", "! Block", "Snake Block", "Blinking Block", "Track Block", "Tree", "Mushroom Trampoline"]
                ]
            }
        }

        self.categories = self.styles[self.style]

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

class GridPoint:
    # uses 1-based indexing
    def __init__(self, x_ind, y_ind):
        self.x = int(x_ind * 915 / 24 - 915 / 48)
        self.y = int(y_ind * 495 / 14 - 495 / 28 + 78)

# TODO refactor into a module maybe
# Before initializing this class: have the emulator started, the game loaded, and have clicked "make game"
class AutomationManager(ABC):
    def __init__(self, x, y, width, height, style, dvorak=False):
        self.win_x = x
        self.win_y = y
        self.win_width = width
        self.win_height = height

        self.object_manager = ObjectManager(style)
        self.current_object = ""
        self.last_inserted_object = None  # Track last inserted object

        self._activate()
        self._resize_and_move(x, y, width, height)

    # Focus the emulator
    @abstractmethod
    def _activate(self):
        pass

    # Resize the emulator to width w and height h, and move it to coords (x,y)
    @abstractmethod
    def _resize_and_move(self, x, y, w, h):
        pass

    # Simulate a click at screen coordinates (x,y), for a given duration in milliseconds
    @abstractmethod
    def _click(self, x, y, duration = 100):
        pass

    # Simulate a keypress for a given duration in milliseconds
    @abstractmethod
    def _keystroke(self, key, duration = 100):
        pass

    def reset(self):
        self._click(875, 530, 3000)
        time.sleep(3)

    def _click_point(self, point, duration = 100):
        self._click(point.x, point.y, duration)

    def obstructed_by_menu(self, grid_point):
        return grid_point.x < 5 or grid_point.x > 22 or grid_point.y < 4

    def select_object(self, object_name):
        if object_name == self.last_inserted_object:
            return

        try:
            obj = self.object_manager.get_object(object_name)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            return

        self._keystroke(Keys.D_UP)
        self._keystroke(Keys.Y_BTN)
        time.sleep(0.5)

        current_list = self.object_manager.current_list
        delta = obj.list_index - current_list
        key = Keys.R if delta > 0 else Keys.L
        for _ in range(abs(delta)):
            self._keystroke(key)

        current_item = self.object_manager.list_indices[obj.list_index]
        delta = obj.index - current_item
        key = Keys.D_RIGHT if delta > 0 else Keys.D_LEFT
        for _ in range(abs(delta)):
            self._keystroke(key)

        self._keystroke(Keys.A_BTN)
        time.sleep(0.2)

        self.object_manager.update_selection(obj.list_index, obj.index)

    def place_object(self, object_name, grid_point):
        self.select_object(object_name)
        self.last_inserted_object = object_name
        obstructed = self.obstructed_by_menu(grid_point)

        if obstructed:
            self._keystroke(Keys.X_BTN)
            time.sleep(0.2)

        self._click_point(grid_point)
        time.sleep(0.2)

        if obstructed:
            self._keystroke(Keys.X_BTN)
            time.sleep(0.2)

    def shorten_track(self):
        self._keystroke(Keys.D_DOWN)
        time.sleep(0.3)
        self._keystroke(Keys.D_RIGHT)
        time.sleep(0.3)
        self._keystroke(Keys.D_RIGHT)
        time.sleep(0.3)
        self._keystroke(Keys.A_BTN)
        time.sleep(0.3)
        self._click(500, 500)
        self._click(550, 520, 4_000) # make track shorter
        self._click(500, 500) # restore focus

        # for i in range(20):
        #     self._click(550, 520)
        #     time.sleep(0.1)

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

    def _click(self, x, y, duration = 100):
        subprocess.run(["./sim", "click", str(x + self.win_x), str(y + self.win_y), str(duration)])

    def _keystroke(self, key, duration = 100):
        subprocess.run(["./sim", "keystroke", str(key), str(duration)])

def get_automation_manager(x, y, width, height, style, dvorak=False):
    if sys.platform == "darwin":
        return MacOSAutomationManager(x, y, width, height, style, dvorak=dvorak)
    else:
        raise NotImplementedError(f"Unsupported platform '{sys.platform}'")

def main():
    am = get_automation_manager(100, 100, 915, 600, "Super Mario Bros")
    am.reset()
    am.shorten_track()
    time.sleep(0.1)

    with open("x.json") as f:
        data = json.load(f)

    for unit in data:
        am.place_object(unit['name'], GridPoint(unit['x'], unit['y']))

if __name__ == "__main__":
    main()

# minimum track grid size is 14 points in height and 24 points in width
# moving the cursor to a (pixel) point less than y=350 will shift the view up. BUT, simply clicking works fine without adjusting the view.
# there is a maximum number of each unit that can be added, differs per unit
# - more fun: the limit applies to groups, so placing a bunch of one unit limits the number of other units
# cannot place any units in the southwest corner (7 width, 5 height), or in the southeast corner (10 width, 2 height)
# it appears to be possible to cover the flagpole with units, but a bad idea
# want to trigger the reset button before we start adding things, IF the game prepopulates anything. I'm not certain if it does.
# bug: if the object in the square below protrudes into the square above (e.g. Koopa Troopa), clicking on the protruding part will fail to register as a click in the above square