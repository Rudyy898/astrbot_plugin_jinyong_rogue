from __future__ import annotations

import random
from math import ceil
from typing import Any

from .game_data import (
    ATTR_LABELS,
    BAITS,
    BACKPACKS,
    BACKPACKS_BY_NAME,
    BOSSES,
    BOSS_CLEAR_REWARDS,
    DIFFICULTIES,
    ENCOUNTER_RULES,
    EQUIPMENT_BY_ID,
    EQUIPMENT_BY_NAME,
    EQUIPMENT_ROWS,
    FISH_CONSUMABLES,
    FISH_CONSUMABLES_BY_NAME,
    EVENT_WEIGHTS,
    FISHING_LOOT_ROWS,
    FISHING_POOLS,
    ITEMS_BY_TIER,
    MARTIAL_ART_EFFECTS,
    MARTIAL_ART_SKILLS,
    MARTIAL_ART_SKILLS_BY_NAME,
    META_UPGRADE_ALIASES,
    META_UPGRADE_ORDER,
    META_UPGRADES,
    PLAYER_START,
    SECT_ENCOUNTER_RULES,
    SECTS,
    SKILL_COMBAT_BY_NAME,
    STATUS_EFFECTS,
)


MAX_FLOOR = 7
DOORS_PER_FLOOR = 3
_DICE_RNG = random.SystemRandom()


def new_player(user_id: str, nickname: str, sect_name: str, difficulty: str, meta_progression: dict[str, Any] | None = None) -> dict[str, Any]:
    sect = SECTS[sect_name]
    meta = normalize_meta_progression(meta_progression)
    fishing_meta = _meta_upgrade_row(meta, "fishing_preparation")
    carried_baits = {}
    if fishing_meta["carry_bait_id"] and int(fishing_meta["carry_bait_qty"]) > 0:
        carried_baits[str(fishing_meta["carry_bait_id"])] = int(fishing_meta["carry_bait_qty"])
    hp = PLAYER_START["hp_base"] + sect.attrs.get("con", 0) * PLAYER_START["hp_per_con"]
    hp += _meta_value(meta, "starting_vigor", "max_hp_bonus")
    mp = PLAYER_START["mp_base"] + sect.attrs.get("int", 0) * PLAYER_START["mp_per_int"]
    mp += _trait_value(sect_name, "max_mp_bonus")
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
        "silver": PLAYER_START["silver"] + _meta_value(meta, "starting_silver", "starting_silver_bonus"),
        "supplies": PLAYER_START["supplies"],
        "materials": 0,
        "essence": 0,
        "scrolls": 0,
        "elixirs": 0,
        "fragments": [],
        "buffs": [],
        "statuses": {},
        "consumables": {},
        "backpack_id": "cloth_travel_bundle",
        "meta_progression": meta,
        "carried_baits": carried_baits,
        "inventory": {},
        "pending_items": {},
        "equipped": {},
        "active_skill": "",
        "merchant_offer": {},
        "fished_floor_keys": [],
        "fish_pool_history": {},
        "learned_skill_ids": [],
        "exclusive_skill_choices": {},
        "finished": False,
        "frozen": False,
        "next_door_dc_bonus": 0,
    }


def roll_die(sides: int) -> int:
    return _DICE_RNG.randint(1, sides)


def roll_percent() -> int:
    return roll_die(100)


def roll_d20() -> int:
    return roll_die(20)


def roll_dice(spec: str) -> int:
    if not spec:
        return 0
    dice_part, _, bonus_part = spec.partition("+")
    count_part, _, die_part = dice_part.partition("d")
    total = sum(roll_die(int(die_part)) for _ in range(int(count_part)))
    return total + (int(bonus_part) if bonus_part else 0)


def roll_dice_results(count: int, die: int, bonus: int = 0) -> list[int]:
    return [roll_die(die) + bonus for _ in range(count)]


def choose_one(items: list[Any]) -> Any:
    return items[_DICE_RNG.randrange(len(items))]


def weighted_choice(weighted_items: tuple[tuple[str, int], ...]) -> str:
    total_weight = sum(weight for _, weight in weighted_items)
    roll = _DICE_RNG.randint(1, total_weight)
    cursor = 0
    for name, weight in weighted_items:
        cursor += weight
        if roll <= cursor:
            return name
    return weighted_items[-1][0]


def weighted_event() -> str:
    return weighted_choice(EVENT_WEIGHTS)


def attr_bonus(player: dict[str, Any], attr: str) -> int:
    sect = SECTS[player["sect"]]
    if attr == "main":
        return sect.attrs.get(sect.main_attr, 0)
    if attr == "sect":
        return sect.attrs.get(sect.main_attr, 0)
    if attr == "all":
        return sum(sect.attrs.values())
    return sect.attrs.get(attr, 0)


def check(player: dict[str, Any], attr: str, dc: int, extra_bonus: int = 0) -> dict[str, Any]:
    die = roll_d20()
    bonus = attr_bonus(player, attr) + int(player.pop("next_check_bonus", 0)) + extra_bonus
    total = die + bonus
    return {"die": die, "bonus": bonus, "total": total, "success": die == 20 or total >= dc, "crit": die == 20, "fumble": die == 1}


def _trait_value(sect_name: str, effect_type: str) -> int:
    from .game_data import SECT_TRAIT_ROWS

    return sum(int(row["effect_value"]) for row in SECT_TRAIT_ROWS if row["sect"] == sect_name and row["effect_type"] == effect_type)


def normalize_meta_progression(meta_progression: dict[str, Any] | None) -> dict[str, int]:
    meta_progression = meta_progression if isinstance(meta_progression, dict) else {}
    meta = {
        "essence": max(0, int(meta_progression.get("essence", 0))),
        "scrolls": max(0, int(meta_progression.get("scrolls", 0))),
        "elixirs": max(0, int(meta_progression.get("elixirs", 0))),
        "clears": max(0, int(meta_progression.get("clears", 0))),
    }
    for upgrade_id in META_UPGRADE_ORDER:
        max_level = max(META_UPGRADES[upgrade_id])
        meta[upgrade_id] = max(0, min(max_level, int(meta_progression.get(upgrade_id, 0))))
    return meta


def _meta_upgrade_row(meta_progression: dict[str, Any], upgrade_id: str) -> dict[str, Any]:
    meta = normalize_meta_progression(meta_progression)
    return META_UPGRADES[upgrade_id][int(meta.get(upgrade_id, 0))]


def _meta_value(meta_progression: dict[str, Any], upgrade_id: str, key: str) -> int:
    return int(_meta_upgrade_row(meta_progression, upgrade_id).get(key, 0))


