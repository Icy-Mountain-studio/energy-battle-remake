"""
/Energy-Battle-Remake/tests/test_act_utils.py
"""

import pytest
from noah import Player, Act
from actions.act_utils import (
    get_direction, 
    free_of_charge,
    crossfire_defend, 
    crossfire_do_damage,
    firecount,           
    crossfire_crash,     
    crossfire_reflect,
    summarize_crossfire_shots_msg,
    summarize_crossfire_hurt_msg,
    summarize_crossfire_misses_msg,   # <-- 新增
    summarize_crossfire_defend_msg,   # <-- 新增
    summarize_crossfire_reflect_msg   # <-- 新增
)


# ==========================================
# Preparation: Create Fake Objects
# This allows us to test the resolution logic without 
# starting the entire game UI and Mod system.
# ==========================================
class FakeUI:
    def get(self, key): 
        return key
    
    def out(self, *args, **kwargs): 
        pass

class FakeCore:
    def __init__(self):
        self.PlDict = {}
        self.ui = FakeUI()
        self.org_delay = 0
        self.BattleEnv = {"msg_summary_threshold": 2} 


# ==========================================
# Test 1: Pure logic test using parameterization
# ==========================================
@pytest.mark.parametrize("place1, place2, expected", [
    (3, 1, -1),   # From level 3 to 1, direction is down (-1)
    (1, 3, 1),    # From level 1 to 3, direction is up (1)
    (2, 2, 0),    # Same level, direction is straight (0)
    (-2, -5, -1), # Negative level coordinates
])
def test_get_direction(place1, place2, expected):
    assert get_direction(place1, place2) == expected


# ==========================================
# Test 2: Simple property function test
# ==========================================
def test_free_of_charge():
    # The price should always be 0 regardless of the Action passed in
    fake_act = Act(ownerID=1, key="any")
    assert free_of_charge(fake_act) == 0


# ==========================================
# Test 3: Core mechanism - Defend logic
# Verifies if the "defend" status successfully nullifies incoming damage.
# ==========================================
def test_crossfire_defend():
    # [Arrange] Prepare the testing environment
    core = FakeCore()
    attacker_act = Act(ownerID=1, key="2")
    
    # Create Player 2 and grant the "defend" status
    target_player = Player(id=2)
    target_player.status["defend"] = True
    core.PlDict[2] = target_player
    
    # Mock the pipe data: Player 2 is supposed to take 5 damage
    pipe_data = {
        "damage": {2: 5}, 
        "msg": [], 
        "statistics": {"defences": {}}
    }
    
    # [Act] Execute the defend evaluation function
    result_data = crossfire_defend(pipe_data, args=(attacker_act, core))
    
    # [Assert] Verify the results
    assert result_data["damage"][2] == 0  # Damage should be nullified
    
    # Verify that the successful defense message was generated
    message_generated = any("./defend" in msg[0] for msg in result_data["msg"])
    assert message_generated is True


# ==========================================
# Test 4: Final resolution - Real damage application
# Verifies if the pipe data correctly reflects on player's HP.
# ==========================================
def test_crossfire_do_damage():
    # [Arrange] Prepare the battlefield
    core = FakeCore()
    
    # Player 1 is the attacker (HP: 100)
    p1 = Player(id=1)
    p1.HP = 100
    core.PlDict[1] = p1
    attacker_act = Act(ownerID=1, key="2")
    
    # Player 2 is the target (HP: 10)
    p2 = Player(id=2)
    p2.HP = 10
    core.PlDict[2] = p2
    
    # Mock the pipe data: Player 2 is taking 3 damage
    pipe_data = {
        "damage": {2: 3}, 
        "signatures": {1: "2", 2: "2"},
        "msg": []
    }
    
    # [Act] Execute the final damage resolution
    crossfire_do_damage(pipe_data, args=(attacker_act, core))
    
    # [Assert] Check HP values
    assert p2.HP == 7    # 10 - 3 = 7, target took damage properly
    assert p1.HP == 100  # Attacker remains unharmed

def test_crossfire_do_damage_reflect():
    # [Additional Test] Verifies if reflected (negative) damage hurts the attacker.
    core = FakeCore()
    
    p1 = Player(id=1)
    p1.HP = 100
    core.PlDict[1] = p1
    attacker_act = Act(ownerID=1, key="2")
    
    p2 = Player(id=2)
    p2.HP = 10
    core.PlDict[2] = p2
    
    # Damage is -5, indicating the damage was reflected back to the attacker
    pipe_data = {
        "damage": {2: -5}, 
        "signatures": {1: "5", 2: "2"}, # Player 1 carries the signature of "5" (Reflect)
        "msg": []
    }
    
    crossfire_do_damage(pipe_data, args=(attacker_act, core))
    
    # [Assert]
    assert p1.HP == 95  # Attacker took the 5 reflected damage
    assert p2.HP == 10  # Target is unharmed

