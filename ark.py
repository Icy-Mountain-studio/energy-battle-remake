"""
Project Ark: The Frontend for Energy Battle - Remake

Having the Noah backend isn't enough.
We need a frontend as elegant as the Noah backend: ark.py
I hereby name it the Ark Frontend!

Together, they create:
Energy Battle - Remake v1.2-6

This is a turn-based, many-vs-many combat game with a command-line interface.

The project has undergone two complete rewrites since its inception:
Energy Battle -> Energy Battle-Remake 1.1 -> Energy Battle-Remake 1.2

Energy Battle-Remake 1.2 utilizes my newly developed game kernel,
which I call the "Noah Kernel".

As you can see, the project is still far from complete.

Project initiated: 2025.8.2
Last updated: 2025.10.6
"""

import noah  # Import the Noah kernel, with all due ceremony.
from noah import C
from localize import Expression


# A simple, data-driven language selector function.
# It's designed to be easily integrated into the Ark/Noah project structure.
def select_language(expressions: dict, default_lang: str = "en_us") -> str:
    """
    Prompts the user to select a language from the available options.

    This function dynamically generates a menu from the top-level keys of the
    provided 'expressions' dictionary. It handles various user inputs, including
    numbers, language codes, and a default action for pressing Enter.

    Args:
        expressions (dict): The main localization dictionary where keys are language
                            codes (e.g., 'en_us', 'zh_cn').
        default_lang (str): The language code to return when the user just presses Enter.
                            Defaults to 'en_us'.

    Returns:
        str: The selected language code.
    """
    # 1. Extract available language codes from the expressions dictionary.
    available_langs = list(expressions.keys())

    # 2. Build a mapping from user input (both numbers and codes) to language codes.
    #    This makes the input handling very flexible.
    #    Example: {'1': 'en_us', 'en_us': 'en_us', '2': 'zh_cn', 'zh_cn': 'zh_cn'}
    options_map = {}
    prompt_lines = [f"{C['YELLOW']}Please select a language{C['RESET']}"]
    for i, lang_code in enumerate(available_langs):
        # Map the option number (as a string) to the language code.
        option_num = str(i + 1)
        options_map[option_num] = lang_code
        # Also map the code itself, so the user can type 'zh_cn' directly.
        options_map[lang_code] = lang_code

        # Create a user-friendly display name for the prompt.
        # Here we make a simple assumption for the display name.

        lang_name = expressions[lang_code]["/ark/lang_name"]
        prompt_lines.append(f"  {C['YELLOW']}{option_num}. {lang_name}{C['RESET']} / {lang_code}")

    # 3. Construct the final prompt string.
    #    The default language is explicitly mentioned to guide the user.
    default_lang_name = expressions[default_lang]["/ark/lang_name"]
    prompt_lines.append(f"\nPress Enter for {C['YELLOW']}{default_lang_name}{C['RESET']} > ")
    prompt = "\n".join(prompt_lines)

    # 4. Loop until a valid choice is made.
    while True:
        choice = input(prompt).strip().lower()

        # Handle the default case: user presses Enter.
        if not choice:
            print(f"Defaulting to {C['YELLOW']}{default_lang_name}{C['RESET']}.")
            return default_lang

        # Check if the input (e.g., '1' or 'zh_cn') is a valid option.
        if choice in options_map:
            selected_lang = options_map[choice]
            selected_name = expressions[selected_lang]["/ark/lang_name"]
            print(f"Language set to: {C['YELLOW']}{selected_name}{C['RESET']}\n")
            return selected_lang

        # Handle invalid input and re-prompt.
        else:
            print(f"\n{C['RED']}Invalid selection. Please try again.{C['RESET']}\n")



# InitBattleEnv: Initial Battle Environment. A dictionary holding the default parameters for a game session.
InitBattleEnv = {
    "num": 10,      # Total number of players.
    "real": 1,      # Number of human players.
    "map": 1,       # Map size (number of vertical levels above and below the center).
    "initHP": 1,    # Initial HP for each player.
    "shot_distance": 1,    # Range of the 'Shoot' action.
    "wave_distance": 99999,    # Range of the 'Energy Wave' action (effectively infinite).
    "team_size": 1,   # Number of players per AI team (1 means free-for-all).
    "assist_team": 0, # Should the first AI team cooperate with humans? (0=No, 1=Yes).
    "setting_options":  {
        "1": "num",
        "2": "real",
        "3": "map",
        "4": "initHP",
        "5": "shot_distance",
        "6": "wave_distance",
        "7": "team_size",
        "8": "assist_team",
        "t1": "tweak_hp",
        "t2": "tweak_energy",
        "t3": "tweak_place",
        "t4": "tweak_team",
    },

    # ===== New: tweak =====
    "tweaks": [],  # Store all the tweak events

    "tweak_args": {
        "tweak_hp": ["target_id", "hp_change"],
        "tweak_energy": ["target_id", "energy_change"],
        "tweak_place": ["target_id", "new_place"],
        "tweak_team": ["target_id", "NewTeamID"],
    },
}


def execute_hp_tweak(PipeData, args):
    core = args
    try:
        target_id = int(PipeData["target_id"])
        hp_change = int(PipeData["hp_change"])

        if target_id in core.PlDict:
            core.PlDict[target_id].HP += hp_change
            core.ui.out("/ark/tweak/hp/success", imp=[target_id, hp_change, core.PlDict[target_id].HP])
        else:
            core.ui.out("/ark/tweak/error/player-not-found", imp=[target_id], color="RED")
    except (ValueError, KeyError) as e:
        core.RaiseError("execute_hp_tweak", f"Invalid parameters: {e}")

    return PipeData


