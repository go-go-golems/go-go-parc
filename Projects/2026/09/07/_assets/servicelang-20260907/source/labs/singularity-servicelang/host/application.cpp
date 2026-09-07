#include "application.hpp"
#include <cstdio>

int main() {
    {
        sl::Pool pool;
        srpc::Simulation a;
        auto denied = srpc::Config{}; denied.permit = false;
        srpc::Simulation b(denied);
        std::optional<svc_generated::Application> app;
        sl::require(svc_generated::create_application(app, pool, {&a, &b}));
        sl::require(!svc_generated::create_application(app, pool, {&a, &b}));
        sl::require(app->start(0) && app->start(1));
        sl::require(!app->start(0));
        unsigned steps = 0;
        for (; steps < 256; ++steps) {
            a.step(); b.step(); app->poll(0); app->poll(1);
            if (app->state(0) == svc_rt::ComponentState::Complete &&
                app->state(1) == svc_rt::ComponentState::Complete) break;
        }
        sl::require(steps < 256);
        // The plan intentionally reverses component order relative to host order.
        sl::require(app->context(0).observation_count == 1 && app->context(0).observations[0].outcome == 3);
        sl::require(app->context(1).observation_count == 1 && app->context(1).observations[0].outcome == 1);
        app.reset(); // endpoints retire before Pool/Simulation destruction
        for (unsigned i = 0; (!a.quiescent() || !b.quiescent()) && i < 256; ++i) { a.step(); b.step(); }
        a.audit(); b.audit();
        std::printf("APPLICATION reversed_endpoint_mapping=PASS outcomes=NotSent,Ok stable_frames=PASS teardown_audit=PASS\n");
    }
    {
        sl::Pool pool; srpc::Simulation a, b;
        std::optional<svc_generated::Application> app;
        sl::require(!svc_generated::create_application(app, pool, {&a, &a}) && !app);
        // Duplicate-host validation did not acquire/retire either endpoint.
        auto ar = a.ready(), br = b.ready(); sl::require(ar.has_value() && br.has_value());
        std::printf("APPLICATION duplicate_host_denied_before_acquisition=PASS\n");
    }
    {
        sl::Pool pool; srpc::Simulation a, b;
        auto held = b.ready(); sl::require(held.has_value());
        std::optional<svc_generated::Application> app;
        sl::require(!svc_generated::create_application(app, pool, {&a, &b}) && !app);
        sl::require(!a.ready()); // earlier acquisition retired, not falsely rolled back
        auto unaffected = held->start(srpc::Service::Sensor, 0, 0, 1000);
        sl::require(unaffected.code == srpc::StartCode::Accepted);
        std::printf("APPLICATION unavailable_endpoint_no_publication=PASS earlier_lease_retired=PASS existing_lease_preserved=PASS\n");
    }
}
