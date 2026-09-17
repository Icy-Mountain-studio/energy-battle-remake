import noah
from actions.act_utils import _get_best_shot_target, predictive_defend_ai, free_of_charge, _calculate_aggression


def move_able(context):
    """Ability check for 'Move'."""
    return context["core"].BattleEnv["map"] > 0


def move_ai(context):
    """AI weight for 'Move'."""
    return context["enmK"]*context["engK"]*50+10


def strategic_move_ai(context):
    aggression = _calculate_aggression(context)
    MOVE_INCENTIVE_THRESHOLD = 150

    s = context["self"]
    core = context["core"]
    current_pos_context = context.copy()
    offense_score_current = _get_best_shot_target(current_pos_context)[1]
    defense_threat_current = predictive_defend_ai(
        current_pos_context, ignore_hp=True)
    current_position_score = offense_score_current - \
        (defense_threat_current * 0.7)
    best_new_position_score = -9999
    possible_moves = [-1, 1]
    for move_delta in possible_moves:
        new_place = s.place + move_delta
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
    if not auto:  # Human logic
        core.ui.indent += 1
        while True:
            # Get the number of levels to move.
            st = core.ui.inp("./ask", imp=[core.ActDict["4"]["step"]])
            core.ui.out('/share/endl')
            try:
                st_int = int(st)
                if abs(st_int) > core.ActDict["4"]["step"]:
                    core.ui.out("/share/out-of-range")
                elif abs(st_int + pl.place) > core.BattleEnv["map"]:
                    core.ui.out("./out-of-map", color="RED")
                else:
                    act = noah.Act(pl.id, "4")
                    act.steps = st_int
                    core.ui.indent -= 1
                    return (True, act)
            except ValueError:
                core.ui.out("./error-int", color="RED")
    else:  # AI logic

        s = pl
        random_select = False

        if s.ai_quality > 0:
            # --- Re-run the strategic evaluation to find the best move direction ---
            context = {"self": s, "core": core}
            context = core.Exec("-build_able_context", "move_s", context)

            current_pos_context = context.copy()
            offense_score_current = _get_best_shot_target(
                current_pos_context)[1]
            defense_score_current = predictive_defend_ai(current_pos_context)
            current_position_score = offense_score_current - \
                (defense_score_current * 0.5)

            best_move_delta = 0
            best_new_position_score = current_position_score

            possible_moves = [-1, 1]
            for move_delta in possible_moves:
                new_place = s.place + move_delta
                if abs(new_place) > core.BattleEnv["map"]:
                    continue

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
            ls = list(
                range(-core.ActDict["4"]["step"], core.ActDict["4"]["step"] + 1))
            ls.remove(0)  # AI should always move.

            st = noah.random.choice(ls)
            # Ensure the move is within map boundaries.
            while abs(st + pl.place) > core.BattleEnv["map"]:
                st = noah.random.choice(ls)

        act = noah.Act(pl.id, "4")
        act.steps = st
        return (True, act)


def move_dealing(PipeData, args):
    """Resolution logic for the 'Move' action."""
    act, core = args
    act.pay(core)
    st = act.steps
    pl = core.PlDict[act.ownerID]
    pl.place += st  # Perform the move.

    if abs(pl.place) > core.BattleEnv["map"]:
        core.RaiseError("move_dealing", f"Player {
                        pl.id} is out of map, in place {pl.place}")

    if pl.real:
        core.ui.typing_delay = core.org_delay*7
    core.ui.out("./dealed", imp=[act.ownerID, st, pl.place])
    if pl.real:
        core.ui.typing_delay = 0
        noah.time.sleep(0.3)
    return None


ActionProperties = {  # Move
    "price": free_of_charge, "priority": 1, "able": move_able,
    "human_only": False, "ai": [move_ai, strategic_move_ai], "weight": 1,
    "selecting_exec": move_selecting, "dealing_exec": [move_dealing],
    "step": 1  # Custom parameter for this action
}

