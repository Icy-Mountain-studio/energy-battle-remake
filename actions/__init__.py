"""
/Energy-Battle-Remake/actions/__init__.py
"""

import noah
from actions import charge, shot, defend, move, reflect, wave, blackhole, ShowRules, breaking

# The master Action Dictionary that defines the entire game's mechanics for the Noah Kernel.
BaseActDict = {
    "1": charge.ActionProperties,
    "2": shot.ActionProperties,
    "3": defend.ActionProperties,
    "4": move.ActionProperties,
    "5": reflect.ActionProperties,
    "6": wave.ActionProperties,
    "7": blackhole.ActionProperties,
    "rl": ShowRules.ActionProperties,
    "bk": breaking.ActionProperties
}

