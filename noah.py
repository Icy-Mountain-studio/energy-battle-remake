"""
The Noah Kernel: A turn-based game engine.
Originally spun off from the development of the game 'Energy Battle'.

Project initiated: 2025.8.2
Last updated: 2025.10.2
"""

import random, re, os, time, sys

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
}

class IO():
    """Defines an IO class for managing input, output, and logging."""

    def __init__(self, exp={}, logpath="log", delay=0.01):
        """
        Initializes the IO manager.

        Args:
            exp (dict): A dictionary of expression templates.
                        Format: {key1: [line1, line2, ...], ...}
                        where lineX is a string template to be processed by explain().
            logpath (str): The path for storing log files.
        """
        self.exp = exp
        self.workdir = "/"  # The current working directory for relative paths in `exp`.
        self.history = []   # A history of all inputs and outputs.
        self.logs = []      # A list of messages to be written to a log file.
        self.logpath = logpath

        self.colors = C
        self.indent = 0     # Tracks the current indentation level for formatted output.
        self.typing_delay = delay  # Delay for the typewriter effect. Set to 0 to disable.

    def out(self, key, mode="sh", real_end="\n", dr=False, imp=[], indent=True, color=None):
        """
        Outputs content to specified channels after evaluating it.

        Args:
            key (str or list): The key(s) for the expression template in `self.exp`, or the direct content if `dr` is True.
            mode (str): A string specifying the output channels.
                        's': standard output (console)
                        'h': history list
                        'l': log list
                        Can be combined, e.g., "shl".
            real_end (str): The character to print at the very end of the output.
            dr (bool): Direct render. If True, treats `key` as the content itself rather than a key to `self.exp`.
            imp (list): A list of values to be imported into the expression template for substitution.
            indent (bool or int): If True, uses the current `self.indent`. If an int, uses that as the indentation level.
                                 If False, no indentation is applied.
            color (str): The key for a color from `self.colors` to apply to the output.
        """
        if isinstance(key, list):
            # If `key` is a list, output each item in it recursively.
            for k in key:
                self.out(k, mode, real_end, dr, imp, indent, color)
        else:
            # Determine indentation prefix.
            if indent is True:
                plus = (self.indent * 4) * " "
            elif isinstance(indent, int):
                plus = (indent * 4) * " "
            else:
                plus = ""

            # Evaluate the final string to be printed.
            if dr:
                res = explain(key, imp)
            else:
                # Resolve path and get the expression template.
                res = explain(self.exp[self.dealpath(key)], imp)

            if res != "NONE":
                _res = plus + res  # Result with indentation for logging/history.

                if color:
                    res = self.colors.get(color, "") + res + self.colors["RESET"]
                    _res = self.colors.get(color, "") + _res + self.colors["RESET"]

                # Output to the specified channels.
                if "s" in mode:
                    if plus:
                        print(plus, end="")
                    if self.typing_delay > 0:
                        self._typewriter_print(res)
                        print(end=real_end)
                    else:
                        print(res, end=real_end)

                if "h" in mode:
                    self.history.append(_res)
                if "l" in mode:
                    self.logs.append(_res)

    def inp(self, key, mode="sh", dr=False, imp=[], indent=True, color=None):
        """
        Prompts the user for input after printing a message, and returns the result.
        The user's response is appended to the message in the history/log.

        Args:
            (See self.out for argument descriptions)

        Returns:
            str: The user's input.
        """
        self.out(key, mode, real_end="", dr=dr, imp=imp, indent=indent, color=color)
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
        return self.exp[self.dealpath(key)]

    def _typewriter_print(self, text: str):
        """Prints text character by character with a typewriter effect."""
        for char in text:
            sys.stdout.write(char)
            sys.stdout.flush()
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
                return match.group(0)  # match.group(0) is the full matched string, e.g., "$12".
        except (ValueError, IndexError):
            # In case of any conversion error, also return the original placeholder.
            return match.group(0)

    # The regex r'\$(\d+)' finds a literal '$' followed by one or more digits.
    # The parentheses (\d+) create a capture group for the digits.
    return re.sub(r'\$(\d+)', replacer, template_str)