def execute_energy_tweak(PipeData, args):
    core = args
    try:
        target_id = int(PipeData["target_id"])
        energy_change = int(PipeData["energy_change"])

        if target_id in core.PlDict:
            core.PlDict[target_id].energy += energy_change
            if core.PlDict[target_id].energy < 0:
                core.PlDict[target_id].energy = 0
            core.ui.out("/ark/tweak/energy/success", imp=[target_id, energy_change, core.PlDict[target_id].energy])
        else:
            core.ui.out("/ark/tweak/error/player-not-found", imp=[target_id], color="RED")
    except (ValueError, KeyError) as e:
        core.RaiseError("execute_energy_tweak", f"Invalid parameters: {e}")

    return PipeData

def execute_place_tweak(PipeData, args):
    core = args
    try:
        target_id = int(PipeData["target_id"])
        new_place = int(PipeData["new_place"])

        if target_id in core.PlDict:
            if abs(new_place) <= core.BattleEnv["map"]:
                core.PlDict[target_id].place = new_place
                core.ui.out("/ark/tweak/place/success", imp=[target_id, new_place])
            else:
                core.ui.out("/ark/tweak/error/out-of-map", imp=[new_place], color="RED")
        else:
            core.ui.out("/ark/tweak/error/player-not-found", imp=[target_id], color="RED")
    except (ValueError, KeyError) as e:
        core.RaiseError("execute_place_tweak", f"Invalid parameters: {e}")

    return PipeData


def execute_team_tweak(PipeData, args):
    core = args
    try:
        target_id = int(PipeData["target_id"])
        NewTeamID = int(PipeData["NewTeamID"])

        if target_id in core.PlDict:
            core.PlDict[target_id].team = NewTeamID
            core.ui.out("/ark/tweak/team/success", imp=[target_id, NewTeamID, core.PlDict[target_id].HP])
        else:
            core.ui.out("/ark/tweak/error/player-not-found", imp=[target_id], color="RED")
    except (ValueError, KeyError) as e:
        core.RaiseError("execute_team_tweak", f"Invalid parameters: {e}")

    return PipeData


# --- Action Logic Functions ---
# These functions define the behavior of each action in the game.
# They are structured to be passed into the Noah Kernel's ActDict.
# Suffix `_s` stands for "Selection Phase" logic.
# Suffix `_d` stands for "Resolution Phase" (Deal) logic.

def charge_s(pl, core, auto):
    """Selection logic for the 'Charge' action."""
    return (True, noah.Act(pl.id, "1"))

def charge_d(PipeData, args):
    """Resolution logic for the 'Charge' action."""
    act, core = args
    act.pay(core)
    pl = core.PlDict[act.ownerID]

    if pl.real:
        core.ui.typing_delay = core.org_delay*2.5
    core.ui.out("./dealed", imp=[act.ownerID, core.PlDict[act.ownerID].energy])
    if pl.real:
        core.ui.typing_delay = 0
        noah.time.sleep(0.3)

    return None

def get_seth(place1, place2):
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

def shot_s(pl, core, auto):
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
                    elif tg.team == s.team and not (tg.real and tg.id!=s.id):
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
                        seth = get_seth(s.place, core.status["snap"][int(target)][2])
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

    else: # --- AI Logic ---
        # 1. Efficiently find a target from the pre-calculated status cache.
        shotable = []
        for i in range(s.place - 1, s.place + 2):
            if i in core.status["pop"]:
                shotable += core.status["pop"][i]["sum"]

        target = pl.id
        _tg = core.status["snap"][target]
        # Ensure the AI doesn't target itself or a teammate.
        while _tg[3] == pl.team and ((not pl.real) or target==pl.id):
            target = noah.random.choice(shotable)
            _tg = core.status["snap"][target]
            shotable.remove(target)

        act = noah.Act(s.id, "2")
        act.lv = 3

        # Calculate the maximum affordable firepower.
        while core.ActDict["2"]["price"](act) > s.energy:
            act.lv -= 1
            if act.lv < 1:
                core.RaiseError("shot_s", f"shot_price might wemt wrong (in P{pl.id}'s selection)")
                break

        # Defensive programming: ensure AI doesn't shoot with 0 energy,
        # even though the 'able' function should prevent this.
        if act.lv <= 0:
            core.RaiseError("shot_s", f"Player {pl.id} could not afford shotting but selected it automatically")
            return (False, None)


        act.target = int(target)
        act.seth = get_seth(s.place, core.status["snap"][target][2])
        act.channel = "shot-like"
        act.dealed = []
        act.color = "RED"
        act.distant = core.BattleEnv["shot_distance"]

        return (True, act)

# --- 'd_exec' Pipeline Functions for Shot-Like Actions ---
# These functions are executed in sequence during the resolution phase.
# The `PipeData` dictionary is passed from one function to the next.

