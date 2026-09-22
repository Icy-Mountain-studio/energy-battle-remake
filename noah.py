from __future__ import annotations

"""
/Energy-Battle-Remake/noah.py
"""

"""
The Noah Kernel: A turn-based game engine.
Originally spun off from the development of the game 'Energy Battle'.

Project initiated: 2025.8.2
Last updated: 2026.9.22
"""

try:
    import readline
except ImportError: # Windows do not have this lib
    pass

import gzip
import sys
import time
import os
import re
import random
from functools import reduce

import importlib.util
from pathlib import Path


# A common trick to enable ANSI escape code support on Windows terminals.
os.system("")


def clear_screen():
    """
    Clears the terminal screen in a cross-platform way.

    It checks the name of the operating system using `os.name` and calls the
    appropriate shell command.
    'nt' corresponds to Windows systems.
    'posix' corresponds to Linux, macOS, and other Unix-like systems.
    """
    # For Windows
    if os.name == 'nt':
        _ = os.system('cls')
    # For macOS and Linux (and other POSIX systems)
    else:
        _ = os.system('clear')


def import_module_from_path(file_path: str):
    """
    Dynamically imports a Python module from a given file path.
    Temporarily adds the module's parent directory to sys.path to allow
    local imports within the mod, while assigning a unique module name
    to avoid collisions when multiple mods share the same file name (e.g. main.py).

    Args:
        file_path (str): The absolute or relative path to the .py file.

    Returns:
        module: The loaded Python module object.
    """
    # 1. Resolve path cross-platform and validate
    mod_path = Path(file_path).resolve()

    if not mod_path.exists() or mod_path.suffix != ".py":
        raise FileNotFoundError(f"Invalid Python module path: {mod_path}")

    dir_path = str(mod_path.parent)

    # Generate a unique module identifier using parent directory and filename
    # to avoid conflicts in sys.modules (e.g., two mods both named 'main.py')
    unique_module_name = f"mod_{abs(hash(dir_path))}_{mod_path.stem}"

    # 2. Temporarily add directory to sys.path to support local dependencies
    path_added = False
    if dir_path not in sys.path:
        sys.path.insert(0, dir_path)
        path_added = True

    try:
        # 3. Create module spec and load module
        spec = importlib.util.spec_from_file_location(
            unique_module_name,
            mod_path
            )

        if spec is None or spec.loader is None:
            raise ImportError(f"Could not load spec for module at: {mod_path}")

        module = importlib.util.module_from_spec(spec)
        sys.modules[unique_module_name] = module
        spec.loader.exec_module(module)

        return module

    finally:
        # 4. Clean up: restore sys.path
        if path_added:
            sys.path.remove(dir_path)

class Override:
    """If data is wrapped by this function, it will directly cover other data during deep_merge"""
    def __init__(self, value):
        self.value = value

def remove_none(obj):
    if isinstance(obj, dict):
        return {k: remove_none(v) for k, v in obj.items() if v is not None}
    elif isinstance(obj, list):
        return [remove_none(item) for item in obj]
    return obj

def deep_merge(low: dict, high: dict):
    """high will cover low"""
    result = {}

    for key, value in low.items():
        if value is not None:
            result[key] = remove_none(value)

    for key, value in high.items():
        if value is None:
            result.pop(key, None)
        elif key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        elif key in result and isinstance(result[key], list) and isinstance(value, list):
            result[key] = result[key] + remove_none(value)
        elif isinstance(value, Override):
            result[key] = value.value
        else:
            result[key] = remove_none(value)

    return result


# --- Color Palette ---
# ANSI escape codes for terminal colors.
C = {
    "RESET": '\033[0m',
    # For titles and highlights.
    "CYAN": '\033[1;36m',
    # For numerical values and key information.
    "YELLOW": '\033[1;33m',
    # For positive feedback and certain actions.
    "GREEN": '\033[1;32m',
    # For negative feedback (damage, errors).
    "RED": '\033[38;5;210m',
    # For AI or system messages.
    "MAGENTA": '\033[1;35m',
    # For general prompts and descriptions.
    "WHITE": '\033[1;37m',
    "GRAY": '\033[38;5;248m',
}


