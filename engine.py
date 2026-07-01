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
    DOOR_TYPE_HINTS,
    ENCOUNTER_RULES,
    ENEMIES_BY_FLOOR,
    EQUIPMENT_DESC,
    EQUIPMENT_BY_ID,
    EQUIPMENT_BY_NAME,
    EQUIPMENT_ROWS,
    FISH_CONSUMABLES,
    FISH_CONSUMABLES_BY_NAME,
    EVENT_WEIGHTS,
    EVENT_FLAVOR,
    FISHING_LOOT_ROWS,
    FISHING_POOLS,
    ITEM_DESC,
    ITEMS_BY_TIER,
    MARTIAL_ART_EFFECTS,
    MARTIAL_ART_SKILLS,
    MARTIAL_ART_SKILLS_BY_NAME,
    MEDICINE_CONSUMABLES,
    MEDICINE_CONSUMABLES_BY_NAME,
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

STARTING_WEAPON_BY_SECT = {
    "少林": "iron_staff",
    "武当": "iron_sword",
    "峨眉": "iron_sword",
    "全真": "iron_sword",
    "华山": "greensteel_sword",
    "丐帮": "bamboo_staff",
    "明教": "iron_sword",
    "青城": "greensteel_sword",
    "雪山派": "greensteel_sword",
    "大理段氏": "iron_sword",
    "逍遥派": "bamboo_staff",
    "金刚宗": "iron_staff",
    "桃花岛": "bamboo_staff",
    "日月神教": "iron_sword",
    "血刀门": "blood_blade",
    "白驼山庄": "bamboo_staff",
}

DEFAULT_MEDICINE_ID = "jinchuang_ointment"
EQUIPMENT_PRICE_BY_RARITY = {
    "common": 36,
    "uncommon": 70,
    "rare": 125,
    "epic": 220,
    "legendary": 420,
}
EQUIPMENT_SELL_RATE_PERCENT = 50


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
    player = {
        "user_id": user_id,
        "nickname": nickname,
        "sect": sect_name,
        "difficulty": difficulty,
        "floor": 1,
        "opened_doors": 0,
        "explored_doors": [False] * DOORS_PER_FLOOR,
        "hp": hp,
        "max_hp": hp,
        "mp": mp,
        "max_mp": mp,
        "silver": PLAYER_START["silver"] + _meta_value(meta, "starting_silver", "starting_silver_bonus"),
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
    _equip_starting_weapon(player)
    _add_inventory_item(player, DEFAULT_MEDICINE_ID, PLAYER_START["starting_medicine"])
    return player


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


def _flavor(items: list[str]) -> str:
    return choose_one(items)


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
        f"HP {player['hp']}/{player['max_hp']}｜临时HP {player.get('temp_hp', 0)}｜MP {player['mp']}/{player['max_mp']}｜AC {_player_ac(player)}｜攻击+{_player_attack_bonus(player)}｜伤害+{_equipment_bonus(player, 'damage_bonus')}｜碎银 {player['silver']}两\n"
        f"属性：{_ability_summary(player)}\n"
        f"素材 {player['materials']}｜局外点数请用 /金庸局外 查看\n"
        f"核心特性：{traits}\n"
        f"已学进阶武学：{'、'.join(learned) if learned else '暂无'}\n"
        f"当前技能：{active_skill}\n"
        f"装备：{equipment}\n"
        f"近期残页：{fragments}\n"
        f"增益：{buffs}\n"
        f"状态：{statuses}\n"
        f"药品：{_medicine_text(player)}\n"
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


def _equipment_price(item: dict[str, Any]) -> int:
    base = EQUIPMENT_PRICE_BY_RARITY.get(str(item.get("rarity")), 50)
    floor_bonus = max(0, int(item.get("min_floor", 1)) - 1) * 8
    stat_bonus = (
        int(item.get("attack_bonus", 0)) * 8
        + int(item.get("damage_bonus", 0)) * 10
        + int(item.get("ac_bonus", 0)) * 12
        + int(item.get("max_hp_bonus", 0)) * 3
    )
    return base + floor_bonus + stat_bonus


def _equipment_sell_price(item: dict[str, Any]) -> int:
    return max(1, int(_equipment_price(item) * EQUIPMENT_SELL_RATE_PERCENT / 100))


def _equipped_count(player: dict[str, Any], item_id: str) -> int:
    return sum(1 for equipped_id in player.get("equipped", {}).values() if equipped_id == item_id)


def _has_current_merchant(player: dict[str, Any]) -> bool:
    if int(player.get("merchant_floor", -1)) == int(player.get("floor", 0)):
        return True
    offer = player.get("merchant_offer") or {}
    if int(offer.get("floor", -1)) == int(player.get("floor", 0)):
        return True
    equipment_offer = offer.get("equipment") or {}
    return int(equipment_offer.get("floor", -1)) == int(player.get("floor", 0))


def _medicine_text(player: dict[str, Any]) -> str:
    _ensure_inventory(player)
    items = []
    for item_id, count in player.get("inventory", {}).items():
        row = MEDICINE_CONSUMABLES.get(item_id)
        if row and int(count) > 0:
            items.append(f"{row['name']}×{count}")
    return "、".join(items) or "暂无"


def _medicine_count(player: dict[str, Any], item_id: str = DEFAULT_MEDICINE_ID) -> int:
    _ensure_inventory(player)
    return int(player.get("inventory", {}).get(item_id, 0))


def _add_medicine(player: dict[str, Any], quantity: int, item_id: str = DEFAULT_MEDICINE_ID) -> None:
    if quantity <= 0:
        return
    if not _add_inventory_item(player, item_id, quantity):
        pending = player.setdefault("pending_items", {})
        pending[item_id] = int(pending.get(item_id, 0)) + quantity


def _remove_medicine(player: dict[str, Any], quantity: int, item_id: str = DEFAULT_MEDICINE_ID) -> int:
    if quantity <= 0:
        return 0
    inventory = player.setdefault("inventory", {})
    removed = min(quantity, int(inventory.get(item_id, 0)))
    if removed <= 0:
        return 0
    left = int(inventory.get(item_id, 0)) - removed
    if left > 0:
        inventory[item_id] = left
    else:
        inventory.pop(item_id, None)
    return removed


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
    legacy_medicine_count = int(player.pop("supplies", 0) or 0)
    if legacy_medicine_count > 0:
        inventory[DEFAULT_MEDICINE_ID] = int(inventory.get(DEFAULT_MEDICINE_ID, 0)) + legacy_medicine_count
    legacy = player.get("consumables", {})
    for item_id, count in list(legacy.items()):
        if item_id in FISH_CONSUMABLES and int(count) > 0:
            inventory[item_id] = int(inventory.get(item_id, 0)) + int(count)
    if legacy:
        player["consumables"] = {}
    player.setdefault("pending_items", {})


def _equip_starting_weapon(player: dict[str, Any]) -> None:
    item_id = STARTING_WEAPON_BY_SECT.get(str(player.get("sect")))
    item = EQUIPMENT_BY_ID.get(item_id or "")
    if not item or item.get("slot") != "weapon":
        return
    inventory = player.setdefault("inventory", {})
    inventory[str(item["item_id"])] = max(1, int(inventory.get(str(item["item_id"]), 0)))
    player.setdefault("equipped", {})["weapon"] = str(item["item_id"])


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
    return FISH_CONSUMABLES.get(item_id) or MEDICINE_CONSUMABLES.get(item_id) or EQUIPMENT_BY_ID.get(item_id)


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
        or MEDICINE_CONSUMABLES_BY_NAME.get(item_name)
        or MEDICINE_CONSUMABLES.get(item_name)
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


def _resource_item_text(player: dict[str, Any]) -> str:
    fragments = player.get("skill_fragments", {})
    fragment_items = [
        f"{_fragment_name(player['sect'], tier)}×{count}(0格)"
        for tier, count in fragments.items()
        if int(count) > 0
    ]
    resources = [
        f"碎银×{player.get('silver', 0)}(0格)",
        f"武学素材×{player.get('materials', 0)}(0格)",
        f"武道真髓×{player.get('essence', 0)}(0格)",
        f"武学残卷×{player.get('scrolls', 0)}(0格)",
    ]
    carried_baits = [
        f"{name}×{count}(0格)"
        for name, count in player.get("carried_baits", {}).items()
        if int(count) > 0
    ]
    return "、".join(resources + fragment_items + carried_baits)


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


def _player_attack_bonus(player: dict[str, Any]) -> int:
    return attr_bonus(player, SECTS[player["sect"]].main_attr) + _equipment_bonus(player, "attack_bonus") + _trait_value(player["sect"], "sword_attack_bonus")


def _ability_summary(player: dict[str, Any]) -> str:
    sect = SECTS[player["sect"]]
    return "｜".join(f"{ATTR_LABELS[key]}+{sect.attrs.get(key, 0)}" for key in ATTR_LABELS)


def _compact_equipment_text(player: dict[str, Any]) -> str:
    equipped = player.get("equipped", {})
    labels = (("weapon", "武"), ("armor", "甲"), ("accessory", "饰"))
    items = []
    for slot, label in labels:
        row = EQUIPMENT_BY_ID.get(equipped.get(slot))
        items.append(f"{label}:{row['name'] if row else '无'}")
    return " ".join(items)


def _core_state_line(player: dict[str, Any]) -> str:
    return (
        f"状态：{_status_text(player)}｜AC {_player_ac(player)}｜攻击+{_player_attack_bonus(player)}｜"
        f"临时HP {player.get('temp_hp', 0)}｜素材 {player.get('materials', 0)}"
    )


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
        f"占格物品：{_inventory_item_text(player)}",
        f"资源物品：{_resource_item_text(player)}",
        f"装备：{_equipment_text(player)}",
        f"待拾取：{_pending_item_text(player)}",
        "查看：/金庸查看 物品名｜装备名｜技能名",
        "规则：装备、药品、鱼获进入背包并占格；碎银、素材、残卷、残页、随身饵剂也显示在背包，但占0格。",
        "商店：遇到【商人门】后，可按报价 /金庸买包、/金庸购买 装备名，也可 /金庸出售 装备名 [数量] 换碎银。",
    ]
    offer = player.get("merchant_offer") or {}
    if offer.get("offer_type") == "backpack" and int(offer.get("floor", -1)) == int(player["floor"]):
        lines.append(f"当前商人报价：「{offer['name']}」{offer['price']}两。发送 /金庸买包 确认购买。")
    equipment_offer = offer.get("equipment") or {}
    if equipment_offer and int(equipment_offer.get("floor", -1)) == int(player["floor"]):
        lines.append(f"商店装备：「{equipment_offer['name']}」{equipment_offer['price']}两，占{equipment_offer['slot_size']}格。发送 /金庸购买 {equipment_offer['name']}。")
    return "\n".join(lines)


