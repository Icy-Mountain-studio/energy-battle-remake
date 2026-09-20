"""
/Energy-Battle-Remake/actions/act_utils.py
"""

def get_direction(place1, place2):
    """
    Calculates the relative direction from place1 to place2.
    Returns: -1 for down, 1 for up, 0 for the same level.
    """
    if place1 > place2:
        return -1
    elif place1 < place2:
        return 1
    else:
        return 0


def firecount(core, act, myself, PipeData):
    for current_act in myself.acts:
        if current_act.channel == "shot-like" and not current_act.acted:
            if current_act.AOE:
                target = core.PlDict[PipeData["target"]]
                if target in current_act.attacked_players:
                    continue
            else:
                target = core.PlDict[current_act.target]
                current_act.acted = True
            is_miss = (current_act.seth != get_direction(myself.place, target.place) or
                    abs(myself.place - target.place) > current_act.distant)

            if is_miss:
                # The shot missed.
                PipeData["msg"].append([f"/act/{current_act.key}/shot-miss", [myself.id, target.id, current_act.lv]])
                try:
                    PipeData["statistics"]["misses"][current_act.lv].append(myself.id)
                except KeyError:
                    PipeData["statistics"]["misses"][current_act.lv] = [myself.id]
            else:
                # The shot hit.
                PipeData["msg"].append([f"/act/{current_act.key}/shot", [myself.id, target.id, current_act.lv]])
                try:
                    PipeData["statistics"]["shots"][current_act.lv].append(target.id)
                except KeyError:
                    PipeData["statistics"]["shots"][current_act.lv] = [target.id]

                if target.id not in PipeData["damage"]:
                    PipeData["damage"][target.id] = current_act.lv
                else:
                    PipeData["damage"][target.id] += current_act.lv
                PipeData["signatures"][target.id] = current_act.key

            if current_act.AOE:
                current_act.attacked_players.append(target)

    return PipeData


def crossfire_crash(PipeData, args):
    """Pipeline Step 2: Check for counter-fire and projectile annihilation."""
    act, core = args
    attacker = core.PlDict[act.ownerID]
    msg = []

    for playerID in PipeData["damage"].keys():
        if playerID != attacker.id:
            for current_act in core.PlDict[playerID].acts:
                # Check if the target is also performing a shot-like action back at the attacker.
                if current_act.channel == "shot-like" and not current_act.acted:
                    if (current_act.target is True or current_act.target == attacker.id):
                        myself = core.PlDict[playerID]
                        is_miss = (current_act.seth != get_direction(myself.place, attacker.place) or
                                   abs(myself.place - attacker.place) > current_act.distant)
                        if is_miss:
                            msg.append([f"/act/{current_act.key}/shot-miss", [playerID, attacker.id, current_act.lv]])
                            try:
                                PipeData["statistics"]["misses"][current_act.lv].append(attacker.id)
                            except KeyError:
                                PipeData["statistics"]["misses"][current_act.lv] = [attacker.id]
                        else:
                            # Both sides hit, projectiles crash.
                            msg.append([f"/act/{current_act.key}/anti", [playerID, attacker.id, current_act.lv]])
                            crash_amount = min(current_act.lv, PipeData["damage"][playerID])
                            msg.append([f"/act/{current_act.key}/crash", [crash_amount]])
                            PipeData["damage"][playerID] -= current_act.lv
                            if PipeData["damage"][playerID] > 0:
                                PipeData["signatures"][playerID] = current_act.key
                            elif PipeData["damage"][playerID] < 0:
                                PipeData["signatures"][attacker.id] = current_act.key

                        current_act.acted = True

    PipeData["msg"] += msg
    if msg:
        PipeData["msg"].append(["/share/endl", []])
    return PipeData


def crossfire_reflect(PipeData, args):
    """Pipeline Step 3: Check if any target has 'Reflect' active."""
    act, core = args
    attacker = core.PlDict[act.ownerID]

    someone_reflected = False
    for playerID in PipeData["damage"].keys():
        if "reflect" in core.PlDict[playerID].status and "reflect" not in attacker.status:
            PipeData["msg"].append(["./reflect", [act.ownerID, PipeData["damage"][playerID], playerID]])

            try:
                PipeData["statistics"]["reflect"][PipeData["damage"][playerID]].append(playerID)
            except KeyError:
                PipeData["statistics"]["reflect"][PipeData["damage"][playerID]] = [playerID]

            if PipeData["damage"][playerID] > 0:
                PipeData["damage"][playerID] *= -1 # Negative damage means it's reflected back
            else:
                PipeData["damage"][playerID] *= 2
            PipeData["signatures"][act.ownerID] = "5"
            someone_reflected = True

    if someone_reflected:
        PipeData["msg"].append(["/share/endl", []])
    return PipeData


