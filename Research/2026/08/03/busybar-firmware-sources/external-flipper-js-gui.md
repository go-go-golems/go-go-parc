---
title: "Captured source: External Flipper Js Gui"
source_file: "external-flipper-js-gui.md"
type: source
---

# Captured source: External Flipper Js Gui

Original ticket source file: `external-flipper-js-gui.md`.

Searching...

No Matches

The module allows you to use GUI (graphical user interface) in concepts off the Flipper Zero firmware. Call the `require` function to load the module before first using its methods. This module depends on the `event_loop` module, so it **must** be imported after the `event_loop` import:

let eventLoop = require("event\_loop");

let gui = require("gui");

## Submodules

GUI module has several submodules:

- [Byte input GUI view](https://developer.flipper.net/flipperzero/doxygen/js_gui__byte_input.html) — Keyboard-like hex input
- [Dialog GUI view](https://developer.flipper.net/flipperzero/doxygen/js_gui__dialog.html) — Dialog with up to 3 options
- [Empty Screen GUI view](https://developer.flipper.net/flipperzero/doxygen/js_gui__empty_screen.html) — Just empty screen
- [File Picker GUI prompt](https://developer.flipper.net/flipperzero/doxygen/js_gui__file_picker.html) — Displays a file selection prompt
- [GUI Icons](https://developer.flipper.net/flipperzero/doxygen/js_gui__icon.html) — Retrieves and loads icons for use in GUI
- [Loading GUI view](https://developer.flipper.net/flipperzero/doxygen/js_gui__loading.html) — Displays an animated hourglass icon
- [Submenu GUI view](https://developer.flipper.net/flipperzero/doxygen/js_gui__submenu.html) — Displays a scrollable list of clickable textual entries
- [Text box GUI view](https://developer.flipper.net/flipperzero/doxygen/js_gui__text_box.html) — Simple multiline text box
- [Text input GUI view](https://developer.flipper.net/flipperzero/doxygen/js_gui__text_input.html) — Keyboard-like text input
- [Widget GUI view](https://developer.flipper.net/flipperzero/doxygen/js_gui__widget.html) — Displays a combination of custom elements on one screen

---

## Conceptualizing GUI

## Event loop

It is highly recommended to familiarize yourself with the event loop first before doing GUI-related things.

## Canvas

The canvas is just a drawing area with no abstractions over it. Drawing on the canvas directly (i.e. not through a viewport) is useful in case you want to implement a custom design element, but this is rather uncommon.

## Viewport

A viewport is a window into a rectangular portion of the canvas. Applications always access the canvas through a viewport.

## View

In Flipper's terminology, a "View" is a fullscreen design element that assumes control over the entire viewport and all input events. Different types of views are available:

- `button_menu`
- `button_panel`
- `byte_input`
- `dialog`
- `empty_screen`
- `file_picker`
- `loading`
- `menu`
- `number_input`
- `popup`
- `submenu`
- `text_box`
- `text_input`
- `vi_list`
- `widget`

In JS, each view has its own set of properties (or just "props"). The programmer can manipulate these properties in two ways:

- Instantiate a `View` using the `makeWith(props)` method, passing an object with the initial properties
- Call `set(name, value)` to modify a property of an existing `View`

## View Dispatcher

The view dispatcher holds references to all the views that an application needs and switches between them as the application makes requests to do so.

## Scene Manager

The scene manager is an optional add-on to the view dispatcher that makes managing applications with complex navigation flows easier. It is currently inaccessible from JS.

## Approaches

In total, there are three different approaches that you may take when writing a GUI application:

| Approach | Use cases | Available from JS |
| --- | --- | --- |
| ViewPort only | Accessing the graphics API directly, without any of the nice UI abstractions | ❌ |
| ViewDispatcher | Common UI elements that fit with the overall look of the system | ✅ |
| SceneManager | Additional navigation flow management for complex applications | ❌ |

---

## Example

An example with three different views using the ViewDispatcher approach:

let eventLoop = require("event\_loop");

let gui = require("gui");

let loadingView = require("gui/loading");

let submenuView = require("gui/submenu");

let emptyView = require("gui/empty\_screen");

// Common pattern: declare all the views in an object. This is absolutely not

// required, but adds clarity to the script.

let views = {

// the view dispatcher auto-✨magically✨ remembers views as they are created

loading: loadingView.make(),

empty: emptyView.make(),

demos: submenuView.makeWith({

items: \[

"Hourglass screen",

"Empty screen",

"Exit app",

\],

}),

};

// go to different screens depending on what was selected

if (index === 0) {

gui.viewDispatcher.switchTo(views.loading);

} else if (index === 1) {

gui.viewDispatcher.switchTo(views.empty);

} else if (index === 2) {

eventLoop.stop();

}

}, gui, eventLoop, views);

// go to the demo chooser screen when the back key is pressed

gui.viewDispatcher.switchTo(views.demos);

}, gui, views);

// run UI

gui.viewDispatcher.switchTo(views.demos);

eventLoop.run();

---

## API reference

## viewDispatcher

The `viewDispatcher` constant holds the `ViewDispatcher` singleton.

### viewDispatcher.switchTo(view)

Switches to a view, giving it control over the display and input.

**Parameters**

- `view`: the `View` to switch to

### viewDispatcher.sendTo(direction)

Sends the viewport that the dispatcher manages to the front of the stackup (effectively making it visible), or to the back (effectively making it invisible).

**Parameters**

- `direction`: either `"front"` or `"back"`

### viewDispatcher.sendCustom(event)

Sends a custom number to the `custom` event handler.

**Parameters**

- `event`: number to send

### viewDispatcher.custom

An event loop `Contract` object that identifies the custom event source, triggered by `ViewDispatcher.sendCustom(event)`.

### viewDispatcher.navigation

An event loop `Contract` object that identifies the navigation event source, triggered when the back key is pressed.

### viewDispatcher.currentView

The `View` object currently being shown.

## ViewFactory

When you import a module implementing a view, a `ViewFactory` is instantiated. For example, in the example above, `loadingView`, `submenuView` and `emptyView` are view factories.

### ViewFactory.make()

Creates an instance of a `View`.

### ViewFactory.makeWith(props, children)

Creates an instance of a `View` and assigns initial properties from `props` and optionally a list of children.

**Parameters**

- `props`: simple key-value object, e.g. `{ header: "Header" }`
- `children`: optional array of children, e.g. `[ { element: "button", button: "right", text: "Back" } ]`

## View

When you call `ViewFactory.make()` or `ViewFactory.makeWith()`, a `View` is instantiated. For example, in the example above, `views.loading`, `views.demos` and `views.empty` are views.

### View.set(property, value)

Assign value to property by name.

**Parameters**

- `property`: name of the property to change
- `value`: value to assign to the property

### View.addChild(child)

Adds a child to the `View`.

**Parameters**

- `child`: the child to add, e.g. `{ element: "button", button: "right", text: "Back" }`

The format of the `child` parameter depends on the type of View that you're working with. Look in the View documentation.

### View.resetChildren()

Removes all children from the `View`.

### View.setChildren(children)

Removes all previous children from the `View` and assigns new children.

**Parameters**

- `children`: the array of new children, e.g. `[ { element: "button", button: "right", text: "Back" } ]`