class IO():
    """Defines an IO class for managing input, output, and logging."""

    def __init__(self, exp:dict | None = None, logpath: str = "noah-log.gz", delay: int | float = 0.01):
        """
        Initializes the IO manager.

        Args:
            exp (dict): A dictionary of expression templates.
                        Format: {key1: [line1, line2, ...], ...}
                        where lineX is a string template to be processed by explain().
            logpath (str): The path for storing log files.
        """
        if exp != None:
            self.exp = exp
        else:
            self.exp = {}
        # The current working directory for relative paths in `exp`.
        self.workdir = "/"
        self.history = []   # A history of all inputs and outputs.
        self.logs = []      # A list of messages to be written to a log file.
        self.logpath = logpath

        self.colors = C
        # Tracks the current indentation level for formatted output.
        self.indent = 0
        # Delay for the typewriter effect. Set to 0 to disable.
        self.typing_delay = delay

    def out(self, key, mode: str = "sh", real_end: str = "\n", directly: bool = False, imp: list | None = None, indent: bool = True, color=None, speed_stability: int | float = 3):
        """
        Outputs content to specified channels after evaluating it.

        Args:
            key (str or list): The key(s) for the expression template in `self.exp`, or the direct content if `directly` is True.
            mode (str): A string specifying the output channels.
                        's': standard output (console)
                        'h': history list
                        'l': log list
                        Can be combined, e.g., "shl".
            real_end (str): The character to print at the very end of the output.
            directly (bool): Direct render. If True, treats `key` as the content itself rather than a key to `self.exp`.
            imp (list): A list of values to be imported into the expression template for substitution.
            indent (bool or int): If True, uses the current `self.indent`. If an int, uses that as the indentation level.
                                 If False, no indentation is applied.
            color (str): The key for a color from `self.colors` to apply to the output.
        """
        if not imp:
            imp = []
        if isinstance(key, list):
            # If `key` is a list, output each item in it recursively.
            for k in key:
                self.out(k, mode, real_end, directly, imp,
                         indent, color, speed_stability)
        else:
            # Determine indentation prefix.
            if indent is True:
                indent_spaces = (self.indent * 4) * " "
            elif isinstance(indent, int):
                indent_spaces = (indent * 4) * " "
            else:
                indent_spaces = ""

            # Evaluate the final string to be printed.
            if directly:
                orinal_result = explain(key, imp)
            else:
                # Resolve path and get the expression template.
                orinal_result = explain(self.get(key), imp)

            if orinal_result != "NONE":
                # Result with indentation for logging/history.
                # indented_result = indent_spaces + orinal_result
                indented_result = orinal_result.replace("\n", "\n"+indent_spaces)
                full_format_result = indented_result

                if color:
                    full_format_result = self.colors.get(
                        color, "") + indented_result + self.colors["RESET"]

                # Output to the specified channels.
                if "s" in mode:
                    if indent_spaces:
                        print(indent_spaces, end="")
                    if self.typing_delay > 0:
                        self._typewriter_print(full_format_result, speed_stability)
                        print(end=real_end)
                    else:
                        print(full_format_result, end=real_end)

                if "h" in mode:
                    self.history.append(full_format_result)
                if "l" in mode:
                    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                    self.logs.append(f"{timestamp}\n{orinal_result}\n")

    def write_log(self):
        try:
            with gzip.open(self.logpath, 'ab') as f:
                # need to encode the string
                f.write(("\n".join(self.logs) + '\n').encode('utf-8'))
        except PermissionError:
            pass

        self.logs.clear()

    def inp(self, key, mode="sh", directly=False, imp=[], indent=True, color=None):
        """
        Prompts the user for input after printing a message, and returns the result.
        The user's response is appended to the message in the history/log.

        Args:
            (See self.out for argument descriptions)

        Returns:
            str: The user's input.
        """
        self.out(key, mode, real_end="", directly=directly,
                 imp=imp, indent=indent, color=color)
        res = input()
        if "h" in mode and self.history:
            self.history[-1] += res
        if "l" in mode and self.logs:
            self.logs[-1] += res

        return res

    def dealpath(self, path):
        """
        Resolves a relative path for the expression table into an absolute path
        based on the current working directory (`self.workdir`).
        """
        if path.startswith('.'):
            # It's a relative path.
            full_path = self.workdir + path[1:]
        else:
            # It's already an absolute path.
            full_path = path

        if "//" in full_path:
            full_path = full_path.replace("//", "/")

        return full_path

    def get(self, key):
        """A simple getter to retrieve an expression template using a resolved path."""
        try:
            return self.exp[self.dealpath(key)]
        except KeyError:
            return "<haven't translated>"

    def _typewriter_print(self, text: str, speed_stability=0):
        """Prints text character by character with a typewriter effect,
        skipping ANSI escape codes."""
        ansi_pattern = re.compile(r'\033\[[0-9;]*m')

        length = len(text)
        i = 0
        while i < length:
            match = ansi_pattern.match(text, i)
            if match:
                sys.stdout.write(match.group())
                sys.stdout.flush()
                i = match.end()
            else:
                sys.stdout.write(text[i])
                sys.stdout.flush()
                i += 1
                if self.typing_delay:
                    if speed_stability:
                        time.sleep(self.typing_delay / i**(1/speed_stability))
                    else:
                        time.sleep(self.typing_delay)


