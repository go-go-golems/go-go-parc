#pragma once
#include "srpc/identity.hpp"
#include "sl/platform.hpp"
namespace srpc {
enum class Admission { Drop, Accepted, Coalesced, Cached, ErrorReply };
struct Admitted { Admission action = Admission::Drop; size_t entry = 0; Packet reply{}; };
class Server {
    enum class State { Idle, InProgress, Completed };
    struct Entry { bool used = false; Binding binding{}; uint32_t high = 0; State state = State::Idle; Packet request{}, reply{}; };
    std::array<Entry, 8> entries_{};
    uint16_t node_;
    uint64_t boot_;
    uint32_t generation_;
    bool lab_enabled_;
    uint64_t commits_ = 0, cache_hits_ = 0, drops_ = 0;
    uint32_t samples_ = 0;
    uint8_t led_ = 0;
    Admitted error(const Frame& request, ReplyCode code) noexcept {
        Admitted out; out.action = Admission::ErrorReply;
        sl::require(encode(reply_for(request, code), out.reply) == Codec::Ok); return out;
    }
public:
    Server(uint16_t node, uint64_t boot, uint32_t generation, bool unauthenticated_lab_mode) noexcept
        : node_(node), boot_(boot), generation_(generation), lab_enabled_(unauthenticated_lab_mode) {}
    bool bind(Binding binding) noexcept {
        if (!binding.valid() || binding.server != node_ || binding.server_boot != boot_ || binding.generation != generation_) return false;
        for (const auto& e : entries_) if (e.used && e.binding.grant == binding.grant) return false;
        for (auto& e : entries_) if (!e.used) { e.used = true; e.binding = binding; return true; }
        return false;
    }
    Admitted admit(const Packet& packet) noexcept {
        Frame f;
        if (!lab_enabled_ || decode(packet, f) != Codec::Ok || f.kind != Kind::Request || f.flags != 0 ||
            f.destination != node_ || f.destination_boot != boot_ || f.generation != generation_) { ++drops_; return {}; }
        for (size_t i = 0; i < entries_.size(); ++i) {
            auto& e = entries_[i];
            if (!e.used || e.binding.grant != f.grant) continue;
            if (!e.binding.accepts_request(f)) { ++drops_; return {}; }
            if (f.request < e.high) return error(f, ReplyCode::Stale);
            if (f.request == e.high && e.state != State::Idle) {
                if (!same(packet, e.request)) return error(f, ReplyCode::Conflict);
                if (e.state == State::InProgress) return {Admission::Coalesced, i, {}};
                ++cache_hits_; return {Admission::Cached, i, e.reply};
            }
            if (e.state == State::InProgress) return error(f, ReplyCode::Busy);
            e.request = packet; e.high = f.request; e.state = State::InProgress;
            return {Admission::Accepted, i, {}};
        }
        ++drops_; return {};
    }
    bool execute(size_t index, Time now, Packet& output) noexcept {
        if (index >= entries_.size()) return false;
        auto& e = entries_[index];
        if (!e.used || e.state != State::InProgress) return false;
        Frame request;
        sl::require(decode(e.request, request) == Codec::Ok);
        auto reply = reply_for(request, ReplyCode::Ok);
        if (request.service == Service::Sensor) {
            if (samples_ == UINT32_MAX) reply.status = ReplyCode::Internal;
            else {
                ++samples_; reply.length = 8;
                put(reply.body.data(), 0, samples_, 4);
                // Explicit bounded synthetic signed value, no calibration claim.
                put(reply.body.data(), 4, uint32_t(int32_t(samples_ % 200) - 100), 4);
            }
        } else if (request.service == Service::Led) {
            led_ = request.body[0]; reply.length = 1; reply.body[0] = led_;
        } else if (request.service == Service::LedRead) {
            reply.length = 1; reply.body[0] = led_; // Observation only; never execute another write.
        } else {
            reply.length = 12; put(reply.body.data(), 0, uint32_t(now / 1000), 4);
            put(reply.body.data(), 4, generation_, 4); // remaining diagnostics zero in fake service
        }
        ++commits_;
        sl::require(encode(reply, e.reply) == Codec::Ok);
        e.state = State::Completed; output = e.reply; return true;
    }
    void reset(uint64_t new_boot) noexcept {
        sl::require(new_boot > boot_); boot_ = new_boot;
        entries_ = {}; samples_ = 0; led_ = 0;
        // commits/cache/drop counters are out-of-band experiment instrumentation.
    }
    uint64_t commits() const noexcept { return commits_; }
    uint64_t cache_hits() const noexcept { return cache_hits_; }
    uint64_t drops() const noexcept { return drops_; }
    uint8_t led() const noexcept { return led_; }
};
} // namespace srpc
