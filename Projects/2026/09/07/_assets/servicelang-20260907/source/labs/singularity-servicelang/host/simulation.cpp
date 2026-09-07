#include "generated.hpp"
#include "srpc/simulation.hpp"
#include <cstdio>

namespace {
struct Scenario { const char* name; srpc::Config config; std::int32_t milliseconds; srpc::Outcome expected; bool retained; };
struct Snapshot {
    std::int32_t outcome = 0, value = 0;
    unsigned attempts = 0, steps = 0, cleanup = 0;
    srpc::Time completed_at = 0;
    bool retained = false, reusable = false;
    std::array<std::uint64_t, 10> counts{};
};
std::array<std::uint64_t, 10> counters(const srpc::Counters& c) {
    return {c.request_starts, c.reply_starts, c.request_drops, c.reply_drops,
        c.recoveries, c.commits, c.cache_hits, c.reset_suppressed,
        c.response_overflow, c.overlap_drops};
}
Snapshot run(const Scenario& scenario, bool generated) {
    srpc::Simulation sim(scenario.config);
    sl::Pool application_pool;
    svc_rt::Context ctx(application_pool);
    auto ready = sim.ready(); sl::require(ready.has_value());
    Snapshot result;
    if (generated) {
        auto started = svc_generated::fnbegin_ufor(ctx, std::move(*ready), sim.now(), scenario.milliseconds);
        sl::require(std::holds_alternative<svc_rt::Started>(started));
        std::optional<svc_rt::Pending> pending;
        pending.emplace(std::move(std::get<svc_rt::Started>(started).a0));
        for (; result.steps < 256; ++result.steps) {
            sim.step();
            auto step = svc_generated::fntick(ctx, svc_rt::take(pending), sim.now());
            if (auto* again = std::get_if<svc_rt::Again>(&step)) {
                pending.emplace(std::move(again->a0)); continue;
            }
            auto& continuation = std::get<svc_rt::Finished>(step).a0;
            if (auto* reusable = std::get_if<svc_rt::Reusable>(&continuation)) {
                ready.reset(); ready.emplace(std::move(reusable->a0)); result.reusable = true;
            }
            sl::require(ctx.observation_count == 1 && ctx.dropped_observations == 0);
            result.outcome = ctx.observations[0].outcome;
            result.value = ctx.observations[0].value;
            result.attempts = unsigned(sim.counters().request_starts);
            break;
        }
    } else {
        // Reference path uses native APIs directly, not the ServiceLang adapter.
        auto started = ready->start(srpc::Service::Sensor, 0, sim.now(),
            sim.now() + std::uint64_t(scenario.milliseconds) * 1000);
        sl::require(started.code == srpc::StartCode::Accepted && started.pending.has_value());
        for (; result.steps < 256; ++result.steps) {
            sim.step(); auto polled = started.pending->poll(sim.now());
            if (polled.result.outcome == srpc::Outcome::Waiting) continue;
            result.outcome = std::int32_t(polled.result.outcome);
            if (polled.result.outcome == srpc::Outcome::Ok)
                result.value = srpc::signed32(std::uint32_t(srpc::get(polled.result.reply.body.data(), 4, 4)));
            else if (polled.result.outcome == srpc::Outcome::RemoteError)
                result.value = std::int32_t(polled.result.reply.status);
            result.attempts = polled.result.attempts;
            result.reusable = polled.ready.has_value();
            if (polled.ready) { ready.reset(); ready.emplace(std::move(*polled.ready)); }
            break;
        }
    }
    sl::require(result.steps < 256);
    result.completed_at = sim.now(); result.retained = !sim.quiescent();
    for (; !sim.quiescent() && result.cleanup < 256; ++result.cleanup) sim.step();
    sl::require(result.cleanup < 256); sim.audit();
    result.counts = counters(sim.counters());
    const auto pool = application_pool.stats();
    sl::require(pool.allocations == pool.releases && pool.live_general == 0 && pool.live_control == 0);
    return result;
}
void compare(const Scenario& scenario) {
    const auto native = run(scenario, false), generated = run(scenario, true);
    sl::require(generated.outcome == std::int32_t(scenario.expected));
    sl::require(generated.retained == scenario.retained);
    sl::require(native.outcome == generated.outcome && native.value == generated.value &&
        native.attempts == generated.attempts && native.steps == generated.steps &&
        native.cleanup == generated.cleanup && native.completed_at == generated.completed_at &&
        native.retained == generated.retained && native.reusable == generated.reusable &&
        native.counts == generated.counts);
    std::printf("PARITY %s outcome=%d attempts=%u completed_us=%llu retained_tx=%d reusable=%d steps=%u cleanup=%u audit=PASS\n",
        scenario.name, generated.outcome, generated.attempts,
        static_cast<unsigned long long>(generated.completed_at), generated.retained,
        generated.reusable, generated.steps + 1, generated.cleanup);
}
void endpoint_edges() {
    sl::Pool pool; svc_rt::Context ctx(pool);
    {
        srpc::Client client(srpc::Binding{}); auto ready = client.ready(); sl::require(ready.has_value());
        auto rejected = svc_generated::fnbegin_ufor(ctx, std::move(*ready), 0, 0);
        sl::require(std::holds_alternative<svc_rt::Rejected>(rejected));
        auto accepted = svc_generated::fnbegin_ufor(ctx, std::move(std::get<svc_rt::Rejected>(rejected).a0), 0, 10);
        sl::require(std::holds_alternative<svc_rt::Started>(accepted));
        client.invalidate();
        auto step = svc_generated::fntick(ctx, std::move(std::get<svc_rt::Started>(accepted).a0), 1);
        sl::require(std::holds_alternative<svc_rt::Lost>(std::get<svc_rt::Finished>(step).a0));
        sl::require(ctx.observations[0].outcome == 3 && !client.ready());
    }
    {
        srpc::Client client(srpc::Binding{}); auto ready = client.ready(); sl::require(ready.has_value());
        auto accepted = svc_generated::fnbegin(ctx, std::move(*ready), 0);
        sl::require(std::holds_alternative<svc_rt::Started>(accepted));
        sl::require(client.tx_started(client.request_id(), 0)); client.invalidate();
        auto step = svc_generated::fntick(ctx, std::move(std::get<svc_rt::Started>(accepted).a0), 1);
        sl::require(std::holds_alternative<svc_rt::Lost>(std::get<svc_rt::Finished>(step).a0));
        sl::require(ctx.observations[1].outcome == 4 && !client.ready());
    }
    {
        srpc::Client client(srpc::Binding{}); auto ready = client.ready(); sl::require(ready.has_value());
        client.invalidate();
        auto unavailable = svc_generated::fnbegin(ctx, std::move(*ready), 0);
        sl::require(std::holds_alternative<svc_rt::Unavailable>(unavailable) && !client.ready());
    }
    std::printf("ENDPOINT rejected_retains_ready=PASS invalidation_notsent_lost=PASS invalidation_unknown_lost=PASS stale_ready_unavailable=PASS\n");
}
} // namespace
int main() {
    srpc::Config config; config.seed = 13;
    compare({"success", config, 8000, srpc::Outcome::Ok, false});
    auto denied = config; denied.permit = false;
    compare({"no-permission", denied, 8000, srpc::Outcome::NotSent, false});
    auto lost = config; lost.reply_loss = 100;
    compare({"lost-replies", lost, 8000, srpc::Outcome::OutcomeUnknown, false});
    compare({"retained-tx", config, 1, srpc::Outcome::OutcomeUnknown, true});
    endpoint_edges();
}