def explain(template_str: str, values: list) -> str:
    """
    A simple yet effective template engine that replaces placeholders like $0, $1, etc.,
    with values from a list. It uses re.sub for a safe, single-pass replacement.
    This approach is chosen over f-strings for its ability to handle dynamic, runtime substitutions.

    Args:
        template_str (str): The string containing placeholders (e.g., "Player $0 has $1 HP.").
        values (list): A list of values to substitute into the template.

    Returns:
        str: The formatted string.
    """
    def replacer(match):
        """
        This inner function is the brain of the replacement logic, called by re.sub for each match.
        """
        # match.group(1) captures the digits inside the parentheses of the regex.
        # e.g., for a match on "$12", match.group(1) will be "12".
        try:
            index = int(match.group(1))
            # Robustness check: return the value if the index is valid.
            if 0 <= index < len(values):
                return str(values[index])
            else:
                # If the index is out of bounds, return the original placeholder to avoid errors.
                # match.group(0) is the full matched string, e.g., "$12".
                return match.group(0)
        except (ValueError, IndexError):
            # In case of any conversion error, also return the original placeholder.
            return match.group(0)

    # The regex r'\$(\d+)' finds a literal '$' followed by one or more digits.
    # The parentheses (\d+) create a capture group for the digits.
    return re.sub(r'\$(\d+)', replacer, template_str)


def table(data: list[list] | list[tuple], exp: str, spl: str ="\n") -> str:
    """
    Generates a formatted string table from data using an expression template.

    Args:
        data (list of lists/tuples): The data to format, where each inner list is a row.
        exp (str): The expression template for each row.
        spl (str): The separator to join the rows with.

    Returns:
        str: The formatted table as a single string.
    """
    return spl.join([explain(exp, i) for i in data])


