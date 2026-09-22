"""
/Energy-Battle-Remake/actions/move.py
"""

import noah


def get_available_steps(pl, core):
    current_pos = pl.place + pl.status.get("moving", 0)
    max_speed = core.BattleEnv["max_move_speed"]
    map_limit = core.BattleEnv["map"]

    if max_speed <= 0 or map_limit <= 0:
        return []

    min_step = max(-max_speed, -map_limit - current_pos)
    max_step = min(max_speed, map_limit - current_pos)

    return [s for s in range(min_step, max_step + 1) if s != 0]


def move_able(context):
    """Ability check for 'Move'."""
    pl = context["self"]
    core = context["core"]
    return len(get_available_steps(pl, core)) > 0 and pl.energy >= 1


def move_ai(context):
    """AI weight for 'Move'."""
    return context["enmK"] * context["engK"] * 50 + 10


def move_selecting(pl, core, auto):
    """Selection logic for the 'Move' action."""
    if "moving" not in pl.status:
        pl.status["moving"] = 0

    valid_steps = get_available_steps(pl, core)
    current_virtual_pos = pl.place + pl.status["moving"]

    if not valid_steps:
        return (False, None)

    if not auto:  # Human logic
        if pl.energy >= 1:
            core.ui.indent += 1
            min_step = max(-core.BattleEnv["max_move_speed"], -core.BattleEnv["map"] - current_virtual_pos)
            max_step = min(core.BattleEnv["max_move_speed"], core.BattleEnv["map"] - current_virtual_pos)

            while True:
                st = core.ui.inp("./ask", imp=[min_step, max_step])
                core.ui.out('/share/endl')
                try:
                    st_int = int(st)
                    if abs(st_int) > core.BattleEnv["max_move_speed"]:
                        core.ui.out("/share/out-of-range")
                    elif abs(st_int + current_virtual_pos) > core.BattleEnv["map"]:
                        core.ui.out("./out-of-map", color="RED")
                    elif not st_int:
                        core.ui.indent -= 1
                        return (False, None)
                    else:
                        act = noah.Act(pl.id, "4")
                        act.steps = st_int
                        pl.status["moving"] += st_int
                        core.ui.indent -= 1
                        act.pay(core)
                        return (True, act)
                except ValueError:
                    core.ui.out("./error-int", color="RED")
        else:
            core.ui.out(['/share/poor', "/share/endl"])
            return (False, None)
    else:  # AI logic
        s = pl
        st = noah.random.choice(valid_steps)

        act = noah.Act(pl.id, "4")
        act.steps = st
        pl.status["moving"] += st
        act.pay(core)
        return (True, act)


def move_dealing(PipeData, args):
    """Resolution logic for the 'Move' action."""
    act, core = args
    act.pay(core)
    st = act.steps
    pl = core.PlDict[act.ownerID]
    pl.place += st  # Perform the move.

    if abs(pl.place) > core.BattleEnv["map"]:
        core.RaiseError("move_dealing", f"Player {pl.id} is out of map, in place {pl.place}")

    if pl.real:
        core.ui.typing_delay = core.org_delay * 10
    core.ui.out("./dealed", imp=[act.ownerID, st, pl.place])
    if pl.real:
        core.ui.typing_delay = 0
        noah.time.sleep(0.3)
    return None

def move_price(act):
    return 1

ActionProperties = {  # Move
    "price": move_price, "priority": 1, "able": move_able,
    "human_only": False, "ai": [move_ai], "weight": 1,
    "selecting_exec": move_selecting, "dealing_exec": [move_dealing],
}