def item_detail_text(name: str, player: dict[str, Any] | None = None) -> str:
    query = name.strip()
    if not query:
        return "用法：/金庸查看 物品名｜装备名｜技能名"

    equipment = EQUIPMENT_BY_NAME.get(query) or EQUIPMENT_BY_ID.get(query)
    if equipment:
        slot_labels = {"weapon": "武器", "armor": "防具", "accessory": "饰品"}
        owned = 0
        equipped = False
        if player is not None:
            owned = int(player.get("inventory", {}).get(equipment["item_id"], 0))
            equipped = str(equipment["item_id"]) in set(player.get("equipped", {}).values())
        lines = [
            f"【装备详情】{equipment['name']}",
            f"类型：{slot_labels.get(str(equipment['slot']), equipment['slot'])}｜品质：{equipment['rarity']}｜最早掉落：第{equipment['min_floor']}层",
            f"占格：{equipment['slot_size']}｜堆叠：{equipment['stack_size']}｜商店价：{_equipment_price(equipment)}两｜出售：{_equipment_sell_price(equipment)}两",
            f"效果：命中+{equipment['attack_bonus']}｜伤害+{equipment['damage_bonus']}｜AC+{equipment['ac_bonus']}｜HP上限+{equipment['max_hp_bonus']}",
            f"描述：{EQUIPMENT_DESC.get(equipment['name'], '暂无描述。')}",
        ]
        if player is not None:
            lines.append(f"拥有：{owned}｜当前装备：{'是' if equipped else '否'}")
        return "\n".join(lines)

    consumable = (
        FISH_CONSUMABLES_BY_NAME.get(query)
        or FISH_CONSUMABLES.get(query)
        or MEDICINE_CONSUMABLES_BY_NAME.get(query)
        or MEDICINE_CONSUMABLES.get(query)
    )
    if consumable:
        owned = int(player.get("inventory", {}).get(consumable["item_id"], 0)) if player is not None else 0
        effect = _consumable_effect_line(consumable)
        lines = [
            f"【物品详情】{consumable['name']}",
            f"类型：{'药品' if consumable['item_type'] == 'medicine_consumable' else '鱼获'}消耗品｜品质：{consumable['rarity']}｜占格：每{consumable['stack_size']}个占{consumable['slot_size']}格",
            f"效果：{effect}",
            f"持续：{consumable['duration']}",
            f"描述：{consumable['description']}",
        ]
        if player is not None:
            lines.append(f"拥有：{owned}")
        return "\n".join(lines)

    backpack = BACKPACKS_BY_NAME.get(query) or BACKPACKS.get(query)
    if backpack:
        current = player is not None and str(player.get("backpack_id", "")) == str(backpack["bag_id"])
        lines = [
            f"【背囊详情】{backpack['name']}",
            f"品质：{backpack['rarity']}｜容量：{backpack['capacity_slots']}格｜基础价格：{backpack['price']}两",
            f"描述：{backpack['description']}",
            "获得：只能在【商人门】遇到游商报价后，用 /金庸买包 购买下一档背囊。",
        ]
        if player is not None:
            lines.append(f"当前装备：{'是' if current else '否'}")
        return "\n".join(lines)

    skill = MARTIAL_ART_SKILLS_BY_NAME.get(query) or SKILL_COMBAT_BY_NAME.get(query)
    if skill:
        lines = [
            f"【技能详情】{skill['name']}",
            f"类型：{skill['category']}｜伤害属性：{skill['damage_type']}｜MP消耗：{skill['mp_cost']}",
            f"伤害：{skill['attack_segments']}段 × {skill['damage_dice_count']}d{skill['damage_die']}+{skill['damage_bonus']}",
        ]
        if "sect" in skill:
            lines.append(f"门派：{skill['sect']}｜品阶：{skill['tier']}｜关键属性：{ATTR_LABELS.get(str(skill['ability']), skill['ability'])}")
            lines.append(f"获取：第{skill['obtain_min_floor']}层后门派奇遇")
        if "damage_avg" in skill:
            lines.append(f"期望伤害：{skill['damage_avg']}｜范围：{skill['damage_min']}-{skill['damage_max']}")
        lines.append(f"描述：{skill.get('description') or _generated_skill_description(skill)}")
        return "\n".join(lines)

    status = next((row for row in STATUS_EFFECTS.values() if query in {str(row["name"]), str(row["status_id"])}), None)
    if status:
        return "\n".join([
            f"【状态详情】{status['name']}",
            f"持续：{status['duration_doors']}次进门｜DC修正：{status['dc_delta']}｜伤害骰：{status['damage_dice'] or '无'}",
            f"描述：{status['description']}",
        ])

    item_desc = ITEM_DESC.get(query)
    if item_desc:
        return "\n".join([f"【物品详情】{query}", f"描述：{item_desc}"])
    fragment_desc = _fragment_detail_text(query)
    if fragment_desc:
        return fragment_desc

    known = _known_detail_names(player)
    return "未找到该条目。可查看：" + "、".join(known[:24])


def _consumable_effect_line(item: dict[str, Any]) -> str:
    effect_type = str(item["effect_type"])
    amount = f"{item['effect_dice']}+{item['effect_value']}" if item["effect_dice"] else f"+{item['effect_value']}"
    labels = {
        "hp_recovery": "回复HP",
        "mp_recovery": "回复MP",
        "temp_hp": "获得临时HP",
        "next_d20_bonus": "下一次d20检定加值",
    }
    return f"{labels.get(effect_type, effect_type)} {amount}"


def _generated_skill_description(skill: dict[str, Any]) -> str:
    return f"{skill['category']}招式，造成{skill['attack_segments']}段{skill['damage_dice_count']}d{skill['damage_die']}+{skill['damage_bonus']}{skill['damage_type']}伤害。"


def _fragment_detail_text(name: str) -> str:
    if name.endswith("中阶武学残页"):
        return "\n".join([
            f"【物品详情】{name}",
            "类型：武学残页｜用途：门派奇遇奖励与武学领悟",
            f"描述：{ITEM_DESC['中阶武学残页']}",
        ])
    if name.endswith("顶级绝学残页"):
        return "\n".join([
            f"【物品详情】{name}",
            "类型：绝学残页｜用途：高层挑战与顶级武学线索",
            f"描述：{ITEM_DESC['顶级绝学残页']}",
        ])
    return ""


def _known_detail_names(player: dict[str, Any] | None = None) -> list[str]:
    names: list[str] = []
    if player is not None:
        for item_id in player.get("inventory", {}):
            row = _inventory_item_row(item_id)
            if row:
                names.append(str(row["name"]))
        for item_id in player.get("equipped", {}).values():
            row = EQUIPMENT_BY_ID.get(item_id)
            if row:
                names.append(str(row["name"]))
    names.extend(row["name"] for row in FISH_CONSUMABLES.values())
    names.extend(row["name"] for row in MEDICINE_CONSUMABLES.values())
    names.extend(row["name"] for row in EQUIPMENT_ROWS)
    names.extend(row["name"] for row in BACKPACKS.values())
    names.extend(row["name"] for row in MARTIAL_ART_SKILLS.values())
    names.extend(SKILL_COMBAT_BY_NAME.keys())
    deduped: list[str] = []
    for item in names:
        if item not in deduped:
            deduped.append(item)
    return deduped


def sect_list_text() -> str:
    grouped: dict[str, list[str]] = {}
    for sect in SECTS.values():
        grouped.setdefault(sect.camp, []).append(sect.name)
    lines = ["可选门派："]
    for camp, names in grouped.items():
        lines.append(f"{camp}：{'、'.join(names)}")
    return "\n".join(lines)


def opening_text(player: dict[str, Any], sect_name: str) -> str:
    """Display the grand opening scene with tower panoramic view."""
    sect = SECTS[sect_name]
    lines = [
        "【武道塔 · 缘起】",
        "",
        "　　大宋理宗年间，九州突现通天武神塔。",
        "",
        "　　古塔高七层，直插云霄，金光万道，瑞气千条，",
        "　　传闻登顶击败武神镜像，可获得武神传承，飞升上界。",
        "",
        "　　消息传开，天下震动！金庸原著十六大门派纷纷派遣弟子前来闯塔，",
        "　　一时间，江湖风云再起，各路英雄齐聚塔下。",
        "",
        "　　而你，正是" + sect_name + "派出的" + sect.camp + "弟子，",
        "　　身怀本门绝学，肩负着门派的荣耀与期望……",
        "",
        "═" * 35,
        "",
        f"【门派】{sect_name}（{sect.camp}）",
        f"【难度】{player['difficulty']}",
        f"【属性】{_ability_summary(player)}",
        f"【武学】{'、'.join(sect.skills)}",
        f"【气血】{player['hp']}/{player['max_hp']}",
        f"【内力】{player['mp']}/{player['max_mp']}",
        f"【防御】AC {_player_ac(player)}",
        f"【攻击】命中+{_player_attack_bonus(player)}｜装备伤害+{_equipment_bonus(player, 'damage_bonus')}",
        f"【装备】{_compact_equipment_text(player)}",
        f"【盘缠】{player['silver']}两",
        "",
        "═" * 35,
        "",
        "　　你站在通天武神塔下，仰望七层古塔直插云霄，",
        "　　塔门缓缓打开，一股沧桑古老的气息扑面而来……",
        "",
        "　　你的江湖，从此刻开始！",
        "",
        "发送 /金庸踢门 开启第1层第1个事件门。",
    ]
    return "\n".join(lines)


