"""
/Energy-Battle-Remake/ark.py
"""

"""
Project Ark: The Frontend for Energy Battle - Remake

Having the Noah backend isn't enough.
We need a frontend as elegant as the Noah backend: ark.py
I hereby name it the Ark Frontend!

Together, they create:
Energy Battle - Remake v1.2-7

This is a turn-based, many-vs-many combat game with a command-line interface.

The project has undergone two complete rewrites since its inception:
Energy Battle -> Energy Battle-Remake 1.1 -> Energy Battle-Remake 1.2

Energy Battle-Remake 1.2 utilizes my newly developed game kernel,
which I call the "Noah Kernel".

As you can see, the project is still far from complete.

Project initiated: 2025.8.2
Last updated: 2025.10.19
"""

import noah  # Import the Noah kernel, with all due ceremony.
from noah import C
from localize import Expression
import copy


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
    "map": 3,       # Map size (number of vertical levels above and below the center).
    "initHP": 15,    # Initial HP for each player.
    "shot_distance": 1,    # Range of the 'Shoot' action.
    "wave_distance": 3,    # Range of the 'Energy Wave' action (effectively infinite).
    "team_size": 1,   # Number of players per AI team (1 means free-for-all).
    "assist_team": 0, # Should the first AI team cooperate with humans? (0=No, 1=Yes).
    "ai_quality": 0,
    "max_consecutive_defend_times": 1,
    "amount_of_actions_per_round": 2,
    "max_move_speed": 2,  # The max amount of steps a player can move at once by action "move"
    "msg_summary_threshold": 20,
    "setting_options":  {
        "1": "num",
        "2": "real",
        "3": "map",
        "4": "max_move_speed",
        "5": "initHP",
        "6": "shot_distance",
        "7": "wave_distance",
        "8": "team_size",
        "9": "assist_team",
        "10": "ai_quality",
        "11": "max_consecutive_defend_times",
        "12": "amount_of_actions_per_round",
        "13": "msg_summary_threshold",
    },
}


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
ArkUI = noah.IO(chosen_lang, delay=float(chosen_lang['/core/typing-delay'])*0.005)

ArkUI.workdir = "/ark/"
ArkUI.out("./welcome", color="YELLOW")


from actions import BaseActDict


def Setting():
    """A function where player can modify the BattleEnv"""
    global InitBattleEnv

    ArkUI.typing_delay = 0.001
    ArkUI.workdir = "/ark/setting/"
    ArkUI.out("./title")
    ArkUI.out("./intro")

    while True:

        ArkUI.workdir = "/ark/setting/"
        ArkUI.out("./current")

        # Display current settings
        display_data = []
        for num, key in InitBattleEnv["setting_options"].items():
            value_display = f"{C['CYAN']}{InitBattleEnv[key]}{C['RESET']}"

            display_data.append((
                f"{C['YELLOW']}{num}{C['RESET']}",
                ArkUI.get(f"./desc/{key}"),
                value_display
            ))

        ArkUI.out(noah.table(display_data, f"{C['YELLOW']}$0{C['RESET']}. $1 {C['YELLOW']}|{C['RESET']} {C['CYAN']}$2{C['RESET']}"), directly=True)
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
            current_value = InitBattleEnv[setting_key]
            new_value_str = ArkUI.inp("./input-new", imp=[current_value])
            ArkUI.out("/share/endl")

            if new_value_str == "":
                # Remain the same
                ArkUI.out("./updated", imp=[setting_name, current_value])
                ArkUI.out("/share/endl")
                continue
            else:
                try:
                    InitBattleEnv[setting_key] = int(new_value_str)
                except ValueError:
                    ArkUI.out("./error-not-int")

            ArkUI.out("/share/endl")

        else:
            ArkUI.out("./error-invalid-choice")
            ArkUI.out("/share/endl")


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
        snap_status[pl.id] = [pl.HP, pl.energy, pl.place, pl.team, pl.real]

    PipeData["snap"] = snap_status
    return PipeData


def build_able_enmK(PipeData: dict, args: noah.Core) -> dict:
    self = PipeData["self"]
    core = PipeData["core"]

    # --- Environment variable generation for decision making ---
    nearby_places = range(self.place - 1, self.place + 2)

    # --- Safer calculation of nearby enemy population ---
    side_enm = 0
    for i in nearby_places:
        place_pop_stats = core.status["pop"].get(i, {})
        total_pop_at_place = len(place_pop_stats.get("sum", []))
        my_team_pop_at_place = len(place_pop_stats.get(self.team, []))
        side_enm += total_pop_at_place - my_team_pop_at_place

    all_enm = core.status["pop"].get("all", 0)
    enmK = side_enm / all_enm if all_enm > 0 else 0 # Ratio of nearby enemies to total enemies.

    PipeData["side_enm"] = side_enm
    PipeData["all_enm"] = all_enm
    PipeData["nearby_places"] = nearby_places
    PipeData["enmK"] = enmK

    return PipeData