def meta_text(meta_progression: dict[str, Any] | None, player: dict[str, Any] | None = None) -> str:
    meta = normalize_meta_progression(meta_progression)
    lines = [
        "【局外强化】",
        f"局外资源：武道真髓×{meta.get('essence', 0)}、武学残卷×{meta.get('scrolls', 0)}、小还丹×{meta.get('elixirs', 0)}、通关次数×{meta.get('clears', 0)}",
    ]
    for upgrade_id in META_UPGRADE_ORDER:
        row = _meta_upgrade_row(meta, upgrade_id)
        next_row = META_UPGRADES[upgrade_id].get(int(row["level"]) + 1)
        lines.append(f"{row['label']} Lv{row['level']}/3：{row['description']}")
        if next_row:
            lines.append(f"下一阶：{next_row['description']}｜消耗武道真髓×{next_row['essence_cost']}、武学残卷×{next_row['scroll_cost']}")
    lines.append("指令：/金庸强化 钓鱼｜背囊｜盘缠｜气血")
    return "\n".join(lines)


def upgrade_meta_progression(player: dict[str, Any], meta_progression: dict[str, Any] | None, upgrade_name: str) -> tuple[str, dict[str, int]]:
    meta = normalize_meta_progression(meta_progression)
    upgrade_id = META_UPGRADE_ALIASES.get(upgrade_name) or upgrade_name
    if upgrade_id not in META_UPGRADES:
        return "未知局外强化。可选：钓鱼、背囊。", meta
    current_level = int(meta[upgrade_id])
    next_row = META_UPGRADES[upgrade_id].get(current_level + 1)
    if next_row is None:
        return f"{META_UPGRADES[upgrade_id][current_level]['label']}已满级。", meta
    essence_cost = int(next_row["essence_cost"])
    scroll_cost = int(next_row["scroll_cost"])
    if int(meta.get("essence", 0)) < essence_cost or int(meta.get("scrolls", 0)) < scroll_cost:
        return f"局外资源不足：需要武道真髓×{essence_cost}、武学残卷×{scroll_cost}。当前武道真髓×{meta.get('essence', 0)}、武学残卷×{meta.get('scrolls', 0)}。", meta
    meta["essence"] = int(meta.get("essence", 0)) - essence_cost
    meta["scrolls"] = int(meta.get("scrolls", 0)) - scroll_cost
    meta[upgrade_id] = current_level + 1
    player["meta_progression"] = meta
    return f"局外强化成功：{next_row['label']} Lv{next_row['level']}。{next_row['description']}", meta


def apply_pending_meta_rewards(meta_progression: dict[str, Any] | None, player: dict[str, Any]) -> tuple[dict[str, int], str]:
    meta = normalize_meta_progression(meta_progression)
    reward = player.pop("pending_meta_rewards", {})
    if not reward:
        return meta, ""
    meta["essence"] += int(reward.get("essence", 0))
    meta["scrolls"] += int(reward.get("scrolls", 0))
    meta["elixirs"] += int(reward.get("elixir", 0))
    meta["clears"] += 1
    player["meta_progression"] = meta
    return (
        meta,
        f"\n局外资源已入账：武道真髓×{reward.get('essence', 0)}、武学残卷×{reward.get('scrolls', 0)}、"
        f"小还丹×{reward.get('elixir', 0)}。累计通关{meta['clears']}次。",
    )


def _apply_damage(player: dict[str, Any], damage: int) -> int:
    damage -= _trait_value(player["sect"], "damage_reduction")
    reduction_die = _trait_value(player["sect"], "damage_reduction_dice")
    if reduction_die:
        damage -= roll_die(reduction_die)
    damage = max(0, damage)
    temp_hp = int(player.get("temp_hp", 0))
    absorbed = min(temp_hp, damage)
    if absorbed:
        player["temp_hp"] = temp_hp - absorbed
    actual = damage - absorbed
    player["hp"] = max(1, player["hp"] - actual)
    return actual


def _event_check_bonus(player: dict[str, Any], event_type: str) -> int:
    bonus = 0
    if event_type == "trap":
        bonus += _trait_value(player["sect"], "trap_check_bonus")
    if event_type == "encounter":
        bonus += _trait_value(player["sect"], "encounter_check_bonus")
    if event_type == "battle":
        bonus += _trait_value(player["sect"], "sword_attack_bonus")
    return bonus


def _status_dc_delta(player: dict[str, Any]) -> int:
    total = 0
    statuses = player.setdefault("statuses", {})
    for status_id, count in list(statuses.items()):
        row = STATUS_EFFECTS.get(status_id)
        if row and int(count) > 0:
            total += int(row["dc_delta"])
    return total


def _apply_status_damage(player: dict[str, Any]) -> str:
    statuses = player.setdefault("statuses", {})
    lines = []
    for status_id, count in list(statuses.items()):
        row = STATUS_EFFECTS.get(status_id)
        if not row or int(count) <= 0:
            statuses.pop(status_id, None)
            continue
        if row["damage_dice"]:
            dmg = roll_dice(str(row["damage_dice"]))
            if status_id == "poison":
                resist = _trait_value(player["sect"], "poison_resist_percent")
                dmg = int(dmg * (100 - resist) / 100)
            actual = _apply_damage(player, dmg)
            lines.append(f"{row['name']}生效：承受{actual}伤害。")
        statuses[status_id] = int(count) - 1
        if statuses[status_id] <= 0:
            statuses.pop(status_id, None)
    return ("\n" + "\n".join(lines)) if lines else ""


def _apply_status(player: dict[str, Any], status_id: str, duration: int = 1) -> str:
    if status_id not in STATUS_EFFECTS:
        return ""
    statuses = player.setdefault("statuses", {})
    statuses[status_id] = max(int(statuses.get(status_id, 0)), duration)
    return f"\n状态附加：{STATUS_EFFECTS[status_id]['name']}（{STATUS_EFFECTS[status_id]['description']}）"


def status_text(player: dict[str, Any]) -> str:
    _ensure_inventory(player)
    sect = SECTS[player["sect"]]
    traits = "、".join(sect.traits[:3])
    fragments = "、".join(player.get("fragments", [])[-4:]) or "暂无"
    buffs = "、".join(player.get("buffs", [])[-4:]) or "暂无"
    statuses = _status_text(player)
    learned = _learned_skill_names(player)
    active_skill = player.get("active_skill") or "自动"
    equipment = _equipment_text(player)
    backpack = _backpack_row(player)
    used_slots = inventory_used_slots(player)
    consumables = _inventory_item_text(player)
    pending = _pending_item_text(player)
    return (
        f"【金庸踢门团】{player.get('nickname', '')}\n"
        f"门派：{player['sect']}（{sect.camp}）｜难度：{player['difficulty']}\n"
        f"进度：第{player['floor']}层，已开门 {player['opened_doors']}/{DOORS_PER_FLOOR}\n"
        f"HP {player['hp']}/{player['max_hp']}｜临时HP {player.get('temp_hp', 0)}｜MP {player['mp']}/{player['max_mp']}｜碎银 {player['silver']}两｜补给 {player['supplies']}\n"
        f"素材 {player['materials']}｜局外点数请用 /金庸局外 查看\n"
        f"核心特性：{traits}\n"
        f"已学进阶武学：{'、'.join(learned) if learned else '暂无'}\n"
        f"当前技能：{active_skill}\n"
        f"装备：{equipment}\n"
        f"近期残页：{fragments}\n"
        f"增益：{buffs}\n"
        f"状态：{statuses}\n"
        f"背囊：{backpack['name']} {used_slots}/{_backpack_capacity(player)}格\n"
        f"随身饵剂：{_carried_bait_text(player)}\n"
        f"背包物品：{consumables}\n"
        f"待拾取：{pending}"
    )


