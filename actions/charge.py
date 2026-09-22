"""
/Energy-Battle-Remake/actions/charge.py
"""

import noah
from actions.act_utils import able_forever

# --- Action Logic Functions ---
# These functions define the behavior of each action in the game.
# They are structured to be passed into the Noah Kernel's ActDict.


def charge_selecting(pl, core, auto):
    """Selection logic for the 'Charge' action."""
    act = noah.Act(pl.id, "1")
    act.pay(core)
    act.energy_should_have = pl.energy

    if pl.real:
        core.ui.typing_delay *= 5
        core.ui.out(["./dealed", "/share/endl"], imp=[pl.id, act.energy_should_have])
        core.ui.typing_delay /= 5
        noah.time.sleep(0.3)

    return (True, act)


def charge_dealing(PipeData, args):
    """Resolution logic for the 'Charge' action."""
    act, core = args
    pl = core.PlDict[act.ownerID]

    if not pl.real:
        core.ui.out("./dealed", imp=[act.ownerID, act.energy_should_have])

    return None


def charge_price(act):
    return -1


def charge_ai(context):
    """AI weight for 'Charge'."""
    return min((100/(context["self"].energy+1))*3, 500)


ActionProperties = {  # Charge
    "price": charge_price, "priority": 10, "able": able_forever,
    "human_only": False, "ai": [charge_ai], "weight": 1,
    "selecting_exec": charge_selecting, "dealing_exec": [charge_dealing],
}

