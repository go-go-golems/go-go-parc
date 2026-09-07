#pragma once
#include <array>
#include <cstddef>
#include <cstdint>
namespace srpc {
struct RadioCommand {
    std::array<uint8_t, 16> bytes{};
    size_t size = 0;
};
template<class... Bytes> constexpr RadioCommand radio_command(Bytes... bytes) {
    static_assert(sizeof...(bytes) > 0 && sizeof...(bytes) <= 16);
    return {{uint8_t(bytes)...}, sizeof...(bytes)};
}
// Candidate bench PHY, not a certified operating profile. No RX/TX/PA or
// antenna-switch enable commands. Exact 915MHz FRF = 915e6 * 2^25 / 32e6.
constexpr uint32_t bench_frequency_hz = 915000000;
constexpr uint32_t bench_frf = uint32_t(uint64_t(bench_frequency_hz) * (1u << 25) / 32000000);
constexpr std::array<RadioCommand, 11> standby_profile{{
    radio_command(0x97, 0x06, 0x00, 0x02, 0x80), // Board TCXO 3.0V, 10ms startup.
    radio_command(0x07, 0x00, 0x00),             // Clear expected cold-start error.
    radio_command(0x89, 0x7f),                   // Calibrate all in STDBY_RC.
    radio_command(0x98, 0xe1, 0xe9),             // Image calibration, 902-928MHz.
    radio_command(0x8a, 0x01),                   // LoRa packet type.
    radio_command(0x86, bench_frf >> 24, bench_frf >> 16, bench_frf >> 8, bench_frf),
    radio_command(0x8b, 7, 0x06, 1, 0),         // SF7, BW500, CR4/5, LDRO off.
    radio_command(0x8c, 0, 8, 0, 128, 1, 0),    // Preamble8, explicit, max128, CRC, normal IQ.
    radio_command(0x8f, 0x00, 0x80),             // TX/RX buffer base addresses only.
    radio_command(0x0d, 0x07, 0x40, 0x14, 0x24),// Private LoRa sync word registers.
    radio_command(0x80, 0x01),                   // Remain in STDBY_XOSC, never SetTx/SetRx.
}};
constexpr bool non_transmitting_opcode(uint8_t opcode) noexcept {
    switch (opcode) {
        case 0x97: case 0x07: case 0x89: case 0x98: case 0x8a: case 0x86:
        case 0x8b: case 0x8c: case 0x8f: case 0x0d: case 0x80: return true;
        default: return false;
    }
}
constexpr bool valid_standby_readback(uint8_t status, uint16_t errors,
                                      uint8_t packet_type, uint16_t sync_word) noexcept {
    const unsigned command = (status >> 1) & 7;
    return (status & 0x81) == 0 && ((status >> 4) & 7) == 3 &&
        !(command >= 3 && command <= 5) && errors == 0 &&
        packet_type == 1 && sync_word == 0x1424;
}
} // namespace srpc
