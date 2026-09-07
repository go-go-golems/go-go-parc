#pragma once
#include "srpc/codec.hpp"
namespace srpc {
inline bool airtime_us(size_t length, unsigned sf, Time& output) noexcept {
    if (length > 128 || (sf != 7 && sf != 9)) return false;
    const int numerator = int(8 * length) - int(4 * sf) + 44;
    const unsigned groups = numerator <= 0 ? 0 : (unsigned(numerator) + 4 * sf - 1) / (4 * sf);
    const Time quarter_symbols = 32 + 17 + 4 * (8 + 5 * groups);
    output = quarter_symbols * (8 * (Time(1) << sf)) / 4;
    return true;
}
// Same restricted LoRa parameters, but physical bench BW500 instead of BW125.
// Excludes ramp, synthesizer/TCXO startup and IRQ delivery latency.
inline bool airtime_bw500_us(size_t length, unsigned sf, Time& output) noexcept {
    Time value;
    if (!airtime_us(length, sf, value)) return false;
    output = value / 4; return true;
}
inline bool add_time(Time a, Time b, Time& out) noexcept {
    if (a > UINT64_MAX - b) return false;
    out = a + b; return true;
}
// Simulation-only permit; the physical driver uses a separate bounded bench arm.
class SimulationPacing {
    uint32_t ppm_;
    Time expires_, next_ = 0;
    bool enabled_;
public:
    SimulationPacing(uint32_t duty_ppm = 1000000, Time expires = UINT64_MAX, bool enabled = true) noexcept
        : ppm_(duty_ppm), expires_(expires), enabled_(enabled) {}
    bool eligible(Time now) const noexcept { return enabled_ && ppm_ && ppm_ <= 1000000 && now < expires_ && now >= next_; }
    bool reserve(Time now, Time duration) noexcept {
        if (!eligible(now) || duration == 0 || duration > (UINT64_MAX - 999999) / 1000000) return false;
        Time end;
        if (!add_time(now, duration, end) || end > expires_) return false;
        const Time period = (duration * 1000000 + ppm_ - 1) / ppm_;
        Time next;
        if (!add_time(now, period, next)) return false;
        next_ = next; return true;
    }
    Time next_eligible() const noexcept { return next_; }
};
} // namespace srpc
