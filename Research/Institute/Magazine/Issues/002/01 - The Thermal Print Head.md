# The Thermal Print Head

## Heat, Paper, and the Physics of a Single Dot

Plug a thermal printer into a serial port and it will print your first line of text within an hour. Wire four pins, open the port at 9600 baud, send the bytes of a sentence, and a line of dark characters appears on a narrow strip of paper. The device seems, at this first encounter, almost embarrassingly simple.

Print a photograph on the same device and the simplicity collapses. A face becomes a black mass. A gray sky vanishes into white. Horizontal bands stripe the image where no banding was sent. The printer, which rendered the text perfectly, has produced a photograph that is unreadable.

The distance between these two outcomes is the subject of this article. It is not a distance in software. A thermal printer is a physical system — a line of heaters, a motor, a chemical paper, a power supply — and the photograph fails because that physical system is being asked to do something the text never asked of it. To see why, we have to look at what the printer actually does when it places a single dot on the page.

---

## The Head Is a Row of Heaters

Open the mechanism and the print head is a small ceramic bar, perhaps four centimeters long, pressed against the paper by a rubber roller. The bar carries 384 resistive heating elements in a single row. For the K118 class of mechanism — the kind embedded in the M5Stack Atom printer and many 58 mm receipt printers — these elements span the 58 mm printable width at a density of 203 dots per inch, which is eight dots per millimeter.

Each element is a resistor of roughly 160 to 200 ohms. When current passes through it, the resistor's temperature rises in microseconds. The paper pressed against it darkens where the heat crosses a threshold. Lift the head away from the paper and you find no ink. The darkness is a chemical change in the paper itself.

The paper is not blank stationery. It is an engineered stack: a base sheet, a precoat, and a reactive thermal layer holding a leuco dye and a developer. Heat melts the dye and developer together, and the dye flips from colorless to colored. The printer does not deposit anything. It triggers a phase transition, in a precise pattern, at a precise time.

The roller, driven by a stepper motor, advances the paper by one line after each row of heaters fires. One line at 203 dpi is about 0.125 mm. A printed page is a stack of these lines, each line a row of 384 binary decisions — burn or do not burn.

Three facts follow from this architecture, and they explain almost everything that happens next.

A horizontal band across the print is a line-to-line phenomenon. If a group of adjacent rows receives different energy, different timing, or different motion than its neighbors, the difference appears as a visible band. Banding lives on the vertical axis, because that is the axis along which the system's state changes.

A full-width raster row costs the same number of bytes whether it is solid black or solid white. Three hundred eighty-four dots, packed eight to a byte, is forty-eight bytes. The serial link pays for the dimensions of the image, not for its darkness.

And the power supply pays for darkness, not for bytes. A row that fires many heaters draws more current than a row that fires few. The mechanical and electrical stress of a print is a function of dot density. Text, which energizes a sparse and irregular subset of the heaters, barely loads the system. A photograph, which may ask for half the heaters on every line, loads it continuously.

Text felt easy because it was easy. The photograph is hard because it stresses the physics.

---

## The Energy Equation

The energy delivered to a single dot follows the oldest equation in circuit theory. A resistor $R$ across a voltage $V$ for a pulse of duration $t$ dissipates

$$E = \frac{V^2}{R}\,t$$

This is the quantity the paper records as darkness, and its shape — quadratic in voltage, linear in time — is the source of most of the printer's bad behavior.

Consider one heater: 180 ohms across 12 volts. The instantaneous power is

$$P = \frac{V^2}{R} = \frac{144}{180} \approx 0.8 \text{ watts}$$

That is one heater. A full-width black row energizes a large fraction of the 384 heaters at once, and the elements are grouped internally so that they fire in sequence rather than all simultaneously — but the aggregate current still flows through the shared power rail. The rail has resistance of its own, in the wiring, in the barrel connector, in the regulator, in the ground return. The voltage that actually reaches each heater is the supply voltage minus the drop across that shared resistance.

The quadratic dependence on voltage makes the loss compound. If the effective head voltage sags by ten percent under load, the energy per dot does not fall by ten percent. It falls to eighty-one percent:

