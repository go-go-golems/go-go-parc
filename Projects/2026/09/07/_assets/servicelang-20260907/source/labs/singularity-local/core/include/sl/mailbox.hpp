#pragma once
#include "sl/pool.hpp"
#include <array>
#include <optional>
#include <type_traits>

namespace sl {
namespace detail {
enum class Tag : uint8_t { Empty, Data, Configure, Ready, Reject, Submit, Done, Failed, Close, Closed };
struct Message {
    Tag tag = Tag::Empty;
    uint64_t session = 0, generation = 0, request = 0;
    uint16_t major = 0, maximum = 0, error = 0;
    OwnedBuffer payload;
    Message() noexcept = default;
    Message(const Message&) = delete;
    Message& operator=(const Message&) = delete;
    Message(Message&& other) noexcept { *this = std::move(other); }
    Message& operator=(Message&& other) noexcept {
        if (this == &other) return *this;
        tag = other.tag; session = other.session; generation = other.generation;
        request = other.request; major = other.major; maximum = other.maximum; error = other.error;
        payload = std::move(other.payload);
        other.tag = Tag::Empty;
        return *this;
    }
    bool empty() const noexcept { return tag == Tag::Empty && payload.allocation_id() == 0; }
};
} // namespace detail

enum class Put { Accepted, Full, Closed, InvalidMessage };
enum class Get { Item, Empty, Closed, OutputNotEmpty, Timeout };
template<size_t Capacity> class Mailbox {
    static_assert(Capacity > 0, "Rendezvous channels are not supported");
    mutable Mutex mutex_;
    WakeEvent ready_;
    std::array<std::optional<detail::Message>, Capacity> slots_{};
    size_t head_ = 0, tail_ = 0, count_ = 0, high_water_ = 0;
    bool sender_closed_ = false, receiver_closed_ = false;
public:
    Mailbox() = default;
    Mailbox(const Mailbox&) = delete;
    Mailbox& operator=(const Mailbox&) = delete;
    ~Mailbox() { close_receiver(); } // All users must already be quiescent.
    Put try_send(detail::Message& input) noexcept {
        if (input.tag == detail::Tag::Empty) return Put::InvalidMessage;
        {
            Lock lock(mutex_);
            if (sender_closed_ || receiver_closed_) return Put::Closed;
            if (count_ == Capacity) return Put::Full;
            require(!slots_[tail_].has_value());
            slots_[tail_].emplace(std::move(input)); // Linearization point.
            tail_ = (tail_ + 1) % Capacity;
            ++count_;
            if (count_ > high_water_) high_water_ = count_;
        }
        ready_.signal();
        return Put::Accepted;
    }
    Get try_receive(detail::Message& out) noexcept {
        if (!out.empty()) return Get::OutputNotEmpty;
        Lock lock(mutex_);
        if (receiver_closed_) return Get::Closed;
        if (count_ != 0) {
            out = std::move(*slots_[head_]);
            slots_[head_].reset(); // Moved-from owner is empty; no pool lock.
            head_ = (head_ + 1) % Capacity; --count_;
            return Get::Item;
        }
        return sender_closed_ ? Get::Closed : Get::Empty;
    }
    Get receive_until(detail::Message& out, int64_t deadline) noexcept {
        for (;;) {
            auto result = try_receive(out);
            if (result != Get::Empty) return result;
            if (now_us() >= deadline) return Get::Timeout;
            ready_.wait_until(deadline);
        }
    }
    void close_sender() noexcept {
        { Lock lock(mutex_); sender_closed_ = true; }
        ready_.signal();
    }
    void close_receiver() noexcept {
        std::array<std::optional<detail::Message>, Capacity> drain;
        {
            Lock lock(mutex_);
            receiver_closed_ = true;
            for (auto& slot : slots_) {
                if (slot) {
                    drain[--count_].emplace(std::move(*slot));
                    slot.reset();
                }
            }
            head_ = tail_ = 0;
        }
        ready_.signal();
        // Drain values destroyed after mailbox unlock, acquiring only pool lock.
    }
    size_t high_water() const noexcept { Lock lock(mutex_); return high_water_; }
};
static_assert(!std::is_copy_constructible<OwnedBuffer>::value, "owner must not copy");
static_assert(std::is_nothrow_move_constructible<detail::Message>::value, "queue move must not throw");
inline bool transform(OwnedBuffer& buffer) noexcept {
    if (!buffer.valid()) return false;
    const size_t length = buffer.size();
    for (size_t i = 0; i < length; ++i) {
        uint8_t value;
        if (!buffer.read(i, value) || !buffer.write(i, value ^ 0x5a)) return false;
    }
    return true;
}
} // namespace sl
