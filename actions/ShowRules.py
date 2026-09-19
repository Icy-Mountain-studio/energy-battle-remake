"""
/Energy-Battle-Remake/actions/ShowRules.py
"""

from actions.act_utils import able_forever, free_of_charge

def ShowRules_selecting(pl, core, auto):
    """Selection logic for 'ShowRules' (human-only utility action)."""
    org = core.ui.typing_delay
    core.ui.typing_delay = 0
    core.ui.out("/ark/rules")
    for act in core.ActDict.keys():
        if f"/act/{act}/rule" in core.ui.exp:
            core.ui.out(f"/act/{act}/rule")
    core.ui.out('/share/endl')
    core.ui.typing_delay = org

    core.ls_acts()
    return (False, None) # (False, ...) indicates no action should be registered for the turn.

ActionProperties = { # Show Rules
        "price": free_of_charge, "priority": 0, "able": able_forever,
        "human_only": True, "ai": [None], "weight": 0,
        "selecting_exec": ShowRules_selecting, "dealing_exec": [],
    }
