#pragma once
#include "bench_identity.hpp"
#include "srpc/console.hpp"
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
        canvas_.fillRect(0, 0, 240, 23, 0x1a2540u);
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
        canvas_.fillRect(7, 85, 226, 4, 0x26334du);
        const unsigned done = calls_ > total_ ? total_ : calls_;
        if (total_) canvas_.fillRect(7, 85, int(226u * done / total_), 4, accent);
        std::snprintf(line, sizeof(line), "OK %u", ok_); small(7, 95, line, 0x74e39a);
        std::snprintf(line, sizeof(line), "UNKNOWN %u", unknown_); small(117, 95, line, 0xffc857);
        small(7, 108, nvs_, 0xaab8d2);
        std::snprintf(line, sizeof(line), "PEER %s %s: %s", identity_.peer, identity_.peer_suffix, seen_ ? "FRAME RX" : "UNTESTED");
        small(7, 122, line, 0xaab8d2);
        canvas_.pushSprite(0, 0); lcd_.waitDMA();
    }
    void console(const srpc::ui::Console& model, const srpc::ui::RuntimeStatus& state) {
        if (!ready_) return;
        using namespace srpc::ui;
        const uint32_t accent = state.board == 'B' ? 0xcf8bffu : 0x36c9eeu;
        const uint32_t muted = 0xaab8d2u, good = 0x74e39au, warn = 0xffc857u, bad = 0xff6868u;
        canvas_.fillScreen(background);
        canvas_.fillRect(0, 0, 240, 17, 0x1a2540u);
        char text[80];
        std::snprintf(text, sizeof(text), "RPC %c > N%u", state.board, unsigned(state.peer)); small(5, 5, text, accent);
        std::snprintf(text, sizeof(text), "SF%u %s", state.sf, state.fault ? "FAULT" : state.armed ? "RF ON" : "RF OFF");
        small(157, 5, text, state.fault ? bad : state.armed ? good : muted);
        constexpr const char* tabs[] = {"SERVICES", "ACTIVITY", "SETUP"};
        for (unsigned i = 0; i < 3; ++i) {
            const bool selected = i == unsigned(model.page());
            if (selected) canvas_.fillRoundRect(4 + i * 79, 21, 74, 13, 2, 0x26334du);
            small(10 + i * 79, 24, tabs[i], selected ? accent : muted);
        }
        auto age = [&](srpc::Time at) { return (unsigned long long)((state.now >= at ? state.now - at : 0) / 1000000); };
        const auto* active = model.active();
        const auto* last = model.newest();
        if (model.page() == Page::Dashboard && !model.detail()) {
            const auto& sensor = model.sensor(); const auto& led = model.led(); const auto& health = model.health();
            for (unsigned row = 0; row < 3; ++row) {
                const int y = 39 + row * 20;
                const bool selected = model.selection() == row;
                if (selected) canvas_.fillRoundRect(4, y - 2, 232, 19, 3, 0x1a2540u);
                small(8, y + 3, selected ? ">" : " ", accent);
                small(19, y + 3, row == 0 ? "SAMPLE" : row == 1 ? "LED STATE" : "HEALTH", muted);
                if (row == 0) {
                    if (sensor.known) std::snprintf(text, sizeof(text), "%ld / %llus", long(sensor.value), age(sensor.at));
                    else std::snprintf(text, sizeof(text), "-- synthetic");
                } else if (row == 1) {
                    if (led.known) std::snprintf(text, sizeof(text), "%s %s", led.value ? "ON" : "OFF", model.led_uncertain() ? "?" : "observed");
                    else std::snprintf(text, sizeof(text), "%s", model.led_uncertain() ? "UNKNOWN" : "-- not read");
                } else {
                    if (health.known) std::snprintf(text, sizeof(text), "%lus uptime", (unsigned long)(health.sequence / 1000));
                    else std::snprintf(text, sizeof(text), "-- not read");
                }
                small(112, y + 3, text, row == 1 && model.led_uncertain() ? warn : white);
            }
        } else if (model.page() == Page::Dashboard) {
            if (model.selection() == 1) {
                small(8, 41, "REMOTE LED INTEGER STATE", accent);
                std::snprintf(text, sizeof(text), "Observed: %s", !model.led().known ? "not read" : model.led().value ? "ON" : "OFF");
                small(8, 55, text);
                small(8, 68, model.led_uncertain() ? "Unknown write may have happened" : "Not a physical GPIO LED", model.led_uncertain() ? warn : muted);
                small(8, 82, "[0] SET OFF  [1] SET ON  [R] READ", accent);
            } else if (model.selection() == 0) {
                small(8, 41, "SYNTHETIC SENSOR", accent);
                std::snprintf(text, sizeof(text), "Value %ld / sequence %lu", long(model.sensor().value), (unsigned long)model.sensor().sequence);
                small(8, 55, model.sensor().known ? text : "No confirmed sample yet");
                std::snprintf(text, sizeof(text), "Observed %llus ago", age(model.sensor().at));
                small(8, 68, model.sensor().known ? text : "No hardware calibration claim", muted);
                small(8, 82, "[S] FETCH SAMPLE   [DEL] BACK", accent);
            } else {
                small(8, 41, "REMOTE HEALTH", accent);
                std::snprintf(text, sizeof(text), "Uptime %lu ms", (unsigned long)model.health().sequence);
                small(8, 55, model.health().known ? text : "No confirmed health yet");
                std::snprintf(text, sizeof(text), "Service generation %lu", (unsigned long)model.health().generation); small(8, 68, text, muted);
                small(8, 82, "[H] FETCH HEALTH   [DEL] BACK", accent);
            }
        } else if (model.page() == Page::History) {
            const auto* selected = model.selected();
            if (!selected) small(8, 47, "No completed calls yet", muted);
            else if (model.detail()) {
                std::snprintf(text, sizeof(text), "#%lu %s %s", (unsigned long)selected->request, service_name(selected->service), outcome_name(selected->outcome)); small(8, 41, text, accent);
                std::snprintf(text, sizeof(text), "%llums / %u attempts", (unsigned long long)((selected->ended - selected->started) / 1000), selected->attempts); small(8, 54, text);
                std::snprintf(text, sizeof(text), "Peer N%u epoch %llu", unsigned(selected->binding.server), (unsigned long long)selected->binding.server_boot); small(8, 67, text, muted);
                small(8, 81, selected->outcome == srpc::Outcome::OutcomeUnknown ? "May have executed; READ to check" : selected->outcome == srpc::Outcome::NotSent ? "No physical attempt started" : "Result matched this call identity", selected->outcome == srpc::Outcome::OutcomeUnknown ? warn : muted);
            } else {
                const size_t offset = model.selected_offset();
                const size_t first = offset / 4 * 4;
                for (size_t i = 0; i < 4; ++i) {
                    const auto* record = model.newest(first + i); if (!record) break;
                    const int y = 40 + i * 14;
                    if (record == selected) canvas_.fillRect(4, y - 2, 232, 13, 0x1a2540u);
                    std::snprintf(text, sizeof(text), "%c%lu %-8s %-8s x%u", record == selected ? '>' : ' ', (unsigned long)record->request,
                        service_name(record->service), outcome_name(record->outcome), record->attempts);
                    small(7, y, text, record->outcome == srpc::Outcome::Ok ? good : warn);
                }
            }
        } else {
            std::snprintf(text, sizeof(text), "LOCAL N%u / E%llu", unsigned(state.node), (unsigned long long)state.epoch); small(8, 40, text, accent);
            std::snprintf(text, sizeof(text), "PEER N%u / E%llu", unsigned(state.peer), (unsigned long long)state.peer_epoch); small(8, 53, text);
            small(8, 66, state.bound ? "BOUND / P2 UNAUTHENTICATED" : "USB: provision + reciprocal bind", state.bound ? warn : muted);
            small(8, 79, "915 MHz BW500 0 dBm / USB arm", muted);
        }
        canvas_.drawFastHLine(5, 99, 230, 0x26334du);
        if (state.fault) std::snprintf(text, sizeof(text), "RADIO FAULT / REBOOT / OWNER %u", unsigned(state.busy));
        else if (active) std::snprintf(text, sizeof(text), "#%lu %s x%u %s", (unsigned long)active->request,
            state.transmitting_call ? "TRANSMITTING" : active->attempts ? "WAIT REPLY" : "QUEUED", active->attempts, !state.armed ? "RF OFF" : "");
        else if (state.busy) std::snprintf(text, sizeof(text), "Call ended; radio finishing");
        else if (last) std::snprintf(text, sizeof(text), "%s %llums x%u", outcome_name(last->outcome), (unsigned long long)((last->ended - last->started) / 1000), last->attempts);
        else std::snprintf(text, sizeof(text), "%s", model.notice(state.now));
        small(7, 104, text, state.fault ? bad : active || state.busy ? warn : white);
        small(7, 115, !state.key_ok ? "KEYBOARD FAULT / USB ONLY" : model.notice(state.now), !state.key_ok ? bad : muted);
        small(7, 126, model.detail() ? "DEL back  TAB page  X stop" : model.page() == Page::Dashboard ? "S L H  ; . select  ENTER  TAB  X" : "; . select  ENTER  TAB  X stop", accent);
        canvas_.pushSprite(0, 0); lcd_.waitDMA();
    }
    void keyboard_check(bool healthy, unsigned events, unsigned position, unsigned key, bool pressed, bool armed) {
        if (!ready_) return;
        const uint32_t accent = identity_.label == 'B' ? 0xcf8bff : 0x36c9ee;
        canvas_.fillScreen(background);
        canvas_.fillRect(0, 0, 240, 24, 0x1a2540u);
        canvas_.setFont(&fonts::Font2); canvas_.setTextSize(1); canvas_.setTextColor(white);
        canvas_.setCursor(7, 3); canvas_.print("RPC / INPUT CHECK");
        canvas_.setTextColor(accent); canvas_.setCursor(219, 3); canvas_.printf("%c", identity_.label);
        small(8, 31, healthy ? "ADV KEYBOARD  /  I2C 0x34" : "KEYBOARD FAULT / REBOOT", healthy ? accent : 0xff6868);
        canvas_.fillRoundRect(8, 47, 224, 44, 5, 0x1a2540u);
        canvas_.setFont(&fonts::Font2); canvas_.setTextColor(white); canvas_.setCursor(17, 50);
        if (!events) canvas_.print("Press a key");
        else if (key == 9) canvas_.print("TAB");
        else if (key == 10) canvas_.print("ENTER");
        else if (key == 8) canvas_.print("DELETE");
        else if (key == 32) canvas_.print("SPACE");
        else if (!key) canvas_.print("MODIFIER");
        else canvas_.printf("%c", char(key));
        char detail[48];
        std::snprintf(detail, sizeof(detail), "POS %02u / %s / EDGES %u", position, pressed ? "DOWN" : "UP", events);
        small(17, 76, detail, 0xaab8d2);
        small(8, 99, "S L H TAB ENTER ; . X", white);
        small(8, 112, "Hold / release: one edge each", 0xaab8d2);
        small(8, 125, armed ? "RF ARMED / USB STOP" : "RF OFF / USB CONTROL PRESERVED", armed ? 0xffc857 : accent);
        canvas_.pushSprite(0, 0); lcd_.waitDMA();
    }
    // Capture the already-rendered sprite, not panel readback (panel is write-only).
    // Owner invokes this only when unarmed, physically idle and no call pending.
    void dump() {
        if (!ready_) { std::puts("UI SCREEN ERROR not_ready"); return; }
        std::puts("UI SCREEN BEGIN width=240 height=135 format=RGB565");
        constexpr char hex[] = "0123456789ABCDEF";
        char row[961];
        for (int y = 0; y < 135; ++y) {
            for (int x = 0; x < 240; ++x) {
                const auto pixel = canvas_.readPixel(x, y);
                for (unsigned digit = 0; digit < 4; ++digit)
                    row[x * 4 + digit] = hex[(pixel >> (12 - digit * 4)) & 15];
            }
            row[960] = 0;
            std::printf("UI SCREEN ROW y=%d data=%s\n", y, row);
            vTaskDelay(1);
        }
        std::puts("UI SCREEN END rows=135");
        std::fflush(stdout);
    }
    void failure(int line) {
        char stage[28]; std::snprintf(stage, sizeof(stage), "FAIL AT LINE %d", line);
        show(stage, false, true);
    }
};
} // namespace bench
