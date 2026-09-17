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


def firecount(myself, PipeData, core, act, target=False):
    """
    Helper function to calculate hits and misses for a single attacker against one or more targets.
    This can be reused by both 'Shoot' and 'Energy Wave'.
    """
    for pos in myself.acts:
        cur_act = core.ActSign[core.ActDict[pos[0]]["priority"]][pos[0]][pos[1]]
        cur_act.pay(core)

        if cur_act.channel == "shot-like":
            if not target:
                target = core.PlDict[cur_act.target]

            # if target.id > cur_act.ownerID:
            is_miss = (cur_act.seth != get_direction(myself.place, target.place) or
                       abs(myself.place - target.place) > cur_act.distant)

            if is_miss:
                # The shot missed.
                PipeData["msg"].append([f"/act/{cur_act.key}/shot-miss", [myself.id, target.id, cur_act.lv]])
            else:
                # The shot hit.
                PipeData["msg"].append([f"/act/{cur_act.key}/shot", [myself.id, target.id, cur_act.lv]])
                if target.id not in PipeData["damage"]:
                    PipeData["damage"][target.id] = cur_act.lv
                else:
                    PipeData["damage"][target.id] += cur_act.lv

    return PipeData


def crossfire_crash(PipeData, args):
    """Pipeline Step 2: Check for counter-fire and projectile annihilation."""
    act, core = args
    attacker = core.PlDict[act.ownerID]
    msg = []

    for playerID in PipeData["damage"].keys():
        if playerID != attacker.id:
            for pos in core.PlDict[playerID].acts:
                cur_act = core.ActSign[core.ActDict[pos[0]]["priority"]][pos[0]][pos[1]]
                # Check if the target is also performing a shot-like action back at the attacker.
                if cur_act.channel == "shot-like":
                    if (cur_act.target is True or cur_act.target == attacker.id):
                        myself = core.PlDict[playerID]
                        is_miss = (cur_act.seth != get_direction(myself.place, attacker.place) or
                                   abs(myself.place - attacker.place) > cur_act.distant)
                        if is_miss:
                            msg.append([f"/act/{cur_act.key}/shot-miss", [playerID, attacker.id, cur_act.lv]])
                        else:
                            # Both sides hit, projectiles crash.
                            msg.append([f"/act/{cur_act.key}/anti", [playerID, attacker.id, cur_act.lv]])
                            crash_amount = min(cur_act.lv, PipeData["damage"][playerID])
                            msg.append([f"/act/{cur_act.key}/crash", [crash_amount]])
                            PipeData["damage"][playerID] -= cur_act.lv

                        cur_act.pay(core)

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
            PipeData["msg"].append(["./reflect", [act.ownerID, PipeData["damage"][playerID]]])
            if PipeData["damage"][playerID] > 0:
                PipeData["damage"][playerID] *= -1 # Negative damage means it's reflected back
            else:
                PipeData["damage"][playerID] *= 2
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
                PipeData["damage"][playerID] = 0 # Nullify damage
            someone_defend = True

    if someone_defend:
        PipeData["msg"].append(["/share/endl", []])
    return PipeData


def crossfire_final(PipeData, args):
    """Pipeline Step 5: Apply final damage and display results."""
    act, core = args
    attacker = core.PlDict[act.ownerID]

    for playerID, hurt_lv in PipeData["damage"].items():
        tg = core.PlDict[playerID]

        if hurt_lv > 0: # Positive value: target takes damage.
            tg.hurted(hurt_lv, attacker.id, act.key, core)
            PipeData["msg"].append(["./final-hurt", [playerID, hurt_lv, tg.HP]])
        elif hurt_lv < 0: # Negative value: attacker takes reflected damage.
            attacker.hurted(-hurt_lv, tg.id, act.key, core)
            PipeData["msg"].append(["./final-hurt", [attacker.id, -hurt_lv, attacker.HP]])
        else: # Zero damage
            PipeData["msg"].append(["./peace", []])

    # Display the battle log.
    if len(PipeData["msg"]) > 1:
        msg = PipeData["msg"].pop(0)
        core.ui.out("/share/endl")
        core.ui.out(msg[0], imp=msg[1], color=act.color)
        core.ui.indent += 1
        for msg in PipeData["msg"]:
            core.ui.out(msg[0], imp=msg[1], color=act.color, speed_stability=-1000)
        if len(PipeData["msg"]) >= 4:
            core.ui.out("./wonderful", color="MAGENTA")
        core.ui.indent -= 1

    core.ui.typing_delay = 0
    act.pay(core)
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
    return 4

