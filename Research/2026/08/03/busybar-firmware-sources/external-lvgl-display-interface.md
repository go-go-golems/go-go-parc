---
title: "Captured source: External Lvgl Display Interface"
source_file: "external-lvgl-display-interface.md"
type: source
---

# Captured source: External Lvgl Display Interface

Original ticket source file: `external-lvgl-display-interface.md`.

[\[中文\]](https://lvgl.100ask.net/v9.2/porting/display.html)

## Display interface

To create a display for LVGL call [lv\_display\_t](https://lvgl.io/docs/open/9.2/API/misc/lv_types.html#_CPPv412lv_display_t "lv_display_t") \* display = [lv\_display\_create](https://lvgl.io/docs/open/9.2/API/display/lv_display.html#_CPPv417lv_display_create7int32_t7int32_t "lv_display_create") (hor\_res, ver\_res). You can create a multiple displays and a different driver for each (see below),

## Basic setup

Draw buffer(s) are simple array(s) that LVGL uses to render the screen's content. Once rendering is ready the content of the draw buffer is sent to the display using the `flush_cb` function.

### flush\_cb

An example `flush_cb` looks like this:

```c
void my_flush_cb(lv_display_t * display, const lv_area_t * area, uint8_t * px_map)
{
    /*The most simple case (but also the slowest) to put all pixels to the screen one-by-one
     *\`put_px\` is just an example, it needs to be implemented by you.*/
    uint16_t * buf16 = (uint16_t *)px_map; /*Let's say it's a 16 bit (RGB565) display*/
    int32_t x, y;
    for(y = area->y1; y <= area->y2; y++) {
        for(x = area->x1; x <= area->x2; x++) {
            put_px(x, y, *buf16);
            buf16++;
        }
    }

    /* IMPORTANT!!!
     * Inform LVGL that you are ready with the flushing and buf is not used anymore*/
    lv_display_flush_ready(disp);
}
```

Use [lv\_display\_set\_flush\_cb](https://lvgl.io/docs/open/9.2/API/display/lv_display.html#_CPPv423lv_display_set_flush_cbP12lv_display_t21lv_display_flush_cb_t "lv_display_set_flush_cb") (disp, my\_flush\_cb) to set a new `flush_cb`.

lv\_display\_flush\_ready(disp) needs to be called when flushing is ready to inform LVGL the buffer is not used anymore by the driver and it can render new content into it.

LVGL might render the screen in multiple chunks and therefore call `flush_cb` multiple times. To see if the current one is the last chunk of rendering use lv\_display\_flush\_is\_last(display).

### Draw buffers

The draw buffers can be set with [lv\_display\_set\_buffers](https://lvgl.io/docs/open/9.2/API/display/lv_display.html#_CPPv422lv_display_set_buffersP12lv_display_tPvPv8uint32_t24lv_display_render_mode_t "lv_display_set_buffers") (display, buf1, buf2, buf\_size\_byte, render\_mode)

- `buf1` a buffer where LVGL can render
- `buf2` a second optional buffer (see more details below)
- `buf_size_byte` size of the buffer(s) in bytes
- `render_mode`
	- [`LV_DISPLAY_RENDER_MODE_PARTIAL`](https://lvgl.io/docs/open/9.2/API/display/lv_display.html#_CPPv4N24lv_display_render_mode_t30LV_DISPLAY_RENDER_MODE_PARTIALE "LV_DISPLAY_RENDER_MODE_PARTIAL") Use the buffer(s) to render the screen in smaller parts. This way the buffers can be smaller then the display to save RAM. At least 1/10 screen size buffer(s) are recommended. In `flush_cb` the rendered images needs to be copied to the given area of the display. In this mode if a button is pressed only the button's area will be redrawn.
		- [`LV_DISPLAY_RENDER_MODE_DIRECT`](https://lvgl.io/docs/open/9.2/API/display/lv_display.html#_CPPv4N24lv_display_render_mode_t29LV_DISPLAY_RENDER_MODE_DIRECTE "LV_DISPLAY_RENDER_MODE_DIRECT") The buffer(s) has to be screen sized and LVGL will render into the correct location of the buffer. This way the buffer always contain the whole image. If two buffer are used the rendered areas are automatically copied to the other buffer after flushing. Due to this in `flush_cb` typically only a frame buffer address needs to be changed. If a button is pressed only the button's area will be redrawn.
		- [`LV_DISPLAY_RENDER_MODE_FULL`](https://lvgl.io/docs/open/9.2/API/display/lv_display.html#_CPPv4N24lv_display_render_mode_t27LV_DISPLAY_RENDER_MODE_FULLE "LV_DISPLAY_RENDER_MODE_FULL") The buffer(s) has to be screen sized and LVGL will always redraw the whole screen even if only 1 pixel has been changed. If two screen sized draw buffers are provided, LVGL's display handling works like "traditional" double buffering. This means the `flush_cb` callback only has to update the address of the frame buffer to the `px_map` parameter.

Example:

```c
static uint16_t buf[LCD_HOR_RES * LCD_VER_RES / 10];
lv_display_set_buffers(disp, buf, NULL, sizeof(buf), LV_DISPLAY_RENDER_MODE_PARTIAL);
```

#### One buffer

If only one buffer is used LVGL draws the content of the screen into that draw buffer and sends it to the display via the `flush_cb`. LVGL then needs to wait until lv\_display\_flush\_ready is called (that is the content of the buffer is sent to the display) before drawing something new into it.

#### Two buffers

If two buffers are used LVGL can draw into one buffer while the content of the other buffer is sent to the display in the background. DMA or other hardware should be used to transfer data to the display so the MCU can continue drawing. This way, the rendering and refreshing of the display become parallel operations.

## Advanced options

### Resolution

To set the resolution of the display after creation use [lv\_display\_set\_resolution](https://lvgl.io/docs/open/9.2/API/display/lv_display.html#_CPPv425lv_display_set_resolutionP12lv_display_t7int32_t7int32_t "lv_display_set_resolution") (display, hor\_res, ver\_res)

It's not mandatory to use the whole display for LVGL, however in some cases the physical resolution is important. For example the touchpad still sees the whole resolution and the values needs to be converted to the active LVGL display area. So the physical resolution and the offset of the active area can be set with [lv\_display\_set\_physical\_resolution](https://lvgl.io/docs/open/9.2/API/display/lv_display.html#_CPPv434lv_display_set_physical_resolutionP12lv_display_t7int32_t7int32_t "lv_display_set_physical_resolution") (disp, hor\_res, ver\_res) and [lv\_display\_set\_offset](https://lvgl.io/docs/open/9.2/API/display/lv_display.html#_CPPv421lv_display_set_offsetP12lv_display_t7int32_t7int32_t "lv_display_set_offset") (disp, x, y)

### Flush wait callback

By using lv\_display\_flush\_ready LVGL will spin in a loop while waiting for flushing.

However with the help of [lv\_display\_set\_flush\_wait\_cb](https://lvgl.io/docs/open/9.2/API/display/lv_display.html#_CPPv428lv_display_set_flush_wait_cbP12lv_display_t26lv_display_flush_wait_cb_t "lv_display_set_flush_wait_cb") a custom wait callback be set for flushing. This callback can use a semaphore, mutex, or anything else to optimize while the waiting for flush.

If `flush_wait_cb` is not set, LVGL assume that lv\_display\_flush\_ready is used.

### Rotation

LVGL supports rotation of the display in 90 degree increments. You can select whether you would like software rotation or hardware rotation.

The orientation of the display can be changed with `lv_display_set_rotation(disp, LV_DISPLAY_ROTATION_0/90/180/270)`. LVGL will swap the horizontal and vertical resolutions internally according to the set degree. When changing the rotation [LV\_EVENT\_SIZE\_CHANGED](https://lvgl.io/docs/open/9.2/API/misc/lv_event.html#_CPPv4N15lv_event_code_t21LV_EVENT_SIZE_CHANGEDE "LV_EVENT_SIZE_CHANGED") is sent to the display to allow reconfiguring the hardware. In lack of hardware display rotation support [lv\_draw\_sw\_rotate](https://lvgl.io/docs/open/9.2/API/draw/sw/lv_draw_sw.html#_CPPv417lv_draw_sw_rotatePKvPv7int32_t7int32_t7int32_t7int32_t21lv_display_rotation_t17lv_color_format_t "lv_draw_sw_rotate") can be used to rotate the buffer in the `flush_cb`.

[lv\_display\_rotate\_area](https://lvgl.io/docs/open/9.2/API/display/lv_display.html#_CPPv422lv_display_rotate_areaP12lv_display_tP9lv_area_t "lv_display_rotate_area") (display, &area) rotates the rendered area according to the current rotation settings of the display.

Note that in [`LV_DISPLAY_RENDER_MODE_DIRECT`](https://lvgl.io/docs/open/9.2/API/display/lv_display.html#_CPPv4N24lv_display_render_mode_t29LV_DISPLAY_RENDER_MODE_DIRECTE "LV_DISPLAY_RENDER_MODE_DIRECT") the small changed areas are rendered directly in the frame buffer so they cannot be rotated later. Therefore in direct mode only the whole frame buffer can be rotated. The same is true for [`LV_DISPLAY_RENDER_MODE_FULL`](https://lvgl.io/docs/open/9.2/API/display/lv_display.html#_CPPv4N24lv_display_render_mode_t27LV_DISPLAY_RENDER_MODE_FULLE "LV_DISPLAY_RENDER_MODE_FULL").

In the case of [`LV_DISPLAY_RENDER_MODE_PARTIAL`](https://lvgl.io/docs/open/9.2/API/display/lv_display.html#_CPPv4N24lv_display_render_mode_t30LV_DISPLAY_RENDER_MODE_PARTIALE "LV_DISPLAY_RENDER_MODE_PARTIAL") the small rendered areas can be rotated on their own before flushing to the frame buffer.

### Color format

The default color format of the display is set according to `LV_COLOR_DEPTH` (see `lv_conf.h`)

- `LV_COLOR_DEPTH` `32`: XRGB8888 (4 bytes/pixel)
- `LV_COLOR_DEPTH` `24`: RGB888 (3 bytes/pixel)
- `LV_COLOR_DEPTH` `16`: RGB565 (2 bytes/pixel)
- `LV_COLOR_DEPTH` `8`: L8 (1 bytes/pixel)
- `LV_COLOR_DEPTH` `1`: I1 (1 bit/pixel) Only support for horizontal mapped buffers. See [:refr:\`monochrome\`](#id2) for more details:

The `color_format` can be changed with lv\_display\_set\_color\_depth(display, LV\_COLOR\_FORMAT\_...). Besides the default value `LV_COLOR_FORMAT_ARGB8888` can be used as a well.

It's very important that draw buffer(s) should be large enough for any selected color format.

### Swap endianness

In case of RGB565 color format it might be required to swap the 2 bytes because the SPI, I2C or 8 bit parallel port periphery sends them in the wrong order.

The ideal solution is configure the hardware to handle the 16 bit data with different byte order, however if it's not possible [lv\_draw\_sw\_rgb565\_swap](https://lvgl.io/docs/open/9.2/API/draw/sw/lv_draw_sw.html#_CPPv422lv_draw_sw_rgb565_swapPv8uint32_t "lv_draw_sw_rgb565_swap") (buf, buf\_size\_in\_px) can be called in the `flush_cb` to swap the bytes.

If you wish you can also write your own function, or use assembly instructions for the fastest possible byte swapping.

Note that this is not about swapping the Red and Blue channel but converting

`RRRRR GGG | GGG BBBBB`

to

`GGG BBBBB | RRRRR GGG`.

### Monochrome Displays

LVGL supports rendering directly in a 1-bit format for monochrome displays. To enable it, set `LV_COLOR_DEPTH 1` or use [lv\_display\_set\_color\_format](https://lvgl.io/docs/open/9.2/API/display/lv_display.html#_CPPv427lv_display_set_color_formatP12lv_display_t17lv_color_format_t "lv_display_set_color_format") (display, [LV\_COLOR\_FORMAT\_I1](https://lvgl.io/docs/open/9.2/API/misc/lv_color.html#_CPPv4N17lv_color_format_t18LV_COLOR_FORMAT_I1E "LV_COLOR_FORMAT_I1")).

The [LV\_COLOR\_FORMAT\_I1](https://lvgl.io/docs/open/9.2/API/misc/lv_color.html#_CPPv4N17lv_color_format_t18LV_COLOR_FORMAT_I1E "LV_COLOR_FORMAT_I1") format assumes that bytes are mapped to rows (i.e., the bits of a byte are written next to each other). The order of bits is MSB first, which means:

```c
MSB           LSB
bits       7 6 5 4 3 2 1 0
pixels     0 1 2 3 4 5 6 7
          Left         Right
```

Ensure that the LCD controller is configured accordingly.

Internally, LVGL rounds the redrawn areas to byte boundaries. Therefore, updated areas will:

- Start on an `Nx8` coordinate.
- End on an `Nx8 - 1` coordinate.

When setting up the buffers for rendering ([`lv_display_set_buffers()`](https://lvgl.io/docs/open/9.2/API/display/lv_display.html#_CPPv422lv_display_set_buffersP12lv_display_tPvPv8uint32_t24lv_display_render_mode_t "lv_display_set_buffers")), make the buffer 8 bytes larger. This is necessary because LVGL reserves 2 x 4 bytes in the buffer, as these are assumed to be used as a palette.

To skip the palette, include the following line in your `flush_cb` function: `px_map += 8`.

As usual, monochrome displays support partial, full, and direct rendering modes as well. In full and direct modes, the buffer size should be large enough for the whole screen, meaning `(horizontal_resolution x vertical_resolution / 8) + 8` bytes. As LVGL can not handle fractional width make sure to round the horizontal resolution to 8- (For example 90 to 96)

### User data

With [lv\_display\_set\_user\_data](https://lvgl.io/docs/open/9.2/API/display/lv_display.html#_CPPv424lv_display_set_user_dataP12lv_display_tPv "lv_display_set_user_data") (disp, p) a pointer to a custom data can be stored in display object.

### Decoupling the display refresh timer

Normally the dirty (a.k.a invalid) areas are checked and redrawn in every `LV_DEF_REFR_PERIOD` milliseconds (set in `lv_conf.h`). However, in some cases you might need more control on when the display refreshing happen, for example to synchronize rendering with VSYNC or the TE signal.

You can do this in the following way:

```c
/*Delete the original display refresh timer*/
lv_display_delete_refr_timer(disp);

/*Call this anywhere you want to refresh the dirty areas*/
_lv_display_refr_timer(NULL);
```

If you have multiple displays call [lv\_display\_set\_default](https://lvgl.io/docs/open/9.2/API/display/lv_display.html#_CPPv422lv_display_set_defaultP12lv_display_t "lv_display_set_default") (disp1) to select the display to refresh before \_lv\_display\_refr\_timer(NULL).

> [!note] Note
> that `lv_timer_handler()` and `_lv_display_refr_timer()` cannot run at the same time.

If the performance monitor is enabled, the value of `LV_DEF_REFR_PERIOD` needs to be set to be consistent with the refresh period of the display to ensure that the statistical results are correct.

### Force refreshing

Normally the invalidated areas (marked for redraw) are rendered in `lv_timer_handler()` in every `LV_DEF_REFR_PERIOD` milliseconds. However, by using `lv_refr_now(display)()` you can ask LVGL to redraw the invalid areas immediately. The refreshing will happen in [`lv_refr_now()`](https://lvgl.io/docs/open/9.2/API/core/lv_refr.html#_CPPv411lv_refr_nowP12lv_display_t "lv_refr_now") which might take longer time.

The parameter of [`lv_refr_now()`](https://lvgl.io/docs/open/9.2/API/core/lv_refr.html#_CPPv411lv_refr_nowP12lv_display_t "lv_refr_now") is a display to refresh. If `NULL` is set the default display will be updated.

## Events

[lv\_display\_add\_event\_cb](https://lvgl.io/docs/open/9.2/API/display/lv_display.html#_CPPv423lv_display_add_event_cbP12lv_display_t13lv_event_cb_t15lv_event_code_tPv "lv_display_add_event_cb") (disp, event\_cb, LV\_EVENT\_..., user\_data) adds an event handler to a display. The following events are sent:

- [`LV_EVENT_INVALIDATE_AREA`](https://lvgl.io/docs/open/9.2/API/misc/lv_event.html#_CPPv4N15lv_event_code_t24LV_EVENT_INVALIDATE_AREAE "LV_EVENT_INVALIDATE_AREA") An area is invalidated (marked for redraw). [lv\_event\_get\_param](https://lvgl.io/docs/open/9.2/API/misc/lv_event.html#_CPPv418lv_event_get_paramP10lv_event_t "lv_event_get_param") (e) returns a pointer to an [`lv_area_t`](https://lvgl.io/docs/open/9.2/API/misc/lv_area.html#_CPPv49lv_area_t "lv_area_t") variable with the coordinates of the area to be invalidated. The area can be freely modified if needed to adopt it the special requirement of the display. Usually needed with monochrome displays to invalidate `N x 8` rows or columns at once.
- [`LV_EVENT_REFR_REQUEST`](https://lvgl.io/docs/open/9.2/API/misc/lv_event.html#_CPPv4N15lv_event_code_t21LV_EVENT_REFR_REQUESTE "LV_EVENT_REFR_REQUEST"): Sent when something happened that requires redraw.
- [`LV_EVENT_REFR_START`](https://lvgl.io/docs/open/9.2/API/misc/lv_event.html#_CPPv4N15lv_event_code_t19LV_EVENT_REFR_STARTE "LV_EVENT_REFR_START"): Sent when a refreshing cycle starts. Sent even if there is nothing to redraw.
- [`LV_EVENT_REFR_READY`](https://lvgl.io/docs/open/9.2/API/misc/lv_event.html#_CPPv4N15lv_event_code_t19LV_EVENT_REFR_READYE "LV_EVENT_REFR_READY"): Sent when refreshing is ready (after rendering and calling the `flush_cb`). Sent even if no redraw happened.
- [`LV_EVENT_RENDER_START`](https://lvgl.io/docs/open/9.2/API/misc/lv_event.html#_CPPv4N15lv_event_code_t21LV_EVENT_RENDER_STARTE "LV_EVENT_RENDER_START"): Sent when rendering starts.
- [`LV_EVENT_RENDER_READY`](https://lvgl.io/docs/open/9.2/API/misc/lv_event.html#_CPPv4N15lv_event_code_t21LV_EVENT_RENDER_READYE "LV_EVENT_RENDER_READY"): Sent when rendering is ready (before calling the `flush_cb`)
- [`LV_EVENT_FLUSH_START`](https://lvgl.io/docs/open/9.2/API/misc/lv_event.html#_CPPv4N15lv_event_code_t20LV_EVENT_FLUSH_STARTE "LV_EVENT_FLUSH_START"): Sent before the `flush_cb` is called.
- `LV_EVENT_FLUSH_READY`: Sent when the `flush_cb` returned.
- [`LV_EVENT_RESOLUTION_CHANGED`](https://lvgl.io/docs/open/9.2/API/misc/lv_event.html#_CPPv4N15lv_event_code_t27LV_EVENT_RESOLUTION_CHANGEDE "LV_EVENT_RESOLUTION_CHANGED"): Sent when the resolution changes due to [`lv_display_set_resolution()`](https://lvgl.io/docs/open/9.2/API/display/lv_display.html#_CPPv425lv_display_set_resolutionP12lv_display_t7int32_t7int32_t "lv_display_set_resolution") or [`lv_display_set_rotation()`](https://lvgl.io/docs/open/9.2/API/display/lv_display.html#_CPPv423lv_display_set_rotationP12lv_display_t21lv_display_rotation_t "lv_display_set_rotation").
