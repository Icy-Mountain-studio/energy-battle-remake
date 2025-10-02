"""
Project Ark: The Frontend for Energy Battle - Remake

Having the Noah backend isn't enough.
We need a frontend as elegant as the Noah backend: ark.py
I hereby name it the Ark Frontend!

Together, they create:
Energy Battle - Remake v1.2-5

This is a turn-based, many-vs-many combat game with a command-line interface.

The project has undergone two complete rewrites since its inception:
Energy Battle -> Energy Battle-Remake 1.1 -> Energy Battle-Remake 1.2

Energy Battle-Remake 1.2 utilizes my newly developed game kernel,
which I call the "Noah Kernel".

As you can see, the project is still far from complete.

Project initiated: 2025.8.2
Last updated: 2025.10.2
"""

import noah  # Import the Noah kernel, with all due ceremony.
from noah import C

Expression = {
"zh_cn": {
    '/ark/round-title': "第$0回合\n"+'-'*10,
    '/share/endl': "",
    '/share/dr-endl': "\n",
    '/core/ask-for-act': f"{C['WHITE']}玩家$0 {C['GREEN']}[血量$1 能量$2 位置$3]{C['RESET']}\n推荐$4 >  ",
    '/core/selected': '已自动选择$0',
    '/core/no-available-act': "玩家$0没有可用行动 将在本回合死亡",
    '/core/actlist-title': f"可选行动\n-------\n   行动  {C['CYAN']}(价格){C['RESET']}\n",
    '/core/ai-dealing': f"{C['MAGENTA']}AI正在决策...",
    '/core/ai-completed': f"AI决策已完成.{C['RESET']}",

    '/act/1/name': f"{C['YELLOW']}充能{C['RESET']}",
    '/act/2/name': f"{C['RED']}射击{C['RESET']}",
    '/act/3/name': f"{C['CYAN']}防御{C['RESET']}",
    '/act/4/name': f"{C['GREEN']}移动{C['RESET']}",
    '/act/5/name': f"{C['MAGENTA']}反射{C['RESET']}",
    '/act/6/name': f"{C['CYAN']}能量波{C['RESET']}",
    '/act/7/name': f"{C['MAGENTA']}黑洞{C['RESET']}",
    '/act/rl/name': f"{C['WHITE']}查看游戏说明{C['RESET']}",
    '/act/stt/name': f"{C['WHITE']}全场玩家状态{C['RESET']}",
    '/act/bk/name': f"{C['WHITE']}退出战场{C['RESET']}",

    '/act/1/price': "增加1点能量",
    '/act/2/price': "1点能量/发",
    '/act/3/price': "0",
    '/act/4/price': "0",
    '/act/5/price': "2",
    '/act/6/price': "4",
    '/act/7/price': "5",
    '/act/rl/price': "0",
    '/act/stt/price': "0",
    '/act/bk/price': "0",

    '/act/1/dealed': f"{C['YELLOW']}玩家$0向真空借走了1点能量 现在拥有$1点能量{C['RESET']}",

    '/act/2/ask-target': "目标(直接回车则取消) > ",
    '/act/2/cancel': f"{C['YELLOW']}[射击已取消...]{C['RESET']}",
    '/act/2/ask-seth': f"射击方向\n    {C['YELLOW']}[ 1向上 / 0平射 / -1向下 / 不填自动 ] {C['RESET']}",
    '/act/2/ask-lv': f"发射的能量大小 {C['YELLOW']}[1/2/3/留空自动] {C['RESET']}",
    '/act/2/auto-lv': f"已选择{C['YELLOW']}$0{C['RESET']}级",
    '/act/2/auto-seth': f"已替你输入{C['YELLOW']}$0{C['RESET']}",
    '/act/2/has-sent': f"{C['YELLOW']}[能量已发射...]{C['RESET']}\n",

    '/act/2/battle': "-- 玩家$0在第$1层向$2方向发射了能量 --",
    '/act/2/shot-miss': "玩家$0的$2发能量飞向玩家$1 但是偏了..",
    '/act/2/shot': "玩家$0的$2发能量飞向玩家$1",
    '/act/2/crash': "两人有$0发能量已经互相湮灭",
    '/act/2/anti': "玩家$0射出了$2发能量来反击玩家$1",
    '/act/2/reflect': "玩家$0的$1发能量被反射了！",
    '/act/2/defend': "玩家$0的防御抵挡住了$1点伤害",
    '/act/2/final-hurt': "最终 玩家$0承受$1点伤害 剩余HP $2",
    '/act/2/wonderful': "精彩的周旋！",
    '/act/2/peace': "最终没有人受伤",

    '/act/2/error-existPL': "这个玩家不存在或者已经淘汰了",
    '/act/2/error-self': "你选择的玩家是AI队友或者自己\n",
    '/act/2/error-int': "请输入一个整数",
    '/act/2/error-int-or-empty': "请输入一个整数或不填",
    '/act/2/error-no-lv': "没有那个发射等级喔",
    '/act/2/error-no-energy': "能量不够喔",
    '/act/2/error-no-seth': "没有那个发射方向喔",

    '/act/3/dealed': f"{C['CYAN']}玩家$0防御了一回合{C['RESET']}",

    '/act/4/ask': f"请输入想要上升（负数则是下降）的层数{C['GREEN']}[-$0~$0]{C['RESET']} ",
    '/act/4/dealed': f"{C['GREEN']}玩家$0移动了$1层并抵达了第$2层{C['RESET']}",
    '/act/4/out-of-map': "这样会越过地图边界的\n",
    '/act/4/error-int': "请输入一个整数\n",

    '/act/5/dealed': f"{C['MAGENTA']}玩家$0启用了反射{C['RESET']}",

    '/act/stt/main-exp': "玩家$0 / 血量$1 能量$2 位置$3 输出$4 击杀$5",
    '/act/stt/select-team': "查看哪个队伍的所有玩家的状态? [0~$0 空则全场] ",

    '/act/6/battle': "-- 玩家$0在第$1层向$2方向放出了能量波 --",
    '/act/6/ask-seth': f"射击方向\n    {C['CYAN']}[ 1向上 / 0平射 / -1向下 / 不填自动 / 空格取消 ] {C['RESET']}",
    '/act/6/cancel': f"{C['CYAN']}[能量波已取消...]{C['RESET']}",
    '/act/6/has-sent': f"{C['CYAN']}[能量波已发射...]{C['RESET']}\n",
    '/act/6/error-no-seth': "这个发射方向不存在",
    '/act/6/error-int-or-empty': "请输入一个整数或不填",
    '/act/6/shot-miss': "玩家$0能量波的$2发能量未能击中玩家$1",
    '/act/6/shot': "玩家$0的$2发能量正飞向玩家$1",
    '/act/6/crash': "$0点能量互相湮灭",
    '/act/6/reflect': "玩家$0的能量波被反射了！",
    '/act/6/anti': "玩家$0也发射了$2发能量 并反击玩家$1的能量波",
    '/act/6/defend': "玩家$0的防御抵挡住了$1点伤害",
    '/act/6/final-hurt': "玩家$0承受$1点伤害 剩余HP $2",
    '/act/6/wonderful': "能量波威力巨大！",
    '/act/6/peace': "NONE",
    '/act/6/auto-seth': f"已替你输入{C['CYAN']}$0{C['RESET']}",

    '/act/7/ask': "请输入你要封禁行动的对象 ",
    '/act/7/result': f"{C['MAGENTA']}玩家$0的行动$1{C['MAGENTA']}已被玩家$2的黑洞永远吞噬{C['RESET']}",

    '/share/poor': f"{C['MAGENTA']}你太穷了 要不还是先去充能吧。。{C['RESET']}",
    '/share/out-of-range': "请输入一个范围内的值",
    '/share/not-found': "目标不存在",
    '/share/unable': f"{C['RED']}此行动不可用{C['RESET']}",

    '/core/dead': f"{C['RED']}\n共$1位玩家在本回合死亡\n$0号{C['RESET']}",
    '/core/dead-team': "队伍$0阵亡$1人",
    '/core/human-dead': f"{C['RED']}\n玩家$0已死亡\n最后一击: 玩家$2使用$3{C['RED']}对你造成$1点伤害\n按回车键确认{C['RESET']}",
    '/ark/game-over-nobody': f"{C['CYAN']}\n///// 游戏结束 无人存活 /////{C['RESET']}\n",
    '/ark/game-over': f"{C['CYAN']}\n///// 游戏结束 玩家$0胜利 /////{C['RESET']}\n",
    "/ark/game-over-by-team": f"{C['CYAN']}\n///// 游戏结束 队伍$0胜利 /////{C['RESET']}\n",
    '/ark/welcome': "# 能量之战-重制版 1.2-5 #\n",

    '/act/1/rule': f"{C['YELLOW']}充能{C['RESET']} - {C['WHITE']}把你的能量增加1点{C['RESET']}",
    '/act/3/rule': f"{C['CYAN']}防御{C['RESET']} - {C['WHITE']}在本回合内进入防御状态 攻击类行动无法伤害你{C['RESET']}",
    '/act/5/rule': f"{C['MAGENTA']}反射{C['RESET']} - {C['WHITE']}当有人对你使用攻击类行动的时候 反过来让对方承受伤害{C['RESET']}",
    '/act/6/rule': f"{C['CYAN']}能量波{C['RESET']} - {C['WHITE']}向某个方向发射AOE攻击 面向选定方向上的全部玩家 伤害5点{C['RESET']}",
    '/act/7/rule': f"{C['MAGENTA']}黑洞{C['RESET']} - {C['WHITE']}吞噬选定玩家本回合的行动 使它无效并不得再使用{C['RESET']}",

    '/ark/opt-title': "请选择\n-------\n",
    '/ark/opt/1': "开启战局",
    '/ark/opt/2': "配置战局",
    '/ark/opt/3': "退出游戏",
    '/ark/break': "已退出战局",
    "/ark/exit": f"{C['YELLOW']}[即将退出游戏]{C['RESET']}",

    '/ark/setting/title': f"{C['CYAN']}// 战场参数配置{C['RESET']}",
    '/ark/setting/intro': "您可以通过这里调整战场的默认参数\n请选择要修改的项 或直接回车返回主菜单\n",
    '/ark/setting/current': "当前设置",
    '/ark/setting/prompt': "请输入要修改的参数编号 [回车返回]\n-> ",
    '/ark/setting/input-new': "请输入新的值(当前 $0)\n[回车保持不变] -> ",
    '/ark/setting/updated': "参数$0已更新为 $1。",
    '/ark/setting/exit': "战场配置完成 祝您游戏愉快！",
    '/ark/setting/error-invalid-choice': f"{C['RED']}没有这个选项... 请重新选择{C['RESET']}",
    '/ark/setting/error-not-int': f"{C['RED']}输入无效 需要整数{C['RESET']}",
    '/ark/setting/error-non-negative': "这个参数必须是非负数",
    '/ark/setting/error-real-num-mismatch': "真人玩家数量($0)不能超过总玩家数量($1) 已自动修正",
    '/ark/setting/error-map-range': "地图大小(当前$0)必须是正整数 且建议范围在1到10之间",

    '/ark/setting/desc/num': "总玩家数量",
    '/ark/setting/desc/real': "真人玩家数量",
    '/ark/setting/desc/map': "地图大小",
    '/ark/setting/desc/initHP': "每位玩家的初始血量",
    '/ark/setting/desc/shot_distance': '"射击"的射程',
    '/ark/setting/desc/wave_distance': '"能量波"的射程',
    '/ark/setting/desc/team_size': "每个AI队伍的人数[1-各自为战]",
    '/ark/setting/desc/assist_team': "第一个AI队伍是否与人类合作？[0-No 1-Yes]",
},
"en_us": {
    '/ark/round-title': "Round $0\n"+'-'*10,
    '/share/endl': "",
    '/share/dr-endl': "\n",
    '/core/ask-for-act': f"{C['WHITE']}Player $0 {C['GREEN']}[HP $1 Energy $2 Pos $3]{C['RESET']}\nSuggest $4 >  ",
    '/core/selected': 'Auto-selected $0',
    '/core/no-available-act': "Player $0 has no available actions and will be eliminated this turn.",
    '/core/actlist-title': f"Available Actions\n-------------\n   Action  {C['CYAN']}(Cost){C['RESET']}\n",
    '/core/ai-dealing': f"{C['MAGENTA']}AI is making a decision...",
    '/core/ai-completed': f"AI decision complete.{C['RESET']}",

    '/act/1/name': f"{C['YELLOW']}Charge{C['RESET']}",
    '/act/2/name': f"{C['RED']}Shoot{C['RESET']}",
    '/act/3/name': f"{C['CYAN']}Defend{C['RESET']}",
    '/act/4/name': f"{C['GREEN']}Move{C['RESET']}",
    '/act/5/name': f"{C['MAGENTA']}Reflect{C['RESET']}",
    '/act/6/name': f"{C['CYAN']}Energy Wave{C['RESET']}",
    '/act/7/name': f"{C['MAGENTA']}Black Hole{C['RESET']}",
    '/act/rl/name': f"{C['WHITE']}View Game Rules{C['RESET']}",
    '/act/stt/name': f"{C['WHITE']}View All Player Status{C['RESET']}",
    '/act/bk/name': f"{C['WHITE']}Surrender{C['RESET']}",

    '/act/1/price': "+1 Energy",
    '/act/2/price': "1 Energy/shot",
    '/act/3/price': "0",
    '/act/4/price': "0",
    '/act/5/price': "2",
    '/act/6/price': "4",
    '/act/7/price': "5",
    '/act/rl/price': "0",
    '/act/stt/price': "0",
    '/act/bk/price': "0",

    '/act/1/dealed': f"{C['YELLOW']}Player $0 drew 1 energy from the void. Now has $1 energy.{C['RESET']}",

    '/act/2/ask-target': "Target (press Enter to cancel) > ",
    '/act/2/cancel': f"{C['YELLOW']}[Shot cancelled.]{C['RESET']}",
    '/act/2/ask-seth': f"Shooting direction\n    {C['YELLOW']}[ 1 up / 0 straight / -1 down / empty for auto ]{C['RESET']} ",
    '/act/2/ask-lv': f"Energy level to fire {C['YELLOW']}[1/2/3/empty for auto]{C['RESET']} ",
    '/act/2/auto-lv': f"Auto-selected level {C['YELLOW']}$0{C['RESET']}.",
    '/act/2/auto-seth': f"Auto-selected direction {C['YELLOW']}$0{C['RESET']}.",
    '/act/2/has-sent': f"{C['YELLOW']}[Energy projectile launched...]{C['RESET']}\n",

    '/act/2/battle': "-- Player $0 fires energy from level $1 in direction $2 --",
    '/act/2/shot-miss': "Player $0's $2 energy projectile(s) flew towards Player $1 but missed...",
    '/act/2/shot': "Player $0's $2 energy projectile(s) fly towards Player $1.",
    '/act/2/crash': "$0 energy projectiles from both sides annihilated each other.",
    '/act/2/anti': "Player $0 fires $2 energy projectile(s) to counter Player $1!",
    '/act/2/reflect': "Player $0's $1 energy projectile(s) were reflected!",
    '/act/2/defend': "Player $0's defense blocked $1 damage.",
    '/act/2/final-hurt': "In the end, Player $0 took $1 damage. Remaining HP: $2.",
    '/act/2/wonderful': "What a brilliant exchange!",
    '/act/2/peace': "Ultimately, no one was harmed.",

    '/act/2/error-existPL': "This player does not exist or has been eliminated.",
    '/act/2/error-self': "You cannot target yourself or an AI teammate.\n",
    '/act/2/error-int': "Please enter an integer.",
    '/act/2/error-int-or-empty': "Please enter an integer or leave it empty.",
    '/act/2/error-no-lv': "That firing level does not exist.",
    '/act/2/error-no-energy': "Not enough energy.",
    '/act/2/error-no-seth': "That firing direction does not exist.",

    '/act/3/dealed': f"{C['CYAN']}Player $0 is defending for one turn.{C['RESET']}",

    '/act/4/ask': f"Enter levels to move up (negative to move down) {C['GREEN']}[-$0~$0]{C['RESET']} ",
    '/act/4/dealed': f"{C['GREEN']}Player $0 moved $1 level(s) and arrived at level $2.{C['RESET']}",
    '/act/4/out-of-map': "This move would go beyond the map boundaries.\n",
    '/act/4/error-int': "Please enter an integer.\n",

    '/act/5/dealed': f"{C['MAGENTA']}Player $0 has activated Reflect.{C['RESET']}",

    '/act/stt/main-exp': "Player $0 / HP $1 / Energy $2 / Position $3 / Damage Dealt $4 / Kills $5",
    '/act/stt/select-team': "View status of which team? [0~$0 / empty for all] ",

    '/act/6/battle': "-- Player $0 unleashes an Energy Wave from level $1 in direction $2 --",
    '/act/6/ask-seth': f"Wave direction\n    {C['CYAN']}[ 1 up / 0 straight / -1 down / empty for auto / space to cancel ]{C['RESET']} ",
    '/act/6/cancel': f"{C['CYAN']}[Energy Wave cancelled.]{C['RESET']}",
    '/act/6/has-sent': f"{C['CYAN']}[Energy Wave launched...]{C['RESET']}\n",
    '/act/6/error-no-seth': "This wave direction does not exist.",
    '/act/6/error-int-or-empty': "Please enter an integer or leave it empty.",
    '/act/6/shot-miss': "Player $0's Energy Wave with $2 power missed Player $1.",
    '/act/6/shot': "Player $0's Energy Wave with $2 power is heading for Player $1.",
    '/act/6/crash': "$0 points of energy from both sides were annihilated.",
    '/act/6/reflect': "Player $0's Energy Wave was reflected!",
    '/act/6/anti': "Player $0 also fired $2 energy to counter Player $1's wave.",
    '/act/6/defend': "Player $0's defense blocked $1 damage.",
    '/act/6/final-hurt': "Player $0 took $1 damage. Remaining HP: $2.",
    '/act/6/wonderful': "The Energy Wave is devastating!",
    '/act/6/peace': "NONE",
    '/act/6/auto-seth': f"Auto-selected direction {C['CYAN']}$0{C['RESET']}.",

    '/act/7/ask': "Enter the target whose action you want to disable: ",
    '/act/7/result': f"{C['MAGENTA']}Player $0's action '$1' {C['MAGENTA']}has been permanently swallowed by Player $2's Black Hole.{C['RESET']}",

    '/share/poor': f"{C['MAGENTA']}Not enough energy. Maybe charge up first?{C['RESET']}",
    '/share/out-of-range': "Please enter a value within the allowed range.",
    '/share/not-found': "Target not found.",
    '/share/unable': f"{C['RED']}This action is currently unavailable.{C['RESET']}",

    '/core/dead': f"{C['RED']}\n$1 player(s) eliminated this turn:\nPlayer(s) $0{C['RESET']}",
    '/core/dead-team': "Team $0 lost $1 member(s).",
    '/core/human-dead': f"{C['RED']}\nPlayer $0 have been eliminated.\nFinal blow: Player $2 used $3{C['RED']} to deal $1 damage to you.\nPress Enter to continue.{C['RESET']}",
    '/ark/game-over-nobody': f"{C['CYAN']}\n///// GAME OVER: NO SURVIVORS /////{C['RESET']}\n",
    '/ark/game-over': f"{C['CYAN']}\n///// GAME OVER: PLAYER $0 WINS! /////{C['RESET']}\n",
    "/ark/game-over-by-team": f"{C['CYAN']}\n///// GAME OVER: TEAM $0 WINS! /////{C['RESET']}\n",
    '/ark/welcome': "# Energy Battle - Remake 1.2-5 #\n",

    '/act/1/rule': f"{C['YELLOW']}Charge{C['RESET']} - {C['WHITE']}Increase your energy by 1.{C['RESET']}",
    '/act/3/rule': f"{C['CYAN']}Defend{C['RESET']} - {C['WHITE']}Enter a defensive state for this turn. You cannot be harmed by attack actions.{C['RESET']}",
    '/act/5/rule': f"{C['MAGENTA']}Reflect{C['RESET']} - {C['WHITE']}When attacked, reflects the damage back to the attacker.{C['RESET']}",
    '/act/6/rule': f"{C['CYAN']}Energy Wave{C['RESET']} - {C['WHITE']}Fires an AOE attack in a chosen direction, hitting all players in that line of sight for 5 damage.{C['RESET']}",
    '/act/7/rule': f"{C['MAGENTA']}Black Hole{C['RESET']} - {C['WHITE']}Consumes the chosen player's action for this turn, making it invalid and unusable.{C['RESET']}",

    '/ark/opt-title': "Please select an option\n-----------------------\n",
    '/ark/opt/1': "Start New Battle",
    '/ark/opt/2': "Configure Battle",
    '/ark/opt/3': "Exit Game",
    '/ark/break': "Exited from the battle.",
    "/ark/exit": f"{C['YELLOW']}[Exiting game...]{C['RESET']}",

    '/ark/setting/title': f"{C['CYAN']}// Battle Parameter Configuration{C['RESET']}",
    '/ark/setting/intro': "You can adjust the default battle parameters here.\nSelect an item to modify, or press Enter to return to the main menu.\n",
    '/ark/setting/current': "Current Settings",
    '/ark/setting/prompt': "Enter the number of the parameter to modify [Enter to return]\n-> ",
    '/ark/setting/input-new': "Enter new value (current: $0)\n[Enter to keep current] -> ",
    '/ark/setting/updated': "Parameter '$0' has been updated to $1.",
    '/ark/setting/exit': "Battle configuration complete. Enjoy the game!",
    '/ark/setting/error-invalid-choice': f"{C['RED']}Invalid option. Please choose again.{C['RESET']}",
    '/ark/setting/error-not-int': f"{C['RED']}Invalid input. An integer is required.{C['RESET']}",
    '/ark/setting/error-non-negative': "This parameter must be a non-negative number.",
    '/ark/setting/error-real-num-mismatch': "Number of human players ($0) cannot exceed total players ($1). It has been auto-corrected.",
    '/ark/setting/error-map-range': "Map size (current: $0) must be a positive integer. Recommended range is 1 to 10.",

    '/ark/setting/desc/num': "Total number of players",
    '/ark/setting/desc/real': "Number of human players",
    '/ark/setting/desc/map': "Map size (vertical levels)",
    '/ark/setting/desc/initHP': "Initial HP for each player",
    '/ark/setting/desc/shot_distance': 'Range of "Shoot"',
    '/ark/setting/desc/wave_distance': 'Range of "Energy Wave"',
    '/ark/setting/desc/team_size': "Players per AI team [1 = free-for-all]",
    '/ark/setting/desc/assist_team': "Should the first AI team cooperate with humans? [0-No 1-Yes]",
}
}

