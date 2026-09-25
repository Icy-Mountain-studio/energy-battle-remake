"""
/Energy-Battle-Remake/tests/test_interactive_actions.py
"""

import pytest
import noah
from noah import Player, Act

# Disable all visual delays to make tests run instantly
noah.time.sleep = lambda x: None 

from actions.charge import charge_selecting, charge_dealing
from actions.blackhole import blackhole_selecting, blackhole_dealing
from actions.wave import wave_selecting
from actions.move import move_selecting, move_dealing
from actions.reflect import reflect_selecting, reflect_dealing
from actions.shot import shot_selecting, crossfire_evaluate
from actions.wave import wave_selecting, crossfire_wave_eval, auto_AOEseth

# ==========================================
# Interactive Fake Core & UI
# ==========================================
class InteractiveFakeUI:
    def __init__(self, predefined_inputs: list):
        self.inputs = predefined_inputs
        self.input_index = 0
        self.indent = 0
        self.typing_delay = 0
    
    def inp(self, *args, **kwargs):
        if self.input_index < len(self.inputs):
            val = self.inputs[self.input_index]
            self.input_index += 1
            return val
        return "" 
    
    def out(self, *args, **kwargs): pass
    def get(self, key): return key

class InteractiveFakeCore:
    def __init__(self, predefined_inputs: list):
        self.PlDict = {}
        self.ui = InteractiveFakeUI(predefined_inputs)
        self.org_delay = 0
        self.error_raised = False
        self.status = {"pop": {"all": 2}, "snap": {}}
        self.BattleEnv = {"wave_distance": 3, "shot_distance": 1, "max_move_speed": 2, "map": 3}
        self.ActDict = {
            "7": {"price": lambda act: 5},
            "6": {"price": lambda act: 6},
            "5": {"price": lambda act: 2},
            "4": {"price": lambda act: 1},
            "2": {"price": lambda act: act.lv},
            "1": {"price": lambda act: -1},
        }
    def RaiseError(self, *args): 
        self.error_raised = True


# ==========================================
# Test 1: Black Hole & Wave
# ==========================================
def test_blackhole_and_wave():
    core = InteractiveFakeCore(["99", "1", "2"])
    p1 = Player(1)
    p1.energy = 10
    core.PlDict[1] = p1
    core.PlDict[2] = Player(2)
    success, act = blackhole_selecting(p1, core, auto=False)
    assert success is True
    
    core = InteractiveFakeCore([""])
    p1.energy = 10 # CRITICAL: Reset energy after blackhole consumed it!
    core.PlDict[1] = p1 # Register player in the new core
    core.status["pop"] = {0: {"sum": [1]}, 1: {"sum": [2, 3]}, "all": 3}
    success, act = wave_selecting(p1, core, auto=False)
    assert act.seth == 1 


# ==========================================
# Test 2: Move Selecting & Dealing
# ==========================================
def test_move_selecting():
    p1 = Player(1)
    p1.energy = 5
    p1.place = 0
    
    # Human Errors
    core = InteractiveFakeCore(["abc", "99", "999", "0"])
    core.PlDict[1] = p1
    success, act = move_selecting(p1, core, auto=False)
    assert success is False
    
    # Human Valid Input: 1
    core = InteractiveFakeCore(["1"])
    core.PlDict[1] = p1
    success, act = move_selecting(p1, core, auto=False)
    assert success is True and act.steps == 1
    
    # Human Poor (No energy)
    p1.energy = 0
    success, act = move_selecting(p1, core, auto=False)
    assert success is False
    
    # AI Selection
    p1.energy = 5
    success, act = move_selecting(p1, core, auto=True)
    assert success is True and act.steps != 0

def test_move_dealing():
    core = InteractiveFakeCore([])
    p1 = Player(1)
    p1.real = True
    core.PlDict[1] = p1
    
    act = Act(1, "4")
    act.steps = 2
    move_dealing(None, (act, core))
    assert p1.place == 2
    
    act.steps = 5
    move_dealing(None, (act, core))
    assert core.error_raised is True


# ==========================================
# Test 3: Reflect Selecting & Dealing
# ==========================================
def test_reflect_selecting_dealing():
    core = InteractiveFakeCore([])
    p1 = Player(1)
    core.PlDict[1] = p1
    
    # Poor
    p1.energy = 1
    success, act = reflect_selecting(p1, core, auto=False)
    assert success is False
    
    # Success
    p1.energy = 2
    success, act = reflect_selecting(p1, core, auto=False)
    assert success is True
    
    # Dealing
    p1.real = True
    reflect_dealing(None, (act, core))
    assert p1.status["reflect"] is True


