#pragma once
#include "srpc/identity.hpp"
#include "srpc/airtime.hpp"
#include "sl/platform.hpp"
#include <optional>
namespace srpc {
class Client; class ReadyClient; class PendingCall;
struct Started; struct Polled;
enum class StartCode { Accepted, Invalid, Busy, IdExhausted };
enum class Outcome { Waiting, Ok, RemoteError, NotSent, OutcomeUnknown, Invalid };
struct Result { Outcome outcome = Outcome::Waiting; Frame reply{}; uint32_t request = 0; unsigned attempts = 0; };
class ReadyClient {
    friend class Client; friend class PendingCall;
    Client* client_ = nullptr; uint64_t lease_ = 0;
    ReadyClient(Client* client, uint64_t lease) noexcept : client_(client), lease_(lease) {}
public:
    ReadyClient(const ReadyClient&) = delete;
    ReadyClient& operator=(const ReadyClient&) = delete;
    ReadyClient(ReadyClient&& other) noexcept;
    ReadyClient& operator=(ReadyClient&& other) noexcept;
    ~ReadyClient() noexcept;
    Started start(Service service, uint8_t level, Time now, Time deadline, Time reply_wait = 2000000) & noexcept;
};
class PendingCall {
    friend class ReadyClient;
    Client* client_ = nullptr; uint64_t lease_ = 0;
    PendingCall(Client* client, uint64_t lease) noexcept : client_(client), lease_(lease) {}
public:
    PendingCall(const PendingCall&) = delete;
    PendingCall& operator=(const PendingCall&) = delete;
    PendingCall(PendingCall&& other) noexcept;
    PendingCall& operator=(PendingCall&& other) noexcept;
    ~PendingCall() noexcept;
    Polled poll(Time now) & noexcept;
};
struct Started { StartCode code; std::optional<PendingCall> pending; };
struct Polled { Result result; std::optional<ReadyClient> ready; };
// Owned by the event/driver task. Applications receive a typed endpoint only.
// Binding is immutable; reconstruct only after trusted peer identity changes.
class Client {
    friend class ReadyClient; friend class PendingCall;
    Binding binding_;
    enum class State { Ready, Active, Complete } state_ = State::Ready;
    bool bound_ = true, issued_ = false, transmitting_ = false, waiting_reply_ = false;
    uint64_t lease_ = 1;
    uint32_t next_id_ = 1;
    Packet request_{};
    Frame frame_{};
    Result result_{};
    Time total_deadline_ = 0, reply_deadline_ = 0, wait_ = 0;
    uint64_t invalid_replies_ = 0;
    void next_lease() noexcept { sl::require(lease_ != UINT64_MAX); ++lease_; }
    bool owns(uint64_t lease) const noexcept { return issued_ && lease == lease_; }
    void finish(Outcome outcome) noexcept {
        result_.outcome = outcome; state_ = State::Complete;
    }
    void abandon(uint64_t lease) noexcept {
        if (!owns(lease)) return;
        invalidate();
    }
public:
    explicit Client(Binding binding) noexcept : binding_(binding), bound_(binding.valid()) {}
    Client(const Client&) = delete; Client& operator=(const Client&) = delete;
    std::optional<ReadyClient> ready() noexcept {
        if (!bound_ || issued_ || state_ != State::Ready) return {};
        issued_ = true; return ReadyClient(this, lease_);
    }
    void invalidate() noexcept {
        if (state_ == State::Active) finish(result_.attempts ? Outcome::OutcomeUnknown : Outcome::NotSent);
        bound_ = false; issued_ = false; next_lease();
    }
    bool active() const noexcept { return state_ == State::Active; }
    bool request_due(Time now) const noexcept {
        return bound_ && active() && now < total_deadline_ && result_.attempts < 3 &&
            !transmitting_ && (!waiting_reply_ || now >= reply_deadline_);
    }
    const Packet& request_packet() const noexcept { return request_; }
    uint32_t request_id() const noexcept { return frame_.request; }
    unsigned attempts() const noexcept { return result_.attempts; }
    Time deadline() const noexcept { return total_deadline_; }
    Time wake_time() const noexcept { return waiting_reply_ && reply_deadline_ < total_deadline_ ? reply_deadline_ : total_deadline_; }
    uint64_t invalid_replies() const noexcept { return invalid_replies_; }
    bool tx_started(uint32_t request, Time now) noexcept {
        if (request != frame_.request || !request_due(now)) return false;
        ++result_.attempts; transmitting_ = true; waiting_reply_ = false; return true;
    }
    bool tx_done(uint32_t request, Time now) noexcept {
        if (!active() || !transmitting_ || request != frame_.request) return false;
        transmitting_ = false; waiting_reply_ = true;
        if (!add_time(now, wait_, reply_deadline_)) reply_deadline_ = total_deadline_;
        if (reply_deadline_ > total_deadline_) reply_deadline_ = total_deadline_;
        return true;
    }
    void driver_fault(uint32_t request) noexcept {
        if (!active() || request != frame_.request || !transmitting_) return;
        transmitting_ = false; waiting_reply_ = false;
    }
    void advance(Time now) noexcept {
        if (!active()) return;
        if (now >= total_deadline_) finish(result_.attempts ? Outcome::OutcomeUnknown : Outcome::NotSent);
        else if (!transmitting_ && result_.attempts >= 3 && (!waiting_reply_ || now >= reply_deadline_))
            finish(Outcome::OutcomeUnknown);
    }
    bool receive(const Packet& packet, Time now) noexcept {
        advance(now);
        Frame f;
        if (!active() || result_.attempts == 0 || decode(packet, f) != Codec::Ok || f.kind != Kind::Reply || f.flags ||
            !binding_.accepts_reply(f) || f.request != frame_.request || f.service != frame_.service || f.opcode != frame_.opcode) {
            ++invalid_replies_; return false;
        }
        if (f.status == ReplyCode::Busy) {
            waiting_reply_ = true;
            if (!add_time(now, wait_, reply_deadline_)) reply_deadline_ = total_deadline_;
            if (reply_deadline_ > total_deadline_) reply_deadline_ = total_deadline_;
            return true;
        }
        result_.reply = f;
        finish(f.status == ReplyCode::Ok ? Outcome::Ok : Outcome::RemoteError); return true;
    }
};
inline ReadyClient::ReadyClient(ReadyClient&& other) noexcept : client_(other.client_), lease_(other.lease_) { other.client_ = nullptr; }
inline ReadyClient& ReadyClient::operator=(ReadyClient&& other) noexcept {
    if (this != &other) { if (client_) client_->abandon(lease_); client_ = other.client_; lease_ = other.lease_; other.client_ = nullptr; }
    return *this;
}
inline ReadyClient::~ReadyClient() noexcept { if (client_) client_->abandon(lease_); }
inline PendingCall::PendingCall(PendingCall&& other) noexcept : client_(other.client_), lease_(other.lease_) { other.client_ = nullptr; }
inline PendingCall& PendingCall::operator=(PendingCall&& other) noexcept {
    if (this != &other) { if (client_) client_->abandon(lease_); client_ = other.client_; lease_ = other.lease_; other.client_ = nullptr; }
    return *this;
}
inline PendingCall::~PendingCall() noexcept { if (client_) client_->abandon(lease_); }
inline Started ReadyClient::start(Service service, uint8_t level, Time now, Time deadline, Time reply_wait) & noexcept {
    if (!client_ || !client_->owns(lease_) || !client_->bound_) return {StartCode::Invalid, {}};
    auto& c = *client_;
    if (c.state_ != Client::State::Ready) return {StartCode::Busy, {}};
    if (c.next_id_ == UINT32_MAX) return {StartCode::IdExhausted, {}};
    if (deadline <= now || !reply_wait) return {StartCode::Invalid, {}};
    Frame f;
    f.source = c.binding_.client; f.destination = c.binding_.server;
    f.source_boot = c.binding_.client_boot; f.destination_boot = c.binding_.server_boot;
    f.request = c.next_id_; f.grant = c.binding_.grant; f.generation = c.binding_.generation;
    f.service = service; f.opcode = uint8_t(service);
    if (service == Service::Led) { f.length = 1; f.body[0] = level; }
    Packet packet; if (encode(f, packet) != Codec::Ok) return {StartCode::Invalid, {}};
    c.frame_ = f; c.request_ = packet; ++c.next_id_;
    c.result_ = {}; c.result_.request = f.request;
    c.total_deadline_ = deadline; c.wait_ = reply_wait;
    c.transmitting_ = c.waiting_reply_ = false; c.state_ = Client::State::Active;
    c.next_lease(); auto* pointer = client_; client_ = nullptr;
    return {StartCode::Accepted, PendingCall(pointer, c.lease_)};
}
inline Polled PendingCall::poll(Time now) & noexcept {
    if (!client_) return {{Outcome::Invalid, {}, 0, 0}, {}};
    auto& c = *client_;
    // Invalidation preserves a final pending outcome but cannot mint a ready lease.
    if (!c.owns(lease_)) { client_ = nullptr; return {c.result_, {}}; }
    c.advance(now);
    if (c.active()) return {c.result_, {}};
    const Result result = c.result_;
    if (c.state_ != Client::State::Complete) return {{Outcome::Invalid, {}, 0, 0}, {}};
    c.state_ = Client::State::Ready; c.next_lease();
    auto* pointer = client_; client_ = nullptr;
    return {result, ReadyClient(pointer, c.lease_)};
}
} // namespace srpc
