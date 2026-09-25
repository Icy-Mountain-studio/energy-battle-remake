# 模组开发指南 (Energy Battle - Remake)

🌐 [English Modding Guide](MODDING.md)

欢迎来到模组 (Mod) 开发指南！**能量之战 - 重制版** 使用了 **Noah Kernel (Noah 内核)**，该内核极其依赖字典合并 (Dictionary Merging) 和数据管道流 (Pipeline) 的概念。因此，为本游戏编写模组非常简单，且完全不需要修改核心源代码。

一个 Mod 本质上只是一个包含名为 `ModContents` 字典的准 `.py` 文件。

## 1. `ModContents` 字典

游戏通过读取你 Python 文件底部的 `ModContents` 字典来加载你的 Mod。
你可以包含以下键值：

```python
ModContents = {
    "mod_name": "MyAwesomeMod",       # (必填) 你的模组显示名称
    "mod_priority": 10,               # (选填) 优先级。数值越大的模组会覆盖数值小的模组。默认为 0。
    "mod_reload": my_reload_hook,     # (选填) 当模组被加载/重载时调用的函数（常用于注入多语言文本）。
    "BattleEnv": { ... },             # (选填) 覆盖默认的战场环境设置（如初始血量、地图大小）。
    "ActDict": { ... },               # (选填) 添加全新的行动指令，或覆盖现有的行动。
    "CmdTable": { ... }               # (选填) 向游戏核心主循环的管道中注入自定义逻辑函数。
}
```

## 2. 创建自定义行动 (Action)

最常见的开发需求是添加一个新的行动（例如：“治疗”）。要做到这一点，你需要定义行动的行为机制，并将其注册到 `ActDict` 中。

### 动作属性模板
```python
import noah
from noah import C

def heal_price(act):
    return 3 # 消耗 3 点能量

def heal_able(context):
    # 仅当生命值低于 5 且能量足够时才允许使用
    pl = context["self"]
    return pl.energy >= 3 and pl.HP < 5

def heal_selecting(pl, core, auto):
    # 玩家（或AI）选择此行动时的处理逻辑
    act = noah.Act(pl.id, "heal_act") # "heal_act" 是内部动作ID
    if pl.energy >= 3:
        act.pay(core)
        return (True, act) # 返回 (是否成功, 行动对象)
    return (False, None)

def heal_dealing(PipeData, args):
    # 结算逻辑（在游戏世界中实际发生的事情）
    act, core = args
    pl = core.PlDict[act.ownerID]
    pl.HP += 2
    
    # 向 UI 输出文本
    core.ui.out("/act/heal_act/dealed", imp=[pl.id, pl.HP], color="GREEN")
    return PipeData # 必须返回 PipeData 以确保内核管道流继续运行

# 注册动作属性
HealProperties = {
    "price": heal_price, 
    "priority": 5,           # 优先级（数字越大，在回合结算时越先执行）
    "able": heal_able,
    "human_only": False,     # 是否仅限人类玩家使用
    "ai": [lambda ctx: 50],  # AI 权重（数字越大，AI 越喜欢用）
    "weight": 1,
    "selecting_exec": heal_selecting, 
    "dealing_exec": [heal_dealing]
}
```

## 3. 添加本地化文本 (Localization)

因为游戏支持多语言，所以请不要将文本硬编码到逻辑中。相反，你应该利用 `mod_reload` 钩子将文本注入到游戏的 Expression（表达式）系统中。

```python
MyModExpressions = {
    "en_us": {
        '/act/heal_act/name': f"{C['GREEN']}Heal{C['RESET']}",
        '/act/heal_act/price': "3 Energy",
        '/act/heal_act/rule': "Restores 2 HP. Requires HP < 5.",
        '/act/heal_act/dealed': "Player $0 healed themselves! HP is now $1."
    },
    "zh_cn": {
        '/act/heal_act/name': f"{C['GREEN']}治疗{C['RESET']}",
        '/act/heal_act/price': "3 能量",
        '/act/heal_act/rule': "恢复 2 点生命值。需要在生命值低于 5 时使用。",
        '/act/heal_act/dealed': "玩家 $0 治疗了自己！目前 HP 为 $1。"
    }
}

def MyModReload():
    # 获取当前玩家选择的语言代码
    lang = ModContents.get("chosen_lang_code", "zh_cn")
    
    # 将我们的文本字典注入到全局 UI 中
    if "ui" in ModContents and ModContents["ui"]:
        ModContents["ui"].exp.update(MyModExpressions.get(lang, {}))

# 最后，组装 ModContents 字典
ModContents = {
    "mod_name": "HealActionMod",
    "mod_priority": 10,
    "mod_reload": MyModReload,
    "ActDict": {
        "8": HealProperties # "8" 就是玩家在终端里需要敲击的行动编号
    }
}
```

## 4. 如何加载你的 Mod

1. 将上述代码保存为一个 `.py` 文件（例如 `heal_mod.py`），并将其放在游戏根目录下。
2. 启动游戏 (`python ark.py`)。
3. 在主菜单中选择 **"3. 管理模组" (Manage Mods)**。
4. 选择 **"1. 加载模组" (Load Mod)**，然后输入你的文件路径（例如 `heal_mod.py`）。
5. 按回车返回主菜单并开始游戏。你会在局内看到全新的行动指令！

