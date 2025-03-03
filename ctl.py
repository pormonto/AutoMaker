import argparse
import subprocess
import sys
import time
from abc import ABC, abstractmethod

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
        time.sleep(0.4) # minimum time that seems to work

    def keystroke(self, key):
        subprocess.run(["./sim", "keystroke", str(key)])
        # time.sleep(0.1)

    # TODO define a map of objects' positions
    def select_object(self, object):
        search_btn = (880, 110)
        next_btn = (760, 360)
        prev_btn = (160, 360)

        self.click(*search_btn)
        self.click(*next_btn)
        self.click(540, 440) # random item

        self.click(550, 250) # random square on grid

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

    am.select_object("foo")

if __name__ == "__main__":
    main()