#pragma once
#include "svc_runtime.hpp"
#include "srpc/simulation.hpp"

namespace svc_rt {
using BeginFunction = StartResult (*)(Context&, Ready, Time) noexcept;
using PollFunction = Step (*)(Context&, Pending, Time) noexcept;
struct ComponentFunctions { BeginFunction begin; PollFunction poll; std::size_t host; };
enum class ComponentState { Ready, Pending, Complete, Lost };

// Stable frame: Context and native leases never outlive the host Pool/Simulation.
class ComponentFrame {
    Context context_;
    std::optional<Ready> ready_;
    std::optional<Pending> pending_;
    ComponentFunctions functions_;
    ComponentState state_ = ComponentState::Ready;
    std::int32_t admission_error_ = 0;
public:
    ComponentFrame(sl::Pool& pool, Ready ready, ComponentFunctions functions) noexcept
        : context_(pool), ready_(std::move(ready)), functions_(functions) {}
    ComponentFrame(const ComponentFrame&) = delete;
    ComponentFrame& operator=(const ComponentFrame&) = delete;
    bool start(Time now) noexcept {
        if (!ready_) return false;
        auto result = functions_.begin(context_, take(ready_), now);
        if (auto* started = std::get_if<Started>(&result)) {
            pending_.emplace(std::move(started->a0)); state_ = ComponentState::Pending;
            admission_error_ = 0; return true;
        }
        if (auto* rejected = std::get_if<Rejected>(&result)) {
            ready_.emplace(std::move(rejected->a0)); admission_error_ = rejected->a1;
            state_ = ComponentState::Ready; return false;
        }
        admission_error_ = std::get<Unavailable>(result).a0;
        state_ = ComponentState::Lost; return false;
    }
    void poll(Time now) noexcept {
        if (!pending_) return;
        auto step = functions_.poll(context_, take(pending_), now);
        if (auto* again = std::get_if<Again>(&step)) { pending_.emplace(std::move(again->a0)); return; }
        auto& continuation = std::get<Finished>(step).a0;
        if (auto* reusable = std::get_if<Reusable>(&continuation)) {
            ready_.emplace(std::move(reusable->a0)); state_ = ComponentState::Complete;
        } else state_ = ComponentState::Lost;
    }
    ComponentState state() const noexcept { return state_; }
    std::int32_t admission_error() const noexcept { return admission_error_; }
    const Context& context() const noexcept { return context_; }
};

template<std::size_t N> class Application {
public:
    static constexpr std::size_t count = N;
    static_assert(N >= 1 && N <= 4);
    using Hosts = std::array<srpc::Simulation*, N>;
    using Leases = std::array<std::optional<Ready>, N>;
private:
    Hosts hosts_;
    std::array<ComponentFunctions, N> functions_;
    std::array<std::optional<ComponentFrame>, N> frames_{};
public:
    // Native constructor is a trusted boundary; normal callers use generated
    // create_application, which validates/acquires all inputs before emplacing.
    Application(sl::Pool& pool, Leases& leases, const Hosts& hosts,
                const std::array<ComponentFunctions, N>& functions) noexcept
        : hosts_(hosts), functions_(functions) {
        for (std::size_t i = 0; i < N; ++i)
            frames_[i].emplace(pool, take(leases[functions[i].host]), functions[i]);
    }
    Application(const Application&) = delete;
    Application& operator=(const Application&) = delete;
    static bool create(std::optional<Application>& output, sl::Pool& pool, const Hosts& hosts,
                       const std::array<ComponentFunctions, N>& functions, std::size_t budget) noexcept {
        if (output || budget > 12) return false;
        const auto stats = pool.stats();
        if (stats.live_general > 12 || budget > 12 - stats.live_general) return false;
        std::array<bool, N> used{};
        for (std::size_t i = 0; i < N; ++i) {
            if (!hosts[i] || !functions[i].begin || !functions[i].poll || functions[i].host >= N) return false;
            if (used[functions[i].host]) return false;
            used[functions[i].host] = true;
            for (std::size_t j = 0; j < i; ++j) if (hosts[i] == hosts[j]) return false;
        }
        Leases leases;
        for (std::size_t i = 0; i < N; ++i) {
            leases[i] = hosts[i]->ready();
            // No partially constructed application is published. A runtime
            // acquisition failure retires earlier acquired leases via RAII;
            // it does not manufacture a rollback Ready or rebind any host.
            if (!leases[i]) return false;
        }
        output.emplace(pool, leases, hosts, functions);
        return true;
    }
    bool start(std::size_t component) noexcept {
        if (component >= N) return false;
        auto* host = hosts_[functions_[component].host];
        if (!host->quiescent()) return false; // Ready is not physical TX permission.
        return frames_[component]->start(host->now());
    }
    void poll(std::size_t component) noexcept {
        sl::require(component < N);
        frames_[component]->poll(hosts_[functions_[component].host]->now());
    }
    ComponentState state(std::size_t component) const noexcept {
        sl::require(component < N); return frames_[component]->state();
    }
    const Context& context(std::size_t component) const noexcept {
        sl::require(component < N); return frames_[component]->context();
    }
};
static_assert(!std::is_move_constructible_v<ComponentFrame> && !std::is_copy_constructible_v<ComponentFrame>);
static_assert(!std::is_move_constructible_v<Application<1>> && !std::is_copy_constructible_v<Application<1>>);
} // namespace svc_rt
