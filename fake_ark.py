import noah
from localize import Expression

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

from actions import BaseActDict


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

timest = noah.time.strftime("%Y-%m-%d_%H-%M-%S")

ModContents = {
    "BattleEnv": InitBattleEnv,
    "ActDict": BaseActDict,
    "ui": noah.IO(Expression["zh_cn"], logpath=f"./logs/noah_{timest}.gz"),
    "CmdTable": CmdTable,
    "mod_priority": 0,
    "mod_name": "FakeArk",
    }

