#pragma once
#include "srpc/codec.hpp"
namespace srpc {
struct Binding {
    uint16_t client = 1, server = 2;
    uint64_t client_boot = 1, server_boot = 1;
    uint32_t grant = 1, generation = 1;
    bool valid() const noexcept { return client && server && client != server && client_boot && server_boot && grant && generation; }
    bool accepts_request(const Frame& f) const noexcept {
        return f.source == client && f.destination == server && f.source_boot == client_boot &&
            f.destination_boot == server_boot && f.grant == grant && f.generation == generation;
    }
    bool accepts_reply(const Frame& f) const noexcept {
        return f.source == server && f.destination == client && f.source_boot == server_boot &&
            f.destination_boot == client_boot && f.grant == grant && f.generation == generation;
    }
};
struct EpochRecord { uint16_t node = 0; uint64_t epoch = 0; };
enum class Store { Ok, Missing, Corrupt, ReadError, WriteError, CommitError, Exhausted, AlreadyProvisioned };
struct BootResult { Store status; EpochRecord record{}; };
template<class Storage> BootResult advance_boot(Storage& storage) noexcept {
    EpochRecord record;
    const auto read = storage.load(record);
    if (read != Store::Ok) return {read, {}};
    if (!record.node || !record.epoch) return {Store::Corrupt, {}};
    if (record.epoch == UINT64_MAX) return {Store::Exhausted, {}};
    ++record.epoch;
    const auto written = storage.save_and_commit(record);
    if (written != Store::Ok) return {written, {}};
    return {Store::Ok, record};
}
template<class Storage> Store provision(Storage& storage, uint16_t node) noexcept {
    if (!node) return Store::Corrupt;
    EpochRecord old;
    const auto read = storage.load(old);
    if (read == Store::Ok) return Store::AlreadyProvisioned;
    if (read != Store::Missing) return read;
    return storage.save_and_commit(EpochRecord{node, 1});
}
// Test store models commit failures before or after the write became durable.
struct MemoryStore {
    EpochRecord record{};
    Store read_status = Store::Missing, write_status = Store::Ok;
    bool apply_on_failure = false;
    unsigned saves = 0;
    Store load(EpochRecord& out) noexcept { if (read_status == Store::Ok) out = record; return read_status; }
    Store save_and_commit(EpochRecord value) noexcept {
        ++saves;
        if (write_status == Store::Ok || apply_on_failure) { record = value; read_status = Store::Ok; }
        return write_status;
    }
};
} // namespace srpc