Expression["zh_cn"]['/act/2/rule'] = "\n".join([
    f"{C['RED']}射击{C['RESET']} - {C['WHITE']}向其他玩家射击并造成伤害",
    "       射击可以一次性射出最多3发能量",
    "       射击方向只有对准了目标才有效 否则会射偏",
    "       如果对方的位置与你不同的话 请选择恰当的射击方向",
    "       如果对方也同时向你射击的话",
    f"       你们的能量可能会有一部分甚至全部互相湮灭{C['RESET']}",
])

Expression["en_us"]['/act/2/rule'] = "\n".join([
    f"{C['RED']}Shoot{C['RESET']} - {C['WHITE']}Fire at another player to deal damage.",
    "       You can fire up to 3 energy projectiles at once.",
    "       The shot will only hit if the direction is correct; otherwise, it will miss.",
    "       If the target is at a different level, choose the appropriate firing direction.",
    "       If the target also shoots at you simultaneously,",
    f"       some or all of your energy projectiles may annihilate each other.{C['RESET']}",
])

Expression["zh_cn"]['/act/4/rule'] = "\n".join([
    f"{C['GREEN']}移动{C['RESET']} - {C['WHITE']}移动你的位置 你可以移动到对方射程之外",
    f"       但是地图大小通常有限 默认为上中下各一层共3层{C['RESET']}",
])