$$\frac{E'}{E} = \left(\frac{0.9\,V}{V}\right)^2 = 0.81$$

A twenty-percent sag is worse. The energy falls to sixty-four percent of nominal. A dot that was marginal at full voltage — a dot that just barely crossed the paper's activation threshold — drops below it and vanishes.

This is why a dense photograph fades in a way that text never does. The dense region is precisely where the most heaters fire, precisely where the rail sags most, and precisely where the marginal dots disappear first. The failure looks like a software bug in the image. It is a brownout in the power supply.

The practical test is not to read the adapter's label. It is to measure the voltage at the printer's input while a dense print is running, and to watch what happens to a gray ramp when the density setting is lowered. If lowering the density dramatically improves a faded image, the cause is energy, not dithering.

---

## Thermal Memory

The energy equation describes a single pulse in isolation. A real print head does not operate in isolation. It operates in a rapid sequence of pulses, and each pulse leaves a residue of heat in the ceramic.

A heater that fired on the previous line is warmer than one that was idle. A head that has just printed a dense block is warmer than one that has printed sparse text. The substrate temperature is a running integral of recent activity, decaying with a time constant set by the thermal mass of the ceramic and its coupling to air. The darkness produced by a given pulse is therefore a function not only of the pulse itself but of the pulses that came before it.

Good printer controllers compensate. They read a thermistor on the head, track the dot history of recent lines, and adjust subsequent pulse widths to keep the delivered energy roughly constant as the substrate warms. The K118 exposes some of this compensation through its density and speed registers, but the internal logic is opaque. What the host sees is a device whose response to a fixed setting drifts with what was printed a moment ago.

The consequence is that print quality is not perfectly reproducible. Two prints of the same bitmap can differ if one follows a dense print and the other follows a cool idle. The only reliable calibration is empirical: print a test pattern under the conditions you intend to use, read it on paper, and fix the settings. This is not a defect of the device. It is the physics, and every thermal printer shares it.

---

## The Command That Carries Everything

The host speaks to the printer in ESC/POS, a byte-oriented command language descended from Epson's receipt printers. Most commands are compact state changes — set bold, set alignment, set font size — that the printer applies to the text that follows. The printer carries its own fonts, and a line of characters costs only a handful of command bytes.

One command carries nearly all the image data the printer will ever receive. It is the raster bitmap command, `GS v 0`, and its structure is a length-prefixed frame:

```
1D 76 30  m  xL xH yL yH  d1 d2 ... dk
|_______|    |________| |________|  |________|
 command      width       height      pixel data
              (bytes)     (rows)
```

The width is in bytes, not pixels, because the data is packed at eight bits per byte, most-significant bit first. For the 384-dot head the width field is 48. The payload is the product: $k = \text{width} \times \text{height}$.

The arithmetic of this command is unforgiving, and it explains why text is responsive and bitmaps are slow. The mechanism is rated at 203 dots per inch, eight dots per millimeter, and a nominal paper speed of 60 millimeters per second. At that speed the paper advances at 480 rows per second. A continuous full-width raster stream must therefore deliver

$$480 \;\text{rows/s} \times 48 \;\text{B/row} = 23{,}040 \;\text{bytes/s}$$

UART framing adds a start and stop bit to each byte, so the line rate is roughly ten times the payload rate: 230,400 bits per second. The default UART configuration of the K118 is 9,600 baud. At that rate the link carries 960 payload bytes per second, which sustains twenty full-width rows per second, which is 2.5 millimeters of paper per second. The mechanism is rated for sixty.

| UART baud | Payload B/s | Full-width rows/s | Paper speed |
|----------:|------------:|------------------:|------------:|
| 9,600     | 960         | 20                | 2.5 mm/s    |
| 38,400    | 3,840       | 80                | 10 mm/s     |
| 115,200   | 11,520      | 240               | 30 mm/s     |
| 230,400   | 23,040      | 480               | 60 mm/s     |
| 460,800   | 46,080      | 960               | 120 mm/s    |

At the default baud, the serial link cannot feed the head at its rated speed. A host that sends a bitmap and expects the printer to maintain nominal motion will discover that the printer must pause, slow, re-buffer, cool, or restart the motor to wait for data. Each of those pauses is a candidate origin for a horizontal band.

Text never exposed this bottleneck, because text never used this command. The printer rendered the characters itself, from a few bytes of instruction. The bitmap path streams one bit per dot, and at 9600 baud the stream cannot keep up with the paper.

---

## The Streaming Contract

The `GS v 0` command carries no flow control at the application layer. The printer receives bytes at the serial rate and interprets them as they arrive. If the host pauses mid-payload — even for a few milliseconds — the printer may decide the command has ended, print whatever it has so far, advance the paper, and interpret the bytes that arrive next as the start of a new command.

The result is a striped print. Some rows are correct. Others are missing, or shifted, or reinterpreted as garbage. The discontinuity sits at exactly the row where the host paused.

The fix is structural. The entire payload of a raster command — the eight-byte header plus all $k$ bytes of pixel data — must reach the UART as a single continuous write. The host must not interleave network reads, log writes, or any other work inside the payload.

In an architecture where an ESP32 receives the bitmap over HTTP and forwards it to the printer over UART, this means the HTTP body must be buffered completely into memory before the first byte is written to the UART. Streaming the body chunk by chunk, writing each chunk as it arrives, injects the network's scheduling jitter directly into the middle of the print command. The printer records that jitter as banding.

The rule is simple and absolute: a `GS v 0` command is a streaming contract. Feed it continuously, or divide it into chunks only when the printer's real buffer and motion behavior are understood. Arbitrary sleeps between small bands are easy to write and frequently visible on paper.

A common debugging mistake compounds the problem. Faced with a striped print, an engineer will often break the image into small five-row bands — 240 bytes, which fits comfortably in a 256-byte receive buffer — and send each as a complete `GS v 0` command with a delay between them. The banding becomes regular and frequent, because every band boundary is now a timing boundary. Legal command syntax has produced physical artifacts. The receive-buffer heuristic was correct, but the cure was worse than the disease.

---

## Two Ways to Pause

A printer's receive buffer is finite. When the host sends faster than the printer can accept, one of three things must happen: the printer asserts a hardware busy signal and the host pauses; the printer sends software flow-control bytes and the host pauses; or bytes are dropped.

The K118 exposes a Clear-To-Send line on its header. Wire it to a hardware flow-control input of the host UART and the peripheral gates transmission itself, below the application layer. The host's UART driver pauses when CTS is deasserted and resumes when it is reasserted, with no code required. This is strictly better than fixed delays, because the pause tracks the receiver's actual readiness rather than the sender's guess.

Software flow control is the alternative. The printer emits XON (`0x11`) and XOFF (`0x13`) bytes on its receive line, and the host reads them while transmitting, stopping when XOFF appears. The appeal is that it needs no extra wire. The catch is that the host must read the receive line while writing to the transmit line, and it must react to a flow-control byte before an in-flight write has committed too many bytes to the driver's transmit buffer. A single large blocking `write()` cannot honor XOFF in time if the buffer has already been filled.

The robust sequence is conservative. Enable CTS first; the hardware handles the timing. Log the receive line during a print and look specifically for `0x11` and `0x13`. Only if the printer actually emits them is it worth writing a chunked sender that honors them. Never assume software flow control works until the line shows the bytes.

---

## The Two Knobs

The K118 exposes two vendor commands that adjust the energy delivered per dot. They are the principal tuning levers, and they are orthogonal to the dot pattern.

Density, set by `ESC ## STDP n` with $n$ from 0 to 39, is a global strobe-energy setting. Raising it darkens every dot, regardless of where the rasterizer placed that dot. There is no separate contrast register on this device. Density *is* the contrast control.

Speed, set by `ESC ## STSP n` from a fixed list — 25, 30, 37, 50, 56, 62, 70, 80, 90, 100, 120, 150, 180, 200, 220 — sets how long the head dwells on each line. Slower speed delivers more energy per dot and burns darker and more evenly. Faster speed prints lighter and quicker. Speed is therefore a second energy lever, but it also serves a role density does not, which is the subject of the next section.

A third command, `ESC ## SPSM n`, selects a graphics mode: 30 for BLE graphics, 31 for adaptive-speed graphics, 32 for constant-speed graphics. The adaptive mode lets the printer's internal scheduler vary the line timing in response to its own state. When a host streams a bitmap faster or slower than the printer can sustain, the adaptive scheduler can paper over the mismatch by inserting pauses of its own — and whether those pauses produce visible banding depends on firmware the host cannot inspect.

---

## Power Droop, and Why Speed Matters

A subtle artifact appears on prints made at low density: the gray tone varies *across a single line*. A row that should be uniform gray is lighter at one edge than the other. The cause is print-head power droop.

When a raster row fires many heaters at once, the shared rail sags under the aggregate current. The heaters that fire later in the row's energization sequence — and most thermal heads energize their elements in groups, not all at once — see a lower voltage than the ones that fired earlier, and their dots come out lighter. The artifact is visible only at low density, because there the dots are already marginal: a small loss of energy pushes them below the paper's threshold and they vanish. At high density the energy headroom is large enough that the sag does not matter.

The obvious response is to raise the density. This fixes the droop but introduces a new problem, which is the subject of the next article. Dense regions on thermal paper exhibit dot gain: each burned dot spreads, and a hot dense region turns into a muddy black mass. There is no single density at which both sparse text and dense photographs print well.

The less obvious response is to lower the print speed. Slower speed gives the rail more time to recover between lines and lengthens the dwell per dot, which reduces the within-line variation and increases the energy delivered. Speed, in other words, is not only a darkness control but an evenness control. Text — printed as long, dense rows of solid strokes — is exactly the content that provokes droop, and text is the content that benefits most from a slower speed. The cost is time. For a printer that emits a few strips a minute, the cost is usually acceptable.

---

## Reading a Banded Print

A horizontal band is a timestamp printed on paper. It marks a row range at which something changed: the buffer availability, the motor motion, the head temperature, the supply voltage, the paper contact, or the host's chunking behavior. A banded print, read as a diagnostic signal rather than a random defect, points to the fault.

The first discriminator is the printer's self-test. If the self-test bands, the host protocol is exonerated; the cause is paper, power, head, platen, or mechanism. If the self-test is clean but host bitmaps band, the host path is implicated.

The second discriminator compares native content to bitmap content. The printer can render text, QR codes, and barcodes internally from short commands; it cannot render a photograph without streamed raster. If a native QR prints cleanly but a bitmap of the same QR bands, the QR algorithm is not at fault. The raster transport is.

The spacing of the bands carries information about their origin.

| Band signature | Likely layer |
|----------------|--------------|
| Period of ~0.6 mm on 384-dot jobs | Host chunking, typically 5-row bands of 240 bytes |
| Period of several centimeters, near roller circumference | Platen defect, eccentricity, contamination, pressure variation |
| Only in dense black regions | Power sag, current limiting, thermal throttling, density too high |
| Only in the first lines after an idle or feed | Backlash, stiction, restart behavior |
| Self-test also bands | Paper, head, platen, power, or mechanism — not host code |
| Native QR clean, bitmap QR banded | Raster bandwidth or pacing, not the QR algorithm |

A print, in this sense, is a physical oscilloscope trace. The vertical axis is time. The horizontal bands are the moments at which the system's state changed. Learning to read them is the difference between debugging a printer by guessing and debugging it by measurement.

---

## What the Hardware Leaves to Software

We now have the physical picture. A thermal printer is a line of heaters and a motor, fed by a serial link that is too slow at default settings to keep up with the mechanism it serves. The energy delivered to a dot is quadratic in voltage, which makes the device acutely sensitive to power integrity and to its own thermal history. Text prints well because it loads the system lightly. Photographs print poorly because they load it heavily, in patterns that expose every weakness in the power path, the timing, and the heat.

The density and speed registers give the host two knobs, but they are global: they set one energy level for the entire page. The printer has no notion of which dots are text and which are photograph. It receives a bitmap and burns it.

The next question belongs to software. Given a device that can only burn or refrain, and a page that carries two hundred fifty-six levels of gray, how should the host choose which dots to burn? The answer is dithering, and the article that follows develops it from the same physical first principles we have used here — because on thermal paper, the right dithering algorithm is not the one that is most tonally accurate. It is the one that compensates for what this hardware does to a dot.
