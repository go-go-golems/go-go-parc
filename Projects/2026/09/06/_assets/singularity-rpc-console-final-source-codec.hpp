#pragma once
#include <array>
#include <cstddef>
#include <cstdint>
#include <algorithm>

namespace srpc {
using Time = uint64_t;
enum class Kind : uint8_t { Request = 1, Reply = 2 };
enum class Service : uint8_t { Sensor = 1, Led = 2, Health = 3, LedRead = 4 };
enum class ReplyCode : uint8_t { Ok, BadRequest, Denied, Revoked, Expired, Busy, Stale, Conflict, Internal };
enum class Codec { Ok, Length, Header, Identity, Body, UnsupportedVersion };
struct Packet { std::array<uint8_t, 128> bytes{}; size_t size = 0; };
struct Frame {
    Kind kind = Kind::Request;
    uint8_t flags = 0;
    Service service = Service::Sensor;
    uint8_t opcode = 1;
    ReplyCode status = ReplyCode::Ok;
    uint16_t source = 0, destination = 0;
    uint64_t source_boot = 0, destination_boot = 0;
    uint32_t request = 0, grant = 0, generation = 0;
    uint16_t length = 0;
    std::array<uint8_t, 64> body{};
    std::array<uint8_t, 16> tag{};
};
inline void put(uint8_t* bytes, size_t offset, uint64_t value, size_t width) noexcept {
    for (size_t i = 0; i < width; ++i) bytes[offset + i] = uint8_t(value >> (8 * i));
}
inline uint64_t get(const uint8_t* bytes, size_t offset, size_t width) noexcept {
    uint64_t result = 0;
    for (size_t i = 0; i < width; ++i) result |= uint64_t(bytes[offset + i]) << (8 * i);
    return result;
}
inline int32_t signed32(uint32_t value) noexcept {
    return value <= INT32_MAX ? int32_t(value) : -1 - int32_t(UINT32_MAX - value);
}
inline Codec valid(const Frame& f) noexcept {
    const auto service = uint8_t(f.service), status = uint8_t(f.status);
    if ((f.kind != Kind::Request && f.kind != Kind::Reply) || f.flags > 1 || status > 8)
        return Codec::Header;
    if (!f.source || !f.destination || !f.source_boot || !f.destination_boot ||
        !f.request || !f.grant || !f.generation) return Codec::Identity;
    if (f.length > 64 || service < 1 || service > 4 || f.opcode != service) return Codec::Body;
    if (f.kind == Kind::Request) {
        if (f.status != ReplyCode::Ok) return Codec::Body;
        if (f.service == Service::Led) return f.length == 1 && f.body[0] <= 1 ? Codec::Ok : Codec::Body;
        return f.length == 0 ? Codec::Ok : Codec::Body;
    }
    if (f.status != ReplyCode::Ok) return f.length == 0 ? Codec::Ok : Codec::Body;
    const bool led = f.service == Service::Led || f.service == Service::LedRead;
    const size_t expected = f.service == Service::Sensor ? 8 : led ? 1 : 12;
    if (f.length != expected || (led && f.body[0] > 1)) return Codec::Body;
    return Codec::Ok;
}
inline Codec encode(const Frame& f, Packet& output) noexcept {
    const auto check = valid(f); if (check != Codec::Ok) return check;
    Packet p;
    auto* b = p.bytes.data();
    b[0] = 'R'; b[1] = 'S'; b[2] = 1; b[3] = uint8_t(f.kind); b[4] = f.flags;
    b[5] = uint8_t(f.service); b[6] = f.opcode; b[7] = uint8_t(f.status);
    put(b, 8, f.source, 2); put(b, 10, f.destination, 2);
    put(b, 12, f.source_boot, 8); put(b, 20, f.destination_boot, 8);
    put(b, 28, f.request, 4); put(b, 32, f.grant, 4); put(b, 36, f.generation, 4);
    put(b, 40, f.length, 2);
    std::copy_n(f.body.begin(), f.length, p.bytes.begin() + 44);
    p.size = 44 + f.length;
    if (f.flags == 1) { std::copy(f.tag.begin(), f.tag.end(), p.bytes.begin() + p.size); p.size += 16; }
    output = p; return Codec::Ok;
}
inline Codec decode(const uint8_t* b, size_t size, Frame& output) noexcept {
    if (!b || size < 44 || size > 128) return Codec::Length;
    if (b[0] != 'R' || b[1] != 'S' || b[42] != 0 || b[43] != 0 || b[4] > 1) return Codec::Header;
    if (b[2] != 1) return Codec::UnsupportedVersion;
    const size_t length = get(b, 40, 2);
    if (length > 64 || size != 44 + length + (b[4] ? 16 : 0)) return Codec::Length;
    Frame f;
    f.kind = Kind(b[3]); f.flags = b[4]; f.service = Service(b[5]); f.opcode = b[6]; f.status = ReplyCode(b[7]);
    f.source = uint16_t(get(b, 8, 2)); f.destination = uint16_t(get(b, 10, 2));
    f.source_boot = get(b, 12, 8); f.destination_boot = get(b, 20, 8);
    f.request = uint32_t(get(b, 28, 4)); f.grant = uint32_t(get(b, 32, 4)); f.generation = uint32_t(get(b, 36, 4));
    f.length = uint16_t(length); std::copy_n(b + 44, length, f.body.begin());
    if (f.flags) std::copy_n(b + 44 + length, 16, f.tag.begin());
    const auto check = valid(f); if (check != Codec::Ok) return check;
    output = f; return Codec::Ok;
}
inline Codec decode(const Packet& p, Frame& out) noexcept { return decode(p.bytes.data(), p.size, out); }
inline bool same(const Packet& a, const Packet& b) noexcept {
    return a.size <= 128 && a.size == b.size && std::equal(a.bytes.begin(), a.bytes.begin() + a.size, b.bytes.begin());
}
inline Frame reply_for(const Frame& request, ReplyCode code) noexcept {
    Frame f = request;
    f.kind = Kind::Reply; std::swap(f.source, f.destination); std::swap(f.source_boot, f.destination_boot);
    f.status = code; f.length = 0; f.body.fill(0); f.tag.fill(0);
    return f;
}
} // namespace srpc