def crossfire_defend(PipeData, args):
    """Pipeline Step 4: Check if any target has 'Defend' active."""
    act, core = args
    someone_defend = False
    for playerID in PipeData["damage"].keys():
        if "defend" in core.PlDict[playerID].status:
            PipeData["msg"].append(["./defend", [playerID, PipeData["damage"][playerID]]])
            if PipeData["damage"][playerID] > 0:
                try:
                    PipeData["statistics"]["defences"][PipeData["damage"][playerID]].append(playerID)
                except KeyError:
                    PipeData["statistics"]["defences"][PipeData["damage"][playerID]] = [playerID]
                PipeData["damage"][playerID] = 0 # Nullify damage
            someone_defend = True

    if someone_defend:
        PipeData["msg"].append(["/share/endl", []])
    return PipeData


def crossfire_do_damage(PipeData, args):
    """Pipeline Step 5: Apply final damage and display results."""
    act, core = args
    attacker = core.PlDict[act.ownerID]

    for playerID, hurt_lv in PipeData["damage"].items():
        tg = core.PlDict[playerID]
        if hurt_lv > 0: # Positive value: target takes damage.
            tg.hurted(hurt_lv, attacker.id, PipeData["signatures"][tg.id], core)
            PipeData["msg"].append(["./final-hurt", [playerID, hurt_lv, tg.HP]])
        elif hurt_lv < 0: # Negative value: attacker takes reflected damage.
            attacker.hurted(-hurt_lv, tg.id, PipeData["signatures"][attacker.id], core)
            PipeData["msg"].append(["./final-hurt", [attacker.id, -hurt_lv, attacker.HP]])
        else: # Zero damage
            PipeData["msg"].append(["./peace", []])
        
    return PipeData

"""
Message summarization functions.
These keep the battle log clean when AOE skills hit many players.
"""

def summarize_crossfire_shots_msg(PipeData, args):
    act, core = args
    threshold = core.BattleEnv.get("msg_summary_threshold", 20)

    # 1. Count total shots
    statistic_amount = 0
    for player_lists in PipeData["statistics"]["shots"].values():
        statistic_amount += len(player_lists)

    # 2. If it exceeds the threshold, rebuild the message list
    if statistic_amount > threshold:
        new_msg = []
        has_inserted = False

        for msg in PipeData["msg"]:
            # Use endswith to avoid deleting "/shot-miss" by mistake
            if msg[0].endswith("/shot"):
                if not has_inserted:
                    # Insert the summary messages exactly where the first detail was
                    for level, player_list in PipeData["statistics"]["shots"].items():
                        unique_count = len(set(player_list))
                        new_msg.append(["./summary-shots", [level, unique_count]])
                    has_inserted = True
                # Else: Do nothing, which effectively deletes the detailed message
            else:
                new_msg.append(msg)

        PipeData["msg"] = new_msg

    return PipeData


def summarize_crossfire_misses_msg(PipeData, args):
    act, core = args
    threshold = core.BattleEnv.get("msg_summary_threshold", 20)

    statistic_amount = 0
    for player_lists in PipeData["statistics"]["misses"].values():
        statistic_amount += len(player_lists)

    if statistic_amount > threshold:
        new_msg = []
        has_inserted = False

        for msg in PipeData["msg"]:
            if msg[0].endswith("/shot-miss"):
                if not has_inserted:
                    for level, player_list in PipeData["statistics"]["misses"].items():
                        unique_count = len(set(player_list))
                        new_msg.append(["./summary-misses", [level, unique_count]])
                    has_inserted = True
            else:
                new_msg.append(msg)

        PipeData["msg"] = new_msg

    return PipeData


def summarize_crossfire_defend_msg(PipeData, args):
    act, core = args
    threshold = core.BattleEnv.get("msg_summary_threshold", 20)

    statistic_amount = 0
    for player_lists in PipeData["statistics"]["defences"].values():
        statistic_amount += len(player_lists)

    if statistic_amount > threshold:
        new_msg = []
        has_inserted = False

        for msg in PipeData["msg"]:
            if "/defend" in msg[0]:
                if not has_inserted:
                    for level, player_list in PipeData["statistics"]["defences"].items():
                        unique_count = len(set(player_list))
                        new_msg.append(["./summary-defences", [level, unique_count]])
                    has_inserted = True
            else:
                new_msg.append(msg)

        PipeData["msg"] = new_msg

    return PipeData


def summarize_crossfire_reflect_msg(PipeData, args):
    act, core = args
    threshold = core.BattleEnv.get("msg_summary_threshold", 20)

    statistic_amount = 0
    for player_lists in PipeData["statistics"]["reflect"].values():
        statistic_amount += len(player_lists)

    if statistic_amount > threshold:
        new_msg = []
        has_inserted = False

        for msg in PipeData["msg"]:
            if "/reflect" in msg[0]:
                if not has_inserted:
                    for level, player_list in PipeData["statistics"]["reflect"].items():
                        unique_count = len(set(player_list))
                        new_msg.append(["./summary-reflects", [level, unique_count]])
                    has_inserted = True
            else:
                new_msg.append(msg)

        PipeData["msg"] = new_msg

    return PipeData


