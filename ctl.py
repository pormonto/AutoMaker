import subprocess
import sys
import time
from abc import ABC, abstractmethod

class AutomationManager(ABC):
    def __init__(self, x, y, width, height):
        self.win_x = x
        self.win_y = y
        self.win_width = width
        self.win_height = height

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

class MacOSAutomationManager(AutomationManager):
    def _script(self, code):
        subprocess.run(["osascript", "-e", code])

    def _activate(self):
        self._script('tell application "Ryujinx" to activate')

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
        subprocess.run(["./click", str(x + self.win_x), str(y + self.win_y)])

def get_automation_manager(x, y, width, height):
    if sys.platform == "darwin":
        return MacOSAutomationManager(x, y, width, height)
    else:
        raise NotImplementedError(f"Unsupported platform '{sys.platform}'")

def main():
    am = get_automation_manager(100, 100, 915, 600)

    am.click(110, 110)
    am.click(669, 435)

    am.click(110, 110)
    am.click(518, 361)

if __name__ == "__main__":
    main()