def _rpg_status_panel(player: dict[str, Any]) -> str:
    """Generate a compact RPG-style status panel."""
    # HP bar (18 characters wide)
    hp_ratio = player["hp"] / max(1, player["max_hp"])
    hp_fill = int(hp_ratio * 18)
    hp_bar = "█" * hp_fill + "░" * (18 - hp_fill)

    # MP bar
    mp_ratio = player["mp"] / max(1, player["max_mp"])
    mp_fill = int(mp_ratio * 18)
    mp_bar = "█" * mp_fill + "░" * (18 - mp_fill)

    # Door progress
    if "explored_doors" not in player or len(player["explored_doors"]) != DOORS_PER_FLOOR:
        player["explored_doors"] = [False] * DOORS_PER_FLOOR
    doors_done = sum(player["explored_doors"])

    lines = [
        "╔══════════════════════════════════════════════╗",
        f"║ 【{player.get('nickname', '侠客')}】门派：{player['sect']}｜第{player['floor']}层｜门 {doors_done}/{DOORS_PER_FLOOR}",
        "╠══════════════════════════════════════════════╣",
        f"║ HP {hp_bar} {player['hp']}/{player['max_hp']}｜MP {mp_bar} {player['mp']}/{player['max_mp']}",
        f"║ {_core_state_line(player)}",
        f"║ 资源：碎银 {player['silver']}两｜药品 {_medicine_text(player)}｜背囊 {inventory_used_slots(player)}/{_backpack_capacity(player)}格",
        f"║ 属性：{_ability_summary(player)}",
        f"║ 装备：{_compact_equipment_text(player)}",
        "╚══════════════════════════════════════════════╝",
    ]

    return "\n".join(lines)


def _floor_atmosphere(floor: int) -> str:
    """Generate atmospheric description for each floor."""
    atmospheres = {
        1: "青石铺就的古殿，空气中弥漫着淡淡的檀香，耳畔隐约传来悠扬的钟声……",
        2: "二层云雾缭绕，仙气氤氲，地上青苔斑驳，似有数百年无人踏足……",
        3: "三层罡风呼啸，殿壁上刻满了无名武学，每一道刻痕都透着凌厉的杀意……",
        4: "四层阴气森森，墙角泛着幽绿的光芒，空气中带着一丝铁锈般的腥味……",
        5: "五行之力在此层交汇，时而燥热时而冰寒，真气运转竟有凝滞之感……",
        6: "六层祥云缭绕，金光万道，威压如山，每走一步都需运足全身功力……",
    }
    return atmospheres.get(floor, "神秘的古殿深处，光影斑驳，不知藏着何等玄机……")


def _door_hints(player: dict[str, Any]) -> list[str]:
    """Generate subtle, non-obvious hints for each door."""
    # Ensure explored_doors exists
    if "explored_doors" not in player or len(player["explored_doors"]) != DOORS_PER_FLOOR:
        player["explored_doors"] = [False] * DOORS_PER_FLOOR

    seed = hash(player.get("user_id", "unknown") + str(player["floor"])) % 1000

    # Subtle hint pools - not obvious what they mean
    left_hints = [
        "门缝中透出淡淡的血色红光",
        "隐隐有金铁交鸣之声传出",
        "靠近时感到一股灼热的气息",
        "门板上布满了刀剑伤痕",
    ]
    middle_hints = [
        "有淡淡的药香从中飘出",
        "门缝中透着柔和的金光",
        "隐约能听到悠扬的钟声",
        "门框上刻着古老的铭文",
    ]
    right_hints = [
        "阵阵凉风从门内吹出",
        "里面似乎传来潺潺水声",
        "门上覆盖着厚厚的青苔",
        "空气中带着草木的清香",
    ]

    hints = []
    door_names = ["左殿", "中殿", "右殿"]
    hint_pools = [left_hints, middle_hints, right_hints]
    hint_seeds = [17, 31, 53]

    for i in range(DOORS_PER_FLOOR):
        if player["explored_doors"][i]:
            # Show explore option for opened doors
            extra_explore_key = f"extra_explored_{player['floor']}_{i+1}"
            if not player.get(extra_explore_key, False):
                hints.append(f"🔍 {door_names[i]}  →  【已探索，可再次搜寻】")
            else:
                hints.append(f"🏯 {door_names[i]}  →  【已探索】")
        else:
            hints.append(f"🚪 {door_names[i]}  →  {hint_pools[i][(seed + hint_seeds[i]) % len(hint_pools[i])]}")

    return hints


def _fishing_available(player: dict[str, Any]) -> bool:
    return str(player.get("floor", 1)) not in player.get("fished_floor_keys", [])


def _fishing_action_hint(player: dict[str, Any]) -> str:
    if _fishing_available(player):
        return "🎣 /金庸钓鱼 [饵剂] → 本层可垂钓一次；不填饵剂默认使用普通蚯蚓饵，不消耗任何东西"
    return "🎣 本层钓鱼已用 → 每层只能垂钓一次"


def floor_square_text(player: dict[str, Any]) -> str:
    """Display the current floor square with door selection (three halls style)."""
    if player.get("finished") or player.get("frozen"):
        return "【武道飞升】你已通关，肉身永寂，神魂不灭。"
    if player["floor"] >= MAX_FLOOR:
        return "\n".join([
            _rpg_status_panel(player),
            "",
            "【武神殿】武神镜像在殿中等待，唯有击败它方能证道飞升。",
            "",
            "═══ 龙池垂钓 ═══",
            "",
            "殿前龙池金光流转，本层仍可进行一次钓鱼。",
            "本层状态：" + ("可垂钓" if _fishing_available(player) else "已钓过，不可再次垂钓"),
            "未指定特殊饵剂时，默认使用普通蚯蚓饵，不消耗碎银或物品。",
            "",
            "═══ 可为之事 ═══",
            "",
            "🏮 /金庸踢门 → 挑战武神镜像",
            _fishing_action_hint(player),
            "📦 /金庸背包 → 查看随身行囊物品",
            "📊 /金庸状态 → 查看完整角色属性",
        ])

    # Check if all doors are done
    if "explored_doors" not in player or len(player["explored_doors"]) != DOORS_PER_FLOOR:
        player["explored_doors"] = [False] * DOORS_PER_FLOOR

    remaining = DOORS_PER_FLOOR - sum(player["explored_doors"])
    door_hints = _door_hints(player)

    lines = [
        _rpg_status_panel(player),
        "",
        f"【第{player['floor']}层 · 古武殿】",
        "",
        _floor_atmosphere(player["floor"]),
        "",
        "═══ 三道殿门 ═══",
        "",
    ]
    lines.extend(door_hints)
    lines.extend([
        "",
        "═══ 灵韵鱼池 ═══",
        "",
        "殿侧有一方古池，池水清澈见底，灵鱼游弋其中。",
        "据传池中之鱼蕴含天地灵气，食之可增益功力。",
        "本层状态：" + ("可垂钓" if _fishing_available(player) else "已钓过，不可再次垂钓"),
        "未指定特殊饵剂时，默认使用普通蚯蚓饵，不消耗碎银或物品。",
        "",
        "═══ 可为之事 ═══",
        "",
        "🏮 /金庸踢门 1/2/3 → 选择一道殿门进入",
        "🔍 /金庸探索 1/2/3 → 搜寻已探索的殿门",
        _fishing_action_hint(player),
        "📦 /金庸背包 → 查看随身行囊物品",
        "📊 /金庸状态 → 查看完整角色属性",
    ])

    if all(player["explored_doors"]):
        lines.append("")
        lines.append("⬆️ /金庸下一层 → 本层已通关，前往下一层！")

    return "\n".join(lines)


def command_hint_text(player: dict[str, Any] | None = None) -> str:
    if player is None:
        return "下一步可用：/金庸门派｜/金庸开局 门派 [普通|困难]｜/金庸帮助"

    if player.get("finished") or player.get("frozen"):
        commands = ["/金庸局外", "/金庸强化 强化名", "/金庸重置 confirm"]
    elif int(player.get("floor", 1)) >= MAX_FLOOR:
        commands = ["/金庸踢门", "/金庸钓鱼 [饵剂]" if _fishing_available(player) else "本层钓鱼已用", "/金庸状态", "/金庸技能 武学名|自动"]
    elif all(player.get("explored_doors", [False]*DOORS_PER_FLOOR)):
        commands = ["/金庸下一层", "/金庸踢门 1/2/3 再探索", "/金庸钓鱼 [饵剂]" if _fishing_available(player) else "本层钓鱼已用", "/金庸状态"]
    else:
        commands = ["/金庸踢门 1/2/3", "/金庸探索 1/2/3", "/金庸钓鱼 [饵剂]" if _fishing_available(player) else "本层钓鱼已用", "/金庸状态"]

    if player.get("merchant_offer"):
        commands.insert(0, "/金庸买包")
        if (player.get("merchant_offer") or {}).get("equipment"):
            commands.insert(0, "/金庸购买 装备名")
    if _has_current_merchant(player):
        commands.append("/金庸出售 装备名 [数量]")
    if player.get("pending_items"):
        commands.append("/金庸拾取 物品名 [数量]")
    if player.get("inventory"):
        commands.append("/金庸背包")

    deduped = list(dict.fromkeys(commands))
    return "下一步可用：" + "｜".join(deduped[:4])


