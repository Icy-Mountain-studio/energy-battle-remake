"""
/Energy-Battle-Remake/actions/defend.py
"""

import noah
from actions.act_utils import free_of_charge


def defend_able(context):
    # If max_consecutive_defend_times equals to zero, then it is disabled to any one
    could_defence = not (hasattr(context["self"], "last_defend_round") and context["self"].last_defend_round >= context["core"].BattleEnv["max_consecutive_defend_times"])
    return could_defence and context["core"].BattleEnv["max_consecutive_defend_times"]


def defend_ai(context):
    """AI weight for 'Defend'."""
    return context["engK"]*context["engK"]*100+10


def defend_selecting(pl, core, auto):
    """Selection logic for the 'Defend' action."""
    if core.BattleEnv["max_consecutive_defend_times"]:
        if hasattr(pl, "last_defend_round"):
            if pl.last_defend_round == core.rounds-1:
                if pl.consecutive_defence < core.BattleEnv["max_consecutive_defend_times"]:
                    pl.consecutive_defence += 1
                else:
                    core.ui.out(["./prohibited", "/share/endl"], imp=[core.BattleEnv["max_consecutive_defend_times"]])
                    return (False, None)
            else:
                pl.consecutive_defence = 1
        else:
            pl.consecutive_defence = 1
        pl.last_defend_round = core.rounds
        return (True, noah.Act(pl.id, "3"))
    else:
        core.ui.out(["./prohibited", "/share/endl"], imp=[core.BattleEnv["max_consecutive_defend_times"]])
        return (False, None)


def defend_dealing(PipeData, args):
    """Resolution logic for the 'Defend' action."""
    act, core = args
    act.pay(core)
    pl = core.PlDict[act.ownerID]
    pl.status["defend"] = True

    if pl.real:
        core.ui.typing_delay = core.org_delay*7
    core.ui.out("./dealed", imp=[act.ownerID])
    if pl.real:
        core.ui.typing_delay = 0
        noah.time.sleep(0.3)
    return None


ActionProperties = {  # Defend
    "price": free_of_charge, "priority": 2, "able": defend_able,
    "human_only": False, "ai": [defend_ai], "weight": 1,
    "selecting_exec": defend_selecting, "dealing_exec": [defend_dealing],
}

