#pragma once
#include <array>
#include <cstdint>
namespace bench {
struct Identity {
    char label;
    const char* peer;
    const char* peer_suffix;
};
// Bench labels only: not provisioning, authenticated identity, or link discovery.
inline Identity identify(const std::array<uint8_t, 6>& mac) noexcept {
    constexpr std::array<uint8_t, 6> a{0xac, 0xa7, 0x04, 0x04, 0x88, 0xf4};
    constexpr std::array<uint8_t, 6> b{0xd8, 0x85, 0xac, 0xa4, 0xfb, 0x7c};
    if (mac == a) return {'A', "B", "A4:FB:7C"};
    if (mac == b) return {'B', "A", "04:88:F4"};
    return {'?', "?", "UNKNOWN"};
}
} // namespace bench