class Player():
    """The main entity of the game: a Player."""

    def __init__(self, id: int):
        self.id = id           # Unique identifier for the player.
        self.energy = 0        # Current amount of energy the player possesses.
        self.HP = 1            # Current health points.
        # The player's current location/level in the game world.
        self.place = 0
        self.ai_quality = 0    # The quality of the player's ai strategy logic.
        # A blacklist of action names this player cannot use.
        self.unable = []
        self.real = True       # True if this is a human player, False for AI.
        self.outd = 0          # Total damage dealt by this player.
        # Log of HP changes: [[damage, source_id, action_name], ...].
        self.HPlog = []
        self.kills = []        # List of player IDs killed by this player.

        # Status varibles that resets every turn.For example, defend for one turn.
        self.status = {}

        # The ID of the AI team this player belongs to.
        # 0 is reserved for human players or AI allied with humans.
        self.team = 0

        # A list of selected actions and their parameters for the current turn. Cleared each turn.
        # Format: [[action_key<str>, action_sign_index<int>], ...]
        self.acts = []

    def select(self, core: Core) -> list[Act]:
        """
        Allows the player to select an action, which generates and returns Act objects.
        This method handles the selection logic for both human and AI players.

        Args:
            core (Core): The main game core instance.
            decision (str, optional): The pre-determined action for an AI, or a suggestion for a human.

        Returns:
            list: A list of `Act` objects created from the player's selection.
        """
        result = []
        if self.real:
            core.ls_acts()

        while len(result) < core.BattleEnv["amount_of_actions_per_round"]:
            auto = not self.real
            able_actions, ai_weights = self.evaluate_ability_and_weights(core)
            if not able_actions:
                # No actions avaliable
                core.deaths.append(self.id)
                break

            if self.real:
                decision = able_actions[ai_weights.index(max(ai_weights))]

                if core.BattleEnv["amount_of_actions_per_round"] > 1:
                    # Prompt human player for input.
                    prompt_imp = [self.id, self.HP, self.energy, self.place, core.ui.get(
                        f"/act/{decision}/name"), len(result), core.BattleEnv["amount_of_actions_per_round"]]
                    selection = core.ui.inp(
                        '/core/ask-for-act-multi', imp=prompt_imp)
                else:
                    prompt_imp = [self.id, self.HP, self.energy,
                                  self.place, core.ui.get(f"/act/{decision}/name")]
                    selection = core.ui.inp(
                        '/core/ask-for-act', imp=prompt_imp)

                if selection == "":
                    # If human player presses Enter, accept the suggested decision.
                    selection = decision
                    auto = True
                    # Slow down typing to make it clear the choice was automated.
                    core.ui.typing_delay *= 3
                    core.ui.out('/core/selected',
                                imp=[core.ui.get(f"/act/{selection}/name")])
                    core.ui.typing_delay /= 3
                    time.sleep(0.5)

                if selection not in core.ActDict:
                    core.ui.out(
                        ['/share/not-found', '/share/endl'], color="RED")
                    continue

                if selection in self.unable:
                    core.ui.out(['/share/unable', '/share/endl'])
                    continue

                core.ui.out('/share/endl')
            else:
                # AI player uses the pre-determined decision.
                # selection = decision
                try:
                    selection = random.choices(
                        population=able_actions, weights=ai_weights, k=1)[0]
                except ValueError:
                    core.deaths.append(self.id)
                    break

            if core.ui:
                # Set the working directory for IO to the context of the selected action.
                core.ui.workdir = f"/act/{selection}"

            # Execute the selection function (`selecting_exec`) of the chosen action.
            quit_selecting, new_act = core.ActDict[selection]["selecting_exec"](
                self, core, auto)

            if new_act:
                result.append(new_act)

            elif not self.real:
                core.RaiseError("Player.select", f"AI Player {
                                self.id} didn't get any act object from selected act {selection}")

            if core.exit_game:
                break

            if quit_selecting:
                continue
            elif not self.real:
                core.RaiseError("Player.select", f"Act {selection} let P{
                                self.id}(AI) go into selection loop")
                break

        return result

    def hurted(self, decrease: int | float, origin: int, act_key: str, core: Core):
        """
        The standard method for a player to take damage and log the event.

        Args:
            decrease (int): The amount of HP to reduce.
            origin (int): The ID of the player who caused the damage.
            act_key (str): The key of the action that caused the damage.
            core (Core): The main game core instance.
        """
        if decrease >= self.HP:
            # Prevents HP from going negative and logs exact lethal damage.
            decrease = self.HP
            self.HP = 0
        else:
            self.HP -= decrease

        if decrease != 0:
            try:
                core.PlDict[origin].outd += decrease
            except KeyError:
                pass
            self.HPlog.append(
                [decrease, origin, core.ui.get(f'/act/{act_key}/name')])


    def evaluate_ability_and_weights(self, core: Core) -> tuple[list]:
        """
        Calculates which actions are currently available to this player based on game state.

        Args:
            core (Core): The main game core instance.

        Returns:
            tuple: A tuple containing two lists:
                   - A list of keys for all usable actions.
                   - A list of corresponding AI weights for those actions.
        """

        able = []
        ai_weights = []

        context = {"self": self, "core": core}
        context = core.Exec("-evaluate_ability_and_weights_context",
                            "Player.evaluate_ability_and_weights", context)

        # Iterate through all possible actions to see which are usable.
        for key, act in core.ActDict.items():

            is_human_only = act["human_only"]
            is_currently_able = (
                key not in self.unable) and act["able"](context)

            if not is_human_only and is_currently_able:
                able.append(key)

                # Calculate AI weight for this action.
                index = min(len(act["ai"])-1, self.ai_quality)
                ai_weights.append(act["ai"][index](context) * act["weight"])

        return able, ai_weights