def _door_scene_intro(player: dict[str, Any], door_num: int, event_type: str) -> str:
    door_names = ["左殿", "中殿", "右殿"]
    door_name = door_names[door_num - 1]
    hint = DOOR_TYPE_HINTS.get(event_type, {})
    title = hint.get("title", "门")
    subtitle = hint.get("subtitle", "未知因缘")
    flavor = hint.get("flavor", "门后气息难辨，像是武神塔故意遮住了天机。")
    floor = int(player.get("floor", 1))
    event_lines = {
        "battle": "殿心气机骤紧，一道身影拦在前方，血条与招式都将在本场战斗中明示结算。",
        "chest": EVENT_FLAVOR.get("chest_open", "门内宝光浮动，箱锁上似有暗纹游走。"),
        "encounter": EVENT_FLAVOR.get("encounter_wise", "门后有人影端坐，似在等一个有缘的闯塔者。"),
        "trap": EVENT_FLAVOR.get("trap_dodge", "脚下机括轻响，墙缝里寒光一闪。"),
        "merchant": EVENT_FLAVOR.get("merchant_greet", "门内算盘声清脆，江湖游商抬头看来。"),
    }
    return "\n".join([
        f"【踢门】第{floor}层｜{door_name}｜{title}·{subtitle}",
        f"这是一次武神塔游戏回合：你选择{door_name}，推开古铜门，门后事件已揭晓。",
        f"{flavor}",
        event_lines.get(event_type, ""),
        _flavor([
            "门轴轰然转动，尘灰被内劲卷成一线，殿中火光映出你的影子。",
            "青铜门钉在掌下微震，像有一股旧日江湖的杀伐气从缝隙里逼出来。",
            "你踏过门槛，脚下石砖浮现残破阵纹，刀光剑影仿佛在墙上重演。",
        ]),
    ])


def open_door(player: dict[str, Any], door_num: int = 0) -> str:
    """Open a specific door (1=left, 2=middle, 3=right). If door_num=0, pick next unopened."""
    if player.get("finished") or player.get("frozen"):
        return "该角色已通关飞升并冻结，请用 /金庸重置 confirm 开新档。"
    if player["floor"] == MAX_FLOOR:
        return boss_fight(player)

    # Initialize explored_doors array if not exists
    if "explored_doors" not in player or len(player["explored_doors"]) != DOORS_PER_FLOOR:
        player["explored_doors"] = [False] * DOORS_PER_FLOOR

    # If all doors are done
    if all(player["explored_doors"]):
        return "本层3道殿门已全部探索完毕。发送 /金庸下一层 继续攀登武道塔。"

    # Validate door number
    if door_num < 1 or door_num > DOORS_PER_FLOOR:
        # Find next unopened door
        for i in range(DOORS_PER_FLOOR):
            if not player["explored_doors"][i]:
                door_num = i + 1
                break
        if door_num == 0:
            return "本层已无可探索的殿门。"
    elif player["explored_doors"][door_num - 1]:
        return f"第{door_num}道殿门你已经探索过了。可以试试 /金庸探索 {door_num} 再次搜寻。"

    # Mark door as explored
    player["explored_doors"][door_num - 1] = True
    player["opened_doors"] = sum(player["explored_doors"])

    event_type = weighted_event()
    difficulty = DIFFICULTIES[player["difficulty"]]
    dc = 9 + player["floor"] + difficulty["base_dc"] - 10 + player.pop("next_door_dc_bonus", 0) + _status_dc_delta(player)
    status_line = _apply_status_damage(player)
    sect = SECTS[player["sect"]]
    result = check(player, sect.main_attr, max(8, dc), _event_check_bonus(player, event_type))

    # Store event type for this door (for flavor text)
    if "door_events" not in player:
        player["door_events"] = {}
    player["door_events"][f"{player['floor']}_{door_num}"] = event_type

    opening_line = _door_scene_intro(player, door_num, event_type) + "\n\n"

    if event_type == "battle":
        return opening_line + status_line + _battle(player, result)
    if event_type == "chest":
        return opening_line + status_line + _chest(player, result)
    if event_type == "encounter":
        return opening_line + status_line + _encounter(player, result)
    if event_type == "trap":
        return opening_line + status_line + _trap(player, result)
    return opening_line + status_line + _merchant(player, result)


def explore_door(player: dict[str, Any], door_num: int) -> str:
    """Explore an already-opened door for a chance to find extra rewards."""
    if door_num < 1 or door_num > DOORS_PER_FLOOR:
        return f"请选择要探索的殿门编号（1-{DOORS_PER_FLOOR}）。"

    # Check if door is opened
    if "explored_doors" not in player or not player["explored_doors"][door_num - 1]:
        door_names = ["左殿", "中殿", "右殿"]
        return f"{door_names[door_num - 1]}还未探索，先发送 /金庸踢门 {door_num} 进入吧。"

    # Check if already explored for extra rewards this floor
    explore_key = f"extra_explored_{player['floor']}_{door_num}"
    if player.get(explore_key, False):
        return "你已经仔细搜寻过此处了，暂时没有新发现。过段时间再来吧。"

    # Mark as explored
    player[explore_key] = True

    door_names = ["左殿", "中殿", "右殿"]
    door_name = door_names[door_num - 1]

    # Exploration roll - 30% chance to find something
    explore_roll = roll_d100()
    find_chance = 30

    lines = [
        f"【探索{door_name}】",
        "",
        f"你在{door_name}内仔细搜寻，翻查每一个角落……",
        "",
    ]

    if explore_roll <= find_chance:
        # Found something!
        reward_type = roll_die(4)
        if reward_type == 1:
            # Extra silver
            silver = 5 + player["floor"] * 3
            player["silver"] += silver
            lines.append(f"✨ 运气不错！你在墙角的暗格中发现了 {silver} 两碎银！")
        elif reward_type == 2:
            # Extra materials
            materials = 1 + player["floor"] // 2
            player["materials"] += materials
            lines.append(f"✨ 你在书架后的暗匣中发现了 {materials} 份珍贵的武学素材！")
        elif reward_type == 3:
            # Small HP recovery
            recovery = min(5, player["max_hp"] - player["hp"])
            player["hp"] += recovery
            lines.append(f"✨ 你在佛像后发现了几颗疗伤丹药，气血恢复了 {recovery} 点！")
        else:
            # Scroll/essence
            player["scrolls"] = player.get("scrolls", 0) + 1
            lines.append(f"✨ 你在石壁夹层中发现了一卷残破的武学残页！")
        lines.append("")
        lines.append("细致的探索果然没有白费！")
    else:
        # Nothing found
        lines.append("你搜遍了每一个角落，却什么也没发现……")
        lines.append("")
        lines.append("看来这里已经被前人搜刮干净了。")

    # Add return to square prompt
    lines.extend([
        "",
        "══════════════════════",
        "",
        "探索完毕，你回到了古殿中央。",
        "",
        "可为之事：",
        f"🏮 /金庸踢门 1/2/3 → 进入其他未探索的殿门",
        _fishing_action_hint(player),
        f"🔍 /金庸探索 1/2/3 → 探索已开启的殿门",
        f"📊 /金庸状态 → 查看当前角色状态",
    ])

    if all(player["explored_doors"]):
        lines.append(f"⬆️ /金庸下一层 → 继续攀登武道塔")

    return "\n".join(lines)


def _combat_status_panel(player: dict[str, Any]) -> str:
    """Generate a compact combat status panel showing both player and enemy."""
    combat = player["combat"]
    enemy_hp = combat["enemy_hp"]
    enemy_max_hp = combat["enemy_max_hp"]
    enemy_ac = combat["enemy_ac"]

    # Enemy HP bar
    enemy_hp_ratio = enemy_hp / max(1, enemy_max_hp)
    enemy_hp_fill = int(enemy_hp_ratio * 18)
    enemy_hp_bar = "█" * enemy_hp_fill + "░" * (18 - enemy_hp_fill)

    # Player HP bar
    hp_ratio = player["hp"] / max(1, player["max_hp"])
    hp_fill = int(hp_ratio * 18)
    hp_bar = "█" * hp_fill + "░" * (18 - hp_fill)

    # Player MP bar
    mp_ratio = player["mp"] / max(1, player["max_mp"])
    mp_fill = int(mp_ratio * 18)
    mp_bar = "█" * mp_fill + "░" * (18 - mp_fill)

    lines = [
        "╔═══════════════════════════════════════════════╗",
        f"║ 【第{combat['round']:2d}回合】              战斗中              ║",
        "╠═══════════════════════════════════════════════╣",
        f"║ ┌─ {combat['enemy_name'][:8]:8s} ───────────────────────────┐ ║",
        f"║ │ HP: {enemy_hp_bar} {enemy_hp:3d}/{enemy_max_hp:3d} │ ║",
        f"║ │ 防御: {enemy_ac}  攻击: +{combat['enemy_attack']}  伤害: {combat['enemy_damage'][:8]:8s} │ ║",
        "║ └─────────────────────────────────────────────┘ ║",
        "╠═══════════════════════════════════════════════╣",
        f"║ ┌─ {player.get('nickname', '侠客')}｜门派：{player['sect']} ─────────────┐ ║",
        f"║ │ HP: {hp_bar} {player['hp']:3d}/{player['max_hp']:3d} │ ║",
        f"║ │ MP: {mp_bar} {player['mp']:3d}/{player['max_mp']:3d} │ ║",
        f"║ │ {_core_state_line(player)[:42]:42s} │ ║",
        f"║ │ 属性：{_ability_summary(player)[:39]:39s} │ ║",
        f"║ │ 装备：{_compact_equipment_text(player)[:39]:39s} │ ║",
        f"║ │ 资源：碎银 {player['silver']}两｜药品 {_medicine_text(player)[:14]:14s} │ ║",
        "║ └─────────────────────────────────────────────┘ ║",
        "╚═══════════════════════════════════════════════╝",
    ]

    return "\n".join(lines)


