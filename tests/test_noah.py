"""
/Energy-Battle-Remake/tests/test_noah.py
"""

import pytest
import gzip
from unittest.mock import patch
from noah import (
    explain, deep_merge, Override, table, clear_screen, import_module_from_path,
    Core, Act, PipeWorkFlow, Event, SelectAct_WorkerFunc, Player, IO
)

# ==========================================
# Preparation: Mock Mod Dictionary
# ==========================================
class MockUI:
    def __init__(self):
        self.typing_delay = 0
        self.workdir = ""
        self.indent = 0
        self.logs = []
    def out(self, *args, **kwargs): pass
    def inp(self, *args, **kwargs): return ""
    def get(self, key): return key
    def write_log(self): pass

mock_mod = {
    "mod_name": "MockMod",
    "mod_priority": 1,
    "BattleEnv": {
        "num": 2, "real": 0, "team_size": 1, "assist_team": 0,
        "ai_quality": 0, "initHP": 10, "amount_of_actions_per_round": 1,
        "msg_summary_threshold": 10
    },
    "ActDict": {
        "mock_act": {
            "priority": 1,
            "price": lambda act: 1,
            "able": lambda ctx: True,
            "human_only": False,
            "ai": [lambda ctx: 100],
            "weight": 1,
            "selecting_exec": lambda pl, core, auto: (True, Act(pl.id, "mock_act")),
            "dealing_exec": [lambda pd, args: pd]
        }
    },
    "ui": MockUI(),
    "CmdTable": {
        "-update_status": [lambda pd, args: pd],
        "-evaluate_ability_and_weights_context": [lambda pd, args: pd],
        "-MainLoop": [lambda pd, args: pd]
    }
}
mock_mods_dict = {"MockMod": mock_mod}


# ==========================================
# Group 1: Utils
# ==========================================
@pytest.mark.parametrize("template, values, expected", [
    ("Player $0 has $1 HP.", ["Alice", 10], "Player Alice has 10 HP."),
    ("$1 hits $0.", ["Bob", "Alice"], "Alice hits Bob."),
    ("Player $0 has $1 HP.", ["Alice"], "Player Alice has $1 HP."),
    ("Look at $999!", [], "Look at $999!"),
    ("", ["Alice"], ""),
    ("$0", [], "$0"),
    ("Pos: $0", [3.14], "Pos: 3.14"),
])
def test_explain(template, values, expected):
    assert explain(template, values) == expected

def test_deep_merge():
    low = {"a": 1, "config": {"x": 10}, "items": [1]}
    high = {"config": {"y": 30}, "items": [2], "b": None, "override": Override({"z": 1})}
    res = deep_merge(low, high)
    assert res["config"] == {"x": 10, "y": 30}
    assert res["items"] == [1, 2]
    assert "b" not in res
    assert res["override"] == {"z": 1}

def test_table():
    data = [[1, "A"], [2, "B"]]
    assert table(data, "ID:$0 Name:$1", spl="|") == "ID:1 Name:A|ID:2 Name:B"

@patch('os.system')
def test_clear_screen(mock_sys):
    with patch('os.name', 'nt'):
        clear_screen()
        mock_sys.assert_called_with('cls')
    with patch('os.name', 'posix'):
        clear_screen()
        mock_sys.assert_called_with('clear')

def test_import_module_from_path(tmp_path):
    p = tmp_path / "dummy_mod.py"
    p.write_text("x = 42")
    mod = import_module_from_path(str(p))
    assert mod.x == 42
    with pytest.raises(FileNotFoundError):
        import_module_from_path("non_existent_file.py")


# ==========================================
# Group 2: IO Class
# ==========================================
def test_io_basic_and_paths():
    io = IO(exp={"/absolute": "ABS", "/relative": "REL"})
    io.workdir = "/test/"
    assert io.dealpath("/absolute") == "/absolute"
    assert io.dealpath("./relative") == "/test/relative"
    assert io.get("/absolute") == "ABS"
    assert io.get("unknown") == "<haven't translated>"

@patch('builtins.print')
def test_io_out_workflows(mock_print):
    io = IO(exp={"/test": "Hello"})
    io.out(["/test", "/test"], mode="h")
    assert len(io.history) == 2
    
    io.indent = 1 
    io.out("Direct", directly=True, mode="shl", indent=True, color="RED")
    assert "\033[38;5;210m    Direct\033[0m" in io.history[-1]
    
    io.out("NONE", directly=True, mode="shl")
    assert "NONE" not in io.history[-1]

@patch('sys.stdout.write')
def test_io_typewriter(mock_write):
    io = IO(delay=0.01)
    text = "\033[31mRed\033[0mText"
    io._typewriter_print(text, speed_stability=0)
    assert mock_write.call_count > 0

@patch('builtins.input', return_value="UserInp")
def test_io_inp(mock_input):
    io = IO()
    res = io.inp("Prompt", directly=True, mode="hl")
    assert res == "UserInp"
    assert "UserInp" in io.history[-1]
    assert "UserInp" in io.logs[-1]

