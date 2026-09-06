#pragma once
#include "srpc/console.hpp"

namespace srpc::ui::test {
// Synthetic renderer inputs only. No Client, Server, packet owner or hardware.
// Never use these values as live protocol observations.
struct ConsoleFixture {
    static constexpr unsigned count = 11;
    Console model;
    RuntimeStatus state{};
    Binding binding{65534, 65535, UINT64_MAX - 1, UINT64_MAX, UINT32_MAX, UINT32_MAX};

    void complete(Service service, Outcome outcome, uint32_t request, Time start, bool positive) {
        Frame frame;
        frame.kind = Kind::Reply; frame.service = service; frame.opcode = uint8_t(service);
        frame.source = binding.server; frame.destination = binding.client;
        frame.source_boot = binding.server_boot; frame.destination_boot = binding.client_boot;
        frame.request = request; frame.grant = binding.grant; frame.generation = binding.generation;
        frame.status = outcome == Outcome::RemoteError ? ReplyCode::Internal : ReplyCode::Ok;
        if (outcome != Outcome::RemoteError) {
            if (service == Service::Sensor) {
                frame.length = 8; put(frame.body.data(), 0, UINT32_MAX, 4);
                put(frame.body.data(), 4, positive ? uint32_t(INT32_MAX) : uint32_t(INT32_MIN), 4);
            } else if (service == Service::Health) {
                frame.length = 12; put(frame.body.data(), 0, UINT32_MAX, 4); put(frame.body.data(), 4, UINT32_MAX, 4);
            } else { frame.length = 1; frame.body[0] = 1; }
        }
        sl::require(valid(frame) == Codec::Ok);
        model.started(binding, request, service, 0, start, start + 1000000);
        model.completed({outcome, frame, request, 3}, start + 100000);
    }
    explicit ConsoleFixture(unsigned mode) {
        sl::require(mode < count);
        state.board = 'T'; state.bound = state.key_ok = true;
        state.node = binding.client; state.peer = binding.server;
        state.epoch = binding.client_boot; state.peer_epoch = binding.server_boot; state.grant = binding.grant;
        state.now = UINT64_MAX - 1000000000; state.rx_seen = true; state.last_rx = 1;
        state.rssi = -127; state.snr_quarters = -128;
        auto key = [&](char value) { model.key({value, 0, true}, state.now); };
        if (mode == 8) {
            state.bound = state.rx_seen = false; state.node = state.peer = 0;
            state.epoch = state.peer_epoch = state.grant = 0;
            key('\t'); key('\t'); return;
        }
        complete(Service::Sensor, Outcome::Ok, 1, 1, mode % 2 != 0);
        complete(Service::LedRead, Outcome::Ok, 2, 200001, false);
        complete(Service::Health, Outcome::Ok, 3, 400001, false);
        for (unsigned i = 0; i < 16; ++i)
            complete(i == 15 ? Service::Health : Service::Sensor,
                     mode == 4 && i == 15 ? Outcome::Ok : Outcome::RemoteError,
                     UINT32_MAX - 16 + i, state.now - 2000000 + i * 1000, mode % 2 != 0);
        if (mode >= 1 && mode <= 4) {
            key('\t');
            if (mode >= 2) { key('\n'); for (unsigned i = 2; i < mode; ++i) key('\n'); }
        } else if (mode == 5 || mode == 10) {
            key('\t'); key('\t'); key('\n'); if (mode == 10) key('\n');
        }
        else if (mode == 6) { state.fault = state.busy = state.transmitting_call = true; }
        else if (mode == 7) state.key_ok = false;
        else if (mode == 9) {
            complete(Service::Led, Outcome::OutcomeUnknown, UINT32_MAX, state.now - 1000000, false);
            key('l');
        }
    }
};
} // namespace srpc::ui::test