def decide(able_actions: list, weights: list, real: bool):
    """
    Performs a weighted random selection from a list of actions.
    For a real player, it suggests the action with the highest weight.

    Args:
        able_actions (list): A list of available actions, e.g., ['attack', 'defend'].
        weights (list): A list of corresponding numerical weights, e.g., [10, 80].
        real (bool): If True, indicates a human player. If False, an AI.

    Returns:
        str: The chosen action.
        None: If the list of actions is empty.
    """
    # Robustness check to prevent crashing on empty lists.
    if not able_actions:
        return None

    if not real:
        # AI player: make a weighted random choice.
        # random.choices returns a list, so we take the first element.
        try:
            chosen_action = random.choices(population=able_actions, weights=weights, k=1)[0]
        except ValueError:
            # This can happen if weights are invalid (e.g., all zero).
            print(f"Warning: Invalid weights for actions. Actions: {able_actions}, Weights: {weights}")
            return None
    else:
        # Human player: suggest the action with the highest weight.
        chosen_action = able_actions[weights.index(max(weights))]

    return chosen_action

def table(data, exp, spl="\n"):
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

    def __init__(self, id):
        self.id = id           # Unique identifier for the player.
        self.energy = 0        # Current amount of energy the player possesses.
        self.HP = 1            # Current health points.
        self.place = 0         # The player's current location/level in the game world.
        self.unable = []       # A blacklist of action names this player cannot use.
        self.real = True       # True if this is a human player, False for AI.
        self.outd = 0          # Total damage dealt by this player.
        self.HPlog = []        # Log of HP changes: [[damage, source_id, action_name], ...].
        self.kills = []        # List of player IDs killed by this player.

        # The ID of the AI team this player belongs to.
        # 0 is reserved for human players or AI allied with humans.
        self.team = 0

        # Player's defense level for the current turn. Resets every turn.
        # The kernel defines 1 as standard defense and -1 as damage reflection.
        self.defend_lv = 0

        # A list of selected actions and their parameters for the current turn. Cleared each turn.
        # Format: [[action_key<str>, action_sign_index<int>], ...]
        self.acts = []

    def select(self, core, decision=None):
        """
        Allows the player to select an action, which generates and returns Act objects.
        This method handles the selection logic for both human and AI players.

        Args:
            core (Core): The main game core instance.
            decision (str, optional): The pre-determined action for an AI, or a suggestion for a human.

        Returns:
            list: A list of `Act` objects created from the player's selection.
        """
        auto = not self.real
        result = []

        while True:
            if self.real:
                # Prompt human player for input.
                prompt_imp = [self.id, self.HP, self.energy, self.place, core.ui.get(f"/act/{decision}/name")]
                selection = core.ui.inp('/core/ask-for-act', imp=prompt_imp)

                if selection == "":
                    # If human player presses Enter, accept the suggested decision.
                    selection = decision
                    auto = True
                    # Slow down typing to make it clear the choice was automated.
                    core.ui.typing_delay *= 7
                    core.ui.out('/core/selected', imp=[core.ui.get(f"/act/{selection}/name")])
                    core.ui.typing_delay /= 7

                if selection not in core.ActDict:
                    core.ui.out(['/share/not-found', '/share/endl'], color="RED")
                    continue

                if selection in self.unable:
                    core.ui.out(['/share/unable', '/share/endl'])
                    continue

                core.ui.out('/share/endl')
            else:
                # AI player uses the pre-determined decision.
                selection = decision

            if core.ui:
                # Set the working directory for IO to the context of the selected action.
                core.ui.workdir = f"/act/{selection}"

            # Execute the selection function (`s_exec`) of the chosen action.
            _break, new_act = core.ActDict[selection]["s_exec"](self, core, auto)

            if new_act:
                result.append(new_act)

            if _break:
                break

        return result

    def hurted(self, decreasion, origin, act_key, core):
        """
        The standard method for a player to take damage and log the event.

        Args:
            decreasion (int): The amount of HP to reduce.
            origin (int): The ID of the player who caused the damage.
            act_key (str): The key of the action that caused the damage.
            core (Core): The main game core instance.
        """
        if decreasion >= self.HP:
            # Prevents HP from going negative and logs exact lethal damage.
            decreasion = self.HP
            self.HP = 0
        else:
            self.HP -= decreasion

        if decreasion != 0:
            core.PlDict[origin].outd += decreasion
            self.HPlog.append([decreasion, origin, core.ui.get(f'/act/{act_key}/name')])

    def build_able(self, core):
        """
        Calculates which actions are currently available to this player based on game state.

        Args:
            core (Core): The main game core instance.

        Returns:
            tuple: A tuple containing two lists:
                   - A list of keys for all usable actions.
                   - A list of corresponding AI weights for those actions.
        """
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

        # --- Safer calculation of nearby enemy energy ---
        side_eng = 0
        for i in nearby_places:
            place_eng_stats = core.status["energy"].get(i, {})
            total_eng_at_place = place_eng_stats.get("sum", 0)
            my_team_eng_at_place = place_eng_stats.get(self.team, 0)
            side_eng += total_eng_at_place - my_team_eng_at_place

        all_eng = core.status["energy"].get("all", 0)
        engK = side_eng / all_eng if all_eng > 0 else 0 # Ratio of nearby enemy energy to total enemy energy.

        able = []
        ai_weights = []

        # Context dictionary passed to action logic functions.
        context = {
            "self": self, "side_enm": side_enm, "all_enm": all_enm,
            "enmK": enmK, "side_eng": side_eng, "all_eng": all_eng,
            "engK": engK, "core": core
        }

        # Iterate through all possible actions to see which are usable.
        for key, act in core.ActDict.items():
            if key == 'cp': continue # Skip special keys.

            is_human_only = act["human_only"]
            is_currently_able = (key not in self.unable) and act["able"](context)

            if (not is_human_only) and is_currently_able:
                able.append(key)
                # Calculate AI weight for this action.
                ai_weights.append(act["ai"](context) * act["weight"])

        return able, ai_weights

