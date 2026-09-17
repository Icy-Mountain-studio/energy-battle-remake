import noah
from actions.act_utils import crossfire_crash, crossfire_reflect, crossfire_defend, crossfire_final
from actions.act_utils import _calculate_aggression, _get_best_shot_target, firecount, get_direction


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
                        while core.ActDict["2"]["price"](act) > s.energy:
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

            core.ui.indent -= 1
            return (True, act)

        else:
            core.ui.out(['/share/poor', '/share/endl'])
            core.ui.indent -= 1
            return (False, None)

    else:  # --- AI Logic ---

        if s.ai_quality == 0:

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
        else:

            # 1. Use our helper function to find the optimal target.
            # This re-calculates the best target, ensuring the AI acts on its decision.
            context = {"self": s, "core": core}
            context = core.Exec("-build_able_context",
                                "shot_selecting", context)

            best_target_pl, _ = _get_best_shot_target(context)

            # If for some reason no target was found, abort.
            if not best_target_pl:
                # This can happen if there are no valid targets. Fallback to charging.
                return (True, noah.Act(pl.id, "1"))
            target = best_target_pl.id

        act = noah.Act(s.id, "2")
        act.lv = 3

        # Calculate the maximum affordable firepower.
        while core.ActDict["2"]["price"](act) > s.energy:
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
        act.distant = core.BattleEnv["shot_distance"]

        return (True, act)


def crossfire_evaluate(PipeData, args):
    """Pipeline Step 1: Evaluate initial hits and damage."""
    act, core = args
    myself = core.PlDict[act.ownerID]
    if myself.real:
        core.ui.typing_delay = core.org_delay*3

    # This function initiates the data stream for a crossfire action.
    PipeData = {"msg": [], "damage": {}}
    PipeData["msg"].append(["./battle", [myself.id, myself.place, act.seth]])
    PipeData = firecount(myself, PipeData, core, act)
    return PipeData


def shot_able(context):
    """Ability check for 'Shoot'."""
    return (context["self"].energy >= 1) and (context["side_enm"] > 0)


def shot_ai(context):
    """AI weight for 'Shoot'."""
    return context["self"].energy*50


def advanced_shot_ai(context):
    aggression = _calculate_aggression(context)
    s = context["self"]
    if s.energy < 1:
        return 0
    _, best_target_score = _get_best_shot_target(context)
    return (best_target_score * s.energy) * aggression


def shot_price(act):
    return act.lv


ActionProperties = {  # Shoot
    "price": shot_price, "priority": -1, "able": shot_able,
    "human_only": False, "ai": [shot_ai, advanced_shot_ai], "weight": 1,
    "selecting_exec": shot_selecting,
    "dealing_exec": [crossfire_evaluate, crossfire_crash, crossfire_reflect, crossfire_defend, crossfire_final],
}

