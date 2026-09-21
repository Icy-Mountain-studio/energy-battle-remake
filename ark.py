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


def Setting():
    """A function where player can modify the BattleEnv"""
    ConfiguredBattleEnv = copy.deepcopy(noah.reduce(noah.deep_merge, sorted(ModsToLoad.values(), key=lambda d: d.get("mod_priority", 0)))["BattleEnv"])

    ArkUI.typing_delay = 0.001
    ArkUI.workdir = "/ark/setting/"
    ArkUI.out("./title")
    ArkUI.out("./intro")

    while True:

        ArkUI.workdir = "/ark/setting/"
        ArkUI.out("./current")

        # Display current settings
        display_data = []
        for num, key in ConfiguredBattleEnv["setting_options"].items():
            value_display = f"{C['CYAN']}{ConfiguredBattleEnv[key]}{C['RESET']}"

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

        if choice in ConfiguredBattleEnv["setting_options"]:
            setting_key = ConfiguredBattleEnv["setting_options"][choice]
            setting_name = ArkUI.get(f"./desc/{setting_key}")
            current_value = ConfiguredBattleEnv[setting_key]
            new_value_str = ArkUI.inp("./input-new", imp=[current_value])
            ArkUI.out("/share/endl")

            if new_value_str == "":
                # Remain the same
                ArkUI.out("./updated", imp=[setting_name, current_value])
                ArkUI.out("/share/endl")
                continue
            else:
                try:
                    ConfiguredBattleEnv[setting_key] = int(new_value_str)
                except ValueError:
                    ArkUI.out("./error-not-int")

            ArkUI.out("/share/endl")

        else:
            ArkUI.out("./error-invalid-choice")
            ArkUI.out("/share/endl")

    ModsToLoad["Settings"] = {
        "BattleEnv": ConfiguredBattleEnv,
        "mod_priority": 1,
        "mod_name": "Settings",
        "mod_reload": lambda: None
        }
    
    ArkUI.workdir = "/ark/"


DefaultMods = ["ark_mod.py"]
ModsToLoad = {}

for mod in DefaultMods:
    mod_object = noah.import_module_from_path(mod)
    mod_object.ModContents["chosen_lang_code"] = chosen_lang_code
    ModsToLoad[mod_object.ModContents["mod_name"]] = mod_object.ModContents

def ModManager():
    ArkUI.workdir = "/ark/mod_manager/"
    while True:
        try:
            user_input = ArkUI.inp("./new_mod_path")
            ArkUI.out("/share/endl")
            if user_input:
                new_mod = noah.import_module_from_path(user_input)
            else:
                break

        except FileNotFoundError:
            ArkUI.out(["./file_system_failure", "/share/endl"], color="RED")
            continue
        except Exception as e:
            ArkUI.out(["./import_failure", "/share/endl"], color="RED")
            continue

        try:
            new_mod.ModContents["chosen_lang_code"] = chosen_lang_code
            new_mod.ModContents["mod_reload"]()
            ModsToLoad[new_mod.ModContents["mod_name"]] = new_mod.ModContents
        except (AttributeError, KeyError):
            ArkUI.out(["./metadata_incomplete", "/share/endl"], color="MAGENTA")
            continue

        ArkUI.out(["./succeed", "/share/endl"], imp=[new_mod.ModContents["mod_name"]], color="GREEN")
        break


def Gaming():
    """This is the main game loop function."""
    for Mod in ModsToLoad.values():
        Mod["mod_reload"]()

    core = noah.Core(ModsToLoad)

    core.ui.out(core.battle_env_snapshot(), mode="l", directly=True)

    core.mk_pldict()
    core.update_status()

    while True:  # The main turn-based loop.
        core.RunMainLoop()

        if core.exit_game:
            core.ui.out(["/ark/break", "/share/endl"])
            break

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
        "3": [ArkUI.get('./opt/3'), ModManager],
        "4": [ArkUI.get('./opt/4'), _exit],
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
        ArkUI.workdir = "/ark/"

        if exit_game:
            break


