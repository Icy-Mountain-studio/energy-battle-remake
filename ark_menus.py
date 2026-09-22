"""
/Energy-Battle-Remake/ark_menus.py
Reusable setting and mod manager menus extracted directly from ark.py.
"""

import noah
from noah import C


def Menu_Setting(ui, env_dict, on_save=None):
    """
    Directly ported from ark.py Setting().
    Accepts dynamic ui and env_dict references.
    """
    noah.clear_screen()
    org_delay = ui.typing_delay
    ui.typing_delay = 0.005
    ui.workdir = "/ark/setting/"

    while True:
        noah.clear_screen()
        ui.out("./title")
        ui.out("./intro")
        
        ui.workdir = "/ark/setting/"
        ui.out("./current")

        # Display current settings
        display_data = []
        for num, key in env_dict["setting_options"].items():
            value_display = f"{C['CYAN']}{env_dict.get(key, 'N/A')}{C['RESET']}"

            display_data.append((
                f"{C['YELLOW']}{num}{C['RESET']}",
                ui.get(f"./desc/{key}"),
                value_display
            ))

        ui.out(noah.table(display_data, f"{C['YELLOW']}$0{C['RESET']}. $1 {C['YELLOW']}|{C['RESET']} {C['CYAN']}$2{C['RESET']}"), directly=True)
        ui.out("/share/endl")

        choice = ui.inp("./prompt")
        ui.out("/share/endl")

        if choice == "":
            ui.inp("./exit")
            noah.clear_screen()
            break

        if choice in env_dict["setting_options"]:
            setting_key = env_dict["setting_options"][choice]
            setting_name = ui.get(f"./desc/{setting_key}")
            current_value = env_dict.get(setting_key)
            new_value_str = ui.inp("./input-new", imp=[current_value])
            ui.out("/share/endl")

            if new_value_str == "":
                # Remain the same
                ui.out("./updated", imp=[setting_name, current_value])
                ui.out("/share/endl")
                continue
            else:
                try:
                    env_dict[setting_key] = int(new_value_str)
                    if on_save:
                        on_save()
                except ValueError:
                    ui.out("./error-not-int")

            ui.out("/share/endl")

        else:
            ui.out("./error-invalid-choice")
            ui.out("/share/endl")

    ui.typing_delay = org_delay


def Menu_ModManager(ui, mods, lang_code, is_core=False, on_reload=None):
    """
    Directly ported from ark.py ModManager().
    is_core: False if mods is a dict (from ark.py), True if mods is a list (from core.Mods).
    """
    ui.workdir = "/ark/mod_manager/"
    noah.clear_screen()
    ui.out("./title")

    while True:
        # Determine whether to sort dict values or list items
        if is_core:
            mod_list = sorted(mods, key=lambda d: d.get("mod_priority", 0), reverse=True)
        else:
            mod_list = sorted(mods.values(), key=lambda d: d.get("mod_priority", 0), reverse=True)
            
        ui.indent = 0
        if mods:
            org_delay = ui.typing_delay
            ui.typing_delay = 0
            ui.out("./demo")
            ui.out(noah.table([(mod_list.index(mod)+1, mod["mod_name"], mod.get("mod_priority", 0)) for mod in mod_list], f"{C['CYAN']}$0{C['RESET']}.\t$1\t{C['GRAY']}[$2]{C['RESET']}", "\n"), directly=True)
            ui.typing_delay = org_delay
        ui.out([
                "/share/endl",
                "./operation-add",
                "./operation-remove",
                "./operation-adjust-priority",
                "/share/endl",
            ])
        operation_code = ui.inp(["./ask-for-operation", "/share/endl"])
        ui.indent += 1

        if operation_code == "1":
            try:
                ui.out("/share/endl")
                user_input = ui.inp("./new_mod_path")
                ui.out("/share/endl")
                if user_input:
                    new_mod = noah.import_module_from_path(user_input)
                else:
                    continue
            except FileNotFoundError:
                ui.out(["./file_system_failure", "/share/endl"], color="RED")
                continue
            except Exception:
                ui.out(["./import_failure", "/share/endl"], color="RED")
                continue

            try:
                new_mod.ModContents["chosen_lang_code"] = lang_code
                if is_core:
                    mods.append(new_mod.ModContents)
                else:
                    mods[new_mod.ModContents["mod_name"]] = new_mod.ModContents
                if on_reload:
                    on_reload()
            except (AttributeError, KeyError):
                ui.out(["./metadata_incomplete", "/share/endl"], color="MA")
                continue

            ui.out(["./add-succeed", "/share/endl"], imp=[new_mod.ModContents["mod_name"]], color="GREEN")

        elif operation_code == "2":
            mod_going_to_remove = ui.inp("./ask-for-modcode-to-remove")
            try:
                if not mod_going_to_remove:
                    continue
                mod_going_to_remove = int(mod_going_to_remove) - 1
                name = mod_list[mod_going_to_remove]["mod_name"]
                ui.out("./selected", imp=[name])
                
                if is_core:
                    mods.remove(mod_list[mod_going_to_remove])
                else:
                    del mods[name]
                if on_reload:
                    on_reload()
                    
                ui.out("./remove-succeed", imp=[name], color="GREEN")
            except (KeyError, IndexError):
                ui.out("/share/not-found", color="RED")
            except ValueError:
                ui.out("./error-int", color="RED")
            finally:
                ui.out("/share/endl")

        elif operation_code == "3":
            mod_going_to_reprior = ui.inp("./ask-for-modcode-to-reprior")
            try:
                if not mod_going_to_reprior:
                    ui.out("/share/endl")
                    continue
                mod_going_to_reprior = int(mod_going_to_reprior) - 1
            except ValueError:
                ui.out(["./error-int", "/share/endl"], color="RED")
                continue

            try:
                ui.out("./selected", imp=[mod_list[mod_going_to_reprior]["mod_name"]])
                new_priority = float(ui.inp("./ask-new-priority-for-mod"))
                if new_priority.is_integer():
                    new_priority = int(new_priority)
                mod_list[mod_going_to_reprior]["mod_priority"] = new_priority
                if on_reload:
                    on_reload()
                ui.out("./priority-modified-succeed", imp=[mod_list[mod_going_to_reprior]["mod_name"], new_priority], color="GREEN")
                ui.out("/share/endl")
            except ValueError:
                ui.out("./float-or-int", color="RED")
            except (KeyError, IndexError):
                ui.out("/share/not-found", color="RED")
            finally:
                ui.out("/share/endl")

        elif not operation_code:
            ui.out("/share/endl")
            break
        else:
            ui.out("/share/not-found", color="RED")

    ui.indent = 0
    ui.inp("./exit", color="YELLOW")
    noah.clear_screen()