class Act():
    """
    'Action': A core concept in the Noah kernel.
    Represents a player's chosen action to be executed during the dealing phase.
    """

    def __init__(self, ownerID: int, key: str, channel: str ='default'):
        self.acted = False      # Has this action been processed/dealt?
        # The ID of the player who initiated this action.
        self.ownerID = ownerID
        self.key = key          # The key of this action in ActDict.
        self.channel = channel  # The pipe processing channel this action uses.
        self.payed = False      # Has the energy cost for this action been paid?

    def deal(self, core: Core):
        """
        Processes or 'settles' this action.
        It adds the action's execution logic to the appropriate PipeWorkFlow.
        """
        if not self.acted:
            core.ui.workdir = f"/act/{self.key}"

            # The action's execution logic is added as a new step in its designated channel's stream.
            core.channels[self.channel] = PipeWorkFlow(
                PipeData=core.channels.get(self.channel, None),
                steps=core.ActDict[self.key]["dealing_exec"],
                args=(self, core)
            )
            self.acted = True

    def pay(self, core: Core):
        """
        Pays the energy cost for this action.
        Separated into its own method to allow one Act to potentially pay for another.
        """
        if not self.payed:
            cost = core.ActDict[self.key]["price"](self)
            core.PlDict[self.ownerID].energy -= cost
            self.payed = True
            if core.PlDict[self.ownerID].energy < 0 and cost > 0:
                core.RaiseError("Act.pay", f"Player {
                                self.ownerID} can't afford act {self.key}")


def SelectAct_WorkerFunc(task: tuple[Player, Core]):
    """
    A worker function designed for use with `map`. It handles the full action
    selection process for a single player.
    """
    player, core = task
    result_acts = []

    able_actions, ai_weights = player.evaluate_ability_and_weights(core)
    if not able_actions:
        # This player has no available actions.
        # Returns empty acts, and player ID for potential "no action" log.
        return [[], [player.id]]
    else:
        result_acts.extend(player.select(core))
    return [result_acts, []]


def PipeWorkFlow(PipeData: dict, steps: list, args: tuple | list):
    """
    Implements a stream processing pipeline architecture.
    It takes an input stream, passes it sequentially through a list of functions (`steps`),
    where the output of one step becomes the input for the next.

    Args:
        PipeData: The initial data/object to be processed.
        steps (list of functions): The functions that make up the processing pipeline.
        args (tuple): Common arguments that are passed to every function in `steps`.

    Returns:
        The final result after the last processing step.
    """
    OutData = PipeData
    for step_func in steps:
        OutData = step_func(OutData, args)
        if OutData:
            if "BREAK_CURRENT_PIPE" in OutData:
                del OutData["BREAK_CURRENT_PIPE"]
                return OutData
            elif "BREAK_ALL_PIPES" in OutData:
                return OutData

    return OutData



