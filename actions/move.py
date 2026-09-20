"""
/Energy-Battle-Remake/actions/move.py
"""

import noah
from actions.act_utils import _get_best_shot_target, predictive_defend_ai, _calculate_aggression


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


def strategic_move_ai(context):
    aggression = _calculate_aggression(context)
    MOVE_INCENTIVE_THRESHOLD = 150

    s = context["self"]
    core = context["core"]
    
    current_virtual_place = s.place + s.status.get("moving", 0)

    current_pos_context = context.copy()
    offense_score_current = _get_best_shot_target(current_pos_context)[1]
    defense_threat_current = predictive_defend_ai(current_pos_context, ignore_hp=True)
    current_position_score = offense_score_current - (defense_threat_current * 0.7)
    
    best_new_position_score = -9999
    possible_moves = [-1, 1]

    for move_delta in possible_moves:
        new_place = current_virtual_place + move_delta
        if abs(new_place) > core.BattleEnv["map"]:
            continue
        temp_s = noah.Player(s.id)
        temp_s.id = s.id
        temp_s.team = s.team
        temp_s.place = new_place
        temp_context = context.copy()
        temp_context["self"] = temp_s

        offense_score_new = _get_best_shot_target(temp_context)[1]
        defense_threat_new = predictive_defend_ai(temp_context, ignore_hp=True)
        new_score = offense_score_new - (defense_threat_new * 0.7)
        if new_score > best_new_position_score:
            best_new_position_score = new_score

    move_incentive = best_new_position_score - current_position_score
    if move_incentive > MOVE_INCENTIVE_THRESHOLD:
        return move_incentive / aggression
    else:
        return 0


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
        random_select = False
        st = None

        if s.ai_quality > 0:
            context = {"self": s, "core": core}
            context = core.Exec("-build_able_context", "move_s", context)

            current_pos_context = context.copy()
            offense_score_current = _get_best_shot_target(current_pos_context)[1]
            defense_score_current = predictive_defend_ai(current_pos_context)
            current_position_score = offense_score_current - (defense_score_current * 0.5)

            best_move_delta = 0
            best_new_position_score = current_position_score

            for move_delta in [-1, 1]:
                if move_delta not in valid_steps:
                    continue

                new_place = current_virtual_pos + move_delta
                temp_s = noah.Player(s.id)
                temp_s.id = s.id
                temp_s.team = s.team
                temp_s.place = new_place
                temp_context = context.copy()
                temp_context["self"] = temp_s

                offense_score_new = _get_best_shot_target(temp_context)[1]
                defense_score_new = predictive_defend_ai(temp_context)
                new_score = offense_score_new - (defense_score_new * 0.5)

                if new_score > best_new_position_score:
                    best_new_position_score = new_score
                    best_move_delta = move_delta

            if best_move_delta == 0:
                random_select = True
            else:
                st = best_move_delta
        else:
            random_select = True

        if random_select:
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
    "human_only": False, "ai": [move_ai, strategic_move_ai], "weight": 1,
    "selecting_exec": move_selecting, "dealing_exec": [move_dealing],
}

