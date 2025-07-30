# Copilot Instructions for Tetris Game

## Project Overview

A professional Tetris implementation using Pygame with modern Tetris features including SRS rotation system, T-spin detection, and advanced scoring mechanics. Built with a clean modular architecture.

## Architecture & Module Structure

### Core Components

- **`core/game.py`**: Central game controller managing state, input, and game logic
- **`game_objects/`**: Game entities (`Tetromino` pieces, `GameGrid` playing field)
- **`ui/renderer.py`**: Separation of concerns - all visual rendering isolated here
- **`config/`**: Centralized constants and shape definitions

### Key Design Patterns

- **Module isolation**: Each module has clear responsibilities with `__init__.py` exports
- **State management**: Game state centralized in `Game` class with explicit state transitions
- **Event-driven input**: Separate handling for `keys_pressed` (continuous) vs `keys_just_pressed` (single events)

## Critical Game Systems

### SRS Rotation & Wall Kicks

- Tetromino rotation uses **SRS (Super Rotation System)** standard
- Wall kick data in `config/shapes.py` - different kick sequences for I-pieces vs JLSTZ pieces
- Wall kicks tested in sequence until valid position found

### Advanced Input Systems

- **DAS (Delayed Auto Shift)**: Handles key repeat for smooth movement - see `handle_horizontal_movement()`
- **Lock Delay**: Prevents immediate piece locking when touching ground - allows for last-second moves
- Input processing pattern: `keys_just_pressed` for single actions, `keys_pressed` for continuous movement

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

### Key Constants to Modify

- Game speed: `FALL_SPEED` in `constants.py`
- Input responsiveness: `DAS_DELAY`, `ARR_RATE` for movement feel
- Lock delay timing: `LOCK_DELAY_MAX`, `MAX_LOCK_RESETS`

### Adding New Features

1. **New game mechanics**: Extend `Game` class in `core/game.py`
2. **Visual elements**: Add to `UIRenderer` in `ui/renderer.py`
3. **Game objects**: Create new classes in `game_objects/` following `Tetromino`/`GameGrid` pattern
4. **Configuration**: Add constants to `config/constants.py`

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
