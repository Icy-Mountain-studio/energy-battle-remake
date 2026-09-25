"""
/Energy-Battle-Remake/stress_test.py
"""

import time
import noah
import ark_mod
import sys_tools_mod

def run_stress_test():
    print("Assembling stress test engine...")
    
    # 1. Load actual Mod logic
    mods = {
        "Ark": ark_mod.ModContents,
        "SysTool": sys_tools_mod.ModContents
    }

    # Inject missing language configuration required by ark_mod.ReloadMod
    mods["Ark"]["chosen_lang_code"] = "en_us"
    mods["SysTool"]["chosen_lang_code"] = "en_us"

    # 2. Modify parameters to extreme limits
    mods["Ark"]["BattleEnv"]["num"] = 1000
    mods["Ark"]["BattleEnv"]["real"] = 0          # Must be 0 to prevent blocking on human input
    mods["Ark"]["BattleEnv"]["initHP"] = 999999999999
    mods["Ark"]["BattleEnv"]["amount_of_actions_per_round"] = 10
    mods["Ark"]["BattleEnv"]["team_size"] = 10     # Free for all

    # Disable Blackhole ("7") to prevent instant rule-based elimination
    del mods["Ark"]["ActDict"]["7"]
    core = noah.Core(mods)

    # 3. Silent UI to prevent terminal I/O bottleneck
    class SilentUI:
        def __init__(self):
            self.typing_delay = 0
            self.workdir = "/"
            self.indent = 0
        
        def out(self, *args, **kwargs): 
            pass
        
        def inp(self, *args, **kwargs): 
            return ""
        
        def get(self, key): 
            return key
        
        def write_log(self): 
            pass

    # Override the UI initialized by the mod reload
    core.ui = SilentUI()

    # 4. Initialize game state
    core.mk_pldict()
    core.update_status()

    # 5. Start the stress loop
    print("\nExtreme Stress Test Started! 2000 actions per round. (Press Ctrl+C to stop)")
    print("=" * 50)
    
    start_time = time.time()
    round_count = 0

    try:
        while True:
            round_start = time.time()
            
            # Execute core game loop
            core.RunMainLoop()
            round_count += 1
            
            round_time = time.time() - round_start

            # Report status every round
            alive = len(core.PlDict)
            print(f"Round {round_count} completed | Alive: {alive} | Round Time: {round_time:.3f}s")

            if core.deaths:
                print(f"Players eliminated: {core.deaths}")

            if alive <= 1:
                break

    except KeyboardInterrupt:
        print("\nStress test aborted manually.")
    except Exception as e:
        print(f"\nEngine crashed! Reason: {e}")

    total_time = time.time() - start_time
    print("=" * 50)
    
    # Calculate average safely to avoid division by zero
    avg_time = total_time / round_count if round_count > 0 else 0
    print(f"Report: {round_count} Rounds | Total Time: {total_time:.2f}s | Avg Time/Round: {avg_time:.3f}s")


if __name__ == "__main__":
    run_stress_test()