def build_able_engK(PipeData: dict, args: noah.Core) -> dict:
    """Safer calculation of nearby enemy energy"""
    self = PipeData["self"]
    core = PipeData["core"]
    nearby_places = PipeData["nearby_places"]

    side_eng = 0
    for i in nearby_places:
        place_eng_stats = core.status["energy"].get(i, {})
        total_eng_at_place = place_eng_stats.get("sum", 0)
        my_team_eng_at_place = place_eng_stats.get(self.team, 0)
        side_eng += total_eng_at_place - my_team_eng_at_place

    all_eng = core.status["energy"].get("all", 0)
    engK = side_eng / all_eng if all_eng > 0 else 0 # Ratio of nearby enemy energy to total enemy energy.

    PipeData["side_eng"] = side_eng
    PipeData["engK"] = engK
    return PipeData


def build_population_status(PipeData: dict, args: noah.Core) -> dict:
    """
    Builds population statistics required by the Noah Kernel.

    Returns:
        dict: {"pop": {place: {team: [ids], "sum": [ids]}, "all": total}}
    """
    core = args
    pop_status = {}

    for pl in core.PlDict.values():
        if pl.place not in pop_status:
            pop_status[pl.place] = {pl.team: [pl.id], "sum": [pl.id]}
        elif pl.team not in pop_status[pl.place]:
            pop_status[pl.place][pl.team] = [pl.id]
            pop_status[pl.place]["sum"].append(pl.id)
        else:
            pop_status[pl.place][pl.team].append(pl.id)
            pop_status[pl.place]["sum"].append(pl.id)

    pop_status["all"] = len(core.PlDict)
    PipeData["pop"] = pop_status

    return PipeData


def build_energy_status(PipeData, args: noah.Core):
    """
    Builds energy statistics for the Energy Battle game.
    This is game-specific and not required by the Noah Kernel.

    Returns:
        dict: {"energy": {place: {team: total, "sum": total}, "all": total}}
    """
    core = args

    energy_status = {}
    all_energy = 0

    for pl in core.PlDict.values():
        if pl.place not in energy_status:
            energy_status[pl.place] = {pl.team: pl.energy, "sum": pl.energy}
        elif pl.team not in energy_status[pl.place]:
            energy_status[pl.place][pl.team] = pl.energy
            energy_status[pl.place]["sum"] = energy_status[pl.place].get("sum", 0) + pl.energy
        else:
            energy_status[pl.place][pl.team] += pl.energy
            energy_status[pl.place]["sum"] += pl.energy

        all_energy += pl.energy

    energy_status["all"] = all_energy
    PipeData["energy"] = energy_status

    return PipeData


if not noah.os.path.exists("./logs"):
    noah.os.mkdir("logs")


CmdTable = noah.default_cmd_table

CmdTable["-update_status"] += [
    build_population_status,
    build_energy_status,
    build_snapshot_status,
]

CmdTable["-build_able_context"] += [
    build_able_enmK,
    build_able_engK,
]

ModsToLoad = {}

def Gaming():
    """This is the main game loop function."""
    timest = noah.time.strftime("%Y-%m-%d_%H-%M-%S")
    ArkMod = {
        "BattleEnv": InitBattleEnv,
        "ActDict": BaseActDict,
        "ui": noah.IO(ArkUI.exp, logpath=f"./logs/noah_{timest}.gz"),
        "CmdTable": CmdTable,
        "mod_priority": 0,
        "mod_name": "Ark",
        }
    ModsToLoad["Ark"] = copy.deepcopy(ArkMod)

    core = noah.Core(ModsToLoad)

    core.ui.out(core.battle_env_snapshot(), mode="l", directly=True)

    core.mk_pldict()
    core.update_status()

    while True:  # The main turn-based loop.
        core.ui.write_log()
        core.clean_round()
        core.rounds += 1

        core.ui.out(["/share/endl", "/ark/round-title", "/share/endl"], imp=[core.rounds], color="WHITE")

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
    ArkUI.typing_delay = 0.1
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

        original_delay = ArkUI.typing_delay
        ArkUI.typing_delay /= 10
        ArkUI.out(optlist, directly=True, speed_stability=0)
        ArkUI.typing_delay = original_delay

        res = ArkUI.inp("> ", directly=True)
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