# ==========================================
# Test 5: Firecount (Complex Scenario)
# Covers Hits, Misses, AOE Deduplication, and Damage Accumulation
# ==========================================
def test_firecount_complex():
    core = FakeCore()
    
    # Attacker (P1) at pos 0
    p1 = Player(id=1)
    p1.place = 0
    core.PlDict[1] = p1
    
    # Target (P2) at pos 1
    p2 = Player(id=2)
    p2.place = 1
    core.PlDict[2] = p2
    
    # Act 1: A normal shot that MISSES (wrong direction)
    act_miss = Act(ownerID=1, key="2")
    act_miss.channel = "shot-like"
    act_miss.AOE = False
    act_miss.target = 2
    act_miss.seth = -1    # Aiming down, but P2 is up! (Miss)
    act_miss.distant = 5
    act_miss.lv = 2
    
    # Act 2: A normal shot that HITS
    act_hit = Act(ownerID=1, key="2")
    act_hit.channel = "shot-like"
    act_hit.AOE = False
    act_hit.target = 2
    act_hit.seth = 1      # Aiming up, correct!
    act_hit.distant = 5
    act_hit.lv = 1
    
    # Act 3: An AOE shot that targets P2, but P2 is already in attacked_players
    act_aoe = Act(ownerID=1, key="6")
    act_aoe.channel = "shot-like"
    act_aoe.AOE = True
    act_aoe.attacked_players = [p2] # Simulating P2 already hit by this AOE
    
    p1.acts = [act_miss, act_hit, act_aoe]
    
    # Pipe data for target P2
    pipe_data = {
        "msg": [], "damage": {2: 2}, # P2 already has 2 damage from somewhere else
        "signatures": {}, "target": 2,
        "statistics": {"shots":{}, "misses":{}, "defences":{}, "reflect":{}}
    }
    
    # [Act] Evaluate all shots from P1 towards P2
    pipe_data = firecount(core, None, p1, pipe_data)
    
    # [Assert]
    # 1. Miss logic covered
    assert 2 in pipe_data["statistics"]["misses"][2] 

    # 2. Hit logic & Damage Accumulation covered (Original 2 + New 1 = 3)
    assert pipe_data["damage"][2] == 3 
    
    # 3. AOE deduplication covered (AOE act should simply 'continue' and do nothing)
    assert p2 in act_aoe.attacked_players
    assert len(act_aoe.attacked_players) == 1


# ==========================================
# Test 6: Crossfire Crash (Complex Overpower Scenario)
# Covers Counter-misses, Complete Annihilation, and Damage Reversal
# ==========================================
def test_crossfire_crash_complex():
    core = FakeCore()
    
    # P1 (Attacker) at pos 0
    p1 = Player(id=1)
    p1.place = 0
    core.PlDict[1] = p1
    attacker_act = Act(ownerID=1, key="2")
    
    # P2 (Target taking 2 damage, firing back 5 damage -> Overpower!)
    p2 = Player(id=2)
    p2.place = 0
    core.PlDict[2] = p2
    act_p2 = Act(ownerID=2, key="2")
    act_p2.channel = "shot-like"
    act_p2.AOE = False
    act_p2.target = 1
    act_p2.seth = 0
    act_p2.distant = 5
    act_p2.lv = 5 # Overpowering level
    p2.acts = [act_p2]
    
    # P3 (Target taking 3 damage, firing back but MISSES!)
    p3 = Player(id=3)
    p3.place = 1
    core.PlDict[3] = p3
    act_p3 = Act(ownerID=3, key="2")
    act_p3.channel = "shot-like"
    act_p3.AOE = False
    act_p3.target = 1
    act_p3.seth = 1 # Aiming up, but P1 is below (Miss!)
    act_p3.distant = 5
    act_p3.lv = 2
    p3.acts = [act_p3]
    
    pipe_data = {
        "msg": [], 
        "damage": {2: 2, 3: 3}, # P2 and P3 are under attack
        "signatures": {},
        "statistics": {"shots":{}, "misses":{}, "defences":{}, "reflect":{}}
    }
    
    # [Act]
    pipe_data = crossfire_crash(pipe_data, args=(attacker_act, core))
    
    # [Assert]
    # P2 overpowered P1: (2 incoming - 5 counter = -3). Negative damage means P1 takes it.
    assert pipe_data["damage"][2] == -3
    assert pipe_data["signatures"][1] == "2" # Signature shifts to attacker
    
    # P3 missed P1: Still takes full 3 damage.
    assert pipe_data["damage"][3] == 3
    assert 1 in pipe_data["statistics"]["misses"][2]