def _battle(player: dict[str, Any], result: dict[str, Any]) -> str:
    """Start a turn-based combat encounter (DND style)."""
    rule = ENCOUNTER_RULES["battle"]
    difficulty_bonus = int(DIFFICULTIES[player["difficulty"]]["enemy_bonus"])
    enemy = choose_one(ENEMIES_BY_FLOOR.get(int(player["floor"]), ENEMIES_BY_FLOOR[1]))
    enemy_hp = int(enemy["hp"]) + difficulty_bonus
    enemy_ac = int(enemy["ac"]) + difficulty_bonus // 2
    enemy_attack = int(enemy["attack_bonus"]) + difficulty_bonus // 2
    enemy_damage = str(enemy["damage_dice"])

    # Roll initiative
    player_init = roll_d20() + attr_bonus(player, "dex")
    enemy_init = roll_d20()

    # Initialize combat state
    player["in_combat"] = True
    player["combat"] = {
        "enemy_id": str(enemy["enemy_id"]),
        "enemy_name": str(enemy["name"]),
        "enemy_hp": enemy_hp,
        "enemy_max_hp": enemy_hp,
        "enemy_ac": enemy_ac,
        "enemy_attack": enemy_attack,
        "enemy_damage": enemy_damage,
        "enemy_damage_type": str(enemy.get("damage_type", "")),
        "enemy_desc": str(enemy.get("desc", "")),
        "round": 1,
        "player_init": player_init,
        "enemy_init": enemy_init,
        "turn": "player" if player_init >= enemy_init else "enemy",
        "log": [],
        "battle_rule": rule,
    }

    # Build combat start message
    lines = [
        _combat_status_panel(player),
        "",
        f"敌人登场：{enemy['name']}｜HP {enemy_hp}｜AC {enemy_ac}｜攻击 +{enemy_attack}｜伤害 {enemy_damage} {enemy.get('damage_type', '')}",
        str(enemy.get("desc", "")),
        _flavor([
            "对方缓缓起身，衣袍无风自动，掌中劲气压得殿灯明灭不定。",
            "兵刃出鞘声在殿内回荡，你知道这不是旁白，这是本回合必须跨过去的敌人。",
            "石壁上的旧剑痕被气机牵动，仿佛整座武神塔都在等你出招。",
        ]),
        "",
        "═══ 先攻投掷 ═══",
        f"你身法：d20 + {attr_bonus(player, 'dex')} = {player_init}",
        f"敌身法：d20 = {enemy_init}",
        "",
    ]

    if player_init >= enemy_init:
        lines.extend([
            "⚡ 你身形更快，抢先出手！",
            "",
            "═══ 你的回合 ═══",
            "",
            "📜 可用行动：",
            "  /攻击 [技能名] → 运功出招",
            "  /逃跑 → 抽身而退",
            "  /技能 技能名 → 切换招式",
            "  /防御 → 抱元守一（防御+2）",
            "",
            f"可用招式：{'、'.join(_available_combat_skill_names(player))}",
        ])
    else:
        # Enemy goes first - run enemy turn immediately
        enemy_result = _enemy_turn(player)
        lines.extend([
            "⚔️ 敌人获得先手！",
            "",
            "═══ 敌人回合 ═══",
            "",
            enemy_result["log"],
        ])
        if enemy_result["combat_end"]:
            lines.extend([
                "",
                "═══ 战斗结束 ═══",
                "",
                _end_combat(player, enemy_result["victory"]),
            ])
        else:
            lines.extend([
                "",
                "═══ 你的回合 ═══",
                "",
                "可用行动：",
                "  /攻击 [技能名] → 使用技能攻击",
                "  /逃跑 → 尝试脱离战斗",
                "  /技能 技能名 → 切换当前技能",
                "  /防御 → 进入防御姿态（AC+2）",
                "",
                f"可用技能：{'、'.join(_available_combat_skill_names(player))}",
            ])

    return "\n".join(lines)


def _wuxia_attack_desc(skill: str, is_crit: bool, is_hit: bool, damage: int) -> str:
    """Generate wuxia-style attack description."""
    crit_descs = [
        "招式运至巅峰，力道竟有开山裂石之势！",
        "真气骤然迸发，这一击如雷霆万钧！",
        "招式突变，正中敌人要害！",
        "招式精妙绝伦，敌人避无可避！",
    ]
    hit_descs = [
        f"手中「{skill}」招式展开，一式击中！",
        f"真气运转，「{skill}」威力尽显！",
        f"身形一晃，「{skill}」已攻至敌人身前！",
        f"掌风/剑影呼啸，「{skill}」正中目标！",
    ]
    miss_descs = [
        "敌人身法灵动，侧身避开了这一击！",
        "招式虽猛，却被敌人以巧劲化开！",
        "敌人早有防备，纵身跃出了招式范围！",
        "差之毫厘！敌人堪堪避过这一击！",
    ]

    if is_crit:
        return choose_one(crit_descs)
    elif is_hit:
        return choose_one(hit_descs)
    else:
        return choose_one(miss_descs)


def _wuxia_enemy_attack_desc(is_crit: bool, is_hit: bool, damage: int) -> str:
    """Generate wuxia-style enemy attack description."""
    crit_descs = [
        "敌人招式突变，一击正中你的破绽！",
        "敌人发力陡然，这一击势大力沉！",
        "竟是致命一击！你避之不及！",
    ]
    hit_descs = [
        "敌人攻势凌厉，你躲闪不及！",
        "敌人招式狠辣，击中你的肩头/胸口！",
        "掌风/刀锋扫过，你闷哼一声！",
    ]
    miss_descs = [
        "你脚下步法展开，从容避开这一击！",
        "你真气护体，双掌相交将攻势卸去！",
        "你侧身避过，刀锋/掌风擦着衣襟而过！",
    ]

    if is_crit:
        return choose_one(crit_descs)
    elif is_hit:
        return choose_one(hit_descs)
    else:
        return choose_one(miss_descs)


def combat_attack(player: dict[str, Any], skill_name: str = "") -> str:
    """Player attack action in turn-based combat."""
    if not player.get("in_combat") or "combat" not in player:
        return "你当前不在战斗中。"

    combat = player["combat"]
    enemy_name = combat["enemy_name"]
    enemy_ac = combat["enemy_ac"]

    # Select skill
    if skill_name:
        if skill_name in _available_combat_skill_names(player) and _skill_combat_row(skill_name):
            skill = skill_name
        else:
            return f"「{skill_name}」不可用。可用技能：{'、'.join(_available_combat_skill_names(player))}"
    else:
        skill = _selected_combat_skill(player)

    # Attack roll
    attack_roll = roll_d20()
    attack_bonus = attr_bonus(player, SECTS[player["sect"]].main_attr) + _equipment_bonus(player, "attack_bonus") + _trait_value(player["sect"], "sword_attack_bonus")
    attack_total = attack_roll + attack_bonus
    is_crit = attack_roll == 20
    is_hit = is_crit or attack_total >= enemy_ac

    lines = [
        _combat_status_panel(player),
        "",
        _flavor([
            f"你沉肩吐纳，脚下踏出半步，使出「{skill}」。",
            f"你指尖真气一转，兵刃顺势递出，「{skill}」已然成势。",
            f"殿中尘灰被劲风卷起，你抓住敌人换息的一瞬，施展「{skill}」。",
        ]),
        f"（d20={attack_roll} + {attack_bonus} = {attack_total} ｜ 敌人防御 {enemy_ac}）",
        "",
    ]

    if is_hit:
        damage_result = _martial_damage_result(player, skill)
        damage = int(damage_result.get("total", 0)) + _equipment_bonus(player, "damage_bonus")
        if is_crit:
            damage *= 2  # Critical hit double damage

        combat["enemy_hp"] = max(0, combat["enemy_hp"] - damage)
        trait_line = _battle_trait_line(player, {"crit": is_crit}, {"total": damage})

        wuxia_desc = _wuxia_attack_desc(skill, is_crit, is_hit, damage)
        lines.append(wuxia_desc)
        if is_crit:
            lines.append(f"暴击！这一击打穿敌人架势，造成 {damage} 点伤害。{damage_result['line']}{trait_line}")
        else:
            lines.append(f"命中！劲力入体，造成 {damage} 点伤害。{damage_result['line']}{trait_line}")
        lines.append(f"敌人踉跄后退，气血剩余：{combat['enemy_hp']}/{combat['enemy_max_hp']}")

        # Check for victory
        if combat["enemy_hp"] <= 0:
            lines.extend([
                "",
                "🎉 只听敌人闷哼一声，颓然倒地！",
                "",
                "═══ 战斗结束 ═══",
                "",
                _end_combat(player, True),
            ])
            return "\n".join(lines)
    else:
        wuxia_desc = _wuxia_attack_desc(skill, False, False, 0)
        lines.append(wuxia_desc)
        lines.append("你的攻势擦着敌人衣角掠过，只在石地上留下一道浅痕。")

    # Enemy turn
    lines.extend([
        "",
        "═══ 敌人回合 ═══",
        "",
    ])

    enemy_result = _enemy_turn(player)
    lines.append(enemy_result["log"])

    if enemy_result["combat_end"]:
        lines.extend([
            "",
            "═══ 战斗结束 ═══",
            "",
            _end_combat(player, enemy_result["victory"]),
        ])
    else:
        combat["round"] += 1
        lines.extend([
            "",
            f"═══ 第{combat['round']}回合 · 你的回合 ═══",
            "",
            "📜 可用行动：",
            "  /攻击 [技能名] → 运功出招",
            "  /逃跑 → 抽身而退",
            "  /技能 技能名 → 切换招式",
            "  /防御 → 抱元守一（防御+2）",
            "",
            f"当前招式：{_selected_combat_skill(player)}",
        ])

    return "\n".join(lines)


