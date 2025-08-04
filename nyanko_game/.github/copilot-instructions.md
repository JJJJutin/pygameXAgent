# Copilot Instructions for Nyanko Game

## Project Overview

This is a pygame-based visual novel/dating simulation game featuring the catgirl maid character "にゃんこ" (Nyan-ko). The codebase follows a modular, event-driven architecture with clean separation of concerns and a sophisticated unified choice system.

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
├── UnifiedChoiceSystem (integrates dialogue + activities + scene actions)
├── DialogueSystem (manages conversations)
├── EventDrivenTimeSystem (player-triggered time progression)
├── AffectionSystem (tracks relationship progress)
├── EventSystem (processes game events)
└── AudioSystem (BGM/SFX management)
```

### Scene System Pattern

- All scenes inherit from `BaseScene` abstract class in `scenes/base_scene.py`
- Scenes registered in `SceneManager._register_scenes()` method
- Scene lifecycle: `on_enter(transition_data)` → `update(dt, game_state)` → `render(screen)` → `on_exit()`
- Inter-scene communication via `transition_data` parameter
- Each scene implements required methods: `load_resources()`, `setup_ui()`, `update()`, `render()`, `handle_event()`

### Unified Choice System Architecture

**Critical Pattern**: The `UnifiedChoiceSystem` is the heart of player interaction, merging:

- **Dialogue responses** (from `DialogueNode.choices`)
- **Activity selections** (from `EventDrivenTimeSystem`)
- **Scene navigation** (inter-scene transitions)
- **Time management** (skip periods, continue chat)

**Integration Points**:

- `DialogueSystem.set_unified_choice_system()` connects dialogue to unified choices
- `UnifiedChoice.add_contextual_choices()` enriches base dialogue with scene-specific activities
- Choice types auto-detected: `dialogue`, `activity`, `scene_action`

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
- Mouse coordinate transformation for fullscreen mode (`GameEngine.transform_mouse_pos()`)
- Native resolution detection and scaling fallbacks
- **Critical**: Mouse events require coordinate transformation in fullscreen mode

### Time System Architecture

**Two-Layer Time Design**:

1. **BasicTimeSystem** - Traditional auto-advancing time
2. **EventDrivenTimeSystem** - Player-action-triggered progression

**Key Pattern**: Time advances only through player choices:

- `ActivityChoice.time_cost` determines advancement
- `TimePeriod` enum defines day segments
- `GameTime.time_points` tracks remaining actions per period

## Development Workflows

### Running the Game

```bash
python main.py                    # Standard execution
python scripts/test_pixel_perfect_scaling.py  # Visual scaling test
```

### Debug Features

- **F1**: Toggle debug info display
- **F2**: Toggle pixel-perfect scaling
- **F11**: Fullscreen toggle
- **Space**: Trigger dialogue with にゃんこ (in game scenes)
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

### Dialogue System Integration

**Critical Pattern**: Dialogue choices get enhanced with contextual options:

```python
# In UnifiedChoiceSystem.add_contextual_choices()
enhanced_choices = base_dialogue_choices.copy()
# Add scene-specific activities
# Add navigation options
# Add time management actions
```

## Common Patterns

### Adding New Scenes

1. Create class inheriting `BaseScene` in `scenes/`
2. Implement `load_resources()`, `setup_ui()`, `update()`, `render()`
3. Register in `SceneManager._register_scenes()`
4. **Important**: Use `self.unified_choice_system = self.game_engine.unified_choice_system`

### Adding Game Events

1. Define event data structure in relevant system
2. Add condition checking logic
3. Implement effect callbacks that modify game state
4. Connect to progress tracking if needed

### Working with Unified Choices

**Key Pattern**: Activities and dialogue share the same choice infrastructure:

```python
# Activity choice format
{
    "text": "🥘 一起做料理",
    "activity_id": "cooking_together",
    "time_cost": 2,
    "affection_change": 5
}

# Dialogue choice format
{
    "text": "我很喜歡和你一起度過時光",
    "next_dialogue": "response_happy_01",
    "affection_change": 3
}
```

### Debugging Tips

- Enable `DebugSettings.DEBUG_MODE` for verbose output
- Use scene debug info (F1) to monitor state changes
- Check `logs/` directory for error tracking
- **Mouse coordinate transformation issues common in fullscreen mode**
- Use `game_engine.transform_mouse_pos()` for accurate click detection

## Performance Considerations

- Image scaling uses pygame's optimized transform functions
- Audio manager pools sound objects for repeated effects
- Scene resources loaded once and cached
- Debug rendering only active when flags enabled
- **Choice system caches available activities per time period**

## Critical Integration Points

1. **Scene → UnifiedChoiceSystem**: `_interact_with_nyanko()` triggers dialogue which auto-enhances with activities
2. **EventDrivenTimeSystem → Activities**: `get_available_activities()` filters by time period and requirements
3. **Mouse Events → Fullscreen**: Always use `transform_mouse_pos()` before processing clicks
4. **Character Data**: Loaded from `nyanko.py` with detailed personality and dialogue rules

Remember: This codebase prioritizes unified player interaction through the choice system. When adding features, integrate with `UnifiedChoiceSystem` rather than creating separate UI flows. The event-driven time progression means all meaningful actions should cost time points and advance the narrative.