# ==========================================
# Test 4: Shot Selecting (Human Errors & AI)
# ==========================================
def test_shot_selecting_human_errors():
    p1 = Player(1)
    p1.energy = 5
    p1.place = 0
    
    # Target Inputs
    core = InteractiveFakeCore(["abc", "99", "1", ""])
    core.PlDict[1] = p1
    core.status["snap"] = {1: [10, 5, 0, 0]}
    success, act = shot_selecting(p1, core, auto=False)
    assert success is False
    
    # Level Inputs
    core = InteractiveFakeCore(["2", "abc", "4", "3", "", ""])
    core.PlDict[1] = p1
    p2 = Player(2)
    p2.team = 1
    p2.HP = 10
    core.PlDict[2] = p2
    core.status["snap"] = {1: [10, 2, 0, 0], 2: [10, 5, 0, 1]}
    p1.energy = 2 
    success, act = shot_selecting(p1, core, auto=False)
    assert success is True
    assert act.lv == 2

    # Seth Inputs
    core = InteractiveFakeCore(["2", "1", "abc", "9", "1"])
    p1.energy = 10
    core.PlDict[1] = p1
    core.PlDict[2] = p2

    core.status["snap"] = {1: [10, 5, 0, 0], 2: [10, 5, 0, 1]} 
    success, act = shot_selecting(p1, core, auto=False)
    assert success is True
    assert act.seth == 1

def test_shot_selecting_ai():
    core = InteractiveFakeCore([])
    p1 = Player(1)
    p1.energy = 5
    p1.place = 0
    p1.real = False
    core.PlDict[1] = p1
    
    p2 = Player(2)
    p2.team = 1 
    core.PlDict[2] = p2
    
    core.status["pop"] = {0: {"sum": [1, 2]}}
    core.status["snap"] = {1: [10, 5, 0, 0], 2: [10, 5, 0, 1]}

    success, act = shot_selecting(p1, core, auto=True)
    assert success is True
    assert act.target == 2
    assert act.lv == 3 
    assert act.seth == 0


# ==========================================
# Test 5: Crossfire Evaluate
# ==========================================
def test_crossfire_evaluate():
    core = InteractiveFakeCore([])
    p1 = Player(1)
    p1.real = True
    core.PlDict[1] = p1
    p2 = Player(2)
    core.PlDict[2] = p2
    
    act = Act(1, "2")
    act.target = 2
    act.seth = 0
    act.distant = 1
    act.lv = 2
    act.channel = "shot-like"
    act.AOE = False
    act.color = "RED"
    p1.acts = [act]
    
    pipe_data = crossfire_evaluate(None, (act, core))
    
    assert pipe_data["damage"][2] == 2

# ==========================================
# Test 6: Charge Selecting & Dealing
# Covers the human UI outputs and AI dealing paths
# ==========================================
def test_charge_selecting_dealing():
    core = InteractiveFakeCore([])
    p1 = Player(1)
    p1.energy = 5
    p1.real = True
    core.PlDict[1] = p1
    
    # [Test Selecting]
    success, act = charge_selecting(p1, core, auto=False)
    assert success is True
    assert act.key == "1"
    assert p1.energy == 6  # Paid! (Cost is -1, so energy goes up)
    assert act.energy_should_have == 6
    
    # [Test Dealing] (Human)
    charge_dealing(None, (act, core))
    
    # [Test Dealing] (AI - Triggers the else branch for non-real players)
    p1.real = False
    charge_dealing(None, (act, core))


# ==========================================
# Test 7: Blackhole Complex Selecting
# Covers the Poverty paths and AI auto-aim logic
# ==========================================
def test_blackhole_selecting_complex():
    core = InteractiveFakeCore([])
    p1 = Player(1)
    core.PlDict[1] = p1
    
    # 1. Human is too poor (Energy < 5)
    p1.energy = 4
    success, act = blackhole_selecting(p1, core, auto=False)
    assert success is False
    
    # 2. AI is too poor (Triggers RaiseError)
    success, act = blackhole_selecting(p1, core, auto=True)
    assert success is False
    assert core.error_raised is True
    
    # 3. AI Selection (Auto Target)
    p1.energy = 10
    p1.team = 0
    p1.real = False # P1 is AI
    
    p2 = Player(2)
    p2.team = 1 # P2 is Enemy AI
    p2.real = False 
    core.PlDict[2] = p2
    
    # Need population and snapshot data for AI targeting
    # Snap format: [HP, Energy, Place, Team, Real]
    core.status["pop"] = {0: {"sum": [1, 2]}, "all": 2}
    core.status["snap"] = {1: [10, 5, 0, 0, False], 2: [10, 5, 0, 1, False]}
    
    success, act = blackhole_selecting(p1, core, auto=True)
    assert success is True
    assert act.target == 2 # AI should automatically target the enemy (P2)


# ==========================================
# Test 8: Blackhole Complex Dealing (The Refund Logic!)
# Covers what happens when a Blackhole eats a Charge action.
# ==========================================
def test_blackhole_dealing_refund():
    core = InteractiveFakeCore([])
    p1 = Player(1)
    p2 = Player(2)
    
    # P2 initially had 5 energy, and is performing a Charge
    p2.energy = 5
    charge_act = Act(ownerID=2, key="1")
    
    # Simulate that P2 has already paid for charge (gained 1 energy -> 6)
    charge_act.payed = True
    p2.energy += 1 
    p2.acts = [charge_act]
    
    core.PlDict[1] = p1
    core.PlDict[2] = p2
    
    # Provide the price of charging for the blackhole's refund calculation
    core.ActDict["1"] = {"price": lambda act: -1} 
    
    # P1 uses blackhole on P2
    bh_act = Act(ownerID=1, key="7")
    bh_act.target = 2
    
    # [Act]
    blackhole_dealing(None, args=(bh_act, core))
    
    # [Assert]
    assert charge_act.acted is True
    assert "1" in p2.unable
    
    # The magical refund logic: 
    # Blackhole finds out the price was -1, and it was paid.
    # It forcibly deducts that 1 energy back! (6 -> 5)
    assert p2.energy == 5 