def combat_flee(player: dict[str, Any]) -> str:
    """Player attempts to flee from combat."""
    if not player.get("in_combat") or "combat" not in player:
        return "你当前不在战斗中。"

    combat = player["combat"]

    # Flee check - Dex check DC 12
    flee_roll = roll_d20()
    flee_bonus = attr_bonus(player, "dex")
    flee_total = flee_roll + flee_bonus
    flee_dc = 12

    lines = [
        _combat_status_panel(player),
        "",
        "你尝试脱离战斗……",
        f"敏捷检定：d20={flee_roll} + {flee_bonus} = {flee_total} （DC {flee_dc}）",
        "",
    ]

    if flee_total >= flee_dc:
        lines.extend([
            "🏃 逃跑成功！你成功脱离了战斗。",
            "",
            "═══ 战斗结束 ═══",
            "",
            _end_combat(player, False, fled=True),
        ])
    else:
        lines.extend([
            "❌ 逃跑失败！敌人挡住了你的退路。",
            "",
            "═══ 敌人回合 ═══",
            "",
        ])

        enemy_result = _enemy_turn(player)
        lines.append(enemy_result["log"])

        if enemy_result["combat_end"]:
            lines.extend([
                "",
                "═══ 战斗结束 ═══",
                "",
                _end_combat(player, enemy_result["victory"]),
            ])
        else:
            combat["round"] += 1
            lines.extend([
                "",
                f"═══ 第{combat['round']}回合 · 你的回合 ═══",
                "",
                "可用行动：",
                "  /攻击 [技能名] → 使用技能攻击",
                "  /逃跑 → 尝试脱离战斗",
                "  /技能 技能名 → 切换当前技能",
                "  /防御 → 进入防御姿态（AC+2）",
                "",
                f"当前技能：{_selected_combat_skill(player)}",
            ])

    return "\n".join(lines)


def combat_defend(player: dict[str, Any]) -> str:
    """Player takes a defensive stance, gaining +2 AC until next turn."""
    if not player.get("in_combat") or "combat" not in player:
        return "你当前不在战斗中。"

    combat = player["combat"]
    combat["defending"] = True

    lines = [
        _combat_status_panel(player),
        "",
        "🛡️ 你摆出防御姿态，运转真气护住周身。",
        "直到下回合开始前，你的 AC +2。",
        "",
        "═══ 敌人回合 ═══",
        "",
    ]

    enemy_result = _enemy_turn(player)
    lines.append(enemy_result["log"])

    if enemy_result["combat_end"]:
        lines.extend([
            "",
            "═══ 战斗结束 ═══",
            "",
            _end_combat(player, enemy_result["victory"]),
        ])
    else:
        combat["round"] += 1
        lines.extend([
            "",
            f"═══ 第{combat['round']}回合 · 你的回合 ═══",
            "",
            "可用行动：",
            "  /攻击 [技能名] → 使用技能攻击",
            "  /逃跑 → 尝试脱离战斗",
            "  /技能 技能名 → 切换当前技能",
            "  /防御 → 进入防御姿态（AC+2）",
            "",
            f"当前技能：{_selected_combat_skill(player)}",
        ])

    return "\n".join(lines)


def _enemy_turn(player: dict[str, Any]) -> dict[str, Any]:
    """Execute enemy turn in combat."""
    combat = player["combat"]
    enemy_name = combat["enemy_name"]
    enemy_attack = combat["enemy_attack"]
    enemy_damage = combat["enemy_damage"]
    enemy_damage_type = combat.get("enemy_damage_type", "")
    player_ac = _player_ac(player)

    # Check for defense stance
    if combat.get("defending"):
        player_ac += 2
        combat["defending"] = False

    enemy_roll = roll_d20()
    enemy_total = enemy_roll + enemy_attack
    is_crit = enemy_roll == 20
    is_hit = is_crit or enemy_total >= player_ac

    if is_hit:
        raw_damage = roll_dice(enemy_damage)
        if is_crit:
            raw_damage *= 2
        actual = _apply_damage(player, raw_damage)

        wuxia_desc = _wuxia_enemy_attack_desc(is_crit, is_hit, actual)

        # Check for player defeat
        if player["hp"] <= 0:
            return {
                "victory": False,
                "combat_end": True,
                "log": f"{enemy_name}骤然抢入中宫！（d20={enemy_roll}+{enemy_attack}={enemy_total}｜你的AC {player_ac}｜伤害骰 {enemy_damage} {enemy_damage_type}）\n{wuxia_desc}\n你受到 {actual} 点伤害，气血翻涌，再也支撑不住，倒了下去……"
            }

        return {
            "victory": None,
            "combat_end": False,
            "log": f"{enemy_name}展开攻势，掌风贴着石壁呼啸而来。（d20={enemy_roll}+{enemy_attack}={enemy_total}｜你的AC {player_ac}｜伤害骰 {enemy_damage} {enemy_damage_type}）\n{wuxia_desc}\n你受到 {actual} 点伤害，当前气血：{player['hp']}/{player['max_hp']}。"
        }
    else:
        wuxia_desc = _wuxia_enemy_attack_desc(False, False, 0)
        return {
            "victory": None,
            "combat_end": False,
            "log": f"{enemy_name}虚晃一招后猛然出手。（d20={enemy_roll}+{enemy_attack}={enemy_total}｜你的AC {player_ac}｜伤害骰 {enemy_damage} {enemy_damage_type}）\n{wuxia_desc}\n这一击未能破开你的防守。"
        }


def _end_combat(player: dict[str, Any], victory: bool, fled: bool = False) -> str:
    """End combat and award rewards or handle defeat, then return to floor square."""
    combat = player.get("combat", {})
    rule = combat.get("battle_rule", ENCOUNTER_RULES["battle"])

    # Clear combat state
    player["in_combat"] = False
    player.pop("combat", None)

    lines = []

    if fled:
        silver = roll_dice(str(rule["fail_silver_dice"])) // 2
        player["silver"] += silver
        lines.extend([
            "你借着殿柱与烟尘遮住身形，纵身退回门外。",
            f"衣袖被劲风撕开一道口子，好在撤退途中摸到散落的碎银{silver}两。",
        ])
    elif victory:
        silver = roll_dice(str(rule["success_silver_dice"])) + player["floor"] * int(rule["success_silver_per_floor"])
        player["silver"] += silver
        player["materials"] += int(rule["success_materials"])
        lines.extend([
            "尘埃落下，殿中只余你的呼吸声与兵刃余响。",
            f"你从敌手遗落的腰囊中搜得碎银{silver}两，又取下一份可供研习的武学素材。",
            f"奖励：碎银+{silver}两｜武学素材+{rule['success_materials']}",
        ])
        drop_line = _maybe_equipment_drop(player, 35)
        if drop_line:
            lines.append(drop_line)
    else:
        # Player defeated
        silver = roll_dice(str(rule["fail_silver_dice"]))
        player["silver"] += silver
        lines.extend([
            "你被逼退到殿门边，胸口气血翻涌，眼前一阵发黑。",
            f"等你勉强站稳，地上只剩几枚散落的碎银。你拾起{silver}两，记下这次败招。",
        ])
        # Heal player to 1 HP to prevent permadeath
        player["hp"] = 1

    # Post combat recovery
    recovery_line = _post_combat_recovery(player)
    if recovery_line:
        lines.append(recovery_line)

    # Return to floor square with full RPG panel
    lines.extend([
        "",
        "════════════════════════════════════════════",
        "",
        "战斗结束，你回到了古殿中央。",
        "",
    ])
    lines.append(floor_square_text(player))

    return "\n".join(lines)


def _selected_combat_skill(player: dict[str, Any]) -> str:
    active = player.get("active_skill")
    available = _available_combat_skill_names(player)
    if active in available and _skill_combat_row(active):
        return str(active)
    usable = [skill for skill in available if _skill_combat_row(skill)]
    return choose_one(usable)


# Legacy function for boss fight (still auto-run for now)
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
        return f"\n战利品搜寻：d100={roll}，阈值≤{chance_percent}。你翻遍兵器架与敌手行囊，只找到些破损杂物。"
    candidates = [row for row in EQUIPMENT_ROWS if int(row["min_floor"]) <= int(player["floor"])]
    if not candidates:
        return ""
    item = choose_one(candidates)
    if _add_inventory_item(player, str(item["item_id"]), 1):
        return f"\n战利品搜寻：d100={roll}，阈值≤{chance_percent}。你在暗格中发现「{item['name']}」（{item['rarity']}），已收入背囊。"
    pending = player.setdefault("pending_items", {})
    pending[item["item_id"]] = int(pending.get(item["item_id"], 0)) + 1
    return f"\n战利品搜寻：d100={roll}，发现「{item['name']}」，但背囊已满。你先把它藏在殿角，已放入待拾取。"


def _return_to_floor_square(player: dict[str, Any]) -> str:
    """Helper to add return to floor square message after events."""
    lines = [
        "",
        "════════════════════════════════════════════",
        "",
        "探索完毕，你回到了古殿中央。",
        "",
    ]

    # Add the full floor square display (with RPG panel)
    lines.append(floor_square_text(player))

    return "\n".join(lines)


def _chest(player: dict[str, Any], result: dict[str, Any]) -> str:
    rule = ENCOUNTER_RULES["chest"]
    if result["fumble"]:
        dmg = roll_dice(str(rule["fumble_damage_dice"]))
        dmg = _apply_damage(player, dmg)
        event_line = (
            "【宝箱门】\n"
            "石台上的铜箱覆满尘灰，锁孔里隐约有机簧转动的细响。\n"
            f"你刚探手去拨，箱底暗弩骤然弹出。检定：d20=1，机关彻底失控。\n"
            f"你侧身已晚，被弩矢擦中，损失{dmg}HP；宝箱也在机关绞动中碎成一地铜片。"
        )
    else:
        silver = roll_dice(str(rule["success_silver_dice"])) + player["floor"] * int(rule["success_silver_per_floor"])
        player["silver"] += silver
        _add_medicine(player, int(rule["success_medicine"]))
        tier = "ultimate" if result["crit"] else "advanced"
        player["fragments"].append(_fragment_name(player["sect"], tier))
        drop_line = _maybe_equipment_drop(player, 45 if result["crit"] else 25)
        event_line = (
            "【宝箱门】\n"
            "你伏身听锁，指尖顺着铜箱纹路一点点摸过去，终于按住了机关的死门。\n"
            f"开箱检定：d20={result['die']} + {result['bonus']} = {result['total']}。\n"
            f"箱盖开启，一缕药香和旧纸气息扑面而来：碎银+{silver}两｜金疮药+{rule['success_medicine']}｜{player['fragments'][-1]}。\n"
            f"{drop_line}"
        )

    return event_line + _return_to_floor_square(player)