def _consumable_text(player: dict[str, Any]) -> str:
    return _inventory_item_text(player)


def _equipment_text(player: dict[str, Any]) -> str:
    equipped = player.get("equipped", {})
    labels = {"weapon": "武器", "armor": "防具", "accessory": "饰品"}
    items = []
    for slot, label in labels.items():
        item_id = equipped.get(slot)
        row = EQUIPMENT_BY_ID.get(item_id)
        items.append(f"{label}:{row['name'] if row else '无'}")
    return "｜".join(items)


def _status_text(player: dict[str, Any]) -> str:
    items = []
    for status_id, count in player.get("statuses", {}).items():
        row = STATUS_EFFECTS.get(status_id)
        if row and int(count) > 0:
            items.append(f"{row['name']}×{count}")
    return "、".join(items) or "暂无"


def _ensure_inventory(player: dict[str, Any]) -> None:
    player.setdefault("backpack_id", "cloth_travel_bundle")
    inventory = player.setdefault("inventory", {})
    legacy = player.get("consumables", {})
    for item_id, count in list(legacy.items()):
        if item_id in FISH_CONSUMABLES and int(count) > 0:
            inventory[item_id] = int(inventory.get(item_id, 0)) + int(count)
    if legacy:
        player["consumables"] = {}
    player.setdefault("pending_items", {})


def _backpack_row(player: dict[str, Any]) -> dict[str, Any]:
    bag_id = str(player.get("backpack_id", "cloth_travel_bundle"))
    return BACKPACKS.get(bag_id) or BACKPACKS["cloth_travel_bundle"]


def _backpack_capacity(player: dict[str, Any]) -> int:
    backpack = _backpack_row(player)
    capacity = int(backpack["capacity_slots"])
    if backpack["bag_id"] == "cloth_travel_bundle":
        meta = normalize_meta_progression(player.get("meta_progression"))
        capacity += int(_meta_upgrade_row(meta, "backpack_foundation")["initial_backpack_bonus"])
    return capacity


def _inventory_item_row(item_id: str) -> dict[str, Any] | None:
    return FISH_CONSUMABLES.get(item_id) or EQUIPMENT_BY_ID.get(item_id)


def _inventory_item_slots(item_id: str, quantity: int) -> int:
    row = _inventory_item_row(item_id)
    if row is None or quantity <= 0:
        return 0
    stack_size = max(1, int(row["stack_size"]))
    return ceil(quantity / stack_size) * int(row["slot_size"])


def inventory_used_slots(player: dict[str, Any]) -> int:
    _ensure_inventory(player)
    return sum(_inventory_item_slots(item_id, int(count)) for item_id, count in player.get("inventory", {}).items())


def _inventory_free_slots(player: dict[str, Any]) -> int:
    return _backpack_capacity(player) - inventory_used_slots(player)


def _can_add_inventory_item(player: dict[str, Any], item_id: str, quantity: int) -> bool:
    _ensure_inventory(player)
    if quantity <= 0:
        return True
    inventory = player.setdefault("inventory", {})
    before = _inventory_item_slots(item_id, int(inventory.get(item_id, 0)))
    after = _inventory_item_slots(item_id, int(inventory.get(item_id, 0)) + quantity)
    return after - before <= _inventory_free_slots(player)


def _add_inventory_item(player: dict[str, Any], item_id: str, quantity: int) -> bool:
    if not _can_add_inventory_item(player, item_id, quantity):
        return False
    inventory = player.setdefault("inventory", {})
    inventory[item_id] = int(inventory.get(item_id, 0)) + quantity
    return True


def _resolve_inventory_item(item_name: str) -> dict[str, Any] | None:
    return (
        FISH_CONSUMABLES_BY_NAME.get(item_name)
        or FISH_CONSUMABLES.get(item_name)
        or EQUIPMENT_BY_NAME.get(item_name)
        or EQUIPMENT_BY_ID.get(item_name)
    )


def _inventory_item_text(player: dict[str, Any]) -> str:
    _ensure_inventory(player)
    items = []
    for item_id, count in player.get("inventory", {}).items():
        row = _inventory_item_row(item_id)
        if row and int(count) > 0:
            slots = _inventory_item_slots(item_id, int(count))
            items.append(f"{row['name']}×{count}({slots}格)")
    return "、".join(items) or "暂无"


def _pending_item_text(player: dict[str, Any]) -> str:
    _ensure_inventory(player)
    items = []
    for item_id, count in player.get("pending_items", {}).items():
        row = _inventory_item_row(item_id)
        if row and int(count) > 0:
            items.append(f"{row['name']}×{count}")
    return "、".join(items) or "暂无"


def _carried_bait_text(player: dict[str, Any]) -> str:
    carried = player.get("carried_baits", {})
    items = []
    for bait in BAITS.values():
        count = int(carried.get(str(bait["bait_id"]), 0))
        if count > 0:
            items.append(f"{bait['name']}×{count}")
    return "、".join(items) or "暂无"


def _equipment_bonus(player: dict[str, Any], key: str) -> int:
    total = 0
    for item_id in player.get("equipped", {}).values():
        row = EQUIPMENT_BY_ID.get(item_id)
        if row:
            total += int(row.get(key, 0))
    return total


def _player_ac(player: dict[str, Any]) -> int:
    return 12 + attr_bonus(player, "dex") + _equipment_bonus(player, "ac_bonus")


def set_active_skill(player: dict[str, Any], skill_name: str) -> str:
    if skill_name in {"自动", "auto", "AUTO"}:
        player["active_skill"] = ""
        return "当前技能已改为自动选择。"
    if skill_name not in _available_combat_skill_names(player):
        return "你尚未掌握该武学。可用：" + "、".join(_available_combat_skill_names(player))
    if _skill_combat_row(skill_name) is None:
        return f"「{skill_name}」没有战斗数值配置，无法设为当前技能。"
    player["active_skill"] = skill_name
    return f"当前技能已设为「{skill_name}」。"


def equip_item(player: dict[str, Any], item_name: str) -> str:
    _ensure_inventory(player)
    item = EQUIPMENT_BY_NAME.get(item_name) or EQUIPMENT_BY_ID.get(item_name)
    if item is None:
        return "未知装备。当前背包：" + _inventory_item_text(player)
    if int(player.get("inventory", {}).get(item["item_id"], 0)) <= 0:
        return f"你没有「{item['name']}」。"
    slot = str(item["slot"])
    old_id = player.setdefault("equipped", {}).get(slot)
    old_hp_bonus = int(EQUIPMENT_BY_ID.get(old_id, {}).get("max_hp_bonus", 0)) if old_id else 0
    new_hp_bonus = int(item.get("max_hp_bonus", 0))
    player["equipped"][slot] = str(item["item_id"])
    hp_delta = new_hp_bonus - old_hp_bonus
    if hp_delta:
        player["max_hp"] = max(1, player["max_hp"] + hp_delta)
        player["hp"] = min(player["max_hp"], max(1, player["hp"] + max(0, hp_delta)))
    return f"已装备「{item['name']}」到{slot}。命中+{item['attack_bonus']}｜伤害+{item['damage_bonus']}｜AC+{item['ac_bonus']}｜HP+{item['max_hp_bonus']}。"


