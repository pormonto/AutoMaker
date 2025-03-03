import CoreGraphics

enum EventError: Error {
    case createFailed
}

func click(at position: CGPoint) throws {
    let source = CGEventSource(stateID: .hidSystemState)

    let mouseMove = CGEvent(mouseEventSource: source, mouseType: .mouseMoved,
        mouseCursorPosition: position, mouseButton: .left)
    let mouseDown = CGEvent(mouseEventSource: source, mouseType: .leftMouseDown,
        mouseCursorPosition: position, mouseButton: .left)
    let mouseUp = CGEvent(mouseEventSource: source, mouseType: .leftMouseUp,
        mouseCursorPosition: position, mouseButton: .left)

    guard let mouseMove = mouseMove, let mouseDown = mouseDown, let mouseUp = mouseUp else {
        throw EventError.createFailed
    }

    mouseMove.post(tap: .cghidEventTap)
    mouseDown.post(tap: .cghidEventTap)
    usleep(100_000) // 100ms
    mouseUp.post(tap: .cghidEventTap)
}

func keystroke(code: CGKeyCode) throws {
    let source = CGEventSource(stateID: .hidSystemState)

    let keyDown = CGEvent(keyboardEventSource: source, virtualKey: code, keyDown: true)
    let keyUp = CGEvent(keyboardEventSource: source, virtualKey: code, keyDown: false)

    guard let keyDown = keyDown, let keyUp = keyUp else {
        throw EventError.createFailed
    }

    keyDown.post(tap: .cghidEventTap)
    usleep(100_000) // 100ms
    keyUp.post(tap: .cghidEventTap)
}

func clickMain() {
    let arguments = CommandLine.arguments

    guard arguments.count == 4 else {
        print("Usage: ./sim click x y")
        exit(1)
    }

    guard let xCoord = Int(arguments[2]), let yCoord = Int(arguments[3]) else {
        print("Error: x and y must be integers")
        exit(1)
    }

    do {
        try click(at: CGPoint(x: xCoord, y: yCoord))
    } catch {
        print("Error: \(error)")
        exit(1)
    }
}

func keystrokeMain() {
    let arguments = CommandLine.arguments

    guard arguments.count == 3 else {
        print("Usage: ./sim keystroke keycode")
        exit(1)
    }

    guard let keycode = UInt16(arguments[2]) else {
        print("Invalid keycode '\(arguments[2])'")
        exit(1)
    }

    do {
        try keystroke(code: keycode)
    } catch {
        print("Error: \(error)")
        exit(1)
    }
}

func main() {
    let arguments = CommandLine.arguments

    guard arguments.count > 1 else {
        print("Usage: ./sim action [args]")
        exit(1)
    }

    switch arguments[1] {
    case "click":
        clickMain()
    case "keystroke":
        keystrokeMain()
    default:
        print("Invalid action '\(arguments[1])'. Known actions are 'click', 'keystroke'.")
        exit(1)
    }
}

main()