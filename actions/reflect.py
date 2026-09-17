import noah
from actions.act_utils import predictive_defend_ai


def reflect_ai(context):
    """AI weight for 'Reflect'."""
    return context["engK"]*30+10


def reflect_able(context):
    """Ability check for 'Reflect'."""
    return (context["self"].energy >= 2)


def reflect_price(act):
    return 1


def reflect_s(pl, core, auto):
    """Selection logic for 'Reflect'."""
    act = noah.Act(pl.id, "5")
    if pl.energy >= core.ActDict["5"]["price"](act):
        return (True, noah.Act(pl.id, "5"))
    else:
        if not auto:
            core.ui.indent += 1
            core.ui.out(["/share/poor", "/share/endl"])
            core.ui.indent -= 1
        return (False, None)


def reflect_d(PipeData, args):
    """Resolution logic for 'Reflect'."""
    act, core = args
    act.pay(core)
    pl = core.PlDict[act.ownerID]
    pl.status["reflect"] = True  # reflect status
    if pl.real:
        core.ui.typing_delay = core.org_delay*7
    core.ui.out("./dealed", imp=[act.ownerID])
    if pl.real:
        core.ui.typing_delay = 0
        noah.time.sleep(0.3)


ActionProperties = {  # Reflect
    "price": reflect_price, "priority": 2, "able": reflect_able,
    "human_only": False, "ai": [reflect_ai, predictive_defend_ai], "weight": 1,
    "selecting_exec": reflect_s, "dealing_exec": [reflect_d],
}

