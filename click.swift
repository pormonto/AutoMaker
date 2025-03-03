import Cocoa

class AppController {
    func clickInEmulator(at position: CGPoint) {
        let source = CGEventSource(stateID: .hidSystemState)

        // Move mouse to position first
        let mouseMove = CGEvent(mouseEventSource: source, mouseType: .mouseMoved,
                               mouseCursorPosition: position, mouseButton: .left)

        // Create events
        let mouseDown = CGEvent(mouseEventSource: source, mouseType: .leftMouseDown,
                               mouseCursorPosition: position, mouseButton: .left)
        let mouseUp = CGEvent(mouseEventSource: source, mouseType: .leftMouseUp,
                             mouseCursorPosition: position, mouseButton: .left)

        // First ensure mouse is at position
        mouseMove?.post(tap: .cghidEventTap)

        mouseDown?.post(tap: .cghidEventTap)
        usleep(100000) // 100ms
        mouseUp?.post(tap: .cghidEventTap)
    }
}

let arguments = CommandLine.arguments

guard arguments.count == 3 else {
    print("Usage: swift click.swift x y")
    exit(1)
}

guard let xCoord = Int(arguments[1]), let yCoord = Int(arguments[2]) else {
    print("Error: x and y must be integers")
    exit(1)
}

// Create controller and perform click
let controller = AppController()
controller.clickInEmulator(at: CGPoint(x: xCoord, y: yCoord))