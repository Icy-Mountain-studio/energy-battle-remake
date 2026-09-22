"""
/Energy-Battle-Remake/actions/shot.py
"""

import noah
from actions.act_utils import crossfire_crash, crossfire_reflect, crossfire_defend, crossfire_do_damage
from actions.act_utils import deliver_messages
from actions.act_utils import firecount, get_direction


def shot_selecting(pl, core, auto):
    """Selection logic for the 'Shoot' action. Handles both human and AI players."""
    s = pl

    if not auto:
        # --- Human Player Logic ---
        # Check for the minimum energy requirement.
        act = noah.Act(pl.id, "2")
        act.lv = 1
        core.ui.indent += 1

        if s.energy >= core.ActDict["2"]["price"](act):

            while True:
                # Prompt for the target.
                target = core.ui.inp('./ask-target')
                if target == "":
                    core.ui.out(["./cancel", "/share/endl"])
                    core.ui.indent -= 1
                    return (False, None)
                try:
                    tg = core.PlDict[int(target)]
                    # Validate that the target exists and is not eliminated.
                    if int(target) not in core.status["snap"]:
                        core.ui.out("./error-existPL")
                        continue
                    # Validate that the target is not a non-human teammate or self.
                    elif tg.team == s.team and not (tg.real and tg.id != s.id):
                        core.ui.out("./error-self")
                        continue
                except (ValueError, KeyError):
                    core.ui.out("./error-int")
                    continue
                break

            core.ui.out("/share/endl")

            while True:
                # Prompt for the firing energy level.
                act.lv = core.ui.inp('./ask-lv')
                try:
                    if act.lv != "":
                        act.lv = int(act.lv)
                        if act.lv not in [1, 2, 3]:
                            core.ui.out("./error-no-lv")
                            continue
                        elif core.ActDict["2"]["price"](act) > s.energy:
                            core.ui.out("./error-no-energy")
                            continue
                    else:
                        # Auto-calculate max possible firing level.
                        act.lv = 3
                        while core.ActDict["2"]["price"](act) > s.energy or act.lv > tg.HP:
                            act.lv -= 1
                        core.ui.out("./auto-lv", imp=[act.lv])

                except ValueError:
                    core.ui.out("./error-int-or-empty")
                    continue
                break

            core.ui.out("/share/endl")

            while True:
                # Prompt for the firing direction (seth).
                seth = core.ui.inp('./ask-seth')
                try:
                    if seth != "":
                        if int(seth) not in [-1, 0, 1]:
                            core.ui.out("./error-no-seth")
                            continue
                    else:
                        # Auto-calculate direction based on target's position.
                        seth = get_direction(
                            s.place, core.status["snap"][int(target)][2])
                        core.ui.out("./auto-seth", imp=[seth])
                except ValueError:
                    core.ui.out("./error-int-or-empty")
                    continue

                core.ui.out('/share/endl')
                break

            act.target = int(target)
            act.seth = int(seth)

            core.ui.typing_delay *= 10
            core.ui.out('./has-sent')
            core.ui.typing_delay /= 10

            # Set properties for the resolution pipeline.
            act.channel = "shot-like"
            act.dealed = []
            act.color = "RED"
            act.distant = core.BattleEnv["shot_distance"]
            act.pay(core)
            act.AOE = False

            core.ui.indent -= 1
            return (True, act)

        else:
            core.ui.out(['/share/poor', '/share/endl'])
            core.ui.indent -= 1
            return (False, None)

    else:  # --- AI Logic ---

        # 1. Efficiently find a target from the pre-calculated status cache.
        shotable = []
        for i in range(s.place - 1, s.place + 2):
            if i in core.status["pop"]:
                shotable += core.status["pop"][i]["sum"]

        target = pl.id
        _tg = core.status["snap"][target]
        # Ensure the AI doesn't target itself or a teammate.
        while _tg[3] == pl.team and ((not pl.real) or target == pl.id):
            target = noah.random.choice(shotable)
            _tg = core.status["snap"][target]
            shotable.remove(target)

        act = noah.Act(s.id, "2")
        act.lv = 3

        # Calculate the maximum affordable firepower.
        while core.ActDict["2"]["price"](act) > s.energy or act.lv > core.status["snap"][target][0]:
            act.lv -= 1
            if act.lv < 1:
                core.RaiseError(
                    "shot_selecting", f"shot_price might wemt wrong (in P{pl.id}'s selection)")
                break

        # Defensive programming: ensure AI doesn't shoot with 0 energy,
        # even though the 'able' function should prevent this.
        if act.lv <= 0:
            core.RaiseError("shot_selecting", f"Player {
                            pl.id} could not afford shotting but selected it automatically")
            return (False, None)

        act.target = int(target)
        act.seth = get_direction(s.place, core.status["snap"][target][2])
        act.channel = "shot-like"
        act.color = "RED"
        act.AOE = False
        act.distant = core.BattleEnv["shot_distance"]
        act.pay(core)

        return (True, act)


def crossfire_evaluate(PipeData, args):
    """Pipeline Step 1: Evaluate initial hits and damage."""
    act, core = args
    myself = core.PlDict[act.ownerID]
    if myself.real:
        core.ui.typing_delay = core.org_delay*3

    # This function initiates the data stream for a crossfire action.
    PipeData = {"msg": [], "damage": {}, "signatures": {}, "target": act.target, "statistics": {"shots":{}, "misses":{}, "defences":{}, "reflect":{}}}
    
    PipeData["msg"].append(["./battle", [myself.id, myself.place, act.seth]])
    PipeData = firecount(core, act, myself, PipeData)
    return PipeData


def shot_able(context):
    """Ability check for 'Shoot'."""
    return (context["self"].energy >= 1) and (context["side_enm"] > 0)


def shot_ai(context):
    """AI weight for 'Shoot'."""
    return context["self"].energy*50


def shot_price(act):
    return act.lv


ActionProperties = {  # Shoot
    "price": shot_price, "priority": -1, "able": shot_able,
    "human_only": False, "ai": [shot_ai], "weight": 1,
    "selecting_exec": shot_selecting,
    "dealing_exec": [
        crossfire_evaluate,
        crossfire_crash,
        crossfire_reflect,
        crossfire_defend,
        crossfire_do_damage,
        deliver_messages
        ],
}

