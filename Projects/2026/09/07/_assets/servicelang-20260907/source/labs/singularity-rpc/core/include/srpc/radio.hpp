#pragma once
#include "srpc/airtime.hpp"
#include "sl/pool.hpp"
namespace srpc {
enum class TxStart { Accepted, Busy, Ineligible, Invalid };
enum class TxEvent { None, Done, Recovered };
struct Completion { TxEvent event = TxEvent::None; uint32_t request = 0; Packet packet{}; };
// Single owner-task API. Not thread-safe and never called by applications/ISRs.
class TxSlot {
    sl::OwnedBuffer owner_;
    Time done_ = 0, recovery_ = 0;
    uint32_t request_ = 0;
    bool suppress_done_ = false;
public:
    ~TxSlot() { sl::require(!busy()); } // Never silently reclaim a live driver owner.
    bool busy() const noexcept { return owner_.valid(); }
    Time next_event() const noexcept { return suppress_done_ ? recovery_ : done_; }
    TxStart start(sl::OwnedBuffer& input, uint32_t request, Time now, Time duration,
                  SimulationPacing& pacing, bool suppress_done = false) noexcept {
        if (busy()) return TxStart::Busy;
        Time done, recovery;
        if (!input.valid() || !request || input.size() < 44 || input.size() > 128 ||
            !add_time(now, duration, done) || !add_time(done, 100000, recovery)) return TxStart::Invalid;
        if (!pacing.reserve(now, duration)) return TxStart::Ineligible;
        request_ = request; done_ = done; recovery_ = recovery; suppress_done_ = suppress_done;
        owner_ = std::move(input); return TxStart::Accepted;
    }
    Completion advance(Time now) noexcept {
        if (!busy() || now < next_event()) return {};
        Completion out;
        out.request = request_;
        if (suppress_done_) {
            // Fake-driver abort is synchronous and confirms no remaining users.
            // A physical adapter must obtain that confirmation, not assume it.
            out.event = TxEvent::Recovered;
        } else {
            out.event = TxEvent::Done; out.packet.size = owner_.size();
            for (size_t i = 0; i < out.packet.size; ++i) sl::require(owner_.read(i, out.packet.bytes[i]));
        }
        owner_.reset(); return out;
    }
};
inline bool allocate_packet(sl::Pool& pool, const Packet& packet, sl::OwnedBuffer& owner) noexcept {
    if (packet.size > 128 || pool.general().allocate(packet.size, owner) != sl::Alloc::Ok) return false;
    for (size_t i = 0; i < packet.size; ++i) sl::require(owner.write(i, packet.bytes[i]));
    return true;
}
} // namespace srpc
