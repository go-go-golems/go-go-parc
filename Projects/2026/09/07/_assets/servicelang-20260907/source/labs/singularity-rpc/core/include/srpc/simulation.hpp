#pragma once
#include "srpc/client.hpp"
#include "srpc/server.hpp"
#include "srpc/radio.hpp"
namespace srpc {
struct Config {
    unsigned sf = 7, request_loss = 0, reply_loss = 0;
    uint32_t seed = 1, duty_ppm = 1000000;
    Time permit_expires = UINT64_MAX;
    bool permit = true, drop_first_request = false, drop_first_reply = false;
    bool suppress_first_completion = false, reset_after_commit = false, duplicate_first_request = false;
    bool trace = false, replay_previous_reply = false;
    uint8_t request_drop_mask = 0, reply_drop_mask = 0, completion_fault_mask = 0;
};
struct Counters {
    uint64_t request_starts = 0, reply_starts = 0, request_drops = 0, reply_drops = 0;
    uint64_t recoveries = 0, commits = 0, cache_hits = 0, reset_suppressed = 0, response_overflow = 0, overlap_drops = 0;
};
enum class Event { Admit, RequestStart, RequestDone, RequestDrop, Commit, Cache, ReplyStart, ReplyDrop, Complete, Recover, Reset };
inline const char* event_name(Event event) noexcept {
    switch (event) {
        case Event::Admit: return "admitted"; case Event::RequestStart: return "request_start";
        case Event::RequestDone: return "request_done"; case Event::RequestDrop: return "request_drop";
        case Event::Commit: return "server_commit"; case Event::Cache: return "cache_hit";
        case Event::ReplyStart: return "reply_start"; case Event::ReplyDrop: return "reply_drop";
        case Event::Complete: return "client_complete"; case Event::Recover: return "driver_recovered";
        case Event::Reset: return "server_reset";
    }
    return "invalid";
}
struct Trace { Time time = 0; Event event = Event::Admit; uint32_t request = 0; unsigned attempt = 0; };
// One execution context owns both simulated radios. There is no physical driver.
class Simulation {
    Config config_;
    uint32_t random_;
    Binding binding_{};
    sl::Pool request_pool_, reply_pool_;
    TxSlot request_tx_, reply_tx_;
    SimulationPacing request_pacing_, reply_pacing_;
    Server server_{2, 1, 1, true};
    Client client_{binding_};
    Packet queued_reply_{};
    bool reply_queued_ = false, reset_done_ = false, duplicate_done_ = false;
    bool request_collided_ = false, reply_collided_ = false;
    uint64_t request_completions_ = 0, reply_completions_ = 0;
    unsigned call_reply_completions_ = 0;
    Packet previous_reply_{};
    bool have_previous_reply_ = false;
    static bool masked(uint8_t mask, unsigned ordinal) noexcept {
        return ordinal >= 1 && ordinal <= 3 && (mask & (1u << (ordinal - 1))) != 0;
    }
    Time now_ = 0;
    Counters counters_{};
    std::array<Trace, 128> trace_{};
    size_t trace_size_ = 0, trace_drops_ = 0;
    void record(Event event, uint32_t request) noexcept {
        if (!config_.trace) return;
        if (trace_size_ == trace_.size()) { ++trace_drops_; return; }
        trace_[trace_size_++] = {now_, event, request, client_.attempts()};
    }
    bool lost(unsigned percent) noexcept {
        random_ ^= random_ << 13; random_ ^= random_ >> 17; random_ ^= random_ << 5;
        return random_ % 100 < percent;
    }
    void queue_reply(const Packet& packet) noexcept {
        if (reply_queued_) { if (!same(packet, queued_reply_)) ++counters_.response_overflow; return; }
        queued_reply_ = packet; reply_queued_ = true;
    }
    void deliver_request(const Packet& packet) noexcept {
        const auto admitted = server_.admit(packet);
        if (admitted.action == Admission::Accepted) {
            Packet reply;
            sl::require(server_.execute(admitted.entry, now_, reply));
            ++counters_.commits; record(Event::Commit, uint32_t(get(packet.bytes.data(), 28, 4)));
            if (config_.reset_after_commit && !reset_done_) {
                reset_done_ = true; ++counters_.reset_suppressed;
                record(Event::Reset, client_.request_id());
                server_.reset(2); auto next = binding_; next.server_boot = 2; sl::require(server_.bind(next));
                return; // Old client is not silently rebound; old reply was never sent.
            }
            queue_reply(reply);
        } else if (admitted.action == Admission::Cached) {
            ++counters_.cache_hits; record(Event::Cache, client_.request_id()); queue_reply(admitted.reply);
        } else if (admitted.action == Admission::ErrorReply) queue_reply(admitted.reply);
    }
public:
    explicit Simulation(Config config = {}) noexcept
        : config_(config), random_(config.seed ? config.seed : 1),
          request_pacing_(config.duty_ppm, config.permit_expires, config.permit),
          reply_pacing_(config.duty_ppm, config.permit_expires, config.permit) {
        sl::require(config.sf == 7 || config.sf == 9);
        sl::require(config.request_loss <= 100 && config.reply_loss <= 100);
        sl::require(server_.bind(binding_));
    }
    std::optional<ReadyClient> ready() noexcept { return client_.ready(); }
    Time now() const noexcept { return now_; }
    const Counters& counters() const noexcept { return counters_; }
    const Trace& trace(size_t index) const noexcept { sl::require(index < trace_size_); return trace_[index]; }
    size_t trace_size() const noexcept { return trace_size_; }
    size_t trace_drops() const noexcept { return trace_drops_; }
    bool quiescent() const noexcept { return !request_tx_.busy() && !reply_tx_.busy() && !reply_queued_; }
    void audit() const noexcept {
        const auto a = request_pool_.stats(), b = reply_pool_.stats();
        sl::require(quiescent() && a.allocations == a.releases && b.allocations == b.releases);
        sl::require(a.live_general == 0 && b.live_general == 0 && a.live_control == 0 && b.live_control == 0);
    }
    void step() noexcept {
        auto request_event = request_tx_.advance(now_);
        if (request_event.event == TxEvent::Recovered) {
            ++counters_.recoveries; record(Event::Recover, request_event.request);
            client_.driver_fault(request_event.request);
        } else if (request_event.event == TxEvent::Done) {
            ++request_completions_; record(Event::RequestDone, request_event.request);
            client_.tx_done(request_event.request, now_);
            const bool random_drop = lost(config_.request_loss);
            if (request_collided_) ++counters_.overlap_drops;
            if (request_collided_ || random_drop || masked(config_.request_drop_mask, client_.attempts()) ||
                (config_.drop_first_request && request_completions_ == 1)) {
                ++counters_.request_drops; record(Event::RequestDrop, request_event.request);
            } else {
                deliver_request(request_event.packet);
                if (config_.duplicate_first_request && !duplicate_done_) {
                    duplicate_done_ = true; deliver_request(request_event.packet);
                }
            }
        }
        auto reply_event = reply_tx_.advance(now_);
        if (reply_event.event == TxEvent::Done) {
            ++reply_completions_; ++call_reply_completions_;
            previous_reply_ = reply_event.packet; have_previous_reply_ = true;
            const bool random_drop = lost(config_.reply_loss);
            if (reply_collided_) ++counters_.overlap_drops;
            if (reply_collided_ || random_drop || masked(config_.reply_drop_mask, call_reply_completions_) ||
                (config_.drop_first_reply && reply_completions_ == 1)) {
                ++counters_.reply_drops; record(Event::ReplyDrop, reply_event.request);
            } else client_.receive(reply_event.packet, now_);
        }
        client_.advance(now_);
        if (!request_tx_.busy() && client_.request_due(now_) && request_pacing_.eligible(now_)) {
            Time duration; sl::require(airtime_us(client_.request_packet().size, config_.sf, duration));
            sl::OwnedBuffer owner;
            sl::require(allocate_packet(request_pool_, client_.request_packet(), owner));
            const auto started = request_tx_.start(owner, client_.request_id(), now_, duration, request_pacing_,
                (config_.suppress_first_completion && counters_.request_starts == 0) ||
                masked(config_.completion_fault_mask, client_.attempts() + 1));
            if (started == TxStart::Accepted) {
                request_collided_ = reply_tx_.busy();
                if (request_collided_) reply_collided_ = true;
                sl::require(client_.tx_started(client_.request_id(), now_));
                ++counters_.request_starts; record(Event::RequestStart, client_.request_id());
                if (config_.replay_previous_reply && have_previous_reply_ &&
                    uint32_t(get(previous_reply_.bytes.data(), 28, 4)) != client_.request_id())
                    sl::require(!client_.receive(previous_reply_, now_));
            }
        }
        if (reply_queued_ && now_ >= config_.permit_expires) { reply_queued_ = false; ++counters_.response_overflow; }
        if (reply_queued_ && !reply_tx_.busy() && reply_pacing_.eligible(now_)) {
            Time duration; sl::require(airtime_us(queued_reply_.size, config_.sf, duration));
            sl::OwnedBuffer owner; sl::require(allocate_packet(reply_pool_, queued_reply_, owner));
            const auto request = uint32_t(get(queued_reply_.bytes.data(), 28, 4));
            if (reply_tx_.start(owner, request, now_, duration, reply_pacing_) == TxStart::Accepted) {
                reply_collided_ = request_tx_.busy();
                if (reply_collided_) request_collided_ = true;
                reply_queued_ = false; ++counters_.reply_starts; record(Event::ReplyStart, request);
            }
        }
        // Jump only to actual future events; no busy-loop advances or RF time claims.
        Time next = UINT64_MAX;
        const auto consider = [&](Time time) { if (time > now_ && time < next) next = time; };
        if (request_tx_.busy()) consider(request_tx_.next_event());
        if (reply_tx_.busy()) consider(reply_tx_.next_event());
        if (client_.active()) { consider(client_.wake_time()); consider(client_.deadline()); }
        if (client_.request_due(now_)) consider(request_pacing_.next_eligible());
        if (reply_queued_) { consider(reply_pacing_.next_eligible()); consider(config_.permit_expires); }
        if (next == UINT64_MAX) sl::require(add_time(now_, 1, next));
        now_ = next;
    }
    Result call(ReadyClient& ready_endpoint, Service service = Service::Led, uint8_t level = 1,
                Time timeout = 30000000, Time reply_wait = 2000000) noexcept {
        Time deadline;
        if (!add_time(now_, timeout, deadline)) return {Outcome::Invalid, {}, 0, 0};
        auto start = ready_endpoint.start(service, level, now_, deadline, reply_wait);
        if (start.code != StartCode::Accepted) return {Outcome::Invalid, {}, 0, 0};
        call_reply_completions_ = 0;
        record(Event::Admit, client_.request_id());
        for (unsigned steps = 0; steps < 10000; ++steps) {
            step(); auto polled = start.pending->poll(now_);
            if (polled.result.outcome == Outcome::Waiting) continue;
            record(Event::Complete, polled.result.request);
            if (polled.ready) ready_endpoint = std::move(*polled.ready);
            for (unsigned cleanup = 0; !quiescent() && cleanup < 10000; ++cleanup) step();
            audit(); return polled.result;
        }
        sl::require(false); return {Outcome::Invalid, {}, 0, 0};
    }
};
} // namespace srpc
