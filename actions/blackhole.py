"""
/Energy-Battle-Remake/actions/blackhole.py
"""

import noah

def blackhole_selecting(pl, core, auto):
    """Selection logic for the 'Black Hole' action."""
    act = noah.Act(pl.id, "7")
    if pl.energy >= core.ActDict["7"]["price"](act):
        if not auto: # Human Logic
            core.ui.indent += 1
            while True:
                inp_target = core.ui.inp("./ask")
                try:
                    get = core.PlDict[int(inp_target)]
                    if get != pl:
                        break
                    else:
                        core.ui.out(["./self-selected", "/share/endl"], color="RED")

                except (ValueError, KeyError):
                    core.ui.out("/share/not-found", color="RED")

            act.target = int(inp_target)
            core.ui.out("/share/endl")
            core.ui.indent -= 1

        else: # AI Logic
            available_targets = []
            for i in core.status["pop"].keys():
                if i != "all":
                    available_targets += core.status["pop"][i]["sum"]

            target = pl.id
            _tg = core.status["snap"][target]
            while (_tg[3] == pl.team and not _tg[4]):
                available_targets.remove(target)
                target = noah.random.choice(available_targets)
                _tg = core.status["snap"][target]

            act.target = target

        act.pay(core)
        return (True, act)

    elif not auto:
        core.ui.indent += 1
        core.ui.out("/share/poor", color='MAGENTA')
        core.ui.indent -= 1
        return (False, None)

    else:
        core.RaiseError("wave_s", f"Player {pl.id} can't afford blackhole but selected it")
        return (False, None)


def blackhole_dealing(PipeData, args):
    """Resolution logic for 'Black Hole'."""
    act, core = args
    target = core.PlDict[act.target]
    myself = core.PlDict[act.ownerID]

    if target.real or myself.real:
        core.ui.typing_delay = core.org_delay*5

    # Add the target's chosen actions to their 'unable' list.
    block = [i.key for i in target.acts]
    block = list(set(block))
    target.unable.extend(block)

    # Mark the target's actions as already acted to prevent them from resolving.
    for target_act in target.acts:
        if target_act.key != "7":
            target_act.acted = True

    block_out = ", ".join([core.ui.get(f"/act/{i}/name") for i in block])
    core.ui.out("./result", imp=[act.target, block_out, act.ownerID])

    if target.real or myself.real:
        core.ui.typing_delay = 0
        noah.time.sleep(0.3)

    return None


def blackhole_price(act):
    return 7

def blackhole_able(context):
    """Ability check for 'Black Hole'."""
    return (context["self"].energy >= 7)


def blackhole_ai(context):
    """AI weight for 'Black Hole'."""
    return context["self"].energy*40


ActionProperties = { # Black Hole
        "price": blackhole_price, "priority": 9999, "able": blackhole_able,
        "human_only": False, "ai": [blackhole_ai], "weight": 1,
        "selecting_exec": blackhole_selecting, "dealing_exec": [blackhole_dealing],
    }