def inventory_text(player: dict[str, Any]) -> str:
    _ensure_inventory(player)
    backpack = _backpack_row(player)
    lines = [
        f"【背包】{backpack['name']}｜容量 {inventory_used_slots(player)}/{_backpack_capacity(player)}格｜剩余 {_inventory_free_slots(player)}格",
        f"物品：{_inventory_item_text(player)}",
        f"装备：{_equipment_text(player)}",
        f"待拾取：{_pending_item_text(player)}",
        "规则：鱼获消耗品进背包；碎银、素材、残卷、残页、补给、小还丹不占背包格。",
        "背囊："
    ]
    for row in BACKPACKS.values():
        lines.append(f"{row['name']}：{row['capacity_slots']}格，{row['price']}两，{row['description']}")
    return "\n".join(lines)


def sect_list_text() -> str:
    grouped: dict[str, list[str]] = {}
    for sect in SECTS.values():
        grouped.setdefault(sect.camp, []).append(sect.name)
    lines = ["可选门派："]
    for camp, names in grouped.items():
        lines.append(f"{camp}：{'、'.join(names)}")
    return "\n".join(lines)


def command_hint_text(player: dict[str, Any] | None = None) -> str:
    if player is None:
        return "下一步可用：/金庸门派｜/金庸开局 门派 [普通|困难]｜/金庸帮助"

    if player.get("finished") or player.get("frozen"):
        commands = ["/金庸局外", "/金庸强化 强化名", "/金庸重置 confirm"]
    elif int(player.get("floor", 1)) >= MAX_FLOOR:
        commands = ["/金庸踢门", "/金庸状态", "/金庸技能 武学名|自动"]
    elif int(player.get("opened_doors", 0)) >= DOORS_PER_FLOOR:
        commands = ["/金庸下一层", "/金庸钓鱼 [饵剂]", "/金庸状态"]
    else:
        commands = ["/金庸踢门", "/金庸钓鱼 [饵剂]", "/金庸状态"]

    if player.get("merchant_offer"):
        commands.insert(0, "/金庸买包")
    if player.get("pending_items"):
        commands.append("/金庸拾取 物品名 [数量]")
    if player.get("inventory"):
        commands.append("/金庸背包")

    deduped = list(dict.fromkeys(commands))
    return "下一步可用：" + "｜".join(deduped[:4])


def open_door(player: dict[str, Any]) -> str:
    if player.get("finished") or player.get("frozen"):
        return "该角色已通关飞升并冻结，请用 /金庸重置 confirm 开新档。"
    if player["floor"] == MAX_FLOOR:
        return boss_fight(player)
    if player["opened_doors"] >= DOORS_PER_FLOOR:
        return "本层3个事件门已清完。发送 /金庸下一层 进行本门奇遇检定并进入下一层。"

    event_type = weighted_event()
    difficulty = DIFFICULTIES[player["difficulty"]]
    dc = 9 + player["floor"] + difficulty["base_dc"] - 10 + player.pop("next_door_dc_bonus", 0) + _status_dc_delta(player)
    status_line = _apply_status_damage(player)
    sect = SECTS[player["sect"]]
    result = check(player, sect.main_attr, max(8, dc), _event_check_bonus(player, event_type))
    player["opened_doors"] += 1

    if event_type == "battle":
        return status_line + _battle(player, result)
    if event_type == "chest":
        return status_line + _chest(player, result)
    if event_type == "encounter":
        return status_line + _encounter(player, result)
    if event_type == "trap":
        return status_line + _trap(player, result)
    return status_line + _merchant(player, result)


def _battle(player: dict[str, Any], result: dict[str, Any]) -> str:
    rule = ENCOUNTER_RULES["battle"]
    enemy_hp = int(rule["enemy_hp_base"]) + player["floor"] * int(rule["enemy_hp_per_floor"]) + int(DIFFICULTIES[player["difficulty"]]["enemy_bonus"])
    enemy_ac = 10 + player["floor"] + int(DIFFICULTIES[player["difficulty"]]["enemy_bonus"]) // 2
    enemy_attack = 3 + player["floor"] + int(DIFFICULTIES[player["difficulty"]]["enemy_bonus"]) // 2
    enemy_damage = str(rule["fail_damage_dice"])
    combat = _run_turn_combat(player, "守塔高手", enemy_hp, enemy_ac, enemy_attack, enemy_damage, max_rounds=5)
    if combat["victory"]:
        silver = roll_dice(str(rule["success_silver_dice"])) + player["floor"] * int(rule["success_silver_per_floor"])
        player["silver"] += silver
        player["materials"] += int(rule["success_materials"])
        reward_line = f"\n结果：胜利。获得碎银{silver}两、武学素材+{rule['success_materials']}。"
        drop_line = _maybe_equipment_drop(player, 35)
    else:
        silver = roll_dice(str(rule["fail_silver_dice"]))
        player["silver"] += silver
        reward_line = f"\n结果：未能击倒对手，脱身时拾得碎银{silver}两。"
        drop_line = ""
    recovery_line = _post_combat_recovery(player)
    return (
        f"【战斗门】遭遇第{player['floor']}层守塔高手（HP{enemy_hp}｜AC{enemy_ac}）。\n"
        f"入场检定：d20={result['die']} + {result['bonus']} = {result['total']}。\n"
        f"{combat['log']}"
        f"{reward_line}"
        f"{drop_line}"
        f"{recovery_line}"
    )


def _selected_combat_skill(player: dict[str, Any]) -> str:
    active = player.get("active_skill")
    available = _available_combat_skill_names(player)
    if active in available and _skill_combat_row(active):
        return str(active)
    usable = [skill for skill in available if _skill_combat_row(skill)]
    return choose_one(usable)


