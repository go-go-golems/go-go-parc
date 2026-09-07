#pragma once
#include "sl/mailbox.hpp"
#include <atomic>
#include <optional>

namespace sl {
namespace testing { struct Access; }
class Session;
class NewClient; class OpeningClient; class ReadyClient; class PendingCall; class ClosingClient;
struct ConfigureResult; struct OpenResult; struct SubmitResult; struct ReplyResult; struct CloseResult;
enum class Status {
    Accepted, Full, Waiting, Ready, Done, Failed, Rejected, Closed,
    InvalidEndpoint, InvalidOwner, Oversize, ProtocolError, OutcomeUnknown, IdExhausted, TransportClosed
};
namespace detail {
class Lease {
protected:
    Session* session_ = nullptr;
    uint16_t maximum_ = 128;
    uint64_t request_ = 1;
    AllocationIdentity allocation_{};
    size_t length_ = 0;
    explicit Lease(Session* s) noexcept : session_(s) {}
    void invalidate() noexcept { session_ = nullptr; }
    bool live() const noexcept;
    Status fault(Status status) noexcept;
public:
    Lease() noexcept = default;
    Lease(const Lease&) = delete;
    Lease& operator=(const Lease&) = delete;
    Lease(Lease&& other) noexcept : session_(other.session_), maximum_(other.maximum_), request_(other.request_),
        allocation_(other.allocation_), length_(other.length_) {
        other.session_ = nullptr;
    }
    Lease& operator=(Lease&& other) noexcept;
    ~Lease() noexcept;
};
}
class NewClient : public detail::Lease {
    friend class Session;
    explicit NewClient(Session* s) noexcept : Lease(s) {}
public:
    ConfigureResult try_configure(uint16_t major, uint16_t maximum) & noexcept;
};
class OpeningClient : public detail::Lease {
    friend class NewClient;
    explicit OpeningClient(detail::Lease&& l) noexcept : Lease(std::move(l)) {}
public:
    OpenResult poll(int64_t deadline) & noexcept;
};
class ReadyClient : public detail::Lease {
    friend class OpeningClient; friend class PendingCall;
    explicit ReadyClient(detail::Lease&& l) noexcept : Lease(std::move(l)) {}
public:
    SubmitResult try_submit(OwnedBuffer& input) & noexcept;
    CloseResult try_close() & noexcept;
};
class PendingCall : public detail::Lease {
    friend class ReadyClient;
    explicit PendingCall(detail::Lease&& l) noexcept : Lease(std::move(l)) {}
public:
    ReplyResult poll(int64_t deadline) & noexcept;
};
class ClosingClient : public detail::Lease {
    friend class ReadyClient;
    explicit ClosingClient(detail::Lease&& l) noexcept : Lease(std::move(l)) {}
public:
    Status poll(int64_t deadline) & noexcept;
};
// Finite result records. next exists only for the successful transition status.
// Empty/moved-from wrappers are runtime-invalid, never a second live endpoint.
struct ConfigureResult { Status status; std::optional<OpeningClient> next; };
struct OpenResult { Status status; std::optional<ReadyClient> next; };
struct SubmitResult { Status status; std::optional<PendingCall> next; };
struct ReplyResult { Status status; std::optional<ReadyClient> next; OwnedBuffer payload; uint64_t request = 0; };
struct CloseResult { Status status; std::optional<ClosingClient> next; };

// Supervisor-owned stable storage. A client receives only its endpoint wrapper.
class Session {
    friend class detail::Lease;
    friend class NewClient; friend class OpeningClient; friend class ReadyClient;
    friend class PendingCall; friend class ClosingClient; friend struct testing::Access;
    Mailbox<1> requests_, replies_;
    const uint64_t id_, generation_;
    std::atomic<bool> aborted_{false};
    bool issued_ = false;
    enum class ServerState { New, Ready, Processing, Closing, Closed };
    ServerState state_ = ServerState::New, after_reply_ = ServerState::New;
    detail::Message reply_;
    uint16_t server_maximum_ = 128;
    uint64_t expected_ = 1, dispatches_ = 0;
    const uint64_t fail_every_;
    static uint64_t fresh_id() noexcept {
        static Mutex lock; static uint64_t sequence = 0;
        Lock held(lock);
        require(sequence != UINT64_MAX);
        return ++sequence;
    }
    detail::Message control(detail::Tag tag, uint64_t request = 0) const noexcept {
        detail::Message m; m.tag = tag; m.session = id_; m.generation = generation_; m.request = request;
        return m;
    }
    bool identity(const detail::Message& m) const noexcept {
        return m.session == id_ && m.generation == generation_;
    }
    bool plain_control(const detail::Message& m) const noexcept {
        return !m.payload.valid() && m.request == 0 && m.major == 0 && m.maximum == 0;
    }
    Status flush_reply() noexcept {
        auto r = replies_.try_send(reply_);
        if (r == Put::Full) return Status::Full;
        if (r != Put::Accepted) { abort(); return Status::Closed; }
        state_ = after_reply_;
        if (state_ == ServerState::Closed) replies_.close_sender();
        return Status::Accepted;
    }
public:
    explicit Session(uint64_t generation = 1, uint64_t fail_every = 17) noexcept
        : id_(fresh_id()), generation_(generation), fail_every_(fail_every) { require(generation != 0); }
    Session(const Session&) = delete;
    Session& operator=(const Session&) = delete;
    ~Session() { abort(); } // Worker must be stopped; reply_ releases its owner.
    NewClient make_client() noexcept { require(!issued_); issued_ = true; return NewClient(this); }
    bool aborted() const noexcept { return aborted_.load(); }
    void abort() noexcept {
        aborted_.store(true);
        // Do NOT touch worker-local reply_ here: worker can still be running.
        requests_.close_sender(); requests_.close_receiver();
        replies_.close_sender(); replies_.close_receiver();
    }
    uint64_t dispatches_after_stop() const noexcept { return dispatches_; }
    // Called only by one server task. deadline applies even to a retained reply.
    Status server_step(int64_t deadline) noexcept {
        using detail::Tag;
        if (aborted() || now_us() >= deadline) {
            abort(); reply_ = detail::Message{}; state_ = ServerState::Closed;
            return Status::Closed;
        }
        if (!reply_.empty()) return flush_reply();
        if (state_ == ServerState::Closed) return Status::Closed;
        detail::Message m;
        auto received = requests_.try_receive(m);
        if (received == Get::Empty) return Status::Waiting;
        if (received != Get::Item) { abort(); return Status::Closed; }
        if (!identity(m)) { abort(); return Status::ProtocolError; }
        if (state_ == ServerState::New && m.tag == Tag::Configure && !m.payload.valid() &&
            m.request == 0 && m.error == 0) {
            if (m.major != 1 || m.maximum == 0 || m.maximum > 128) {
                reply_ = control(Tag::Reject); reply_.error = 1; after_reply_ = ServerState::Closed;
            } else {
                server_maximum_ = m.maximum;
                reply_ = control(Tag::Ready); reply_.major = 1; reply_.maximum = m.maximum;
                after_reply_ = ServerState::Ready;
            }
        } else if (state_ == ServerState::Ready && m.tag == Tag::Submit &&
            m.request == expected_ && m.request != UINT64_MAX && m.payload.valid() &&
            m.payload.size() <= server_maximum_ && m.major == 0 && m.maximum == 0 && m.error == 0) {
            state_ = ServerState::Processing; ++dispatches_; ++expected_;
            const bool failed = fail_every_ != 0 && m.request % fail_every_ == 0;
            if (!failed && !transform(m.payload)) { abort(); return Status::ProtocolError; }
            reply_ = control(failed ? Tag::Failed : Tag::Done, m.request);
            reply_.error = failed ? 1 : 0;
            reply_.payload = std::move(m.payload);
            after_reply_ = ServerState::Ready;
        } else if (state_ == ServerState::Ready && m.tag == Tag::Close && plain_control(m) && m.error == 0) {
            state_ = ServerState::Closing;
            reply_ = control(Tag::Closed); after_reply_ = ServerState::Closed;
        } else { abort(); return Status::ProtocolError; }
        return flush_reply();
    }
};
inline bool detail::Lease::live() const noexcept { return session_ && !session_->aborted(); }
inline Status detail::Lease::fault(Status status) noexcept {
    if (session_) session_->abort();
    invalidate();
    return status;
}
inline detail::Lease::~Lease() noexcept { if (session_) session_->abort(); }
inline detail::Lease& detail::Lease::operator=(Lease&& other) noexcept {
    if (this != &other) {
        if (session_) session_->abort();
        session_ = other.session_; maximum_ = other.maximum_; request_ = other.request_;
        allocation_ = other.allocation_; length_ = other.length_;
        other.session_ = nullptr;
    }
    return *this;
}
inline ConfigureResult NewClient::try_configure(uint16_t major, uint16_t maximum) & noexcept {
    if (!live()) return {fault(Status::InvalidEndpoint), {}};
    auto m = session_->control(detail::Tag::Configure); m.major = major; m.maximum = maximum;
    auto sent = session_->requests_.try_send(m);
    if (sent == Put::Full) return {Status::Full, {}};
    if (sent != Put::Accepted) return {fault(Status::Closed), {}};
    maximum_ = maximum;
    return {Status::Accepted, OpeningClient(std::move(*this))};
}
inline OpenResult OpeningClient::poll(int64_t deadline) & noexcept {
    using detail::Tag;
    if (!live()) return {fault(Status::InvalidEndpoint), {}};
    if (now_us() >= deadline) return {fault(Status::OutcomeUnknown), {}};
    detail::Message m; const auto r = session_->replies_.try_receive(m);
    if (r == Get::Empty) return {Status::Waiting, {}};
    if (r != Get::Item) return {fault(Status::Closed), {}};
    if (!session_->identity(m) || m.payload.valid() || m.request != 0) return {fault(Status::ProtocolError), {}};
    if (m.tag == Tag::Reject && m.error == 1 && m.major == 0 && m.maximum == 0) {
        session_->requests_.close_sender(); invalidate(); return {Status::Rejected, {}};
    }
    if (m.tag != Tag::Ready || m.major != 1 || m.maximum == 0 || m.maximum > maximum_ ||
        m.maximum > 128 || m.error != 0) return {fault(Status::ProtocolError), {}};
    maximum_ = m.maximum;
    return {Status::Ready, ReadyClient(std::move(*this))};
}
inline SubmitResult ReadyClient::try_submit(OwnedBuffer& input) & noexcept {
    if (!live()) return {fault(Status::InvalidEndpoint), {}};
    if (!input.valid()) return {Status::InvalidOwner, {}};
    if (input.size() > maximum_) return {Status::Oversize, {}};
    if (request_ == UINT64_MAX) return {fault(Status::IdExhausted), {}};
    const auto allocation = input.identity(); const auto length = input.size();
    auto m = session_->control(detail::Tag::Submit, request_); m.payload = std::move(input);
    auto sent = session_->requests_.try_send(m);
    if (sent != Put::Accepted) {
        input = std::move(m.payload);
        if (sent == Put::Full) return {Status::Full, {}};
        return {fault(Status::Closed), {}};
    }
    allocation_ = allocation; length_ = length;
    return {Status::Accepted, PendingCall(std::move(*this))};
}
inline ReplyResult PendingCall::poll(int64_t deadline) & noexcept {
    using detail::Tag;
    if (!session_) return {Status::InvalidEndpoint, {}, {}, 0};
    if (!live() || now_us() >= deadline) return {fault(Status::OutcomeUnknown), {}, {}, request_};
    detail::Message m; const auto r = session_->replies_.try_receive(m);
    if (r == Get::Empty) return {Status::Waiting, {}, {}, request_};
    if (r != Get::Item) return {fault(Status::OutcomeUnknown), {}, {}, request_};
    const bool done = m.tag == Tag::Done && m.error == 0;
    const bool failed = m.tag == Tag::Failed && m.error == 1;
    if (!session_->identity(m) || (!done && !failed) || m.request != request_ ||
        !m.payload.valid() || m.payload.size() != length_ || m.payload.identity() != allocation_ ||
        m.payload.size() > maximum_ || m.major != 0 || m.maximum != 0)
        return {fault(Status::ProtocolError), {}, {}, request_};
    const auto request = request_++;
    return {done ? Status::Done : Status::Failed, ReadyClient(std::move(*this)), std::move(m.payload), request};
}
inline CloseResult ReadyClient::try_close() & noexcept {
    if (!live()) return {fault(Status::InvalidEndpoint), {}};
    auto m = session_->control(detail::Tag::Close);
    auto sent = session_->requests_.try_send(m);
    if (sent == Put::Full) return {Status::Full, {}};
    if (sent != Put::Accepted) return {fault(Status::Closed), {}};
    session_->requests_.close_sender();
    return {Status::Accepted, ClosingClient(std::move(*this))};
}
inline Status ClosingClient::poll(int64_t deadline) & noexcept {
    if (!live()) return fault(Status::InvalidEndpoint);
    if (now_us() >= deadline) return fault(Status::OutcomeUnknown);
    detail::Message m; const auto r = session_->replies_.try_receive(m);
    if (r == Get::Empty) return Status::Waiting;
    if (r != Get::Item) return fault(Status::TransportClosed);
    if (!session_->identity(m) || m.tag != detail::Tag::Closed || !session_->plain_control(m) || m.error != 0)
        return fault(Status::ProtocolError);
    invalidate(); return Status::Closed;
}
} // namespace sl