Expression["en_us"]['/act/4/rule'] = "\n".join([
    f"{C['GREEN']}Move{C['RESET']} - {C['WHITE']}Change your position. You can move out of an opponent's range.",
    f"       However, the map size is usually limited. The default is 3 levels (e.g., top, middle, bottom).{C['RESET']}",
])

Expression["zh_cn"]["/ark/rules"] = "\n".join([
    "",
    "这是一个回合制的多人对战策略游戏",
    "默认设置下每人1点血量、1个人类和9个AI玩家各自为战",
    "每位玩家每回合可以通过输入编号选择一项行动",
    "如果你在选择行动时直接按下回车键",
    "将会由AI帮你自动决策",
    "不同的行动具有不同的效果和价格",
    "你需要击败所有其他队伍的玩家并取得胜利",
    "同一队伍的玩家之间不能互相攻击",
    "以下是各行动的说明",
    "",
])

Expression["en_us"]["/ark/rules"] = "\n".join([
    "",
    "This is a turn-based, multiplayer strategy game.",
    "By default, each game starts with 1 human and 9 AIs, each for themselves, with 1 HP each.",
    "Each turn, every player selects an action by entering its corresponding number.",
    "If you press Enter without selecting an action, an AI will decide for you (auto-select).",
    "Different actions have unique effects and energy costs.",
    "Your goal is to defeat all players from other teams to win.",
    "Players on the same team cannot attack each other.",
    "Below are the descriptions for each action.",
    "",
])


