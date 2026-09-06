#pragma once
#include "srpc/keyboard.hpp"
#include "driver/i2c_master.h"
#include "esp_timer.h"
#include <array>
#include <cstdio>

namespace bench {
// Synchronous bounded polling on the existing I2C0 bus, by the same owner task.
// TI SCPS215G section 8.6.4: overflow detection needs CFG bits 3 AND 5.
class Keyboard {
    i2c_master_dev_handle_t device_ = nullptr;
    srpc::ui::KeyEdges edges_;
    int64_t next_poll_ = 0;
    esp_err_t error_ = ESP_ERR_INVALID_STATE;
    unsigned events_ = 0, overflows_ = 0;
    bool access(esp_err_t error) {
        if (error == ESP_OK) return true;
        error_ = error; edges_.clear();
        std::printf("UI KEYBOARD fault=%s events=%u overflows=%u\n", esp_err_to_name(error), events_, overflows_);
        return false;
    }
    bool read(uint8_t reg, uint8_t& value) {
        return access(i2c_master_transmit_receive(device_, &reg, 1, &value, 1, 5));
    }
    bool write(uint8_t reg, uint8_t value) {
        const uint8_t bytes[] = {reg, value};
        return access(i2c_master_transmit(device_, bytes, sizeof(bytes), 5));
    }
public:
    bool begin() {
        if (device_) return healthy(); // Explicit single initialization; fault remains latched.
        i2c_master_bus_handle_t bus = nullptr;
        if (!access(i2c_master_get_bus_handle(I2C_NUM_0, &bus))) return false;
        i2c_device_config_t config{};
        config.dev_addr_length = I2C_ADDR_BIT_LEN_7;
        config.device_address = 0x34; config.scl_speed_hz = 100000;
        if (!access(i2c_master_bus_add_device(bus, &config, &device_))) return false;
        // Disable event IRQs while initializing. Matrix pins are keypad-controlled;
        // unused GPIOs neither create events nor claim output pins.
        if (!write(0x01, 0) || !write(0x1a, 0) || !write(0x1b, 0) || !write(0x1c, 0) ||
            !write(0x20, 0) || !write(0x21, 0) || !write(0x22, 0) ||
            !write(0x1d, 0x7f) || !write(0x1e, 0xff) || !write(0x1f, 0)) return false;
        uint8_t value = 0;
        // FIFO capacity is ten; initialization never drains indefinitely.
        for (unsigned i = 0; i < 10; ++i) if (!read(0x04, value)) return false;
        if (!write(0x02, 0x1f) || !write(0x01, 0x29)) return false;
        if (!read(0x01, value) || value != 0x29) return access(ESP_ERR_INVALID_RESPONSE);
        if (!read(0x1d, value) || value != 0x7f) return access(ESP_ERR_INVALID_RESPONSE);
        if (!read(0x1e, value) || value != 0xff) return access(ESP_ERR_INVALID_RESPONSE);
        error_ = ESP_OK;
        std::puts("UI KEYBOARD ready=1 addr=0x34 matrix=7x8 cfg=0x29 polling=1");
        return true;
    }
    bool healthy() const noexcept { return error_ == ESP_OK; }
    unsigned events() const noexcept { return events_; }
    unsigned overflows() const noexcept { return overflows_; }
    esp_err_t error() const noexcept { return error_; }
    // At most four event reads per 10 ms poll. Failure/overflow latches the input
    // offline until reboot: never execute uncertain FIFO contents after lost edges.
    size_t poll(std::array<srpc::ui::KeyEvent, 4>& output) {
        const auto now = esp_timer_get_time();
        if (!healthy() || now < next_poll_) return 0;
        next_poll_ = now + 10000;
        uint8_t status = 0, count = 0;
        if (!read(0x02, status)) return 0;
        if (status & 8) { ++overflows_; access(ESP_ERR_INVALID_RESPONSE); return 0; }
        if (!read(0x03, count)) return 0;
        count &= 15;
        if (count > 10) { access(ESP_ERR_INVALID_RESPONSE); return 0; }
        if (!count) return 0;
        size_t size = 0;
        for (unsigned i = 0; i < count && i < output.size(); ++i) {
            uint8_t raw = 0;
            if (!read(0x04, raw)) return 0;
            srpc::ui::KeyEvent event;
            if (!srpc::ui::decode_key(raw, event)) { access(ESP_ERR_INVALID_RESPONSE); return 0; }
            if (edges_.accept(raw, event)) {
                output[size++] = event; ++events_;
                std::printf("UI KEY source=physical raw=%u pos=%u key=%u pressed=%u at_us=%llu\n",
                    unsigned(raw), unsigned(event.position), unsigned(uint8_t(event.key)), unsigned(event.pressed),
                    (unsigned long long)esp_timer_get_time());
            }
        }
        // Detect overflow during reads before delivering any actions to the app.
        if (!read(0x02, status)) return 0;
        if (status & 8) { ++overflows_; access(ESP_ERR_INVALID_RESPONSE); return 0; }
        if (!write(0x02, 1)) return 0;
        return size;
    }
};
} // namespace bench