def _run_turn_combat(player: dict[str, Any], enemy_name: str, enemy_hp: int, enemy_ac: int, enemy_attack: int, enemy_damage_dice: str, max_rounds: int) -> dict[str, Any]:
    lines = []
    for round_no in range(1, max_rounds + 1):
        skill = _selected_combat_skill(player)
        attack_roll = roll_d20()
        attack_bonus = attr_bonus(player, SECTS[player["sect"]].main_attr) + _equipment_bonus(player, "attack_bonus") + _trait_value(player["sect"], "sword_attack_bonus")
        attack_total = attack_roll + attack_bonus
        if attack_roll == 20 or attack_total >= enemy_ac:
            damage_result = _martial_damage_result(player, skill)
            damage = int(damage_result.get("total", 0)) + _equipment_bonus(player, "damage_bonus")
            enemy_hp = max(0, enemy_hp - damage)
            trait_line = _battle_trait_line(player, {"crit": attack_roll == 20}, {"total": damage})
            lines.append(f"第{round_no}回合：你用「{skill}」攻击 d20={attack_roll}+{attack_bonus}={attack_total} 命中，造成{damage}伤害，敌HP剩{enemy_hp}。{damage_result['line']}{trait_line}")
        else:
            lines.append(f"第{round_no}回合：你用「{skill}」攻击 d20={attack_roll}+{attack_bonus}={attack_total} 未破AC{enemy_ac}。")
        if enemy_hp <= 0:
            return {"victory": True, "log": "\n".join(lines)}

        enemy_roll = roll_d20()
        enemy_total = enemy_roll + enemy_attack
        player_ac = _player_ac(player)
        if enemy_roll == 20 or enemy_total >= player_ac:
            raw_damage = roll_dice(enemy_damage_dice)
            actual = _apply_damage(player, raw_damage)
            lines.append(f"{enemy_name}反击 d20={enemy_roll}+{enemy_attack}={enemy_total} 命中AC{player_ac}，你损失{actual}HP。")
        else:
            lines.append(f"{enemy_name}反击 d20={enemy_roll}+{enemy_attack}={enemy_total} 未破AC{player_ac}。")
    return {"victory": False, "log": "\n".join(lines)}


def _post_combat_recovery(player: dict[str, Any]) -> str:
    lines = []
    if player["sect"] == "华山" and "养气诀" in SECTS["华山"].skills and player["hp"] < player["max_hp"]:
        effect = MARTIAL_ART_EFFECTS["养气诀"]
        recovered = min(player["max_hp"] - player["hp"], int(effect["effect_value"]))
        player["hp"] += recovered
        lines.append(f"养气诀（{effect['tier']}）生效：脱战调息，回复{recovered}HP。")
    trait_hp = _trait_value(player["sect"], "post_combat_hp_recovery")
    if trait_hp and player["hp"] < player["max_hp"]:
        recovered = min(player["max_hp"] - player["hp"], trait_hp)
        player["hp"] += recovered
        lines.append(f"门派特性生效：战后回复{recovered}HP。")
    trait_mp = _trait_value(player["sect"], "post_combat_mp_recovery")
    if trait_mp and player["mp"] < player["max_mp"]:
        recovered = min(player["max_mp"] - player["mp"], trait_mp)
        player["mp"] += recovered
        lines.append(f"门派特性生效：战后回复{recovered}MP。")
    return ("\n" + "\n".join(lines)) if lines else ""


def _maybe_equipment_drop(player: dict[str, Any], chance_percent: int) -> str:
    roll = roll_percent()
    if roll > chance_percent:
        return f"\n装备掉落：d100={roll}，阈值≤{chance_percent}，无掉落。"
    candidates = [row for row in EQUIPMENT_ROWS if int(row["min_floor"]) <= int(player["floor"])]
    if not candidates:
        return ""
    item = choose_one(candidates)
    if _add_inventory_item(player, str(item["item_id"]), 1):
        return f"\n装备掉落：d100={roll}，获得「{item['name']}」（{item['rarity']}）。"
    pending = player.setdefault("pending_items", {})
    pending[item["item_id"]] = int(pending.get(item["item_id"], 0)) + 1
    return f"\n装备掉落：d100={roll}，获得「{item['name']}」，但背囊已满，已放入待拾取。"


def _chest(player: dict[str, Any], result: dict[str, Any]) -> str:
    rule = ENCOUNTER_RULES["chest"]
    if result["fumble"]:
        dmg = roll_dice(str(rule["fumble_damage_dice"]))
        dmg = _apply_damage(player, dmg)
        return f"【宝箱门】机关暗弩触发：d20=1。损失{dmg}HP，宝箱损毁。"
    silver = roll_dice(str(rule["success_silver_dice"])) + player["floor"] * int(rule["success_silver_per_floor"])
    player["silver"] += silver
    player["supplies"] += int(rule["success_supplies"])
    tier = "ultimate" if result["crit"] else "advanced"
    player["fragments"].append(_fragment_name(player["sect"], tier))
    drop_line = _maybe_equipment_drop(player, 45 if result["crit"] else 25)
    return f"【宝箱门】开箱检定 {result['total']}。获得碎银{silver}两、补给+1、{player['fragments'][-1]}。{drop_line}"


def _encounter(player: dict[str, Any], result: dict[str, Any]) -> str:
    rule = ENCOUNTER_RULES["encounter"]
    if result["success"]:
        player["materials"] += int(rule["success_materials"])
        mp_recovery = int(rule["success_mp_recovery"]) + _trait_value(player["sect"], "encounter_mp_recovery_bonus")
        player["mp"] = min(player["max_mp"], player["mp"] + mp_recovery)
        skill_line = _sect_encounter_skill_reward(player)
        return f"【奇遇门】高人指点成功：d20={result['die']}，武学素材+{rule['success_materials']}，MP恢复{mp_recovery}。{skill_line}"
    return f"【奇遇门】擦肩而过：d20={result['die']} + {result['bonus']} = {result['total']}，无奖励也无惩罚。"


def _fragment_name(sect_name: str, tier: str) -> str:
    return str(ITEMS_BY_TIER[tier]["name_template"]).format(sect=sect_name)


def _learned_skill_names(player: dict[str, Any]) -> list[str]:
    names = []
    for skill_id in player.get("learned_skill_ids", []):
        row = MARTIAL_ART_SKILLS.get(skill_id)
        if row:
            names.append(str(row["name"]))
    return names


def _available_combat_skill_names(player: dict[str, Any]) -> list[str]:
    sect = SECTS[player["sect"]]
    return list(sect.skills) + _learned_skill_names(player)


def _sect_encounter_skill_reward(player: dict[str, Any]) -> str:
    if player["floor"] < 2:
        return ""
    sect_name = str(player["sect"])
    choices = player.setdefault("exclusive_skill_choices", {})

    candidates = [
        row for row in MARTIAL_ART_SKILLS.values()
        if row["sect"] == sect_name
        and row["obtain_source"] == "sect_encounter"
        and player["floor"] >= int(row["obtain_min_floor"])
        and row["skill_id"] not in player.get("learned_skill_ids", [])
        and (not row["exclusive_group"] or row["exclusive_group"] not in choices)
    ]
    if not candidates:
        return ""

    row = choose_one(candidates)
    player.setdefault("learned_skill_ids", []).append(row["skill_id"])
    if row["exclusive_group"]:
        choices[str(row["exclusive_group"])] = row["skill_id"]
    return (
        f"\n进阶武学奇遇：习得「{row['name']}」（{row['tier']}）。"
        f"该互斥组已锁定，不能再习得同组另一门进阶武学。"
    )


def _skill_combat_row(skill_name: str) -> dict[str, Any] | None:
    row = SKILL_COMBAT_BY_NAME.get(skill_name)
    if row is None:
        art = MARTIAL_ART_SKILLS_BY_NAME.get(skill_name)
        if art:
            return {
                "name": art["name"],
                "category": art["category"],
                "damage_type": art["damage_type"],
                "attack_segments": art["attack_segments"],
                "damage_dice_count": art["damage_dice_count"],
                "damage_die": art["damage_die"],
                "damage_bonus": art["damage_bonus"],
                "mp_cost": art["mp_cost"],
            }
    return row