def _encounter(player: dict[str, Any], result: dict[str, Any]) -> str:
    rule = ENCOUNTER_RULES["encounter"]
    if result["success"]:
        player["materials"] += int(rule["success_materials"])
        mp_recovery = int(rule["success_mp_recovery"]) + _trait_value(player["sect"], "encounter_mp_recovery_bonus")
        player["mp"] = min(player["max_mp"], player["mp"] + mp_recovery)
        skill_line = _sect_encounter_skill_reward(player)
        event_line = (
            "【奇遇门】\n"
            "殿内没有敌人，只有一盏将熄未熄的青灯。灯旁老人抬眼看你，袖中竹简轻轻一敲。\n"
            f"悟性检定：d20={result['die']} + {result['bonus']} = {result['total']}。\n"
            f"你听得心神澄明，真气自行流转：武学素材+{rule['success_materials']}｜MP恢复{mp_recovery}。\n"
            f"{skill_line}"
        )
    else:
        event_line = (
            "【奇遇门】\n"
            "你在壁画前驻足良久，只觉画中招式似有深意，却始终差一线明悟。\n"
            f"检定：d20={result['die']} + {result['bonus']} = {result['total']}。\n"
            "这次机缘与你擦肩而过；你没有收获，却也没有惊动殿中禁制。"
        )

    return event_line + _return_to_floor_square(player)


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
        f"\n「{skill_name}」消耗{row['mp_cost']}MP，"
        f"{row['attack_segments']}段劲力次第爆发（{row['damage_dice_count']}d{row['damage_die']}+{row['damage_bonus']}），"
        f"每段伤害={segment_rolls}，{row['damage_type']}合计{base_total}{bonus_line}。"
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
        event_line = (
            "【陷阱门】\n"
            "地砖下传来轻微空响，你停步、俯身，用兵刃挑开了机关盖板。\n"
            f"拆解检定：d20={result['die']} + {result['bonus']} = {result['total']}。\n"
            f"你拆下几枚还能用的铜簧与暗扣，转手可换碎银{silver}两。"
        )
    else:
        dmg = roll_dice(str(rule["fail_damage_dice"]))
        dmg = _apply_damage(player, dmg)
        event_line = (
            "【陷阱门】\n"
            "你察觉脚下一沉，却只来得及护住要害。墙缝中喷出一阵腥甜毒雾。\n"
            f"检定失败：d20={result['die']} + {result['bonus']} = {result['total']}。\n"
            f"你强行冲出机关范围，损失{dmg}HP。{_apply_status(player, 'poison', 1)}"
        )

    return event_line + _return_to_floor_square(player)


def _merchant(player: dict[str, Any], result: dict[str, Any]) -> str:
    player["merchant_floor"] = player["floor"]
    rule = ENCOUNTER_RULES["merchant"]
    discount = int(rule["success_discount"]) if result["success"] else 0
    cost = max(int(rule["min_cost"]), int(rule["base_cost"]) - discount)
    bag_offer_line = _create_merchant_backpack_offer(player, result)
    equipment_offer_line = _create_merchant_equipment_offer(player, result)
    if player["silver"] >= cost:
        player["silver"] -= cost
        _add_medicine(player, int(rule["buy_medicine"]))
        event_line = (
            "【商人门】\n"
            "殿角挂着一盏小灯，灯下游商正慢条斯理地擦拭算盘。见你进门，他先看兵刃，再看钱袋。\n"
            f"交涉检定：d20={result['die']} + {result['bonus']} = {result['total']}。\n"
            f"一番讨价还价后，你花费{cost}两购得金疮药+{rule['buy_medicine']}。{bag_offer_line}{equipment_offer_line}"
        )
    else:
        event_line = (
            "【商人门】\n"
            "游商把药匣推到灯下，又把算盘珠拨得清脆作响。\n"
            f"报价{cost}两，可你摸了摸钱袋，碎银还差一截。{bag_offer_line}{equipment_offer_line}"
        )

    return event_line + _return_to_floor_square(player)


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


def _create_merchant_equipment_offer(player: dict[str, Any], result: dict[str, Any]) -> str:
    candidates = [row for row in EQUIPMENT_ROWS if int(row["min_floor"]) <= int(player["floor"])]
    if not candidates:
        return ""
    item = choose_one(candidates)
    rule = ENCOUNTER_RULES["merchant"]
    discount_percent = int(rule["backpack_discount_percent_success"]) if result["success"] else 0
    price = int(_equipment_price(item) * (100 - discount_percent) / 100)
    offer = player.setdefault("merchant_offer", {})
    offer["equipment"] = {
        "offer_type": "equipment",
        "item_id": item["item_id"],
        "name": item["name"],
        "price": price,
        "slot_size": item["slot_size"],
        "floor": player["floor"],
    }
    discount_line = f"，交涉成功折扣{discount_percent}%" if discount_percent else ""
    return f"\n他又从柜底取出「{item['name']}」：占{item['slot_size']}格，报价{price}两{discount_line}。发送 /金庸购买 {item['name']} 买下。"


def next_floor(player: dict[str, Any]) -> str:
    if player.get("finished") or player.get("frozen"):
        return "该角色已通关飞升并冻结，请重置后再开新周目。"
    if player["floor"] >= MAX_FLOOR:
        return "你已在武神殿。发送 /金庸踢门 挑战武神镜像。"

    # Initialize explored_doors array if not exists
    if "explored_doors" not in player or len(player["explored_doors"]) != DOORS_PER_FLOOR:
        player["explored_doors"] = [False] * DOORS_PER_FLOOR

    if not all(player["explored_doors"]):
        remaining = DOORS_PER_FLOOR - sum(player["explored_doors"])
        return f"本层还有 {remaining} 道殿门未探索。"

    # Reset floor state for new floor
    player["floor"] += 1
    player["explored_doors"] = [False] * DOORS_PER_FLOOR
    player["opened_doors"] = 0

    sect = SECTS[player["sect"]]
    dc = int(DIFFICULTIES[player["difficulty"]]["base_dc"])
    result = check(player, sect.main_attr, dc)
    lines = [
        "【本门奇遇】",
        "本层三殿皆已探尽，你在中央石台前盘膝片刻。石台上浮现出本门旧印，似在检验你的武道根基。",
        f"本门检定：d20={result['die']} + {result['bonus']} = {result['total']}，DC{dc}。",
    ]
    if result["crit"]:
        rule = SECT_ENCOUNTER_RULES["crit"]
        reward = _fragment_name(player["sect"], str(rule["fragment_tier"]))
        player["fragments"].append(reward)
        _add_medicine(player, int(rule["medicine_delta"]))
        player["materials"] += int(rule["materials_delta"])
        lines.append(f"自然20：旧印大亮，你从石台暗匣中取得{reward}，并获得金疮药+{rule['medicine_delta']}、素材+{rule['materials_delta']}。")
        skill_line = _sect_encounter_skill_reward(player)
        if skill_line:
            lines.append(skill_line.strip())
    elif result["success"]:
        rule = SECT_ENCOUNTER_RULES["success"]
        reward = _fragment_name(player["sect"], str(rule["fragment_tier"]))
        player["fragments"].append(reward)
        _add_medicine(player, int(rule["medicine_delta"]))
        player["materials"] += int(rule["materials_delta"])
        lines.append(f"成功：石台机关缓缓开启，你获得{reward}，并整理出金疮药+{rule['medicine_delta']}。")
        skill_line = _sect_encounter_skill_reward(player)
        if skill_line:
            lines.append(skill_line.strip())
    elif result["fumble"]:
        if _medicine_count(player) > 0:
            rule = SECT_ENCOUNTER_RULES["fumble_with_medicine"]
            lost = _remove_medicine(player, abs(int(rule["medicine_delta"])))
            lines.append(f"自然1：石台真气逆冲，你匆忙护住心脉，却撞碎随身金疮药{lost}份。")
        else:
            rule = SECT_ENCOUNTER_RULES["fumble_without_medicine"]
            player["next_door_dc_bonus"] = int(rule["next_door_dc_delta"])
            lines.append(f"自然1：旧印黯淡，殿中机关被你误触；下次进门首次检定DC+{rule['next_door_dc_delta']}。")
    else:
        lines.append("失败：石台上的纹路亮起又熄灭，这次没有回应你的内息。")

    player["floor"] += 1
    player["opened_doors"] = 0
    player["merchant_offer"] = {}
    if player["floor"] == MAX_FLOOR:
        lines.append("石阶尽头传来沉闷钟鸣，第7层武神殿已解锁。发送 /金庸踢门 挑战唯一BOSS武神镜像。")
    else:
        lines.append(f"你收束气息，沿石阶继续上行，进入第{player['floor']}层。")
    return "\n".join(lines)


