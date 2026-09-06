#!/usr/bin/env python3
"""Render reference screens with the original Screen drawing code and M5GFX fonts.

Not physical board screenshots. Hardware begin/flush are replaced; show(), the
state setters and drawing primitives remain the snapshot's implementation.
Requires g++, pkg-config, SDL2 development files, ImageMagick and M5GFX 0.2.27 sources.
Usage: python3 singularity-cardputer-ui-render.py --m5gfx /path/to/m5stack__m5gfx
"""
import argparse
import hashlib
import json
import pathlib
import subprocess
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('--m5gfx', required=True, type=pathlib.Path)
args = parser.parse_args()
source = (HERE / 'singularity-cardputer-ui-status-screen.hpp').read_text()
identity = (HERE / 'singularity-cardputer-ui-bench-identity.hpp').read_text().replace('#pragma once\n', '')
body = source[source.index('class Screen {'):source.rindex('} // namespace bench')]
body = body.replace('    CardputerLcd lcd_;\n', '')
body = body.replace('lgfx::LGFX_Sprite canvas_{&lcd_};', 'lgfx::LGFX_Sprite canvas_;')
start, end = body.index('    bool begin('), body.index('    void radio_status(')
body = body[:start] + '''    bool begin(Identity identity, const char* mac, const char* nvs) {
        identity_ = identity; std::snprintf(mac_, sizeof(mac_), "%s", mac); nvs_ = nvs;
        canvas_.setColorDepth(16); canvas_.setPsram(false);
        if (!canvas_.createSprite(240, 135)) return false;
        canvas_.setTextWrap(false, false); ready_ = true; return true;
    }
    void save(const char* path) {
        FILE* file = std::fopen(path, "wb");
        std::fprintf(file, "P6\\n240 135\\n255\\n");
        for (int y = 0; y < 135; ++y) for (int x = 0; x < 240; ++x) {
            auto c = canvas_.readPixelRGB(x, y);
            uint8_t rgb[] = {c.r, c.g, c.b};
            std::fwrite(rgb, 1, 3, file);
        }
        std::fclose(file);
    }
''' + body[end:]
flush = '        canvas_.pushSprite(0, 0); lcd_.waitDMA();'
assert body.count(flush) == 1
body = body.replace(flush, '        // Host reference: retain the rendered sprite instead of LCD transfer.')
program = '#include <M5GFX.h>\n#include <cstdio>\n' + identity + '\nnamespace bench {\n' + body + '\n}\n'
program += r'''
int main() {
    bench::Screen a, b, unknown;
    if (!a.begin({'A', "B", "A4:FB:7C"}, "AC:A7:04:04:88:F4", "NVS MISSING / UNPROVISIONED")) return 1;
    if (!b.begin({'B', "A", "04:88:F4"}, "D8:85:AC:A4:FB:7C", "N2 E7 EX20 DUP1 L1")) return 1;
    if (!unknown.begin({'?', "?", "UNKNOWN"}, "00:11:22:33:44:55", "NVS UNCHECKED")) return 1;
    a.show("STARTING TESTS"); a.save("startup.ppm");
    a.radio_status(0x32, true, false);
    a.counts(6000, 5720, 280, 6000); a.show("LOCAL SIM PASS", true); a.save("sim-pass.ppm");
    b.physical(true, true, 9, "N2 E7 EX20 DUP1 L1");
    b.counts(20, 20, 0, 128); b.show("RPC READY / SERVING"); b.save("live-b.ppm");
    a.physical(true, true, 7, "N1 E5 EX4 DUP1 L0");
    a.counts(4, 2, 1, 128); a.show("RPC WAITING"); a.save("waiting-a.ppm");
    a.physical(false, true, 9, "N1 E5 EX21 DUP0 L1");
    a.counts(22, 21, 0, 128); a.show("USB: ARM TO TEST"); a.save("disarmed-a.ppm");
    a.show("RADIO FAULT", false, true); a.save("fault-a.ppm");
    unknown.show("STARTING TESTS"); unknown.save("unknown.ppm");
    lgfx::LGFX_Sprite metrics;
    metrics.setFont(&fonts::Font2); metrics.setTextSize(1);
    const char* labels[] = {"SINGULARITY RPC", "RPC READY / SERVING", "USB: ARM TO TEST", "RADIO FAULT", "A", "B"};
    for (auto label : labels) std::printf("METRIC %s\t%d\n", label, int(metrics.textWidth(label)));
    metrics.setColorDepth(16);
    if (!metrics.createSprite(2, 1)) return 2;
    metrics.drawPixel(0, 0, 0x1a2540);
    metrics.drawPixel(1, 0, uint32_t(0x21aad6));
    if (metrics.readPixel(0, 0) != metrics.readPixel(1, 0)) return 3;
    metrics.drawPixel(0, 0, 0x26334d);
    metrics.drawPixel(1, 0, uint32_t(0x316d9c));
    if (metrics.readPixel(0, 0) != metrics.readPixel(1, 0)) return 4;
    std::puts("CHECK explicit RGB888 palette matches both original RGB565 pixels");
}
'''
manifest = (args.m5gfx / 'idf_component.yml').read_text()
if 'version: 0.2.27' not in manifest.splitlines():
    raise SystemExit('Reference rendering requires the pinned M5GFX 0.2.27 component.')
m = args.m5gfx.resolve() / 'src'
cpp = [m / 'lgfx/v1' / name for name in ('LGFXBase.cpp', 'LGFX_Sprite.cpp', 'lgfx_fonts.cpp',
       'misc/pixelcopy.cpp', 'misc/SpriteBuffer.cpp', 'misc/DividedFrameBuffer.cpp',
       'misc/common_function.cpp', 'platforms/sdl/common.cpp')]
