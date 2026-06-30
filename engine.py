from __future__ import annotations

import random
from typing import Any

from .game_data import ATTR_LABELS, BAITS, DIFFICULTIES, EVENT_WEIGHTS, FISHING_SPOTS, SECTS


MAX_FLOOR = 7
DOORS_PER_FLOOR = 3


def new_player(user_id: str, nickname: str, sect_name: str, difficulty: str) -> dict[str, Any]:
    sect = SECTS[sect_name]
    hp = 28 + sect.attrs.get("con", 0) * 3
    mp = 8 + sect.attrs.get("int", 0) + (4 if sect_name == "大理段氏" else 0)
    return {
        "user_id": user_id,
        "nickname": nickname,
        "sect": sect_name,
        "difficulty": difficulty,
        "floor": 1,
        "opened_doors": 0,
        "hp": hp,
        "max_hp": hp,
        "mp": mp,
        "max_mp": mp,
        "silver": 60,
        "supplies": 2,
        "materials": 0,
        "essence": 0,
        "scrolls": 0,
        "fragments": [],
        "buffs": [],
        "finished": False,
        "frozen": False,
        "next_door_dc_bonus": 0,
    }


def roll_d20() -> int:
    return random.randint(1, 20)


def weighted_event() -> str:
    names = [item[0] for item in EVENT_WEIGHTS]
    weights = [item[1] for item in EVENT_WEIGHTS]
    return random.choices(names, weights=weights, k=1)[0]


def attr_bonus(player: dict[str, Any], attr: str) -> int:
    sect = SECTS[player["sect"]]
    if attr == "sect":
        return sect.attrs.get(sect.main_attr, 0)
    if attr == "all":
        return sum(sect.attrs.values())
    return sect.attrs.get(attr, 0)


def check(player: dict[str, Any], attr: str, dc: int) -> dict[str, Any]:
    die = roll_d20()
    bonus = attr_bonus(player, attr)
    total = die + bonus
    return {"die": die, "bonus": bonus, "total": total, "success": die == 20 or total >= dc, "crit": die == 20, "fumble": die == 1}


def status_text(player: dict[str, Any]) -> str:
    sect = SECTS[player["sect"]]
    traits = "、".join(sect.traits[:3])
    fragments = "、".join(player.get("fragments", [])[-4:]) or "暂无"
    buffs = "、".join(player.get("buffs", [])[-4:]) or "暂无"
    return (
        f"【金庸踢门团】{player.get('nickname', '')}\n"
        f"门派：{player['sect']}（{sect.camp}）｜难度：{player['difficulty']}\n"
        f"进度：第{player['floor']}层，已开门 {player['opened_doors']}/{DOORS_PER_FLOOR}\n"
        f"HP {player['hp']}/{player['max_hp']}｜MP {player['mp']}/{player['max_mp']}｜碎银 {player['silver']}两｜补给 {player['supplies']}\n"
        f"素材 {player['materials']}｜武道真髓 {player['essence']}｜武学残卷 {player['scrolls']}\n"
        f"核心特性：{traits}\n"
        f"近期残页：{fragments}\n"
        f"增益：{buffs}"
    )


def sect_list_text() -> str:
    grouped: dict[str, list[str]] = {}
    for sect in SECTS.values():
        grouped.setdefault(sect.camp, []).append(sect.name)
    lines = ["可选门派："]
    for camp, names in grouped.items():
        lines.append(f"{camp}：{'、'.join(names)}")
    return "\n".join(lines)


def open_door(player: dict[str, Any]) -> str:
    if player.get("finished") or player.get("frozen"):
        return "该角色已通关飞升并冻结，请用 /jy重置 confirm 开新档。"
    if player["floor"] == MAX_FLOOR:
        return boss_fight(player)
    if player["opened_doors"] >= DOORS_PER_FLOOR:
        return "本层3个事件门已清完。发送 /jy下一层 进行本门奇遇检定并进入下一层。"

    event_type = weighted_event()
    difficulty = DIFFICULTIES[player["difficulty"]]
    dc = 9 + player["floor"] + difficulty["dc"] - 10 + player.pop("next_door_dc_bonus", 0)
    sect = SECTS[player["sect"]]
    result = check(player, sect.main_attr, max(8, dc))
    player["opened_doors"] += 1

    if event_type == "战斗":
        return _battle(player, result)
    if event_type == "宝箱":
        return _chest(player, result)
    if event_type == "奇遇":
        return _encounter(player, result)
    if event_type == "陷阱":
        return _trap(player, result)
    return _merchant(player, result)