def test_io_write_log(tmp_path):
    log_file = tmp_path / "test.log.gz"
    io = IO(logpath=str(log_file))
    io.logs = ["Log1", "Log2"]
    io.write_log()
    assert len(io.logs) == 0
    with gzip.open(str(log_file), 'rt') as f:
        content = f.read()
        assert "Log1\nLog2" in content
    with patch('gzip.open', side_effect=PermissionError):
        io.logs = ["Log3"]
        io.write_log() 


# ==========================================
# Group 3: Player Mechanics & Select Loop
# ==========================================
def test_player_hurted():
    core = Core(mock_mods_dict)
    core.PlDict[2] = Player(2)
    p1 = Player(1)
    p1.HP = 10
    
    p1.hurted(3, origin=2, act_key="shot", core=core)
    assert p1.HP == 7
    assert core.PlDict[2].outd == 3
    
    p1.hurted(100, origin=2, act_key="wave", core=core)
    assert p1.HP == 0
    # [FIX] hurted only logs the damage. Kills are processed in rm_deaths!
    assert p1.HPlog[-1][1] == 2 

def test_player_select_complex():
    mock_mod_local = {
        "mod_name": "Mock", 
        # [FIX] Provided complete BattleEnv variables required by mk_pldict
        "BattleEnv": {
            "amount_of_actions_per_round": 2, "num": 2, "real": 1, 
            "team_size": 1, "assist_team": 0, "ai_quality": 0, "initHP": 10
        },
        "ActDict": {
            "valid_act": {
                "human_only": False, "able": lambda c: True, "priority": 1,
                "ai": [lambda c: 10], "weight": 1,
                "selecting_exec": lambda p, c, auto: (True, Act(p.id, "valid_act"))
            },
            "quit_act": { 
                "human_only": False, "able": lambda c: True, "priority": 1,
                "ai": [lambda c: 1], "weight": 1,
                "selecting_exec": lambda p, c, auto: (True, None) 
            }
        },
        "ui": IO()
    }
    core = Core({"Mock": mock_mod_local})
    core.mk_pldict()
    p1 = Player(1)
    p1.real = True
    
    with patch.object(core.ui, 'inp', side_effect=["bad_id", "quit_act", "", "valid_act"]):
        p1.unable = ["quit_act"] 
        def sneaky_exec(p, c, a): c.exit_game = True; return False, None
        core.ActDict["valid_act"]["selecting_exec"] = sneaky_exec
        acts = p1.select(core)
        assert len(acts) == 0 
        
    p2 = Player(2)
    p2.real = False
    core.exit_game = False
    core.ActDict["valid_act"]["selecting_exec"] = lambda p, c, auto: (True, Act(p.id, "valid"))
    p2.unable = ["valid_act", "quit_act"] 
    p2.select(core)
    assert 2 in core.deaths


# ==========================================
# Group 4: Core & Event Mechanics 
# ==========================================
# [FIX] Patch input so if RaiseError is accidentally triggered, it won't crash pytest
@patch('builtins.input', return_value="")
def test_core_lifecycle(mock_input):
    mock_mod_local = {
        "mod_name": "M", 
        "BattleEnv": {"num": 1, "real": 0, "ai_quality": 0, "team_size": 1, "assist_team": 0, "initHP": 10, "amount_of_actions_per_round": 1},
        "ActDict": {"act1": {"priority": 1, "human_only": False, "able": lambda c: True, "ai": [lambda c: 1], "weight": 1, "price": lambda a: 0, "selecting_exec": lambda p, c, a: (True, Act(1, "act1")), "dealing_exec": []}},
        "ui": IO(),
        # [FIX] Added the missing command that caused the cascade failure!
        "CmdTable": {
            "-MainLoop": [lambda p, c: p], 
            "-update_status": [lambda p, c: p],
            "-evaluate_ability_and_weights_context": [lambda p, c: p]
        }
    }
    core = Core({"M": mock_mod_local})
    core.mk_pldict()
    
    core.SelectAct()
    core.DealAct()
    core.clean_round()
    core.round_title()
    core.update_status()
    core.RunMainLoop()
    
    snap = core.debug_snapshot()
    env_snap = core.battle_env_snapshot()
    assert "P1" in snap
    assert "num" in env_snap
    
def test_events():
    core = Core(mock_mods_dict)
    evt = Event("-FakeCmd", "Domain", {})
    core.EventBus.append(evt)
    
    core.DealEvents()
    assert evt.has_happened is True
    
    evt.has_happened = True
    core.EventBus.append(evt)
    core.DealEvents() 


# ==========================================
# Group 5: Error Handling & Robustness
# ==========================================
@patch('builtins.input', return_value="") 
def test_core_init_error_handling_fallback(mock_builtin_input):
    core = Core({}) 
    assert isinstance(core, Core)
    mock_builtin_input.assert_called_once()
    args, kwargs = mock_builtin_input.call_args
    printed_error_msg = args[0]
    assert "ERROR" in printed_error_msg
    assert "MergedMod" in printed_error_msg 
