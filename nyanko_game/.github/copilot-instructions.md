# Copilot Instructions for Nyanko Game

## Project Overview

This is a pygame-based visual novel/dating simulation game featuring the catgirl maid character "にゃんこ" (Nyan-ko). The codebase follows a modular, event-driven architecture with clean separation of concerns and a sophisticated unified choice system that seamlessly integrates dialogue, activities, and scene navigation.

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
├── AudioSystem (BGM/SFX management)
├── ProgressTracker (achievements/progress)
└── DailyEventSystem (day-based events)
```

### Unified Choice System - The Heart of Interaction

**Critical Pattern**: The `UnifiedChoiceSystem` is the central hub for all player interactions:

- **Auto-detects choice types**: `dialogue`, `activity`, `scene_action` via `UnifiedChoice` constructor
- **Contextual enhancement**: `add_contextual_choices()` enriches base dialogue with scene-specific activities and navigation
- **Input delay protection**: Prevents immediate response after choice display (configurable via `input_delay`)
- **Smart filtering**: Checks conditions, time points, and requirements before showing choices

**Integration Points**:

- `DialogueSystem.set_unified_choice_system()` connects dialogue to unified choices
- Scene-specific activities injected via `get_scene_activities(scene_name)`
- Time management actions (skip time, continue chat) automatically added

### Event-Driven Time System

**Key Innovation**: Time advances only through player actions, not automatically:

```python
# Time structure
class GameTime:
    current_day: int = 1
    current_period: TimePeriod = TimePeriod.EARLY_MORNING
    time_points: int = 1  # Actions remaining in period
    week_day: int = 1

# Activity defines time cost
@dataclass
class ActivityChoice:
    time_cost: int  # 1-3 points consumed
    available_periods: List[TimePeriod]
```

### Scene System Pattern

- All scenes inherit from `BaseScene` abstract class in `scenes/base_scene.py`
- Scene lifecycle: `on_enter(transition_data)` → `update(dt, game_state)` → `render(screen)` → `on_exit()`
- **Critical**: Use `self.unified_choice_system = self.game_engine.unified_choice_system` in scene constructors
- Scene-specific `_interact_with_nyanko()` methods trigger dialogue with contextual activities

## Display & Input Handling

### Fullscreen Mouse Coordinate Transformation

**Critical System**: Complex mouse coordinate transformation for fullscreen scaling:

```python
# In GameEngine - always use these methods for mouse handling
def transform_mouse_pos(self, mouse_pos: tuple) -> tuple:
    """Transforms screen coordinates to game coordinates"""

def get_mouse_pos(self) -> tuple:
    """Gets correctly transformed mouse position"""

def is_mouse_in_game_area(self, mouse_pos: tuple) -> bool:
    """Checks if mouse is within game area"""
```

**Event Handling Pattern**: Events are automatically transformed in `handle_events()`:

```python
# GameEngine automatically transforms mouse events before passing to scenes
if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
    transformed_pos = self.transform_mouse_pos(event.pos)
    if transformed_pos is not None:
        transformed_event = pygame.event.Event(
            event.type, {**event.dict, "pos": transformed_pos}
        )
```

### Pixel-Perfect Scaling

- `ImageScaling.pixel_perfect_scale()` maintains crisp graphics across resolutions
- **F2**: Toggle pixel-perfect scaling mode
- Automatic resolution detection and fallback handling

## Development Workflows

### Running & Debugging

```bash
python main.py                              # Standard execution
python scripts/test_pixel_perfect_scaling.py  # Visual scaling test
```

**Debug Keys** (when `DebugSettings.DEBUG_MODE = True`):

- **F1**: Toggle debug info display (FPS, mouse coordinates, scaling status)
- **F2**: Toggle pixel-perfect scaling
- **F11**: Fullscreen toggle
- **Space**: Trigger dialogue with にゃんこ (in game scenes)
- **ESC**: Scene-specific handling or pause

### Character Implementation

Character behavior defined in `nyanko.py` with detailed personality rules:

- Self-reference as "人家" or "にゃんこ"
- Always ends responses with "喵"
- Detailed emotional states and physical descriptions
- Supports romantic/intimate interactions

## Configuration Management

### Settings Structure (`config/settings.py`)

Organized into class-based categories:

- `Colors`: Theme colors and UI palette
- `FontSettings`: Microsoft JhengHei fonts with fallbacks
- `UISettings`: Dialogue boxes, buttons, animations
- `ImageScaling`: Pixel-perfect scaling algorithms
- `DebugSettings`: Debug flags and logging

### Game State Management

Central `game_state` dict passed between systems:

```python
game_state = {
    "nyanko_affection": 0,
    "current_time_period": "morning",
    "current_time": "08:00",
    "current_day": 1,
    "current_weekday": 1,
    "time_points": 2,
    "flags": {},
    "items": {}
}
```

## Common Development Patterns

### Adding New Activities

1. Define in `EventDrivenTimeSystem` activity data
2. Specify `time_cost`, `available_periods`, and effects
3. Activities automatically appear in `UnifiedChoiceSystem` when contextually relevant

### Working with Mouse Events

**Always use scene helper methods**:

```python
# In scene classes - correct pattern
mouse_pos = self.get_mouse_pos()           # Transformed coordinates
is_pressed = self.is_mouse_button_pressed(1)  # Left click
in_area = self.is_mouse_in_game_area()     # Within game bounds

# From events - coordinates already transformed
def handle_event(self, event):
    if event.type == pygame.MOUSEBUTTONDOWN:
        mouse_pos = event.pos  # Already transformed by GameEngine
```

### Scene Navigation

Navigation handled through `UnifiedChoiceSystem`:

```python
# Scene change choice format
{
    "text": "🍳 去廚房看看",
    "target_scene": "kitchen",
    "scene_action": "change_scene",
    "description": "和にゃんこ一起去廚房"
}
```

### Dialogue System Integration

**Critical Pattern**: Dialogue choices automatically enhanced with contextual options:

```python
# Base dialogue choices get enhanced with:
# - Scene-specific activities (cooking, napping, etc.)
# - Navigation options (room changes)
# - Time management (skip time, continue chat)
enhanced_choices = self.unified_choice_system.add_contextual_choices(base_choices)
```

## Performance & Best Practices

### Resource Management

- `systems/image_manager.py` handles all image caching
- Audio manager pools sounds for repeated effects
- Scene resources loaded once and cached
- Debug rendering only active when flags enabled

### System Communication

- Callback-based architecture prevents tight coupling
- `GameEngine` sets system callbacks like `affection_system.on_affection_change`
- Events trigger cascading updates across systems

### File Organization

- **Scenes**: `scenes/` - inherit from `BaseScene`
- **Systems**: `systems/` - modular game logic
- **Configuration**: `config/` - settings and constants
- **Character**: `nyanko.py` - character behavior definitions

## Critical Integration Points

1. **Mouse Handling**: Always use `transform_mouse_pos()` or scene helper methods
2. **Choice System**: Integrate new features through `UnifiedChoiceSystem`, not separate UI
3. **Time Progression**: All meaningful actions should have `time_cost` and advance narrative
4. **Event Priority**: `UnifiedChoiceSystem` → `DialogueSystem` → `SceneManager` (handle events in this order)

**Remember**: This codebase prioritizes unified player interaction. New features should integrate with the existing choice system rather than creating separate interaction flows. The event-driven time system means player agency drives all progression.
