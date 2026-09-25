# Energy Battle - Remake (v1.3-1)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/)
[![Status](https://img.shields.io/badge/Status-Active%20Development-brightgreen)](#)

[English](README.md) | [简体中文](README_zh.md)

---

欢迎体验 **能量之战-重制版 (v1.3-1)**！  
基于 **Noah 内核 (Noah Kernel)** 构建的高扩展性、轻量化终端回合制多人群战策略游戏。

在 1.3-1 版本中，项目完成了一次全面的架构蜕变：**彻底的模组化驱动解耦**。原有的核心游戏规则已被重构为独立模组（`ark_mod.py`）。开发者与玩家无需修改内核引擎代码，即可在游戏运行时自由定制、拓展甚至完全重写战斗逻辑。

---

### 🌟 v1.3-1 核心更新与亮点

*   🧩 **100% 模组驱动内核**：Noah 内核（`noah.py`）不包含任何预设游戏业务规则。战场环境（`BattleEnv`）、行动字典（`ActDict`）以及生命周期钩子均由外置模组动态注入。
*   🔄 **优先级深度合并与热重载**：支持基于 `mod_priority` 的字典深度合并（`deep_merge`）与覆盖标记（`Override`）。支持在战斗内或战斗外随时执行模组热重载（`ModsHotReload`）。
*   ⛓️ **管道化主循环与生命周期 (`CmdTable`)**：整个对局的回合流程（日志沉降、状态快照、行动选择、行动结算、阵亡清理）均被拆解为顺序执行的数据管道（`PipeWorkFlow`），支持任意插桩与拦截。
*   🛠️ **战时系统管理工具 (`SysTool Mod`)**：内置实战调试模组，支持在战斗中随时查询全场高维数据、热调整战场参数、热插拔模组，并支持使用选择器（`all`、`t1` 选队伍、`p0` 选层级、`1-5` 选区间）批量修改玩家属性（`生命值`、`能量`、`位置`、`队伍`、`AI推理级别`）。
*   🌐 **四语言本地化系统**：原生支持简体中文（`zh_cn`）、英文（`en_us`）、繁体中文（`zh_tw`）及日文（`ja_jp`），结合动态模板引擎（`explain`）与打字机终端动效。
*   🛡️ **零外部第三方依赖**：纯 Python 3.12+ 标准库构建，任何支持 ANSI 颜色输出的终端均可即开即玩。

---

### 🏛️ 系统架构解析

项目采用双层解耦架构：

```text
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

 编号 | 行动名称 | 能量消耗 | 优先级 | 说明 |
 :---: | :--- | :---: | :---: | :--- |
 `1` | **充能** | 增加 1 点 | 10 | 向真空汲取能量，每回合随时可用。 |
 `2` | **射击** | 1~3 点/发 | -1 | 发射指定能量大小与方向（上/平/下）的飞弹。双方同时对射将发生能量湮灭。 |
 `3` | **防御** | 0 | 2 | 本回合进入格挡态，免受任何攻击伤害（受最大连续防御限制）。 |
 `4` | **移动** | 1 | 1 | 在最大步长与地图边界限制内调整自身的垂直站位。 |
 `5` | **反射** | 2 | 2 | 激活反射屏障，将受到的攻击伤害原路反弹给攻击发起者。 |
 `6` | **能量波** | 6 | -1 | 向指定方向释放高能 AOE，击穿视野内的全部玩家，造成 5 点伤害。 |
 `7` | **黑洞** | 5 | 9 | 永久吞噬目标本回合选择的行动，使其无效且后续无法再次使用。 |
 `sys`| **系统工具** | 0 | 0 | *(SysTool 模组)* 战时高级数据查询、参数配置修改与玩家批量修改。 |
 `rl` | **查看规则** | 0 | 0 | 调出当前对局所有已加载行动的规则与机制说明。 |
 `bk` | **退出战局** | 0 | 0 | 投降并主动脱离当前对局，返回主菜单。 |

---

### 📦 编写你的第一个 Mod

在 1.3-1 中，编写一个扩展 Mod 极为简单。只需创建一个 `.py` 文件并暴露 `ModContents`：

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
*   Python 3.12 或更高版本。
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

