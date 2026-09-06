#pragma once
#include "radio_probe.hpp"
#include "srpc/radio.hpp"
#include "freertos/semphr.h"
#include <algorithm>

namespace bench {
// Static lifetime; all methods except irq() run on the sole persistent owner task.
class PacketRadio {
    RadioProbe& bus_ = RadioProbe::instance();
    StaticSemaphore_t wake_storage_{};
    SemaphoreHandle_t wake_ = nullptr;
    sl::OwnedBuffer tx_owner_;
    bool armed_ = false, fault_ = false, suppress_done_ = false;
    srpc::Time expires_ = 0, next_tx_ = 0, tx_deadline_ = 0;
    unsigned remaining_ = 0;
    portMUX_TYPE irq_lock_ = portMUX_INITIALIZER_UNLOCKED;
    int64_t irq_at_ = 0, tx_at_ = 0;
    static void irq(void* arg) {
        auto* self = static_cast<PacketRadio*>(arg);
        portENTER_CRITICAL_ISR(&self->irq_lock_);
        self->irq_at_ = esp_timer_get_time();
        portEXIT_CRITICAL_ISR(&self->irq_lock_);
        BaseType_t woken = pdFALSE;
        xSemaphoreGiveFromISR(self->wake_, &woken);
        portYIELD_FROM_ISR(woken);
    }
    bool fail(esp_err_t error) {
        fault_ = true; armed_ = false;
        gpio_set_level(GPIO_NUM_3, 0);
        std::printf("RADIO FAULT error=%s quarantined=%u spi_poisoned=%u\n",
            esp_err_to_name(error), unsigned(tx_owner_.valid()), unsigned(bus_.poisoned_));
        return false; // Retain both SPI storage and any owner until reboot.
    }
    bool command(const srpc::RadioCommand& cmd) {
        if (fault_) return false;
        const auto error = bus_.exchange(cmd);
        return error == ESP_OK || fail(error);
    }
    bool modify(uint16_t address, uint8_t clear, uint8_t set) {
        if (!command(srpc::radio_command(0x1d, address >> 8, address, 0, 0))) return false;
        const uint8_t value = (bus_.rx_[4] & ~clear) | set;
        return command(srpc::radio_command(0x0d, address >> 8, address, value));
    }
    bool expander(uint8_t reg, bool set) {
        uint8_t value = 0;
        auto error = i2c_master_transmit_receive(bus_.expander_, &reg, 1, &value, 1, 100);
        if (error != ESP_OK) return fail(error);
        const uint8_t bytes[] = {reg, uint8_t(set ? value | 1 : value & ~1)};
        error = i2c_master_transmit(bus_.expander_, bytes, 2, 100);
        return error == ESP_OK || fail(error);
    }
    bool standby() {
        if (!command(srpc::radio_command(0x80, 1)) || !command(srpc::radio_command(0xc0, 0))) return false;
        const auto status = bus_.rx_[1];
        const unsigned code = (status >> 1) & 7;
        return (((status >> 4) & 7) == 3 && !(code >= 3 && code <= 5)) || fail(ESP_ERR_INVALID_RESPONSE);
    }
    bool packet_length(size_t size) {
        return command(srpc::radio_command(0x8c, 0, 8, 0, size, 1, 0));
    }
public:
    enum class Event { None, Received, Done, Recovered, Fault };
    unsigned tx_count = 0, rx_count = 0, recoveries = 0, bad_rx = 0, irq_wakes = 0;
    unsigned sf = 7;
    int rssi = 0, snr_quarters = 0;
    uint64_t expected_airtime = 0, last_tx_edge_us = 0;
    size_t last_tx_size = 0;
    PacketRadio() = default;
    PacketRadio(const PacketRadio&) = delete;
    PacketRadio& operator=(const PacketRadio&) = delete;
    bool busy() const { return tx_owner_.valid(); }
    bool armed() const { return armed_; }
    bool fault() const { return fault_; }
    unsigned remaining_starts() const { return remaining_; }
    srpc::Time arm_deadline() const { return expires_; }
    bool eligible(srpc::Time now) const { return armed_ && !fault_ && !busy() && now < expires_ && remaining_ && now >= next_tx_; }
    bool receive() {
        return armed_ && !busy() && standby() && packet_length(128) &&
            command(srpc::radio_command(0x02, 0xff, 0xff)) &&
            command(srpc::radio_command(0x82, 0xff, 0xff, 0xff));
    }
    bool arm(unsigned spreading) {
        if (fault_ || busy() || armed_ || (spreading != 7 && spreading != 9)) return false;
        if (!wake_) {
            wake_ = xSemaphoreCreateBinaryStatic(&wake_storage_);
            auto error = gpio_install_isr_service(0);
            if (error != ESP_OK && error != ESP_ERR_INVALID_STATE) return fail(error);
            error = gpio_isr_handler_add(GPIO_NUM_4, irq, this);
            if (error != ESP_OK) return fail(error);
            error = gpio_set_intr_type(GPIO_NUM_4, GPIO_INTR_POSEDGE);
            if (error != ESP_OK) return fail(error);
        }
        // Preserve all other expander pins. Enable only the carrier RF front end.
        if (!expander(0x05, false) || !expander(0x03, true) || !expander(0x07, false) || !expander(0x05, true)) return false;
        sf = spreading;
        if (!standby() ||
            !command(srpc::radio_command(0x8b, sf, 6, 1, 0)) ||
            !command(srpc::radio_command(0x9d, 1)) || // DIO2 controls the RF switch.
            !command(srpc::radio_command(0x95, 2, 2, 0, 1)) || // SX1262 +14 dBm PA configuration, operated at 0 dBm.
            !command(srpc::radio_command(0x8e, 0, 4)) || // 0 dBm, 200 us ramp.
            !modify(0x08d8, 0, 0x1e) || // PA clamp workaround.
            !modify(0x0889, 4, 0) || // BW500 modulation-quality workaround.
            !modify(0x0736, 0, 4) || // Normal-IQ workaround.
            !command(srpc::radio_command(0x93, 0x30)) || // Automatic fallback STDBY_XOSC.
            !command(srpc::radio_command(0x08, 2, 0x63, 2, 0x63, 0, 0, 0, 0))) return false;
        armed_ = true; expires_ = esp_timer_get_time() + 600000000ULL; remaining_ = 128;
        return receive();
    }
    bool stop() {
        if (fault_) return false;
        if (!standby() || !command(srpc::radio_command(0x02, 0xff, 0xff))) return false;
        if (busy()) { tx_owner_.reset(); ++recoveries; }
        armed_ = false;
        return expander(0x05, false);
    }
    // Accepted consumes input; Busy/Ineligible preserve it. Uncertain failures
    // after consumption quarantine it rather than pretending the driver finished.
    bool start(sl::OwnedBuffer& input, srpc::Time now, bool suppress_done = false,
               srpc::Time start_deadline = UINT64_MAX) {
        if (!eligible(now) || !input.valid() || input.size() < 1 || input.size() > 128) return false;
        if (!standby() || !packet_length(input.size()) || !command(srpc::radio_command(0x02, 0xff, 0xff))) return false;
        tx_owner_ = std::move(input);
        for (size_t offset = 0; offset < tx_owner_.size();) {
            srpc::RadioCommand cmd{}; const auto count = std::min(size_t(14), tx_owner_.size() - offset);
            cmd.bytes[0] = 0x0e; cmd.bytes[1] = uint8_t(offset); cmd.size = count + 2;
            for (size_t i = 0; i < count; ++i) sl::require(tx_owner_.read(offset + i, cmd.bytes[i + 2]));
            if (!command(cmd)) return false;
            offset += count;
        }
        if (srpc::Time(esp_timer_get_time()) >= start_deadline) {
            // FIFO copies completed, but SetTx was never issued; safe NotSent path.
            tx_owner_.reset(); receive(); return false;
        }
        suppress_done_ = suppress_done;
        // Hardware timeout 1 second; owner recovery after 1.2 seconds.
        tx_deadline_ = esp_timer_get_time() + 1200000;
        next_tx_ = now + 250000; --remaining_; ++tx_count;
        last_tx_size = tx_owner_.size();
        sl::require(srpc::airtime_bw500_us(last_tx_size, sf, expected_airtime));
        tx_at_ = esp_timer_get_time();
        return command(srpc::radio_command(0x83, 0, 0xfa, 0));
    }
    Event poll(srpc::Packet& packet) {
        if (fault_) return Event::Fault;
        if (!armed_) return Event::None;
        const auto now = srpc::Time(esp_timer_get_time());
        if (busy() && now >= tx_deadline_) {
            if (!standby() || !command(srpc::radio_command(0x02, 0xff, 0xff))) return Event::Fault;
            tx_owner_.reset(); ++recoveries;
            if (!receive()) return Event::Fault;
            return Event::Recovered;
        }
        if (!busy() && now >= expires_) { stop(); return Event::None; }
        const bool woke = xSemaphoreTake(wake_, 0) == pdTRUE;
        if (woke) ++irq_wakes;
        if (!woke && !gpio_get_level(GPIO_NUM_4)) return Event::None;
        if (!command(srpc::radio_command(0x12, 0, 0, 0))) return Event::Fault;
        const uint16_t flags = uint16_t(bus_.rx_[2]) << 8 | bus_.rx_[3];
        if (!flags) return Event::None;
        if (busy()) {
            if ((flags & 1) && !suppress_done_) {
                // TxDone certifies the chip no longer uses this transmission.
                portENTER_CRITICAL(&irq_lock_);
                const auto edge = irq_at_;
                portEXIT_CRITICAL(&irq_lock_);
                last_tx_edge_us = edge >= tx_at_ ? uint64_t(edge - tx_at_) : 0;
                tx_owner_.reset();
                if (!receive()) return Event::Fault;
                return Event::Done;
            }
            return Event::None; // Missing TxDone/timeout is recovered by verified standby above.
        }
        if (!(flags & 2) || (flags & 0x60)) {
            ++bad_rx; if (!receive()) return Event::Fault;
            return Event::None;
        }
        if (!standby() || !command(srpc::radio_command(0x13, 0, 0, 0))) return Event::Fault;
        const size_t size = bus_.rx_[2]; const uint8_t start = bus_.rx_[3];
        if (!size || size > packet.bytes.size()) { ++bad_rx; receive(); return Event::None; }
        packet = {}; packet.size = size;
        for (size_t offset = 0; offset < size;) {
            srpc::RadioCommand cmd{}; const auto count = std::min(size_t(13), size - offset);
            cmd.bytes[0] = 0x1e; cmd.bytes[1] = uint8_t(start + offset); cmd.size = count + 3;
            if (!command(cmd)) return Event::Fault;
            for (size_t i = 0; i < count; ++i) packet.bytes[offset + i] = bus_.rx_[i + 3];
            offset += count;
        }
        if (!command(srpc::radio_command(0x14, 0, 0, 0, 0))) return Event::Fault;
        rssi = -int(bus_.rx_[2]) / 2; snr_quarters = int8_t(bus_.rx_[3]);
        ++rx_count;
        if (!receive()) return Event::Fault;
        return Event::Received;
    }
};
} // namespace bench