def _battle(player: dict[str, Any], result: dict[str, Any]) -> str:
    sect = SECTS[player["sect"]]
    enemy_hp = 12 + player["floor"] * 5 + DIFFICULTIES[player["difficulty"]]["enemy_bonus"]
    skill = random.choice(sect.skills)
    if result["success"]:
        silver = random.randint(8, 18) + player["floor"] * 2
        player["silver"] += silver
        player["materials"] += 1
        line = "胜利"
    else:
        dmg = random.randint(4, 10) + player["floor"]
        player["hp"] = max(1, player["hp"] - dmg)
        silver = random.randint(2, 8)
        player["silver"] += silver
        line = f"险胜，损失{dmg}HP"
    return (
        f"【战斗门】遭遇第{player['floor']}层守塔高手（HP{enemy_hp}）。\n"
        f"你以「{skill}」检定：d20={result['die']} + {result['bonus']} = {result['total']}。\n"
        f"结果：{line}。获得碎银{silver}两、武学素材+{1 if result['success'] else 0}。"
    )


def _chest(player: dict[str, Any], result: dict[str, Any]) -> str:
    if result["fumble"]:
        dmg = random.randint(3, 8)
        player["hp"] = max(1, player["hp"] - dmg)
        return f"【宝箱门】机关暗弩触发：d20=1。损失{dmg}HP，宝箱损毁。"
    silver = random.randint(12, 30) + player["floor"] * 3
    player["silver"] += silver
    player["supplies"] += 1
    if result["crit"]:
        player["fragments"].append(f"{player['sect']}顶级绝学残页")
    else:
        player["fragments"].append(f"{player['sect']}武学残页")
    return f"【宝箱门】开箱检定 {result['total']}。获得碎银{silver}两、补给+1、{player['fragments'][-1]}。"


def _encounter(player: dict[str, Any], result: dict[str, Any]) -> str:
    if result["success"]:
        player["materials"] += 2
        player["mp"] = min(player["max_mp"], player["mp"] + 2)
        return f"【奇遇门】高人指点成功：d20={result['die']}，武学素材+2，MP恢复2。"
    return f"【奇遇门】擦肩而过：d20={result['die']} + {result['bonus']} = {result['total']}，无奖励也无惩罚。"


def _trap(player: dict[str, Any], result: dict[str, Any]) -> str:
    if result["success"]:
        player["silver"] += 10
        return f"【陷阱门】拆解成功：d20={result['die']}，回收机关零件换得碎银10两。"
    dmg = random.randint(5, 12)
    player["hp"] = max(1, player["hp"] - dmg)
    return f"【陷阱门】检定失败：d20={result['die']}，损失{dmg}HP。"


def _merchant(player: dict[str, Any], result: dict[str, Any]) -> str:
    discount = 10 if result["success"] else 0
    cost = max(8, 20 - discount)
    if player["silver"] >= cost:
        player["silver"] -= cost
        player["supplies"] += 2
        return f"【商人门】交涉检定{result['total']}，花费{cost}两购得补给+2。"
    return f"【商人门】游商报价{cost}两，但你碎银不足。"


def next_floor(player: dict[str, Any]) -> str:
    if player.get("finished") or player.get("frozen"):
        return "该角色已通关飞升并冻结，请重置后再开新周目。"
    if player["floor"] >= MAX_FLOOR:
        return "你已在武神殿。发送 /jy踢门 挑战武神镜像。"
    if player["opened_doors"] < DOORS_PER_FLOOR:
        return f"本层还剩 {DOORS_PER_FLOOR - player['opened_doors']} 个门未清。"

    sect = SECTS[player["sect"]]
    dc = DIFFICULTIES[player["difficulty"]]["dc"]
    result = check(player, sect.main_attr, dc)
    lines = [f"【本门奇遇】d20={result['die']} + {result['bonus']} = {result['total']}，DC{dc}。"]
    if result["crit"]:
        reward = f"{player['sect']}顶级绝学残页"
        player["fragments"].append(reward)
        player["supplies"] += 1
        player["materials"] += 2
        lines.append(f"自然20：获得{reward}、专属丹药补给+1、随机素材+2。")
    elif result["success"]:
        reward = f"{player['sect']}中阶武学残页"
        player["fragments"].append(reward)
        player["supplies"] += 1
        lines.append(f"成功：获得{reward}、普通补给+1。")
    elif result["fumble"]:
        if player["supplies"] > 0:
            player["supplies"] -= 1
            lines.append("自然1：遗失普通补给1份。")
        else:
            player["next_door_dc_bonus"] = 1
            lines.append("自然1：下次进门首次检定DC+1。")
    else:
        lines.append("失败：无奖励，无负面效果。")

    player["floor"] += 1
    player["opened_doors"] = 0
    if player["floor"] == MAX_FLOOR:
        lines.append("第7层武神殿已解锁。发送 /jy踢门 挑战唯一BOSS武神镜像。")
    else:
        lines.append(f"进入第{player['floor']}层。")
    return "\n".join(lines)