# A simple, data-driven language selector function.
# It's designed to be easily integrated into the Ark/Noah project structure.
def select_language(expressions: dict, default_lang: str = "en_us") -> str:
    """
    Prompts the user to select a language from the available options.

    This function dynamically generates a menu from the top-level keys of the
    provided 'expressions' dictionary. It handles various user inputs, including
    numbers, language codes, and a default action for pressing Enter.

    Args:
        expressions (dict): The main localization dictionary where keys are language
                            codes (e.g., 'en_us', 'zh_cn').
        default_lang (str): The language code to return when the user just presses Enter.
                            Defaults to 'en_us'.

    Returns:
        str: The selected language code.
    """
    # 1. Extract available language codes from the expressions dictionary.
    available_langs = list(expressions.keys())

    # 2. Build a mapping from user input (both numbers and codes) to language codes.
    #    This makes the input handling very flexible.
    #    Example: {'1': 'en_us', 'en_us': 'en_us', '2': 'zh_cn', 'zh_cn': 'zh_cn'}
    options_map = {}
    prompt_lines = ["Please select a language:"]
    for i, lang_code in enumerate(available_langs):
        # Map the option number (as a string) to the language code.
        option_num = str(i + 1)
        options_map[option_num] = lang_code
        # Also map the code itself, so the user can type 'zh_cn' directly.
        options_map[lang_code] = lang_code

        # Create a user-friendly display name for the prompt.
        # Here we make a simple assumption for the display name.
        # You could add a 'display_name' field to your Expression dict for a fancier version.
        display_name = lang_code.replace('_', '-')
        prompt_lines.append(f"  {option_num}. {display_name}")

    # 3. Construct the final prompt string.
    #    The default language is explicitly mentioned to guide the user.
    prompt_lines.append(f"\n[Press Enter for {default_lang}] > ")
    prompt = "\n".join(prompt_lines)

    # 4. Loop until a valid choice is made.
    while True:
        choice = input(prompt).strip().lower()

        # Handle the default case: user presses Enter.
        if not choice:
            print(f"Defaulting to {default_lang}.")
            return default_lang

        # Check if the input (e.g., '1' or 'zh_cn') is a valid option.
        if choice in options_map:
            selected_lang = options_map[choice]
            print(f"Language set to: {selected_lang}\n")
            return selected_lang

        # Handle invalid input and re-prompt.
        else:
            print("\nInvalid selection. Please try again.")



# InitBattleEnv: Initial Battle Environment. A dictionary holding the default parameters for a game session.
InitBattleEnv = {
    "num": 10,      # Total number of players.
    "real": 1,      # Number of human players.
    "map": 1,       # Map size (number of vertical levels above and below the center).
    "initHP": 1,    # Initial HP for each player.
    "shot_distance": 1,    # Range of the 'Shoot' action.
    "wave_distance": 99999,    # Range of the 'Energy Wave' action (effectively infinite).
    "team_size": 1,   # Number of players per AI team (1 means free-for-all).
    "assist_team": 0, # Should the first AI team cooperate with humans? (0=No, 1=Yes).
    "setting_options":  {
        "1": "num",
        "2": "real",
        "3": "map",
        "4": "initHP",
        "5": "shot_distance",
        "6": "wave_distance",
        "7": "team_size",
        "8": "assist_team",
    }
}

# --- Action Logic Functions ---
# These functions define the behavior of each action in the game.
# They are structured to be passed into the Noah Kernel's ActDict.
# Suffix `_s` stands for "Selection Phase" logic.
# Suffix `_d` stands for "Resolution Phase" (Deal) logic.

def charge_s(pl, core, auto):
    """Selection logic for the 'Charge' action."""
    return (True, noah.Act(pl.id, "1"))

def charge_d(InStream, args):
    """Resolution logic for the 'Charge' action."""
    act, core = args
    act.pay(core)
    core.ui.out("./dealed", imp=[act.ownerID, core.PlDict[act.ownerID].energy])
    return None

def get_seth(place1, place2):
    """
    Calculates the relative direction from place1 to place2.
    Returns: -1 for down, 1 for up, 0 for the same level.
    """
    if place1 > place2:
        return -1
    elif place1 < place2:
        return 1
    else:
        return 0

