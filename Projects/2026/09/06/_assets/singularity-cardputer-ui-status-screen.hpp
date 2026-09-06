#pragma once
#include "bench_identity.hpp"
#include <M5GFX.h>
#include <lgfx/v1/panel/Panel_ST7789.hpp>
#include <cstdio>

namespace bench {
// Explicit panel configuration avoids M5GFX autodetection, which can probe GPIO5/6
// (radio CS/BUSY on the Cap). LCD is on SPI2; reserve SPI3 for future SX1262 use.
class CardputerLcd final : public lgfx::LGFX_Device {
    lgfx::Bus_SPI bus_;
    lgfx::Panel_ST7789 panel_;
    lgfx::Light_PWM light_;
public:
    CardputerLcd() {
        auto bus = bus_.config();
        bus.spi_host = SPI2_HOST;
        bus.spi_mode = 0; bus.freq_write = 40000000; bus.freq_read = 16000000;
        bus.pin_sclk = 36; bus.pin_mosi = 35; bus.pin_miso = -1; bus.pin_dc = 34;
        bus.spi_3wire = true; bus.use_lock = true;
        bus_.config(bus); panel_.setBus(&bus_);
        auto panel = panel_.config();
        panel.pin_cs = 37; panel.pin_rst = 33;
        panel.panel_width = 135; panel.panel_height = 240;
        panel.offset_x = 52; panel.offset_y = 40;
        panel.invert = true; panel.readable = false; panel.bus_shared = false;
        panel_.config(panel);
        auto light = light_.config();
        light.pin_bl = 38; light.invert = false; light.freq = 1200; light.pwm_channel = 7;
        light_.config(light); panel_.setLight(&light_); setPanel(&panel_);
    }
};
class Screen {
    CardputerLcd lcd_;
    lgfx::LGFX_Sprite canvas_{&lcd_};
    Identity identity_{'?', "?", "UNKNOWN"};
    char mac_[18]{};
    const char* nvs_ = "NVS UNCHECKED";
    char radio_[14] = "NOT PROBED";
    bool radio_ok_ = false;
    unsigned calls_ = 0, ok_ = 0, unknown_ = 0, total_ = 6000;
    bool ready_ = false, physical_ = false, armed_ = false, seen_ = false;
    static constexpr uint32_t background = 0x0b1020, white = 0xeef3ff;
    void small(int x, int y, const char* text, uint32_t color = white) {
        canvas_.setFont(&fonts::Font0); canvas_.setTextSize(1);
        canvas_.setTextColor(color); canvas_.setCursor(x, y); canvas_.print(text);
    }
public:
    bool begin(Identity identity, const char* mac, const char* nvs) {
        identity_ = identity; std::snprintf(mac_, sizeof(mac_), "%s", mac); nvs_ = nvs;
        if (!lcd_.init()) return false;
        lcd_.setRotation(1); lcd_.setBrightness(180); lcd_.setColorDepth(16);
        if (lcd_.width() != 240 || lcd_.height() != 135) return false;
        canvas_.setColorDepth(16); canvas_.setPsram(false);
        if (!canvas_.createSprite(240, 135)) return false;
        canvas_.setTextWrap(false, false); ready_ = true;
        show("STARTING TESTS"); return true;
    }
    void radio_status(uint8_t status, bool ok, bool held) {
        radio_ok_ = ok;
        std::snprintf(radio_, sizeof(radio_), !ok ? "SX ERR %02X" : held ? "SX %02X HELD" : "SX %02X XOSC", unsigned(status));
    }
    void physical(bool armed, bool seen, unsigned sf, const char* identity) {
        physical_ = true; armed_ = armed; seen_ = seen; nvs_ = identity;
        std::snprintf(radio_, sizeof(radio_), "SF%u BW500", sf);
        radio_ok_ = armed;
    }
    void counts(unsigned calls, unsigned ok, unsigned unknown, unsigned total) {
        calls_ = calls; ok_ = ok; unknown_ = unknown; total_ = total;
    }
    void show(const char* stage, bool passed = false, bool failed = false) {
        if (!ready_) return;
        const uint32_t accent = identity_.label == 'A' ? 0x36c9ee : identity_.label == 'B' ? 0xcf8bff : 0xffc857;
        canvas_.fillScreen(background);
        canvas_.fillRect(0, 0, 240, 23, 0x1a2540);
        canvas_.setFont(&fonts::Font2); canvas_.setTextSize(1); canvas_.setTextColor(white);
        canvas_.setCursor(6, 3); canvas_.print("SINGULARITY RPC");
        canvas_.fillRoundRect(207, 2, 28, 19, 3, accent);
        canvas_.setTextColor(background); canvas_.setCursor(216, 3); canvas_.printf("%c", identity_.label);
        small(7, 27, mac_, accent);
        small(158, 27, radio_, radio_ok_ ? 0x74e39a : 0xffc857);
        small(7, 40, physical_ ? "915 MHz / 0 dBm" : "FAKE LINK", 0xffc857);
        small(162, 40, armed_ ? "RF ARMED" : "RF OFF", armed_ ? 0x74e39a : 0xff8e89);
        canvas_.setFont(&fonts::Font2); canvas_.setTextColor(failed ? 0xff6868 : passed ? 0x74e39a : white);
        canvas_.setCursor(7, 52); canvas_.print(stage);
        char line[40];
        std::snprintf(line, sizeof(line), "%u / %u CALLS", calls_, total_); small(7, 73, line);
        canvas_.fillRect(7, 85, 226, 4, 0x26334d);
        const unsigned done = calls_ > total_ ? total_ : calls_;
        if (total_) canvas_.fillRect(7, 85, int(226u * done / total_), 4, accent);
        std::snprintf(line, sizeof(line), "OK %u", ok_); small(7, 95, line, 0x74e39a);
        std::snprintf(line, sizeof(line), "UNKNOWN %u", unknown_); small(117, 95, line, 0xffc857);
        small(7, 108, nvs_, 0xaab8d2);
        std::snprintf(line, sizeof(line), "PEER %s %s: %s", identity_.peer, identity_.peer_suffix, seen_ ? "FRAME RX" : "UNTESTED");
        small(7, 122, line, 0xaab8d2);
        canvas_.pushSprite(0, 0); lcd_.waitDMA();
    }
    void failure(int line) {
        char stage[28]; std::snprintf(stage, sizeof(stage), "FAIL AT LINE %d", line);
        show(stage, false, true);
    }
};
} // namespace bench