class Core():
    """
    The Core class encapsulates the main game state and logic.
    It's designed to solve the problem of passing many "global" state variables
    between functions by holding them as attributes, making the code cleaner and more modular.
    """

    def __init__(self, Mods: dict):

        # Make a mod-load to get original core settings and gaming data
        self.ModsHotReload(Mods)

        # A dictionary that registers actions for the current turn, grouped by priority.
        # This structure allows for easy, priority-based processing.
        # Format: {priority1: {ActName1: [Act1, ...], ...}, ...}
        self.ActSign: dict = {}

        # The central dictionary of all players in the game.
        # Format: {player_id: Player_instance, ...}
        self.PlDict: dict = {}

        # The current round number.
        self.rounds: int = 0

        # A dictionary holding cached statistics about the current game state,
        # used for quick lookups by AI and for displaying info.
        #
        # Build-In Format (you can change it by modifying Core.status_components):
        # "pop": {
        #     place: {team: [player_ids], "sum": [all_ids_at_place]},
        #     "all": total_population
        # },
        # "energy": {
        #     place: {team: total_energy, "sum": total_energy_at_place},
        #     "all": total_energy_in_game
        # }
        self.status: dict = {}

        # A temporary dictionary to hold stream data for each channel during the dealing phase.
        self.channels: dict = {}

        self.deaths: list = []  # List of player IDs who died this turn.
        self.exit_game: bool = False  # A flag to signal the end of the game loop.

        # A table that contain the Event objects
        self.EventBus: list = []

        self.debug: bool = False  # The debug mode of the Core


    def mk_pldict(self):
        """Creates the `self.PlDict` (player dictionary) based on `self.BattleEnv` settings."""
        if self.BattleEnv["team_size"] < 1:
            self.BattleEnv["team_size"] = 1  # Prevent division by zero.

        team_count = 0
        cur_team = 1 if not self.BattleEnv["assist_team"] else 0

        for i in range(self.BattleEnv["num"]):
            pl = Player(i + 1)
            pl.HP = self.BattleEnv["initHP"]
            pl.ai_quality = self.BattleEnv["ai_quality"]

            if i + 1 > self.BattleEnv["real"]:
                # This is an AI player.
                pl.real = False
                team_count += 1
                pl.team = cur_team
                if team_count >= self.BattleEnv["team_size"]:
                    cur_team += 1
                    team_count = 0
            else:
                # This is a human player.
                pl.team = 0
                pl.ai_quality = 9999

            self.PlDict[i + 1] = pl

    def ModsHotReload(self, NewMods: dict | None = None):

        if NewMods:
            # Sort the mods by their priorities
            self.Mods = sorted(NewMods.values(), key=lambda d: d.get("mod_priority", 0))

        for mod in self.Mods:
            if "mod_reload" in mod.keys():
                mod["mod_reload"]()

        try:
            # Merging Mods by their priorities
            self.MergedMod: list = reduce(deep_merge, self.Mods, {})
        except AttributeError:
            return -1

        # A dictionary containing battle setup parameters (e.g., number of players, initial HP).
        self.BattleEnv: dict = self.MergedMod["BattleEnv"]

        # The dictionary defining all possible actions in the game.
        # Format: { "action_key": { ... action properties ... }, ... }
        #
        # Action properties include:
        #   "name": (str) The display name of the action.
        #   "price": (func) A function that calculates the energy cost of the action.
        #   "price_display": (str) A string representing the price for display purposes.
        #   "priority": (int) The execution priority. Higher numbers are executed first.
        #   "able": (func) A function returning a bool, checking if the action is usable.
        #   "human_only": (bool) If True, this action is only available to human players (e.g., "help").
        #   "ai": (func) A function that returns a numerical weight for AI decision-making.
        #   "selecting_exec": (func) The selection-phase execution function, called immediately after a player chooses the action.
        #   "dealing_exec": (list) A list of deal-phase execution functions, added to the PipeWorkFlow.
        self.ActDict: dict = self.MergedMod["ActDict"]

        self.ui: IO = self.MergedMod["ui"]

        # A table that contain the names and PipeWorkFlows of kernel commands
        self.CmdTable: dict = self.MergedMod.get("CmdTable", default_cmd_table)


    def RunMainLoop(self):
        return self.Exec("-MainLoop", "GameMainLoop", {"core": self, "stages": []})


    def update_status(self):
        """
        Updates the cached game state statistics in `self.status`.

        This design allows:
        - Noah to provide essential status paths
        - Games to add custom status paths (e.g., snapshot)
        - Easy extension without modifying core Noah code
        """
        self.status = self.Exec("-update_status", "Core.update_status", {})

    def SelectAct(self):
        """
        Orchestrates the action selection phase for all players.
        It separates human and AI players and processes their decisions.
        Note: A previous attempt at multithreading this showed minimal performance gains
        for cheap tasks, so a simpler sequential approach is used.
        """

        human_players = [pl for pl in self.PlDict.values() if pl.real]
        ai_players = [pl for pl in self.PlDict.values() if not pl.real]
        self.org_delay = self.ui.typing_delay

        all_results = []

        # Process human players sequentially.
        for pl in human_players:
            all_results.append(SelectAct_WorkerFunc([pl, self]))
            # if one of the human player asked to leave the game
            if self.exit_game:
                return 0

        # Process AI players using `map` for a clean, parallel-ready structure.
        if ai_players:
            # Show progress bar for a large number of AIs.
            show_progress = len(self.PlDict) >= 10000 or (
                self.BattleEnv["ai_quality"] > 0 and len(self.PlDict) >= 100)
            if show_progress:
                print(f"{self.ui.get('/core/ai-dealing')
                         }  {0.000:3.0f}%", end='\r', flush=True)

            tasks = [[pl, self] for pl in ai_players]
            results_iterator = map(SelectAct_WorkerFunc, tasks)

            completed_tasks = 0
            total_tasks = len(ai_players)

            for res in results_iterator:
                if show_progress:
                    completed_tasks += 1
                    percentage = (completed_tasks / total_tasks) * 100
                    status_line = f"{self.ui.get(
                        '/core/ai-dealing')}  {percentage:3.0f}%".ljust(40)
                    print(status_line, end='\r', flush=True)
                all_results.append(res)

            if show_progress:
                print(self.ui.get('/core/ai-completed').ljust(40), end='\n\n')


        # Aggregate results and register the chosen actions.
        for acts, dead_ids in all_results:
            self.deaths.extend(dead_ids)
            for new_act in acts:
                priority = self.ActDict[new_act.key]["priority"]

                # Ensure the priority and action key exist in the registry.
                if priority not in self.ActSign:
                    self.ActSign[priority] = {}
                if new_act.key not in self.ActSign[priority]:
                    self.ActSign[priority][new_act.key] = []

                # Register the new action.
                self.ActSign[priority][new_act.key].append(new_act)

                # Record the action index on the player object for reference.
                # idx = len(self.ActSign[priority][new_act.key]) - 1
                # self.PlDict[new_act.ownerID].acts.append([new_act.key, idx])
                self.PlDict[new_act.ownerID].acts.append(new_act)

        if self.deaths:
            # Report players who were unable to select an action.
            player_ids_str = ", ".join([str(d) for d in self.deaths])
            org_typing_delay = self.ui.typing_delay
            self.ui.typing_delay = 0
            self.ui.out("/core/no-available-act",
                        imp=[player_ids_str], color="RED")
            self.ui.typing_delay = org_typing_delay

    def DealAct(self):

        self.ui.out(self.debug_snapshot(), mode="l", directly=True)

        """Processes all selected actions for the round, in descending order of priority."""
        self.org_delay = self.ui.typing_delay
        self.ui.typing_delay = 0  # Disable typing delay for faster processing.

        # Get priorities and sort them from highest to lowest.
        act_order = sorted(self.ActSign.keys(), reverse=True)
        for priority in act_order:
            for act_name in self.ActSign[priority]:
                for act in self.ActSign[priority][act_name]:
                    act.deal(self)  # Queues the action into the pipe workflow.

        # After all actions are dealt, check for deaths. This is a preliminary check.
        for _pl in list(self.PlDict.keys()):
            if self.PlDict[_pl].HP <= 0:
                self.deaths.append(_pl)

        self.ui.typing_delay = self.org_delay  # Restore original typing delay.

    def rm_deaths(self):
        """Removes deceased players from the game and logs their demise."""
        show = []
        teams_affected = {}

        # Group deaths by team for team-based reporting.
        unique_deaths = sorted(list(set(self.deaths)))
        for _pl in unique_deaths:
            if _pl in self.PlDict:
                team_id = self.PlDict[_pl].team
                if team_id not in teams_affected:
                    teams_affected[team_id] = []
                teams_affected[team_id].append(_pl)

        for _pl in unique_deaths:
            if _pl in self.PlDict:
                player = self.PlDict[_pl]
                if player.real:
                    # Pause for human player's death message.
                    self.ui.typing_delay *= 5
                    last_hit = player.HPlog[-1] if player.HPlog else [0,
                                                                      "Unknown", "Fate"]
                    self.ui.inp('/core/human-dead', imp=[_pl] + last_hit)
                    self.ui.typing_delay /= 5

                try:
                    # Attribute the kill to the source of the last damage.
                    if player.HPlog:
                        killerID = player.HPlog[-1][1]
                        if killerID in self.PlDict:
                            self.PlDict[killerID].kills.append(_pl)
                except IndexError:
                    pass  # No damage log available.

                del self.PlDict[_pl]
                show.append(str(_pl))

        if show:
            org_delay = self.ui.typing_delay
            self.ui.typing_delay = 0  # Speed up death announcements.
            if len(show) > self.BattleEnv["msg_summary_threshold"]:
                imp = [", ".join(
                    show[:self.BattleEnv["msg_summary_threshold"]-1])+"...(etc)...", len(show)]
            else:
                imp = [", ".join(show), len(show)]
            self.ui.out('/core/dead', imp=imp)

            if self.BattleEnv["team_size"] > 1 and len(teams_affected) > 0:
                for t, dead_members in teams_affected.items():
                    self.ui.out('/core/dead-team',
                                imp=[t, len(dead_members)], color="RED")

            self.ui.typing_delay = org_delay

        self.deaths = []

    def clean_round(self):
        
        """Clears temporary round-specific data to prepare for the next round."""
        self.ActSign = {}
        for pl in self.PlDict.values():
            pl.acts = []
            pl.status = {}
        self.deaths = []
        self.channels = {}

    def ls_acts(self, typing_delay: int | float = 0, speed_stability: int | float = 2):
        """Displays the list of available actions in a nicely formatted table."""
        self.ui.workdir = "/act/"

        title = self.ui.get("/core/actlist-title")

        act_data = [
            (key, self.ui.get(f"./{key}/name"), self.ui.get(f"./{key}/price"))
            for key in self.ActDict.keys()
        ]

        table_str = table(
            act_data,
            f"{C['YELLOW']}$0{C['RESET']}. $1 {C['CYAN']}($2){C['RESET']}"
        )

        final_list = title + table_str + "\n"
        original_typing_delay = self.ui.typing_delay
        self.ui.typing_delay = typing_delay
        self.ui.out(final_list, directly=True, speed_stability=speed_stability)
        self.ui.typing_delay = original_typing_delay

    def RaiseError(self, domain: str, msg: str):
        mode = "l"
        if not self.debug:
            mode += "s"
        self.ui.inp(f"[{domain}] ERROR: {msg}",
                    mode=mode, directly=True, color="RED")
        self.ui.write_log()

    def Exec(self, cmd_name: str, domain: str, PipeData=None):
        if cmd_name not in self.CmdTable:
            self.RaiseError(domain, f"Command not found: {cmd_name}")
            return PipeData
        else:
            try:
                return PipeWorkFlow(PipeData, self.CmdTable[cmd_name], self)
            except Exception as e:
                if not self.debug:
                    self.RaiseError(domain, f"Kernel command '{
                                    cmd_name}' failed: {e}")
                    return {}
                else:
                    raise e

    def DealEvents(self):
        """
        Deal the events in EventBus and clear it
        """
        if not self.EventBus:
            return

        for event in self.EventBus:
            try:
                event.happen(self)
            except Exception as e:
                if not self.debug:
                    self.RaiseError("Core.DealEvents", f"Event '{
                                    event.type}' failed: {e}")
                else:
                    raise e

        # Clear the EventBus
        self.EventBus.clear()

    def debug_snapshot(self, title: str = "Game State", split_str_lenth: int = 30):
        msg = []
        msg.append(f"{'='*split_str_lenth}")
        msg.append(f"{title} - Round {self.rounds}")
        msg.append(f"{'='*split_str_lenth}")

        msg.append(f"Alive: {len(self.PlDict)} players")
        for pid, pl in self.PlDict.items():
            msg.append(f"\tP{pid}: HP={pl.HP} E={
                       pl.energy} Pos={pl.place} Team={pl.team}")

        if self.ActSign:
            msg.append(f"\nPending Actions:")
            for priority in sorted(self.ActSign.keys(), reverse=True):
                for act_key, acts in self.ActSign[priority].items():
                    msg.append(f"  Priority {
                               priority} / ActCode {act_key}: {len(acts)} actions")

        msg.append(f"{'='*split_str_lenth}")

        return "\n".join(msg)

    def battle_env_snapshot(self, title:str = "Battle Environment", split_str_lenth:int = 30):
        msg = []
        msg.append(f"{'='*split_str_lenth}")
        msg.append(f"{title}s")
        msg.append(f"{'='*split_str_lenth}")

        for env_key, env_value in self.BattleEnv.items():
            msg.append(f"\t{env_key} -> {env_value}")

        msg.append(f"{'='*split_str_lenth}")

        return "\n".join(msg)

    def round_title(self):
        self.ui.out(["/share/endl", "/core/round-title", "/share/endl"], imp=[self.rounds], color="WHITE")


default_cmd_table = {

    "-update_status": [
    ],

    "-evaluate_ability_and_weights_context": [
    ],

    "-MainLoop": [
    ],
}


class Event():
    """
    Represents a deferred kernel command.

    An Event encapsulates a command that can be triggered later,
    potentially with conditions or delays.
    """

    def __init__(self, cmd_type: str, domain: str, PipeData=None):
        self.type = cmd_type
        self.inp = PipeData
        self.domain = domain
        self.has_happened = False

    def happen(self, core: Core):
        if not self.has_happened:
            core.Exec(self.type, self.domain, self.inp)
        else:
            core.RaiseError(
                self.domain, f"One Event object has happened but try to happend again (Type {self.type}).")
        self.has_happened = True