def _martial_damage_result(player: dict[str, Any], skill_name: str) -> dict[str, Any]:
    row = _skill_combat_row(skill_name)
    if row is None:
        return {"line": "", "total": 0, "damage_type": ""}
    if player["mp"] < int(row["mp_cost"]):
        return {"line": f"\n{skill_name}需要{row['mp_cost']}MP，当前MP不足，改用基础招式完成战斗。", "total": 0, "damage_type": ""}

    player["mp"] -= int(row["mp_cost"])
    segment_rolls = [
        sum(roll_dice_results(int(row["damage_dice_count"]), int(row["damage_die"]))) + int(row["damage_bonus"])
        for _ in range(int(row["attack_segments"]))
    ]
    base_total = sum(segment_rolls)
    total = _damage_with_trait_bonus(player, str(row["damage_type"]), base_total)
    bonus_line = f"，门派伤害增幅后={total}" if total != base_total else ""
    line = (
        f"\n{skill_name}消耗{row['mp_cost']}MP："
        f"{row['attack_segments']}段{row['damage_dice_count']}d{row['damage_die']}+{row['damage_bonus']}"
        f"{row['damage_type']}伤害，掷骰={segment_rolls}，合计{base_total}{bonus_line}。"
    )
    return {"line": line, "total": total, "damage_type": str(row["damage_type"])}


def _damage_with_trait_bonus(player: dict[str, Any], damage_type: str, total: int) -> int:
    percent = 0
    if player["sect"] == "明教" and damage_type == "灼烧":
        percent += _trait_value(player["sect"], "damage_type_bonus_percent")
    if player["sect"] == "青城" and damage_type == "毒":
        percent += _trait_value(player["sect"], "damage_type_bonus_percent")
    if percent:
        return int(total * (100 + percent) / 100)
    return total


def _battle_trait_line(player: dict[str, Any], result: dict[str, Any], damage_result: dict[str, Any]) -> str:
    lines = []
    if _trait_value(player["sect"], "status_apply"):
        lines.append(_apply_status(player, "slow", 1).strip())
    lifesteal = _trait_value(player["sect"], "crit_lifesteal_percent")
    if lifesteal and result["crit"] and int(damage_result.get("total", 0)) > 0:
        amount = int(int(damage_result["total"]) * lifesteal / 100)
        recovered = min(player["max_hp"] - player["hp"], amount)
        if recovered > 0:
            player["hp"] += recovered
            lines.append(f"门派特性生效：暴击吸血回复{recovered}HP。")
    return ("\n" + "\n".join(line for line in lines if line)) if lines else ""


def _trap(player: dict[str, Any], result: dict[str, Any]) -> str:
    rule = ENCOUNTER_RULES["trap"]
    if result["success"]:
        silver = int(rule["success_silver"])
        player["silver"] += silver
        return f"【陷阱门】拆解成功：d20={result['die']}，回收机关零件换得碎银{silver}两。"
    dmg = roll_dice(str(rule["fail_damage_dice"]))
    dmg = _apply_damage(player, dmg)
    return f"【陷阱门】检定失败：d20={result['die']}，损失{dmg}HP。{_apply_status(player, 'poison', 1)}"


def _merchant(player: dict[str, Any], result: dict[str, Any]) -> str:
    rule = ENCOUNTER_RULES["merchant"]
    discount = int(rule["success_discount"]) if result["success"] else 0
    cost = max(int(rule["min_cost"]), int(rule["base_cost"]) - discount)
    bag_offer_line = _create_merchant_backpack_offer(player, result)
    if player["silver"] >= cost:
        player["silver"] -= cost
        player["supplies"] += int(rule["buy_supplies"])
        return f"【商人门】交涉检定{result['total']}，花费{cost}两购得补给+{rule['buy_supplies']}。{bag_offer_line}"
    return f"【商人门】游商报价{cost}两，但你碎银不足。{bag_offer_line}"


def _create_merchant_backpack_offer(player: dict[str, Any], result: dict[str, Any]) -> str:
    current = _backpack_row(player)
    candidates = [
        row for row in BACKPACKS.values()
        if int(row["capacity_slots"]) > int(current["capacity_slots"])
    ]
    if not candidates:
        player["merchant_offer"] = {}
        return "\n游商查看你的行囊后摇头：已无更大背囊可售。"

    target = min(candidates, key=lambda row: int(row["capacity_slots"]))
    rule = ENCOUNTER_RULES["merchant"]
    discount_percent = int(rule["backpack_discount_percent_success"]) if result["success"] else 0
    price = int(int(target["price"]) * (100 - discount_percent) / 100)
    player["merchant_offer"] = {
        "offer_type": "backpack",
        "bag_id": target["bag_id"],
        "name": target["name"],
        "price": price,
        "floor": player["floor"],
    }
    discount_line = f"，交涉成功折扣{discount_percent}%" if discount_percent else ""
    return f"\n游商另售「{target['name']}」：{target['capacity_slots']}格，报价{price}两{discount_line}。发送 /金庸买包 确认购买。"


def next_floor(player: dict[str, Any]) -> str:
    if player.get("finished") or player.get("frozen"):
        return "该角色已通关飞升并冻结，请重置后再开新周目。"
    if player["floor"] >= MAX_FLOOR:
        return "你已在武神殿。发送 /金庸踢门 挑战武神镜像。"
    if player["opened_doors"] < DOORS_PER_FLOOR:
        return f"本层还剩 {DOORS_PER_FLOOR - player['opened_doors']} 个门未清。"

    sect = SECTS[player["sect"]]
    dc = int(DIFFICULTIES[player["difficulty"]]["base_dc"])
    result = check(player, sect.main_attr, dc)
    lines = [f"【本门奇遇】d20={result['die']} + {result['bonus']} = {result['total']}，DC{dc}。"]
    if result["crit"]:
        rule = SECT_ENCOUNTER_RULES["crit"]
        reward = _fragment_name(player["sect"], str(rule["fragment_tier"]))
        player["fragments"].append(reward)
        player["supplies"] += int(rule["supplies_delta"])
        player["materials"] += int(rule["materials_delta"])
        lines.append(f"自然20：获得{reward}、专属丹药补给+{rule['supplies_delta']}、素材+{rule['materials_delta']}。")
        skill_line = _sect_encounter_skill_reward(player)
        if skill_line:
            lines.append(skill_line.strip())
    elif result["success"]:
        rule = SECT_ENCOUNTER_RULES["success"]
        reward = _fragment_name(player["sect"], str(rule["fragment_tier"]))
        player["fragments"].append(reward)
        player["supplies"] += int(rule["supplies_delta"])
        player["materials"] += int(rule["materials_delta"])
        lines.append(f"成功：获得{reward}、普通补给+{rule['supplies_delta']}。")
        skill_line = _sect_encounter_skill_reward(player)
        if skill_line:
            lines.append(skill_line.strip())
    elif result["fumble"]:
        if player["supplies"] > 0:
            rule = SECT_ENCOUNTER_RULES["fumble_with_supply"]
            player["supplies"] += int(rule["supplies_delta"])
            lines.append(f"自然1：遗失普通补给{abs(int(rule['supplies_delta']))}份。")
        else:
            rule = SECT_ENCOUNTER_RULES["fumble_without_supply"]
            player["next_door_dc_bonus"] = int(rule["next_door_dc_delta"])
            lines.append(f"自然1：下次进门首次检定DC+{rule['next_door_dc_delta']}。")
    else:
        lines.append("失败：无奖励，无负面效果。")

    player["floor"] += 1
    player["opened_doors"] = 0
    player["merchant_offer"] = {}
    if player["floor"] == MAX_FLOOR:
        lines.append("第7层武神殿已解锁。发送 /金庸踢门 挑战唯一BOSS武神镜像。")
    else:
        lines.append(f"进入第{player['floor']}层。")
    return "\n".join(lines)