# ==========================================
# Test 6: Wave Selecting (Errors & AI)
# Covers poverty checks and human input validation.
# ==========================================
def test_wave_selecting_errors():
    p1 = Player(1)
    p1.place = 0
    p1.energy = 5 # Poor! (Needs 6)
    
    # 1. Human is too poor
    core = InteractiveFakeCore([])
    core.PlDict[1] = p1
    success, act = wave_selecting(p1, core, auto=False)
    assert success is False
    
    # 2. AI is too poor (Triggers RaiseError to warn developers)
    success, act = wave_selecting(p1, core, auto=True)
    assert success is False
    assert core.error_raised is True
    
    # 3. Human valid & invalid inputs
    p1.energy = 10
    core = InteractiveFakeCore(["abc", "9", "-1"]) # Error, Error, Valid(-1)
    core.PlDict[1] = p1
    success, act = wave_selecting(p1, core, auto=False)
    
    assert success is True
    assert act.seth == -1 # Finally selected down
    assert act.AOE is True


# ==========================================
# Test 7: Wave AI Auto-Aim (auto_AOEseth)
# Verifies if AI correctly calculates enemy density and ignores allies.
# ==========================================
def test_wave_auto_aim_complex():
    core = InteractiveFakeCore([])
    p1 = Player(1)
    p1.place = 0
    p1.team = 1
    p1.real = False  # P1 is an AI
    
    # Mocking Population Distribution
    # -1 (Down): 3 enemies (Team 2)
    #  0 (Same): 2 allies (Team 1) -> Should be ignored by AI
    #  1 (Up)  : 1 enemy (Team 2)
    core.status["pop"] = {
        -1: {"sum": [2, 3, 4], 2: [2, 3, 4]}, 
         0: {"sum": [1, 5],    1: [1, 5]},
         1: {"sum": [6],       2: [6]},
        "all": 6
    }
    
    # AI calculates optimal direction (Distance limit is 3)
    seth = auto_AOEseth(p1, core, distance=3)
    
    # Down (-1) has 3 enemies, Up (1) has 1 enemy. Same (0) has 0 enemies (allies subtracted).
    # AI must aim DOWN.
    assert seth == -1


# ==========================================
# Test 8: Wave Evaluator (crossfire_wave_eval)
# Covers the AOE line-of-sight targeting logic.
# ==========================================
def test_crossfire_wave_eval():
    core = InteractiveFakeCore([])
    core.BattleEnv["wave_distance"] = 3
    
    # P1: Attacker (Pos: 0)
    p1 = Player(1)
    p1.place = 0
    p1.team = 0
    p1.real = True
    core.PlDict[1] = p1
    
    # P2: Enemy in range, correct direction (Pos: 1) -> HIT!
    p2 = Player(2)
    p2.place = 1
    p2.team = 1
    p2.real = False
    core.PlDict[2] = p2
    
    # P3: Enemy in range, wrong direction (Pos: -1) -> MISS!
    p3 = Player(3)
    p3.place = -1
    p3.team = 1
    core.PlDict[3] = p3
    
    # P4: Ally in range, correct direction (Pos: 2)
    # Note: In Noah, real players don't have teammate immunity for AOEs unless specified!
    p4 = Player(4)
    p4.place = 2
    p4.team = 0
    p4.real = True 
    core.PlDict[4] = p4
    
    # Setup Wave Action (Aiming UP: 1)
    act = Act(1, "6")
    act.seth = 1 
    act.distant = 3
    act.lv = 5
    act.AOE = True
    act.channel = "shot-like"
    act.target = True
    act.attacked_players = []
    p1.acts = [act]
    
    # [Act] Evaluate the wave
    pipe_data = crossfire_wave_eval(None, (act, core))
    
    # [Assert]
    # P2 (Enemy Up) and P4 (Real Player Up) should be hit and take 5 damage.
    assert 2 in pipe_data["damage"]
    assert 4 in pipe_data["damage"]
    assert pipe_data["damage"][2] == 5

    # P3 is below P1, so he is totally safe.
    assert 3 not in pipe_data["damage"]
    
    # [Bonus Assert] What if nobody is hit?
    act_miss = Act(1, "6")
    act_miss.seth = 0 # Aim down, nobody is there
    act_miss.distant = 3
    act_miss.lv = 5
    act_miss.AOE = True
    act_miss.target = True
    act_miss.channel = "shot-like"
    act_miss.attacked_players = []
    p1.acts = [act_miss]

    pipe_data_miss = crossfire_wave_eval(None, (act_miss, core))

    # If no damage is dealt, the evaluator clears the message log to keep the UI clean
    assert pipe_data_miss["msg"] == []