def summarize_crossfire_hurt_msg(PipeData, args):
    act, core = args
    threshold = core.BattleEnv.get("msg_summary_threshold", 20)

    # Count how many players actually took damage (non-zero)
    valid_damages = [abs(hurt_lv) for hurt_lv in PipeData["damage"].values() if hurt_lv != 0]

    if len(valid_damages) > threshold:
        # Count the frequency of each damage amount
        damage_counts = {}
        for lv in valid_damages:
            damage_counts[lv] = damage_counts.get(lv, 0) + 1

        new_msg = []
        has_inserted = False

        for msg in PipeData["msg"]:
            if "/final-hurt" in msg[0]:
                if not has_inserted:
                    # Sort the damage amounts for cleaner output
                    for lv, count in sorted(damage_counts.items()):
                        new_msg.append(["./summary-damage", [lv, count]])
                    has_inserted = True
            else:
                new_msg.append(msg)

        PipeData["msg"] = new_msg

    return PipeData


def deliver_messages(PipeData, args):
    # Display the battle log.
    act, core = args
    if len(PipeData["msg"]) > 1:
        msg = PipeData["msg"].pop(0)
        core.ui.out("/share/endl")
        core.ui.out(msg[0], imp=msg[1], color=act.color)
        core.ui.indent += 1
        for msg_index in range(len(PipeData["msg"])):
            msg = PipeData["msg"][msg_index]
            if not (PipeData["msg"][msg_index-1][0] == "/share/endl" and msg[0]=="/share/endl"):
                core.ui.out(msg[0], imp=msg[1], color=act.color, speed_stability=-1000)
        if len(PipeData["msg"]) >= 4:
            core.ui.out("./wonderful", color="MAGENTA")
        core.ui.indent -= 1

    core.ui.typing_delay = 0
    return None


def _calculate_aggression(context: dict) -> float:
    """
    A self-contained helper function to calculate an AI's aggression level.
    This acts as a "mood sensor" for the advanced AI.
    Returns:
        A multiplier where > 1.0 is aggressive, < 1.0 is defensive.
    """
    self = context["self"]
    core = context["core"]

    my_team_energy = 0
    enemy_team_energy = 0
    my_team_population = 0
    enemy_team_population = 0

    for pl in core.PlDict.values():
        if pl.team == self.team:
            my_team_energy += pl.energy
            my_team_population += 1
        else:
            enemy_team_energy += pl.energy
            enemy_team_population += 1

    if enemy_team_energy == 0: enemy_team_energy = 1
    if enemy_team_population == 0: enemy_team_population = 1

    energy_ratio = my_team_energy / enemy_team_energy
    population_ratio = my_team_population / enemy_team_population

    base_multiplier = (energy_ratio * 0.7) + (population_ratio * 0.3)

    aggression = max(0.5, min(2.0, base_multiplier))

    return aggression



def predictive_defend_ai(context, ignore_hp=False):
    aggression = _calculate_aggression(context)

    s = context["self"]
    core = context["core"]
    base_threat = (context.get("enmK", 0.5) *
                   context.get("engK", 0.5)) * 150 + 10
    specific_threat = 0
    for i in range(s.place - 1, s.place + 2):
        if i in core.status["pop"]:
            for pl_id in core.status["pop"][i]["sum"]:
                if core.PlDict[pl_id].team == s.team or pl_id == s.id:
                    continue
                enemy_pl = core.PlDict[pl_id]
                if enemy_pl.energy >= wave_price(None):
                    specific_threat += 300
                if enemy_pl.energy >= 3:
                    specific_threat += enemy_pl.energy * 20
    incoming_threat_score = base_threat + specific_threat
    if ignore_hp:
        return incoming_threat_score
    hp_multiplier = 2.5 / (s.HP + 0.5)
    final_score = incoming_threat_score * hp_multiplier
    return final_score / aggression


def _get_best_shot_target(context):
    """
    A helper function to find the best target for a shot-like action.
    It returns the target player object and its calculated priority score.
    """
    s = context["self"]
    core = context["core"]
    best_target = None
    max_score = -1

    # Find all potential targets within one level (shot's default range)
    shotable_players_ids = []
    for i in range(s.place - 1, s.place + 2):
        if i in core.status["pop"]:
            for pl_id in core.status["pop"][i]["sum"]:
                # Cannot target teammates (unless they are human) or self
                if core.PlDict[pl_id].team == s.team and not core.PlDict[pl_id].real:
                    continue
                if pl_id == s.id:
                    continue
                shotable_players_ids.append(pl_id)

    if not shotable_players_ids:
        return None, 0


    for target_id in shotable_players_ids:
        target_pl = core.PlDict[target_id]
        hp_score = 60 / (target_pl.HP + 0.1)
        energy_score = (target_pl.energy ** 1.5) * 25
        human_bonus = 75 if target_pl.real else 0

        score = hp_score + energy_score + human_bonus

        if score > max_score:
            max_score = score
            best_target = target_pl

    return best_target, max_score

def free_of_charge(act):
    return 0

def able_forever(context):
    """Ability check for actions that are always available."""
    return True

def wave_price(act):
    return 6