def boss_fight(player: dict[str, Any]) -> str:
    sect = SECTS[player["sect"]]
    boss = BOSSES["wushen_mirror"]
    intro = check(player, sect.main_attr, int(boss["check_dc"]) + int(DIFFICULTIES[player["difficulty"]]["enemy_bonus"]) // 2)
    combat = _run_turn_combat(
        player,
        str(boss["name"]),
        int(boss["hp"]),
        int(boss["ac"]),
        7 + int(DIFFICULTIES[player["difficulty"]]["enemy_bonus"]) // 2,
        str(boss["fail_damage_dice"]),
        max_rounds=8,
    )
    if not combat["victory"]:
        return (
            f"【武神殿】{boss['name']} HP{boss['hp']} AC{boss['ac']}，四象护体抵消伤害。\n"
            f"入殿检定：d20={intro['die']} + {intro['bonus']} = {intro['total']}。\n"
            f"{combat['log']}\n"
            f"挑战未竟，补给整备后可再次 /金庸踢门。"
        )

    reward = BOSS_CLEAR_REWARDS[player["difficulty"]]
    player["silver"] += int(reward["silver"])
    player["pending_meta_rewards"] = {
        "essence": int(reward["essence"]),
        "scrolls": int(reward["scrolls"]),
        "elixir": int(reward["elixir"]),
    }
    ultimate_roll = roll_percent()
    if ultimate_roll <= int(boss["ultimate_drop_chance"]):
        player["fragments"].append(sect.ultimate)
    player["finished"] = True
    player["frozen"] = True
    return (
        "【武神殿通关】你击败武神镜像，角色飞升并永久冻结。\n"
        f"入殿检定：d20={intro['die']} + {intro['bonus']} = {intro['total']}。\n"
        f"{combat['log']}\n"
        f"通关奖励：武道真髓×{reward['essence']}、武学残卷×{reward['scrolls']}、小还丹×{reward['elixir']}、碎银×{reward['silver']}两。\n"
        f"本门顶级绝学掉落：d100={ultimate_roll}，阈值≤{boss['ultimate_drop_chance']}。当前残页：{'、'.join(player['fragments'][-5:]) or '暂无'}。"
    )


def fish(player: dict[str, Any], bait_name: str) -> str:
    bait = BAITS.get(bait_name)
    if bait is None:
        return "未知饵剂。可选：" + "、".join(BAITS)
    floor_key = str(player["floor"])
    fished_floor_keys = player.setdefault("fished_floor_keys", [])
    if floor_key in fished_floor_keys:
        return f"第{player['floor']}层已经钓过鱼。每层只能进行一次钓鱼。"

    carried = player.setdefault("carried_baits", {})
    bait_id = str(bait["bait_id"])
    used_carried_bait = int(carried.get(bait_id, 0)) > 0
    total_cost = 0 if used_carried_bait else int(bait["price"])
    if player["silver"] < total_cost:
        return f"碎银不足，本次垂钓需要{total_cost}两。"
    player["silver"] -= total_cost
    if used_carried_bait:
        carried[bait_id] = int(carried.get(bait_id, 0)) - 1
        if carried[bait_id] <= 0:
            carried.pop(bait_id, None)

    pool = _select_fishing_pool(player)
    roll_count = max(int(pool["advantage_rolls"]), int(bait["advantage_rolls"]))
    raw_rolls = [roll_percent() for _ in range(roll_count)]
    base_roll = min(raw_rolls)
    meta = normalize_meta_progression(player.get("meta_progression"))
    meta_quality_bonus = int(_meta_upgrade_row(meta, "fishing_preparation")["fishing_quality_bonus"])
    quality_bonus = int(pool["loot_roll_bonus"]) + int(bait["loot_roll_bonus"]) + meta_quality_bonus
    final_roll = max(1, base_roll - quality_bonus)
    loot_row = _select_fishing_loot(final_roll)
    item = FISH_CONSUMABLES[str(loot_row["item_id"])]
    quantity = int(loot_row["quantity"])
    stored = _add_inventory_item(player, str(item["item_id"]), quantity)
    if stored:
        storage_line = f"已收入背囊，占格后容量 {inventory_used_slots(player)}/{_backpack_capacity(player)}。"
    else:
        pending = player.setdefault("pending_items", {})
        pending[item["item_id"]] = int(pending.get(item["item_id"], 0)) + quantity
        storage_line = (
            f"背囊剩余{_inventory_free_slots(player)}格不足，已暂存为待拾取。"
            f"可先 /金庸丢弃 物品名 [数量]，再 /金庸拾取 {item['name']} {quantity}。"
        )
    fished_floor_keys.append(floor_key)
    player.setdefault("fish_pool_history", {})[floor_key] = str(pool["pool_id"])

    return (
        f"【钓鱼】第{player['floor']}层｜{pool['name']}｜{bait_name}｜花费{total_cost}两{'｜消耗随身饵剂' if used_carried_bait else ''}\n"
        f"鱼池品质：{pool['tier']}｜鱼池修正+{pool['loot_roll_bonus']}｜钓饵修正+{bait['loot_roll_bonus']}｜局外修正+{meta_quality_bonus}｜优势骰数{roll_count}\n"
        f"鱼获判定：d100={raw_rolls}，取{base_roll}，品质修正后={final_roll}\n"
        f"获得：{item['name']}×{quantity}（{item['rarity']}，{item['description']}）\n"
        f"{storage_line}"
    )


def _select_fishing_pool(player: dict[str, Any]) -> dict[str, Any]:
    floor = int(player["floor"])
    if floor == 7:
        return FISHING_POOLS["wushen_dragon_pool"]
    advanced = FISHING_POOLS["hidden_cold_pool"]
    if int(advanced["min_floor"]) <= floor <= int(advanced["max_floor"]):
        if roll_percent() <= int(advanced["spawn_chance_percent"]):
            return advanced
    return FISHING_POOLS["floor_stream"]


def _select_fishing_loot(final_roll: int) -> dict[str, Any]:
    for row in FISHING_LOOT_ROWS:
        if int(row["roll_min"]) <= final_roll <= int(row["roll_max"]):
            return row
    return FISHING_LOOT_ROWS[-1]


def use_consumable(player: dict[str, Any], item_name: str) -> str:
    _ensure_inventory(player)
    item = _resolve_inventory_item(item_name)
    if item is None:
        return "未知鱼获消耗品。可用：" + _inventory_item_text(player)
    if item.get("item_type") != "fish_consumable":
        return f"「{item['name']}」不是可使用消耗品；装备请用 /金庸装备 {item['name']}。"
    item_id = str(item["item_id"])
    inventory = player.setdefault("inventory", {})
    if int(inventory.get(item_id, 0)) <= 0:
        return f"你没有可使用的「{item['name']}」。"

    inventory[item_id] = int(inventory.get(item_id, 0)) - 1
    if inventory[item_id] <= 0:
        inventory.pop(item_id, None)
    effect_type = str(item["effect_type"])
    amount = roll_dice(str(item["effect_dice"])) + int(item["effect_value"])
    if effect_type == "hp_recovery":
        before = player["hp"]
        player["hp"] = min(player["max_hp"], player["hp"] + amount)
        return f"使用「{item['name']}」：回复HP {player['hp'] - before}点。"
    if effect_type == "mp_recovery":
        before = player["mp"]
        player["mp"] = min(player["max_mp"], player["mp"] + amount)
        return f"使用「{item['name']}」：回复MP {player['mp'] - before}点。"
    if effect_type == "temp_hp":
        player["temp_hp"] = max(int(player.get("temp_hp", 0)), amount)
        return f"使用「{item['name']}」：获得临时HP {player['temp_hp']}点，持续到下一场战斗。"
    if effect_type == "next_d20_bonus":
        player["next_check_bonus"] = int(player.get("next_check_bonus", 0)) + int(item["effect_value"])
        return f"使用「{item['name']}」：下一次d20检定+{item['effect_value']}。"
    return f"使用「{item['name']}」失败：物品效果表配置错误 effect_type={effect_type}。"


def discard_item(player: dict[str, Any], item_name: str, quantity: int = 1) -> str:
    _ensure_inventory(player)
    item = _resolve_inventory_item(item_name)
    if item is None:
        return "未知物品。当前背包：" + _inventory_item_text(player)
    if not bool(item["droppable"]):
        return f"「{item['name']}」不可丢弃。"
    quantity = max(1, quantity)
    item_id = str(item["item_id"])
    inventory = player.setdefault("inventory", {})
    owned = int(inventory.get(item_id, 0))
    if owned <= 0:
        return f"你没有「{item['name']}」。"
    removed = min(quantity, owned)
    left = owned - removed
    if left:
        inventory[item_id] = left
    else:
        inventory.pop(item_id, None)
        for slot, equipped_id in list(player.setdefault("equipped", {}).items()):
            if equipped_id == item_id:
                player["equipped"].pop(slot, None)
    return f"已丢弃「{item['name']}」×{removed}。当前背囊容量 {inventory_used_slots(player)}/{_backpack_capacity(player)}格。"


def pickup_item(player: dict[str, Any], item_name: str, quantity: int = 1) -> str:
    _ensure_inventory(player)
    item = _resolve_inventory_item(item_name)
    if item is None:
        return "未知待拾取物品。当前待拾取：" + _pending_item_text(player)
    quantity = max(1, quantity)
    item_id = str(item["item_id"])
    pending = player.setdefault("pending_items", {})
    available = int(pending.get(item_id, 0))
    if available <= 0:
        return f"没有待拾取的「{item['name']}」。"
    amount = min(quantity, available)
    if not _add_inventory_item(player, item_id, amount):
        return f"背囊剩余{_inventory_free_slots(player)}格不足，无法拾取「{item['name']}」×{amount}。"
    left = available - amount
    if left:
        pending[item_id] = left
    else:
        pending.pop(item_id, None)
    return f"已拾取「{item['name']}」×{amount}。当前背囊容量 {inventory_used_slots(player)}/{_backpack_capacity(player)}格。"


def buy_backpack(player: dict[str, Any], backpack_name: str = "") -> str:
    _ensure_inventory(player)
    offer = player.get("merchant_offer") or {}
    if offer.get("offer_type") != "backpack" or int(offer.get("floor", -1)) != int(player["floor"]):
        return "当前没有商人背囊报价。需要在踢门遇到【商人门】后，按商人报价使用 /金庸买包。"
    target = BACKPACKS.get(str(offer.get("bag_id", "")))
    if target is None:
        player["merchant_offer"] = {}
        return "当前商人背囊报价已失效。"
    if backpack_name and backpack_name not in {str(target["name"]), str(target["bag_id"])}:
        return f"当前商人只出售「{target['name']}」。发送 /金庸买包 确认购买。"
    current = _backpack_row(player)
    if int(target["capacity_slots"]) <= int(current["capacity_slots"]):
        player["merchant_offer"] = {}
        return f"当前已装备「{current['name']}」{current['capacity_slots']}格，不能降级或重复购买。"
    price = int(offer["price"])
    if player["silver"] < price:
        return f"碎银不足，购买「{target['name']}」需要{price}两，当前{player['silver']}两。"
    player["silver"] -= price
    player["backpack_id"] = str(target["bag_id"])
    player["merchant_offer"] = {}
    return f"已向游商购买并装备「{target['name']}」：容量提升至{target['capacity_slots']}格，花费{price}两。"


def help_text() -> str:
    return (
        "【金庸武侠DND肉鸽踢门团】\n"
        "/金庸帮助：查看指令\n"
        "/金庸门派：查看16大门派\n"
        "/金庸开局 门派 [普通|困难]：创建角色\n"
        "/金庸状态：查看当前角色\n"
        "/金庸踢门：开启当前层随机事件门；第7层挑战武神镜像\n"
        "/金庸下一层：清完3门后触发本门奇遇并上楼\n"
        "/金庸钓鱼 [饵剂]：每层一次，鱼池自动判定，默认普通蚯蚓饵\n"
        "/金庸背包：查看背囊容量、物品、待拾取与占格规则\n"
        "/金庸装备 装备名：装备武器、防具或饰品\n"
        "/金庸技能 武学名|自动：设置战斗优先使用的武学\n"
        "/金庸买包：遇到商人门后，购买当前商人报价的背囊\n"
        "/金庸局外：查看局外强化等级与下一阶消耗\n"
        "/金庸强化 钓鱼|背囊|盘缠|气血：消耗通关后的局外点数提升局外属性\n"
        "/金庸丢弃 物品名 [数量]：丢弃背包物品\n"
        "/金庸拾取 物品名 [数量]：拾取因容量不足暂存的物品\n"
        "/金庸使用 鱼获名：使用鱼获消耗品\n"
        "/金庸重置 confirm：删除当前角色档案\n"
        "兼容旧指令：以上命令也可继续使用 /jy 前缀。\n"
        f"鱼池：{'、'.join(row['name'] for row in FISHING_POOLS.values())}\n"
        f"饵剂：{'、'.join(BAITS)}"
    )


def format_attrs(sect_name: str) -> str:
    sect = SECTS[sect_name]
    return "、".join(f"{ATTR_LABELS[k]}+{v}" for k, v in sect.attrs.items())
