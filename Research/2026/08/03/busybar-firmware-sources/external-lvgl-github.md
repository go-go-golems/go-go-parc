---
title: "Captured source: External Lvgl Github"
source_file: "external-lvgl-github.md"
type: source
---

# Captured source: External Lvgl Github

Original ticket source file: `external-lvgl-github.md`.

[Docs](https://lvgl.io/docs "Documentation") • [Forum](https://forum.lvgl.io/ "Community forum") • [Blog](https://blog.lvgl.io/ "News and articles") • [Services](https://lvgl.io/services "Professional services") **EN** • [中文](https://github.com/lvgl/lvgl/blob/master/docs/README_zh.md) • [日本語](https://github.com/lvgl/lvgl/blob/master/docs/README_ja.md) • [한국어](https://github.com/lvgl/lvgl/blob/master/docs/README_ko.md) • [PT](https://github.com/lvgl/lvgl/blob/master/docs/README_pt_BR.md) • [עברית](https://github.com/lvgl/lvgl/blob/master/docs/README_he.md)

[![](https://camo.githubusercontent.com/683e5c40d265b2bc59a5261e271d121a027db68a37a4675e244f14962496b2c7/68747470733a2f2f6c76676c2e696f2f6769746875622d6173736574732f6c6f676f2d636f6c6f7265642e706e67)](https://lvgl.io/)

## Light and Versatile Graphics Library

[![Ebike demo with vector graphics](https://private-user-images.githubusercontent.com/7599318/626076378-965e8b8b-d240-45ed-9744-bdd81785967d.gif?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3ODU3OTE3ODIsIm5iZiI6MTc4NTc5MTQ4MiwicGF0aCI6Ii83NTk5MzE4LzYyNjA3NjM3OC05NjVlOGI4Yi1kMjQwLTQ1ZWQtOTc0NC1iZGQ4MTc4NTk2N2QuZ2lmP1gtQW16LUFsZ29yaXRobT1BV1M0LUhNQUMtU0hBMjU2JlgtQW16LUNyZWRlbnRpYWw9QUtJQVZDT0RZTFNBNTNQUUs0WkElMkYyMDI2MDgwMyUyRnVzLWVhc3QtMSUyRnMzJTJGYXdzNF9yZXF1ZXN0JlgtQW16LURhdGU9MjAyNjA4MDNUMjExMTIyWiZYLUFtei1FeHBpcmVzPTMwMCZYLUFtei1TaWduYXR1cmU9NzkyZGI2YmJkNWU1MjEzYmRjZWM1ODA3MzIzNjRlMjQxMmFkODEwNGRmMDAyYjFmYWM0MWRjNmUzMTIxYjAxNiZYLUFtei1TaWduZWRIZWFkZXJzPWhvc3QmcmVzcG9uc2UtY29udGVudC10eXBlPWltYWdlJTJGZ2lmIn0.nJyCMXm9LIOeGzpWv7QJkTyavcfl3rDTNwXbYGbTSHs)](https://private-user-images.githubusercontent.com/7599318/626076378-965e8b8b-d240-45ed-9744-bdd81785967d.gif?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3ODU3OTE3ODIsIm5iZiI6MTc4NTc5MTQ4MiwicGF0aCI6Ii83NTk5MzE4LzYyNjA3NjM3OC05NjVlOGI4Yi1kMjQwLTQ1ZWQtOTc0NC1iZGQ4MTc4NTk2N2QuZ2lmP1gtQW16LUFsZ29yaXRobT1BV1M0LUhNQUMtU0hBMjU2JlgtQW16LUNyZWRlbnRpYWw9QUtJQVZDT0RZTFNBNTNQUUs0WkElMkYyMDI2MDgwMyUyRnVzLWVhc3QtMSUyRnMzJTJGYXdzNF9yZXF1ZXN0JlgtQW16LURhdGU9MjAyNjA4MDNUMjExMTIyWiZYLUFtei1FeHBpcmVzPTMwMCZYLUFtei1TaWduYXR1cmU9NzkyZGI2YmJkNWU1MjEzYmRjZWM1ODA3MzIzNjRlMjQxMmFkODEwNGRmMDAyYjFmYWM0MWRjNmUzMTIxYjAxNiZYLUFtei1TaWduZWRIZWFkZXJzPWhvc3QmcmVzcG9uc2UtY29udGVudC10eXBlPWltYWdlJTJGZ2lmIn0.nJyCMXm9LIOeGzpWv7QJkTyavcfl3rDTNwXbYGbTSHs) [![ECG demo with animated 3D model](https://private-user-images.githubusercontent.com/7599318/626076472-d83820ed-5448-494e-94c8-3ca1b4ddceb0.gif?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3ODU3OTE3ODIsIm5iZiI6MTc4NTc5MTQ4MiwicGF0aCI6Ii83NTk5MzE4LzYyNjA3NjQ3Mi1kODM4MjBlZC01NDQ4LTQ5NGUtOTRjOC0zY2ExYjRkZGNlYjAuZ2lmP1gtQW16LUFsZ29yaXRobT1BV1M0LUhNQUMtU0hBMjU2JlgtQW16LUNyZWRlbnRpYWw9QUtJQVZDT0RZTFNBNTNQUUs0WkElMkYyMDI2MDgwMyUyRnVzLWVhc3QtMSUyRnMzJTJGYXdzNF9yZXF1ZXN0JlgtQW16LURhdGU9MjAyNjA4MDNUMjExMTIyWiZYLUFtei1FeHBpcmVzPTMwMCZYLUFtei1TaWduYXR1cmU9ZDU3M2YzNGQ1MTNkMjczMTQ2YTkxNjdiNjRmMDFmZWJjOWEwZTE2NzQ4ZDkxOWIxMTZkYjNjYmU4ZGUwMjI1OSZYLUFtei1TaWduZWRIZWFkZXJzPWhvc3QmcmVzcG9uc2UtY29udGVudC10eXBlPWltYWdlJTJGZ2lmIn0.w83lVcwKjKkYxhSfEYZqifjdnk_tcfiGzrjj6mZXzfs)](https://private-user-images.githubusercontent.com/7599318/626076472-d83820ed-5448-494e-94c8-3ca1b4ddceb0.gif?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3ODU3OTE3ODIsIm5iZiI6MTc4NTc5MTQ4MiwicGF0aCI6Ii83NTk5MzE4LzYyNjA3NjQ3Mi1kODM4MjBlZC01NDQ4LTQ5NGUtOTRjOC0zY2ExYjRkZGNlYjAuZ2lmP1gtQW16LUFsZ29yaXRobT1BV1M0LUhNQUMtU0hBMjU2JlgtQW16LUNyZWRlbnRpYWw9QUtJQVZDT0RZTFNBNTNQUUs0WkElMkYyMDI2MDgwMyUyRnVzLWVhc3QtMSUyRnMzJTJGYXdzNF9yZXF1ZXN0JlgtQW16LURhdGU9MjAyNjA4MDNUMjExMTIyWiZYLUFtei1FeHBpcmVzPTMwMCZYLUFtei1TaWduYXR1cmU9ZDU3M2YzNGQ1MTNkMjczMTQ2YTkxNjdiNjRmMDFmZWJjOWEwZTE2NzQ4ZDkxOWIxMTZkYjNjYmU4ZGUwMjI1OSZYLUFtei1TaWduZWRIZWFkZXJzPWhvc3QmcmVzcG9uc2UtY29udGVudC10eXBlPWltYWdlJTJGZ2lmIn0.w83lVcwKjKkYxhSfEYZqifjdnk_tcfiGzrjj6mZXzfs)

[Overview](#overview "What LVGL is") • [Features](#features "What LVGL can do") • [LVGL Pro](#lvgl-pro "The professional toolchain") • [Examples](#examples "C and XML examples") • [Integration](#integration "How to add LVGL to your project") • [Contributing](#contributing "How to get involved") • [License](#license "Licensing terms")

## Overview

**LVGL** is a free and open-source UI library that enables you to create graphical user interfaces for any MCUs and MPUs from any vendor on any platform.

**Requirements**: LVGL has no external dependencies, which makes it easy to compile for any modern target, from small MCUs to multi-core Linux-based MPUs with 3D support. For a *typical* UI, you need only ~100kB RAM, ~200–300kB flash, and a buffer size of 1/10 of the screen for rendering.

**Wide adoption**: Chip vendors (like NXP, Espressif, Renesas, and so on), RTOS projects (Zephyr, NuttX, etc.), and board manufacturers (Riverdi, Seeed Studio, VIEWE, Elecrow, etc.) have all integrated LVGL already. If a development board has a display, it's very likely the vendor offers LVGL support too.

**Professional tools**: Instead of writing C code, you can hugely speed up and simplify UI development by using [LVGL Pro](#lvgl-pro), a complete toolkit with Editor, Figma integration, Online Viewer, and CLI. It exports pure LVGL C code from XML, with no extra runtime or hidden magic. It's free for non-commercial use and evaluation.

**To get started**, browse the [Examples](#examples), spin up a [Simulator project](https://lvgl.io/docs/open/integration/pc), explore the [Online Viewer](https://viewer.lvgl.io/) of LVGL Pro, compile and run a UI in a window in [LVGL Pro](https://lvgl.io/docs/pro/integration/simulator) with one click, or dive into our AI-ready [Docs](https://lvgl.io/docs/open). Just click [**Ask AI**](https://lvgl.io/docs/open) and ask anything!

## Features

**Free, Portable, and Scalable**

- A fully portable C (C++ compatible) library with no external dependencies.
- Can be compiled for any MCU or MPU, with any (RT)OS. Make, CMake, and simple globbing are all supported.
- Supports monochrome, ePaper, OLED, or TFT displays, or even monitors. [Displays](https://lvgl.io/docs/open/main-modules/display)
- Distributed under the MIT license, so you can easily use it in commercial projects too.
- At a bare minimum needs only 32kB RAM and 128kB Flash, a frame buffer, and at least a 1/10 screen-sized buffer for rendering.
- OS, external memory, and GPU are supported but not required.

**Widgets, Styles, Layouts, and More**

- 30+ built-in [Widgets](https://lvgl.io/docs/open/widgets): Button, Label, Slider, Chart, Keyboard, Meter, Arc, Table, and many more.
- Flexible [Style system](https://lvgl.io/docs/open/common-widget-features/styles) with 100+ style properties to customize any part of the widgets in any state.
- [Flexbox](https://lvgl.io/docs/open/common-widget-features/layouts/flex) and [Grid](https://lvgl.io/docs/open/common-widget-features/layouts/grid) -like layout engines to automatically size and position the widgets responsively.
- [Data bindings](https://lvgl.io/docs/open/main-modules/observer) to easily connect the UI with the application.
- Supports Mouse, Touchpad, Keypad, Keyboard, External buttons, Encoder [Input devices](https://lvgl.io/docs/open/main-modules/indev).
- [Multiple display](https://lvgl.io/docs/open/main-modules/display/overview#how-many-displays-can-lvgl-use) support.

**Rendering**

- Built-in 2D rendering engine supporting basic shapes, gradients, anti-aliasing, opacity, smooth scrolling, box and drop shadows, image transformation, etc.
- [Powerful 3D rendering engine](https://lvgl.io/docs/open/libs/gltf) to show [glTF models](https://sketchfab.com/) with OpenGL.
- Vector graphics, SVG, and Lottie support.
- Text is rendered with UTF-8 encoding, supporting CJK, Thai, Hindi, Arabic, and Persian writing systems.
- Built-in support for GPUs like VG-Lite, Dave2D, NeoChrome, OpenGL, etc.

## LVGL Pro

Building UIs in C works well, but it gets slow to iterate on and harder to keep consistent as a project grows. [LVGL Pro](https://lvgl.io/pro) lets you build reusable components and screens visually, preview changes instantly, and manage data bindings, translations, animations, and tests in one place.

Pro exports plain LVGL C code: the same LVGL you already use, with no extra runtime or dependency. It drops into an existing project without changing how you build or ship.

[![Building a UI in the LVGL Pro editor with live preview](https://private-user-images.githubusercontent.com/7599318/626089632-8cef0f05-0ff1-4766-8dfd-1d15e47f181a.gif?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3ODU3OTE3ODIsIm5iZiI6MTc4NTc5MTQ4MiwicGF0aCI6Ii83NTk5MzE4LzYyNjA4OTYzMi04Y2VmMGYwNS0wZmYxLTQ3NjYtOGRmZC0xZDE1ZTQ3ZjE4MWEuZ2lmP1gtQW16LUFsZ29yaXRobT1BV1M0LUhNQUMtU0hBMjU2JlgtQW16LUNyZWRlbnRpYWw9QUtJQVZDT0RZTFNBNTNQUUs0WkElMkYyMDI2MDgwMyUyRnVzLWVhc3QtMSUyRnMzJTJGYXdzNF9yZXF1ZXN0JlgtQW16LURhdGU9MjAyNjA4MDNUMjExMTIyWiZYLUFtei1FeHBpcmVzPTMwMCZYLUFtei1TaWduYXR1cmU9ZmEyYmE5YTUyZjAzMzRhYTJkM2MyYmU0OWYyZjM5MzQzODgyMmVkMjliOThiZmRkZGU2NWExMzgxNDliM2M0OSZYLUFtei1TaWduZWRIZWFkZXJzPWhvc3QmcmVzcG9uc2UtY29udGVudC10eXBlPWltYWdlJTJGZ2lmIn0.DnulBS38SXDBoO40YGwI8BfrcZt1-LlG7oo_x02lJKI)](https://private-user-images.githubusercontent.com/7599318/626089632-8cef0f05-0ff1-4766-8dfd-1d15e47f181a.gif?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3ODU3OTE3ODIsIm5iZiI6MTc4NTc5MTQ4MiwicGF0aCI6Ii83NTk5MzE4LzYyNjA4OTYzMi04Y2VmMGYwNS0wZmYxLTQ3NjYtOGRmZC0xZDE1ZTQ3ZjE4MWEuZ2lmP1gtQW16LUFsZ29yaXRobT1BV1M0LUhNQUMtU0hBMjU2JlgtQW16LUNyZWRlbnRpYWw9QUtJQVZDT0RZTFNBNTNQUUs0WkElMkYyMDI2MDgwMyUyRnVzLWVhc3QtMSUyRnMzJTJGYXdzNF9yZXF1ZXN0JlgtQW16LURhdGU9MjAyNjA4MDNUMjExMTIyWiZYLUFtei1FeHBpcmVzPTMwMCZYLUFtei1TaWduYXR1cmU9ZmEyYmE5YTUyZjAzMzRhYTJkM2MyYmU0OWYyZjM5MzQzODgyMmVkMjliOThiZmRkZGU2NWExMzgxNDliM2M0OSZYLUFtei1TaWduZWRIZWFkZXJzPWhvc3QmcmVzcG9uc2UtY29udGVudC10eXBlPWltYWdlJTJGZ2lmIn0.DnulBS38SXDBoO40YGwI8BfrcZt1-LlG7oo_x02lJKI)

You can try it in the browser at [viewer.lvgl.io](https://viewer.lvgl.io/) without installing anything, or [download the Editor](https://lvgl.io/pro#download) and use it under the free Community license.

LVGL Pro consists of four tightly related tools:

1. **Editor**: The heart of LVGL Pro. A desktop app to build components and screens in XML, manage data bindings, translations, animations, tests, and more. Learn more about the [XML Format](https://lvgl.io/docs/pro/syntax) and the [Widgets](https://lvgl.io/docs/pro/built_in_widgets).
2. **Online Viewer**: Run the Editor in your browser, open GitHub projects, and share easily without setting up a developer environment. Visit [https://viewer.lvgl.io](https://viewer.lvgl.io/).
3. **Figma Plugin**: Move a Figma design to LVGL Pro with one click. See how it works [here](https://lvgl.io/docs/pro/figma).
4. **CLI Tool**: Generate C code and run tests in CI/CD. See the details [here](https://lvgl.io/docs/pro/cli).

The Community and Evaluation tiers are free to use; see [licensing](#license) for commercial use.

## Examples

You can check out more than 100 C and XML examples at [https://lvgl.io/docs/open/examples](https://lvgl.io/docs/open/examples)

The [Online Viewer](https://viewer.lvgl.io/) of LVGL Pro also contains many tutorials and the same examples that you can play with interactively.

As a teaser, here is the same simple UI written in C and in XML:

[![A centered button that prints when clicked](https://private-user-images.githubusercontent.com/7599318/498852534-5948b485-e3f7-4a63-bb21-984381417c4a.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3ODU3OTE3ODIsIm5iZiI6MTc4NTc5MTQ4MiwicGF0aCI6Ii83NTk5MzE4LzQ5ODg1MjUzNC01OTQ4YjQ4NS1lM2Y3LTRhNjMtYmIyMS05ODQzODE0MTdjNGEucG5nP1gtQW16LUFsZ29yaXRobT1BV1M0LUhNQUMtU0hBMjU2JlgtQW16LUNyZWRlbnRpYWw9QUtJQVZDT0RZTFNBNTNQUUs0WkElMkYyMDI2MDgwMyUyRnVzLWVhc3QtMSUyRnMzJTJGYXdzNF9yZXF1ZXN0JlgtQW16LURhdGU9MjAyNjA4MDNUMjExMTIyWiZYLUFtei1FeHBpcmVzPTMwMCZYLUFtei1TaWduYXR1cmU9MjNmZGQ5NWI0ZmU1NWNhMzI3MzMxZjJjZDE0MWZkZGNiMjIyMjljNjc2MTViODg3Nzk4NGZlM2YxZjYxYzcxNiZYLUFtei1TaWduZWRIZWFkZXJzPWhvc3QmcmVzcG9uc2UtY29udGVudC10eXBlPWltYWdlJTJGcG5nIn0.XJEuhqKLSu7xK31hPfcwQSMDYcskm6pxDn3Lt_Cvqe0)](https://private-user-images.githubusercontent.com/7599318/498852534-5948b485-e3f7-4a63-bb21-984381417c4a.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3ODU3OTE3ODIsIm5iZiI6MTc4NTc5MTQ4MiwicGF0aCI6Ii83NTk5MzE4LzQ5ODg1MjUzNC01OTQ4YjQ4NS1lM2Y3LTRhNjMtYmIyMS05ODQzODE0MTdjNGEucG5nP1gtQW16LUFsZ29yaXRobT1BV1M0LUhNQUMtU0hBMjU2JlgtQW16LUNyZWRlbnRpYWw9QUtJQVZDT0RZTFNBNTNQUUs0WkElMkYyMDI2MDgwMyUyRnVzLWVhc3QtMSUyRnMzJTJGYXdzNF9yZXF1ZXN0JlgtQW16LURhdGU9MjAyNjA4MDNUMjExMTIyWiZYLUFtei1FeHBpcmVzPTMwMCZYLUFtei1TaWduYXR1cmU9MjNmZGQ5NWI0ZmU1NWNhMzI3MzMxZjJjZDE0MWZkZGNiMjIyMjljNjc2MTViODg3Nzk4NGZlM2YxZjYxYzcxNiZYLUFtei1TaWduZWRIZWFkZXJzPWhvc3QmcmVzcG9uc2UtY29udGVudC10eXBlPWltYWdlJTJGcG5nIn0.XJEuhqKLSu7xK31hPfcwQSMDYcskm6pxDn3Lt_Cvqe0)

| ``` static void button_clicked_cb(lv_event_t * e) {     printf("Clicked\n"); }  /* ... */  lv_obj_t * button = lv_button_create(lv_screen_active()); lv_obj_center(button); lv_obj_add_event_cb(button, button_clicked_cb,                     LV_EVENT_CLICKED, NULL);  lv_obj_t * label = lv_label_create(button); lv_label_set_text(label, "Hello from LVGL!"); ``` | ``` <screen>   <view>     <lv_button align="center">       <event_cb callback="button_clicked_cb" />       <lv_label text="Hello from LVGL!" />     </lv_button>   </view> </screen> ``` |
| --- | --- |

The XML above is what [LVGL Pro](#lvgl-pro) works with: you build the screen visually and it generates the C for you.

## Integration

LVGL has no external dependencies, so it can be easily compiled for any device. It comes with built-in drivers, is available in many package managers and RTOSes, and is also easy to port to any new device.

### Pre-integrated

- **Chip vendors**: [ESP32](https://components.espressif.com/components/lvgl/lvgl), [NXP MCUXpresso component](https://www.nxp.com/design/software/embedded-software/lvgl-open-source-graphics-library:LITTLEVGL-OPEN-SOURCE-GRAPHICS-LIBRARY), [Renesas FSP](https://lvgl.io/docs/open/integration/chip/renesas), [STM32](https://lvgl.io/docs/open/integration/chip/stm32)
- **RTOSes**: [Zephyr](https://lvgl.io/docs/open/integration/os/zephyr), [NuttX](https://lvgl.io/docs/open/integration/os/nuttx), [RT-Thread](https://lvgl.io/docs/open/integration/os/rt-thread)
- **Frameworks**: [Arduino](https://lvgl.io/docs/open/integration/framework/arduino), [PlatformIO](https://registry.platformio.org/libraries/lvgl/lvgl), [CMSIS-Pack](https://lvgl.io/docs/open/integration/framework/cmsis-pack)
- **Board manufacturers**: [Seeed Studio](https://www.seeedstudio.com/), [Elecrow](https://www.elecrow.com/display/esp-hmi-display.html), [Riverdi](https://lvgl.io/docs/open/integration/boards/manufacturers/riverdi), [VIEWE](https://lvgl.io/docs/open/integration/boards/manufacturers/viewe), and [many more](https://lvgl.io/boards)

### Built-in drivers

LVGL ships with ready-to-use drivers, so on common platforms you don't have to write display and input handling yourself:

- **Simulator / desktop**: [SDL](https://lvgl.io/docs/open/integration/pc/sdl), X11, and [Wayland](https://lvgl.io/docs/open/integration/embedded_linux/drivers/wayland) windows to develop and preview your UI on a PC.
- **Display controllers**: Generic MIPI-DBI/SPI LCDs ([ILI9341](https://lvgl.io/docs/open/integration/external_display_controllers/ili9341), ST7789, and similar), plus vendor controllers like ST's [LTDC](https://lvgl.io/docs/open/integration/chip_vendors/stm32/ltdc) and NXP's [eLCDIF](https://lvgl.io/docs/open/integration/chip_vendors/nxp/elcdif).
- **Embedded Linux**: framebuffer (fbdev), DRM/KMS, Wayland, and `libinput` / `evdev` for touch and pointer input. Learn more [here](https://lvgl.io/docs/open/integration/embedded_linux).
- **GPU / accelerators**: VG-Lite, NXP PXP, ThinkSilicon NemaGFX, Arm-2D and [OpenGL ES](https://lvgl.io/docs/open/integration/embedded_linux/drivers/opengl_driver)

See the full list and setup guides in the [Integration docs](https://lvgl.io/docs/open/integration).

### In LVGL Pro

In LVGL Pro you can create ready-to-use UI-only, VSCode, Zephyr, and Linux projects with a single click. [![image](https://private-user-images.githubusercontent.com/7599318/626349645-5aadb850-6b40-49d1-ba96-2296041c7e27.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3ODU3OTE3ODIsIm5iZiI6MTc4NTc5MTQ4MiwicGF0aCI6Ii83NTk5MzE4LzYyNjM0OTY0NS01YWFkYjg1MC02YjQwLTQ5ZDEtYmE5Ni0yMjk2MDQxYzdlMjcucG5nP1gtQW16LUFsZ29yaXRobT1BV1M0LUhNQUMtU0hBMjU2JlgtQW16LUNyZWRlbnRpYWw9QUtJQVZDT0RZTFNBNTNQUUs0WkElMkYyMDI2MDgwMyUyRnVzLWVhc3QtMSUyRnMzJTJGYXdzNF9yZXF1ZXN0JlgtQW16LURhdGU9MjAyNjA4MDNUMjExMTIyWiZYLUFtei1FeHBpcmVzPTMwMCZYLUFtei1TaWduYXR1cmU9Y2EyMWRkNTMwODdiNjFiYTExNDQ1ZTliM2EyY2ViYzgwMjk1M2U5ODVkNmU1OTNhNTk5NzdmOTA3N2NkY2Y0OCZYLUFtei1TaWduZWRIZWFkZXJzPWhvc3QmcmVzcG9uc2UtY29udGVudC10eXBlPWltYWdlJTJGcG5nIn0.yEXFDhozqyLwmJ4MTen4GYXtaVORKNsJsrHL1BVnj_s)](https://private-user-images.githubusercontent.com/7599318/626349645-5aadb850-6b40-49d1-ba96-2296041c7e27.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3ODU3OTE3ODIsIm5iZiI6MTc4NTc5MTQ4MiwicGF0aCI6Ii83NTk5MzE4LzYyNjM0OTY0NS01YWFkYjg1MC02YjQwLTQ5ZDEtYmE5Ni0yMjk2MDQxYzdlMjcucG5nP1gtQW16LUFsZ29yaXRobT1BV1M0LUhNQUMtU0hBMjU2JlgtQW16LUNyZWRlbnRpYWw9QUtJQVZDT0RZTFNBNTNQUUs0WkElMkYyMDI2MDgwMyUyRnVzLWVhc3QtMSUyRnMzJTJGYXdzNF9yZXF1ZXN0JlgtQW16LURhdGU9MjAyNjA4MDNUMjExMTIyWiZYLUFtei1FeHBpcmVzPTMwMCZYLUFtei1TaWduYXR1cmU9Y2EyMWRkNTMwODdiNjFiYTExNDQ1ZTliM2EyY2ViYzgwMjk1M2U5ODVkNmU1OTNhNTk5NzdmOTA3N2NkY2Y0OCZYLUFtei1TaWduZWRIZWFkZXJzPWhvc3QmcmVzcG9uc2UtY29udGVudC10eXBlPWltYWdlJTJGcG5nIn0.yEXFDhozqyLwmJ4MTen4GYXtaVORKNsJsrHL1BVnj_s)

### Porting manually

Integrating LVGL is very simple. Just drop it into any project and compile it as you would compile other files. To configure LVGL, copy `lv_conf_template.h` as `lv_conf.h`, enable the first `#if 0`, and adjust the configs as needed. (The default config is usually fine.) If available, LVGL can also be used with Kconfig.

Once in the project, you can initialize LVGL and create display and input devices as follows:

```
#include "lvgl/lvgl.h" /*Define LV_LVGL_H_INCLUDE_SIMPLE to include as "lvgl.h"*/

#define TFT_HOR_RES 320
#define TFT_VER_RES 240

static uint32_t my_tick_cb(void)
{
    return my_get_millisec();
}

static void my_flush_cb(lv_display_t * disp, const lv_area_t * area, uint8_t * px_map)
{
    /*Write px_map to the area->x1, area->x2, area->y1, area->y2 area of the
     *frame buffer or external display controller. */

    /* signal LVGL that we're done */
    lv_display_flush_ready(disp);
}

static void my_touch_read_cb(lv_indev_t * indev, lv_indev_data_t * data)
{
   if(my_touch_is_pressed()) {
       data->point.x = touchpad_x;
       data->point.y = touchpad_y;
       data->state = LV_INDEV_STATE_PRESSED;
   } else {
       data->state = LV_INDEV_STATE_RELEASED;
   }
}

void main(void)
{
    my_hardware_init();

    /*Initialize LVGL*/
    lv_init();

    /*Set millisecond-based tick source for LVGL so that it can track time.*/
    lv_tick_set_cb(my_tick_cb);

    /*Create a display where screens and widgets can be added*/
    lv_display_t * display = lv_display_create(TFT_HOR_RES, TFT_VER_RES);

    /*Add rendering buffers to the screen.
     *Here adding a smaller partial buffer assuming 16-bit (RGB565 color format)*/
    static uint8_t buf[TFT_HOR_RES * TFT_VER_RES / 10 * 2]; /* x2 because of 16-bit color depth */
    lv_display_set_buffers(display, buf, NULL, sizeof(buf), LV_DISPLAY_RENDER_MODE_PARTIAL);

    /*Add a callback that can flush the content from \`buf\` when it has been rendered*/
    lv_display_set_flush_cb(display, my_flush_cb);

    /*Create an input device for touch handling*/
    lv_indev_t * indev = lv_indev_create();
    lv_indev_set_type(indev, LV_INDEV_TYPE_POINTER);
    lv_indev_set_read_cb(indev, my_touch_read_cb);

    /*The drivers are in place; now we can create the UI*/
    lv_obj_t * label = lv_label_create(lv_screen_active());
    lv_label_set_text(label, "Hello world");
    lv_obj_center(label);

    /*Execute the LVGL-related tasks in a loop*/
    while(1) {
        lv_timer_handler();
        my_sleep_ms(5);         /*Wait a little to let the system breathe*/
    }
}
```

## Contributing

LVGL is an open project, and contributions are very welcome. There are many ways to contribute, from simply speaking about your project, writing examples, improving the documentation, fixing bugs, or even hosting your own project under the LVGL organization.

For a detailed description of contribution opportunities, visit the [Contributing](https://lvgl.io/docs/open/contributing) section of the documentation.

Hundreds of people have already left their fingerprint on LVGL. Be one of them! See you here! 🙂

## License

The LVGL library is distributed under the **MIT license**, so you can use it freely in both open-source and commercial products with no royalties. See [`LICENCE.txt`](https://github.com/lvgl/lvgl/blob/master/LICENCE.txt).

All third-party libraries bundled with LVGL are released under MIT-compatible licenses too, so you can use LVGL and its dependencies with confidence.

**[LVGL Pro](https://lvgl.io/pro)** has separate licensing:

- The **Community** and **Evaluation** tiers are **free for non-commercial use**, perfect for learning, hobby projects, and evaluating the tools.
- Commercial use of LVGL Pro requires a paid license. See the [Pricing and Details](https://lvgl.io/pro#pricing).