def firecount(myself, PipeData, core, act, target=False):
    """
    Helper function to calculate hits and misses for a single attacker against one or more targets.
    This can be reused by both 'Shoot' and 'Energy Wave'.
    """
    for pos in myself.acts:
        cur_act = core.ActSign[core.ActDict[pos[0]]["priority"]][pos[0]][pos[1]]
        cur_act.pay(core)

        if cur_act.channel == "shot-like" and not cur_act.acted:
            if not target:
                target = core.PlDict[cur_act.target]

            if target.id not in cur_act.dealed:
                is_miss = (cur_act.seth != get_seth(myself.place, target.place) or
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
                cur_act.dealed.append(target.id)
    return PipeData

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

def crossfire_wave_eval(PipeData, args):
    """Pipeline Step 1 (for Wave): Evaluate hits on all players in the path."""
    act, core = args
    myself = core.PlDict[act.ownerID]

    # This function initiates the data stream for a wave action.
    PipeData = {"msg": [], "damage": {}}
    PipeData["msg"].append(["./battle", [myself.id, myself.place, act.seth]])
    PipeData["msg"].append(["/share/endl", []])

    for pl in core.PlDict.values():
        is_target = ((pl.real and pl != myself) or myself.team != pl.team) and \
                        get_seth(myself.place, pl.place) == act.seth
        if is_target:
            PipeData = firecount(myself, PipeData, core, act, pl)

    PipeData["msg"].append(["/share/endl", []])
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
                if cur_act.channel == "shot-like" and not cur_act.acted and attacker.id not in cur_act.dealed:
                    if (cur_act.target is True or cur_act.target == attacker.id):
                        myself = core.PlDict[playerID]
                        is_miss = (cur_act.seth != get_seth(myself.place, attacker.place) or
                                   abs(myself.place - attacker.place) > cur_act.distant)
                        if is_miss:
                            msg.append([f"/act/{cur_act.key}/shot-miss", [playerID, attacker.id, cur_act.lv]])
                        else:
                            # Both sides hit, projectiles crash.
                            msg.append([f"/act/{cur_act.key}/anti", [playerID, attacker.id, cur_act.lv]])
                            crash_amount = min(cur_act.lv, PipeData["damage"][playerID])
                            msg.append([f"/act/{cur_act.key}/crash", [crash_amount]])
                            PipeData["damage"][playerID] -= cur_act.lv

                        cur_act.dealed.append(attacker.id)
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
            core.ui.out(msg[0], imp=msg[1], color=act.color)
        if len(PipeData["msg"]) >= 4:
            core.ui.out("./wonderful", color="MAGENTA")
        core.ui.indent -= 1

    core.ui.typing_delay = 0
    act.pay(core)
    return None

def defend_s(pl, core, auto):
    """Selection logic for the 'Defend' action."""
    return (True, noah.Act(pl.id, "3"))

def defend_d(PipeData, args):
    """Resolution logic for the 'Defend' action."""
    act, core = args
    act.pay(core)
    pl = core.PlDict[act.ownerID]
    pl.status["defend"] = True

    if pl.real:
        core.ui.typing_delay = core.org_delay*2.5
    core.ui.out("./dealed", imp=[act.ownerID])
    if pl.real:
        core.ui.typing_delay = 0
        noah.time.sleep(0.3)
    return None

def move_s(pl, core, auto):
    """Selection logic for the 'Move' action."""
    if not auto: # Human logic
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
    else: # AI logic
        ls = list(range(-core.ActDict["4"]["step"], core.ActDict["4"]["step"] + 1))
        ls.remove(0) # AI should always move.

        st = noah.random.choice(ls)
        # Ensure the move is within map boundaries.
        while abs(st + pl.place) > core.BattleEnv["map"]:
            st = noah.random.choice(ls)

        act = noah.Act(pl.id, "4")
        act.steps = st
        return (True, act)

def blackhole_s(pl, core, auto):
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
            return (True, act)

        else: # AI Logic
            available_targets = []
            for i in core.status["pop"].keys():
                if i != "all":
                    available_targets += core.status["pop"][i]["sum"]

            target = pl.id
            _tg = core.status["snap"][target]
            while _tg[3] == pl.team and ((not pl.real) or target == pl.id):
                available_targets.remove(target)
                target = noah.random.choice(available_targets)
                _tg = core.status["snap"][target]

            act.target = target
            return (True, act)

    elif not auto:
        core.ui.indent += 1
        core.ui.out("/share/poor", color='MAGENTA')
        core.ui.indent -= 1
        return (False, None)

    else:
        core.RaiseError("wave_s", f"Player {pl.id} can't afford blackhole but selected it")
        return (False, None)


def blackhole_d(PipeData, args):
    """Resolution logic for 'Black Hole'."""
    act, core = args
    act.pay(core)
    target = core.PlDict[act.target]
    myself = core.PlDict[act.ownerID]

    if target.real or myself.real:
        core.ui.typing_delay = core.org_delay*5

    # Add the target's chosen actions to their 'unable' list.
    block = [i[0] for i in target.acts]
    target.unable += block

    # Mark the target's actions as already acted to prevent them from resolving.
    for pos in target.acts:
        core.ActSign[core.ActDict[pos[0]]["priority"]][pos[0]][pos[1]].acted = True

    block_out = ", ".join([core.ui.get(f"/act/{i}/name") for i in block])
    core.ui.out("./result", imp=[target.id, block_out, act.ownerID])

    if target.real or myself.real:
        core.ui.typing_delay = 0
        noah.time.sleep(0.3)

    return None


def move_d(PipeData, args):
    """Resolution logic for the 'Move' action."""
    act, core = args
    act.pay(core)
    st = act.steps
    pl = core.PlDict[act.ownerID]
    pl.place += st  # Perform the move.

    if abs(pl.place) > core.BattleEnv["map"]:
        core.RaiseError("move_d", f"Player {pl.id} is out of map, in place {pl.place}")

    if pl.real:
        core.ui.typing_delay = core.org_delay*2.5
    core.ui.out("./dealed", imp=[act.ownerID, st, pl.place])
    if pl.real:
        core.ui.typing_delay = 0
        noah.time.sleep(0.3)
    return None


def auto_AOEseth(pl, core):
    """
    AI helper to determine the optimal direction for an AOE attack.
    It scans the battlefield to find the direction with the most enemies.
    """
    tree_seth = [0, 0, 0] # [-1 (down), 0 (straight), 1 (up)]
    for place, pls in core.status["pop"].items():
        if place != "all":
            if place > pl.place: # Above player
                tree_seth[2] += len(pls["sum"])
                if not pl.real: tree_seth[2] -= len(pls.get(pl.team, []))
            elif place == pl.place: # Same level
                tree_seth[1] += len(pls["sum"])
                if not pl.real: tree_seth[1] -= len(pls.get(pl.team, []))
            else: # Below player
                tree_seth[0] += len(pls["sum"])
                if not pl.real: tree_seth[0] -= len(pls.get(pl.team, []))

    return tree_seth.index(max(tree_seth)) - 1

def wave_s(pl, core, auto):
    """Selection logic for the 'Energy Wave' action."""
    act = noah.Act(pl.id, "6")

    if pl.energy < core.ActDict["6"]["price"](act):
        if not auto:
            core.ui.indent += 1
            core.ui.out(["/share/poor", "/share/endl"], color='MAGENTA')
            core.ui.indent -= 1
        else:
            core.RaiseError("wave_s", f"Player {pl.id} can't afford wave but selected it")
        return (False, None)

    elif not auto: # Human Logic
        core.ui.indent += 1
        while True:
            seth = core.ui.inp('./ask-seth')
            if seth == " ": # Cancel option
                core.ui.out(["./cancel", "/share/endl"])
                core.ui.indent -= 1
                return (False, None)
            try:
                if seth != "":
                    if int(seth) not in [-1, 0, 1]:
                        core.ui.out("./error-no-seth")
                        continue
                else: # Auto-calculate direction
                    seth = auto_AOEseth(pl, core)
                    core.ui.out("./auto-seth", imp=[seth])
            except ValueError:
                core.ui.out("./error-int-or-empty")
                continue
            core.ui.out('/share/endl')
            break

        act.seth = int(seth)
        core.ui.typing_delay *= 10
        core.ui.out('./has-sent')
        core.ui.typing_delay /= 10
        core.ui.indent -= 1

    elif auto: # AI Logic
        act.seth = auto_AOEseth(pl, core)

    # Set properties for the resolution pipeline.
    act.target = True # Indicates an AOE attack
    act.lv = 5
    act.channel = "shot-like"
    act.dealed = []
    act.color = "CYAN"
    act.distant = core.BattleEnv["wave_distance"]
    return (True, act)

# --- Action Price, Ability, and AI Weight Functions ---

def charge_price(act): return -1
def shot_price(act): return act.lv
def reflect_price(act): return 1
def blackhole_price(act): return 3
def wave_price(act): return 4
def free_of_charge(act): return 0


def able_forever(context):
    """Ability check for actions that are always available."""
    return True

def shot_able(context):
    """Ability check for 'Shoot'."""
    return (context["self"].energy >= 1) and (context["side_enm"] > 0)

def move_able(context):
    """Ability check for 'Move'."""
    return context["core"].BattleEnv["map"] > 0

def blackhole_able(context):
    """Ability check for 'Black Hole'."""
    return (context["self"].energy >= 3)

def reflect_able(context):
    """Ability check for 'Reflect'."""
    return (context["self"].energy >= 2)

def wave_able(context):
    """Ability check for 'Energy Wave'."""
    return (context["self"].energy >= 4)

def charge_ai(context):
    """AI weight for 'Charge'."""
    return min((100/(context["self"].energy+1))*3, 500)

def shot_ai(context):
    """AI weight for 'Shoot'."""
    return context["self"].energy*50

def defend_ai(context):
    """AI weight for 'Defend'."""
    return context["engK"]*context["engK"]*100+10

def move_ai(context):
    """AI weight for 'Move'."""
    return context["enmK"]*context["engK"]*50+10

def blackhole_ai(context):
    """AI weight for 'Black Hole'."""
    return context["self"].energy*40

def reflect_ai(context):
    """AI weight for 'Reflect'."""
    return context["engK"]*30+10

def wave_ai(context):
    """AI weight for 'Energy Wave'."""
    return context["self"].energy*100

def reflect_s(pl, core, auto):
    """Selection logic for 'Reflect'."""
    act = noah.Act(pl.id, "5")
    if pl.energy >= core.ActDict["5"]["price"](act):
        return (True, noah.Act(pl.id, "5"))
    else:
        if not auto:
            core.ui.indent += 1
            core.ui.out(["/share/poor", "/share/endl"])
            core.ui.indent -= 1
        return (False, None)

def reflect_d(PipeData, args):
    """Resolution logic for 'Reflect'."""
    act, core = args
    act.pay(core)
    pl = core.PlDict[act.ownerID]
    pl.status["reflect"] = True # reflect status
    if pl.real:
        core.ui.typing_delay = core.org_delay*2.5
    core.ui.out("./dealed", imp=[act.ownerID])
    if pl.real:
        core.ui.typing_delay = 0
        noah.time.sleep(0.3)

def ShowRules_s(pl, core, auto):
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

def ShowStatus_s(pl, core, auto):
    """Selection logic for 'ShowStatus' (human-only utility action)."""
    core.ui.indent += 1
    all_teams = [i[3] for i in core.status["snap"].values()]
    ask = core.ui.inp('./select-team')
    try:
        selected_team_ids = [int(ask)]
    except ValueError:
        selected_team_ids = list(set(all_teams)) # Show all teams if input is invalid/empty

    show_pls = []
    for i in core.PlDict.values():
        if i.team in selected_team_ids:
            show_pls.append((i.id, i.HP, i.energy, i.place, i.outd, len(i.kills)))

    org = core.ui.typing_delay
    core.ui.typing_delay = 0
    for s in show_pls:
        core.ui.out('./main-exp', imp=s, color="YELLOW")
    core.ui.out('/share/endl')
    core.ui.typing_delay = org
    core.ui.indent -= 1

    return (False, None)

def break_s(pl, core, auto):
    """Selection logic for 'Surrender'."""
    core.exit_game = True
    return (True, None)


# Terminal check
try:
    from terminal_check import show_check_result
    if not show_check_result():
        quit()
except ImportError:
    pass  # Skip if module not found


# ArkUI is the UI instance managed by the frontend, distinct from core.ui.
# You can select a language here
chosen_lang_code = select_language(Expression)
noah.time.sleep(0.3)
noah.clear_screen()

chosen_lang = Expression[chosen_lang_code]
ArkUI = noah.IO(chosen_lang, delay=float(chosen_lang['/core/typing-delay'])*0.01)

ArkUI.workdir = "/ark/"
ArkUI.out("./welcome", color="YELLOW")

# The master Action Dictionary that defines the entire game's mechanics for the Noah Kernel.
BaseActDict = {
    "1": { # Charge
        "price": charge_price, "priority": 0, "able": able_forever,
        "human_only": False, "ai": charge_ai, "weight": 1,
        "s_exec": charge_s, "d_exec": [charge_d],
    },
    "2": { # Shoot
        "price": shot_price, "priority": -1, "able": shot_able,
        "human_only": False, "ai": shot_ai, "weight": 1,
        "s_exec": shot_s,
        "d_exec": [crossfire_evaluate, crossfire_crash, crossfire_reflect, crossfire_defend, crossfire_final],
    },
    "3": { # Defend
        "price": free_of_charge, "priority": 2, "able": able_forever,
        "human_only": False, "ai": defend_ai, "weight": 1,
        "s_exec": defend_s, "d_exec": [defend_d],
    },
    "4": { # Move
        "price": free_of_charge, "priority": 1, "able": move_able,
        "human_only": False, "ai": move_ai, "weight": 1,
        "s_exec": move_s, "d_exec": [move_d],
        "step": 1 # Custom parameter for this action
    },
    "5": { # Reflect
        "price": reflect_price, "priority": 2, "able": reflect_able,
        "human_only": False, "ai": reflect_ai, "weight": 1,
        "s_exec": reflect_s, "d_exec": [reflect_d],
    },
    "6": { # Energy Wave
        "price": wave_price, "priority": -1, "able": wave_able,
        "human_only": False, "ai": wave_ai, "weight": 1,
        "s_exec": wave_s,
        "d_exec": [crossfire_wave_eval, crossfire_crash, crossfire_reflect, crossfire_defend, crossfire_final],
    },
    "7": { # Black Hole
        "price": blackhole_price, "priority": 9999, "able": blackhole_able,
        "human_only": False, "ai": blackhole_ai, "weight": 1,
        "s_exec": blackhole_s, "d_exec": [blackhole_d],
    },
    "rl": { # Show Rules
        "price": free_of_charge, "priority": 0, "able": able_forever,
        "human_only": True, "ai": None, "weight": 0,
        "s_exec": ShowRules_s, "d_exec": [],
    },
    "stt": { # Show Status
        "price": free_of_charge, "priority": 0, "able": able_forever,
        "human_only": True, "ai": None, "weight": 0,
        "s_exec": ShowStatus_s, "d_exec": [],
    },
    "bk": { # Surrender/Break
        "price": free_of_charge, "priority": 0, "able": able_forever,
        "human_only": True, "ai": None, "weight": 0,
        "s_exec": break_s, "d_exec": [],
    },
}



def validate_int(PipeData, args):
    core, ArkUI = args
    if PipeData["error"]:
        return PipeData

    try:
        PipeData["value"] = int(PipeData["value"])
        return PipeData
    except ValueError:
        PipeData["error"] = "/ark/setting/error-not-int"
        PipeData["success"] = False
        return PipeData


def validate_non_negative(PipeData, args):
    core, ArkUI = args
    if PipeData["error"]:
        return PipeData

    if PipeData["value"] < 0:
        PipeData["error"] = "/ark/setting/error-non-negative"
        PipeData["success"] = False
        return PipeData
    return PipeData


def validate_int_and_non_negative(PipeData, args):
    PipeData = validate_int(PipeData, args)
    PipeData = validate_non_negative(PipeData, args)
    return PipeData


def validate_map_range(PipeData, args):
    """check if the map size reasonable"""
    core, ArkUI = args
    if PipeData["error"] or PipeData["key"] != "map":
        return PipeData

    if PipeData["value"] > 100:
        PipeData["error"] = "/ark/setting/error-map-range"
        PipeData["error_imp"] = [PipeData["value"]]
        PipeData["success"] = False
        return PipeData
    return PipeData


def validate_team_size(PipeData, args):
    """team_size >= 1"""
    core, ArkUI = args
    if PipeData["error"] or PipeData["key"] != "team_size":
        return PipeData

    if PipeData["value"] < 1:
        PipeData["value"] = 1  # auto correct
        PipeData["auto_corrected"] = True
    return PipeData


def post_check_real_num_consistency(PipeData, args):
    """The amount of real player could not greater than the total"""
    core, ArkUI = args
    if PipeData["error"] or PipeData["key"] not in ["num", "real"]:
        return PipeData

    BattleEnv = core.BattleEnv if hasattr(core, 'BattleEnv') else InitBattleEnv

    # temply apply
    temp_env = BattleEnv.copy()
    temp_env[PipeData["key"]] = PipeData["value"]

    if temp_env["real"] > temp_env["num"]:
        # auto correct
        if PipeData["key"] == "real":
            PipeData["value"] = temp_env["num"]
        else:
            # It means that key == "num"
            if temp_env["real"] > PipeData["value"]:
                BattleEnv["real"] = PipeData["value"]
                PipeData["also_updated"] = [
                    ("real", BattleEnv["real"])
                ]

        PipeData["warning"] = "/ark/setting/error-real-num-mismatch"
        PipeData["warning_imp"] = [temp_env["real"], temp_env["num"]]

    return PipeData


def apply_value(PipeData, args):
    """Apply the value to BattleEnv"""
    core, ArkUI = args
    if PipeData["error"]:
        return PipeData

    BattleEnv = core.BattleEnv if hasattr(core, 'BattleEnv') else InitBattleEnv
    BattleEnv[PipeData["key"]] = PipeData["value"]
    PipeData["success"] = True
    return PipeData


def display_result(PipeData, args):
    """Final step: show result"""
    core, ArkUI = args

    if PipeData["error"]:
        ArkUI.out(PipeData["error"], imp=PipeData.get("error_imp", []))
        return PipeData

    setting_name = ArkUI.get(f"/ark/setting/desc/{PipeData['key']}")

    # Show warnings
    if PipeData.get("warning"):
        ArkUI.out(PipeData["warning"], imp=PipeData.get("warning_imp", []))

    # Show updated result
    ArkUI.out("/ark/setting/updated", imp=[setting_name, PipeData["value"]])

    # the "also updated" args
    if PipeData.get("also_updated"):
        for param_key, param_value in PipeData["also_updated"]:
            param_name = ArkUI.get(f"/ark/setting/desc/{param_key}")
            ArkUI.out("/ark/setting/updated", imp=[param_name, param_value])

    return PipeData


def apply_and_display(PipeData, args):
    PipeData = apply_value(PipeData, args)
    PipeData = display_result(PipeData, args)
    return PipeData



def parse_target_ids(input_str: str, max_id: int = 9999) -> list:
    """
    Explain the ID input from user
    - Single ID: "5"
    - Multiple ID: "1,3,5"
    - Range: "1-5"
    - Mixed: "1,3-5,8"
    """
    if not input_str.strip():
        raise ValueError("Input cannot be empty")

    result = set()  # auto remove the repeated ones

    parts = input_str.split(',')

    for part in parts:
        part = part.strip()

        if '-' in part:
            # Deal range
            try:
                start_str, end_str = part.split('-', 1)
                start = int(start_str.strip())
                end = int(end_str.strip())

                if start > end:
                    raise ValueError(f"Range formant error：{part}")

                if start < 1 or end > max_id:
                    raise ValueError(f"ID out of range：{part}")

                # add
                result.update(range(start, end + 1))
            except ValueError as e:
                if "Range formant error" in str(e) or "ID out of range" in str(e):
                    raise
                raise ValueError(f"Range formant error：{part}")
        else:
            # 处理单个ID
            try:
                id_num = int(part)
                if id_num < 1 or id_num > max_id:
                    raise ValueError(f"ID out of range：{id_num}")
                result.add(id_num)
            except ValueError:
                raise ValueError(f"Invalid ID：{part}")

    return sorted(list(result))



def ask_for_tweak_params(tweak_name: str, ArkUI: noah.IO) -> dict:
    params = {}
    arg_list = InitBattleEnv["tweak_args"].get(tweak_name, [])

    ArkUI.workdir = f"/ark/setting/{tweak_name}/args/"
    ArkUI.indent += 1

    for arg_name in arg_list:
        while True:
            try:
                value_str = ArkUI.inp(f"./{arg_name}")

                if arg_name == "target_id":
                    target_ids = parse_target_ids(value_str, max_id=InitBattleEnv["num"])
                    params[arg_name] = target_ids

                    ArkUI.out("/ark/setting/target-parsed", imp=[len(target_ids)], color="GREEN")
                else:
                    value = int(value_str)
                    params[arg_name] = value

                break
            except ValueError as e:
                ArkUI.out("/ark/setting/error-parse", imp=[str(e)], color="RED")

    ArkUI.indent -= 1
    ArkUI.out("/share/endl")

    return params


def create_tweak_event(PipeData, args):
    core, ArkUI = args
    tweak_name = PipeData["key"]

    params = ask_for_tweak_params(tweak_name, ArkUI)

    if "target_id" in params:
        target_ids = params["target_id"]

        for target_id in target_ids:
            single_params = params.copy()
            single_params["target_id"] = target_id

            tweak_event = noah.Event(
                cmd_type=f"-{tweak_name}",
                domain="Setting.Tweak",
                PipeData=single_params
            )

            InitBattleEnv["tweaks"].append(tweak_event)

        PipeData["target_count"] = len(target_ids)
    else:
        tweak_event = noah.Event(
            cmd_type=f"-{tweak_name}",
            domain="Setting.Tweak",
            PipeData=params
        )

        InitBattleEnv["tweaks"].append(tweak_event)
        PipeData["target_count"] = 1

    PipeData["success"] = True
    return PipeData



def display_tweak_result(PipeData, args):
    core, ArkUI = args

    if PipeData["success"]:
        tweak_name = ArkUI.get(f"/ark/setting/desc/{PipeData['key']}")
        target_count = PipeData.get("target_count", 1)

        if target_count > 1:
            ArkUI.out("/ark/setting/tweak-added-batch", imp=[tweak_name, target_count], color="GREEN")
        else:
            ArkUI.out("/ark/setting/tweak-added", imp=[tweak_name], color="GREEN")

    return PipeData



EnvProcessors = {
    "num": {
        "steps": [
            validate_int_and_non_negative,
            post_check_real_num_consistency,
            apply_and_display,
        ]
    },
    "real": {
        "steps": [
            validate_int_and_non_negative,
            post_check_real_num_consistency,
            apply_and_display
        ]
    },
    "map": {
        "steps": [
            validate_int_and_non_negative,
            validate_map_range,
            apply_and_display
        ]
    },
    "initHP": {
        "steps": [validate_int_and_non_negative, apply_and_display]
    },
    "shot_distance": {
        "steps": [validate_int_and_non_negative, apply_and_display]
    },
    "wave_distance": {
        "steps": [validate_int_and_non_negative, apply_and_display]
    },
    "team_size": {
        "steps": [
            validate_int_and_non_negative,
            validate_team_size,
            apply_and_display
        ]
    },
    "assist_team": {
        "steps": [validate_int_and_non_negative, apply_and_display]
    },
    "tweak_hp": {
        "steps": [create_tweak_event, display_tweak_result]
    },
    "tweak_energy": {
        "steps": [create_tweak_event, display_tweak_result]
    },
    "tweak_place": {
        "steps": [create_tweak_event, display_tweak_result]
    },
    "tweak_team": {
        "steps": [create_tweak_event, display_tweak_result]
    },
}


def Setting():
    """A function where player can modify the BattleEnv"""
    global InitBattleEnv

    # Temp core for PipeWorkFlow.We don't need a full core
    class SettingCore:
        def __init__(self):
            self.BattleEnv = InitBattleEnv

    core = SettingCore()

    ArkUI.typing_delay = 0.001
    ArkUI.workdir = "/ark/setting/"
    ArkUI.out("./title")
    ArkUI.out("./intro")

    while True:

        ArkUI.workdir = "/ark/setting/"
        ArkUI.out("./current")

        # 显示当前设置
        display_data = []
        for num, key in InitBattleEnv["setting_options"].items():
            if key in InitBattleEnv.get("tweak_args", {}):
                tweak_count = len([t for t in InitBattleEnv["tweaks"] if t.type == f"-{key}"])
                value_display = f"{C['MAGENTA']}{tweak_count}{ArkUI.get("./tweak-configured")}{C['RESET']}"
            else:
                value_display = f"{C['CYAN']}{InitBattleEnv[key]}{C['RESET']}"

            display_data.append((
                f"{C['YELLOW']}{num}{C['RESET']}",
                ArkUI.get(f"./desc/{key}"),
                value_display
            ))

        ArkUI.out(noah.table(display_data, f"{C['YELLOW']}$0{C['RESET']}. $1 / {C['CYAN']}$2{C['RESET']}"), dr=True)
        ArkUI.out("/share/endl")

        choice = ArkUI.inp("./prompt")
        ArkUI.out("/share/endl")

        if choice == "":
            ArkUI.out("./exit")
            ArkUI.out("/share/endl")
            break

        if choice in InitBattleEnv["setting_options"]:
            setting_key = InitBattleEnv["setting_options"][choice]
            setting_name = ArkUI.get(f"./desc/{setting_key}")

            is_tweak = setting_key in InitBattleEnv.get("tweak_args", {})

            if is_tweak:
                # Tweaks
                ArkUI.out("./tweak-adding", imp=[setting_name], color="CYAN")

                PipeData = {
                    "key": setting_key,
                    "success": False,
                }

            else:
                current_value = InitBattleEnv[setting_key]
                new_value_str = ArkUI.inp("./input-new", imp=[current_value])
                ArkUI.out("/share/endl")

                if new_value_str == "":
                    # Remain the same
                    ArkUI.out("./updated", imp=[setting_name, current_value])
                    ArkUI.out("/share/endl")
                    continue

                # ===== Use PipeWorkFlow to deal the modify =====
                PipeData = {
                    "key": setting_key,
                    "value": new_value_str,
                    "old_value": current_value,
                    "error": None,
                    "success": False,
                    "warning": None,
                }

            # Get the processing stream
            if setting_key in EnvProcessors:
                steps = EnvProcessors[setting_key]["steps"]
            else:
                # Default steam
                steps = [
                    validate_int,
                    validate_non_negative,
                    apply_value,
                    display_result
                ]

            # Conduct the processing
            try:
                OutData = noah.PipeWorkFlow(
                    PipeData=PipeData,
                    steps=steps,
                    args=(core, ArkUI)
                )
            except Exception as e:
                ArkUI.out(f"An unexpected error occurred: {e}", dr=True)

            ArkUI.out("/share/endl")

        else:
            ArkUI.out("./error-invalid-choice")
            ArkUI.out("/share/endl")

    if InitBattleEnv["tweaks"]:
        ArkUI.out("./tweak-summary", imp=[len(InitBattleEnv["tweaks"])], color="YELLOW")

        ArkUI.org_delay = ArkUI.typing_delay
        ArkUI.typing_delay = 0

        for tweak in InitBattleEnv["tweaks"]:
            tweak_type = tweak.type[1:]
            ArkUI.out("./tweak-summary-item", imp=[
                ArkUI.get(f"/ark/setting/desc/{tweak_type}"),
                str(tweak.inp)[1:-1]
            ], color="MAGENTA", indent=1)
        ArkUI.out("/share/endl")

        ArkUI.typing_delay = ArkUI.org_delay

    ArkUI.workdir = "/ark/"



def build_snapshot_status(PipeData, args):
    """
    Builds a snapshot of all players' current state.

    Returns:
        dict: {"snap": {player_id: [HP, energy, place, team], ...}}
    """
    core = args
    snap_status = {}
    for pl in core.PlDict.values():
        snap_status[pl.id] = [pl.HP, pl.energy, pl.place, pl.team]

    PipeData["snap"] = snap_status
    return PipeData


if not noah.os.path.exists("./logs"):
    noah.os.mkdir("logs")


CmdTable = noah.default_cmd_table
CmdTable["-tweak_hp"] = [execute_hp_tweak]
CmdTable["-tweak_energy"] = [execute_energy_tweak]
CmdTable["-tweak_place"] = [execute_place_tweak]
CmdTable["-tweak_team"] = [execute_team_tweak]
CmdTable["-update_status"].append(build_snapshot_status)


def Gaming():
    """This is the main game loop function."""
    timest = noah.time.strftime("%Y-%m-%d_%H-%M-%S")
    core = noah.Core(InitBattleEnv, BaseActDict, noah.IO(ArkUI.exp, logpath=f"./logs/noah_{timest}.gz"))

    core.ui.out(core.battle_env_snapshot(), mode="l", dr=True)

    # Add CmdTable to the core
    core.CmdTable = CmdTable

    core.mk_pldict()
    core.ls_acts()
    core.update_status()

    if InitBattleEnv["tweaks"]:
        core.ui.org_delay = core.ui.typing_delay
        core.ui.typing_delay = 0
        core.ui.out("/ark/tweak/executing", color="CYAN")
        for tweak_event in InitBattleEnv["tweaks"]:
            tweak_event.has_happened = False
            core.EventBus.append(tweak_event)
        core.DealEvents()
        core.ui.out("/ark/tweak/complete", color="GREEN")
        core.ui.out("/share/endl")
        core.ui.typing_delay = core.ui.org_delay


    while True:  # The main turn-based loop.
        core.ui.write_log()
        core.clean_round()
        core.rounds += 1

        org_delay = core.ui.typing_delay
        core.ui.typing_delay = 0
        core.ui.out("/ark/round-title", imp=[core.rounds], color="WHITE")
        core.ui.typing_delay = org_delay

        core.SelectAct()
        if core.exit_game:
            core.ui.out(["/ark/break", "/share/endl"])
            break

        core.DealAct()
        core.rm_deaths()
        core.update_status()

        teams = []
        for place in core.status["pop"].keys():
            if place != "all":
                teams += list(core.status["pop"][place].keys())
        while "sum" in teams:
            teams.remove("sum")
        teams = set(teams)

        if len(teams) <= 1:
            core.ui.typing_delay *= 7
            if teams and 0 not in teams:
                if core.status["pop"]["all"] > 1:
                    core.ui.out("/ark/game-over-by-team", imp=[list(core.PlDict.values())[0].team])
                    break
                elif core.status["pop"]["all"] == 1:
                    core.ui.out("/ark/game-over", imp=[list(core.PlDict.values())[0].id])
                    break

            elif teams and 0 in teams:
                humans_num = 0
                ai_num = 0
                for pl in core.PlDict.values():
                    if pl.real:
                        humans_num += 1
                    else:
                        ai_num += 1
                if ai_num == 0 and humans_num == 1:
                    core.ui.out("/ark/game-over", imp=[list(core.PlDict.values())[0].id])
                    break
                elif ai_num != 0:
                    core.ui.out("/ark/game-over-by-team", imp=[0])
                    break
            else:
                core.ui.out("/ark/game-over-nobody")
                break
            core.ui.typing_delay /= 7

        core.ui.out("/share/endl")

    core.ui.write_log()


def _exit():
    """Function to exit the game gracefully."""
    ArkUI.typing_delay *= 10
    ArkUI.out("./exit")
    return True

# Transition Table: Maps user input from the main menu to corresponding functions.
TransTable = {
    "mode": {
        "1": [ArkUI.get('./opt/1'), Gaming],
        "2": [ArkUI.get('./opt/2'), Setting],
        "3": [ArkUI.get('./opt/3'), _exit],
    }
}

if __name__ == "__main__":

    exit_game = False

    while True: # The session loop (allows playing multiple games).
        # Display main menu options.
        optlist = ArkUI.get('./opt-title')
        optlist += noah.table(
            [(num, show[0]) for num, show in TransTable['mode'].items()], f"{C['YELLOW']}$0{C['RESET']}. $1"
        )
        optlist += "\n"
        ArkUI.out(optlist, dr=True)

        res = ArkUI.inp("> ", dr=True)
        ArkUI.out("/share/endl")

        if res in TransTable['mode']:
            exit_game = TransTable['mode'][res][1]()
        elif res == "": # Default action is to start the game.
            exit_game = TransTable['mode']["1"][1]()
        else:
            ArkUI.out("/share/not-found")
            ArkUI.out("/share/endl")

        if exit_game:
            break

