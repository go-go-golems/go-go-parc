#pragma once
#include "srpc/client.hpp"
#include "srpc/keyboard.hpp"
#include <array>
#include <cstdio>

namespace srpc::ui {
enum class Page { Dashboard, History, Setup };
enum class ActionKind { Call, Stop, Arm, DropReplies, SuppressDone, ClearHooks, Sequence };
struct Action {
    ActionKind kind = ActionKind::Call;
    Service service = Service::Sensor;
    uint8_t level = 0;
    unsigned deadline_ms = 8000;
};
struct CallRecord {
    uint64_t sequence = 0;
    Binding binding{};
    uint32_t request = 0;
    Service service = Service::Sensor;
    uint8_t level = 0;
    Time started = 0, deadline = 0, ended = 0;
    unsigned attempts = 0;
    Outcome outcome = Outcome::Waiting;
    Frame reply{};
};
struct Observation {
    bool known = false;
    Time at = 0;
    int32_t value = 0;
    uint32_t sequence = 0, generation = 0;
};
struct RuntimeStatus {
    char board = '?';
    uint16_t node = 0, peer = 0;
    uint64_t epoch = 0, peer_epoch = 0;
    uint32_t grant = 0;
    bool bound = false, armed = false, busy = false, fault = false, key_ok = false;
    bool transmitting_call = false;
    unsigned sf = 7, remaining = 0, drop_replies = 0, sequence_remaining = 0, sequence_completed = 0;
    unsigned sequence_skipped = 0;
    uint32_t transmitting_request = 0;
    bool suppress_done = false;
    Time arm_until = 0, now = 0, last_rx = 0;
    bool rx_seen = false;
    int rssi = 0, snr_quarters = 0;
    uint64_t commits = 0, cache = 0;
    unsigned pool_live = 0;
};
inline std::array<char, 16> snr_text(int quarters) {
    const auto magnitude = unsigned(quarters < 0 ? -int64_t(quarters) : int64_t(quarters));
    std::array<char, 16> text{};
    std::snprintf(text.data(), text.size(), "%s%u.%02u", quarters < 0 ? "-" : "", magnitude / 4, (magnitude % 4) * 25);
    return text;
}
inline const char* phase_name(const CallRecord& call, const RuntimeStatus& state) {
    if (!state.armed) return "RESOLVING";
    if (state.transmitting_call && state.transmitting_request == call.request) return "TRANSMITTING";
    return call.attempts ? "WAIT REPLY" : "QUEUED";
}
inline const char* service_name(Service service) {
    switch (service) {
    case Service::Sensor: return "SAMPLE";
    case Service::Led: return "LED SET";
    case Service::Health: return "HEALTH";
    case Service::LedRead: return "LED READ";
    }
    return "INVALID";
}
inline const char* outcome_name(Outcome outcome) {
    switch (outcome) {
    case Outcome::Waiting: return "WAITING";
    case Outcome::Ok: return "OK";
    case Outcome::RemoteError: return "REMOTE ERROR";
    case Outcome::NotSent: return "NOT SENT";
    case Outcome::OutcomeUnknown: return "UNKNOWN";
    case Outcome::Invalid: return "INVALID";
    }
    return "INVALID";
}
class Console {
    std::array<Action, 4> actions_{};
    size_t action_head_ = 0, action_size_ = 0;
    bool stop_ = false;
    std::array<CallRecord, 16> history_{};
    size_t history_next_ = 0, history_size_ = 0;
    uint64_t sequence_ = 0, selected_ = 0;
    CallRecord active_{};
    bool active_valid_ = false;
    Page page_ = Page::Dashboard;
    unsigned service_selection_ = 0;
    bool detail_ = false;
    unsigned detail_page_ = 0;
    RuntimeStatus runtime_{};
    unsigned selected_sf_ = 7, deadline_ms_ = 8000;
    bool lab_ = false;
    enum class Confirmation { None, Arm, Lab } confirmation_ = Confirmation::None;
    Time confirm_until_ = 0;
    Observation sensor_{}, led_{}, health_{};
    bool led_uncertain_ = false;
    char notice_[48] = "USB bind both peers, then arm";
    Time notice_until_ = 0;
    void enqueue(Action action, Time now) {
        if (action_size_ == actions_.size()) { notice("Input queue full; not accepted", now); return; }
        if (action.kind == ActionKind::Call || action.kind == ActionKind::Sequence) action.deadline_ms = deadline_ms_;
        actions_[(action_head_ + action_size_) % actions_.size()] = action; ++action_size_;
    }
public:
    void update_runtime(RuntimeStatus state) {
        runtime_ = state;
        if (confirmation_ != Confirmation::None && state.now >= confirm_until_) {
            confirmation_ = Confirmation::None; notice("Confirmation expired", state.now);
        }
    }
    bool lab() const { return lab_; }
    unsigned selected_sf() const { return selected_sf_; }
    unsigned deadline_ms() const { return deadline_ms_; }
    bool confirming_arm() const { return confirmation_ == Confirmation::Arm; }
    bool confirming_lab() const { return confirmation_ == Confirmation::Lab; }
    Page page() const { return page_; }
    bool detail() const { return detail_; }
    unsigned detail_page() const { return detail_page_; }
    unsigned selection() const { return service_selection_; }
    const Observation& sensor() const { return sensor_; }
    const Observation& led() const { return led_; }
    const Observation& health() const { return health_; }
    bool led_uncertain() const { return led_uncertain_; }
    const CallRecord* active() const { return active_valid_ ? &active_ : nullptr; }
    size_t history_size() const { return history_size_; }
    const CallRecord* newest(size_t offset = 0) const {
        if (offset >= history_size_) return nullptr;
        return &history_[(history_next_ + history_.size() - 1 - offset) % history_.size()];
    }
    const CallRecord* selected() const {
        for (size_t i = 0; i < history_size_; ++i) if (newest(i)->sequence == selected_) return newest(i);
        return nullptr;
    }
    size_t selected_offset() const {
        for (size_t i = 0; i < history_size_; ++i) if (newest(i)->sequence == selected_) return i;
        return 0;
    }
    void notice(const char* text, Time now) {
        std::snprintf(notice_, sizeof(notice_), "%s", text); notice_until_ = now + 4000000;
    }
    const char* notice(Time now) const { return now <= notice_until_ ? notice_ : ""; }
    void key(KeyEvent event, Time now) {
        if (!event.pressed || !event.key) return;
        const char key = event.key;
        if (key == 'x') {
            action_head_ = action_size_ = 0; stop_ = true; detail_ = false; confirmation_ = Confirmation::None;
            notice("Stopping radio; call may still wait", now); return;
        }
        if (key == '\t') {
            confirmation_ = Confirmation::None;
            page_ = Page((unsigned(page_) + 1) % 3); detail_ = false;
            if (page_ == Page::History && newest()) selected_ = newest()->sequence;
            return;
        }
        if (key == '`' || key == '\b') { detail_ = false; confirmation_ = Confirmation::None; return; }
        if (confirmation_ != Confirmation::None) {
            if (now >= confirm_until_) { confirmation_ = Confirmation::None; notice("Confirmation expired", now); return; }
            if (key == '\n') {
                if (confirmation_ == Confirmation::Lab) { lab_ = true; notice("LAB controls act on THIS board", now); }
                else if (runtime_.bound && !runtime_.armed && !runtime_.busy && !runtime_.fault && !active_valid_)
                    enqueue({ActionKind::Arm, Service::Sensor, uint8_t(selected_sf_)}, now);
                else notice("Cannot arm: binding or busy/fault", now);
                confirmation_ = Confirmation::None;
            }
            return;
        }
        if (page_ == Page::Setup) {
            if (key == 'g') {
                if (lab_) {
                    lab_ = false; deadline_ms_ = 8000; cancel_actions();
                    enqueue({ActionKind::ClearHooks}, now); notice("Lab exited; hooks/sequence cleared", now);
                } else { confirmation_ = Confirmation::Lab; confirm_until_ = now + 10000000; }
            } else if (lab_) {
                if (key == 'd') enqueue({ActionKind::DropReplies}, now);
                else if (key == 'z') enqueue({ActionKind::SuppressDone}, now);
                else if (key == 'c') { cancel_actions(); enqueue({ActionKind::ClearHooks}, now); }
                else if (key == 't') deadline_ms_ = deadline_ms_ == 8000 ? 100 : deadline_ms_ == 100 ? 1000 : 8000;
                else if (key == 's') enqueue({ActionKind::Call, Service::Sensor, 0}, now);
                else if (key == '5') enqueue({ActionKind::Sequence}, now);
            } else if (key == '7' || key == '9') {
                if (runtime_.armed || runtime_.busy || active_valid_) notice("Stop and finish call before SF", now);
                else selected_sf_ = unsigned(key - '0');
            } else if (key == 'a') {
                if (!runtime_.bound || runtime_.armed || runtime_.busy || runtime_.fault || active_valid_)
                    notice("Cannot arm: binding or busy/fault", now);
                else { confirmation_ = Confirmation::Arm; confirm_until_ = now + 10000000; }
            } else if (key == '\n') {
                if (!detail_) { detail_ = true; detail_page_ = 0; }
                else detail_page_ = (detail_page_ + 1) % 2;
            }
            return;
        }
        if (key == ';' || key == '.') {
            if (page_ == Page::Dashboard && !detail_)
                service_selection_ = (service_selection_ + (key == '.' ? 1 : 2)) % 3;
            else if (page_ == Page::History && history_size_) {
                auto offset = selected_offset();
                if (key == '.' && offset + 1 < history_size_) ++offset;
                if (key == ';' && offset) --offset;
                selected_ = newest(offset)->sequence;
            }
            return;
        }
        if (key == '\n') {
            if (page_ == Page::Dashboard) detail_ = !detail_;
            else if (page_ == Page::History && selected()) {
                if (!detail_) { detail_ = true; detail_page_ = 0; }
                else detail_page_ = (detail_page_ + 1) % 3;
            }
            return;
        }
        if (page_ != Page::Dashboard) return;
        if (key == 's') enqueue({ActionKind::Call, Service::Sensor, 0}, now);
        else if (key == 'h') enqueue({ActionKind::Call, Service::Health, 0}, now);
        else if (key == 'l') { service_selection_ = 1; detail_ = true; }
        else if (detail_ && service_selection_ == 1) {
            if (key == '0' || key == '1') enqueue({ActionKind::Call, Service::Led, uint8_t(key - '0')}, now);
            else if (key == 'r') enqueue({ActionKind::Call, Service::LedRead, 0}, now);
        }
    }
    void cancel_actions() noexcept {
        action_head_ = action_size_ = 0; stop_ = false; confirmation_ = Confirmation::None;
    }
    bool next_action(Action& action) {
        if (stop_) { stop_ = false; action = {ActionKind::Stop, Service::Sensor, 0}; return true; }
        if (!action_size_) return false;
        action = actions_[action_head_]; action_head_ = (action_head_ + 1) % actions_.size(); --action_size_;
        return true;
    }
    void started(Binding binding, uint32_t request, Service service, uint8_t level, Time now, Time deadline) {
        sl::require(!active_valid_ && sequence_ != UINT64_MAX);
        active_ = {}; active_.sequence = ++sequence_; active_.binding = binding;
        active_.request = request; active_.service = service; active_.level = level;
        active_.started = now; active_.deadline = deadline; active_valid_ = true;
        notice("Call admitted", now);
    }
    void attempts(unsigned count) { if (active_valid_) active_.attempts = count; }
    void completed(const Result& result, Time now) {
        sl::require(active_valid_ && result.request == active_.request && result.outcome != Outcome::Waiting);
        active_.ended = now; active_.outcome = result.outcome; active_.attempts = result.attempts; active_.reply = result.reply;
        if (result.outcome == Outcome::Ok) {
            const auto& frame = result.reply;
            if (active_.service == Service::Sensor) {
                sensor_ = {true, now, signed32(uint32_t(get(frame.body.data(), 4, 4))), uint32_t(get(frame.body.data(), 0, 4)), 0};
            } else if (active_.service == Service::Led || active_.service == Service::LedRead) {
                led_ = {true, now, frame.body[0], 0, 0}; led_uncertain_ = false;
            } else if (active_.service == Service::Health) {
                health_ = {true, now, 0, uint32_t(get(frame.body.data(), 0, 4)), uint32_t(get(frame.body.data(), 4, 4))};
            }
        } else if (active_.service == Service::Led && result.outcome == Outcome::OutcomeUnknown) led_uncertain_ = true;
        history_[history_next_] = active_; history_next_ = (history_next_ + 1) % history_.size();
        if (history_size_ < history_.size()) ++history_size_;
        if (!selected_) selected_ = active_.sequence;
        if (!selected()) { selected_ = active_.sequence; notice("Older selected record evicted", now); }
        else notice(outcome_name(result.outcome), now);
        active_valid_ = false;
    }
};
} // namespace srpc::ui