def boss_fight(player: dict[str, Any]) -> str:
    sect = SECTS[player["sect"]]
    boss = BOSSES["wushen_mirror"]
    difficulty_bonus = int(DIFFICULTIES[player["difficulty"]]["enemy_bonus"])
    boss_attack = int(boss["attack_bonus"]) + difficulty_bonus // 2
    boss_damage = str(boss["damage_dice"])
    intro = check(player, sect.main_attr, int(boss["check_dc"]) + difficulty_bonus // 2)
    combat = _run_turn_combat(
        player,
        str(boss["name"]),
        int(boss["hp"]),
        int(boss["ac"]),
        boss_attack,
        boss_damage,
        max_rounds=8,
    )
    boss_panel = (
        f"【武神殿】{boss['name']}｜HP {boss['hp']}｜AC {boss['ac']}｜攻击 +{boss_attack}｜伤害 {boss_damage} {boss.get('damage_type', '')}\n"
        f"{boss.get('desc', '')}\n"
        "殿顶星图旋转，四壁浮现你一路击败过的招式残影；这是本局最终 Boss 战，所有数值公开结算。"
    )
    if not combat["victory"]:
        return (
            f"{boss_panel}\n"
            f"入殿检定：d20={intro['die']} + {intro['bonus']} = {intro['total']}。\n"
            f"{combat['log']}\n"
            f"挑战未竟，服药调息后可再次 /金庸踢门。"
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
        f"{boss_panel}\n"
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
        return f"【钓鱼】第{player['floor']}层已钓过鱼，本层钓鱼不可用了。每层只能进行一次钓鱼。"

    carried = player.setdefault("carried_baits", {})
    bait_id = str(bait["bait_id"])
    used_carried_bait = int(carried.get(bait_id, 0)) > 0
    is_default_bait = bait_id == "worm"
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

    event_line = (
        f"【钓鱼】第{player['floor']}层｜{pool['name']}\n"
        f"你在殿侧古池边坐下，将「{bait_name}」挂上鱼钩。水面初时平静，片刻后忽有灵光在池底一闪。\n"
        f"消耗：{'随身饵剂×1' if used_carried_bait else ('无；默认基础鱼饵不消耗任何东西' if is_default_bait else '无；未携带随身饵剂时也不扣碎银')}\n"
        f"鱼池品质：{pool['tier']}｜鱼池修正+{pool['loot_roll_bonus']}｜钓饵修正+{bait['loot_roll_bonus']}｜局外修正+{meta_quality_bonus}｜优势骰数{roll_count}\n"
        f"鱼获判定：d100={raw_rolls}，取{base_roll}，品质修正后={final_roll}\n"
        f"鱼线猛地一沉，你稳住竿身，将{item['name']}×{quantity}拖出水面。\n"
        f"鱼获：{item['rarity']}｜{item['description']}\n"
        f"{storage_line}"
    )

    return event_line + _return_to_floor_square(player)


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
        return "未知消耗品。当前背囊：" + _inventory_item_text(player)
    if item.get("item_type") not in {"fish_consumable", "medicine_consumable"}:
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
    if item.get("item_type") == "medicine_consumable":
        action = "你撕开药包，将金疮药敷在伤处" if item["item_id"] == "jinchuang_ointment" else "你取出药瓶，倒出丹丸含入口中"
    else:
        action = "你处理好鱼获，就地食用其中蕴含的灵气"
    if effect_type == "hp_recovery":
        before = player["hp"]
        player["hp"] = min(player["max_hp"], player["hp"] + amount)
        recovered = player["hp"] - before
        return f"【使用消耗品】{item['name']}\n{action}。暖意沿经脉散开，伤口渐渐止痛。\n效果：回复HP {recovered}点｜当前HP {player['hp']}/{player['max_hp']}"
    if effect_type == "mp_recovery":
        before = player["mp"]
        player["mp"] = min(player["max_mp"], player["mp"] + amount)
        recovered = player["mp"] - before
        return f"【使用消耗品】{item['name']}\n{action}。一股清灵之气沉入丹田，内息重新变得绵长。\n效果：回复MP {recovered}点｜当前MP {player['mp']}/{player['max_mp']}"
    if effect_type == "temp_hp":
        player["temp_hp"] = max(int(player.get("temp_hp", 0)), amount)
        return f"【使用消耗品】{item['name']}\n{action}。寒潭灵气在体表凝成一层若有若无的护劲。\n效果：获得临时HP {player['temp_hp']}点，持续到下一场战斗。"
    if effect_type == "next_d20_bonus":
        player["next_check_bonus"] = int(player.get("next_check_bonus", 0)) + int(item["effect_value"])
        return f"【使用消耗品】{item['name']}\n{action}。骨节微热，心神也随之沉稳下来。\n效果：下一次d20检定+{item['effect_value']}。"
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


def buy_merchant_equipment(player: dict[str, Any], item_name: str = "") -> str:
    _ensure_inventory(player)
    offer = (player.get("merchant_offer") or {}).get("equipment") or {}
    if not offer or int(offer.get("floor", -1)) != int(player["floor"]):
        return "当前没有商人装备报价。需要在踢门遇到【商人门】后，按商人报价使用 /金庸购买 装备名。"
    item = EQUIPMENT_BY_ID.get(str(offer.get("item_id", "")))
    if item is None:
        player.setdefault("merchant_offer", {}).pop("equipment", None)
        return "当前商人装备报价已失效。"
    if item_name and item_name not in {str(item["name"]), str(item["item_id"])}:
        return f"当前商人只出售「{item['name']}」。发送 /金庸购买 {item['name']} 确认购买。"
    price = int(offer["price"])
    if player["silver"] < price:
        return f"碎银不足，购买「{item['name']}」需要{price}两，当前{player['silver']}两。"
    if not _can_add_inventory_item(player, str(item["item_id"]), 1):
        return f"背囊剩余{_inventory_free_slots(player)}格不足，无法购买「{item['name']}」（占{item['slot_size']}格）。可先 /金庸出售 装备名 或 /金庸丢弃 物品名 腾出空间。"
    player["silver"] -= price
    _add_inventory_item(player, str(item["item_id"]), 1)
    player.setdefault("merchant_offer", {}).pop("equipment", None)
    return (
        f"你付给游商{price}两，买下「{item['name']}」。他用旧布裹好兵器递来，叮嘱你江湖路险，莫让好物蒙尘。\n"
        f"已收入背囊：占{item['slot_size']}格｜当前容量 {inventory_used_slots(player)}/{_backpack_capacity(player)}格。"
    )


def sell_equipment(player: dict[str, Any], item_name: str, quantity: int = 1) -> str:
    _ensure_inventory(player)
    if not _has_current_merchant(player):
        return "当前没有商人在场，不能出售装备。需要在踢门遇到【商人门】后，再使用 /金庸出售 装备名 [数量]。"
    item = EQUIPMENT_BY_NAME.get(item_name) or EQUIPMENT_BY_ID.get(item_name)
    if item is None:
        return "只能出售装备。当前装备物品：" + _inventory_item_text(player)
    quantity = max(1, quantity)
    item_id = str(item["item_id"])
    inventory = player.setdefault("inventory", {})
    owned = int(inventory.get(item_id, 0))
    equipped = _equipped_count(player, item_id)
    sellable = max(0, owned - equipped)
    if sellable <= 0:
        if equipped > 0:
            return f"「{item['name']}」正在装备中，不能直接出售。请先换下该部位装备，或出售背包中未装备的同名装备。"
        return f"你没有可出售的「{item['name']}」。"
    amount = min(quantity, sellable)
    price_each = _equipment_sell_price(item)
    total = price_each * amount
    left = owned - amount
    if left > 0:
        inventory[item_id] = left
    else:
        inventory.pop(item_id, None)
    player["silver"] += total
    return (
        f"你将「{item['name']}」×{amount}摆到柜上，游商验过刃口与成色，数出碎银{total}两。\n"
        f"单价：{price_each}两｜当前碎银 {player['silver']}两｜背囊容量 {inventory_used_slots(player)}/{_backpack_capacity(player)}格。"
    )


def buy_backpack(player: dict[str, Any], backpack_name: str = "") -> str:
    _ensure_inventory(player)
    offer = player.get("merchant_offer") or {}
    if offer.get("offer_type") != "backpack" or int(offer.get("floor", -1)) != int(player["floor"]):
        return "当前没有商人背囊报价。需要在踢门遇到【商人门】后，按商人报价使用 /金庸买包。"
    target = BACKPACKS.get(str(offer.get("bag_id", "")))
    if target is None:
        equipment_offer = offer.get("equipment")
        player["merchant_offer"] = {"equipment": equipment_offer} if equipment_offer else {}
        return "当前商人背囊报价已失效。"
    if backpack_name and backpack_name not in {str(target["name"]), str(target["bag_id"])}:
        return f"当前商人只出售「{target['name']}」。发送 /金庸买包 确认购买。"
    current = _backpack_row(player)
    if int(target["capacity_slots"]) <= int(current["capacity_slots"]):
        equipment_offer = offer.get("equipment")
        player["merchant_offer"] = {"equipment": equipment_offer} if equipment_offer else {}
        return f"当前已装备「{current['name']}」{current['capacity_slots']}格，不能降级或重复购买。"
    price = int(offer["price"])
    if player["silver"] < price:
        return f"碎银不足，购买「{target['name']}」需要{price}两，当前{player['silver']}两。"
    player["silver"] -= price
    player["backpack_id"] = str(target["bag_id"])
    equipment_offer = offer.get("equipment")
    player["merchant_offer"] = {"equipment": equipment_offer} if equipment_offer else {}
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
        "/金庸钓鱼 [饵剂]：每层一次，默认普通蚯蚓饵，不消耗碎银\n"
        "/金庸背包：查看背囊容量、物品、待拾取与占格规则\n"
        "/金庸装备 装备名：装备武器、防具或饰品\n"
        "/金庸技能 武学名|自动：设置战斗优先使用的武学\n"
        "/金庸买包：遇到商人门后，购买当前商人报价的背囊\n"
        "/金庸购买 装备名：遇到商人门后，购买当前商人报价的装备\n"
        "/金庸出售 装备名 [数量]：在商店出售未装备的背包装备换碎银\n"
        "/金庸局外：查看局外强化等级与下一阶消耗\n"
        "/金庸强化 钓鱼|背囊|盘缠|气血：消耗通关后的局外点数提升局外属性\n"
        "/金庸丢弃 物品名 [数量]：丢弃背包物品\n"
        "/金庸拾取 物品名 [数量]：拾取因容量不足暂存的物品\n"
        "/金庸使用 药品名|鱼获名：使用药品或鱼获消耗品\n"
        "/金庸重置 confirm：删除当前角色档案\n"
        "兼容旧指令：以上命令也可继续使用 /jy 前缀。\n"
        f"鱼池：{'、'.join(row['name'] for row in FISHING_POOLS.values())}\n"
        f"饵剂：{'、'.join(BAITS)}"
    )


def format_attrs(sect_name: str) -> str:
    sect = SECTS[sect_name]
    return "、".join(f"{ATTR_LABELS[k]}+{v}" for k, v in sect.attrs.items())