def shot_s(pl, core, auto):
    """Selection logic for the 'Shoot' action. Handles both human and AI players."""
    s = pl

    if not auto:
        # --- Human Player Logic ---
        # Check for the minimum energy requirement.
        act = noah.Act(pl.id, "2")
        act.lv = 1
        core.ui.indent += 1

        if s.energy >= core.ActDict["2"]["price"](act):

            while True:
                # Prompt for the target.
                target = core.ui.inp('./ask-target')
                if target == "":
                    core.ui.out(["./cancel", "/share/endl"])
                    core.ui.indent -= 1
                    return (False, None)
                try:
                    tg = core.PlDict[int(target)]
                    # Validate that the target exists and is not eliminated.
                    if int(target) not in core.status["snap"]:
                        core.ui.out("./error-existPL")
                        continue
                    # Validate that the target is not a non-human teammate or self.
                    elif tg.team == s.team and not (tg.real and tg.id!=s.id):
                        core.ui.out("./error-self")
                        continue
                except (ValueError, KeyError):
                    core.ui.out("./error-int")
                    continue
                break

            core.ui.out("/share/endl")

            while True:
                # Prompt for the firing energy level.
                act.lv = core.ui.inp('./ask-lv')
                try:
                    if act.lv != "":
                        act.lv = int(act.lv)
                        if act.lv not in [1, 2, 3]:
                            core.ui.out("./error-no-lv")
                            continue
                        elif core.ActDict["2"]["price"](act) > s.energy:
                            core.ui.out("./error-no-energy")
                            continue
                    else:
                        # Auto-calculate max possible firing level.
                        act.lv = 3
                        while core.ActDict["2"]["price"](act) > s.energy:
                            act.lv -= 1
                        core.ui.out("./auto-lv", imp=[act.lv])

                except ValueError:
                    core.ui.out("./error-int-or-empty")
                    continue
                break

            core.ui.out("/share/endl")

            while True:
                # Prompt for the firing direction (seth).
                seth = core.ui.inp('./ask-seth')
                try:
                    if seth != "":
                        if int(seth) not in [-1, 0, 1]:
                            core.ui.out("./error-no-seth")
                            continue
                    else:
                        # Auto-calculate direction based on target's position.
                        seth = get_seth(s.place, core.status["snap"][int(target)][2])
                        core.ui.out("./auto-seth", imp=[seth])
                except ValueError:
                    core.ui.out("./error-int-or-empty")
                    continue

                core.ui.out('/share/endl')
                break

            act.target = int(target)
            act.seth = int(seth)

            core.ui.typing_delay *= 10
            core.ui.out('./has-sent')
            core.ui.typing_delay /= 10

            # Set properties for the resolution pipeline.
            act.channel = "shot-like"
            act.dealed = []
            act.color = "RED"
            act.distant = core.BattleEnv["shot_distance"]

            core.ui.indent -= 1
            return (True, act)

        else:
            core.ui.out(['/share/poor', '/share/endl'])
            core.ui.indent -= 1
            return (False, None)

    else: # --- AI Logic ---
        # 1. Efficiently find a target from the pre-calculated status cache.
        shot_able = []
        for i in range(s.place - 1, s.place + 2):
            if i in core.status["pop"]:
                shot_able += core.status["pop"][i]["sum"]

        target = pl.id
        _tg = core.status["snap"][target]
        # Ensure the AI doesn't target itself or a teammate.
        while _tg[3] == pl.team and ((not pl.real) or target==pl.id):
            target = noah.random.choice(shot_able)
            _tg = core.status["snap"][target]
            shot_able.remove(target)

        act = noah.Act(s.id, "2")
        act.lv = 3

        # Calculate the maximum affordable firepower.
        while core.ActDict["2"]["price"](act) > s.energy:
            act.lv -= 1

        # Defensive programming: ensure AI doesn't shoot with 0 energy,
        # even though the 'able' function should prevent this.
        if act.lv <= 0:
            return (False, None)

        act.target = int(target)
        act.seth = get_seth(s.place, core.status["snap"][target][2])
        act.channel = "shot-like"
        act.dealed = []
        act.color = "RED"
        act.distant = core.BattleEnv["shot_distance"]

        return (True, act)

# --- 'd_exec' Pipeline Functions for Shot-Like Actions ---
# These functions are executed in sequence during the resolution phase.
# The `InStream` dictionary is passed from one function to the next.

def firecount(myself, InStream, core, act, target=False):
    """
    Helper function to calculate hits and misses for a single attacker against one or more targets.
    This can be reused by both 'Shoot' and 'Energy Wave'.
    """
    for pos in myself.acts:
        cur_act = core.ActSign[core.ActDict[pos[0]]["priority"]][pos[0]][pos[1]]
        cur_act.pay(core)

        if cur_act.channel == "shot-like" and not cur_act.acted:
            if not target:
                target = core.PlDict[cur_act.target]

            if target.id not in cur_act.dealed:
                is_miss = (cur_act.seth != get_seth(myself.place, target.place) or
                           abs(myself.place - target.place) > cur_act.distant)

                if is_miss:
                    # The shot missed.
                    InStream["msg"].append([f"/act/{cur_act.key}/shot-miss", [myself.id, target.id, cur_act.lv]])
                else:
                    # The shot hit.
                    InStream["msg"].append([f"/act/{cur_act.key}/shot", [myself.id, target.id, cur_act.lv]])
                    if target.id not in InStream["damage"]:
                        InStream["damage"][target.id] = cur_act.lv
                    else:
                        InStream["damage"][target.id] += cur_act.lv
                cur_act.dealed.append(target.id)
    return InStream

def crossfire_evaluate(InStream, args):
    """Pipeline Step 1: Evaluate initial hits and damage."""
    act, core = args
    myself = core.PlDict[act.ownerID]
    if myself.real:
        core.ui.typing_delay = core.org_delay*5

    # This function initiates the data stream for a crossfire action.
    InStream = {"msg": [], "damage": {}}
    InStream["msg"].append(["./battle", [myself.id, myself.place, act.seth]])
    InStream = firecount(myself, InStream, core, act)
    return InStream

def crossfire_wave_eval(InStream, args):
    """Pipeline Step 1 (for Wave): Evaluate hits on all players in the path."""
    act, core = args
    myself = core.PlDict[act.ownerID]

    # This function initiates the data stream for a wave action.
    InStream = {"msg": [], "damage": {}}
    InStream["msg"].append(["./battle", [myself.id, myself.place, act.seth]])
    InStream["msg"].append(["/share/endl", []])

    for pl in core.PlDict.values():
        is_target = ((myself.team != pl.team) or (myself.real and myself != pl)) and \
                    get_seth(myself.place, pl.place) == act.seth
        if is_target:
            InStream = firecount(myself, InStream, core, act, pl)

    InStream["msg"].append(["/share/endl", []])
    return InStream