class Act():
    """
    'Action': A core concept in the Noah kernel.
    Represents a player's chosen action to be executed during the dealing phase.
    """
    def __init__(self, ownerID, key, channel='default'):
        self.acted = False      # Has this action been processed/dealt?
        self.ownerID = ownerID  # The ID of the player who initiated this action.
        self.key = key          # The key of this action in ActDict.
        self.channel = channel  # The stream processing channel this action uses.
        self.payed = False      # Has the energy cost for this action been paid?

    def deal(self, core):
        """
        Processes or 'settles' this action.
        It adds the action's execution logic to the appropriate stream processor.
        """
        if not self.acted:
            core.ui.workdir = f"/act/{self.key}"

            # The action's execution logic is added as a new step in its designated channel's stream.
            core.channels[self.channel] = StreamProcessor(
                InStream=core.channels.get(self.channel, None),
                steps=core.ActDict[self.key]["d_exec"],
                args=(self, core)
            )
            self.acted = True

    def pay(self, core):
        """
        Pays the energy cost for this action.
        Separated into its own method to allow one Act to potentially pay for another.
        """
        if not self.payed:
            cost = core.ActDict[self.key]["price"](self)
            core.PlDict[self.ownerID].energy -= cost
            self.payed = True

def SelectAct_WorkerFunc(task):
    """
    A worker function designed for use with `map`. It handles the full action
    selection process for a single player.
    """
    player, core = task
    result_acts = []

    able_actions, ai_weights = player.build_able(core)
    if not able_actions:
        # This player has no available actions.
        return [[], [player.id]] # Returns empty acts, and player ID for potential "no action" log.

    decision_key = decide(able_actions, ai_weights, player.real)
    if decision_key is None:
        return [[], [player.id]]
    else:
        result_acts.extend(player.select(core, decision_key))

    return [result_acts, []]

def StreamProcessor(InStream, steps: list, args: tuple):
    """
    Implements a stream processing pipeline architecture.
    It takes an input stream, passes it sequentially through a list of functions (`steps`),
    where the output of one step becomes the input for the next.

    Args:
        InStream: The initial data/object to be processed.
        steps (list of functions): The functions that make up the processing pipeline.
        args (tuple): Common arguments that are passed to every function in `steps`.

    Returns:
        The final result after the last processing step.
    """
    OutStream = InStream
    for step_func in steps:
        OutStream = step_func(OutStream, args)
    return OutStream

