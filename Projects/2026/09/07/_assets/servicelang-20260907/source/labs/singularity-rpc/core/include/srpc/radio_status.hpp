#pragma once
#include <cstdint>
namespace srpc {
enum class ProbeState { Standby, TcxoUnconfigured, Fault };
// Semtech DS rev2.2 sections13.3.6/13.5.1/13.6.1. This classifies a
// reset-time diagnostic, not radio readiness or unique silicon identity.
constexpr ProbeState classify_radio_status(uint8_t status, uint16_t errors) noexcept {
    if ((status & 0x81) != 0 || ((status >> 4) & 7) != 2) return ProbeState::Fault;
    const unsigned command = (status >> 1) & 7;
    if (command == 5 && errors == 0x0020) return ProbeState::TcxoUnconfigured;
    // Match the reference RadioLib SPI parser: only codes3/4/5 signal
    // command errors. Hardware can report code1 during successful operation.
    if (errors != 0 || (command >= 3 && command <= 5))
        return ProbeState::Fault;
    return ProbeState::Standby;
}
} // namespace srpc