def crossfire_crash(InStream, args):
    """Pipeline Step 2: Check for counter-fire and projectile annihilation."""
    act, core = args
    attacker = core.PlDict[act.ownerID]
    msg = []

    for playerID in InStream["damage"].keys():
        if playerID != attacker.id:
            for pos in core.PlDict[playerID].acts:
                cur_act = core.ActSign[core.ActDict[pos[0]]["priority"]][pos[0]][pos[1]]
                # Check if the target is also performing a shot-like action back at the attacker.
                if cur_act.channel == "shot-like" and not cur_act.acted and attacker.id not in cur_act.dealed:
                    if (cur_act.target is True or cur_act.target == attacker.id):
                        myself = core.PlDict[playerID]
                        is_miss = (cur_act.seth != get_seth(myself.place, attacker.place) or
                                   abs(myself.place - attacker.place) > cur_act.distant)
                        if is_miss:
                            msg.append([f"/act/{cur_act.key}/shot-miss", [playerID, attacker.id, cur_act.lv]])
                        else:
                            # Both sides hit, projectiles crash.
                            msg.append([f"/act/{cur_act.key}/anti", [playerID, attacker.id, cur_act.lv]])
                            crash_amount = min(cur_act.lv, InStream["damage"][playerID])
                            msg.append([f"/act/{cur_act.key}/crash", [crash_amount]])
                            InStream["damage"][playerID] -= cur_act.lv

                        cur_act.dealed.append(attacker.id)
                        cur_act.pay(core)

    InStream["msg"] += msg
    if msg:
        InStream["msg"].append(["/share/endl", []])
    return InStream

def crossfire_reflect(InStream, args):
    """Pipeline Step 3: Check if any target has 'Reflect' active."""
    act, core = args
    attacker = core.PlDict[act.ownerID]

    someone_reflected = False
    for playerID in InStream["damage"].keys():
        if core.PlDict[playerID].defend_lv == -1 and attacker.defend_lv != -1: # -1 signifies Reflect
            InStream["msg"].append(["./reflect", [act.ownerID, InStream["damage"][playerID]]])
            if InStream["damage"][playerID] > 0:
                InStream["damage"][playerID] *= -1 # Negative damage means it's reflected back
            else:
                InStream["damage"][playerID] *= 2
            someone_reflected = True

    if someone_reflected:
        InStream["msg"].append(["/share/endl", []])
    return InStream

def crossfire_defend(InStream, args):
    """Pipeline Step 4: Check if any target has 'Defend' active."""
    act, core = args
    someone_defend = False
    for playerID in InStream["damage"].keys():
        if core.PlDict[playerID].defend_lv == 1: # 1 signifies Defend
            InStream["msg"].append(["./defend", [playerID, InStream["damage"][playerID]]])
            if InStream["damage"][playerID] > 0:
                InStream["damage"][playerID] = 0 # Nullify damage
            someone_defend = True

    if someone_defend:
        InStream["msg"].append(["/share/endl", []])
    return InStream

def crossfire_final(InStream, args):
    """Pipeline Step 5: Apply final damage and display results."""
    act, core = args
    attacker = core.PlDict[act.ownerID]

    for playerID, hurt_lv in InStream["damage"].items():
        tg = core.PlDict[playerID]

        if hurt_lv > 0: # Positive value: target takes damage.
            tg.hurted(hurt_lv, attacker.id, act.key, core)
            InStream["msg"].append(["./final-hurt", [playerID, hurt_lv, tg.HP]])
        elif hurt_lv < 0: # Negative value: attacker takes reflected damage.
            attacker.hurted(-hurt_lv, tg.id, act.key, core)
            InStream["msg"].append(["./final-hurt", [attacker.id, -hurt_lv, attacker.HP]])
        else: # Zero damage
            InStream["msg"].append(["./peace", []])

    # Display the battle log.
    if len(InStream["msg"]) > 1:
        msg = InStream["msg"].pop(0)
        core.ui.out("/share/endl")
        core.ui.out(msg[0], imp=msg[1], color=act.color)
        core.ui.indent += 1
        for msg in InStream["msg"]:
            core.ui.out(msg[0], imp=msg[1], color=act.color)
        if len(InStream["msg"]) >= 4:
            core.ui.out("./wonderful", color="MAGENTA")
        core.ui.indent -= 1

    core.ui.typing_delay = 0
    act.pay(core)
    return None

def defend_s(pl, core, auto):
    """Selection logic for the 'Defend' action."""
    return (True, noah.Act(pl.id, "3"))

def defend_d(InStream, args):
    """Resolution logic for the 'Defend' action."""
    act, core = args
    act.pay(core)
    core.PlDict[act.ownerID].defend_lv = 1
    core.ui.out("./dealed", imp=[act.ownerID])
    return None

def move_s(pl, core, auto):
    """Selection logic for the 'Move' action."""
    if not auto: # Human logic
        core.ui.indent += 1
        while True:
            # Get the number of levels to move.
            st = core.ui.inp("./ask", imp=[core.ActDict["4"]["step"]])
            core.ui.out('/share/endl')
            try:
                st_int = int(st)
                if abs(st_int) > core.ActDict["4"]["step"]:
                    core.ui.out("/share/out-of-range")
                elif abs(st_int + pl.place) > core.BattleEnv["map"]:
                    core.ui.out("./out-of-map", color="RED")
                else:
                    act = noah.Act(pl.id, "4")
                    act.steps = st_int
                    core.ui.indent -= 1
                    return (True, act)
            except ValueError:
                core.ui.out("./error-int", color="RED")
    else: # AI logic
        ls = list(range(-core.ActDict["4"]["step"], core.ActDict["4"]["step"] + 1))
        ls.remove(0) # AI should always move.

        st = noah.random.choice(ls)
        # Ensure the move is within map boundaries.
        while abs(st + pl.place) > core.BattleEnv["map"]:
            st = noah.random.choice(ls)

        act = noah.Act(pl.id, "4")
        act.steps = st
        return (True, act)

def blackhole_s(pl, core, auto):
    """Selection logic for the 'Black Hole' action."""
    act = noah.Act(pl.id, "7")
    if not auto: # Human Logic
        core.ui.indent += 1
        if pl.energy >= core.ActDict["7"]["price"](act):
            while True:
                inp_target = core.ui.inp("./ask")
                try:
                    get = core.PlDict[int(inp_target)]
                    break
                except (ValueError, KeyError):
                    core.ui.out("/share/not-found", color="RED")

            act.target = int(inp_target)
            core.ui.out("/share/endl")
            core.ui.indent -= 1
            return (True, act)
        else:
            core.ui.out("/share/poor", color='MAGENTA')
            core.ui.indent -= 1
            return (False, None)

    else: # AI Logic
        available_targets = []
        for i in core.status["pop"].keys():
            if i != "all":
                available_targets += core.status["pop"][i]["sum"]

        target = pl.id
        _tg = core.status["snap"][target]
        while _tg[3] == pl.team and ((not pl.real) or target == pl.id):
            available_targets.remove(target)
            target = noah.random.choice(available_targets)
            _tg = core.status["snap"][target]

        act.target = target
        return (True, act)

def blackhole_d(InStream, args):
    """Resolution logic for 'Black Hole'."""
    act, core = args
    act.pay(core)
    target = core.PlDict[act.target]

    # Add the target's chosen actions to their 'unable' list.
    block = [i[0] for i in target.acts]
    target.unable += block

    # Mark the target's actions as already acted to prevent them from resolving.
    for pos in target.acts:
        core.ActSign[core.ActDict[pos[0]]["priority"]][pos[0]][pos[1]].acted = True

    block_out = ", ".join([core.ui.get(f"/act/{i}/name") for i in block])
    core.ui.out("./result", imp=[target.id, block_out, act.ownerID])
    return None

def move_d(InStream, args):
    """Resolution logic for the 'Move' action."""
    act, core = args
    act.pay(core)
    st = act.steps
    core.PlDict[act.ownerID].place += st  # Perform the move.
    core.ui.out("./dealed", imp=[act.ownerID, st, core.PlDict[act.ownerID].place])
    return None