def boss_fight(player: dict[str, Any]) -> str:
    sect = SECTS[player["sect"]]
    result = check(player, sect.main_attr, 18 + DIFFICULTIES[player["difficulty"]]["enemy_bonus"] // 2)
    if not result["success"]:
        dmg = random.randint(12, 22)
        player["hp"] = max(1, player["hp"] - dmg)
        return (
            "【武神殿】武神镜像 HP70 AC19，四象护体抵消伤害。\n"
            f"终局检定：d20={result['die']} + {result['bonus']} = {result['total']}。\n"
            f"挑战未竟，损失{dmg}HP。补给整备后可再次 /jy踢门。"
        )

    reward = DIFFICULTIES[player["difficulty"]]
    player["essence"] += reward["essence"]
    player["scrolls"] += reward["scrolls"]
    if random.randint(1, 10) == 1:
        player["fragments"].append(sect.ultimate)
    player["finished"] = True
    player["frozen"] = True
    return (
        "【武神殿通关】你击败武神镜像，角色飞升并永久冻结。\n"
        f"通关奖励：武道真髓×{reward['essence']}、武学残卷×{reward['scrolls']}、小还丹×5、碎银×100两。\n"
        f"本门顶级绝学掉落检定已结算，当前残页：{'、'.join(player['fragments'][-5:]) or '暂无'}。"
    )


def fish(player: dict[str, Any], spot_name: str, bait_name: str) -> str:
    spot = FISHING_SPOTS.get(spot_name)
    bait = BAITS.get(bait_name)
    if spot is None:
        return "未知钓点。可选：" + "、".join(FISHING_SPOTS)
    if bait is None:
        return "未知饵剂。可选：" + "、".join(BAITS)
    if spot_name == "门派专属钓点" and player["floor"] <= 1 and player["opened_doors"] < DOORS_PER_FLOOR:
        return "门派专属钓点需要至少通关1层后解锁。"
    if spot_name == "武神塔顶龙池" and not player.get("finished"):
        return "武神塔顶龙池需要通关武神殿后解锁。"

    total_cost = spot["cost"] + bait["price"]
    if player["silver"] < total_cost:
        return f"碎银不足，本次垂钓需要{total_cost}两。"
    player["silver"] -= total_cost

    dc = int(spot["dc"])
    attr = str(spot["attr"])
    result = check(player, attr, dc) if dc > 0 else {"die": 0, "bonus": 0, "total": 99, "success": True, "crit": False, "fumble": False}
    if dc > 0 and not result["crit"]:
        result["total"] += bait["bonus"]
        result["success"] = result["total"] >= dc
    rare_roll = random.randint(1, 100)
    rare_line = _fish_reward(player, spot_name, rare_roll, bait["rare_mul"], result["success"])
    check_line = "无需检定" if dc <= 0 else f"d20={result['die']} + {result['bonus']} + 饵剂{bait['bonus']} = {result['total']}，DC{dc}"
    return f"【钓鱼】{spot_name}｜{bait_name}｜花费{total_cost}两\n检定：{check_line}\n{rare_line}"


def _fish_reward(player: dict[str, Any], spot_name: str, rare_roll: int, rare_mul: int, success: bool) -> str:
    if not success:
        player["supplies"] = max(0, player["supplies"] - 1)
        return "垂钓失败，消耗补给整理渔具。"
    legendary_threshold = 1 * rare_mul
    epic_threshold = legendary_threshold + 4 * rare_mul
    rare_threshold = epic_threshold + 25
    if rare_roll <= legendary_threshold:
        player["scrolls"] += 1
        return "传说渔获：武学残卷×1。"
    if rare_roll <= epic_threshold:
        player["buffs"].append("机关拆解永久+1")
        return "史诗渔获：机关大师笔记，永久机关拆解+1。"
    if rare_roll <= rare_threshold or spot_name in ("秘境水潭", "门派专属钓点"):
        player["materials"] += 1
        return "稀有渔获：武学素材×1。"
    silver = random.randint(1, 10)
    player["silver"] += silver
    return f"普通渔获：鱼获与杂物折价{silver}两。"


def help_text() -> str:
    return (
        "【金庸武侠DND肉鸽踢门团】\n"
        "/jy帮助：查看指令\n"
        "/jy门派：查看16大门派\n"
        "/jy开局 门派 [普通|困难]：创建角色\n"
        "/jy状态：查看当前角色\n"
        "/jy踢门：开启当前层随机事件门；第7层挑战武神镜像\n"
        "/jy下一层：清完3门后触发本门奇遇并上楼\n"
        "/jy钓鱼 [钓点] [饵剂]：默认山涧浅滩+普通蚯蚓饵\n"
        "/jy重置 confirm：删除当前角色档案\n"
        f"钓点：{'、'.join(FISHING_SPOTS)}\n"
        f"饵剂：{'、'.join(BAITS)}"
    )


def format_attrs(sect_name: str) -> str:
    sect = SECTS[sect_name]
    return "、".join(f"{ATTR_LABELS[k]}+{v}" for k, v in sect.attrs.items())
