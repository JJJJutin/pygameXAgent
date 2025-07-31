# Copilot Instructions for Tetris Game

## Project Overview

A professional Tetris implementation using Pygame with modern Tetris features including SRS rotation system, T-spin detection, and advanced scoring mechanics. Features a unique **WindowKill-style multi-window system** with independent desktop windows for different game components. Built with clean modular architecture and comprehensive game mechanics.

## Architecture & Module Structure

### Core Components

- **`core/game.py`**: Central game controller managing state, input, and game logic
- **`game_objects/`**: Game entities (`Tetromino` pieces, `GameGrid` playing field)
- **`ui/windowkill_manager.py`**: Multi-window system using Tkinter + Pygame hybrid approach
- **`ui/renderer.py`**: Traditional single-window rendering (legacy)
- **`config/`**: Centralized constants and shape definitions

### Key Design Patterns

- **Module isolation**: Each module has clear responsibilities with `__init__.py` exports
- **Hybrid UI system**: Pygame main window + Tkinter satellite windows for WindowKill effect
- **State management**: Game state centralized in `Game` class with explicit state transitions
- **Event-driven input**: Separate handling for `keys_pressed` (continuous) vs `keys_just_pressed` (single events)
- **Visual feedback**: Shake effects and animations triggered by game events

## Critical Game Systems

### WindowKill Multi-Window System

- **Architecture**: Hybrid Pygame (main game) + Tkinter (satellite windows) approach
- **Windows**: Main game, Hold, Next, Info, Controls, and Game Over windows
- **Implementation**: `WindowKillManager` class handles all window lifecycle and positioning
- **Key features**: Independent window movement, shake effects, automatic show/hide logic
- **Threading**: Window updates run on separate threads for smooth performance

### SRS Rotation & Wall Kicks

- Tetromino rotation uses **SRS (Super Rotation System)** standard
- Wall kick data in `config/shapes.py` - different kick sequences for I-pieces vs JLSTZ pieces
- Wall kicks tested in sequence until valid position found

### Advanced Input Systems

- **DAS (Delayed Auto Shift)**: Handles key repeat for smooth movement - see `handle_horizontal_movement()`
- **Lock Delay**: Prevents immediate piece locking when touching ground - allows for last-second moves
- Input processing pattern: `keys_just_pressed` for single actions, `keys_pressed` for continuous movement

### Visual Feedback System

- **Shake effects**: Triggered by line clears, T-spins, Perfect Clears with varying intensity
- **Animation management**: `update_shake()` and `update_window_animations()` in WindowKillManager
- **Event-based**: Game events automatically trigger appropriate visual feedback

### T-Spin Detection

- Uses 3-corner rule: checks 4 diagonal corners around T-piece center
- Distinguishes between full T-spin vs Mini T-spin based on "front corners" (pointing direction)
- Critical: `last_move_was_rotation` flag must be true for T-spin to register

### Advanced Scoring Features

- **7-bag randomizer**: Ensures fair piece distribution - refills bag when empty
- **Combo system**: Tracks consecutive line clears
- **Back-to-back**: 50% bonus for consecutive difficult moves (Tetris/T-spin)
- **Perfect Clear**: Detects when board is completely empty after line clear

## Development Workflows

### Running the Game

```bash
pip install pygame
python main.py
```

### Multi-Window Development

- **Main architecture**: `main.py` creates `WindowKillManager` instead of traditional single window
- **Window lifecycle**: Windows auto-show based on game state, Game Over window triggers restart callback
- **Testing windows**: Each window can be tested independently via manager methods
- **Shake system**: Use `trigger_shake(intensity, duration)` for visual feedback integration

### Key Constants to Modify

- Game speed: `FALL_SPEED` in `constants.py`
- Input responsiveness: `DAS_DELAY`, `ARR_RATE` for movement feel
- Lock delay timing: `LOCK_DELAY_MAX`, `MAX_LOCK_RESETS`

### Adding New Features

1. **New game mechanics**: Extend `Game` class in `core/game.py`
2. **Visual elements**: Add to `WindowKillManager` for multi-window or `UIRenderer` for single-window
3. **Game objects**: Create new classes in `game_objects/` following `Tetromino`/`GameGrid` pattern
4. **Configuration**: Add constants to `config/constants.py`
5. **New windows**: Extend `WindowKillManager` with new Tkinter window methods

## Code Conventions

### State Management

- Use explicit boolean flags for state tracking (e.g., `last_move_was_rotation`, `can_hold`)
- Reset state flags after significant events (piece locking, game restart)
- Centralize timers in Game class (e.g., `fall_timer`, `lock_delay_timer`)

### Coordinate System

- Game grid uses logical coordinates (0-9 width, 0-19 height)
- Screen rendering converts to pixel coordinates using `CELL_SIZE`
- Tetromino position is top-left of 4x4 bounding box

### Error Handling

- Bounds checking in `is_valid_position()` methods
- Graceful degradation when wall kicks fail
- Game over detection when new piece can't spawn

## Testing & Debugging

- Debug T-spin detection: Check console output for corner analysis
- Visual debugging: Lock delay progress bar in UI
- State inspection: Action text displays show scoring events

## Integration Notes

- Pygame event loop in `main.py` - separate `KEYDOWN` events from continuous key states
- 60 FPS game loop with delta time for consistent timing
- All game logic updates before rendering in main loop
- Multi-window threading: Tkinter windows run on separate threads for responsiveness
- Cleanup handling: `atexit.register()` ensures proper window cleanup on exit
