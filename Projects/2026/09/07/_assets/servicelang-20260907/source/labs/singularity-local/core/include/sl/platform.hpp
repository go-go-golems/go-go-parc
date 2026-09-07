#pragma once
#include <cstdint>
#include <cstdlib>
#ifdef ESP_PLATFORM
#include "freertos/FreeRTOS.h"
#include "freertos/semphr.h"
#include "esp_timer.h"
#else
#include <chrono>
#include <condition_variable>
#include <mutex>
#endif

namespace sl {
// Invariant failures remain fatal with NDEBUG; do not silently corrupt owners.
inline void require(bool ok) noexcept { if (!ok) std::abort(); }
class Mutex {
#ifdef ESP_PLATFORM
    StaticSemaphore_t storage_{};
    SemaphoreHandle_t handle_ = xSemaphoreCreateMutexStatic(&storage_);
#else
    std::mutex mutex_;
#endif
public:
    Mutex() noexcept {
#ifdef ESP_PLATFORM
        require(handle_ != nullptr);
#endif
    }
    Mutex(const Mutex&) = delete;
    Mutex& operator=(const Mutex&) = delete;
    ~Mutex() {
#ifdef ESP_PLATFORM
        vSemaphoreDelete(handle_);
#endif
    }
    void lock() noexcept {
#ifdef ESP_PLATFORM
        require(xSemaphoreTake(handle_, portMAX_DELAY) == pdTRUE);
#else
        mutex_.lock();
#endif
    }
    void unlock() noexcept {
#ifdef ESP_PLATFORM
        require(xSemaphoreGive(handle_) == pdTRUE);
#else
        mutex_.unlock();
#endif
    }
};
class Lock {
    Mutex& mutex_;
public:
    explicit Lock(Mutex& m) noexcept : mutex_(m) { mutex_.lock(); }
    ~Lock() { mutex_.unlock(); }
    Lock(const Lock&) = delete;
    Lock& operator=(const Lock&) = delete;
};
inline int64_t now_us() noexcept {
#ifdef ESP_PLATFORM
    return esp_timer_get_time();
#else
    return std::chrono::duration_cast<std::chrono::microseconds>(
        std::chrono::steady_clock::now().time_since_epoch()).count();
#endif
}
// Retained binary wake, not a message counter. Stable storage outlives callers.
// IDF uses a static semaphore rather than a task handle: supports startup before
// receiver creation and eliminates post-unlock notifications to deleted tasks.
class WakeEvent {
#ifdef ESP_PLATFORM
    StaticSemaphore_t storage_{};
    SemaphoreHandle_t handle_ = xSemaphoreCreateBinaryStatic(&storage_);
#else
    std::mutex mutex_;
    std::condition_variable cv_;
    bool pending_ = false;
#endif
public:
    WakeEvent() noexcept {
#ifdef ESP_PLATFORM
        require(handle_ != nullptr);
#endif
    }
    WakeEvent(const WakeEvent&) = delete;
    WakeEvent& operator=(const WakeEvent&) = delete;
    ~WakeEvent() {
#ifdef ESP_PLATFORM
        vSemaphoreDelete(handle_);
#endif
    }
    void signal() noexcept {
#ifdef ESP_PLATFORM
        (void)xSemaphoreGive(handle_); // Already-full binary event coalesces.
#else
        { std::lock_guard<std::mutex> lock(mutex_); pending_ = true; }
        cv_.notify_one();
#endif
    }
    void wait_until(int64_t deadline) noexcept {
#ifdef ESP_PLATFORM
        const int64_t remaining = deadline - now_us();
        if (remaining <= 0) return;
        const int64_t tick_us = 1000000 / configTICK_RATE_HZ;
        const int64_t rounded = (remaining + tick_us - 1) / tick_us;
        const TickType_t ticks = static_cast<TickType_t>(
            rounded > 1000 ? 1000 : rounded); // Always bounded.
        (void)xSemaphoreTake(handle_, ticks);
#else
        std::unique_lock<std::mutex> lock(mutex_);
        const auto until = std::chrono::steady_clock::time_point(
            std::chrono::microseconds(deadline));
        cv_.wait_until(lock, until, [this] { return pending_; });
        pending_ = false;
#endif
    }
};
} // namespace sl
