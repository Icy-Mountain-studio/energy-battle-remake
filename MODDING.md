# Modding Guide for Energy Battle - Remake

🌐 [简体中文模组开发指南](MODDING_zh.md)

Welcome to the Modding Guide! **Energy Battle - Remake** uses the **Noah Kernel**, a custom engine built heavily around the concept of dictionary merging and pipeline data flows. Modding is incredibly easy and does not require modifying the core game files.

A Mod is simply a standard `.py` file that contains a dictionary named `ModContents`.

## 1. The `ModContents` Dictionary

The game loads your Mod by reading the `ModContents` dictionary at the bottom of your Python file. 
Here are the keys you can include:

```python
ModContents = {
    "mod_name": "MyAwesomeMod",       # (Required) The display name of your mod.
    "mod_priority": 10,               # (Optional) Higher priority overwrites lower priority mods. Default is 0.
    "mod_reload": my_reload_hook,     # (Optional) A function called when the mod is loaded/reloaded (useful for injecting language strings).
    "BattleEnv": { ... },             # (Optional) Overrides default environment settings (e.g., initial HP, map size).
    "ActDict": { ... },               # (Optional) Adds new Actions or overrides existing ones.
    "CmdTable": { ... }               # (Optional) Injects pipeline functions into the core game loop.
}
```

## 2. Creating a Custom Action

The most common modding task is adding a new action (like "Heal"). To do this, you define the action's behavior and register it in the `ActDict`.

### Action Properties Template
```python
import noah
from noah import C

def heal_price(act):
    return 3 # Costs 3 Energy

def heal_able(context):
    # Only allowed if HP is less than 5 and energy is enough
    pl = context["self"]
    return pl.energy >= 3 and pl.HP < 5

def heal_selecting(pl, core, auto):
    # What happens when the player chooses this action?
    act = noah.Act(pl.id, "heal_act")
    if pl.energy >= 3:
        act.pay(core)
        return (True, act) # (Success, ActionObject)
    return (False, None)

def heal_dealing(PipeData, args):
    # The resolution logic (what actually happens in the game world)
    act, core = args
    pl = core.PlDict[act.ownerID]
    pl.HP += 2
    
    # Send a message to the UI
    core.ui.out("/act/heal_act/dealed", imp=[pl.id, pl.HP], color="GREEN")
    return PipeData # Must return PipeData for the pipeline to continue

# Register properties
HealProperties = {
    "price": heal_price, 
    "priority": 5,           # Higher priority resolves earlier in the turn
    "able": heal_able,
    "human_only": False, 
    "ai": [lambda ctx: 50],  # AI weight (how much the AI wants to use this)
    "weight": 1,
    "selecting_exec": heal_selecting, 
    "dealing_exec": [heal_dealing]
}
```

## 3. Adding Localization (Text)

Since the game supports multiple languages, you shouldn't hardcode text into your logic. Instead, inject your text into the game's Expression system using the `mod_reload` hook.

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
    # Fetch the currently selected language
    lang = ModContents.get("chosen_lang_code", "en_us")
    
    # Inject our expressions into the global UI
    if "ui" in ModContents and ModContents["ui"]:
        ModContents["ui"].exp.update(MyModExpressions.get(lang, {}))

# Finally, construct the ModContents dictionary
ModContents = {
    "mod_name": "HealActionMod",
    "mod_priority": 10,
    "mod_reload": MyModReload,
    "ActDict": {
        "8": HealProperties # "8" will be the number players type to select this action
    }
}
```

## 4. How to Load Your Mod

1. Save your code into a `.py` file (e.g., `heal_mod.py`) and place it in the game directory.
2. Run the game (`python ark.py`).
3. Select **"3. Manage Mods"** from the main menu.
4. Select **"1. Load Mod"** and type the path to your file (e.g., `heal_mod.py`).
5. Return to the main menu and start a game. Your new action will appear in the action list!
