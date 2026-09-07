#pragma once
#include "sl/platform.hpp"
#include <array>
#include <cstddef>
#include <cstdint>
#include <limits>
#include <utility>

namespace sl {
class Pool;
class OwnedBuffer;
class AllocationIdentity {
    friend class OwnedBuffer;
    uint64_t domain_ = 0, sequence_ = 0;
    AllocationIdentity(uint64_t domain, uint64_t sequence) noexcept : domain_(domain), sequence_(sequence) {}
public:
    AllocationIdentity() noexcept = default;
    bool operator==(const AllocationIdentity& other) const noexcept {
        return domain_ == other.domain_ && sequence_ == other.sequence_;
    }
    bool operator!=(const AllocationIdentity& other) const noexcept { return !(*this == other); }
};
class OwnedBuffer {
    friend class Pool;
    Pool* pool_ = nullptr;
    size_t slot_ = 0;
    uint64_t generation_ = 0, id_ = 0;
    OwnedBuffer(Pool* p, size_t slot, uint64_t generation, uint64_t id) noexcept
        : pool_(p), slot_(slot), generation_(generation), id_(id) {}
    void steal(OwnedBuffer& source) noexcept {
        pool_ = source.pool_; slot_ = source.slot_;
        generation_ = source.generation_; id_ = source.id_;
        source.pool_ = nullptr; source.id_ = source.generation_ = 0;
    }
public:
    OwnedBuffer() noexcept = default;
    OwnedBuffer(const OwnedBuffer&) = delete;
    OwnedBuffer& operator=(const OwnedBuffer&) = delete;
    OwnedBuffer(OwnedBuffer&& source) noexcept { steal(source); }
    OwnedBuffer& operator=(OwnedBuffer&& source) noexcept {
        if (this != &source) { reset(); steal(source); }
        return *this;
    }
    ~OwnedBuffer() noexcept { reset(); }
    bool valid() const noexcept;
    uint64_t allocation_id() const noexcept { return id_; }
    AllocationIdentity identity() const noexcept;
    size_t size() const noexcept;
    bool read(size_t index, uint8_t& out) const noexcept;
    bool write(size_t index, uint8_t value) noexcept;
    void reset() noexcept;
};
enum class Alloc { Ok, Oversize, Exhausted, IdExhausted, OutputNotEmpty };
struct PoolStats {
    uint64_t allocations = 0, releases = 0;
    size_t live_general = 0, live_control = 0, high_water = 0;
};
class Pool {
    friend class OwnedBuffer;
    struct Slot {
        std::array<uint8_t, 128> bytes{};
        size_t length = 0;
        uint64_t generation = 0, id = 0;
        bool live = false;
    };
    mutable Mutex mutex_;
    std::array<Slot, 16> slots_{};
    uint64_t next_id_ = 0;
    static uint64_t fresh_domain() noexcept {
        static Mutex mutex; static uint64_t counter = 0;
        Lock lock(mutex); require(counter != UINT64_MAX); return ++counter;
    }
    const uint64_t domain_ = fresh_domain();
    PoolStats stats_{};
    bool matches(const OwnedBuffer& owner) const noexcept {
        if (owner.pool_ != this || owner.slot_ >= slots_.size()) return false;
        const auto& s = slots_[owner.slot_];
        return s.live && s.id == owner.id_ && s.generation == owner.generation_;
    }
    Alloc allocate_range(size_t length, OwnedBuffer& out, size_t begin, size_t end) noexcept {
        if (out.pool_ != nullptr) return Alloc::OutputNotEmpty;
        if (length > 128) return Alloc::Oversize;
        Lock lock(mutex_);
        if (next_id_ == std::numeric_limits<uint64_t>::max()) return Alloc::IdExhausted;
        for (size_t i = begin; i < end; ++i) {
            auto& s = slots_[i];
            if (s.live) continue;
            if (s.generation == std::numeric_limits<uint64_t>::max()) return Alloc::IdExhausted;
            ++s.generation; s.id = ++next_id_; s.length = length;
            s.bytes.fill(0); s.live = true;
            // out was checked empty: move assignment cannot release under lock.
            out = OwnedBuffer(this, i, s.generation, s.id);
            ++stats_.allocations;
            if (i < 12) ++stats_.live_general; else ++stats_.live_control;
            const size_t live = stats_.live_general + stats_.live_control;
            if (live > stats_.high_water) stats_.high_water = live;
            return Alloc::Ok;
        }
        return Alloc::Exhausted;
    }
public:
    // Applications receive GeneralAllocator, not Pool. Supervisor keeps Pool.
    class GeneralAllocator {
        Pool& pool_;
        friend class Pool;
        explicit GeneralAllocator(Pool& p) : pool_(p) {}
    public:
        Alloc allocate(size_t size, OwnedBuffer& out) noexcept {
            return pool_.allocate_range(size, out, 0, 12);
        }
    };
    Pool() = default;
    Pool(const Pool&) = delete;
    Pool& operator=(const Pool&) = delete;
    ~Pool() { const auto s = stats(); require(s.live_general == 0 && s.live_control == 0); }
    GeneralAllocator general() noexcept { return GeneralAllocator(*this); }
    Alloc allocate_control(size_t size, OwnedBuffer& out) noexcept {
        return allocate_range(size, out, 12, 16);
    }
    PoolStats stats() const noexcept { Lock lock(mutex_); return stats_; }
};
inline AllocationIdentity OwnedBuffer::identity() const noexcept {
    return pool_ ? AllocationIdentity(pool_->domain_, id_) : AllocationIdentity{};
}
inline bool OwnedBuffer::valid() const noexcept {
    if (!pool_) return false;
    Lock lock(pool_->mutex_); return pool_->matches(*this);
}
inline size_t OwnedBuffer::size() const noexcept {
    if (!pool_) return 0;
    Lock lock(pool_->mutex_);
    return pool_->matches(*this) ? pool_->slots_[slot_].length : 0;
}
inline bool OwnedBuffer::read(size_t index, uint8_t& out) const noexcept {
    if (!pool_) return false;
    Lock lock(pool_->mutex_);
    if (index >= 128 || !pool_->matches(*this) || index >= pool_->slots_[slot_].length) return false;
    out = pool_->slots_[slot_].bytes[index]; return true;
}
inline bool OwnedBuffer::write(size_t index, uint8_t value) noexcept {
    if (!pool_) return false;
    Lock lock(pool_->mutex_);
    if (index >= 128 || !pool_->matches(*this) || index >= pool_->slots_[slot_].length) return false;
    pool_->slots_[slot_].bytes[index] = value; return true;
}
inline void OwnedBuffer::reset() noexcept {
    if (!pool_) return;
    Pool* p = pool_;
    Lock lock(p->mutex_);
    require(p->matches(*this));
    p->slots_[slot_].live = false;
    ++p->stats_.releases;
    if (slot_ < 12) --p->stats_.live_general; else --p->stats_.live_control;
    pool_ = nullptr; id_ = generation_ = 0;
}
} // namespace sl
