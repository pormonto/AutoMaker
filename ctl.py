import subprocess
import time

def script(code):
    subprocess.run(["osascript", "-e", code])

def activate():
    script('tell application "Ryujinx" to activate')

def tell_ryujinx(*cmds):
    code = '\n'.join(cmds)
    script(f'tell application "System Events" to tell process "Ryujinx"\n{code}\nend tell')

def resize_and_move(x, y, w, h):
    tell_ryujinx(
        f"set position of window 1 to {{{x}, {y}}}",
        f"set size of window 1 to {{{w}, {h}}}"
    )

def click(x, y):
    subprocess.run(["./click", str(x), str(y)])

def main():
    x, y, w, h = 100, 100, 915, 600

    resize_and_move(x, y, w, h)
    activate()
    time.sleep(0.2)

    click(210, 210)
    click(769, 535)

    click(210, 210)
    click(618, 461)

if __name__ == "__main__":
    main()