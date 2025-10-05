"""
Terminal Compatibility Quick Check for Energy Battle
Only checks the essentials: terminal width and color support
"""

import os
import sys
import shutil
from noah import C

def check_terminal():
    """
    Quick check if terminal is suitable for the game
    Returns: (passed, warnings_list)
    """
    warnings = []

    # Enable Windows ANSI support (silent execution)
    if os.name == 'nt':
        os.system("")

    # 1. Check terminal width
    try:
        cols, rows = shutil.get_terminal_size(fallback=(80, 24))
        if cols < 80:
            warnings.append(f"Terminal width is narrow ({cols} cols), recommend at least 80")
    except:
        pass  # Skip if unable to detect

    # 2. Check color support
    term = os.environ.get('TERM', '').lower()
    has_color = (
        'color' in term or
        '256' in term or
        os.environ.get('COLORTERM') or
        os.name != 'nt'  # Non-Windows usually supports color
    )

    if not has_color:
        warnings.append("Terminal may not support colors, game playable but may show artifacts")

    return len(warnings) == 0, warnings

def show_check_result():
    """Display check result (with interaction)"""
    print(f"{C['CYAN']}═══ Terminal Check ═══{C['RESET']}")

    passed, warnings = check_terminal()

    if passed:
        print(f"{C['GREEN']}✓ Terminal compatible{C['RESET']}\n")
        return True
    else:
        print(f"{C['YELLOW']}⚠ Issues detected:{C['RESET']}")
        for w in warnings:
            print(f"  • {w}")
        if warnings:
            print()

        return True

def silent_check():
    """Silent check (no output, returns bool only)"""
    passed, _ = check_terminal()
    return passed

def quick_color_test():
    """One-line color test"""
    print(f"{C['RED']}Red {C['GREEN']}Green {C['YELLOW']}Yellow {C['CYAN']}Cyan {C['MAGENTA']}Magenta{C['RESET']}")
    print("These should be different colors\n")

if __name__ == "__main__":
    if show_check_result():
        print("Running color test:")
        quick_color_test()
