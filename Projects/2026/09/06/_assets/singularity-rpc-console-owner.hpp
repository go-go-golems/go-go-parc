#pragma once
#include "packet_radio.hpp"
#include "status_screen.hpp"
#include "nvs_epoch.hpp"
#include "keyboard.hpp"
#include "srpc/client.hpp"
#include "srpc/server.hpp"
#include "esp_system.h"
#include <unistd.h>
#include <fcntl.h>
#include <cstring>

namespace bench {
// Static runtime: one Client per binding lifetime, one owner for SPI, endpoints,
// service state and rendering. USB is a trusted supervisor, radio is unauthenticated.
class LiveBench {
    PacketRadio radio_;
    Keyboard keyboard_;
    srpc::ui::KeyEvent last_key_{};
    enum class View { Console, Input, Bench } view_ = View::Console;
    bool dump_requested_ = false;
    srpc::ui::Console console_;
    srpc::Time last_rx_ = 0;
    sl::Pool pool_;
    sl::OwnedBuffer waiting_;
    enum class Outbound { Smoke, Call, Reply } waiting_kind_ = Outbound::Smoke;
    srpc::Time waiting_at_ = 0, call_at_ = 0;
    std::optional<srpc::Client> client_;
    std::optional<srpc::Server> server_;
    std::optional<srpc::ReadyClient> ready_;
    std::optional<srpc::PendingCall> pending_;
    srpc::EpochRecord identity_{};
    srpc::Binding binding_{};
    srpc::Store identity_status_ = srpc::Store::Missing;
    bool tx_call_ = false, suppress_next_ = false, peer_seen_ = false;
    uint32_t tx_request_ = 0;
    unsigned drop_replies_ = 0, dropped_ = 0, completed_ = 0, ok_ = 0, unknown_ = 0;
    char line_[128]{}, display_identity_[48]{};
    size_t used_ = 0;
    bool overflow_ = false;
    unsigned sequence_ = 0;
    char board_ = '?';
    void boot_identity() {
        srpc::NvsEpoch storage;
        const auto boot = srpc::advance_boot(storage);
        identity_status_ = boot.status;
        srpc::EpochRecord verify;
        if (boot.status == srpc::Store::Ok) {
            if (storage.load(verify) != srpc::Store::Ok || verify.node != boot.record.node || verify.epoch != boot.record.epoch)
                identity_status_ = srpc::Store::ReadError;
            else identity_ = verify; // Publish only after commit and readback.
        }
        std::printf("LIVE IDENTITY status=%u node=%u epoch=%llu committed=%u\n", unsigned(identity_status_),
            unsigned(identity_.node), (unsigned long long)identity_.epoch, unsigned(identity_.node != 0));
    }
    void status() {
        const auto pool = pool_.stats();
        std::printf("LIVE STATUS board=%c armed=%u busy=%u fault=%u sf=%u tx=%u rx=%u recoveries=%u bad_rx=%u irq=%u node=%u epoch=%llu bound=%u completed=%u ok=%u unknown=%u commits=%llu cache=%llu dropped=%u peer=%u peer_epoch=%llu grant=%u rejected=%llu led=%u pool_live=%u allocations=%llu releases=%llu heap=%u\n",
            board_, unsigned(radio_.armed()), unsigned(radio_.busy()), unsigned(radio_.fault()), radio_.sf,
            radio_.tx_count, radio_.rx_count, radio_.recoveries, radio_.bad_rx, radio_.irq_wakes,
            unsigned(identity_.node), (unsigned long long)identity_.epoch, unsigned(client_.has_value()), completed_, ok_, unknown_,
            (unsigned long long)(server_ ? server_->commits() : 0), (unsigned long long)(server_ ? server_->cache_hits() : 0), dropped_,
            unsigned(client_ ? binding_.server : 0), (unsigned long long)(client_ ? binding_.server_boot : 0),
            unsigned(client_ ? binding_.grant : 0), (unsigned long long)(server_ ? server_->drops() : 0), unsigned(server_ ? server_->led() : 0), unsigned(pool.live_general + pool.live_control),
            (unsigned long long)pool.allocations, (unsigned long long)pool.releases, unsigned(esp_get_free_heap_size()));
    }
    bool queue(const srpc::Packet& packet, Outbound kind, srpc::Time when) {
        if (waiting_.valid()) return false;
        if (!srpc::allocate_packet(pool_, packet, waiting_)) return false;
        waiting_kind_ = kind; waiting_at_ = when; return true;
    }
    void start_call(unsigned service, unsigned level, unsigned deadline_ms) {
        const auto now = srpc::Time(esp_timer_get_time());
        if (!ready_ || pending_ || radio_.busy() || waiting_.valid() || !radio_.armed() || service < 1 || service > 4 || level > 255 || !deadline_ms || deadline_ms > 30000) {
            std::puts("LIVE ERROR call_guard");
            console_.notice(!client_ ? "USB: bind peers first" : !radio_.armed() ? "Radio stopped: arm in setup" : "Busy or invalid call; not accepted", now);
            return;
        }
        call_at_ = now;
        auto started = ready_->start(srpc::Service(service), uint8_t(level), now, now + uint64_t(deadline_ms) * 1000, 2000000);
        std::printf("RPC START code=%u id=%u service=%u deadline_ms=%u\n", unsigned(started.code), unsigned(client_->request_id()), service, deadline_ms);
        if (started.code == srpc::StartCode::Accepted) {
            console_.started(binding_, client_->request_id(), srpc::Service(service), uint8_t(level), now, client_->deadline());
            pending_ = std::move(started.pending); ready_.reset();
        } else console_.notice("Call rejected by typed endpoint", now);
    }
    void stop_radio() {
        waiting_.reset(); const bool busy = radio_.busy(); const bool stopped = radio_.stop();
        if (stopped && busy && tx_call_ && client_) client_->driver_fault(tx_request_);
        if (stopped) tx_call_ = false;
        console_.notice(stopped ? (pending_ ? "Stopped; pending call still resolves" : "Radio stopped") : "Radio fault; reboot required", esp_timer_get_time());
        std::printf("LIVE STOP ok=%u\n", unsigned(stopped));
    }
    srpc::ui::RuntimeStatus ui_status() const {
        srpc::ui::RuntimeStatus state;
        state.board = board_; state.node = identity_.node; state.epoch = identity_.epoch;
        state.bound = client_.has_value(); state.peer = state.bound ? binding_.server : 0;
        state.peer_epoch = state.bound ? binding_.server_boot : 0; state.grant = state.bound ? binding_.grant : 0;
        state.armed = radio_.armed(); state.busy = radio_.busy(); state.fault = radio_.fault();
        state.sf = radio_.sf; state.key_ok = keyboard_.healthy(); state.transmitting_call = tx_call_ && radio_.busy();
        state.now = esp_timer_get_time(); state.last_rx = last_rx_; state.rx_seen = radio_.rx_count != 0;
        state.rssi = radio_.rssi; state.snr_quarters = radio_.snr_quarters;
        state.commits = server_ ? server_->commits() : 0; state.cache = server_ ? server_->cache_hits() : 0;
        return state;
    }
    void command(const char* text) {
        unsigned a = 0, b = 0, c = 0; unsigned long long epoch = 0; char trailing;
        if (!std::strcmp(text, "status")) { status(); return; }
        if (!std::strcmp(text, "ui_status")) {
            std::printf("UI STATUS page=%u detail=%u history=%u active=%u sensor_known=%u sensor=%ld led_known=%u led=%ld led_uncertain=%u\n",
                unsigned(console_.page()), unsigned(console_.detail()), unsigned(console_.history_size()), unsigned(console_.active() != nullptr),
                unsigned(console_.sensor().known), long(console_.sensor().value), unsigned(console_.led().known), long(console_.led().value), unsigned(console_.led_uncertain()));
            return;
        }
        if (std::sscanf(text, "ui_key %u %c", &a, &trailing) == 1 && a > 0 && a < 128) {
            std::printf("UI KEY source=injected key=%u pressed=1\n", a);
            console_.key({char(a), 0, true}, esp_timer_get_time()); return;
        }
        if (!std::strcmp(text, "keyboard_status")) {
            std::printf("UI KEYBOARD status=%s events=%u overflows=%u error=%s\n",
                keyboard_.healthy() ? "ready" : "fault", keyboard_.events(), keyboard_.overflows(), esp_err_to_name(keyboard_.error()));
            return;
        }
        if (!std::strcmp(text, "screen_dump")) {
            if (radio_.armed() || radio_.busy() || pending_) { std::puts("UI SCREEN ERROR active_radio_or_call"); return; }
            dump_requested_ = true; return;
        }
        if (!std::strcmp(text, "input_check")) { view_ = View::Input; return; }
        if (!std::strcmp(text, "bench_screen")) { view_ = View::Bench; return; }
        if (!std::strcmp(text, "console_screen")) { view_ = View::Console; return; }
        if (std::sscanf(text, "provision %u %c", &a, &trailing) == 1) {
            if (radio_.armed() || identity_.node || !a || a > 65535) { std::puts("LIVE ERROR provision_guard"); return; }
            srpc::NvsEpoch storage; const auto result = srpc::provision(storage, uint16_t(a));
            std::printf("LIVE PROVISION status=%u\n", unsigned(result));
            if (result == srpc::Store::Ok) boot_identity();
            return;
        }
        if (std::sscanf(text, "bind %u %llu %u %c", &a, &epoch, &b, &trailing) == 3) {
            if (radio_.armed() || !identity_.node || client_ || !a || a > 65535 || a == identity_.node || !epoch || !b) {
                std::puts("LIVE ERROR bind_guard"); return;
            }
            const srpc::Binding outgoing{identity_.node, uint16_t(a), identity_.epoch, epoch, b, 1};
            const srpc::Binding incoming{uint16_t(a), identity_.node, epoch, identity_.epoch, b, 1};
            server_.emplace(identity_.node, identity_.epoch, 1, true);
            sl::require(server_->bind(incoming));
            binding_ = outgoing; client_.emplace(outgoing); ready_ = client_->ready();
            std::printf("LIVE BOUND peer=%u epoch=%llu grant=%u mode=P2_UNAUTHENTICATED\n", a, epoch, b); return;
        }
        if (std::sscanf(text, "arm %u %c", &a, &trailing) == 1) {
            std::printf("LIVE ARM ok=%u sf=%u hz=915000000 bw=500000 dbm=0\n", unsigned(radio_.arm(a)), a); return;
        }
        if (!std::strcmp(text, "stop")) { stop_radio(); return; }
        if (!std::strcmp(text, "reboot")) {
            // Reset hardware before resetting memory, including a quarantined driver.
            gpio_set_level(GPIO_NUM_3, 0);
            std::puts("LIVE REBOOT requested=1"); std::fflush(stdout);
            vTaskDelay(pdMS_TO_TICKS(100)); esp_restart();
        }
        if (std::sscanf(text, "drop_replies %u %c", &a, &trailing) == 1 && a <= 3) {
            drop_replies_ = a; std::printf("LIVE DROP armed=%u\n", a); return;
        }
        if (!std::strcmp(text, "suppress_done")) {
            suppress_next_ = true; std::puts("LIVE SUPPRESS armed=1"); return;
        }
        if (std::sscanf(text, "call %u %u %u %c", &a, &b, &c, &trailing) == 3) {
            start_call(a, b, c); return;
        }
        if (!std::strcmp(text, "ping")) {
            if (pending_ || waiting_.valid() || !radio_.eligible(esp_timer_get_time())) { std::puts("LIVE ERROR busy_or_unarmed"); return; }
            srpc::Packet packet{}; packet.size = 48;
            const char* prefix = "SINGULARITY-PHYSICAL-SMOKE";
            std::memcpy(packet.bytes.data(), prefix, std::strlen(prefix));
            packet.bytes[32] = uint8_t(board_); srpc::put(packet.bytes.data(), 36, ++sequence_, 4);
            sl::require(queue(packet, Outbound::Smoke, esp_timer_get_time()));
            std::printf("LIVE PING queued=%u\n", sequence_); return;
        }
        std::puts("LIVE ERROR command_or_arguments");
    }
    void received(const srpc::Packet& packet, srpc::Time now) {
        last_rx_ = now;
        std::printf("LIVE RX bytes=%u rssi=%d snr_quarters=%d data=", unsigned(packet.size), radio_.rssi, radio_.snr_quarters);
        for (size_t i = 0; i < packet.size; ++i) std::printf("%02X", unsigned(packet.bytes[i]));
        std::puts("");
        srpc::Frame frame;
        if (srpc::decode(packet, frame) != srpc::Codec::Ok) return;
        if (frame.kind == srpc::Kind::Reply) {
            if (client_ && client_->receive(packet, now)) peer_seen_ = true;
            return;
        }
        if (!server_) return;
        auto admission = server_->admit(packet);
        if (admission.action == srpc::Admission::Drop) return;
        peer_seen_ = true;
        srpc::Packet reply;
        const bool have_reply = admission.action == srpc::Admission::Accepted
            ? server_->execute(admission.entry, now, reply)
            : admission.action == srpc::Admission::Cached || admission.action == srpc::Admission::ErrorReply;
        if (admission.action != srpc::Admission::Accepted) reply = admission.reply;
        std::printf("RPC SERVER id=%u admission=%u commits=%llu cache=%llu\n", unsigned(frame.request), unsigned(admission.action),
            (unsigned long long)server_->commits(), (unsigned long long)server_->cache_hits());
        if (!have_reply) return;
        if (drop_replies_) {
            --drop_replies_; ++dropped_;
            std::printf("RPC DROP REPLY id=%u after_commit=1 remaining=%u\n", unsigned(frame.request), drop_replies_);
        } else if (!queue(reply, Outbound::Reply, now + 100000)) std::puts("RPC REPLY queue_full=1 cache_retained=1");
    }
    void step() {
        srpc::Packet packet{};
        const auto event = radio_.poll(packet);
        auto now = srpc::Time(esp_timer_get_time());
        if (event == PacketRadio::Event::Received) received(packet, now);
        else if (event == PacketRadio::Event::Done || event == PacketRadio::Event::Recovered) {
            if (tx_call_ && client_) {
                if (event == PacketRadio::Event::Done) client_->tx_done(tx_request_, now);
                else client_->driver_fault(tx_request_);
            }
            tx_call_ = false;
            if (event == PacketRadio::Event::Done)
                std::printf("PHY TIMING sf=%u bytes=%u expected_us=%llu edge_us=%llu\n", radio_.sf, unsigned(radio_.last_tx_size),
                    (unsigned long long)radio_.expected_airtime, (unsigned long long)radio_.last_tx_edge_us);
            std::printf("LIVE TX %s owner_released=1\n", event == PacketRadio::Event::Done ? "DONE" : "RECOVERED standby_verified=1");
        }
        if (pending_) {
            auto polled = pending_->poll(now);
            if (polled.result.outcome != srpc::Outcome::Waiting) {
                const auto& result = polled.result;
                ++completed_; if (result.outcome == srpc::Outcome::Ok) ++ok_;
                if (result.outcome == srpc::Outcome::OutcomeUnknown) ++unknown_;
                std::printf("RPC RESULT id=%u outcome=%u attempts=%u elapsed_us=%llu driver_busy=%u service=%u body=",
                    unsigned(result.request), unsigned(result.outcome), result.attempts, (unsigned long long)(now - call_at_),
                    unsigned(radio_.busy()), unsigned(result.reply.service));
                for (size_t i = 0; i < result.reply.length; ++i) std::printf("%02X", unsigned(result.reply.body[i]));
                std::puts("");
                console_.completed(result, now);
                ready_ = std::move(polled.ready); pending_.reset();
                if (waiting_.valid() && waiting_kind_ == Outbound::Call) waiting_.reset();
            }
        }
        now = esp_timer_get_time();
        if (client_ && client_->request_due(now) && !waiting_.valid() && radio_.eligible(now))
            queue(client_->request_packet(), Outbound::Call, now);
        if (waiting_.valid() && now >= waiting_at_ && radio_.eligible(now)) {
            const bool call = waiting_kind_ == Outbound::Call;
            const uint32_t request = call ? client_->request_id() : 0;
            const bool accepted = radio_.start(waiting_, now, suppress_next_, call ? client_->deadline() : UINT64_MAX);
            if (accepted || radio_.busy()) {
                suppress_next_ = false;
                tx_call_ = call; tx_request_ = request;
                if (call) { sl::require(client_->tx_started(request, now)); console_.attempts(client_->attempts()); }
            }
            std::printf("LIVE TX START accepted=%u request=%u call=%u\n", unsigned(accepted), unsigned(request), unsigned(call));
        }
    }
public:
    [[noreturn]] void run(Screen& screen, char board) {
        board_ = board; boot_identity();
        keyboard_.begin();
        fcntl(STDIN_FILENO, F_SETFL, O_NONBLOCK);
        std::puts("LIVE READY transport=PHYSICAL startup=UNARMED mode=P2_UNAUTHENTICATED");
        auto next_screen = esp_timer_get_time();
        for (;;) {
            char input[32]; const auto n = ::read(STDIN_FILENO, input, sizeof(input));
            for (int i = 0; i < n; ++i) {
                const char c = input[i];
                if (c == '\r') continue;
                if (c == '\n') {
                    line_[used_] = 0;
                    if (overflow_) std::puts("LIVE ERROR line_too_long"); else command(line_);
                    used_ = 0; overflow_ = false;
                } else if (used_ < sizeof(line_) - 1) line_[used_++] = c;
                else overflow_ = true;
            }
            step();
            if (dump_requested_) {
                dump_requested_ = false;
                if (!radio_.armed() && !radio_.busy() && !pending_) screen.dump();
                else std::puts("UI SCREEN ERROR active_radio_or_call");
            }
            std::array<srpc::ui::KeyEvent, 4> keys{};
            const auto key_count = keyboard_.poll(keys);
            for (size_t i = 0; i < key_count; ++i) {
                last_key_ = keys[i];
                if (view_ == View::Console) console_.key(keys[i], esp_timer_get_time());
                else if (keys[i].pressed && keys[i].key == 'x') stop_radio();
            }
            srpc::ui::Action action;
            if (console_.next_action(action)) {
                if (action.kind == srpc::ui::ActionKind::Stop) stop_radio();
                else start_call(unsigned(action.service), action.level, 8000);
            }
            if (esp_timer_get_time() >= next_screen) {
                if (view_ == View::Console) {
                    screen.console(console_, ui_status());
                    next_screen = esp_timer_get_time() + 100000;
                    vTaskDelay(1);
                    continue;
                }
                if (view_ == View::Input) {
                    screen.keyboard_check(keyboard_.healthy(), keyboard_.events(), last_key_.position,
                        unsigned(uint8_t(last_key_.key)), last_key_.pressed, radio_.armed());
                    next_screen = esp_timer_get_time() + 100000;
                    vTaskDelay(1);
                    continue;
                }
                std::snprintf(display_identity_, sizeof(display_identity_), "N%u E%llu EX%llu DUP%llu L%u", unsigned(identity_.node),
                    (unsigned long long)identity_.epoch, (unsigned long long)(server_ ? server_->commits() : 0),
                    (unsigned long long)(server_ ? server_->cache_hits() : 0), unsigned(server_ ? server_->led() : 0));
                screen.physical(radio_.armed(), peer_seen_, radio_.sf, display_identity_);
                screen.counts(completed_, ok_, unknown_, 128);
                screen.show(radio_.fault() ? "RADIO FAULT" : pending_ ? "RPC WAITING" : radio_.armed() ? "RPC READY / SERVING" : "USB: ARM TO TEST", false, radio_.fault());
                next_screen = esp_timer_get_time() + 500000;
            }
            vTaskDelay(1);
        }
    }
};
} // namespace bench
