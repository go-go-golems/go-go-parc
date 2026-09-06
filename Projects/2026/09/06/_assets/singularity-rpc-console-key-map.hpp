#pragma once
#include <array>
#include <cstdint>

namespace srpc::ui {
// Physical ADV layout after the TCA8418 electrical 7x8 -> physical 4x14 remap.
// Modifiers have no action character: this console uses single-key commands.
struct KeyEvent {
    char key = 0;
    uint8_t position = 0;
    bool pressed = false;
};
inline bool decode_key(uint8_t raw, KeyEvent& output) noexcept {
    const unsigned number = raw & 0x7f;
    if (!number) return false;
    const unsigned row = (number - 1) / 10, column = (number - 1) % 10;
    if (row >= 7 || column >= 8) return false;
    constexpr char map[4][14] = {
        {'`','1','2','3','4','5','6','7','8','9','0','-','=','\b'},
        {'\t','q','w','e','r','t','y','u','i','o','p','[',']','\\'},
        {0,0,'a','s','d','f','g','h','j','k','l',';','\'','\n'},
        {0,0,0,'z','x','c','v','b','n','m',',','.','/',' '}
    };
    const unsigned physical_row = column % 4;
    const unsigned physical_column = row * 2 + unsigned(column >= 4);
    output = {map[physical_row][physical_column], uint8_t(physical_row * 14 + physical_column), bool(raw & 0x80)};
    return true;
}
class KeyEdges {
    std::array<bool, 56> held_{};
public:
    void clear() noexcept { held_.fill(false); }
    // Every valid transition is observable; duplicate presses/releases are ignored.
    bool accept(uint8_t raw, KeyEvent& output) noexcept {
        KeyEvent event;
        if (!decode_key(raw, event) || held_[event.position] == event.pressed) return false;
        held_[event.position] = event.pressed;
        output = event;
        return true;
    }
};
} // namespace srpc::ui
