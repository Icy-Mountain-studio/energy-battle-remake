"""
/Energy-Battle-Remake/actions/wave.py
"""

import noah
from actions.act_utils import summarize_crossfire_shots_msg, summarize_crossfire_defend_msg, summarize_crossfire_hurt_msg, summarize_crossfire_misses_msg, summarize_crossfire_reflect_msg, deliver_messages
from actions.act_utils import wave_price, get_direction, firecount
from actions.act_utils import crossfire_crash, crossfire_reflect, crossfire_defend, crossfire_do_damage


def crossfire_wave_eval(PipeData, args):
    """Pipeline Step 1 (for Wave): Evaluate hits on all players in the path."""
    act, core = args
    myself = core.PlDict[act.ownerID]

    # This function initiates the data stream for a wave action.
    PipeData = {"msg": [], "damage": {}, "signatures": {}, "target": act.target, "statistics": {"shots":{}, "misses":{}, "defences":{}, "reflect":{}}}
    PipeData["msg"].append(["./battle", [myself.id, myself.place, act.seth]])

    for pl in core.PlDict.values():
        is_target = ((pl.real and pl != myself) or myself.team != pl.team) and \
                        get_direction(myself.place, pl.place) == act.seth and abs(myself.place - pl.place) < act.distant
        if is_target:
            PipeData["target"] = pl.id
            PipeData = firecount(core, act, myself, PipeData)

    PipeData["msg"].append(["/share/endl", []])
    if not PipeData["damage"]:
        PipeData["msg"] = []

    return PipeData



def auto_AOEseth(pl, core, distance):
    """
    AI helper to determine the optimal direction for an AOE attack.
    It scans the battlefield to find the direction with the most enemies.
    """
    tree_seth = [0, 0, 0]  # [-1 (down), 0 (straight), 1 (up)]
    for place, pls in core.status["pop"].items():
        if place != "all":
            if place > pl.place and abs(place - pl.place) < distance:  # Above player
                tree_seth[2] += len(pls["sum"])
                if not pl.real:
                    tree_seth[2] -= len(pls.get(pl.team, []))
            elif place == pl.place:  # Same level
                tree_seth[1] += len(pls["sum"])
                if not pl.real:
                    tree_seth[1] -= len(pls.get(pl.team, []))
            elif abs(place - pl.place) < distance:  # Below player
                tree_seth[0] += len(pls["sum"])
                if not pl.real:
                    tree_seth[0] -= len(pls.get(pl.team, []))

    return tree_seth.index(max(tree_seth)) - 1


def wave_selecting(pl, core, auto):
    """Selection logic for the 'Energy Wave' action."""
    act = noah.Act(pl.id, "6")

    if pl.energy < core.ActDict["6"]["price"](act):
        if not auto:
            core.ui.indent += 1
            core.ui.out(["/share/poor", "/share/endl"], color='MAGENTA')
            core.ui.indent -= 1
        else:
            core.RaiseError("wave_s", f"Player {
                            pl.id} can't afford wave but selected it")
        return (False, None)

    elif not auto:  # Human Logic
        core.ui.indent += 1
        while True:
            seth = core.ui.inp('./ask-seth')
            if seth == " ":  # Cancel option
                core.ui.out(["./cancel", "/share/endl"])
                core.ui.indent -= 1
                return (False, None)
            try:
                if seth != "":
                    if int(seth) not in [-1, 0, 1]:
                        core.ui.out("./error-no-seth")
                        continue
                else:  # Auto-calculate direction
                    seth = auto_AOEseth(pl, core, core.BattleEnv["wave_distance"])
                    core.ui.out("./auto-seth", imp=[seth])
            except ValueError:
                core.ui.out("./error-int-or-empty")
                continue
            core.ui.out('/share/endl')
            break

        act.seth = int(seth)
        core.ui.typing_delay *= 10
        core.ui.out('./has-sent')
        core.ui.typing_delay /= 10
        core.ui.indent -= 1

    else:  # AI Logic
        act.seth = auto_AOEseth(pl, core, core.BattleEnv["wave_distance"])

    # Set properties for the resolution pipeline.
    act.target = True  # Indicates an AOE attack
    act.lv = 5
    act.channel = "shot-like"
    act.color = "CYAN"
    act.AOE = True
    act.distant = core.BattleEnv["wave_distance"]
    act.attacked_players = []
    act.pay(core)

    return (True, act)


def wave_ai(context):
    """AI weight for 'Energy Wave'."""
    return context["self"].energy*20


def wave_able(context):
    """Ability check for 'Energy Wave'."""
    return (context["self"].energy >= 6)


ActionProperties = {  # Energy Wave
    "price": wave_price, "priority": -1, "able": wave_able,
    "human_only": False, "ai": [wave_ai], "weight": 1,
    "selecting_exec": wave_selecting,
    "dealing_exec": [
        crossfire_wave_eval,
        crossfire_crash,
        crossfire_reflect,
        crossfire_defend,
        crossfire_do_damage,
        summarize_crossfire_shots_msg,
        summarize_crossfire_defend_msg,
        summarize_crossfire_reflect_msg,
        summarize_crossfire_hurt_msg,
        deliver_messages
        ],
}

