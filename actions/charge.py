import noah
from actions.act_utils import able_forever, _calculate_aggression

# --- Action Logic Functions ---
# These functions define the behavior of each action in the game.
# They are structured to be passed into the Noah Kernel's ActDict.


def charge_selecting(pl, core, auto):
    """Selection logic for the 'Charge' action."""
    return (True, noah.Act(pl.id, "1"))


def charge_dealing(PipeData, args):
    """Resolution logic for the 'Charge' action."""
    act, core = args
    act.pay(core)
    pl = core.PlDict[act.ownerID]

    if pl.real:
        core.ui.typing_delay = core.org_delay*5
    core.ui.out("./dealed", imp=[act.ownerID, core.PlDict[act.ownerID].energy])
    if pl.real:
        core.ui.typing_delay = 0
        noah.time.sleep(0.3)

    return None


def charge_price(act):
    return -1


def charge_ai(context):
    """AI weight for 'Charge'."""
    return min((100/(context["self"].energy+1))*3, 500)


def advanced_charge_ai(context):
    """Advanced AI's logic for charging. Becomes less willing to charge when aggressive."""
    aggression = _calculate_aggression(context)
    base_desire = min((100/(context["self"].energy+1))*3, 500)
    return base_desire / aggression


ActionProperties = {  # Charge
    "price": charge_price, "priority": 0, "able": able_forever,
    "human_only": False, "ai": [charge_ai, advanced_charge_ai], "weight": 1,
    "selecting_exec": charge_selecting, "dealing_exec": [charge_dealing],
}

