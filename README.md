# Project Ark & The Noah Kernel

Welcome to **Energy Battle - Remake**, a sophisticated turn-based strategy game in your terminal! This project showcases a powerful dual-architecture design:

*   **Ark (`ark.py`)**: The frontend delivering "Energy Battle" — complete game logic, player experience, and rich configuration systems.
*   **Noah (`noah.py`)**: A decoupled, reusable turn-based game kernel. The engine that powers it all.

This document explores both components, with special focus on the **Noah Kernel's** elegant architecture.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.6%2B-blue.svg)](https://www.python.org/)
![Status](https://img.shields.io/badge/status-in_development-orange)

---

## ✨ Features

### Core Gameplay
*   **Classic Turn-Based Combat**: Tactical battles with multiple AI opponents
*   **Resource Management**: Strategic energy allocation for powerful actions
*   **Positional Strategy**: Multi-layer battlefield with vertical movement
*   **Diverse Actions**: Shoot, Defend, Move, Energy Wave, Reflect, Black Hole and more

### Advanced Systems
*   **Tweak System**: Pre-battle fine-tuning of player stats, positions, and AI behavior
*   **Quality AI**: Two-tier AI system with basic and strategic decision-making
*   **Event Architecture**: Deferred command execution for complex game mechanics
*   **Zero Dependencies**: Pure Python — runs anywhere

---

## 🚀 The Noah Kernel: Architectural Deep Dive

Noah embodies a core principle: **complete separation of game engine from game logic**. The kernel knows *how* to run turn-based games, but has zero knowledge about *what* your game does. It manages "Actions" with priorities and costs, not "attacks" or "spells".

This makes Noah incredibly portable across different game projects.

### Key Components

#### Core Classes

1.  **`Core`**: The orchestrator. Manages game state (`BattleEnv`), all players (`PlDict`), and coordinates the turn cycle. Now includes:
    - `CmdTable`: Registry for kernel commands and pipelines
    - `EventBus`: Queue for deferred execution
    - `Exec()`: Universal command dispatcher

2.  **`Player`**: Any game participant. Tracks HP, energy, position, chosen actions, and team affiliation. Supports both human and AI control with configurable `ai_quality` levels.

3.  **`Act`**: Data container for a player's chosen action. Lightweight, serializable representation of intent.

4.  **`Event`**: **New!** Deferred kernel commands that can be queued and executed later, perfect for pre-battle tweaks or timed effects.

5.  **`IO`**: Versatile I/O handler with template system, color support, typewriter effects, and compressed logging.

### 🔄 Turn Lifecycle

Each turn flows through three precise phases:

#### 1. Selection Phase (`SelectAct`)
- Builds context for each player (nearby enemies, energy ratios, etc.)
- Generates available actions and AI weights via `build_able()`
- Prompts humans or uses weighted random for AI
- Registers choices in `ActSign` registry by priority

#### 2. Resolution Phase (`DealAct`)
- Processes actions in strict **priority order** (high → low)
- Each action feeds into its **PipeWorkFlow** (see below)
- Multiple pipeline channels can run in parallel
- Preliminary death detection

#### 3. Cleanup Phase
- Removes eliminated players (`rm_deaths`)
- Announces casualties
- Resets turn-based states
- Clears temporary data (`clean_round`)

### 🤖 Data-Driven Design: The `ActDict`

Noah stays game-agnostic through the **Action Dictionary**. When Ark initializes the `Core`, it passes this master definition of all possible actions:

```python

"2": {  # "Shoot" action
    "price": shot_price,        # Function: calculate energy cost
    "priority": -1,             # Execution order (negative = resolve attacks later)
    "able": shot_able,          # Function: check if usable
    "human_only": False,        # Available to AI?
    "ai": [shot_ai, advanced_shot_ai],  # AI weight functions (basic, advanced)
    "weight": 1,                # Base weight multiplier
    "s_exec": shot_s,           # Selection phase logic
    "d_exec": [                 # Resolution pipeline (see below)
        crossfire_evaluate,
        crossfire_crash,
        crossfire_reflect,
        crossfire_defend,
        crossfire_final
    ],
}

```

Modify this dictionary to completely change your game — no kernel edits needed.

### ⛓️ The PipeWorkFlow System

The secret sauce of Noah's flexibility. Previously called "StreamProcessor", now refined as PipeWorkFlow.

When an action resolves, its d_exec list defines a processing pipeline. Data flows through functions sequentially, each transforming the stream for the next:

```python

def PipeWorkFlow(PipeData, steps: list, args: tuple):
    """Stream processing: data flows through each step function"""
    OutData = PipeData
    for step_func in steps:
        OutData = step_func(OutData, args)
    return OutData
```

Example: The "Shoot" action's pipeline:

```python

"d_exec": [
    crossfire_evaluate,  # 1. Calculate who's hit, initial damage
    crossfire_crash,     # 2. Check counter-fire, annihilate projectiles
    crossfire_reflect,   # 3. Check Reflect status, reverse damage
    crossfire_defend,    # 4. Check Defend status, nullify damage
    crossfire_final      # 5. Apply final damage, display results
]
```

Adding a "Dodge" mechanic? Insert crossfire_dodge into the pipeline. Clean, modular, powerful.

### 🧩 The CmdTable Architecture

New in v1.2-7! A registry for kernel-level operations:

```python

CmdTable = {
    "-update_status": [build_population_status, build_energy_status, ...],
    "-build_able_context": [build_able_enmK, build_able_engK, ...],
    "-tweak_hp": [execute_hp_tweak],
    # ... custom game commands
}
```

Commands are invoked via Core.Exec(cmd_name, domain, PipeData), running their pipelines. This enables:

    Extensibility: Games add custom commands without modifying Noah
    Consistency: All operations use the same pipeline paradigm
    Debugging: Clear execution traces via domain tracking

## 🎮 Ark Frontend: Game-Specific Systems

Ark demonstrates Noah's power through rich, modular implementations:
### 🛠️ Tweak System

Pre-battle customization engine for fine-tuning game state:

```python

InitBattleEnv["tweaks"] = [
    Event("-tweak_hp", domain="Setting.Tweak", PipeData={"target_id": 5, "hp_change": 10}),
    Event("-tweak_team", domain="Setting.Tweak", PipeData={"target_id": 3, "NewTeamID": 2}),
]
```

Supported tweaks:

    tweak_hp / tweak_energy: Modify stats
    tweak_place: Relocate players
    tweak_team: Change team assignments
    tweak_ai_quality: Adjust AI intelligence

Tweaks are queued as Event objects and executed before Round 1.
### 🧠 Dual-Tier AI

AI behavior adapts based on ai_quality:

Level 0 (Basic):

    Random target selection
    Max affordable firepower
    Simple movement

Level 1+ (Advanced):

    _calculate_aggression(): Dynamic risk assessment
    _get_best_shot_target(): Prioritizes low-HP, high-energy, human targets
    predictive_defend_ai(): Anticipates incoming threats
    strategic_move_ai(): Evaluates offensive/defensive value of positions

### ⚙️ EnvProcessors: Validation Pipelines

Settings changes flow through configurable validation chains:

```python

EnvProcessors = {
    "num": {
        "steps": [
            validate_int_and_non_negative,
            post_check_real_num_consistency,
            apply_and_display,
        ]
    },
    "tweak_hp": {
        "steps": [create_tweak_event, display_tweak_result]
    },
}
```

Each setting gets its own pipeline ensuring data integrity before application.


### 📋 Expression System & Localization

Multi-language support via structured dictionaries.
The IO class resolves paths (/ark/welcome) with dynamic substitution ($0, $1).


## 🛠️ Getting Started

### Prerequisites

    Python 3.6+
    A terminal with ANSI color support


### Installation & Running

```shell

# Clone the repository
git clone <your-repo-url>
cd <your-repo-folder>

# Run immediately — no dependencies!
python ark.py
```


First Launch

    Select language (English/中文)
    Main Menu:
        1: Start game with current settings
        2: Modify battle environment
        3: Exit
    In Settings, configure:
        Player counts, HP, map size
        Action ranges
        AI quality (0=basic, 1+=strategic)
        Tweaks for advanced customization


## 🔮 Extending the System
Adding a New Action

    Define logic functions:

```python

def teleport_s(pl, core, auto):
    """Selection phase"""
    # ... input handling
    return (True, noah.Act(pl.id, "teleport"))

def teleport_d(PipeData, args):
    """Resolution phase"""
    act, core = args
    # ... teleport logic
    return None
```

Register in ActDict:

```python

"teleport": {
    "price": lambda act: 5,
    "priority": 10,
    "able": lambda ctx: ctx["self"].energy >= 5,
    "ai": [lambda ctx: ctx["self"].energy * 20],
    "s_exec": teleport_s,
    "d_exec": [teleport_d],
}
```

## 📄 License
MIT License — See LICENSE for details.

## 💭 Design Philosophy

    "Separate mechanism from policy. Build small, composable pieces. Let data drive behavior."

This project has undergone three complete rewrites:

    v1.0: Monolithic design
    v1.1: Introduced separation of concerns
    v1.2: Full kernel abstraction with Noah

The current architecture prioritizes:

    Modularity: Change game rules without touching the engine
    Readability: Code explains itself through clear naming and structure
    Extensibility: Adding features should feel natural, not hacky

It's still evolving, but hopefully the journey is as interesting as the destination! 🚀