def auto_AOEseth(pl, core):
    """
    AI helper to determine the optimal direction for an AOE attack.
    It scans the battlefield to find the direction with the most enemies.
    """
    tree_seth = [0, 0, 0] # [-1 (down), 0 (straight), 1 (up)]
    for place, pls in core.status["pop"].items():
        if place != "all":
            if place > pl.place: # Above player
                tree_seth[2] += len(pls["sum"])
                if not pl.real: tree_seth[2] -= len(pls.get(pl.team, []))
            elif place == pl.place: # Same level
                tree_seth[1] += len(pls["sum"])
                if not pl.real: tree_seth[1] -= len(pls.get(pl.team, []))
            else: # Below player
                tree_seth[0] += len(pls["sum"])
                if not pl.real: tree_seth[0] -= len(pls.get(pl.team, []))

    return tree_seth.index(max(tree_seth)) - 1

def wave_s(pl, core, auto):
    """Selection logic for the 'Energy Wave' action."""
    act = noah.Act(pl.id, "6")

    if pl.energy < core.ActDict["6"]["price"](act):
        if not auto:
            core.ui.indent += 1
            core.ui.out(["/share/poor", "/share/endl"], color='MAGENTA')
            core.ui.indent -= 1
        return (False, None)
    elif not auto: # Human Logic
        core.ui.indent += 1
        while True:
            seth = core.ui.inp('./ask-seth', indent=1)
            if seth == " ": # Cancel option
                core.ui.out(["./cancel", "/share/endl"])
                core.ui.indent -= 1
                return (False, None)
            try:
                if seth != "":
                    if int(seth) not in [-1, 0, 1]:
                        core.ui.out("./error-no-seth", indent=1)
                        continue
                else: # Auto-calculate direction
                    seth = auto_AOEseth(pl, core)
                    core.ui.out("./auto-seth", imp=[seth], indent=1)
            except ValueError:
                core.ui.out("./error-int-or-empty", indent=1)
                continue
            core.ui.out('/share/endl', indent=1)
            break

        act.seth = int(seth)
        core.ui.typing_delay *= 10
        core.ui.out('./has-sent')
        core.ui.typing_delay /= 10
        core.ui.indent -= 1

    elif auto: # AI Logic
        act.seth = auto_AOEseth(pl, core)

    # Set properties for the resolution pipeline.
    act.target = True # Indicates an AOE attack
    act.lv = 5
    act.channel = "shot-like"
    act.dealed = []
    act.color = "CYAN"
    act.distant = core.BattleEnv["wave_distance"]
    return (True, act)

# --- Action Price, Ability, and AI Weight Functions ---

def charge_price(act): return -1
def shot_price(act): return act.lv
def reflect_price(act): return 2
def blackhole_price(act): return 5
def wave_price(act): return 4
def free_of_charge(act): return 0

def able_forever(context):
    """Ability check for actions that are always available."""
    return True

def shot_able(context):
    """Ability check for 'Shoot'."""
    return (context["self"].energy >= 1) and (context["side_enm"] > 0)

def move_able(context):
    """Ability check for 'Move'."""
    return context["core"].BattleEnv["map"] > 0

def blackhole_able(context):
    """Ability check for 'Black Hole'."""
    return (context["self"].energy >= 5)

def reflect_able(context):
    """Ability check for 'Reflect'."""
    return (context["self"].energy >= 2)

def wave_able(context):
    """Ability check for 'Energy Wave'."""
    return (context["self"].energy >= 4)

def charge_ai(context):
    """AI weight for 'Charge'."""
    return min((100/(context["self"].energy+1))*3, 500)

def shot_ai(context):
    """AI weight for 'Shoot'."""
    return context["self"].energy*100

def defend_ai(context):
    """AI weight for 'Defend'."""
    return context["engK"]*100+10

def move_ai(context):
    """AI weight for 'Move'."""
    return context["enmK"]*100+10

def blackhole_ai(context):
    """AI weight for 'Black Hole'."""
    return context["self"].energy * 3000

def reflect_ai(context):
    """AI weight for 'Reflect'."""
    return context["engK"]*20+10

def wave_ai(context):
    """AI weight for 'Energy Wave'."""
    return context["self"].energy*1000

def reflect_s(pl, core, auto):
    """Selection logic for 'Reflect'."""
    act = noah.Act(pl.id, "5")
    if pl.energy >= core.ActDict["5"]["price"](act):
        return (True, noah.Act(pl.id, "5"))
    else:
        if not auto:
            core.ui.indent += 1
            core.ui.out(["/share/poor", "/share/endl"])
            core.ui.indent -= 1
        return (False, None)

def reflect_d(InStream, args):
    """Resolution logic for 'Reflect'."""
    act, core = args
    act.pay(core)
    core.PlDict[act.ownerID].defend_lv = -1 # -1 signifies reflect status
    core.ui.out("./dealed", imp=[act.ownerID])

def ShowRules_s(pl, core, auto):
    """Selection logic for 'ShowRules' (human-only utility action)."""
    org = core.ui.typing_delay
    core.ui.typing_delay = 0
    core.ui.out("/ark/rules")
    for act in core.ActDict.keys():
        if f"/act/{act}/rule" in core.ui.exp:
            core.ui.out(f"/act/{act}/rule")
    core.ui.out('/share/endl')
    core.ui.typing_delay = org

    core.ls_acts()
    return (False, None) # (False, ...) indicates no action should be registered for the turn.

def ShowStatus_s(pl, core, auto):
    """Selection logic for 'ShowStatus' (human-only utility action)."""
    core.ui.indent += 1
    all_teams = [i[3] for i in core.status["snap"].values()]
    ask = core.ui.inp('./select-team', imp=[max(all_teams) if all_teams else 0])
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

def break_s(pl, core, auto):
    """Selection logic for 'Surrender'."""
    core._break = True
    return (True, None)

# ArkUI is the UI instance managed by the frontend, distinct from core.ui.
# You can select a language here
chosen_lang_code = select_language(Expression)
noah.time.sleep(1)
noah.clear_screen()
ArkUI = noah.IO(Expression[chosen_lang_code])
ArkUI.workdir = "/ark/"
ArkUI.out("./welcome", color="YELLOW")