class Core():
    """
    The Core class encapsulates the main game state and logic.
    It's designed to solve the problem of passing many "global" state variables
    between functions by holding them as attributes, making the code cleaner and more modular.
    """

    def __init__(self, BattleEnv: dict, ActDict: dict, ui: IO):
        # A dictionary containing battle setup parameters (e.g., number of players, initial HP).
        self.BattleEnv = BattleEnv

        # A dictionary that registers actions for the current turn, grouped by priority.
        # This structure allows for easy, priority-based processing.
        # Format: {priority1: {ActName1: [Act1, ...], ...}, ...}
        self.ActSign = {}

        # The central dictionary of all players in the game.
        # Format: {player_id: Player_instance, ...}
        self.PlDict = {}

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
        #   "s_exec": (func) The selection-phase execution function, called immediately after a player chooses the action.
        #   "d_exec": (list) A list of deal-phase execution functions, added to the StreamProcessor.
        self.ActDict = ActDict

        # The current round number.
        self.rounds = 0

        # A dictionary holding cached statistics about the current game state,
        # used for quick lookups by AI and for displaying info.
        #
        # Format:
        # "pop": {
        #     place: {team: [player_ids], "sum": [all_ids_at_place]},
        #     "all": total_population
        # },
        # "energy": {
        #     place: {team: total_energy, "sum": total_energy_at_place},
        #     "all": total_energy_in_game
        # },
        # "snap": {
        #     player_id: [HP, energy, place, team], ...
        # }
        self.status = {}

        # A temporary dictionary to hold stream data for each channel during the dealing phase.
        self.channels = {}

        self.deaths = [] # List of player IDs who died this turn.
        self.ui = ui
        self._break = False # A flag to signal the end of the game loop.

    def mk_pldict(self):
        """Creates the `self.PlDict` (player dictionary) based on `self.BattleEnv` settings."""
        if self.BattleEnv["team_size"] < 1:
            self.BattleEnv["team_size"] = 1 # Prevent division by zero.

        team_count = 0
        cur_team = 1 if not self.BattleEnv["assist_team"] else 0

        for i in range(self.BattleEnv["num"]):
            pl = Player(i + 1)
            pl.HP = self.BattleEnv["initHP"]

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

            self.PlDict[i + 1] = pl

    def update_status(self):
        """Updates the cached game state statistics in `self.status`."""
        self.status = {"pop": {}, "energy": {}, "snap": {}}

        # First pass for population and snapshot data.
        for pl in self.PlDict.values():
            # Update population by place and team.
            if pl.place not in self.status["pop"]:
                self.status["pop"][pl.place] = {pl.team: [pl.id], "sum": [pl.id]}
            elif pl.team not in self.status["pop"][pl.place]:
                self.status["pop"][pl.place][pl.team] = [pl.id]
                self.status["pop"][pl.place]["sum"].append(pl.id)
            else:
                self.status["pop"][pl.place][pl.team].append(pl.id)
                self.status["pop"][pl.place]["sum"].append(pl.id)

            # Create a snapshot of the player's state.
            self.status["snap"][pl.id] = [pl.HP, pl.energy, pl.place, pl.team]

        # Second pass for energy data, requires all players to be iterated first.
        all_energy = 0
        for pl in self.PlDict.values():
            if pl.place not in self.status["energy"]:
                self.status["energy"][pl.place] = {pl.team: pl.energy, "sum": pl.energy}
            elif pl.team not in self.status["energy"][pl.place]:
                self.status["energy"][pl.place][pl.team] = pl.energy
                self.status["energy"][pl.place]["sum"] = self.status["energy"][pl.place].get("sum", 0) + pl.energy
            else:
                self.status["energy"][pl.place][pl.team] += pl.energy
                self.status["energy"][pl.place]["sum"] += pl.energy
            all_energy += pl.energy

        self.status["pop"]["all"] = len(self.PlDict)
        self.status["energy"]["all"] = all_energy

    def SelectAct(self):
        """
        Orchestrates the action selection phase for all players.
        It separates human and AI players and processes their decisions.
        Note: A previous attempt at multithreading this showed minimal performance gains
        for cheap tasks, so a simpler sequential approach is used.
        """
        human_players = [pl for pl in self.PlDict.values() if pl.real]
        ai_players = [pl for pl in self.PlDict.values() if not pl.real]

        all_results = []

        # Process AI players using `map` for a clean, parallel-ready structure.
        if ai_players:
            # Show progress bar for a large number of AIs.
            show_progress = len(self.PlDict) >= 10000
            if show_progress:
                print(f"{self.ui.get('/core/ai-dealing')}  {0.000:3.0f}%", end='\r', flush=True)

            tasks = [[pl, self] for pl in ai_players]
            results_iterator = map(SelectAct_WorkerFunc, tasks)

            completed_tasks = 0
            total_tasks = len(ai_players)

            for res in results_iterator:
                if show_progress:
                    completed_tasks += 1
                    percentage = (completed_tasks / total_tasks) * 100
                    status_line = f"{self.ui.get('/core/ai-dealing')}  {percentage:3.0f}%".ljust(40)
                    print(status_line, end='\r', flush=True)
                all_results.append(res)

            if show_progress:
                print(self.ui.get('/core/ai-completed').ljust(40), end='\n\n')

        # Process human players sequentially.
        for pl in human_players:
            all_results.append(SelectAct_WorkerFunc([pl, self]))

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
                idx = len(self.ActSign[priority][new_act.key]) - 1
                self.PlDict[new_act.ownerID].acts.append([new_act.key, idx])

        if self.deaths:
            # Report players who were unable to select an action.
            player_ids_str = ", ".join([str(d) for d in self.deaths])
            self.ui.out("/core/no-available-act", imp=[player_ids_str], color="RED")

    def DealAct(self):
        """Processes all selected actions for the round, in descending order of priority."""
        self.org_delay = self.ui.typing_delay
        self.ui.typing_delay = 0 # Disable typing delay for faster processing.

        # Get priorities and sort them from highest to lowest.
        act_order = sorted(self.ActSign.keys(), reverse=True)
        for priority in act_order:
            for act_name in self.ActSign[priority]:
                for act in self.ActSign[priority][act_name]:
                    act.deal(self) # Queues the action into the stream processor.

        # After all actions are dealt, check for deaths. This is a preliminary check.
        for _pl in list(self.PlDict.keys()):
            if self.PlDict[_pl].HP <= 0:
                self.deaths.append(_pl)

        self.ui.typing_delay = self.org_delay # Restore original typing delay.

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
                    last_hit = player.HPlog[-1] if player.HPlog else [0, "Unknown", "Fate"]
                    self.ui.inp('/core/human-dead', imp=[_pl] + last_hit)
                    self.ui.typing_delay /= 5

                try:
                    # Attribute the kill to the source of the last damage.
                    if player.HPlog:
                        killerID = player.HPlog[-1][1]
                        if killerID in self.PlDict:
                            self.PlDict[killerID].kills.append(_pl)
                except IndexError:
                    pass # No damage log available.

                del self.PlDict[_pl]
                show.append(str(_pl))

        if show:
            org_delay = self.ui.typing_delay
            self.ui.typing_delay = 0 # Speed up death announcements.
            self.ui.out('/core/dead', imp=[", ".join(show), len(show)])

            if self.BattleEnv["team_size"] > 1 and len(teams_affected) > 0:
                for t, dead_members in teams_affected.items():
                    self.ui.out('/core/dead-team', imp=[t, len(dead_members)], color="RED")

            self.ui.typing_delay = org_delay

        self.deaths = []

    def clean_round(self):
        """Clears temporary round-specific data to prepare for the next round."""
        self.ActSign = {}
        for pl in self.PlDict.values():
            pl.acts = []
            pl.defend_lv = 0
        self.deaths = []
        self.channels = {}

    def ls_acts(self):
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

        # Temporarily speed up printing for the list.
        original_delay = self.ui.typing_delay
        self.ui.typing_delay /= 30
        self.ui.out(final_list, dr=True)
        self.ui.typing_delay = original_delay

    def refresh(self):
        """Resets all data for the current battle session to start fresh."""
        self.clean_round()
        self.PlDict = {}
        # Assuming `exp` is available in the global scope to re-initialize IO.
        # This might need adjustment based on the main script's structure.
        self.ui = IO(exp=self.ui.exp)
