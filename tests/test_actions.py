"""
/Energy-Battle-Remake/tests/test_actions.py
"""

import pytest
import noah
from noah import Player, Act
from actions.act_utils import free_of_charge
from actions.charge import charge_price, charge_ai
from actions.move import get_available_steps, move_price, move_able, move_ai
from actions.blackhole import blackhole_price, blackhole_able, blackhole_ai
from actions.defend import defend_able, defend_ai, defend_selecting, defend_dealing
from actions.reflect import reflect_price, reflect_able, reflect_ai
from actions.shot import shot_price, shot_able, shot_ai
from actions.wave import wave_able, wave_ai

# ==========================================
# Fake Core
# ==========================================
class FakeCore:
    def __init__(self):
        self.BattleEnv = {"max_move_speed": 2, "map": 3, "max_consecutive_defend_times": 1}
        self.rounds = 1
        self.PlDict = {}
        self.ActDict = {}
        self.org_delay = 0
    class FakeUI:
        def out(self, *args, **kwargs): pass
    ui = FakeUI()

# ==========================================
# Test 1-4: Charge, Move, Blackhole, Defend (Previous & New Properties)
# ==========================================
def test_charge_properties():
    assert charge_price(Act(1, "1")) == -1
    p1 = Player(1)
    p1.energy = 0
    assert charge_ai({"self": p1}) == 300 

def test_move_properties():
    # Test Price & AI
    assert move_price(Act(1, "4")) == 1
    assert move_ai({"enmK": 0.5, "engK": 0.5}) == 0.5 * 0.5 * 50 + 10
    
    # Test Able
    core = FakeCore()
    p1 = Player(1)
    p1.place = 0
    p1.energy = 1
    assert move_able({"self": p1, "core": core}) is True
    p1.energy = 0 # No energy
    assert move_able({"self": p1, "core": core}) is False

def test_move_available_steps():
    core = FakeCore()
    p1 = Player(1)
    p1.place = 0
    assert set(get_available_steps(p1, core)) == {-2, -1, 1, 2}
    p1.place = 3
    assert set(get_available_steps(p1, core)) == {-2, -1}

def test_blackhole_properties():
    assert blackhole_price(Act(1, "7")) == 5
    p1 = Player(1)
    p1.energy = 5
    assert blackhole_able({"self": p1}) is True
    assert blackhole_ai({"self": p1}) == 35 

def test_defend_properties():
    core = FakeCore()
    p1 = Player(1)
    assert defend_ai({"engK": 0.5}) == 35.0
    core.BattleEnv["max_consecutive_defend_times"] = 0
    assert defend_able({"self": p1, "core": core}) == 0
    core.BattleEnv["max_consecutive_defend_times"] = 1
    assert defend_able({"self": p1, "core": core}) == 1

def test_defend_selecting_and_dealing():
    core = FakeCore()
    p1 = Player(1)
    core.BattleEnv["max_consecutive_defend_times"] = 2
    success, act = defend_selecting(p1, core, auto=False)
    assert success is True
    
    # Dealing Mock
    noah.time.sleep = lambda x: None # 拦截休眠
    p1.real = True  
    core.PlDict[1] = p1
    core.ActDict = {"3": {"price": free_of_charge}}
    defend_dealing(None, args=(Act(1, "3"), core))
    assert p1.status["defend"] is True

# ==========================================
# Test 5: Reflect Properties
# ==========================================
def test_reflect_properties():
    assert reflect_price(Act(1, "5")) == 2
    assert reflect_ai({"engK": 0.5}) == 25.0
    
    p1 = Player(1)
    p1.energy = 2
    assert reflect_able({"self": p1}) is True
    p1.status["reflect"] = True # Already reflecting
    assert reflect_able({"self": p1}) is False

# ==========================================
# Test 6: Shot Properties
# ==========================================
def test_shot_properties():
    act = Act(1, "2")
    act.lv = 3
    assert shot_price(act) == 3
    
    p1 = Player(1)
    p1.energy = 5
    assert shot_ai({"self": p1}) == 250
    assert shot_able({"self": p1, "side_enm": 1}) is True
    assert shot_able({"self": p1, "side_enm": 0}) is False # No enemies nearby

# ==========================================
# Test 7: Wave Properties
# ==========================================
def test_wave_properties():
    p1 = Player(1)
    
    # Able check (Needs 6 energy)
    p1.energy = 5
    assert wave_able({"self": p1}) is False
    p1.energy = 6
    assert wave_able({"self": p1}) is True
    
    # AI weight (energy * 20)
    assert wave_ai({"self": p1}) == 120

