// Report-time host probe for revision fb35635 / implementation 08dbb8f.
// Uses the explicit untyped test adapter, not the normal application API.
#include "protocol_suite.hpp"
int main() {
    using sl::testing::Access;
    {
        sl::Pool first, second;
        sl::Session session;
        auto ready = suite::connect(session);
        auto input = suite::data(first);
        auto pending = ready.try_submit(input.payload);
        CHECK(session.server_step(suite::deadline()) == sl::Status::Accepted);
        sl::detail::Message reply;
        CHECK(Access::remove_reply(session, reply) == sl::Get::Item);
        const auto original_id = reply.payload.allocation_id();
        reply.payload.reset();
        CHECK(second.general().allocate(64, reply.payload) == sl::Alloc::Ok);
        const auto replacement_id = reply.payload.allocation_id();
        CHECK(Access::reply(session, reply) == sl::Put::Accepted);
        auto result = pending.next->poll(suite::deadline());
        std::printf("cross_pool original_id=%llu replacement_id=%llu accepted_done=%d\n",
            (unsigned long long)original_id, (unsigned long long)replacement_id,
            result.status == sl::Status::Done);
    }
    {
        sl::Session session;
        auto ready = suite::connect(session);
        auto closing = ready.try_close();
        CHECK(session.server_step(suite::deadline()) == sl::Status::Accepted);
        sl::detail::Message discarded;
        CHECK(Access::remove_reply(session, discarded) == sl::Get::Item);
        auto result = closing.next->poll(suite::deadline());
        std::printf("missing_close_ack returned_closed=%d session_aborted=%d\n",
            result == sl::Status::Closed, session.aborted());
    }
}