with tempfile.TemporaryDirectory(prefix='cardputer-ui-') as temp:
    temp = pathlib.Path(temp)
    (temp / 'render.cpp').write_text(program)
    flags = subprocess.check_output(['pkg-config', '--cflags', '--libs', 'sdl2'], text=True).split()
    cmd = ['g++', '-std=c++17', '-O2', '-ffunction-sections', '-fdata-sections', '-I' + str(m),
           str(temp / 'render.cpp'), *map(str, cpp), '-Wl,--gc-sections', '-pthread', *flags, '-o', str(temp / 'render')]
    subprocess.run(cmd, check=True)
    result = subprocess.run([str(temp / 'render')], cwd=temp, check=True, capture_output=True, text=True)
    metrics = dict(line.removeprefix('METRIC ').split('\t') for line in result.stdout.splitlines() if line.startswith('METRIC '))
    colors = {}
    for p in sorted(temp.glob('*.ppm')):
        raster = p.read_bytes().split(b'\n', 3)[3]
        assert len(raster) == 240 * 135 * 3
        def pixel(x, y):
            offset = (y * 240 + x) * 3
            return list(raster[offset:offset + 3])
        colors[p.stem] = {'background_rgb': pixel(0, 134), 'header_rgb': pixel(0, 0),
                         'bar_right_rgb': pixel(232, 85), 'badge_rgb': pixel(210, 7)}
        assert pixel(0, 134) == [8, 16, 33]
        assert pixel(0, 0) == [33, 170, 214]
        if p.stem == 'live-b':
            assert all(pixel(x, 86) == [206, 138, 255] for x in range(7, 42))
            assert all(pixel(x, 86) == [49, 109, 156] for x in range(42, 233))
        subprocess.run(['convert', str(p), '-filter', 'point', '-resize', '400%', '-strip', '-define', 'png:exclude-chunks=date,time',
                        str(HERE / f'singularity-cardputer-ui-{p.stem}.png')], check=True)
    metadata = {'kind': 'source-rendered reference images, not hardware captures', 'native_size': [240, 135],
                'export_scale': 4, 'scaling': 'nearest-neighbor', 'm5gfx_version': '0.2.27',
                'explicit_palette_equivalence_checked': True,
                'source_sha256': hashlib.sha256(source.encode()).hexdigest(),
                'identity_source_sha256': hashlib.sha256((HERE / 'singularity-cardputer-ui-bench-identity.hpp').read_bytes()).hexdigest(),
                'font2_advance_widths': metrics,
                'raster_colors': colors, 'compile_command': [x.replace(str(temp), '<TEMP>').replace(str(m), '<M5GFX_SRC>') for x in cmd],
                'compiled_library_sources_sha256': {str(p.relative_to(m)): hashlib.sha256(p.read_bytes()).hexdigest() for p in cpp},
                'font_headers_sha256': {name: hashlib.sha256((m / name).read_bytes()).hexdigest() for name in ('lgfx/Fonts/glcdfont.h', 'lgfx/Fonts/Font16.h')},
                'component_manifest_sha256': hashlib.sha256(manifest.encode()).hexdigest()}
    (HERE / 'singularity-cardputer-ui-render-metadata.json').write_text(json.dumps(metadata, indent=2) + '\n')
    print(result.stdout)

# Coordinate figure: the source-rendered B frame, with device-pixel annotations.
import base64
picture = base64.b64encode((HERE / 'singularity-cardputer-ui-live-b.png').read_bytes()).decode()
svg = ['<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="1280" height="640" viewBox="0 0 1280 640">',
       '<rect width="1280" height="640" fill="#ffffff"/>',
       '<g font-family="sans-serif" fill="#172b42">',
       '<text x="35" y="35" font-size="24">Cardputer dashboard: device-pixel coordinate map</text>',
       f'<image xlink:href="data:image/png;base64,{picture}" x="60" y="90" width="720" height="405"/>']
for x in (0, 60, 120, 180, 239):
    svg.append(f'<text x="{60 + x * 3}" y="78" text-anchor="middle" font-size="12">{x}</text>')
for y in (0, 23, 40, 52, 73, 85, 95, 108, 122, 134):
    svg.append(f'<text x="50" y="{94 + y * 3}" text-anchor="end" font-size="12">{y}</text>')
labels = [(12, 'Header: (0,0), 240 x 23; badge: (207,2), 28 x 19'),
          (30, 'MAC: (7,27); radio badge: (158,27)'),
          (43, 'Mode: (7,40); RF state: (162,40)'),
          (59, 'Stage: (7,52), Font2 / 16-pixel line height'),
          (77, 'Call count: (7,73), Font0 / 6-pixel advance'),
          (87, 'Progress: (7,85), width 226, height 4'),
          (98, 'Results: (7,95) and (117,95)'),
          (111, 'Identity / service counters: (7,108)'),
          (125, 'Peer observation: (7,122)')]
for y, label in labels:
    yy = 90 + y * 3
    svg.append(f'<path d="M784 {yy} H808" stroke="#70859b"/>')
    svg.append(f'<text x="820" y="{yy + 5}" font-size="14">{label}</text>')
svg += ['<text x="60" y="550" font-size="17">Native canvas: 240 x 135. Diagram enlarged 3x; coordinates remain native pixels.</text>',
        '<text x="60" y="583" font-size="15">Source-rendered reference, not a physical board capture. Fixed origins; no responsive layout.</text>',
        '</g></svg>']
(HERE / 'singularity-cardputer-ui-coordinate-map.svg').write_text('\n'.join(svg) + '\n')
