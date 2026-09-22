# Energy Battle - Remake (v1.3-0)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Status](https://img.shields.io/badge/Status-Active%20Development-brightgreen)](#)

[English](#english) | [简体中文](#简体中文)

---

<a name="english"></a>
## 🇬🇧 English

Welcome to **Energy Battle - Remake (v1.3-0)**!  
A tactical, highly extensible, turn-based terminal strategy game powered by the **Noah Kernel**.

In version 1.3-0, the project completed a massive architectural upgrade: **complete mod-driven decoupling**. Even the original base game logic has been extracted into a standalone mod (`ark_mod.py`), allowing developers to customize, extend, or completely replace game mechanics at runtime without modifying a single line of engine core code.

---

### 🌟 Key Highlights in v1.3-0

*   🧩 **100% Mod-Driven Architecture**: The Noah Kernel (`noah.py`) has zero built-in game rules. Battle environment (`BattleEnv`), action dictionaries (`ActDict`), and lifecycle hooks are loaded dynamically from pluggable mods.
*   🔄 **Priority Deep Merge & Hot Reloading**: Mods specify loading priorities. Higher-priority mods seamlessly override or extend lower-priority ones. Supports real-time hot-reloading (`ModsHotReload`) during gameplay.
*   ⛓️ **Pipeline-Driven Lifecycle (`CmdTable`)**: Turn operations (logging, status snapshot, action selection, resolution, elimination checks) are decomposed into customizable, sequential execution pipelines (`PipeWorkFlow`).
*   🛠️ **In-Battle Administration (`SysTool Mod`)**: Built-in wartime dev-tools allowing real-time status inspection, battlefield environment tweaking, live mod swapping, and batch player attribute editing (`HP`, `energy`, `place`, `team`, `ai_quality`) using flexible selectors (`all`, `t1`, `p0`, `1-5`).
*   🌐 **Quad-Language Localization**: Full I18N support for English (`en_us`), Simplified Chinese (`zh_cn`), Traditional Chinese (`zh_tw`), and Japanese (`ja_jp`), complete with dynamic path resolution and ANSI typewriter effects.
*   🛡️ **Zero External Dependencies**: Written in pure Python 3.10+. Runs in any terminal with ANSI color support.

---

### 🏛️ System Architecture

The project maintains a clean two-tier decoupled architecture:

```
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

| Key | Name | Cost | Priority | Description |
| :---: | :--- | :---: | :---: | :--- |
| `1` | **Charge** | +1 Energy | 10 | Draws 1 energy from the void. Always available. |
| `2` | **Shoot** | 1~3 Energy | -1 | Launches directional projectiles (up, level, down). Colliding shots annihilate each other. |
| `3` | **Defend** | 0 | 2 | Shields against attacks for the turn. Subject to consecutive usage limits. |
| `4` | **Move** | 1 Energy | 1 | Shifts vertical level within allowed speed and map boundaries. |
| `5` | **Reflect** | 2 Energy | 2 | Reverses incoming attack damage back to the attacker. |
| `6` | **Energy Wave** | 6 Energy | -1 | Devastating 5-damage directional AOE hitting all targets in line of sight. |
| `7` | **Black Hole** | 5 Energy | 9 | Consumes an opponent's chosen action, disabling and sealing it permanently. |
| `sys`| **System Tools** | 0 | 0 | *(SysTool Mod)* In-battle administration, batch editing, and live mod loading. |
| `rl` | **Show Rules** | 0 | 0 | Displays gameplay instructions and rules. |
| `bk` | **Surrender** | 0 | 0 | Forfeits the battle and returns to the menu. |

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
*   Python 3.10 or higher.
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

<a name="简体中文"></a>
## 🇨🇳 简体中文

欢迎体验 **能量之战-重制版 (v1.3-0)**！  
基于 **Noah 内核 (Noah Kernel)** 构建的高扩展性、轻量化终端回合制多人群战策略游戏。

在 1.3-0 版本中，项目完成了一次全面的架构蜕变：**彻底的模组化驱动解耦**。原有的核心游戏规则已被重构为独立模组（`ark_mod.py`）。开发者与玩家无需修改内核引擎代码，即可在游戏运行时自由定制、拓展甚至完全重写战斗逻辑。

---

### 🌟 v1.3-0 核心更新与亮点

*   🧩 **100% 模组驱动内核**：Noah 内核（`noah.py`）不包含任何预设游戏业务规则。战场环境（`BattleEnv`）、行动字典（`ActDict`）以及生命周期钩子均由外置模组动态注入。
*   🔄 **优先级深度合并与热重载**：支持基于 `mod_priority` 的字典深度合并（`deep_merge`）与覆盖标记（`Override`）。支持在战斗内或战斗外随时执行模组热重载（`ModsHotReload`）。
*   ⛓️ **管道化主循环与生命周期 (`CmdTable`)**：整个对局的回合流程（日志沉降、状态快照、行动选择、行动结算、阵亡清理）均被拆解为顺序执行的数据管道（`PipeWorkFlow`），支持任意插桩与拦截。
*   🛠️ **战时系统管理工具 (`SysTool Mod`)**：内置实战调试模组，支持在战斗中随时查询全场高维数据、热调整战场参数、热插拔模组，并支持使用选择器（`all`、`t1` 选队伍、`p0` 选层级、`1-5` 选区间）批量修改玩家属性（`生命值`、`能量`、`位置`、`队伍`、`AI推理级别`）。
*   🌐 **四语言本地化系统**：原生支持简体中文（`zh_cn`）、英文（`en_us`）、繁体中文（`zh_tw`）及日文（`ja_jp`），结合动态模板引擎（`explain`）与打字机终端动效。
*   🛡️ **零外部第三方依赖**：纯 Python 3.10+ 标准库构建，任何支持 ANSI 颜色输出的终端均可即开即玩。

---

### 🏛️ 系统架构解析

项目采用双层解耦架构：

```
┌────────────────────────────────────────────────────────┐
│                   Ark 前端 (ark.py)                    │
│  - 命令行主菜单与对局会话控制                          │
│  - 动态多语言选择器与交互式菜单 (ark_menus.py)        │
│  - 终端兼容性自检模块 (terminal_check.py)             │
└───────────────────────────┬────────────────────────────┘
                            │ 实例化并注入模组集合
┌───────────────────────────▼────────────────────────────┐
│                    模组加载池 (Mods)                   │
│  ├── ark_mod.py        (能量之战核心规则模组)          │
│  ├── sys_tools_mod.py  (战时管理工具模组)              │
│  └── 外部自定义模组...  (开发者扩展)                   │
└───────────────────────────┬────────────────────────────┘
                            │ 基于优先级的深度合并 (deep_merge)
┌───────────────────────────▼────────────────────────────┐
│                   Noah 内核 (noah.py)                  │
│  - 核心编排调度器 (Core) 与行动注册表 (ActSign)        │
│  - 数据流管道处理器 (PipeWorkFlow)                     │
│  - 隔离作用域的动态模块加载器 (import_module_from_path)│
│  - 集成 gzip 压缩日志与模板渲染的 I/O 引擎 (IO)        │
└────────────────────────────────────────────────────────┘
```

#### 回合生命周期 (`-MainLoop`)
每个回合在 `CmdTable["-MainLoop"]` 管道中流转：
1.  **`write_core_log`**：将当前缓存日志以 gzip 格式压缩并追加写入 `logs/noah_*.gz`。
2.  **`next_round`**：递增回合计数器。
3.  **`clean_round_workflow`**：重置玩家回合专属状态（防御态、反射态、移动中缓存等）。
4.  **`round_title_workflow`**：输出格式化回合分割栏与标题。
5.  **`SelectAct_workflow`**：收集人类与 AI 的行动决策，按优先级归类注册至 `ActSign`。
6.  **`DealAct_workflow`**：按优先级降序触发行动结算流（如：射击对冲湮灭、反射结算、防御格挡、最终伤害落点与战报汇总折叠）。
7.  **`rm_deaths_workflow`**：处理全场致命伤害归属、阵亡通报与队伍减员统计。
8.  **`update_status_workflow`**：重新生成全场人口拓扑、能量热图及全局状态快照。

---

### 🎮 默认行动列表 (Energy Battle Ruleset)

| 编号 | 行动名称 | 能量消耗 | 优先级 | 说明 |
| :---: | :--- | :---: | :---: | :--- |
| `1` | **充能** | 增加 1 点 | 10 | 向真空汲取能量，每回合随时可用。 |
| `2` | **射击** | 1~3 点/发 | -1 | 发射指定能量大小与方向（上/平/下）的飞弹。双方同时对射将发生能量湮灭。 |
| `3` | **防御** | 0 | 2 | 本回合进入格挡态，免受任何攻击伤害（受最大连续防御限制）。 |
| `4` | **移动** | 1 | 1 | 在最大步长与地图边界限制内调整自身的垂直站位。 |
| `5` | **反射** | 2 | 2 | 激活反射屏障，将受到的攻击伤害原路反弹给攻击发起者。 |
| `6` | **能量波** | 6 | -1 | 向指定方向释放高能 AOE，击穿视野内的全部玩家，造成 5 点伤害。 |
| `7` | **黑洞** | 5 | 9 | 永久吞噬目标本回合选择的行动，使其无效且后续无法再次使用。 |
| `sys`| **系统工具** | 0 | 0 | *(SysTool 模组)* 战时高级数据查询、参数配置修改与玩家批量修改。 |
| `rl` | **查看规则** | 0 | 0 | 调出当前对局所有已加载行动的规则与机制说明。 |
| `bk` | **退出战局** | 0 | 0 | 投降并主动脱离当前对局，返回主菜单。 |

---

### 📦 编写你的第一个 Mod

在 1.3-0 中，编写一个扩展 Mod 极为简单。只需创建一个 `.py` 文件并暴露 `ModContents`：

```python
# my_heal_mod.py
import noah
from actions.act_utils import able_forever

def heal_selecting(pl, core, auto):
    pl.HP += 3
    core.ui.out(f"玩家 {pl.id} 恢复了 3 点生命值！", directly=True)
    return (True, noah.Act(pl.id, "heal"))

ActionProperties = {
    "price": lambda act: 2,
    "priority": 5,
    "able": lambda ctx: ctx["self"].energy >= 2,
    "human_only": False,
    "ai": [lambda ctx: 20 if ctx["self"].HP < 5 else 0],
    "weight": 1,
    "selecting_exec": heal_selecting,
    "dealing_exec": [],
}

ModContents = {
    "mod_name": "HealMod",
    "mod_priority": 10,
    "ActDict": {
        "heal": ActionProperties
    }
}
```

随后在游戏主菜单的 **模组管理器**（或对局中输入 `sys`）中输入该文件路径即可完成热加载！

---

### 🚀 快速开始

#### 环境要求
*   Python 3.10 或更高版本。
*   支持 ANSI 转义序列色彩的终端环境（推荐宽度 ≥ 80 列）。

#### 启动游戏
```bash
# 克隆代码仓库
git clone <repository-url>
cd Energy-Battle-Remake

# 运行游戏（零依赖，无需 pip 安装三方库）
python ark.py
```

---

## 📄 License
MIT License — 详见 [LICENSE](LICENSE)。
