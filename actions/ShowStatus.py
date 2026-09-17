from actions.act_utils import able_forever, free_of_charge

def ShowStatus_selecting(pl, core, auto):
    """Selection logic for 'ShowStatus' (human-only utility action)."""
    core.ui.indent += 1
    all_teams = [i[3] for i in core.status["snap"].values()]
    ask = core.ui.inp('./select-team')
    try:
        selected_team_ids = [int(ask)]
    except ValueError:
        selected_team_ids = list(set(all_teams)) # Show all teams if input is invalid/empty

    show_pls = []
    for i in core.PlDict.values():
        if i.team in selected_team_ids:
            show_pls.append((i.id, i.HP, i.energy, i.place, i.outd, len(i.kills)))

    org = core.ui.typing_delay
    core.ui.typing_delay = 0
    for s in show_pls:
        core.ui.out('./main-exp', imp=s, color="YELLOW")
    core.ui.out('/share/endl')
    core.ui.typing_delay = org
    core.ui.indent -= 1

    return (False, None)

ActionProperties = { # Show Status
        "price": free_of_charge, "priority": 0, "able": able_forever,
        "human_only": True, "ai": [None], "weight": 0,
        "selecting_exec": ShowStatus_selecting, "dealing_exec": [],
    }
