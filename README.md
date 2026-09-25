# Energy Battle - Remake (v1.3-1)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/)
[![Status](https://img.shields.io/badge/Status-Active%20Development-brightgreen)](#)

[English](README.md) | [简体中文](README_zh.md)

---

Welcome to **Energy Battle - Remake (v1.3-1)**!  
A tactical, highly extensible, turn-based terminal strategy game powered by the **Noah Kernel**.

In version 1.3-1, the project completed a massive architectural upgrade: **complete mod-driven decoupling**. Even the original base game logic has been extracted into a standalone mod (`ark_mod.py`), allowing developers to customize, extend, or completely replace game mechanics at runtime without modifying a single line of engine core code.

---

### 🌟 Key Highlights in v1.3-1

*   🧩 **100% Mod-Driven Architecture**: The Noah Kernel (`noah.py`) has zero built-in game rules. Battle environment (`BattleEnv`), action dictionaries (`ActDict`), and lifecycle hooks are loaded dynamically from pluggable mods.
*   🔄 **Priority Deep Merge & Hot Reloading**: Mods specify loading priorities. Higher-priority mods seamlessly override or extend lower-priority ones. Supports real-time hot-reloading (`ModsHotReload`) during gameplay.
*   ⛓️ **Pipeline-Driven Lifecycle (`CmdTable`)**: Turn operations (logging, status snapshot, action selection, resolution, elimination checks) are decomposed into customizable, sequential execution pipelines (`PipeWorkFlow`).
*   🛠️ **In-Battle Administration (`SysTool Mod`)**: Built-in wartime dev-tools allowing real-time status inspection, battlefield environment tweaking, live mod swapping, and batch player attribute editing (`HP`, `energy`, `place`, `team`, `ai_quality`) using flexible selectors (`all`, `t1`, `p0`, `1-5`).
*   🌐 **Quad-Language Localization**: Full I18N support for English (`en_us`), Simplified Chinese (`zh_cn`), Traditional Chinese (`zh_tw`), and Japanese (`ja_jp`), complete with dynamic path resolution and ANSI typewriter effects.
*   🛡️ **Zero External Dependencies**: Written in pure Python 3.12+. Runs in any terminal with ANSI color support.

---

### 🏛️ System Architecture

The project maintains a clean two-tier decoupled architecture:

```text
┌────────────────────────────────────────────────────────┐
│                   Ark Frontend (ark.py)                │
│  - CLI Main Menu & Session Management                  │
│  - Language Selector & Menu System (ark_menus.py)      │
│  - Pre-flight Terminal Check (terminal_check.py)       │
└───────────────────────────┬────────────────────────────┘
                            │ Instantiates & Injects
┌───────────────────────────▼────────────────────────────┐
│                    Loaded Mods Pool                    │
│  ├── ark_mod.py        (Base Energy Battle Ruleset)    │
│  ├── sys_tools_mod.py  (In-Battle Admin Suite)         │
│  └── Custom Mods...    (Community Addons)              │
└───────────────────────────┬────────────────────────────┘
                            │ Priority Deep-Merge (`deep_merge`)
┌───────────────────────────▼────────────────────────────┐
│                   Noah Kernel (noah.py)                │
│  - Core Orchestrator & Action Registry (ActSign)       │
│  - Stream Processing Pipelines (PipeWorkFlow)          │
│  - Dynamic Importer (import_module_from_path)          │
│  - Unified I/O Engine with gzip compression (IO)       │
└────────────────────────────────────────────────────────┘
```

#### The Life of a Turn (`-MainLoop`)
Every turn executes through a modular pipeline registered in `CmdTable["-MainLoop"]`:
1.  **`write_core_log`**: Flushes compressed session logs (`logs/noah_*.gz`).
2.  **`next_round`**: Increments the turn counter.
3.  **`clean_round_workflow`**: Resets turn-specific player flags (defend, reflect, temporary movement).
4.  **`round_title_workflow`**: Renders formatted round headers.
5.  **`SelectAct_workflow`**: Handles human input and AI weighted evaluations. Actions are registered into `ActSign` grouped by priority.
6.  **`DealAct_workflow`**: Dispatches actions in descending priority order through action-specific `dealing_exec` pipelines (e.g., crossfire evaluation, annihilation, reflection, defense, and damage delivery).
7.  **`rm_deaths_workflow`**: Processes casualties and casualty attribution.
8.  **`update_status_workflow`**: Rebuilds cached battlefield metrics (population distribution, energy mapping, snapshot).

---

### 🎮 Default Actions in Energy Battle

 Key | Name | Cost | Priority | Description |
 :---: | :--- | :---: | :---: | :--- |
 `1` | **Charge** | +1 Energy | 10 | Draws 1 energy from the void. Always available. |
 `2` | **Shoot** | 1~3 Energy | -1 | Launches directional projectiles (up, level, down). Colliding shots annihilate each other. |
 `3` | **Defend** | 0 | 2 | Shields against attacks for the turn. Subject to consecutive usage limits. |
 `4` | **Move** | 1 Energy | 1 | Shifts vertical level within allowed speed and map boundaries. |
 `5` | **Reflect** | 2 Energy | 2 | Reverses incoming attack damage back to the attacker. |
 `6` | **Energy Wave** | 6 Energy | -1 | Devastating 5-damage directional AOE hitting all targets in line of sight. |
 `7` | **Black Hole** | 5 Energy | 9 | Consumes an opponent's chosen action, disabling and sealing it permanently. |
 `sys`| **System Tools** | 0 | 0 | *(SysTool Mod)* In-battle administration, batch editing, and live mod loading. |
 `rl` | **Show Rules** | 0 | 0 | Displays gameplay instructions and rules. |
 `bk` | **Surrender** | 0 | 0 | Forfeits the battle and returns to the menu. |

---

### 📦 Writing a Custom Mod

Creating a mod is straightforward. A mod is a standalone `.py` file exposing a `ModContents` dictionary:

```python
# my_teleport_mod.py
import noah
from actions.act_utils import able_forever

def teleport_select(pl, core, auto):
    pl.place = 0  # Blink to center level
    return (True, noah.Act(pl.id, "tp"))

ActionProperties = {
    "price": lambda act: 3,
    "priority": 8,
    "able": lambda ctx: ctx["self"].energy >= 3,
    "human_only": False,
    "ai": [lambda ctx: 15],
    "weight": 1,
    "selecting_exec": teleport_select,
    "dealing_exec": [],
}

ModContents = {
    "mod_name": "TeleportMod",
    "mod_priority": 10,  # Merged on top of lower priority mods
    "ActDict": {
        "tp": ActionProperties
    }
}
```

Load your mod dynamically before or during battle via the **Mod Manager**!

---

### 🚀 Quick Start

#### Requirements
*   Python 3.12 or higher.
*   Terminal supporting ANSI escape sequences (width ≥ 80 cols recommended).

#### Run the Game
```bash
# Clone the repository
git clone <repository-url>
cd Energy-Battle-Remake

# Launch immediately (no pip installs needed!)
python ark.py
```

---

## 📄 License
MIT License — See [LICENSE](LICENSE) for details.

