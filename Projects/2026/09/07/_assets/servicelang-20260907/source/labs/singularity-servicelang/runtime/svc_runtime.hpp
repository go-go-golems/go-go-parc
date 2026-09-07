#pragma once
#include "srpc/client.hpp"
#include "sl/pool.hpp"
#include <array>
#include <cstdlib>
#include <optional>
#include <type_traits>
#include <utility>
#include <variant>

namespace svc_rt {
inline constexpr unsigned abi_version = 1;
using Time = srpc::Time;
using Ready = srpc::ReadyClient;
using Pending = srpc::PendingCall;
using Buffer = sl::OwnedBuffer;
struct Unit {};
struct Sample { std::int32_t value; };
struct Ok { Sample a0; };
struct RemoteError { std::int32_t a0; };
struct NotSent {};
struct Unknown {};
struct RuntimeFault { std::int32_t a0; };
using CallResult = std::variant<Ok, RemoteError, NotSent, Unknown, RuntimeFault>;
struct Started { Pending a0; };
struct Rejected { Ready a0; std::int32_t a1; };
struct Unavailable { std::int32_t a0; };
using StartResult = std::variant<Started, Rejected, Unavailable>;
struct Reusable { Ready a0; };
struct Lost { std::int32_t a0; };
using Continuation = std::variant<Reusable, Lost>;
struct Waiting { Pending a0; };
struct Complete { CallResult a0; Continuation a1; };
using PollResult = std::variant<Waiting, Complete>;
struct Again { Pending a0; };
struct Finished { Continuation a0; };
using Step = std::variant<Again, Finished>;
struct Allocated { Buffer a0; };
struct AllocFailed { std::int32_t a0; };
using Allocation = std::variant<Allocated, AllocFailed>;
struct Number { std::int32_t a0; };
struct Overflow {};
using Arithmetic = std::variant<Number, Overflow>;

// Stable host context; Pool must outlive context and every generated owner.
// This is not a radio driver or an authority to arm RF.
struct Observation { std::int32_t outcome, value; };
struct Context {
    sl::Pool::GeneralAllocator memory;
    std::array<Observation, 64> observations{};
    std::size_t observation_count = 0, dropped_observations = 0;
    explicit Context(sl::Pool& pool) noexcept : memory(pool.general()) {}
    Context(const Context&) = delete;
    Context& operator=(const Context&) = delete;
};
template<class T> T take(std::optional<T>& slot) noexcept {
    sl::require(slot.has_value());
    T value = std::move(*slot);
    slot.reset();
    return value;
}
[[noreturn]] inline void unreachable() noexcept { std::abort(); }
inline StartResult rpc_start(Context&, Ready ready, Time now, std::int32_t milliseconds) noexcept {
    Time deadline = 0;
    if (milliseconds <= 0 || !srpc::add_time(now, std::uint64_t(milliseconds) * 1000, deadline))
        return Rejected{std::move(ready), 1};
    auto result = ready.start(srpc::Service::Sensor, 0, now, deadline);
    if (result.code == srpc::StartCode::Accepted && result.pending)
        return Started{std::move(*result.pending)};
    // Unexpected native failures retire Ready via destruction; no automatic rebind.
    return Unavailable{2};
}
inline CallResult decode_result(const srpc::Result& r) noexcept {
    switch (r.outcome) {
    case srpc::Outcome::Ok:
        if (r.reply.kind != srpc::Kind::Reply || r.reply.service != srpc::Service::Sensor ||
            r.reply.status != srpc::ReplyCode::Ok || srpc::valid(r.reply) != srpc::Codec::Ok)
            return RuntimeFault{3};
        return Ok{Sample{srpc::signed32(std::uint32_t(srpc::get(r.reply.body.data(), 4, 4)))}};
    case srpc::Outcome::RemoteError: return RemoteError{std::int32_t(r.reply.status)};
    case srpc::Outcome::NotSent: return NotSent{};
    case srpc::Outcome::OutcomeUnknown: return Unknown{};
    case srpc::Outcome::Invalid: return RuntimeFault{4};
    case srpc::Outcome::Waiting: return RuntimeFault{5};
    }
    return RuntimeFault{6};
}
inline PollResult rpc_poll(Context&, Pending pending, Time now) noexcept {
    auto native = pending.poll(now);
    if (native.result.outcome == srpc::Outcome::Waiting) {
        if (native.ready) return Complete{RuntimeFault{7}, Lost{7}};
        return Waiting{std::move(pending)};
    }
    CallResult result = decode_result(native.result);
    if (native.ready) return Complete{result, Reusable{std::move(*native.ready)}};
    return Complete{result, Lost{8}};
}
inline Unit close(Context&, Ready) noexcept { return {}; }
inline Allocation allocate(Context& ctx, std::int32_t bytes) noexcept {
    if (bytes < 0 || bytes > 128) return AllocFailed{1};
    Buffer buffer;
    const auto result = ctx.memory.allocate(std::size_t(bytes), buffer);
    if (result != sl::Alloc::Ok) return AllocFailed{2};
    return Allocated{std::move(buffer)};
}
inline Unit release(Context&, Buffer) noexcept { return {}; }
inline std::int32_t length(Context&, const Buffer& buffer) noexcept { return std::int32_t(buffer.size()); }
inline Unit observe(Context& ctx, std::int32_t outcome, std::int32_t value) noexcept {
    if (ctx.observation_count < ctx.observations.size())
        ctx.observations[ctx.observation_count++] = Observation{outcome, value};
    else if (ctx.dropped_observations != SIZE_MAX) ++ctx.dropped_observations;
    return {};
}
inline Arithmetic add(Context&, std::int32_t a, std::int32_t b) noexcept {
    const std::int64_t sum = std::int64_t(a) + std::int64_t(b);
    if (sum < INT32_MIN || sum > INT32_MAX) return Overflow{};
    return Number{std::int32_t(sum)};
}
static_assert(!std::is_copy_constructible_v<Ready> && std::is_nothrow_move_constructible_v<Ready>);
static_assert(!std::is_copy_constructible_v<Pending> && std::is_nothrow_move_constructible_v<Pending>);
static_assert(!std::is_copy_constructible_v<Buffer> && std::is_nothrow_move_constructible_v<Buffer>);
static_assert(!std::is_copy_constructible_v<Step> && std::is_nothrow_move_constructible_v<Step>);
} // namespace svc_rt
