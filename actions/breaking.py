"""
/Energy-Battle-Remake/actions/breaking.py
"""

from actions.act_utils import free_of_charge, able_forever


def break_selecting(pl, core, auto):
    """Selection logic for 'Surrender'."""
    core.exit_game = True
    return (True, None)


ActionProperties = {  # Surrender/Break
    "price": free_of_charge, "priority": 0, "able": able_forever,
    "human_only": True, "ai": [None], "weight": 0,
    "selecting_exec": break_selecting, "d_exec": [],
}

