# Copilot Instructions for Nyanko Game

## Project Overview

This is a pygame-based visual novel/dating simulation game featuring the catgirl maid character "にゃんこ" (Nyan-ko). The codebase follows a modular, event-driven architecture with clean separation of concerns.

## Architecture Patterns

### Entry Point & Initialization

- **Main entry**: `main.py` → `app/launcher.py` → `core/game_engine.py`
- Game engine initializes all systems in `_initialize_systems()` method
- Scene management handles transitions between game areas (living room, kitchen, bedroom, etc.)

### Core Systems Architecture

The game uses a plugin-style system architecture where all major components are loosely coupled:

```
GameEngine
├── SceneManager (handles scene transitions)
├── DialogueSystem (manages conversations & choices)
├── AffectionSystem (tracks relationship progress)
├── EventSystem (processes game events)
├── TimeSystem (manages day/night cycles)
└── AudioSystem (BGM/SFX management)
```

### Scene System Pattern

- All scenes inherit from `BaseScene` abstract class
- Scenes registered in `SceneManager._register_scenes()`
- Scene lifecycle: `on_enter()` → `update()` → `render()` → `on_exit()`
- Inter-scene communication via `transition_data` parameter

### Event-Driven Communication

Systems communicate through callbacks rather than direct dependencies:

- `GameEngine` sets callback functions like `affection_system.on_affection_change`
- Events trigger cascading updates (affection change → relationship level → dialogue unlock)
- Progress tracking system monitors all events for achievements

## Configuration Management

### Settings Structure

- `config/settings.py`: Central configuration hub with categorized classes
- `Colors`, `FontSettings`, `UISettings`, `GameSettings`, `ImageScaling`
- Character data in `config/character_data.py`
- Debug flags controlled via `DebugSettings` class

### Display System

Complex fullscreen handling with pixel-perfect scaling:

- `ImageScaling.pixel_perfect_scale()` maintains crisp graphics
- Mouse coordinate transformation for fullscreen mode
- Native resolution detection and scaling fallbacks

## Development Workflows

### Running the Game

```bash
python main.py                    # Standard execution
python scripts/test_pixel_perfect_scaling.py  # Visual scaling test
```

### Debug Features

- F1: Toggle debug info display
- F2: Toggle pixel-perfect scaling
- F11: Fullscreen toggle
- `DebugSettings.DEBUG_MODE = True` enables verbose logging

### Asset Management

- `systems/image_manager.py` handles all image loading/caching
- `systems/audio_system.py` manages BGM/SFX with volume control
- Assets organized in `assets/{images,sounds,fonts}/` hierarchy

## Code Conventions

### File Organization

- **Scenes**: `scenes/` - inherit from `BaseScene`, implement required methods
- **Systems**: `systems/` - modular game logic (dialogue, affection, events)
- **Configuration**: `config/` - settings, character data, constants
- **Utilities**: `utils/` - helper functions (file, math, string operations)

### Naming Patterns

- Classes: PascalCase (`DialogueSystem`, `BaseScene`)
- Files: snake_case (`dialogue_system.py`, `base_scene.py`)
- Constants: UPPER_SNAKE_CASE in settings classes
- Game state keys: lowercase with underscores (`nyanko_affection`, `current_time_period`)

### Character Implementation

- Character behavior defined in `nyanko.py` with detailed personality rules
- Dialogue system supports conditional branches based on affection/flags
- Text rendering with typewriter effect and emotion states

## Data Flow Patterns

### Game State Management

Central `game_state` dict passed between systems:

```python
game_state = {
    "nyanko_affection": 0,
    "current_time_period": "morning",
    "flags": {},
    "current_scene": "living_room"
}
```

### Save System

- JSON-based saves in `data/` directory
- Each system provides `save_data()`/`load_data()` methods
- Auto-save triggers on major state changes

### Dialogue System

- JSON dialogue data with conditional branching
- Choice effects modify game state immediately
- Progress tracking for all dialogue interactions

## Common Patterns

### Adding New Scenes

1. Create class inheriting `BaseScene` in `scenes/`
2. Implement `load_resources()`, `setup_ui()`, `update()`, `render()`
3. Register in `SceneManager._register_scenes()`

### Adding Game Events

1. Define event data structure in relevant system
2. Add condition checking logic
3. Implement effect callbacks that modify game state
4. Connect to progress tracking if needed

### Debugging Tips

- Enable `DebugSettings.DEBUG_MODE` for verbose output
- Use scene debug info (F1) to monitor state changes
- Check `logs/` directory for error tracking
- Mouse coordinate transformation issues common in fullscreen mode

## Performance Considerations

- Image scaling uses pygame's optimized transform functions
- Audio manager pools sound objects for repeated effects
- Scene resources loaded once and cached
- Debug rendering only active when flags enabled

Remember: This codebase prioritizes modularity and clean separation between game logic, presentation, and data management. When adding features, follow the established patterns of event-driven communication and system-specific responsibilities.