# ==========================================
# Test 7: Crossfire Do Damage (Peace Scenario)
# Covers the 0 damage logic
# ==========================================
def test_crossfire_do_damage_complex():
    core = FakeCore()
    
    p1 = Player(id=1)
    p1.HP = 100
    core.PlDict[1] = p1
    attacker_act = Act(ownerID=1, key="2")
    
    p2 = Player(id=2)
    p2.HP = 10
    core.PlDict[2] = p2
    
    # Damage is exactly 0 (mitigated by crash or defense previously)
    pipe_data = {
        "damage": {2: 0}, 
        "signatures": {2: "2"},
        "msg": []
    }
    
    # [Act]
    crossfire_do_damage(pipe_data, args=(attacker_act, core))
    
    # [Assert]
    assert p1.HP == 100
    assert p2.HP == 10
    
    # Ensure the peace message is triggered
    message_generated = any("./peace" in msg[0] for msg in pipe_data["msg"])
    assert message_generated is True

# ==========================================
# Test 8: Message Summary (Shots) - Exceeds Threshold
# ==========================================
def test_summarize_crossfire_shots_msg_exceeds_threshold():
    core = FakeCore()
    core.BattleEnv["msg_summary_threshold"] = 2 
    act = Act(ownerID=1, key="6")

    pipe_data = {
        "msg": [
            ["/act/6/shot", [1, 2, 5]], 
            ["/act/6/shot", [1, 3, 5]],
            ["/act/6/shot", [1, 4, 5]],
            ["/share/endl", []]  # <--- 混入一个无关消息，为了触发 else 分支 (突破 94%!)
        ],
        "statistics": {
            "shots": {5: [2, 3, 4]} 
        }
    }

    result = summarize_crossfire_shots_msg(pipe_data, args=(act, core))
    
    # 3条细节消息变成了1条 summary，加上那条无关消息，一共是 2 条
    assert len(result["msg"]) == 2  
    assert result["msg"][0][0] == "./summary-shots"
    assert result["msg"][1][0] == "/share/endl"  # 无关消息被完好保留

def test_summarize_crossfire_shots_msg_under_threshold():
    core = FakeCore()
    core.BattleEnv["msg_summary_threshold"] = 10 
    act = Act(ownerID=1, key="6")

    pipe_data = {
        "msg": [["/act/6/shot", [1, 2, 5]], ["/act/6/shot", [1, 3, 5]]],
        "statistics": {"shots": {5: [2, 3]}}
    }
    result = summarize_crossfire_shots_msg(pipe_data, args=(act, core))
    assert len(result["msg"]) == 2 


# ==========================================
# Test 9: Hurt Message Summary
# ==========================================
def test_summarize_crossfire_hurt_msg():
    core = FakeCore()
    core.BattleEnv["msg_summary_threshold"] = 2
    act = Act(ownerID=1, key="6")

    pipe_data = {
        "msg": [
            ["./final-hurt", [2, 5, 10]],
            ["./final-hurt", [3, 5, 10]],
            ["./final-hurt", [4, 5, 10]],
            ["./peace", []] # 混入无关消息触发 else
        ],
        "damage": {2: 5, 3: 5, 4: 5} 
    }

    result = summarize_crossfire_hurt_msg(pipe_data, args=(act, core))
    
    assert len(result["msg"]) == 2
    assert result["msg"][0][0] == "./summary-damage"
    assert result["msg"][1][0] == "./peace"


# ==========================================
# Test 10: Parametrized Test for the rest (Misses, Defend, Reflect)
# We test 3 functions at once using parameterization!
# ==========================================
@pytest.mark.parametrize("summary_func, stat_key, msg_keyword, summary_keyword", [
    (summarize_crossfire_misses_msg, "misses", "/shot-miss", "./summary-misses"),
    (summarize_crossfire_defend_msg, "defences", "/defend", "./summary-defences"),
    (summarize_crossfire_reflect_msg, "reflect", "/reflect", "./summary-reflects"),
])
def test_other_summaries(summary_func, stat_key, msg_keyword, summary_keyword):
    core = FakeCore()
    core.BattleEnv["msg_summary_threshold"] = 2
    act = Act(ownerID=1, key="6")

    pipe_data = {
        "msg": [
            [f"prefix{msg_keyword}", [1, 2, 5]],
            [f"prefix{msg_keyword}", [1, 3, 5]],
            [f"prefix{msg_keyword}", [1, 4, 5]],
            ["/unrelated/message", []]
        ],
        "statistics": {
            stat_key: {5: [2, 3, 4]}
        }
    }

    # [Act] Execute the function passed in via parametrization
    result = summary_func(pipe_data, args=(act, core))
    
    # [Assert]
    assert len(result["msg"]) == 2
    assert result["msg"][0][0] == summary_keyword
    assert result["msg"][1][0] == "/unrelated/message"
