---
title: "Captured source: External Flipper Gui Framework"
source_file: "external-flipper-gui-framework.md"
type: source
---

# Captured source: External Flipper Gui Framework

Original ticket source file: `external-flipper-gui-framework.md`.

[DeepWiki](https://deepwiki.com/)

- [Introduction to Flipper Zero Firmware](https://deepwiki.com/flipperdevices/flipperzero-firmware/1-introduction-to-flipper-zero-firmware)
- [System Architecture](https://deepwiki.com/flipperdevices/flipperzero-firmware/2-system-architecture)
- [Furi Core OS](https://deepwiki.com/flipperdevices/flipperzero-firmware/2.1-furi-core-os)
- [Hardware Abstraction Layer](https://deepwiki.com/flipperdevices/flipperzero-firmware/2.2-hardware-abstraction-layer)
- [Communication System](https://deepwiki.com/flipperdevices/flipperzero-firmware/2.3-communication-system)
- [GUI Framework](https://deepwiki.com/flipperdevices/flipperzero-firmware/2.4-gui-framework)
- [Development Environment](https://deepwiki.com/flipperdevices/flipperzero-firmware/3-development-environment)
- [Build System](https://deepwiki.com/flipperdevices/flipperzero-firmware/3.1-build-system)
- [CI/CD Pipeline](https://deepwiki.com/flipperdevices/flipperzero-firmware/3.2-cicd-pipeline)
- [IDE and Tooling Setup](https://deepwiki.com/flipperdevices/flipperzero-firmware/3.3-ide-and-tooling-setup)
- [Core Services](https://deepwiki.com/flipperdevices/flipperzero-firmware/4-core-services)
- [Desktop Service](https://deepwiki.com/flipperdevices/flipperzero-firmware/4.1-desktop-service)
- [Power Management](https://deepwiki.com/flipperdevices/flipperzero-firmware/4.2-power-management)
- [Storage Service](https://deepwiki.com/flipperdevices/flipperzero-firmware/4.3-storage-service)
- [Application Loader Service](https://deepwiki.com/flipperdevices/flipperzero-firmware/4.4-application-loader-service)
- [Applications Framework](https://deepwiki.com/flipperdevices/flipperzero-firmware/5-applications-framework)
- [Scene Management](https://deepwiki.com/flipperdevices/flipperzero-firmware/5.1-scene-management)
- [JavaScript Scripting Engine](https://deepwiki.com/flipperdevices/flipperzero-firmware/5.2-javascript-scripting-engine)
- [Protocol Implementations](https://deepwiki.com/flipperdevices/flipperzero-firmware/6-protocol-implementations)
- [SubGHz System](https://deepwiki.com/flipperdevices/flipperzero-firmware/6.1-subghz-system)
- [NFC Implementation](https://deepwiki.com/flipperdevices/flipperzero-firmware/6.2-nfc-implementation)
- [Infrared System](https://deepwiki.com/flipperdevices/flipperzero-firmware/6.3-infrared-system)
- [LFRFID System](https://deepwiki.com/flipperdevices/flipperzero-firmware/6.4-lfrfid-system)
- [Bad USB Implementation](https://deepwiki.com/flipperdevices/flipperzero-firmware/6.5-bad-usb-implementation)
- [iButton System](https://deepwiki.com/flipperdevices/flipperzero-firmware/6.6-ibutton-system)
- [Dolphin System](https://deepwiki.com/flipperdevices/flipperzero-firmware/7-dolphin-system)
- [Glossary](https://deepwiki.com/flipperdevices/flipperzero-firmware/8-glossary)

## GUI Framework

Relevant source files
- [applications/debug/direct\_draw/application.fam](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/applications/debug/direct_draw/application.fam)
- [applications/debug/display\_test/view\_display\_test.c](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/applications/debug/display_test/view_display_test.c)
- [applications/debug/lfrfid\_debug/scenes/lfrfid\_debug\_app\_scene\_tune.c](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/applications/debug/lfrfid_debug/scenes/lfrfid_debug_app_scene_tune.c)
- [applications/debug/lfrfid\_debug/views/lfrfid\_debug\_view\_tune.c](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/applications/debug/lfrfid_debug/views/lfrfid_debug_view_tune.c)
- [applications/debug/lfrfid\_debug/views/lfrfid\_debug\_view\_tune.h](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/applications/debug/lfrfid_debug/views/lfrfid_debug_view_tune.h)
- [applications/debug/unit\_tests/tests/furi/furi\_errno\_test.c](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/applications/debug/unit_tests/tests/furi/furi_errno_test.c)
- [applications/debug/unit\_tests/tests/furi/furi\_event\_loop\_test.c](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/applications/debug/unit_tests/tests/furi/furi_event_loop_test.c)
- [applications/debug/unit\_tests/tests/furi/furi\_primitives\_test.c](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/applications/debug/unit_tests/tests/furi/furi_primitives_test.c)
- [applications/debug/unit\_tests/tests/furi/furi\_test.c](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/applications/debug/unit_tests/tests/furi/furi_test.c)
- [applications/examples/example\_date\_time\_input/ReadMe.md](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/applications/examples/example_date_time_input/ReadMe.md?plain=1)
- [applications/examples/example\_date\_time\_input/application.fam](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/applications/examples/example_date_time_input/application.fam)
- [applications/examples/example\_date\_time\_input/example\_date\_time\_input.c](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/applications/examples/example_date_time_input/example_date_time_input.c)
- [applications/examples/example\_date\_time\_input/example\_date\_time\_input.h](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/applications/examples/example_date_time_input/example_date_time_input.h)
- [applications/examples/example\_date\_time\_input/scenes/example\_date\_time\_input\_scene.c](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/applications/examples/example_date_time_input/scenes/example_date_time_input_scene.c)
- [applications/examples/example\_date\_time\_input/scenes/example\_date\_time\_input\_scene.h](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/applications/examples/example_date_time_input/scenes/example_date_time_input_scene.h)
- [applications/examples/example\_date\_time\_input/scenes/example\_date\_time\_input\_scene\_config.h](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/applications/examples/example_date_time_input/scenes/example_date_time_input_scene_config.h)
- [applications/examples/example\_date\_time\_input/scenes/example\_date\_time\_input\_scene\_input\_date\_time.c](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/applications/examples/example_date_time_input/scenes/example_date_time_input_scene_input_date_time.c)
- [applications/examples/example\_date\_time\_input/scenes/example\_date\_time\_input\_scene\_show\_date\_time.c](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/applications/examples/example_date_time_input/scenes/example_date_time_input_scene_show_date_time.c)
- [applications/examples/example\_event\_loop/application.fam](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/applications/examples/example_event_loop/application.fam)
- [applications/examples/example\_event\_loop/example\_event\_loop\_event\_flags.c](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/applications/examples/example_event_loop/example_event_loop_event_flags.c)
- [applications/examples/example\_event\_loop/example\_event\_loop\_multi.c](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/applications/examples/example_event_loop/example_event_loop_multi.c)
- [applications/examples/example\_event\_loop/example\_event\_loop\_mutex.c](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/applications/examples/example_event_loop/example_event_loop_mutex.c)
- [applications/examples/example\_event\_loop/example\_event\_loop\_stream\_buffer.c](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/applications/examples/example_event_loop/example_event_loop_stream_buffer.c)
- [applications/examples/example\_number\_input/scenes/example\_number\_input\_scene\_show\_number.c](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/applications/examples/example_number_input/scenes/example_number_input_scene_show_number.c)
- [applications/main/archive/helpers/archive\_browser.c](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/applications/main/archive/helpers/archive_browser.c)
- [applications/main/archive/helpers/archive\_browser.h](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/applications/main/archive/helpers/archive_browser.h)
- [applications/main/archive/helpers/archive\_files.c](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/applications/main/archive/helpers/archive_files.c)
- [applications/main/archive/helpers/archive\_files.h](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/applications/main/archive/helpers/archive_files.h)
- [applications/main/archive/views/archive\_browser\_view.c](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/applications/main/archive/views/archive_browser_view.c)
- [applications/main/archive/views/archive\_browser\_view.h](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/applications/main/archive/views/archive_browser_view.h)
- [applications/main/gpio/gpio\_items.c](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/applications/main/gpio/gpio_items.c)
- [applications/main/lfrfid/scenes/lfrfid\_scene\_save\_type.c](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/applications/main/lfrfid/scenes/lfrfid_scene_save_type.c)
- [applications/main/nfc/scenes/nfc\_scene\_mf\_classic\_keys\_list.c](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/applications/main/nfc/scenes/nfc_scene_mf_classic_keys_list.c)
- [applications/main/nfc/scenes/nfc\_scene\_mf\_desfire\_app.c](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/applications/main/nfc/scenes/nfc_scene_mf_desfire_app.c)
- [applications/main/u2f/views/u2f\_view.c](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/applications/main/u2f/views/u2f_view.c)
- [applications/services/bt/bt\_cli.c](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/applications/services/bt/bt_cli.c)
- [applications/services/cli/cli\_command\_gpio.c](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/applications/services/cli/cli_command_gpio.c)
- [applications/services/desktop/views/desktop\_view\_slideshow.c](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/applications/services/desktop/views/desktop_view_slideshow.c)
- [applications/services/dialogs/dialogs.c](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/applications/services/dialogs/dialogs.c)
- [applications/services/dialogs/dialogs.h](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/applications/services/dialogs/dialogs.h)
- [applications/services/dialogs/dialogs\_api.c](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/applications/services/dialogs/dialogs_api.c)
- [applications/services/dialogs/dialogs\_message.h](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/applications/services/dialogs/dialogs_message.h)
- [applications/services/dialogs/dialogs\_module\_file\_browser.c](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/applications/services/dialogs/dialogs_module_file_browser.c)
- [applications/services/gui/application.fam](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/applications/services/gui/application.fam)
- [applications/services/gui/canvas.c](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/applications/services/gui/canvas.c)
- [applications/services/gui/canvas.h](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/applications/services/gui/canvas.h)
- [applications/services/gui/canvas\_i.h](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/applications/services/gui/canvas_i.h)
- [applications/services/gui/elements.c](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/applications/services/gui/elements.c)
- [applications/services/gui/elements.h](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/applications/services/gui/elements.h)
- [applications/services/gui/gui.c](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/applications/services/gui/gui.c)
- [applications/services/gui/gui.h](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/applications/services/gui/gui.h)
- [applications/services/gui/gui\_i.h](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/applications/services/gui/gui_i.h)
- [applications/services/gui/modules/button\_menu.c](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/applications/services/gui/modules/button_menu.c)
- [applications/services/gui/modules/byte\_input.c](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/applications/services/gui/modules/byte_input.c)
- [applications/services/gui/modules/date\_time\_input.c](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/applications/services/gui/modules/date_time_input.c)
- [applications/services/gui/modules/dialog\_ex.c](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/applications/services/gui/modules/dialog_ex.c)
- [applications/services/gui/modules/file\_browser.c](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/applications/services/gui/modules/file_browser.c)
- [applications/services/gui/modules/file\_browser.h](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/applications/services/gui/modules/file_browser.h)
- [applications/services/gui/modules/file\_browser\_worker.c](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/applications/services/gui/modules/file_browser_worker.c)
- [applications/services/gui/modules/file\_browser\_worker.h](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/applications/services/gui/modules/file_browser_worker.h)
- [applications/services/gui/modules/menu.c](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/applications/services/gui/modules/menu.c)
- [applications/services/gui/modules/popup.c](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/applications/services/gui/modules/popup.c)
- [applications/services/gui/modules/submenu.c](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/applications/services/gui/modules/submenu.c)
- [applications/services/gui/modules/text\_input.c](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/applications/services/gui/modules/text_input.c)
- [applications/services/gui/modules/variable\_item\_list.c](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/applications/services/gui/modules/variable_item_list.c)
- [applications/services/gui/modules/variable\_item\_list.h](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/applications/services/gui/modules/variable_item_list.h)
- [applications/services/gui/scene\_manager\_i.h](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/applications/services/gui/scene_manager_i.h)
- [applications/services/gui/view.c](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/applications/services/gui/view.c)
- [applications/services/gui/view.h](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/applications/services/gui/view.h)
- [applications/services/gui/view\_dispatcher.c](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/applications/services/gui/view_dispatcher.c)
- [applications/services/gui/view\_dispatcher.h](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/applications/services/gui/view_dispatcher.h)
- [applications/services/gui/view\_dispatcher\_i.h](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/applications/services/gui/view_dispatcher_i.h)
- [applications/services/gui/view\_i.h](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/applications/services/gui/view_i.h)
- [applications/services/gui/view\_port.c](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/applications/services/gui/view_port.c)
- [applications/services/gui/view\_port.h](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/applications/services/gui/view_port.h)
- [applications/services/gui/view\_port\_i.h](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/applications/services/gui/view_port_i.h)
- [applications/services/input/input.c](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/applications/services/input/input.c)
- [applications/services/input/input.h](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/applications/services/input/input.h)
- [applications/services/input/input\_cli.c](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/applications/services/input/input_cli.c)
- [applications/services/rpc/rpc.h](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/applications/services/rpc/rpc.h)
- [applications/services/rpc/rpc\_cli.c](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/applications/services/rpc/rpc_cli.c)
- [applications/settings/desktop\_settings/views/desktop\_settings\_view\_pin\_setup\_howto.c](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/applications/settings/desktop_settings/views/desktop_settings_view_pin_setup_howto.c)
- [applications/settings/desktop\_settings/views/desktop\_settings\_view\_pin\_setup\_howto2.c](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/applications/settings/desktop_settings/views/desktop_settings_view_pin_setup_howto2.c)
- [applications/settings/system/system\_settings.c](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/applications/settings/system/system_settings.c)
- [assets/icons/Common/Hashmark\_7x7.png](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/assets/icons/Common/Hashmark_7x7.png)
- [assets/icons/Common/More\_data\_placeholder\_5x7.png](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/assets/icons/Common/More_data_placeholder_5x7.png)
- [assets/icons/Common/arrow\_nano\_down.png](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/assets/icons/Common/arrow_nano_down.png)
- [assets/icons/Common/arrow\_nano\_up.png](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/assets/icons/Common/arrow_nano_up.png)
- [assets/icons/StatusBar/Rpc\_active\_7x8.png](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/assets/icons/StatusBar/Rpc_active_7x8.png)
- [furi/core/base.h](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/furi/core/base.h)
- [furi/core/event\_loop.c](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/furi/core/event_loop.c)
- [furi/core/event\_loop.h](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/furi/core/event_loop.h)
- [furi/core/event\_loop\_i.h](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/furi/core/event_loop_i.h)
- [furi/core/thread\_i.h](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/furi/core/thread_i.h)
- [lib/digital\_signal/digital\_sequence.c](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/lib/digital_signal/digital_sequence.c)
- [lib/digital\_signal/digital\_signal\_i.h](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/lib/digital_signal/digital_signal_i.h)
- [lib/print/printf\_tiny.c](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/lib/print/printf_tiny.c)
- [lib/toolbox/buffer\_stream.c](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/lib/toolbox/buffer_stream.c)
- [lib/toolbox/protocols/protocol\_dict.c](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/lib/toolbox/protocols/protocol_dict.c)
- [lib/toolbox/protocols/protocol\_dict.h](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/lib/toolbox/protocols/protocol_dict.h)
- [lib/u8g2/u8g2.h](https://github.com/flipperdevices/flipperzero-firmware/blob/5dc71870/lib/u8g2/u8g2.h)

The Flipper Zero GUI framework is a multi-layered system designed to manage concurrent display access, user input routing, and complex UI state transitions. It abstracts the underlying monochrome LCD hardware and provides a high-level API for creating responsive applications.

## GUI Service and Architecture

The GUI Service is the central authority for screen access. It manages multiple instances across different layers (StatusBar, Window, Fullscreen) and coordinates the rendering process using a object.

### Code Entity Relationship

The following diagram illustrates the relationship between the central GUI service and the components that applications interact with.

**GUI System Component Map**

**Sources:**,,

## Canvas Rendering

The is the primary drawing interface. It provides a wrapper around the library, adding support for Flipper-specific features like compressed icons and animations.

- **Initialization**: The canvas is initialized with a framebuffer and a mutex to ensure thread-safe drawing.
- **Coordinate System**: Drawing functions accept and coordinates, which are adjusted by the current offsets.
- **Fonts**: The system supports several built-in fonts:,,, and.
- **Commit**: The function sends the buffer to the display via and triggers registered framebuffer callbacks.

**Sources:**,,

## ViewPort

A represents a rectangular area of the screen that an application can draw on. It acts as the bridge between an application's drawing logic and the GUI service.

- **Callbacks**: Applications provide a to render content and an to handle button presses.
- **Layers**: ViewPorts are assigned to specific layers (e.g., or ). The GUI service iterates through these layers to compose the final image.

**Sources:**,

## ViewDispatcher

The is a high-level manager that handles multiple objects. It simplifies application development by providing:

1. **View Switching**: manages the lifecycle of entering and exiting different UI screens.
2. **Event Loop**: It uses to process input and custom events in a dedicated thread.
3. **Input Routing**: It intercepts raw data and routes it to the currently active.

**Sources:**,

## UI Flow Data Path

This diagram shows how a physical button press reaches the application logic.

**Input and Rendering Data Flow**

**Sources:**,,

## Reusable UI Modules

The framework includes a library of standardized modules to ensure a consistent look and feel across the firmware.

| Module | Description | Key Functions |
| --- | --- | --- |
| **Menu** | A vertical list of items with icons. | , |
| **DialogEx** | A flexible dialog with header, text, and button icons. | , |
| **TextInput** | On-screen QWERTY/numeric keyboard. |  |
| **FileBrowser** | Navigates the SD card/Internal storage. | , |
| **Submenu** | A simple vertical list of text options. |  |
| **VariableItemList** | List items with selectable values (e.g., ON/OFF). |  |

### Elements Library

The file provides low-level drawing primitives for common UI components like:

- **Progress Bars**:.
- **Scrollbars**:.
- **Buttons**: Standardized prompts for Left/Right/Up/Down buttons.

**Sources:**,,