# The master Action Dictionary that defines the entire game's mechanics for the Noah Kernel.
BaseActDict = {
    "1": { # Charge
        "price": charge_price, "priority": 0, "able": able_forever,
        "human_only": False, "ai": charge_ai, "weight": 1,
        "s_exec": charge_s, "d_exec": [charge_d],
    },
    "2": { # Shoot
        "price": shot_price, "priority": -1, "able": shot_able,
        "human_only": False, "ai": shot_ai, "weight": 1,
        "s_exec": shot_s,
        "d_exec": [crossfire_evaluate, crossfire_crash, crossfire_reflect, crossfire_defend, crossfire_final],
    },
    "3": { # Defend
        "price": free_of_charge, "priority": 2, "able": able_forever,
        "human_only": False, "ai": defend_ai, "weight": 1,
        "s_exec": defend_s, "d_exec": [defend_d],
    },
    "4": { # Move
        "price": free_of_charge, "priority": 1, "able": move_able,
        "human_only": False, "ai": move_ai, "weight": 1,
        "s_exec": move_s, "d_exec": [move_d],
        "step": 1 # Custom parameter for this action
    },
    "5": { # Reflect
        "price": reflect_price, "priority": 2, "able": reflect_able,
        "human_only": False, "ai": reflect_ai, "weight": 1,
        "s_exec": reflect_s, "d_exec": [reflect_d],
    },
    "6": { # Energy Wave
        "price": wave_price, "priority": -1, "able": wave_able,
        "human_only": False, "ai": wave_ai, "weight": 1,
        "s_exec": wave_s,
        "d_exec": [crossfire_wave_eval, crossfire_crash, crossfire_reflect, crossfire_defend, crossfire_final],
    },
    "7": { # Black Hole
        "price": blackhole_price, "priority": 9999, "able": blackhole_able,
        "human_only": False, "ai": blackhole_ai, "weight": 1,
        "s_exec": blackhole_s, "d_exec": [blackhole_d],
    },
    "rl": { # Show Rules
        "price": free_of_charge, "priority": 0, "able": able_forever,
        "human_only": True, "ai": None, "weight": 0,
        "s_exec": ShowRules_s, "d_exec": [],
    },
    "stt": { # Show Status
        "price": free_of_charge, "priority": 0, "able": able_forever,
        "human_only": True, "ai": None, "weight": 0,
        "s_exec": ShowStatus_s, "d_exec": [],
    },
    "bk": { # Surrender/Break
        "price": free_of_charge, "priority": 0, "able": able_forever,
        "human_only": True, "ai": None, "weight": 0,
        "s_exec": break_s, "d_exec": [],
    },
}

def Setting():
    """Handles the game settings configuration screen."""
    global InitBattleEnv # Declare intent to modify the global settings dictionary.

    ArkUI.typing_delay = 0.001
    ArkUI.workdir = "/ark/setting/" # Switch UI working directory for easier path management.
    ArkUI.out("./title")
    ArkUI.out("./intro")

    while True:
        ArkUI.out("./current")
        # Display the current settings in a formatted table.
        display_data = []
        for num, key in InitBattleEnv["setting_options"].items():
            display_data.append((num, ArkUI.get(f"./desc/{key}"), InitBattleEnv[key]))
        ArkUI.out(noah.table(display_data, f"{C['YELLOW']}$0{C['RESET']}. $1 / {C['CYAN']}$2{C['RESET']}"), dr=True)
        ArkUI.out("/share/endl")

        choice = ArkUI.inp("./prompt")
        ArkUI.out("/share/endl")

        if choice == "": # Player pressed Enter, meaning exit.
            ArkUI.out("./exit")
            ArkUI.out("/share/endl")
            break

        if choice in InitBattleEnv["setting_options"]:
            setting_key = InitBattleEnv["setting_options"][choice]
            setting_name = ArkUI.get(f"./desc/{setting_key}")
            current_value = InitBattleEnv[setting_key]

            new_value_str = ArkUI.inp("./input-new", imp=[current_value])
            ArkUI.out("/share/endl")

            if new_value_str == "": # Player pressed Enter, keep the old value.
                ArkUI.out("./updated", imp=[setting_name, current_value])
                ArkUI.out("/share/endl")
                continue

            try:
                new_value = int(new_value_str)

                # General validation: non-negative.
                if new_value < 0:
                    ArkUI.out("./error-non-negative")
                    continue

                # Specific parameter validation.
                if setting_key == "map" and new_value > 100: # Set a reasonable upper limit for map size.
                    ArkUI.out("./error-map-range", imp=[new_value])
                    continue

                # Update parameter.
                InitBattleEnv[setting_key] = new_value

                # Cross-validation: human players cannot exceed total players.
                if setting_key in ["num", "real"]:
                    if InitBattleEnv["real"] > InitBattleEnv["num"]:
                        ArkUI.out("./error-real-num-mismatch", imp=[InitBattleEnv["real"], InitBattleEnv["num"]])
                        InitBattleEnv["real"] = InitBattleEnv["num"] # Auto-correct.
                        ArkUI.out("/ark/setting/updated", imp=[setting_name, InitBattleEnv["real"]])
                        ArkUI.out("/share/endl")

                ArkUI.out("./updated", imp=[setting_name, InitBattleEnv[setting_key]])

            except ValueError:
                ArkUI.out("./error-not-int")
            except Exception as e:
                # Catch other potential errors gracefully.
                ArkUI.out(f"An unexpected error occurred: {e}", dr=True)
            finally:
                ArkUI.out("/share/endl") # Add a blank line for readability.

        else:
            ArkUI.out("./error-invalid-choice")
            ArkUI.out("/share/endl")

    ArkUI.workdir = "/ark/" # Restore the UI's working directory.

def Gaming():
    """This is the main game loop function."""
    core = noah.Core(InitBattleEnv, BaseActDict, noah.IO(ArkUI.exp))
    core.mk_pldict()
    core.ls_acts()
    core.update_status()

    while True:  # The main turn-based loop.
        core.clean_round()
        core.rounds += 1

        org_delay = core.ui.typing_delay
        core.ui.typing_delay = 0
        core.ui.out("/ark/round-title", imp=[core.rounds], color="WHITE")
        core.ui.typing_delay = org_delay

        core.SelectAct()
        if core._break:
            core.ui.out(["/ark/break", "/share/endl"])
            break

        core.DealAct()
        core.rm_deaths()
        core.update_status()

        teams = []
        for place in core.status["pop"].keys():
            if place != "all":
                teams += list(core.status["pop"][place].keys())
        while "sum" in teams:
            teams.remove("sum")
        teams = set(teams)

        if len(teams) <= 1:
            core.ui.typing_delay *= 7
            if teams and 0 not in teams:
                if core.status["pop"]["all"] > 1:
                    core.ui.out("/ark/game-over-by-team", imp=[list(core.PlDict.values())[0].team])
                    break
                elif core.status["pop"]["all"] == 1:
                    core.ui.out("/ark/game-over", imp=[list(core.PlDict.values())[0].id])
                    break

            elif teams and 0 in teams:
                humans_num = 0
                ai_num = 0
                for pl in core.PlDict.values():
                    if pl.real:
                        humans_num += 1
                    else:
                        ai_num += 1
                if ai_num == 0 and humans_num == 1:
                    core.ui.out("/ark/game-over", imp=[list(core.PlDict.values())[0].id])
                    break
                elif ai_num != 0:
                    core.ui.out("/ark/game-over-by-team", imp=[0])
                    break
            else:
                core.ui.out("/ark/game-over-nobody")
                break

        core.ui.out("/share/endl")


def _exit():
    """Function to exit the game gracefully."""
    ArkUI.typing_delay *= 10
    ArkUI.out("./exit")
    return True

# Transition Table: Maps user input from the main menu to corresponding functions.
TransTable = {
    "mode": {
        "1": [ArkUI.get('./opt/1'), Gaming],
        "2": [ArkUI.get('./opt/2'), Setting],
        "3": [ArkUI.get('./opt/3'), _exit],
    }
}

if __name__ == "__main__":
    while True: # The session loop (allows playing multiple games).
        # Display main menu options.
        optlist = ArkUI.get('./opt-title')
        optlist += noah.table(
            [(num, show[0]) for num, show in TransTable['mode'].items()], f"{C['YELLOW']}$0{C['RESET']}. $1"
        )
        optlist += "\n"
        ArkUI.out(optlist, dr=True)

        res = ArkUI.inp("> ", dr=True)
        ArkUI.out("/share/endl")

        if res in TransTable['mode']:
            _break = TransTable['mode'][res][1]()
        elif res == "": # Default action is to start the game.
            _break = TransTable['mode']["1"][1]()
        else:
            ArkUI.out("/share/not-found")
            ArkUI.out("/share/endl")

        if _break:
            break
