from __future__ import annotations

import random
from math import ceil
from typing import Any

from .game_data import (
    ATTR_LABELS,
    ATTRIBUTE_UP_INTERVAL,
    ATTRIBUTE_UP_VALUE,
    BAITS,
    BACKPACKS,
    BACKPACKS_BY_NAME,
    BOSSES,
    BOSS_CLEAR_REWARDS,
    DIFFICULTIES,
    DOOR_TYPE_HINTS,
    ENCOUNTER_RULES,
    ENEMIES_BY_FLOOR,
    ENEMY_XP_BY_FLOOR,
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
    LEGENDARY_MARTIAL_ART_SKILLS,
    LEVEL_UP_BONUS,
    LEVEL_UP_XP,
    MARTIAL_ART_EFFECTS,
    MARTIAL_ART_SKILLS,
    MARTIAL_ART_SKILLS_BY_NAME,
    MAX_LEVEL,
    MEDICINE_CONSUMABLES,
    MEDICINE_CONSUMABLES_BY_NAME,
    META_UPGRADE_ALIASES,
    META_UPGRADE_ORDER,
    META_UPGRADES,
    PLAYER_START,
    SECT_ENCOUNTER_RULES,
    SECT_FLOOR_RECOVERY_RULES,
    SECTS,
    SKILL_COMBAT_BY_NAME,
    STATUS_EFFECTS,
)


MAX_FLOOR = 7
DOORS_PER_FLOOR = 3
EXPLORE_FIND_CHANCE = 33
COMBAT_BASE_HIT_BONUS = 1
COMBAT_MISS_STREAK_BONUS_STEP = 2
COMBAT_MISS_STREAK_BONUS_CAP = 6
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
CONSUMABLE_PRICE_BY_RARITY = {
    "common": 12,
    "uncommon": 24,
    "rare": 50,
    "epic": 90,
    "legendary": 160,
}
CONSUMABLE_SELL_RATE_PERCENT = 50
MARTIAL_LEARN_COSTS = {
    "进阶": {"fragment_tier": "advanced", "fragments": 1, "materials": 3},
    "顶级": {"fragment_tier": "ultimate", "fragments": 1, "materials": 8},
}
MARTIAL_FRAGMENT_COMPOSE_RATE = 4


def new_player(user_id: str, nickname: str, sect_name: str, difficulty: str, meta_progression: dict[str, Any] | None = None) -> dict[str, Any]:
    sect = SECTS[sect_name]
    meta = normalize_meta_progression(meta_progression)
    fishing_meta = _meta_upgrade_row(meta, "fishing_preparation")
    revive_cap = _meta_value(meta, "revive_elixir_carry", "revive_elixir_cap")
    revive_target = max(0, min(3, int(meta.get("revive_elixir_target", 1))))
    carried_revive_elixirs = min(int(meta.get("elixirs", 0)), revive_cap, revive_target)
    meta["elixirs"] = max(0, int(meta.get("elixirs", 0)) - carried_revive_elixirs)
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
        "level": 1,
        "xp": 0,
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
        "elixirs": 0,
        "revive_elixirs": carried_revive_elixirs,
        "fragments": [],
        "martial_fragments": {"advanced": 0, "ultimate": 0},
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
        "merchant_miss_floor_streak": 0,
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


def _combat_miss_streak_bonus(miss_streak: int) -> int:
    return min(COMBAT_MISS_STREAK_BONUS_CAP, max(0, miss_streak) * COMBAT_MISS_STREAK_BONUS_STEP)


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


# === 经验升级系统 ===
def get_current_level(xp: int) -> int:
    """根据经验值计算当前等级"""
    for level in range(MAX_LEVEL, 0, -1):
        if xp >= LEVEL_UP_XP[level]:
            return level
    return 1


def get_xp_for_next_level(current_level: int) -> int:
    """获取下一级所需的经验值"""
    if current_level >= MAX_LEVEL:
        return 0
    return LEVEL_UP_XP[current_level + 1]


def get_xp_progress(player: dict[str, Any]) -> tuple[int, int]:
    """获取当前经验进度：(当前经验, 下一级所需经验)"""
    level = player.get("level", 1)
    current_xp = player.get("xp", 0)
    if level >= MAX_LEVEL:
        return (current_xp, 0)
    next_xp = LEVEL_UP_XP[level + 1]
    return (current_xp, next_xp)


def _apply_level_up(player: dict[str, Any], old_level: int, new_level: int) -> list[str]:
    """应用升级带来的属性加成，返回升级描述列表"""
    sect = SECTS[player["sect"]]
    main_attr = sect.main_attr
    messages = []

    for level in range(old_level + 1, new_level + 1):
        level_msgs = [f"【等级提升】Lv{level - 1} → Lv{level}"]

        # HP 提升
        hp_gain = LEVEL_UP_BONUS["hp_base"] + sect.attrs.get("con", 0) * LEVEL_UP_BONUS["hp_con_multi"]
        player["max_hp"] += hp_gain
        player["hp"] += hp_gain
        level_msgs.append(f"气血上限 +{hp_gain}")

        # MP 提升
        mp_gain = LEVEL_UP_BONUS["mp_base"] + sect.attrs.get("int", 0) * LEVEL_UP_BONUS["mp_int_multi"]
        player["max_mp"] += mp_gain
        player["mp"] += mp_gain
        level_msgs.append(f"内力上限 +{mp_gain}")

        # 每2级提升主要属性
        if level % ATTRIBUTE_UP_INTERVAL == 0:
            # 这里只记录，实际门派属性是固定的
            # 未来可以实现每级属性点分配系统
            attr_name = ATTR_LABELS.get(main_attr, main_attr)
            level_msgs.append(f"{attr_name}感悟加深 (隐藏加成已生效)")

        messages.append("｜".join(level_msgs))

    player["level"] = new_level
    return messages


def add_xp(player: dict[str, Any], xp_amount: int, enemy_name: str = "") -> tuple[bool, list[str]]:
    """
    添加经验值，检查是否升级
    返回：(是否升级, 消息列表)
    """
    old_level = player.get("level", 1)
    old_xp = player.get("xp", 0)
    new_xp = old_xp + xp_amount
    player["xp"] = new_xp

    messages = []
    if enemy_name:
        messages.append(f"击败「{enemy_name}」，获得经验值 +{xp_amount}")
    else:
        messages.append(f"获得经验值 +{xp_amount}")

    new_level = get_current_level(new_xp)
    leveled_up = new_level > old_level

    if leveled_up:
        level_up_msgs = _apply_level_up(player, old_level, new_level)
        messages.extend(level_up_msgs)

    # 显示进度
    if new_level < MAX_LEVEL:
        next_xp = LEVEL_UP_XP[new_level + 1]
        progress_pct = int((new_xp - LEVEL_UP_XP[new_level]) / (next_xp - LEVEL_UP_XP[new_level]) * 100)
        messages.append(f"Lv{new_level} 进度: {new_xp}/{next_xp} XP ({progress_pct}%)")
    else:
        messages.append(f"已达最高等级 Lv{MAX_LEVEL}！")

    return (leveled_up, messages)


def _room_completion_xp(player: dict[str, Any], multiplier: int = 1) -> int:
    floor = int(player.get("floor", 1))
    base = max(10, int(ENEMY_XP_BY_FLOOR.get(floor, 50) * 0.2))
    return base * max(1, multiplier)


def _award_room_completion_xp(player: dict[str, Any], multiplier: int = 1, label: str = "房间完成") -> list[str]:
    xp_amount = _room_completion_xp(player, multiplier)
    _, messages = add_xp(player, xp_amount)
    if messages:
        messages[0] = f"{label}，获得经验值 +{xp_amount}"
    return messages


def _as_str_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value if str(item)]
    if isinstance(value, tuple) or isinstance(value, set):
        return [str(item) for item in value if str(item)]
    return []


def _as_int_dict(value: Any) -> dict[str, int]:
    if not isinstance(value, dict):
        return {}
    return {str(key): max(0, int(val)) for key, val in value.items()}


def normalize_meta_progression(meta_progression: dict[str, Any] | None) -> dict[str, Any]:
    meta_progression = meta_progression if isinstance(meta_progression, dict) else {}
    meta = {
        "essence": max(0, int(meta_progression.get("essence", 0))),
        "elixirs": max(0, int(meta_progression.get("elixirs", 0))),
        "clears": max(0, int(meta_progression.get("clears", 0))),
        "revive_elixir_target": max(
            0,
            min(3, int(meta_progression.get("revive_elixir_target", meta_progression.get("carry_revive_elixir", 1)))),
        ),
        "unlocked_sect_ultimates": sorted(set(_as_str_list(meta_progression.get("unlocked_sect_ultimates")))),
        "unlocked_legendary_ultimates": sorted(set(_as_str_list(meta_progression.get("unlocked_legendary_ultimates")))),
        "hard_clear_sects": sorted(set(_as_str_list(meta_progression.get("hard_clear_sects")))),
        "sect_advanced_fragments": _as_int_dict(meta_progression.get("sect_advanced_fragments")),
        "sect_ultimate_fragments": _as_int_dict(meta_progression.get("sect_ultimate_fragments")),
        "legendary_fragments": max(0, int(meta_progression.get("legendary_fragments", 0))),
    }
    for upgrade_id in META_UPGRADE_ORDER:
        max_level = max(META_UPGRADES[upgrade_id])
        meta[upgrade_id] = max(0, min(max_level, int(meta_progression.get(upgrade_id, 0))))
    return meta


def merge_meta_progression(stored_meta: dict[str, Any] | None, player_meta: dict[str, Any] | None = None) -> dict[str, Any]:
    stored = normalize_meta_progression(stored_meta)
    player = normalize_meta_progression(player_meta)
    merged = normalize_meta_progression(stored)
    for key in ("essence", "elixirs", "clears", "revive_elixir_target"):
        merged[key] = max(int(stored.get(key, 0)), int(player.get(key, 0)))
    for upgrade_id in META_UPGRADE_ORDER:
        merged[upgrade_id] = max(int(stored.get(upgrade_id, 0)), int(player.get(upgrade_id, 0)))
    merged["unlocked_sect_ultimates"] = sorted(set(stored.get("unlocked_sect_ultimates", [])) | set(player.get("unlocked_sect_ultimates", [])))
    merged["unlocked_legendary_ultimates"] = sorted(set(stored.get("unlocked_legendary_ultimates", [])) | set(player.get("unlocked_legendary_ultimates", [])))
    merged["hard_clear_sects"] = sorted(set(stored.get("hard_clear_sects", [])) | set(player.get("hard_clear_sects", [])))
    for fragment_key in ("sect_advanced_fragments", "sect_ultimate_fragments"):
        stored_has_key = isinstance(stored_meta, dict) and fragment_key in stored_meta
        merged[fragment_key] = _as_int_dict(stored.get(fragment_key) if stored_has_key else player.get(fragment_key))
    stored_has_legendary = isinstance(stored_meta, dict) and "legendary_fragments" in stored_meta
    merged["legendary_fragments"] = int((stored if stored_has_legendary else player).get("legendary_fragments", 0))
    return merged


def difficulty_gate_text(sect_name: str, difficulty: str, meta_progression: dict[str, Any] | None) -> str:
    if difficulty != "炼狱":
        return ""
    meta = normalize_meta_progression(meta_progression)
    if sect_name in set(meta.get("hard_clear_sects", [])):
        return ""
    return f"「{sect_name}」尚未困难通关，不能选择炼狱难度。先用 /金庸开局 {sect_name} 困难 通关后解锁该门派炼狱。"


def _meta_upgrade_row(meta_progression: dict[str, Any], upgrade_id: str) -> dict[str, Any]:
    meta = normalize_meta_progression(meta_progression)
    return META_UPGRADES[upgrade_id][int(meta.get(upgrade_id, 0))]


def _meta_value(meta_progression: dict[str, Any], upgrade_id: str, key: str) -> int:
    return int(_meta_upgrade_row(meta_progression, upgrade_id).get(key, 0))


def _meta_ultimate_skill_summary(row: dict[str, Any] | None) -> str:
    if not row:
        return ""
    mp_text = f"MP{row['mp_cost']}" if int(row["mp_cost"]) > 0 else "免费"
    return (
        f"{row['tier']}·{row['category']}·{row['damage_type']}｜{mp_text}｜"
        f"{row['attack_segments']}段×{row['damage_dice_count']}d{row['damage_die']}+{row['damage_bonus']}｜"
        f"{row['description']}"
    )


def meta_text(meta_progression: dict[str, Any] | None, player: dict[str, Any] | None = None) -> str:
    meta = normalize_meta_progression(meta_progression)
    advanced_fragment_stock = _as_int_dict(meta.get("sect_advanced_fragments"))
    sect_fragment_stock = _as_int_dict(meta.get("sect_ultimate_fragments"))
    hard_clear_sects = list(meta.get("hard_clear_sects", []))
    lines = [
        "【局外强化】",
        f"当前武道真髓×{meta.get('essence', 0)}",
        f"局外资源：小还丹×{meta.get('elixirs', 0)}、通关次数×{meta.get('clears', 0)}",
        f"绝学残页库存：传说残页×{meta.get('legendary_fragments', 0)}｜门派中阶残页："
        + ("、".join(f"{sect}×{count}" for sect, count in advanced_fragment_stock.items() if count > 0) or "暂无"),
        "门派顶级残页："
        + ("、".join(f"{sect}×{count}" for sect, count in sect_fragment_stock.items() if count > 0) or "暂无"),
        "已解锁炼狱门派：" + ("、".join(hard_clear_sects) if hard_clear_sects else "暂无"),
        f"小还丹携带目标×{meta.get('revive_elixir_target', 1)}｜当前升级上限×{_meta_value(meta, 'revive_elixir_carry', 'revive_elixir_cap')}",
        "说明：开局实际带入数量 = 局外库存、携带目标、升级上限三者取最小；本局死亡时自动消耗1颗并半血复活。",
        "背包里获得的「小还丹」仍是普通回血药品，可用 /金庸使用 小还丹 回复2d6+6点HP。",
        "绝学库：发送 /金庸绝学 查看门派/传说绝学解锁状态与技能详情。",
    ]
    for upgrade_id in META_UPGRADE_ORDER:
        row = _meta_upgrade_row(meta, upgrade_id)
        max_level = max(META_UPGRADES[upgrade_id])
        next_row = META_UPGRADES[upgrade_id].get(int(row["level"]) + 1)
        lines.append(f"{row['label']} Lv{row['level']}/{max_level}：{row['description']}")
        if next_row:
            lines.append(f"下一阶：{next_row['description']}｜消耗武道真髓×{next_row['essence_cost']}")
    lines.append("指令：/金庸强化 钓鱼｜背囊｜盘缠｜气血｜小还丹；/金庸小还丹 0｜1｜2｜3；/金庸绝学")
    return "\n".join(lines)


def ultimate_text(meta_progression: dict[str, Any] | None) -> str:
    meta = normalize_meta_progression(meta_progression)
    unlocked_sects = set(meta.get("unlocked_sect_ultimates", []))
    unlocked_legends = set(meta.get("unlocked_legendary_ultimates", []))
    sect_fragment_stock = _as_int_dict(meta.get("sect_ultimate_fragments"))
    lines = [
        "【局外绝学库】",
        f"传说残页×{meta.get('legendary_fragments', 0)}",
        "门派顶级残页：" + ("、".join(f"{sect}×{count}" for sect, count in sect_fragment_stock.items() if count > 0) or "暂无"),
    ]
    sect_lines = []
    unlocked_sect_detail_lines = []
    for sect_name, sect in SECTS.items():
        stock = int(sect_fragment_stock.get(sect_name, 0))
        if sect_name in unlocked_sects:
            row = next(
                (
                    skill for skill in MARTIAL_ART_SKILLS.values()
                    if skill.get("sect") == sect_name and skill.get("obtain_source") == "meta_sect_unlock"
                ),
                None,
            )
            summary = _meta_ultimate_skill_summary(row)
            sect_lines.append(f"{sect_name}:{sect.ultimate}[已解锁]")
            unlocked_sect_detail_lines.append(f"{sect_name}:{sect.ultimate}｜{summary}".rstrip())
        else:
            state = f"可解锁({stock}/1)" if stock >= 1 else f"未解锁({stock}/1)"
            sect_lines.append(f"{sect_name}:{sect.ultimate}[{state}]")
    lines.extend(["", "【门派局外绝学】", "｜".join(sect_lines)])
    if unlocked_sect_detail_lines:
        lines.extend(["已解锁门派绝学详情：", *unlocked_sect_detail_lines])
    legend_lines = []
    unlocked_legend_detail_lines = []
    for skill in LEGENDARY_MARTIAL_ART_SKILLS.values():
        if skill["skill_id"] in unlocked_legends:
            legend_lines.append(f"{skill['name']}[已解锁]")
            unlocked_legend_detail_lines.append(f"{skill['name']}｜{_meta_ultimate_skill_summary(skill)}")
        else:
            state = "可解锁" if int(meta.get("legendary_fragments", 0)) > 0 else "未解锁"
            legend_lines.append(f"{skill['name']}[{state}]")
    lines.extend(["", "【传说通用绝学】", "｜".join(legend_lines)])
    if unlocked_legend_detail_lines:
        lines.extend(["已解锁传说绝学详情：", *unlocked_legend_detail_lines])
    lines.append("指令：/金庸解锁绝学 绝学名；/金庸局外")
    return "\n".join(lines)


def unlock_meta_ultimate(meta_progression: dict[str, Any] | None, ultimate_name: str) -> tuple[str, dict[str, Any]]:
    meta = normalize_meta_progression(meta_progression)
    name = ultimate_name.strip()
    if not name:
        return "用法：/金庸解锁绝学 绝学名\n例：/金庸解锁绝学 太极真意", meta

    sect_match = next((sect_name for sect_name, sect in SECTS.items() if name in {sect.ultimate, sect_name}), "")
    if sect_match:
        unlocked = set(meta.get("unlocked_sect_ultimates", []))
        if sect_match in unlocked:
            return f"{sect_match}「{SECTS[sect_match].ultimate}」已经解锁。", meta
        stock = _as_int_dict(meta.get("sect_ultimate_fragments"))
        if int(stock.get(sect_match, 0)) < 1:
            return f"缺少{sect_match}顶级残页，无法解锁「{SECTS[sect_match].ultimate}」。当前库存{stock.get(sect_match, 0)}/1。", meta
        stock[sect_match] = int(stock.get(sect_match, 0)) - 1
        unlocked.add(sect_match)
        meta["sect_ultimate_fragments"] = {sect: count for sect, count in stock.items() if int(count) > 0}
        meta["unlocked_sect_ultimates"] = sorted(unlocked)
        return f"局外绝学解锁：{sect_match}「{SECTS[sect_match].ultimate}」。该门派新局可在 /金庸武学 中领悟。", meta

    legend_match = next((row for row in LEGENDARY_MARTIAL_ART_SKILLS.values() if name in {str(row["name"]), str(row["skill_id"])}), None)
    if legend_match:
        unlocked = set(meta.get("unlocked_legendary_ultimates", []))
        skill_id = str(legend_match["skill_id"])
        if skill_id in unlocked:
            return f"传说绝学「{legend_match['name']}」已经解锁。", meta
        if int(meta.get("legendary_fragments", 0)) < 1:
            return f"缺少传说残页，无法解锁「{legend_match['name']}」。当前库存{meta.get('legendary_fragments', 0)}/1。", meta
        meta["legendary_fragments"] = int(meta.get("legendary_fragments", 0)) - 1
        unlocked.add(skill_id)
        meta["unlocked_legendary_ultimates"] = sorted(unlocked)
        return f"传说绝学解锁：{legend_match['name']}。所有门派新局均可在 /金庸武学 中领悟。", meta

    return "没有找到这个绝学。可在 /金庸绝学 查看【门派局外绝学】和【传说通用绝学】名称。", meta


def set_meta_elixir_carry(meta_progression: dict[str, Any] | None, target_count: int) -> tuple[str, dict[str, Any]]:
    meta = normalize_meta_progression(meta_progression)
    target = max(0, min(3, int(target_count)))
    meta["revive_elixir_target"] = target
    cap = _meta_value(meta, "revive_elixir_carry", "revive_elixir_cap")
    effective = min(target, cap, int(meta.get("elixirs", 0)))
    return f"局外小还丹携带目标已设为{target}颗。当前升级上限{cap}颗，按现有库存下局实际可带{effective}颗。", meta


def upgrade_meta_progression(player: dict[str, Any], meta_progression: dict[str, Any] | None, upgrade_name: str) -> tuple[str, dict[str, Any]]:
    meta = normalize_meta_progression(meta_progression)
    upgrade_id = META_UPGRADE_ALIASES.get(upgrade_name) or upgrade_name
    if upgrade_id not in META_UPGRADES:
        return "未知局外强化。可选：钓鱼、背囊、盘缠、气血、小还丹。", meta
    current_level = int(meta[upgrade_id])
    next_row = META_UPGRADES[upgrade_id].get(current_level + 1)
    if next_row is None:
        return f"{META_UPGRADES[upgrade_id][current_level]['label']}已满级。", meta
    essence_cost = int(next_row["essence_cost"])
    if int(meta.get("essence", 0)) < essence_cost:
        return f"局外资源不足：需要武道真髓×{essence_cost}。当前武道真髓×{meta.get('essence', 0)}。", meta
    meta["essence"] = int(meta.get("essence", 0)) - essence_cost
    meta[upgrade_id] = current_level + 1
    player["meta_progression"] = meta
    return f"局外强化成功：{next_row['label']} Lv{next_row['level']}。{next_row['description']}", meta


def apply_pending_meta_rewards(meta_progression: dict[str, Any] | None, player: dict[str, Any]) -> tuple[dict[str, Any], str]:
    meta = normalize_meta_progression(meta_progression)
    reward = player.pop("pending_meta_rewards", {})
    if not reward:
        return meta, ""
    meta["essence"] += int(reward.get("essence", 0))
    meta["elixirs"] += int(reward.get("elixir", 0))
    meta["clears"] += 1
    player["meta_progression"] = meta
    return (
        meta,
        f"\n局外资源已入账：武道真髓×{reward.get('essence', 0)}、小还丹×{reward.get('elixir', 0)}。累计通关{meta['clears']}次。",
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
    player["hp"] = player["hp"] - actual
    return actual


def _try_meta_elixir_revive(player: dict[str, Any]) -> str:
    if int(player.get("hp", 0)) > 0:
        return ""
    carried = int(player.get("revive_elixirs", 0))
    if carried <= 0:
        return ""
    player["revive_elixirs"] = carried - 1
    revive_hp = max(1, int(player.get("max_hp", 1)) // 2)
    player["hp"] = revive_hp
    player.pop("temp_hp", None)
    return f"【小还丹护命】你气机将绝之际，随身小还丹自行化开，护住心脉。消耗局外小还丹×1，HP恢复至{revive_hp}/{player['max_hp']}，本局剩余护命小还丹×{player['revive_elixirs']}。"


def _calculate_rogue_points(player: dict[str, Any]) -> tuple[int, str]:
    """计算本局结算获得的武道真髓：每通过一层给1点。"""
    floor_points = player["floor"] - 1  # 当前层数-1 = 已通过层数
    total = max(0, floor_points)
    return total, f"层数奖励：{total}点，合计：{total}点"


def _game_over_text(player: dict[str, Any], points: int, defeat_reason: str) -> str:
    """生成战败结局描述"""
    sect = player["sect"]
    floor = player["floor"]

    endings = {
        "少林": f"你盘膝坐倒，念珠散落一地。少林金刚之躯终究未能在第{floor}层破局，手中禅杖重重插入石缝，为后来者留下一道微弱的佛光。",
        "武当": f"你长剑拄地，一口鲜血洒在太极图上。武当道法自然终未能逆转第{floor}层的杀局，身形化作一道清烟，只留下剑穗在风中飘摇。",
        "峨眉": f"你轻轻倚在石壁旁，拂尘散落。峨眉女侠的身影定格在第{floor}层，手中依然紧握着那柄短剑，仿佛下一刻便能刺出。",
        "全真": f"你道冠歪斜，缓缓倒在北斗剑阵之中。全真七子的剑阵在第{floor}层终究未能护住你，只留下一道剑气冲天。",
        "华山": f"你剑已断，人已伤。华山剑道在第{floor}层遇到了真正的对手，你用最后一丝气力，在石壁上刻下了一式剑招。",
        "丐帮": f"你仰天大笑，手中打狗棒深深插入地面。丐帮弟子在第{floor}层倒下，但侠义精神早已传遍整个武神塔。",
        "明教": f"圣火熄灭，但光明永存。明教弟子在第{floor}层战败，你眼中闪烁的圣火，将照亮后来者的道路。",
    }

    ending = endings.get(sect, f"你倒在第{floor}层的石阶上，手中还握着兵器。武道之路漫漫，这次你未能走到终点。")

    if defeat_reason == "battle":
        defeat_desc = "你在激战中气血耗尽，再也支撑不住。"
    elif defeat_reason == "trap":
        defeat_desc = "机关重重，你终究没能躲过致命一击。"
    elif defeat_reason == "surrender":
        defeat_desc = "你决定暂避锋芒，活着走出武神塔。"
    else:
        defeat_desc = "你在武神塔中倒下了。"

    return f"""════════════════════════════════════════════
【游戏结束】{defeat_desc}

{ending}

════════════════════════════════════════════
【结算】
到达层数：第{floor}层
获得武道真髓：{points}点

武道真髓已存入局外强化。
使用 /金庸开局 可开始新的挑战。"""


def surrender_game(player: dict[str, Any]) -> str:
    """放弃当前游戏，结算点数并冻结角色"""
    if player.get("game_over") or player.get("frozen"):
        if player.get("finished"):
            return "该角色已通关飞升并冻结，请用 /金庸开局 开始新的挑战。"
        return "本局已结束。使用 /金庸开局 开始新的挑战。"
    if player.get("in_combat"):
        return "战斗中无法放弃，请先结束战斗。"

    player["game_over"] = True
    player["frozen"] = True

    # 计算并结算点数
    points, points_desc = _calculate_rogue_points(player)

    # 应用到 meta
    meta = normalize_meta_progression(player.get("meta_progression"))
    meta["essence"] = meta.get("essence", 0) + points
    meta, martial_line = _settle_martial_fragments_to_meta(player, meta)

    return _game_over_text(player, points, "surrender") + martial_line


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


def _game_phase_text(player: dict[str, Any]) -> str:
    if player.get("finished") or player.get("frozen"):
        return "当前局面：已通关飞升｜可查看局外强化或重置后重开"
    if player.get("game_over"):
        return "当前局面：本局已结算｜可查看局外强化或重置后重开"
    if player.get("in_combat") and player.get("combat"):
        combat = player["combat"]
        enemy_name = combat.get("enemy_name", "敌人")
        return (
            f"当前局面：战斗中｜{enemy_name} HP {combat.get('enemy_hp', 0)}/{combat.get('enemy_max_hp', 0)}｜"
            "可攻击、防御或逃跑"
        )
    if player.get("in_trap") and player.get("trap_state"):
        trap = player["trap_state"]
        return f"当前局面：陷阱处理中｜{trap.get('name', '机关')}｜可躲避、格挡或反击"
    merchant = "｜游商在场" if _has_current_merchant(player) else ""
    if int(player.get("floor", 1)) >= MAX_FLOOR:
        fishing = "本层可钓鱼" if _fishing_available(player) else "本层已钓鱼"
        return f"当前局面：武神殿门前｜可挑战武神镜像｜{fishing}{merchant}"

    if "explored_doors" not in player or len(player.get("explored_doors", [])) != DOORS_PER_FLOOR:
        player["explored_doors"] = [False] * DOORS_PER_FLOOR
    unopened = _unopened_door_numbers(player)
    searchable = _searchable_door_numbers(player)
    fishing = "本层可钓鱼" if _fishing_available(player) else "本层已钓鱼"
    if not unopened:
        return f"当前局面：本层三门已清｜可前往下一层｜{fishing}{merchant}"

    parts = [f"当前局面：古武殿门前｜待选择门 {_door_numbers_text(unopened)}"]
    if searchable:
        parts.append(f"可细搜门 {_door_numbers_text(searchable)}")
    parts.append(fishing)
    if merchant:
        parts.append("游商在场")
    return "｜".join(parts)


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
    level = player.get("level", 1)
    current_xp = player.get("xp", 0)
    if level < MAX_LEVEL:
        next_xp = LEVEL_UP_XP.get(level + 1, 0)
        prev_xp = LEVEL_UP_XP.get(level, 0)
        xp_text = f"{current_xp}/{next_xp}"
    else:
        xp_text = "已满级"
    return (
        f"【金庸踢门团】{player.get('nickname', '')}｜Lv{level}\n"
        f"门派：{player['sect']}（{sect.camp}）｜难度：{player['difficulty']}\n"
        f"进度：第{player['floor']}层，已开门 {player['opened_doors']}/{DOORS_PER_FLOOR}\n"
        f"{_game_phase_text(player)}\n"
        f"经验：{xp_text} XP｜HP {player['hp']}/{player['max_hp']}｜临时HP {player.get('temp_hp', 0)}｜MP {player['mp']}/{player['max_mp']}｜AC {_player_ac(player)}｜攻击+{_player_attack_bonus(player)}｜伤害+{_equipment_bonus(player, 'damage_bonus')}｜碎银 {player['silver']}两｜护命丹 {player.get('revive_elixirs', 0)}\n"
        f"属性：{_ability_summary(player)}\n"
        f"素材 {player['materials']}｜局外资源请用 /金庸局外 查看\n"
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
        f"资源物品：{_resource_item_text(player)}\n"
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


def _inventory_item_price(item: dict[str, Any]) -> int:
    if str(item.get("item_type", "")) == "equipment" or "slot" in item:
        return _equipment_price(item)
    return int(CONSUMABLE_PRICE_BY_RARITY.get(str(item.get("rarity", "common")), 12))


def _inventory_item_sell_price(item: dict[str, Any]) -> int:
    if str(item.get("item_type", "")) == "equipment" or "slot" in item:
        return _equipment_sell_price(item)
    return max(1, int(_inventory_item_price(item) * CONSUMABLE_SELL_RATE_PERCENT / 100))


def _equipped_count(player: dict[str, Any], item_id: str) -> int:
    return sum(1 for equipped_id in player.get("equipped", {}).values() if equipped_id == item_id)


def _sellable_inventory_count(player: dict[str, Any], item_id: str) -> int:
    row = _inventory_item_row(item_id)
    if row is None or int(row.get("slot_size", 0)) <= 0:
        return 0
    owned = int(player.get("inventory", {}).get(item_id, 0))
    equipped = _equipped_count(player, item_id) if ("slot" in row or str(row.get("item_type", "")) == "equipment") else 0
    return max(0, owned - equipped)


def _has_current_merchant(player: dict[str, Any]) -> bool:
    if int(player.get("merchant_floor", -1)) == int(player.get("floor", 0)):
        return True
    offer = player.get("merchant_offer") or {}
    if int(offer.get("floor", -1)) == int(player.get("floor", 0)):
        return True
    equipment_offer = offer.get("equipment") or {}
    return int(equipment_offer.get("floor", -1)) == int(player.get("floor", 0))


def _active_merchant_door_num(player: dict[str, Any]) -> int:
    if not player.get("merchant_pending_leave"):
        return 0
    if int(player.get("merchant_floor", -1)) != int(player.get("floor", 0)):
        return 0
    door_num = int(player.get("merchant_door_num", 0))
    return door_num if 1 <= door_num <= DOORS_PER_FLOOR else 0


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
    equipped_ids = set(player.get("equipped", {}).values())
    return sum(
        _inventory_item_slots(item_id, int(count) - (1 if item_id in equipped_ids else 0))
        for item_id, count in player.get("inventory", {}).items()
    )


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
    equipped_ids = set(player.get("equipped", {}).values())
    for item_id, count in player.get("inventory", {}).items():
        row = _inventory_item_row(item_id)
        if row and int(count) > 0:
            display_count = int(count) - (1 if item_id in equipped_ids else 0)
            if display_count > 0:
                slots = _inventory_item_slots(item_id, display_count)
                items.append(f"{row['name']}×{display_count}({slots}格)")
    return "、".join(items) or "暂无"


def _usable_consumable_text(player: dict[str, Any]) -> str:
    _ensure_inventory(player)
    items = []
    for item_id, count in player.get("inventory", {}).items():
        row = FISH_CONSUMABLES.get(item_id) or MEDICINE_CONSUMABLES.get(item_id)
        if row and int(count) > 0:
            items.append(f"{row['name']}×{count}")
    return "、".join(items) or "暂无"


def _resource_item_text(player: dict[str, Any]) -> str:
    fragments = _ensure_martial_fragments(player)
    fragment_items = []
    if fragments.get("advanced", 0) > 0:
        fragment_items.append(f"{_fragment_name(player['sect'], 'advanced')}×{fragments['advanced']}(0格)")
    if fragments.get("ultimate", 0) > 0:
        fragment_items.append(f"{_fragment_name(player['sect'], 'ultimate')}×{fragments['ultimate']}(0格)")
    resources = [
        f"碎银×{player.get('silver', 0)}(0格)",
        f"武学素材×{player.get('materials', 0)}(0格)",
        f"武道真髓×{player.get('essence', 0)}(0格)",
    ]
    carried_baits = []
    for bait_id, count in player.get("carried_baits", {}).items():
        if int(count) > 0:
            bait_name = next((str(row["name"]) for row in BAITS.values() if str(row["bait_id"]) == str(bait_id)), str(bait_id))
            carried_baits.append(f"{bait_name}×{count}(0格)")
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
        f"临时HP {player.get('temp_hp', 0)}｜护命丹 {player.get('revive_elixirs', 0)}｜素材 {player.get('materials', 0)}"
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
        "商店：遇到【商人门】或游商后，可 /金庸出售 物品名 [数量] 出售任意占格物品；已装备的装备不会被出售。",
    ]
    offer = player.get("merchant_offer") or {}
    if offer.get("offer_type") == "backpack" and int(offer.get("floor", -1)) == int(player["floor"]):
        lines.append(f"商店背囊：「{offer['name']}」{offer['price']}两。发送 /金庸购买 {offer['name']}。")
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
            f"占格：{equipment['slot_size']}｜堆叠：{equipment['stack_size']}｜商店价：{_inventory_item_price(equipment)}两｜出售：{_inventory_item_sell_price(equipment)}两",
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
            f"商店价：{_inventory_item_price(consumable)}两｜出售：{_inventory_item_sell_price(consumable)}两",
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
            "获得：只能在【商人门】遇到游商报价后，用 /金庸购买 背囊名 购买下一档背囊。",
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
            lines.append(f"获取：第{skill['obtain_min_floor']}层后，用 /金庸武学 查看并 /金庸领悟 {skill['name']}")
            lines.append(f"领悟消耗：{_martial_cost_text(skill)}")
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
            "使用：发送 /金庸武学 查看可领悟武学，再用 /金庸领悟 武学名 消耗。",
        ])
    if name.endswith("顶级绝学残页"):
        return "\n".join([
            f"【物品详情】{name}",
            "类型：绝学残页｜用途：高层挑战与顶级武学线索",
            f"描述：{ITEM_DESC['顶级绝学残页']}",
            "使用：发送 /金庸武学 查看可领悟绝学，再用 /金庸领悟 武学名 消耗。",
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
    names.extend(row["name"] for row in BAITS.values())
    names.extend(ITEM_DESC.keys())
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


def sect_detail_text(sect_name: str, meta_progression: dict[str, Any] | None = None) -> str:
    """Generate detailed information panel for a specific sect."""
    if sect_name not in SECTS:
        return f"未知门派「{sect_name}」。\n发送 /金庸门派 查看所有可选门派。"

    sect = SECTS[sect_name]
    meta = normalize_meta_progression(meta_progression)
    ultimate_status = "已解锁" if sect_name in set(meta.get("unlocked_sect_ultimates", [])) else "未解锁"

    # Build attributes line
    attr_parts = []
    for abbr, value in sect.attrs.items():
        if value > 0:
            label = ATTR_LABELS.get(abbr, abbr)
            attr_parts.append(f"{label}+{value}")
    attr_line = "、".join(attr_parts)

    # Get sect trait descriptions (from SECT_TRAIT_ROWS)
    from .game_data import SECT_TRAIT_ROWS
    trait_details = []
    for trait_name in sect.traits:
        for row in SECT_TRAIT_ROWS:
            if row["sect"] == sect_name and row["label"] == trait_name:
                trait_details.append(f"• {trait_name}：{_trait_description(row)}")
                break

    # Build initial skills with details
    initial_skill_lines = []
    for skill_name in sect.skills:
        skill = SKILL_COMBAT_BY_NAME.get(skill_name)
        if skill:
            category = skill["category"]
            damage_type = skill["damage_type"]
            attack_segments = skill["attack_segments"]
            dice_count = skill["damage_dice_count"]
            die = skill["damage_die"]
            bonus = skill["damage_bonus"]
            mp_cost = skill["mp_cost"]
            mp_text = f"MP{mp_cost}" if mp_cost > 0 else "免费"
            initial_skill_lines.append(f"• 【{skill_name}】{category}·{damage_type}｜{mp_text}")
            initial_skill_lines.append(f"  伤害：{attack_segments}段×{dice_count}d{die}+{bonus}")
        else:
            initial_skill_lines.append(f"• 【{skill_name}】")

    # Build advanced martial arts (sect encounter skills)
    advanced_skill_lines = []
    from .game_data import MARTIAL_ART_SKILL_ROWS
    for row in MARTIAL_ART_SKILL_ROWS:
        if row["sect"] == sect_name:
            skill_name = row["name"]
            tier = row["tier"]
            category = row["category"]
            damage_type = row["damage_type"]
            attack_segments = row["attack_segments"]
            dice_count = row["damage_dice_count"]
            die = row["damage_die"]
            bonus = row["damage_bonus"]
            mp_cost = row["mp_cost"]
            mp_text = f"MP{mp_cost}" if mp_cost > 0 else "免费"
            advanced_skill_lines.append(f"• 【{skill_name}】{tier}·{category}·{damage_type}｜{mp_text}")
            advanced_skill_lines.append(f"  伤害：{attack_segments}段×{dice_count}d{die}+{bonus}")
            advanced_skill_lines.append(f"  {row['description']}")

    if not advanced_skill_lines:
        advanced_skill_lines = ["（该门派暂无可进阶武学）"]

    ultimate_lines = [f"• 【{sect.ultimate}】{ultimate_status}"]
    ultimate_row = next(
        (
            row for row in MARTIAL_ART_SKILLS.values()
            if row.get("sect") == sect_name and row.get("obtain_source") == "meta_sect_unlock"
        ),
        None,
    )
    if ultimate_row:
        mp_text = f"MP{ultimate_row['mp_cost']}" if int(ultimate_row["mp_cost"]) > 0 else "免费"
        ultimate_lines.append(f"  {ultimate_row['tier']}·{ultimate_row['category']}·{ultimate_row['damage_type']}｜{mp_text}")
        ultimate_lines.append(
            f"  伤害：{ultimate_row['attack_segments']}段×"
            f"{ultimate_row['damage_dice_count']}d{ultimate_row['damage_die']}+{ultimate_row['damage_bonus']}"
        )
        ultimate_lines.append(f"  {ultimate_row['description']}")

    # Build final panel
    lines = [
        "╔══════════════════════════════════════════════╗",
        f"║         【{sect.name}】门派详细资料",
        "╠══════════════════════════════════════════════╣",
        f"║ 【阵营】{sect.camp}",
        f"║ 【属性】{attr_line}",
        "╠══════════════════════════════════════════════╣",
        "║ 【门派特性】",
    ]

    for td in trait_details:
        lines.append(f"║ {td}")

    lines.extend([
        "╠══════════════════════════════════════════════╣",
        "║ 【初始武学】",
    ])

    for line in initial_skill_lines:
        lines.append(f"║ {line}")

    lines.extend([
        "╠══════════════════════════════════════════════╣",
        "║ 【武学进阶·门派奇遇可获】",
    ])

    for line in advanced_skill_lines:
        lines.append(f"║ {line}")

    lines.extend([
        "╠══════════════════════════════════════════════╣",
        "║ 【顶级绝学】",
    ])
    for line in ultimate_lines:
        lines.append(f"║ {line}")
    lines.extend([
        "║ （消耗本门局外顶级残页手动解锁；解锁后新局可领悟）",
        "╚══════════════════════════════════════════════╝",
        "",
        "提示：发送 /金庸开局 门派名 [普通|困难|炼狱] 选择该门派开始游戏",
    ])

    return "\n".join(lines)


def _trait_description(trait_row: dict) -> str:
    """Convert a trait row to human-readable description."""
    effect_type = trait_row["effect_type"]
    effect_value = trait_row["effect_value"]

    descriptions = {
        "damage_reduction": f"伤害减免{effect_value}点",
        "incoming_damage_delta": f"受到伤害{effect_value:+d}",
        "post_combat_hp_recovery": f"战斗后回复{effect_value}点HP",
        "encounter_mp_recovery_bonus": f"奇遇事件MP回复+{effect_value}",
        "sword_attack_bonus": f"剑法命中+{effect_value}",
        "damage_type_bonus_percent": f"对应伤害类型加成{effect_value}%",
        "status_apply": f"施加状态效果{effect_value}级",
        "max_mp_bonus": f"MP上限+{effect_value}",
        "trap_check_bonus": f"陷阱检定+{effect_value}",
        "damage_reduction_dice": f"每回合抵消1d{effect_value}伤害",
        "encounter_check_bonus": f"奇遇检定+{effect_value}",
        "crit_lifesteal_percent": f"暴击吸血{effect_value}%",
        "poison_resist_percent": f"毒抗+{effect_value}%",
    }

    return descriptions.get(effect_type, f"{effect_type} {effect_value}")


def opening_text(player: dict[str, Any], sect_name: str) -> str:
    """Display the grand opening scene with tower panoramic view."""
    sect = SECTS[sect_name]
    lines = [
        "【武神塔 · 缘起】",
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
        f"【护命小还丹】{player.get('revive_elixirs', 0)}颗｜死亡时自动消耗并半血复活",
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

    level = player.get("level", 1)
    current_xp = player.get("xp", 0)
    if level < MAX_LEVEL:
        next_xp = LEVEL_UP_XP.get(level + 1, 0)
        prev_xp = LEVEL_UP_XP.get(level, 0)
        xp_progress = int((current_xp - prev_xp) / max(1, next_xp - prev_xp) * 18)
    else:
        xp_progress = 18
    xp_bar = "█" * xp_progress + "░" * (18 - xp_progress)

    lines = [
        "╔══════════════════════════════════════════════╗",
        f"║ 【{player.get('nickname', '侠客')}】Lv{level}｜门派：{player['sect']}｜第{player['floor']}层｜门 {doors_done}/{DOORS_PER_FLOOR}",
        "╠══════════════════════════════════════════════╣",
        f"║ HP {hp_bar} {player['hp']}/{player['max_hp']}｜MP {mp_bar} {player['mp']}/{player['max_mp']}",
        f"║ EXP {xp_bar} {current_xp}/{next_xp if level < MAX_LEVEL else 'MAX'}",
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
    merchant_door = _active_merchant_door_num(player)

    for i in range(DOORS_PER_FLOOR):
        if player["explored_doors"][i]:
            # Show explore option for opened doors
            extra_explore_key = f"extra_explored_{player['floor']}_{i+1}"
            if not player.get(extra_explore_key, False):
                hints.append(f"🔍 {door_names[i]}  →  【已探索，可再次搜寻】")
            else:
                hints.append(f"🏯 {door_names[i]}  →  【已探索】")
        elif i + 1 == merchant_door:
            hints.append(f"🏪 {door_names[i]}  →  【商人仍在，可返回商店】")
        else:
            hints.append(f"🚪 {door_names[i]}  →  {hint_pools[i][(seed + hint_seeds[i]) % len(hint_pools[i])]}")

    return hints


def _fishing_available(player: dict[str, Any]) -> bool:
    return str(player.get("floor", 1)) not in player.get("fished_floor_keys", [])


def _fishing_action_hint(player: dict[str, Any]) -> str:
    if _fishing_available(player):
        return "🎣 /金庸钓鱼 [饵剂] → 本层可垂钓一次；不填饵剂默认使用普通蚯蚓饵，不消耗任何东西"
    return "🎣 本层钓鱼已用 → 每层只能垂钓一次"


def _door_numbers_text(numbers: list[int]) -> str:
    return "/".join(str(num) for num in numbers)


def _unopened_door_numbers(player: dict[str, Any]) -> list[int]:
    explored_doors = player.get("explored_doors", [False] * DOORS_PER_FLOOR)
    merchant_door = _active_merchant_door_num(player)
    return [
        idx + 1
        for idx, explored in enumerate(explored_doors[:DOORS_PER_FLOOR])
        if not explored and idx + 1 != merchant_door
    ]


def _searchable_door_numbers(player: dict[str, Any]) -> list[int]:
    explored_doors = player.get("explored_doors", [False] * DOORS_PER_FLOOR)
    floor = player.get("floor", 1)
    return [
        idx + 1
        for idx, explored in enumerate(explored_doors[:DOORS_PER_FLOOR])
        if explored and not player.get(f"extra_explored_{floor}_{idx + 1}", False)
    ]


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

    door_hints = _door_hints(player)
    unopened_doors = _unopened_door_numbers(player)
    searchable_doors = _searchable_door_numbers(player)

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
    ])
    if unopened_doors:
        door_text = _door_numbers_text(unopened_doors)
        lines.append(f"🏮 /金庸踢门 {door_text} → 选择未探索殿门进入")
    if searchable_doors:
        door_text = _door_numbers_text(searchable_doors)
        lines.append(f"🔍 /金庸探索 {door_text} → 搜寻已探索但未细搜的殿门")
    lines.extend([
        _fishing_action_hint(player),
        "📦 /金庸背包 → 查看随身行囊物品",
        "📊 /金庸状态 → 查看完整角色属性",
    ])

    if all(player["explored_doors"]):
        lines.append("")
        lines.append("⬆️ /金庸下一层 → 本层已通关，前往下一层！")

    return "\n".join(lines)


def _floor_square_return_summary_text(player: dict[str, Any]) -> str:
    """Generate a compact floor summary after events without the status panel."""
    if player.get("finished") or player.get("frozen"):
        return "【武道飞升】你已通关，肉身永寂，神魂不灭。"
    if player["floor"] >= MAX_FLOOR:
        return "\n".join([
            "【武神殿】武神镜像在殿中等待，唯有击败它方能证道飞升。",
            "本层状态：" + ("可垂钓" if _fishing_available(player) else "已钓过，不可再次垂钓"),
        ])

    door_hints = _door_hints(player)
    lines = [
        f"【第{player['floor']}层 · 古武殿】",
        _floor_atmosphere(player["floor"]),
    ]
    lines.extend(door_hints)
    lines.append("本层状态：" + ("可垂钓" if _fishing_available(player) else "已钓过，不可再次垂钓"))
    if all(player.get("explored_doors", [False] * DOORS_PER_FLOOR)):
        lines.append("/金庸下一层 → 本层已通关，前往下一层！")
    return "\n".join(lines)


def command_hint_text(player: dict[str, Any] | None = None) -> str:
    if player is None:
        return "下一步可用：/金庸门派｜/金庸开局 门派 [普通|困难|炼狱]｜/金庸帮助"

    if player.get("finished") or player.get("frozen"):
        commands = ["/金庸局外", "/金庸强化 强化名", "/金庸重置 confirm"]
    elif player.get("pending_true_wushen"):
        commands = ["/金庸踢门", "/金庸不挑战", "/金庸状态", "/金庸武学", "/金庸技能 武学名|自动"]
    elif int(player.get("floor", 1)) >= MAX_FLOOR:
        commands = ["/金庸踢门", "/金庸钓鱼 [饵剂]" if _fishing_available(player) else "本层钓鱼已用", "/金庸状态", "/金庸武学", "/金庸技能 武学名|自动"]
    elif all(player.get("explored_doors", [False]*DOORS_PER_FLOOR)):
        commands = ["/金庸下一层", "/金庸钓鱼 [饵剂]" if _fishing_available(player) else "本层钓鱼已用", "/金庸状态", "/金庸武学"]
    else:
        commands = []
        unopened_doors = _unopened_door_numbers(player)
        searchable_doors = _searchable_door_numbers(player)
        if unopened_doors:
            commands.append(f"/金庸踢门 {_door_numbers_text(unopened_doors)}")
        if searchable_doors:
            commands.append(f"/金庸探索 {_door_numbers_text(searchable_doors)}")
        commands.extend(["/金庸钓鱼 [饵剂]" if _fishing_available(player) else "本层钓鱼已用", "/金庸状态", "/金庸武学"])

    if player.get("merchant_offer"):
        offer = player.get("merchant_offer") or {}
        if offer.get("offer_type") == "backpack" and int(offer.get("floor", -1)) == int(player.get("floor", 0)):
            commands.insert(0, f"/金庸购买 {offer.get('name', '背囊名')}")
        if (offer.get("equipment") or {}).get("floor") == player.get("floor"):
            commands.insert(0, f"/金庸购买 {(offer.get('equipment') or {}).get('name', '装备名')}")
    if _has_current_merchant(player):
        commands.append("/金庸出售 物品名 [数量]")
        if player.get("merchant_pending_leave"):
            commands.append("/金庸离开商人")
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
    if player.get("game_over"):
        return "本局已结束。使用 /金庸开局 开始新的挑战。"
    if player.get("finished") or player.get("frozen"):
        return "该角色已通关飞升并冻结，请用 /金庸开局 开始新的挑战。"
    if player["floor"] == MAX_FLOOR:
        return boss_fight(player)

    # Initialize explored_doors array if not exists
    if "explored_doors" not in player or len(player["explored_doors"]) != DOORS_PER_FLOOR:
        player["explored_doors"] = [False] * DOORS_PER_FLOOR

    # If all doors are done
    if all(player["explored_doors"]):
        return "本层3道殿门已全部探索完毕。发送 /金庸下一层 继续攀登武神塔。"

    merchant_door = _active_merchant_door_num(player)
    if merchant_door and door_num == merchant_door:
        return _merchant_shop_text(player)

    # Validate door number
    if door_num < 1 or door_num > DOORS_PER_FLOOR:
        # Find next unopened door
        for i in range(DOORS_PER_FLOOR):
            if not player["explored_doors"][i] and i + 1 != merchant_door:
                door_num = i + 1
                break
        if door_num == 0:
            if merchant_door:
                return f"本层其他殿门已处理。商人仍在第{merchant_door}门，发送 /金庸离开商人 后才算完成该门。"
            return "本层已无可探索的殿门。"
    elif player["explored_doors"][door_num - 1]:
        return f"第{door_num}道殿门你已经探索过了。可以试试 /金庸探索 {door_num} 再次搜寻。"

    # Mark door as explored
    player["explored_doors"][door_num - 1] = True
    player["opened_doors"] = sum(player["explored_doors"])

    # Non-combat MP regeneration - 2 MP per turn
    _noncombat_regenerate_mp(player, 2)

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
        return opening_line + status_line + _trap_start(player, dc)
    return opening_line + status_line + _merchant(player, result, door_num)


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

    # Non-combat MP regeneration - 2 MP per turn
    _noncombat_regenerate_mp(player, 2)

    door_names = ["左殿", "中殿", "右殿"]
    door_name = door_names[door_num - 1]

    # Exploration roll - about one find every three searches.
    explore_roll = roll_percent()
    find_chance = EXPLORE_FIND_CHANCE

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
            # Martial notes become the existing in-run progression material.
            player["materials"] += 1
            lines.append("✨ 你在石壁夹层中发现一页残破的武学心得，整理后化作武学素材+1！")
        lines.append("")
        lines.append("细致的探索果然没有白费！")
    else:
        # Nothing found
        lines.append("你搜遍了每一个角落，却什么也没发现……")
        lines.append("")
        lines.append("看来这里已经被前人搜刮干净了。")

    unopened_doors = _unopened_door_numbers(player)
    searchable_doors = _searchable_door_numbers(player)

    # Add return to square prompt
    lines.extend([
        "",
        "══════════════════════",
        "",
        "探索完毕，你回到了古殿中央。",
        "",
        "可为之事：",
    ])
    if unopened_doors:
        door_text = _door_numbers_text(unopened_doors)
        lines.append(f"🏮 /金庸踢门 {door_text} → 进入其他未探索的殿门")
    lines.append(_fishing_action_hint(player))
    if searchable_doors:
        door_text = _door_numbers_text(searchable_doors)
        lines.append(f"🔍 /金庸探索 {door_text} → 探索已开启但未细搜的殿门")
    lines.append(f"📊 /金庸状态 → 查看当前角色状态")

    if all(player["explored_doors"]):
        lines.append(f"⬆️ /金庸下一层 → 继续攀登武神塔")

    return "\n".join(lines)


def _combat_status_panel(player: dict[str, Any]) -> str:
    """Generate a compact combat status panel showing both player and enemy."""
    combat = player["combat"]
    enemy_hp = combat["enemy_hp"]
    enemy_max_hp = combat["enemy_max_hp"]
    enemy_ac = combat["enemy_ac"]
    enemy_bleed_stacks = _enemy_bleed_stacks(combat)

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
    ]
    if enemy_bleed_stacks:
        lines.append(f"║ │ 状态: 流血×{enemy_bleed_stacks:<34d} │ ║")
    lines.extend([
        "║ └─────────────────────────────────────────────┘ ║",
        "╠═══════════════════════════════════════════════╣",
        f"║ ┌─ {player.get('nickname', '侠客')}｜Lv{player.get('level', 1)}｜门派：{player['sect']} ─────────┐ ║",
        f"║ │ HP: {hp_bar} {player['hp']:3d}/{player['max_hp']:3d} │ ║",
        f"║ │ MP: {mp_bar} {player['mp']:3d}/{player['max_mp']:3d} │ ║",
        f"║ │ {_core_state_line(player)[:42]:42s} │ ║",
        f"║ │ 属性：{_ability_summary(player)[:39]:39s} │ ║",
        f"║ │ 装备：{_compact_equipment_text(player)[:39]:39s} │ ║",
        f"║ │ 资源：碎银 {player['silver']}两｜药品 {_medicine_text(player)[:14]:14s} │ ║",
        "║ └─────────────────────────────────────────────┘ ║",
        "╚═══════════════════════════════════════════════╝",
    ])

    return "\n".join(lines)


def _battle(player: dict[str, Any], result: dict[str, Any]) -> str:
    """Start a turn-based combat encounter (DND style)."""
    rule = ENCOUNTER_RULES["battle"]
    difficulty = _difficulty_row(player)
    difficulty_bonus = int(difficulty["enemy_bonus"])
    enemy_floor = min(MAX_FLOOR, int(player["floor"]) + int(difficulty.get("enemy_floor_offset", 0)))
    enemy = choose_one(ENEMIES_BY_FLOOR.get(enemy_floor, ENEMIES_BY_FLOOR[1]))
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
        "player_miss_streak": 0,
        "enemy_miss_streak": 0,
        "enemy_bleed_stacks": 0,
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


def _enemy_bleed_stacks(combat: dict[str, Any]) -> int:
    return max(0, int(combat.get("enemy_bleed_stacks", 0)))


def _apply_enemy_bleed_stacks(combat: dict[str, Any], damage_result: dict[str, Any]) -> str:
    if damage_result.get("damage_type") != "流血":
        return ""
    stacks = max(0, int(damage_result.get("attack_segments", 0)))
    if stacks <= 0:
        return ""
    current = _enemy_bleed_stacks(combat) + stacks
    combat["enemy_bleed_stacks"] = current
    return f"\n流血叠加：敌人获得{stacks}层流血，当前流血×{current}。"


def _resolve_enemy_bleed(combat: dict[str, Any]) -> str:
    stacks = _enemy_bleed_stacks(combat)
    if stacks <= 0:
        return ""
    before = int(combat.get("enemy_hp", 0))
    after = max(0, before - stacks)
    combat["enemy_hp"] = after
    return f"流血发作：敌人受到{stacks}点伤害，剩余HP {after}/{combat['enemy_max_hp']}。"


def _combat_action_lines(combat: dict[str, Any], attack_text: str = "使用技能攻击") -> list[str]:
    lines = [f"  /攻击 [技能名] → {attack_text}"]
    if not combat.get("is_boss"):
        lines.append("  /逃跑 → 尝试脱离战斗")
    lines.extend([
        "  /技能 技能名 → 切换当前技能",
        "  /防御 → 进入防御姿态（AC+2）",
    ])
    return lines


def _zero_mp_combat_skill_names(player: dict[str, Any]) -> list[str]:
    names = []
    for skill in _available_combat_skill_names(player):
        row = _skill_combat_row(skill)
        if row and int(row.get("mp_cost", 0)) <= 0:
            names.append(skill)
    return names


def _mp_locked_action_text(player: dict[str, Any]) -> str:
    free_skills = _zero_mp_combat_skill_names(player)
    if free_skills:
        return "当前MP不足，只能使用0MP招式：" + "、".join(free_skills)
    return "当前MP不足且没有0MP攻击招式，只能使用 /金庸逃跑；逃跑失败时敌人会获得优势命中加成。"


def combat_attack(player: dict[str, Any], skill_name: str = "") -> str:
    """Player attack action in turn-based combat."""
    if player.get("game_over"):
        return "本局已结束。使用 /金庸开局 开始新的挑战。"
    if not player.get("in_combat") or "combat" not in player:
        return "你当前不在战斗中。"

    combat = player["combat"]
    _combat_regenerate_mp(player)
    enemy_name = combat["enemy_name"]
    enemy_ac = combat["enemy_ac"]

    # Select skill
    if skill_name:
        if skill_name in _available_combat_skill_names(player) and _skill_combat_row(skill_name):
            skill = skill_name
        else:
            return f"「{skill_name}」不可用。可用技能：{'、'.join(_available_combat_skill_names(player))}"
        row = _skill_combat_row(skill)
        if row and int(row["mp_cost"]) > int(player.get("mp", 0)):
            return "\n".join([
                _combat_status_panel(player),
                "",
                f"「{skill}」需要{row['mp_cost']}MP，当前MP不足。",
                _mp_locked_action_text(player),
            ])
    else:
        skill = _selected_combat_skill(player)
        if not skill:
            return "\n".join([
                _combat_status_panel(player),
                "",
                _mp_locked_action_text(player),
            ])

    # Attack roll
    attack_roll = roll_d20()
    attack_bonus = attr_bonus(player, SECTS[player["sect"]].main_attr) + _equipment_bonus(player, "attack_bonus") + _trait_value(player["sect"], "sword_attack_bonus")
    accuracy_bonus = COMBAT_BASE_HIT_BONUS + _combat_miss_streak_bonus(int(combat.get("player_miss_streak", 0)))
    attack_total = attack_roll + attack_bonus + accuracy_bonus
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
        f"（d20={attack_roll} + {attack_bonus} + 命中补正{accuracy_bonus} = {attack_total} ｜ 敌人防御 {enemy_ac}）",
        "",
    ]

    if is_hit:
        combat["player_miss_streak"] = 0
        damage_result = _martial_damage_result(player, skill)
        damage = int(damage_result.get("total", 0)) + _equipment_bonus(player, "damage_bonus")
        if combat.get("enemy_id") == "true_wushen" and _is_ultimate_or_legendary_skill(skill):
            damage = max(1, damage // 2)
            damage_result["line"] += "\n真·武神洞悉绝学脉络，绝学伤害减半。"
        if is_crit:
            damage *= 2  # Critical hit double damage

        combat["enemy_hp"] = max(0, combat["enemy_hp"] - damage)
        bleed_line = _apply_enemy_bleed_stacks(combat, damage_result)
        trait_line = _battle_trait_line(player, {"crit": is_crit}, {"total": damage})

        wuxia_desc = _wuxia_attack_desc(skill, is_crit, is_hit, damage)
        lines.append(wuxia_desc)
        if is_crit:
            lines.append(f"暴击！这一击打穿敌人架势，造成 {damage} 点伤害。{damage_result['line']}{bleed_line}{trait_line}")
        else:
            lines.append(f"命中！劲力入体，造成 {damage} 点伤害。{damage_result['line']}{bleed_line}{trait_line}")
        lines.append(f"敌人踉跄后退，气血剩余：{combat['enemy_hp']}/{combat['enemy_max_hp']}")

        # Check for victory
        if combat["enemy_hp"] <= 0:
            lines.extend([
                "",
                "🎉 只听敌人闷哼一声，颓然倒地！",
                "",
                "═══ 战斗结束 ═══",
                "",
                _end_combat(player, True, enemy_name=enemy_name),
            ])
            return "\n".join(lines)
    else:
        combat["player_miss_streak"] = int(combat.get("player_miss_streak", 0)) + 1
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
            _end_combat(player, enemy_result["victory"], enemy_name=enemy_name if enemy_result["victory"] else ""),
        ])
    else:
        combat["round"] += 1
        lines.extend([
            "",
            f"═══ 第{combat['round']}回合 · 你的回合 ═══",
            "",
            "📜 可用行动：",
            *_combat_action_lines(combat, "运功出招"),
            "",
            f"当前招式：{_selected_combat_skill(player)}",
        ])

    return "\n".join(lines)


def combat_flee(player: dict[str, Any]) -> str:
    """Player attempts to flee from combat."""
    if player.get("game_over"):
        return "本局已结束。使用 /金庸开局 开始新的挑战。"
    if not player.get("in_combat") or "combat" not in player:
        return "你当前不在战斗中。"
    if player.get("combat", {}).get("is_boss"):
        return "\n".join([
            _combat_status_panel(player),
            "",
            "武神殿石门已经闭合，武神镜像锁定了你的气机。",
            "最终 Boss 战不能逃跑，只能攻击、防御或调整技能。",
            "",
            "可用行动：",
            *_combat_action_lines(player["combat"]),
        ])

    combat = player["combat"]
    _combat_regenerate_mp(player)
    enemy_name = combat["enemy_name"]

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
            "本门算作完成，但你没有获得战斗奖励。",
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

        enemy_result = _enemy_turn(player, accuracy_extra=4, log_prefix="逃跑失败，敌人趁你背身抢攻，获得优势命中加成。")
        lines.append(enemy_result["log"])

        if enemy_result["combat_end"]:
            lines.extend([
                "",
                "═══ 战斗结束 ═══",
                "",
                _end_combat(player, enemy_result["victory"], enemy_name=enemy_name if enemy_result["victory"] else ""),
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
    if player.get("game_over"):
        return "本局已结束。使用 /金庸开局 开始新的挑战。"
    if not player.get("in_combat") or "combat" not in player:
        return "你当前不在战斗中。"

    combat = player["combat"]
    _combat_regenerate_mp(player)
    enemy_name = combat["enemy_name"]
    if int(player.get("mp", 0)) <= 0 and not _zero_mp_combat_skill_names(player):
        return "\n".join([
            _combat_status_panel(player),
            "",
            _mp_locked_action_text(player),
        ])
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
            _end_combat(player, enemy_result["victory"], enemy_name=enemy_name if enemy_result["victory"] else ""),
        ])
    else:
        combat["round"] += 1
        lines.extend([
            "",
            f"═══ 第{combat['round']}回合 · 你的回合 ═══",
            "",
            "可用行动：",
            *_combat_action_lines(combat),
            "",
            f"当前技能：{_selected_combat_skill(player)}",
        ])

    return "\n".join(lines)


def _enemy_turn(player: dict[str, Any], accuracy_extra: int = 0, log_prefix: str = "") -> dict[str, Any]:
    """Execute enemy turn in combat."""
    combat = player["combat"]
    enemy_name = combat["enemy_name"]
    enemy_attack = combat["enemy_attack"]
    enemy_damage = combat["enemy_damage"]
    enemy_damage_type = combat.get("enemy_damage_type", "")
    true_wushen_skill = choose_one(list(LEGENDARY_MARTIAL_ART_SKILLS.values())) if combat.get("enemy_id") == "true_wushen" else None
    if true_wushen_skill:
        enemy_damage_type = str(true_wushen_skill["damage_type"])
        enemy_damage = (
            f"{true_wushen_skill['attack_segments']}段×"
            f"{true_wushen_skill['damage_dice_count']}d{true_wushen_skill['damage_die']}+{true_wushen_skill['damage_bonus']}"
        )
    player_ac = _player_ac(player)
    bleed_log = _resolve_enemy_bleed(combat)
    if bleed_log and int(combat.get("enemy_hp", 0)) <= 0:
        return {
            "victory": True,
            "combat_end": True,
            "log": f"{bleed_log}\n{enemy_name}伤口血流不止，踉跄数步后倒在殿中。"
        }
    bleed_prefix = f"{bleed_log}\n" if bleed_log else ""

    # Check for defense stance
    if combat.get("defending"):
        player_ac += 2
        combat["defending"] = False

    enemy_roll = roll_d20()
    accuracy_bonus = COMBAT_BASE_HIT_BONUS + _combat_miss_streak_bonus(int(combat.get("enemy_miss_streak", 0))) + max(0, int(accuracy_extra))
    enemy_total = enemy_roll + enemy_attack + accuracy_bonus
    is_crit = enemy_roll == 20
    is_hit = is_crit or enemy_total >= player_ac

    if is_hit:
        combat["enemy_miss_streak"] = 0
        if true_wushen_skill:
            segment_rolls = [
                sum(roll_dice_results(int(true_wushen_skill["damage_dice_count"]), int(true_wushen_skill["damage_die"]))) + int(true_wushen_skill["damage_bonus"])
                for _ in range(int(true_wushen_skill["attack_segments"]))
            ]
            raw_damage = sum(segment_rolls)
            skill_line = f"\n真·武神施展传说绝学「{true_wushen_skill['name']}」，每段伤害={segment_rolls}，{enemy_damage_type}合计{raw_damage}。"
        else:
            raw_damage = roll_dice(str(enemy_damage))
            skill_line = ""
        if is_crit:
            raw_damage *= 2
        actual = _apply_damage(player, raw_damage)

        wuxia_desc = _wuxia_enemy_attack_desc(is_crit, is_hit, actual)

        # Check for player defeat
        if player["hp"] <= 0:
            revive_line = _try_meta_elixir_revive(player)
            if revive_line:
                return {
                    "victory": None,
                    "combat_end": False,
                    "log": f"{bleed_prefix}{log_prefix + chr(10) if log_prefix else ''}{enemy_name}骤然抢入中宫！（d20={enemy_roll}+{enemy_attack}+命中补正{accuracy_bonus}={enemy_total}｜你的AC {player_ac}｜伤害骰 {enemy_damage} {enemy_damage_type}）{skill_line}\n{wuxia_desc}\n你受到 {actual} 点伤害，气血一度断绝。\n{revive_line}"
                }
            return {
                "victory": False,
                "combat_end": True,
                "log": f"{bleed_prefix}{log_prefix + chr(10) if log_prefix else ''}{enemy_name}骤然抢入中宫！（d20={enemy_roll}+{enemy_attack}+命中补正{accuracy_bonus}={enemy_total}｜你的AC {player_ac}｜伤害骰 {enemy_damage} {enemy_damage_type}）{skill_line}\n{wuxia_desc}\n你受到 {actual} 点伤害，气血翻涌，再也支撑不住，倒了下去……"
            }

        return {
            "victory": None,
            "combat_end": False,
            "log": f"{bleed_prefix}{log_prefix + chr(10) if log_prefix else ''}{enemy_name}展开攻势，掌风贴着石壁呼啸而来。（d20={enemy_roll}+{enemy_attack}+命中补正{accuracy_bonus}={enemy_total}｜你的AC {player_ac}｜伤害骰 {enemy_damage} {enemy_damage_type}）{skill_line}\n{wuxia_desc}\n你受到 {actual} 点伤害，当前气血：{player['hp']}/{player['max_hp']}。"
        }
    else:
        combat["enemy_miss_streak"] = int(combat.get("enemy_miss_streak", 0)) + 1
        wuxia_desc = _wuxia_enemy_attack_desc(False, False, 0)
        return {
            "victory": None,
            "combat_end": False,
            "log": f"{bleed_prefix}{log_prefix + chr(10) if log_prefix else ''}{enemy_name}虚晃一招后猛然出手。（d20={enemy_roll}+{enemy_attack}+命中补正{accuracy_bonus}={enemy_total}｜你的AC {player_ac}｜伤害骰 {enemy_damage} {enemy_damage_type}）\n{wuxia_desc}\n这一击未能破开你的防守。"
        }


def _end_combat(player: dict[str, Any], victory: bool, fled: bool = False, enemy_name: str = "") -> str:
    """End combat and award rewards or handle defeat, then return to floor square."""
    combat = player.get("combat", {})
    rule = combat.get("battle_rule", ENCOUNTER_RULES["battle"])

    # Clear combat state
    player["in_combat"] = False
    player.pop("combat", None)

    lines = []

    # Check for player defeat (HP <= 0)
    if player["hp"] <= 0:
        player["game_over"] = True
        player["frozen"] = True
        points, points_desc = _calculate_rogue_points(player)
        meta = normalize_meta_progression(player.get("meta_progression"))
        meta["essence"] = meta.get("essence", 0) + points
        meta, martial_line = _settle_martial_fragments_to_meta(player, meta)
        return _game_over_text(player, points, "battle") + martial_line

    if fled:
        lines.extend([
            "你借着殿柱与烟尘遮住身形，纵身退回门外。",
            "本门已算完成；因为主动脱战，本场战斗没有经验、碎银、素材、残页或装备奖励。",
        ])
    elif victory and combat.get("is_boss"):
        boss_id = str(combat.get("enemy_id", "wushen_mirror"))
        boss = BOSSES.get(boss_id, BOSSES["wushen_mirror"])
        if player.get("difficulty") == "炼狱" and boss_id == "wushen_mirror":
            player["pending_true_wushen"] = True
            player["boss_defeated"] = True
            lines.extend([
                "武神镜像轰然崩碎，露出其后真正的武神法相。",
                "【炼狱抉择】你已击败武神雕像。",
                "继续发送 /金庸踢门 可挑战【真·武神】；发送 /金庸不挑战 可就此离塔结算，并低概率获得传说残页。",
            ])
            return "\n".join(lines)
        legendary_delta, fragment_lines = _apply_clear_fragment_rewards(player, "true_wushen" if boss_id == "true_wushen" else "normal")
        return _finish_boss_clear(player, boss, legendary_delta, fragment_lines)
    elif victory:
        silver = roll_dice(str(rule["success_silver_dice"])) + player["floor"] * int(rule["success_silver_per_floor"])
        player["silver"] += silver
        player["materials"] += int(rule["success_materials"])
        lines.extend([
            "尘埃落下，殿中只余你的呼吸声与兵刃余响。",
            f"你从敌手遗落的腰囊中搜得碎银{silver}两，又取下一份可供研习的武学素材。",
            f"奖励：碎银+{silver}两｜武学素材+{rule['success_materials']}",
        ])

        # 经验奖励
        floor = player["floor"]
        xp_amount = ENEMY_XP_BY_FLOOR.get(floor, 50)
        _, xp_msgs = add_xp(player, xp_amount, enemy_name)
        lines.extend(xp_msgs)

        fragment_chance = int(_difficulty_row(player).get("battle_fragment_chance", 0))
        if fragment_chance > 0:
            roll = roll_percent()
            if roll <= fragment_chance:
                fragment = _add_martial_fragment(player, "advanced")
                lines.append(f"战斗残篇掉落：d100={roll}，阈值≤{fragment_chance}，获得{fragment}。")
            else:
                lines.append(f"战斗残篇掉落：d100={roll}，阈值≤{fragment_chance}，未掉落。")

        drop_line = _maybe_equipment_drop(player, 35)
        if drop_line:
            lines.append(drop_line)
    else:
        # Player defeated but HP > 0 (should not happen with new logic, but keep as fallback)
        silver = roll_dice(str(rule["fail_silver_dice"]))
        player["silver"] += silver
        lines.extend([
            "你被逼退到殿门边，胸口气血翻涌，眼前一阵发黑。",
            f"等你勉强站稳，地上只剩几枚散落的碎银。你拾起{silver}两，记下这次败招。",
        ])

    # Post combat recovery
    recovery_line = _post_combat_recovery(player)
    if recovery_line:
        lines.append(recovery_line)

    lines.extend([
        "",
        "════════════════════════════════════════════",
        "",
        "战斗结束，你回到了古殿中央。",
        "",
    ])
    lines.append(_floor_square_return_summary_text(player))

    return "\n".join(lines)


def _selected_combat_skill(player: dict[str, Any]) -> str:
    active = player.get("active_skill")
    available = _available_combat_skill_names(player)
    current_mp = int(player.get("mp", 0))
    if active in available:
        row = _skill_combat_row(active)
        if row and int(row.get("mp_cost", 0)) <= current_mp:
            return str(active)
    usable = [
        skill for skill in available
        if (row := _skill_combat_row(skill)) and int(row.get("mp_cost", 0)) <= current_mp
    ]
    if usable:
        return usable[0]
    zero_mp = _zero_mp_combat_skill_names(player)
    if zero_mp:
        return zero_mp[0]
    return ""


# Legacy function for boss fight (still auto-run for now)
def _run_turn_combat(player: dict[str, Any], enemy_name: str, enemy_hp: int, enemy_ac: int, enemy_attack: int, enemy_damage_dice: str, max_rounds: int) -> dict[str, Any]:
    lines = []
    player_miss_streak = 0
    enemy_miss_streak = 0
    combat = {
        "enemy_name": enemy_name,
        "enemy_hp": enemy_hp,
        "enemy_max_hp": enemy_hp,
        "enemy_bleed_stacks": 0,
    }
    for round_no in range(1, max_rounds + 1):
        skill = _selected_combat_skill(player)
        attack_roll = roll_d20()
        attack_bonus = attr_bonus(player, SECTS[player["sect"]].main_attr) + _equipment_bonus(player, "attack_bonus") + _trait_value(player["sect"], "sword_attack_bonus")
        accuracy_bonus = COMBAT_BASE_HIT_BONUS + _combat_miss_streak_bonus(player_miss_streak)
        attack_total = attack_roll + attack_bonus + accuracy_bonus
        if attack_roll == 20 or attack_total >= enemy_ac:
            player_miss_streak = 0
            damage_result = _martial_damage_result(player, skill)
            damage = int(damage_result.get("total", 0)) + _equipment_bonus(player, "damage_bonus")
            if attack_roll == 20:
                damage *= 2
            combat["enemy_hp"] = max(0, int(combat["enemy_hp"]) - damage)
            enemy_hp = int(combat["enemy_hp"])
            bleed_line = _apply_enemy_bleed_stacks(combat, damage_result)
            trait_line = _battle_trait_line(player, {"crit": attack_roll == 20}, {"total": damage})
            crit_text = "暴击，" if attack_roll == 20 else ""
            lines.append(f"第{round_no}回合：你用「{skill}」攻击 d20={attack_roll}+{attack_bonus}+命中补正{accuracy_bonus}={attack_total} {crit_text}命中，造成{damage}伤害，敌HP剩{enemy_hp}。{damage_result['line']}{bleed_line}{trait_line}")
        else:
            player_miss_streak += 1
            lines.append(f"第{round_no}回合：你用「{skill}」攻击 d20={attack_roll}+{attack_bonus}+命中补正{accuracy_bonus}={attack_total} 未破AC{enemy_ac}。")
        if enemy_hp <= 0:
            return {"victory": True, "log": "\n".join(lines)}

        bleed_log = _resolve_enemy_bleed(combat)
        if bleed_log:
            lines.append(bleed_log)
            enemy_hp = int(combat["enemy_hp"])
            if enemy_hp <= 0:
                lines.append(f"{enemy_name}伤口血流不止，踉跄数步后倒在殿中。")
                return {"victory": True, "log": "\n".join(lines)}

        enemy_roll = roll_d20()
        enemy_accuracy_bonus = COMBAT_BASE_HIT_BONUS + _combat_miss_streak_bonus(enemy_miss_streak)
        enemy_total = enemy_roll + enemy_attack + enemy_accuracy_bonus
        player_ac = _player_ac(player)
        if enemy_roll == 20 or enemy_total >= player_ac:
            enemy_miss_streak = 0
            raw_damage = roll_dice(enemy_damage_dice)
            actual = _apply_damage(player, raw_damage)
            lines.append(f"{enemy_name}反击 d20={enemy_roll}+{enemy_attack}+命中补正{enemy_accuracy_bonus}={enemy_total} 命中AC{player_ac}，你损失{actual}HP。")
        else:
            enemy_miss_streak += 1
            lines.append(f"{enemy_name}反击 d20={enemy_roll}+{enemy_attack}+命中补正{enemy_accuracy_bonus}={enemy_total} 未破AC{player_ac}。")
    return {"victory": False, "log": "\n".join(lines)}


def _regenerate_mp(player: dict[str, Any], amount: int) -> int:
    """Regenerate MP by amount (capped at max_mp). Returns actual amount recovered."""
    recovered = min(player["max_mp"] - player["mp"], amount)
    if recovered > 0:
        player["mp"] += recovered
    return recovered


def _difficulty_row(player: dict[str, Any]) -> dict[str, Any]:
    return DIFFICULTIES.get(player.get("difficulty", "普通"), DIFFICULTIES["普通"])


def _combat_regenerate_mp(player: dict[str, Any]) -> int:
    difficulty = _difficulty_row(player)
    amount = int(difficulty.get("combat_mp_regen", 1))
    interval = max(1, int(difficulty.get("combat_mp_regen_interval", 1)))
    combat = player.get("combat") if isinstance(player.get("combat"), dict) else {}
    round_no = max(1, int(combat.get("round", 1)))
    if amount <= 0 or round_no % interval != 0:
        return 0
    return _regenerate_mp(player, amount)


def _noncombat_regenerate_mp(player: dict[str, Any], fallback: int = 2) -> int:
    return _regenerate_mp(player, int(_difficulty_row(player).get("noncombat_mp_regen", fallback)))


def _floor_transition_hp_recovery(player: dict[str, Any]) -> str:
    rule = SECT_FLOOR_RECOVERY_RULES.get(player["sect"])
    if not rule:
        return ""
    amount = int(rule["hp_recovery"])
    before = int(player.get("hp", 0))
    max_hp = int(player.get("max_hp", 0))
    recovered = max(0, min(max_hp - before, amount))
    if recovered:
        player["hp"] = before + recovered
        return f"门派调息：{rule['flavor']}，回复{recovered}HP。"
    return f"门派调息：{rule['flavor']}，你气血已满。"


def _floor_transition_mp_recovery(player: dict[str, Any]) -> str:
    amount = int(_difficulty_row(player).get("floor_mp_recovery", 0))
    if amount <= 0:
        return ""
    before = int(player.get("mp", 0))
    recovered = _regenerate_mp(player, amount)
    if recovered:
        return f"下层调息：回复{recovered}MP（{before}->{player['mp']}）。"
    return "下层调息：你的MP已满。"


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

    lines.append(_floor_square_return_summary_text(player))
    merchant_line = _maybe_floor_merchant_after_doors(player)
    if merchant_line:
        lines.append(merchant_line)

    return "\n".join(lines)


def _chest(player: dict[str, Any], result: dict[str, Any]) -> str:
    rule = ENCOUNTER_RULES["chest"]
    xp_msgs = _award_room_completion_xp(player, label="宝箱房间完成")
    if result["fumble"]:
        dmg = roll_dice(str(rule["fumble_damage_dice"]))
        dmg = _apply_damage(player, dmg)
        event_line = (
            "【宝箱门】\n"
            "石台上的铜箱覆满尘灰，锁孔里隐约有机簧转动的细响。\n"
            f"你刚探手去拨，箱底暗弩骤然弹出。检定：d20=1，机关彻底失控。\n"
            f"你侧身已晚，被弩矢擦中，损失{dmg}HP；宝箱也在机关绞动中碎成一地铜片。\n"
            + "\n".join(xp_msgs)
        )
    else:
        silver = roll_dice(str(rule["success_silver_dice"])) + player["floor"] * int(rule["success_silver_per_floor"])
        player["silver"] += silver
        _add_medicine(player, int(rule["success_medicine"]))
        tier = "ultimate" if result["crit"] else "advanced"
        fragment = _add_martial_fragment(player, tier)
        drop_line = _maybe_equipment_drop(player, 45 if result["crit"] else 25)
        event_line = (
            "【宝箱门】\n"
            "你伏身听锁，指尖顺着铜箱纹路一点点摸过去，终于按住了机关的死门。\n"
            f"开箱检定：d20={result['die']} + {result['bonus']} = {result['total']}。\n"
            f"箱盖开启，一缕药香和旧纸气息扑面而来：碎银+{silver}两｜金疮药+{rule['success_medicine']}｜{fragment}。\n"
            + "\n".join(xp_msgs) + "\n"
            f"{drop_line}"
        )

    return event_line + _return_to_floor_square(player)


def _encounter(player: dict[str, Any], result: dict[str, Any]) -> str:
    rule = ENCOUNTER_RULES["encounter"]
    xp_msgs = _award_room_completion_xp(player, label="奇遇房间完成")
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
            + "\n".join(xp_msgs) + "\n"
            f"{skill_line}"
        )
    else:
        event_line = (
            "【奇遇门】\n"
            "你在壁画前驻足良久，只觉画中招式似有深意，却始终差一线明悟。\n"
            f"检定：d20={result['die']} + {result['bonus']} = {result['total']}。\n"
            "这次机缘与你擦肩而过；你没有收获，却也没有惊动殿中禁制。\n"
            + "\n".join(xp_msgs)
        )

    return event_line + _return_to_floor_square(player)


def _fragment_name(sect_name: str, tier: str) -> str:
    return str(ITEMS_BY_TIER[tier]["name_template"]).format(sect=sect_name)


def _ensure_martial_fragments(player: dict[str, Any]) -> dict[str, int]:
    fragments = player.get("martial_fragments")
    if not isinstance(fragments, dict):
        fragments = {"advanced": 0, "ultimate": 0}
        for name in player.get("fragments", []):
            if str(name).endswith("中阶武学残页"):
                fragments["advanced"] += 1
            elif str(name).endswith("顶级绝学残页"):
                fragments["ultimate"] += 1
        for tier, count in player.get("skill_fragments", {}).items():
            if str(tier) in fragments:
                fragments[str(tier)] += max(0, int(count))
        player["martial_fragments"] = fragments
    fragments["advanced"] = max(0, int(fragments.get("advanced", 0)))
    fragments["ultimate"] = max(0, int(fragments.get("ultimate", 0)))
    return fragments


def _add_martial_fragment(player: dict[str, Any], tier: str, quantity: int = 1) -> str:
    fragments = _ensure_martial_fragments(player)
    fragments[tier] = int(fragments.get(tier, 0)) + max(0, int(quantity))
    name = _fragment_name(player["sect"], tier)
    player.setdefault("fragments", []).append(name)
    return name


def _consume_martial_fragment(player: dict[str, Any], tier: str, quantity: int) -> None:
    fragments = _ensure_martial_fragments(player)
    fragments[tier] = max(0, int(fragments.get(tier, 0)) - int(quantity))
    suffix = "中阶武学残页" if tier == "advanced" else "顶级绝学残页"
    old_fragments = list(player.get("fragments", []))
    for _ in range(int(quantity)):
        for idx in range(len(old_fragments) - 1, -1, -1):
            if str(old_fragments[idx]).endswith(suffix):
                old_fragments.pop(idx)
                break
    player["fragments"] = old_fragments


def compose_martial_fragments(player: dict[str, Any], quantity: int = 1) -> str:
    quantity = max(1, int(quantity))
    fragments = _ensure_martial_fragments(player)
    required = MARTIAL_FRAGMENT_COMPOSE_RATE * quantity
    if int(fragments.get("advanced", 0)) < required:
        return (
            f"中阶残页不足，无法合成顶级残页。\n"
            f"比例：中阶残页{MARTIAL_FRAGMENT_COMPOSE_RATE}张 → 顶级残页1张。\n"
            f"当前：中阶残页{fragments.get('advanced', 0)}张｜顶级残页{fragments.get('ultimate', 0)}张。"
        )
    _consume_martial_fragment(player, "advanced", required)
    for _ in range(quantity):
        _add_martial_fragment(player, "ultimate")
    fragments = _ensure_martial_fragments(player)
    return (
        f"残页合成完成：消耗中阶残页{required}张，获得顶级残页{quantity}张。\n"
        f"当前：中阶残页{fragments.get('advanced', 0)}张｜顶级残页{fragments.get('ultimate', 0)}张。\n"
        "发送 /金庸武学 查看可领悟绝学。"
    )


def _settle_martial_fragments_to_meta(player: dict[str, Any], meta_progression: dict[str, Any] | None, legendary_fragment_delta: int = 0) -> tuple[dict[str, Any], str]:
    meta = normalize_meta_progression(meta_progression)
    sect_name = str(player["sect"])
    fragments = _ensure_martial_fragments(player)
    advanced_stock = _as_int_dict(meta.get("sect_advanced_fragments"))
    ultimate_stock = _as_int_dict(meta.get("sect_ultimate_fragments"))
    lines: list[str] = []

    run_advanced = int(fragments.get("advanced", 0))
    run_ultimate = int(fragments.get("ultimate", 0))
    total_advanced = int(advanced_stock.get(sect_name, 0)) + run_advanced
    composed_ultimate = total_advanced // MARTIAL_FRAGMENT_COMPOSE_RATE
    advanced_stock[sect_name] = total_advanced % MARTIAL_FRAGMENT_COMPOSE_RATE
    total_ultimate = int(ultimate_stock.get(sect_name, 0)) + run_ultimate + composed_ultimate

    if run_advanced or run_ultimate or composed_ultimate:
        lines.append(
            f"残页结算：本局中阶残页×{run_advanced}、顶级残页×{run_ultimate}；"
            f"自动合成顶级残页×{composed_ultimate}，剩余中阶残页×{advanced_stock[sect_name]}存入局外。"
        )

    ultimate_stock[sect_name] = total_ultimate
    if total_ultimate > 0:
        lines.append(f"{sect_name}顶级残页库存×{total_ultimate}。可手动 /金庸解锁绝学 {SECTS[sect_name].ultimate}。")

    legendary_delta = max(0, int(legendary_fragment_delta))
    if legendary_delta:
        meta["legendary_fragments"] = int(meta.get("legendary_fragments", 0)) + legendary_delta
        lines.append(f"传说残页入账：+{legendary_delta}。")

    meta["unlocked_sect_ultimates"] = sorted(set(meta.get("unlocked_sect_ultimates", [])))
    meta["unlocked_legendary_ultimates"] = sorted(set(meta.get("unlocked_legendary_ultimates", [])))
    meta["sect_advanced_fragments"] = {sect: count for sect, count in advanced_stock.items() if int(count) > 0}
    meta["sect_ultimate_fragments"] = {sect: count for sect, count in ultimate_stock.items() if int(count) > 0}
    fragments["advanced"] = 0
    fragments["ultimate"] = 0
    player["fragments"] = []
    player["meta_progression"] = meta
    return meta, ("\n" + "\n".join(lines) if lines else "")


def _apply_clear_fragment_rewards(player: dict[str, Any], mode: str) -> tuple[int, list[str]]:
    difficulty = _difficulty_row(player)
    lines: list[str] = []
    legendary_delta = 0
    if mode == "true_wushen":
        reward = _add_martial_fragment(player, "ultimate")
        legendary_delta = 1
        lines.append(f"炼狱真·武神奖励：{reward}、传说残页×1。")
        return legendary_delta, lines

    if int(difficulty.get("clear_ultimate_fragment", 0)) > 0:
        reward = _add_martial_fragment(player, "ultimate")
        lines.append(f"通关门派残篇奖励：{reward}。")
    advanced_chance = int(difficulty.get("clear_advanced_fragment_chance", 0))
    if advanced_chance > 0:
        roll = roll_percent()
        if roll <= advanced_chance:
            reward = _add_martial_fragment(player, "advanced")
            lines.append(f"通关中阶残篇掉落：d100={roll}，阈值≤{advanced_chance}，获得{reward}。")
        else:
            lines.append(f"通关中阶残篇掉落：d100={roll}，阈值≤{advanced_chance}，未掉落。")
    legendary_chance = int(difficulty.get("clear_legendary_chance", 0))
    if legendary_chance > 0:
        roll = roll_percent()
        if roll <= legendary_chance:
            legendary_delta = 1
            lines.append(f"传说残页掉落：d100={roll}，阈值≤{legendary_chance}，获得传说残页×1。")
        else:
            lines.append(f"传说残页掉落：d100={roll}，阈值≤{legendary_chance}，未掉落。")
    return legendary_delta, lines


def _finish_boss_clear(player: dict[str, Any], boss: dict[str, Any], legendary_delta: int, fragment_lines: list[str]) -> str:
    reward = BOSS_CLEAR_REWARDS[player["difficulty"]]
    clear_points, _ = _calculate_rogue_points(player)
    total_essence = clear_points + int(reward["essence"])
    player["silver"] += int(reward["silver"])
    meta = normalize_meta_progression(player.get("meta_progression"))
    meta["essence"] += total_essence
    meta["elixirs"] += int(reward["elixir"])
    meta["clears"] += 1
    unlock_lines: list[str] = []
    if player.get("difficulty") == "困难":
        hard_clear_sects = set(meta.get("hard_clear_sects", []))
        if player["sect"] not in hard_clear_sects:
            hard_clear_sects.add(player["sect"])
            meta["hard_clear_sects"] = sorted(hard_clear_sects)
            unlock_lines.append(f"炼狱解锁：{player['sect']}困难通关完成，今后可选择该门派炼狱难度。")
    meta, martial_line = _settle_martial_fragments_to_meta(player, meta, legendary_delta)
    player["boss_defeated"] = True
    player["finished"] = True
    player["frozen"] = True
    player.pop("pending_true_wushen", None)
    lines = [
        f"{boss['name']}身形寸寸碎裂，殿顶星图重新归位。",
        f"【武神殿通关】你击败{boss['name']}，角色飞升并永久冻结。",
        f"结算奖励：层数武道真髓×{clear_points}、通关武道真髓×{reward['essence']}，合计武道真髓×{total_essence}；小还丹×{reward['elixir']}、碎银×{reward['silver']}两。",
        *unlock_lines,
        *fragment_lines,
    ]
    return "\n".join(lines) + martial_line


def decline_true_wushen(player: dict[str, Any]) -> str:
    if player.get("game_over"):
        return "本局已结束。使用 /金庸开局 开始新的挑战。"
    if player.get("finished") or player.get("frozen"):
        return "该角色已通关飞升并冻结，请用 /金庸开局 开始新的挑战。"
    if not player.get("pending_true_wushen"):
        return "当前没有真·武神抉择。只有炼狱击败武神雕像后，才可 /金庸不挑战。"

    difficulty = _difficulty_row(player)
    legendary_delta, fragment_lines = _apply_clear_fragment_rewards(player, "normal")
    chance = int(difficulty.get("decline_true_wushen_legendary_chance", 0))
    if chance > 0:
        roll = roll_percent()
        if roll <= chance:
            legendary_delta += 1
            fragment_lines.append(f"不挑战传说残页检定：d100={roll}，阈值≤{chance}，获得传说残页×1。")
        else:
            fragment_lines.append(f"不挑战传说残页检定：d100={roll}，阈值≤{chance}，未获得。")
    text = _finish_boss_clear(player, BOSSES["wushen_mirror"], legendary_delta, fragment_lines)
    return "你收剑后退，没有踏入真·武神法相。\n" + text


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


def _martial_cost(row: dict[str, Any]) -> dict[str, int | str]:
    if row.get("obtain_source") == "meta_sect_unlock":
        return {"fragment_tier": "", "fragments": 0, "materials": 8}
    if row.get("obtain_source") == "meta_legendary_unlock":
        return {"fragment_tier": "", "fragments": 0, "materials": 10}
    return MARTIAL_LEARN_COSTS.get(str(row.get("tier")), MARTIAL_LEARN_COSTS["进阶"])


def _martial_cost_text(row: dict[str, Any]) -> str:
    cost = _martial_cost(row)
    if int(cost["fragments"]) <= 0:
        return f"素材x{cost['materials']}"
    frag_label = "中阶残页" if cost["fragment_tier"] == "advanced" else "顶级残页"
    return f"{frag_label}x{cost['fragments']} + 素材x{cost['materials']}"


def _martial_learn_rows(player: dict[str, Any]) -> list[dict[str, Any]]:
    sect_name = str(player["sect"])
    meta = normalize_meta_progression(player.get("meta_progression"))
    unlocked_sects = set(meta.get("unlocked_sect_ultimates", []))
    unlocked_legends = set(meta.get("unlocked_legendary_ultimates", []))
    rows = []
    for row in MARTIAL_ART_SKILLS.values():
        source = str(row.get("obtain_source", ""))
        if row["sect"] == sect_name and source == "sect_encounter":
            rows.append(row)
        elif row["sect"] == sect_name and source == "meta_sect_unlock" and sect_name in unlocked_sects:
            rows.append(row)
        elif row["sect"] == "通用" and source == "meta_legendary_unlock" and row["skill_id"] in unlocked_legends:
            rows.append(row)
    return rows


def _martial_row_status(player: dict[str, Any], row: dict[str, Any]) -> str:
    if row["skill_id"] in player.get("learned_skill_ids", []):
        return "已学"
    choices = player.setdefault("exclusive_skill_choices", {})
    group = str(row.get("exclusive_group") or "")
    if group and group in choices:
        return "同组已锁"
    if int(player.get("floor", 1)) < int(row.get("obtain_min_floor", 1)):
        return f"第{row['obtain_min_floor']}层后"
    cost = _martial_cost(row)
    fragments = _ensure_martial_fragments(player)
    if int(cost["fragments"]) > 0 and int(fragments.get(str(cost["fragment_tier"]), 0)) < int(cost["fragments"]):
        return "残页不足"
    if int(player.get("materials", 0)) < int(cost["materials"]):
        return "素材不足"
    return "可领悟"


def martial_text(player: dict[str, Any]) -> str:
    fragments = _ensure_martial_fragments(player)
    learned = _learned_skill_names(player)
    lines = [
        "【武学领悟】",
        f"资源：武学素材 {player.get('materials', 0)}｜中阶残页 {fragments.get('advanced', 0)}｜顶级残页 {fragments.get('ultimate', 0)}",
        f"残页合成：中阶残页{MARTIAL_FRAGMENT_COMPOSE_RATE}张 → 顶级残页1张；命令 /金庸合成残页 [数量]",
        "",
        "已学进阶/绝学：",
        "、".join(learned) if learned else "暂无",
        "",
        "可领悟武学：",
        "────────────────",
    ]
    rows = _martial_learn_rows(player)
    for idx, row in enumerate(rows, start=1):
        status = _martial_row_status(player, row)
        lines.append(
            f"{idx}. {row['name']}｜{row['tier']}｜{row['category']}｜{row['damage_type']}｜MP{row['mp_cost']}｜{status}"
        )
        lines.append(f"   消耗：{_martial_cost_text(row)}")
        lines.append(f"   伤害：{row['attack_segments']}段 × {row['damage_dice_count']}d{row['damage_die']}+{row['damage_bonus']}")
    lines.extend([
        "────────────────",
        "命令：/金庸领悟 武学名｜/金庸合成残页 [数量]｜/金庸查看 武学名｜/金庸技能 武学名",
    ])
    return "\n".join(lines)


def learn_martial_skill(player: dict[str, Any], skill_name: str) -> str:
    name = skill_name.strip()
    if not name:
        return "用法：/金庸领悟 武学名\n发送 /金庸武学 查看可领悟武学。"
    row = MARTIAL_ART_SKILLS_BY_NAME.get(name)
    if not row or row not in _martial_learn_rows(player):
        return f"没有找到你当前门派可领悟的「{name}」。发送 /金庸武学 查看列表。"
    if row["skill_id"] in player.get("learned_skill_ids", []):
        return f"你已经领悟「{row['name']}」。"
    status = _martial_row_status(player, row)
    if status != "可领悟":
        return f"暂不能领悟「{row['name']}」：{status}。\n发送 /金庸武学 查看资源和条件。"
    cost = _martial_cost(row)
    player["materials"] = max(0, int(player.get("materials", 0)) - int(cost["materials"]))
    if int(cost["fragments"]) > 0:
        _consume_martial_fragment(player, str(cost["fragment_tier"]), int(cost["fragments"]))
    player.setdefault("learned_skill_ids", []).append(row["skill_id"])
    group = str(row.get("exclusive_group") or "")
    if group:
        player.setdefault("exclusive_skill_choices", {})[group] = row["skill_id"]
    return (
        f"你消耗{_martial_cost_text(row)}，领悟「{row['name']}」（{row['tier']}）。\n"
        f"现在可用 /金庸技能 {row['name']} 设为常用招式，战斗中也可 /金庸攻击 {row['name']}。"
    )


def _sect_encounter_skill_reward(player: dict[str, Any]) -> str:
    if player["floor"] < 2:
        return ""
    player["materials"] += 1
    return (
        "\n进阶武学奇遇：你整理本门心得，额外获得武学素材+1。"
        "发送 /金庸武学 查看可领悟武学。"
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


def _is_ultimate_or_legendary_skill(skill_name: str) -> bool:
    art = MARTIAL_ART_SKILLS_BY_NAME.get(skill_name)
    return bool(art and str(art.get("tier")) in {"顶级", "传说"})


def _martial_damage_result(player: dict[str, Any], skill_name: str) -> dict[str, Any]:
    row = _skill_combat_row(skill_name)
    if row is None:
        return {"line": "", "total": 0, "damage_type": "", "attack_segments": 0, "segment_rolls": []}
    if player["mp"] < int(row["mp_cost"]):
        return {"line": f"\n{skill_name}需要{row['mp_cost']}MP，当前MP不足。", "total": 0, "damage_type": "", "attack_segments": 0, "segment_rolls": []}

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
    return {
        "line": line,
        "total": total,
        "damage_type": str(row["damage_type"]),
        "attack_segments": int(row["attack_segments"]),
        "segment_rolls": segment_rolls,
    }


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
        else:
            lines.append("门派特性触发：暴击吸血，但气血已满。")
    return ("\n" + "\n".join(line for line in lines if line)) if lines else ""


def _trap_start(player: dict[str, Any], dc: int) -> str:
    """触发陷阱，进入选择状态"""
    rule = ENCOUNTER_RULES["trap"]
    player["in_trap"] = True
    player["trap_state"] = {
        "dc": dc,
        "damage_dice": rule["fail_damage_dice"],
        "success_silver": rule["success_silver"],
    }
    return (
        "【陷阱门】\n"
        "地砖下传来轻微空响，机关已然触发！\n\n"
        "墙缝中喷出一阵腥甜毒雾，你必须立即应对——\n\n"
        "▸ /金庸躲避  （敏捷检定：成功完全闪避，失败受全额伤害）\n"
        "▸ /金庸格挡  （体质检定：无论成败都减伤，但奖励降低）\n"
        "▸ /金庸反击  （力量检定：高风险高回报，成功获双倍奖励）"
    )


def _clear_trap_state(player: dict[str, Any]) -> None:
    """清理陷阱状态"""
    player.pop("in_trap", None)
    player.pop("trap_state", None)


def _check_trap_game_over(player: dict[str, Any]) -> str | None:
    """检查陷阱是否导致游戏结束"""
    if player["hp"] <= 0:
        revive_line = _try_meta_elixir_revive(player)
        if revive_line:
            _clear_trap_state(player)
            return revive_line + _return_to_floor_square(player)
        player["game_over"] = True
        player["frozen"] = True
        points, points_desc = _calculate_rogue_points(player)
        meta = normalize_meta_progression(player.get("meta_progression"))
        meta["essence"] = meta.get("essence", 0) + points
        meta, martial_line = _settle_martial_fragments_to_meta(player, meta)
        _clear_trap_state(player)
        return _game_over_text(player, points, "trap") + martial_line
    return None


def trap_dodge(player: dict[str, Any]) -> str:
    """躲避：敏捷检定，成功完全避开，失败受全额伤害"""
    if not player.get("in_trap") or "trap_state" not in player:
        return "你当前不在陷阱中。"

    trap = player["trap_state"]
    dc = trap["dc"]
    damage_dice = trap["damage_dice"]
    base_silver = int(trap["success_silver"])

    # 敏捷检定
    result = check(player, "dex", dc, _event_check_bonus(player, "trap"))

    if result["success"]:
        silver = int(base_silver * 0.5)
        player["silver"] += silver
        xp_msgs = _award_room_completion_xp(player, label="陷阱房间完成")
        _clear_trap_state(player)
        event_line = (
            "【陷阱门 - 躲避成功】\n"
            "你脚下步法展开，身形如鬼魅般挪移！\n"
            f"敏捷检定：d20={result['die']} + {result['bonus']} = {result['total']}。\n"
            f"毒雾从你身边擦过，毫发无损。顺手拆下机关零件，换得碎银{silver}两。\n"
            + "\n".join(xp_msgs)
        )
        return event_line + _return_to_floor_square(player)
    else:
        dmg = roll_dice(str(damage_dice))
        dmg = _apply_damage(player, dmg)
        poison_effect = _apply_status(player, "poison", 1)

        game_over_result = _check_trap_game_over(player)
        if game_over_result:
            return game_over_result

        _clear_trap_state(player)
        xp_msgs = _award_room_completion_xp(player, label="陷阱房间完成")
        event_line = (
            "【陷阱门 - 躲避失败】\n"
            "你身法虽快，却还是慢了半步！\n"
            f"敏捷检定：d20={result['die']} + {result['bonus']} = {result['total']}。\n"
            f"毒雾侵入经脉，损失{dmg}HP。{poison_effect}\n"
            + "\n".join(xp_msgs)
        )
        return event_line + _return_to_floor_square(player)


def trap_block(player: dict[str, Any]) -> str:
    """格挡：体质检定，无论成功失败都减伤"""
    if not player.get("in_trap") or "trap_state" not in player:
        return "你当前不在陷阱中。"

    trap = player["trap_state"]
    dc = trap["dc"]
    damage_dice = trap["damage_dice"]
    base_silver = int(trap["success_silver"])

    # 体质检定
    result = check(player, "con", dc, _event_check_bonus(player, "trap"))
    full_damage = roll_dice(str(damage_dice))

    if result["success"]:
        dmg = max(1, int(full_damage * 0.33))
        actual_dmg = _apply_damage(player, dmg)
        silver = int(base_silver * 0.25)
        player["silver"] += silver

        game_over_result = _check_trap_game_over(player)
        if game_over_result:
            return game_over_result

        _clear_trap_state(player)
        xp_msgs = _award_room_completion_xp(player, label="陷阱房间完成")
        event_line = (
            "【陷阱门 - 格挡成功】\n"
            "你运转真气，双臂交错硬接！\n"
            f"体质检定：d20={result['die']} + {result['bonus']} = {result['total']}。\n"
            f"毒雾被你真气逼退大半，只受了{actual_dmg}点轻伤。拆下少量零件，换得碎银{silver}两。\n"
            + "\n".join(xp_msgs)
        )
        return event_line + _return_to_floor_square(player)
    else:
        dmg = max(1, int(full_damage * 0.5))
        actual_dmg = _apply_damage(player, dmg)
        poison_chance = roll_percent()
        poison_effect = _apply_status(player, "poison", 1) if poison_chance <= 50 else ""

        game_over_result = _check_trap_game_over(player)
        if game_over_result:
            return game_over_result

        _clear_trap_state(player)
        xp_msgs = _award_room_completion_xp(player, label="陷阱房间完成")
        event_line = (
            "【陷阱门 - 格挡勉强】\n"
            "你虽想硬接，但力道还是差了些！\n"
            f"体质检定：d20={result['die']} + {result['bonus']} = {result['total']}。\n"
            f"毒雾部分侵入，损失{actual_dmg}HP。{poison_effect}\n"
            + "\n".join(xp_msgs)
        )
        return event_line + _return_to_floor_square(player)


def trap_counter(player: dict[str, Any]) -> str:
    """反击：力量检定，高风险高回报"""
    if not player.get("in_trap") or "trap_state" not in player:
        return "你当前不在陷阱中。"

    trap = player["trap_state"]
    dc = trap["dc"]
    damage_dice = trap["damage_dice"]
    base_silver = int(trap["success_silver"])

    # 力量检定
    result = check(player, "str", dc, _event_check_bonus(player, "trap"))

    if result["success"]:
        silver = int(base_silver * 2)
        player["silver"] += silver
        extra_exp = _room_completion_xp(player, 2)
        xp_msgs = _award_room_completion_xp(player, 2, "陷阱反击双倍奖励")
        _clear_trap_state(player)
        event_line = (
            "【陷阱门 - 反击成功！】\n"
            "你不闪不避，反而一掌拍向机关核心！\n"
            f"力量检定：d20={result['die']} + {result['bonus']} = {result['total']}。\n"
            f"机关被你彻底破坏，零件完好无损！\n"
            f"双倍奖励：收获碎银{silver}两，额外获得{extra_exp}点武道经验。\n"
            + "\n".join(xp_msgs)
        )
        return event_line + _return_to_floor_square(player)
    else:
        dmg = roll_dice(str(damage_dice))
        dmg = max(1, int(dmg * 1.5))
        actual_dmg = _apply_damage(player, dmg)
        # 附加重伤状态（-1 所有检定）
        wound_effect = _apply_status(player, "wounded", 2)

        game_over_result = _check_trap_game_over(player)
        if game_over_result:
            return game_over_result

        _clear_trap_state(player)
        xp_msgs = _award_room_completion_xp(player, label="陷阱房间完成")
        event_line = (
            "【陷阱门 - 反击失败】\n"
            "你太过急躁，反而正中机关圈套！\n"
            f"力量检定：d20={result['die']} + {result['bonus']} = {result['total']}。\n"
            f"机关全力爆发，损失{actual_dmg}HP。{wound_effect}\n"
            + "\n".join(xp_msgs)
        )
        return event_line + _return_to_floor_square(player)


def _merchant_shop_text(player: dict[str, Any]) -> str:
    offer = player.get("merchant_offer") or {}
    lines = ["【商店】游商仍在本层等候。"]
    if offer.get("offer_type") == "backpack" and int(offer.get("floor", -1)) == int(player.get("floor", 0)):
        lines.append(f"背囊：「{offer['name']}」{offer['price']}两｜/金庸购买 {offer['name']}")
    equipment = offer.get("equipment") or {}
    if equipment and int(equipment.get("floor", -1)) == int(player.get("floor", 0)):
        lines.append(f"装备：「{equipment['name']}」{equipment['price']}两｜/金庸购买 {equipment['name']}")
    lines.append("不再购买时，发送 /金庸离开商人。离开后该商人门才算完成。")
    return "\n".join(lines)


def _merchant(player: dict[str, Any], result: dict[str, Any], door_num: int = 0) -> str:
    player["merchant_floor"] = player["floor"]
    player["merchant_door_floor"] = player["floor"]
    player["merchant_door_num"] = door_num
    player["merchant_pending_leave"] = True
    player["merchant_miss_floor_streak"] = 0
    if 1 <= door_num <= DOORS_PER_FLOOR:
        player["explored_doors"][door_num - 1] = False
        player["opened_doors"] = sum(player["explored_doors"])
    rule = ENCOUNTER_RULES["merchant"]
    xp_msgs = _award_room_completion_xp(player, label="商人房间完成")
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
            f"一番讨价还价后，你花费{cost}两购得金疮药+{rule['buy_medicine']}。\n"
            + "\n".join(xp_msgs)
            + f"{bag_offer_line}{equipment_offer_line}"
        )
    else:
        event_line = (
            "【商人门】\n"
            "游商把药匣推到灯下，又把算盘珠拨得清脆作响。\n"
            f"报价{cost}两，可你摸了摸钱袋，碎银还差一截。\n"
            + "\n".join(xp_msgs)
            + f"{bag_offer_line}{equipment_offer_line}"
        )

    return event_line + "\n\n" + _merchant_shop_text(player)


def leave_merchant(player: dict[str, Any]) -> str:
    if not _has_current_merchant(player):
        return "当前没有游商在场。"
    door_num = _active_merchant_door_num(player)
    if door_num:
        if "explored_doors" not in player or len(player["explored_doors"]) != DOORS_PER_FLOOR:
            player["explored_doors"] = [False] * DOORS_PER_FLOOR
        player["explored_doors"][door_num - 1] = True
        player["opened_doors"] = sum(player["explored_doors"])
    player["merchant_offer"] = {}
    player.pop("merchant_pending_leave", None)
    player.pop("merchant_door_num", None)
    player.pop("merchant_floor", None)
    return "你向游商拱手作别，商人收起货箱离开。本门探索完成。" + _return_to_floor_square(player)


def _create_floor_merchant_offer(player: dict[str, Any]) -> str:
    player["merchant_floor"] = player["floor"]
    result = {"success": False}
    bag_offer_line = _create_merchant_backpack_offer(player, result)
    equipment_offer_line = _create_merchant_equipment_offer(player, result)
    return (
        "【游商驻足】\n"
        "本层三道殿门皆已踢过，一名游商挑灯从偏廊现身。他不占三道殿门，只把货箱摊开，等你自取自买。\n"
        f"{bag_offer_line}{equipment_offer_line}\n"
        "可直接使用 /金庸购买 商品名 购买，或 /金庸出售 物品名 [数量] 出售背包占格物品。"
    )


def _maybe_floor_merchant_after_doors(player: dict[str, Any]) -> str:
    if int(player.get("merchant_guaranteed_floor", -1)) != int(player.get("floor", 0)):
        return ""
    if not all(player.get("explored_doors", [False] * DOORS_PER_FLOOR)):
        return ""
    player.pop("merchant_guaranteed_floor", None)
    return "\n" + _create_floor_merchant_offer(player)


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
    return f"\n游商另售「{target['name']}」：{target['capacity_slots']}格，报价{price}两{discount_line}。发送 /金庸购买 {target['name']} 买下。"


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
    if player.get("game_over"):
        return "本局已结束。使用 /金庸开局 开始新的挑战。"
    if player.get("finished") or player.get("frozen"):
        return "该角色已通关飞升并冻结，请用 /金庸开局 开始新的挑战。"
    if player["floor"] >= MAX_FLOOR:
        if player.get("pending_true_wushen"):
            return "真·武神法相已现。发送 /金庸踢门 挑战真·武神，或 /金庸不挑战 就此离塔结算。"
        return "你已在武神殿。发送 /金庸踢门 挑战武神镜像。"

    # Initialize explored_doors array if not exists
    if "explored_doors" not in player or len(player["explored_doors"]) != DOORS_PER_FLOOR:
        player["explored_doors"] = [False] * DOORS_PER_FLOOR

    if not all(player["explored_doors"]):
        remaining = DOORS_PER_FLOOR - sum(player["explored_doors"])
        return f"本层还有 {remaining} 道殿门未探索。"

    # Non-combat MP regeneration - 2 MP per turn
    _noncombat_regenerate_mp(player, 2)

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
        reward = _add_martial_fragment(player, str(rule["fragment_tier"]))
        _add_medicine(player, int(rule["medicine_delta"]))
        player["materials"] += int(rule["materials_delta"])
        lines.append(f"自然20：旧印大亮，你从石台暗匣中取得{reward}，并获得金疮药+{rule['medicine_delta']}、素材+{rule['materials_delta']}。")
        skill_line = _sect_encounter_skill_reward(player)
        if skill_line:
            lines.append(skill_line.strip())
    elif result["success"]:
        rule = SECT_ENCOUNTER_RULES["success"]
        reward = _add_martial_fragment(player, str(rule["fragment_tier"]))
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

    recovery_line = _floor_transition_hp_recovery(player)
    if recovery_line:
        lines.append(recovery_line)
    mp_recovery_line = _floor_transition_mp_recovery(player)
    if mp_recovery_line:
        lines.append(mp_recovery_line)

    old_floor = int(player["floor"])
    had_merchant_door = int(player.get("merchant_door_floor", -1)) == old_floor
    miss_streak = 0 if had_merchant_door else int(player.get("merchant_miss_floor_streak", 0)) + 1

    player["floor"] += 1
    player["explored_doors"] = [False] * DOORS_PER_FLOOR
    player["opened_doors"] = 0
    player["merchant_offer"] = {}
    if miss_streak >= 2:
        player["merchant_miss_floor_streak"] = 0
        player["merchant_guaranteed_floor"] = player["floor"]
    else:
        player["merchant_miss_floor_streak"] = miss_streak
    if player["floor"] == MAX_FLOOR:
        lines.append("石阶尽头传来沉闷钟鸣，第7层武神殿已解锁。发送 /金庸踢门 挑战唯一BOSS武神镜像；炼狱胜后可选择挑战真·武神。")
    else:
        lines.append(f"你收束气息，沿石阶继续上行，进入第{player['floor']}层。")
    return "\n".join(lines)


def boss_fight(player: dict[str, Any]) -> str:
    sect = SECTS[player["sect"]]
    boss_key = "true_wushen" if player.get("pending_true_wushen") else "wushen_mirror"
    boss = BOSSES[boss_key]
    if boss_key == "true_wushen":
        player.pop("pending_true_wushen", None)
    difficulty_bonus = int(DIFFICULTIES[player["difficulty"]]["enemy_bonus"])
    boss_attack = int(boss["attack_bonus"]) + difficulty_bonus // 2
    boss_damage = str(boss["damage_dice"])
    intro = check(player, sect.main_attr, int(boss["check_dc"]) + difficulty_bonus // 2)

    player_init = roll_d20() + attr_bonus(player, "dex")
    boss_init = roll_d20() + difficulty_bonus // 2
    player["in_combat"] = True
    player["combat"] = {
        "enemy_id": str(boss["boss_id"]),
        "enemy_name": str(boss["name"]),
        "enemy_hp": int(boss["hp"]),
        "enemy_max_hp": int(boss["hp"]),
        "enemy_ac": int(boss["ac"]),
        "enemy_attack": boss_attack,
        "enemy_damage": boss_damage,
        "enemy_damage_type": str(boss.get("damage_type", "")),
        "enemy_desc": str(boss.get("desc", "")),
        "round": 1,
        "player_init": player_init,
        "enemy_init": boss_init,
        "turn": "player" if player_init >= boss_init else "enemy",
        "log": [],
        "battle_rule": ENCOUNTER_RULES["battle"],
        "player_miss_streak": 0,
        "enemy_miss_streak": 0,
        "enemy_bleed_stacks": 0,
        "is_boss": True,
    }

    boss_panel = (
        f"【武神殿】{boss['name']}｜HP {boss['hp']}｜AC {boss['ac']}｜攻击 +{boss_attack}｜伤害 {boss_damage} {boss.get('damage_type', '')}\n"
        f"{boss.get('desc', '')}\n"
        ("真·武神会随机施展所有传说绝学；你使用顶级/传说绝学命中时伤害减半。"
         if boss_key == "true_wushen"
         else "殿顶星图旋转，四壁浮现你一路击败过的招式残影；这是本局最终 Boss 战，不能逃跑。")
    )
    lines = [
        _combat_status_panel(player),
        "",
        boss_panel,
        f"入殿检定：d20={intro['die']} + {intro['bonus']} = {intro['total']}。",
        "",
        "═══ 先攻投掷 ═══",
        f"你身法：d20 + {attr_bonus(player, 'dex')} = {player_init}",
        f"{boss['name']}：d20 + {difficulty_bonus // 2} = {boss_init}",
        "",
    ]
    if player_init >= boss_init:
        lines.extend([
            "⚡ 你身形更快，抢先出手！",
            "",
            "═══ 你的回合 ═══",
            "",
            "可用行动：",
            *_combat_action_lines(player["combat"]),
            "",
            f"可用技能：{'、'.join(_available_combat_skill_names(player))}",
        ])
    else:
        enemy_result = _enemy_turn(player)
        lines.extend([
            f"⚔️ {boss['name']}获得先手！",
            "",
            "═══ 敌人回合 ═══",
            "",
            enemy_result["log"],
        ])
        if enemy_result["combat_end"]:
            lines.extend(["", "═══ 战斗结束 ═══", "", _end_combat(player, enemy_result["victory"], enemy_name=str(boss["name"]))])
        else:
            lines.extend([
                "",
                "═══ 你的回合 ═══",
                "",
                "可用行动：",
                *_combat_action_lines(player["combat"]),
                "",
                f"可用技能：{'、'.join(_available_combat_skill_names(player))}",
            ])
    return "\n".join(lines)


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

    # Non-combat MP regeneration - 2 MP per turn
    _noncombat_regenerate_mp(player, 2)

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


def _non_consumable_use_hint(query: str, player: dict[str, Any]) -> str:
    name = query.strip()
    if not name:
        return "用法：/金庸使用 药品名或鱼获名\n药品和鱼获可直接使用；资源、装备、饵剂需要用对应命令。"
    if name in {"碎银", "银两", "钱"}:
        return (
            "「碎银」是交易货币，不能直接 /金庸使用。\n"
            "使用场景：遇到【商人门】后，用 /金庸购买 背囊名或装备名 购买商店商品。"
        )
    if name in {"武学素材", "素材"}:
        return (
            "「武学素材」是局内成长资源，不能直接 /金庸使用。\n"
            "使用场景：发送 /金庸武学 查看可领悟武学；中阶残页可用 /金庸合成残页 合成顶级残页。"
        )
    if name in {"武道真髓", "真髓", "局外点数", "局外资源"}:
        return (
            "「武道真髓」是局外强化资源，不能直接 /金庸使用。\n"
            "使用场景：发送 /金庸局外 查看强化表，再用 /金庸强化 钓鱼|背囊|盘缠|气血|小还丹 消耗。"
        )
    if name in {"武学残卷", "残卷"}:
        return (
            "「武学残卷」是旧版局外资源，当前版本不再使用。\n"
            "现在局外强化统一消耗「武道真髓」；发送 /金庸局外 查看当前可强化项目。"
        )
    if name.endswith("中阶武学残页") or name.endswith("顶级绝学残页") or name in {"武学残页", "残页"}:
        return (
            f"「{name}」是武学线索类记录，不能直接 /金庸使用。\n"
            "使用场景：发送 /金庸武学 查看可领悟武学，再用 /金庸领悟 武学名 消耗。"
        )
    bait = BAITS.get(name) or next((row for row in BAITS.values() if name == str(row["bait_id"])), None)
    if bait:
        return (
            f"「{bait['name']}」是钓鱼饵剂，不能用 /金庸使用。\n"
            f"使用场景：本层还可钓鱼时，发送 /金庸钓鱼 {bait['name']}；每层只能钓鱼一次。"
        )
    backpack = BACKPACKS_BY_NAME.get(name) or BACKPACKS.get(name)
    if backpack:
        return (
            f"「{backpack['name']}」是背囊，不是消耗品。\n"
            "使用场景：遇到【商人门】出现背囊报价后，发送 /金庸购买 背囊名 购买并自动替换。"
        )
    skill = MARTIAL_ART_SKILLS_BY_NAME.get(name) or SKILL_COMBAT_BY_NAME.get(name)
    if skill:
        return (
            f"「{name}」是武学技能，不能用 /金庸使用。\n"
            "使用场景：发送 /金庸技能 武学名 设置常用技能；战斗中也可以 /金庸攻击 武学名 指定招式。"
        )
    return (
        f"无法直接使用「{name}」。/金庸使用 只支持药品和鱼获消耗品。\n"
        "资源看 /金庸背包，条目详情看 /金庸查看 名称。当前可用消耗品："
        + _usable_consumable_text(player)
    )


def use_consumable(player: dict[str, Any], item_name: str) -> str:
    _ensure_inventory(player)
    item_name = item_name.strip()
    item = _resolve_inventory_item(item_name)
    if item is None:
        return _non_consumable_use_hint(item_name, player)
    if item.get("item_type") not in {"fish_consumable", "medicine_consumable"}:
        return (
            f"「{item['name']}」不是可使用消耗品。\n"
            f"使用场景：装备请用 /金庸装备 {item['name']}；遇到商人门后也可 /金庸出售 {item['name']} [数量] 换碎银。"
        )
    item_id = str(item["item_id"])
    inventory = player.setdefault("inventory", {})
    if int(inventory.get(item_id, 0)) <= 0:
        return f"你没有可使用的「{item['name']}」。"

    effect_type = str(item["effect_type"])
    if effect_type == "hp_recovery" and int(player.get("hp", 0)) >= int(player.get("max_hp", 0)):
        return (
            f"现在不需要使用「{item['name']}」：你的HP已满（{player['hp']}/{player['max_hp']}）。\n"
            "使用场景：受伤后、Boss战前补血，或背包满了需要腾格子时再使用。"
        )
    if effect_type == "mp_recovery" and int(player.get("mp", 0)) >= int(player.get("max_mp", 0)):
        return (
            f"现在不需要使用「{item['name']}」：你的MP已满（{player['mp']}/{player['max_mp']}）。\n"
            "使用场景：连续使用武学导致内力不足后再使用。"
        )
    if effect_type == "temp_hp" and int(player.get("temp_hp", 0)) > 0:
        return (
            f"现在不适合使用「{item['name']}」：你已有临时HP {player.get('temp_hp', 0)} 点。\n"
            "使用场景：临时HP消耗完后，或进入高风险战斗前再使用。"
        )
    if effect_type == "next_d20_bonus" and int(player.get("next_check_bonus", 0)) > 0:
        return (
            f"现在不适合使用「{item['name']}」：你已有下一次d20检定+{player.get('next_check_bonus', 0)}。\n"
            "使用场景：先触发一次踢门、奇遇、陷阱等d20检定，消耗当前加值后再使用。"
        )

    inventory[item_id] = int(inventory.get(item_id, 0)) - 1
    if inventory[item_id] <= 0:
        inventory.pop(item_id, None)

    # Non-combat MP regeneration - 2 MP per turn
    _noncombat_regenerate_mp(player, 2)

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
    merchant_offer = player.get("merchant_offer") or {}
    backpack_offer = merchant_offer if merchant_offer.get("offer_type") == "backpack" else {}
    if backpack_offer and int(backpack_offer.get("floor", -1)) == int(player["floor"]):
        target = BACKPACKS.get(str(backpack_offer.get("bag_id", "")))
        if target and item_name in {str(target["name"]), str(target["bag_id"])}:
            return buy_backpack(player, item_name)
        if target and not item_name:
            return f"商人同时出售背囊「{target['name']}」。发送 /金庸购买 {target['name']} 确认购买。"

    offer = merchant_offer.get("equipment") or {}
    if not offer or int(offer.get("floor", -1)) != int(player["floor"]):
        if backpack_offer:
            return f"当前商人只出售背囊「{backpack_offer.get('name', '背囊')}」。发送 /金庸购买 {backpack_offer.get('name', '背囊名')} 确认购买。"
        return "当前没有商人商品报价。需要在踢门遇到【商人门】后，按商人报价使用 /金庸购买 商品名。"
    item = EQUIPMENT_BY_ID.get(str(offer.get("item_id", "")))
    if item is None:
        player.setdefault("merchant_offer", {}).pop("equipment", None)
        return "当前商人装备报价已失效。"
    if item_name and item_name not in {str(item["name"]), str(item["item_id"])}:
        if backpack_offer:
            names = [str(backpack_offer.get("name", "背囊")), str(item["name"])]
            return "当前商人出售：" + "、".join(names) + "。发送 /金庸购买 商品名 确认购买。"
        return f"当前商人只出售「{item['name']}」。发送 /金庸购买 {item['name']} 确认购买。"
    price = int(offer["price"])
    if player["silver"] < price:
        return f"碎银不足，购买「{item['name']}」需要{price}两，当前{player['silver']}两。"
    if not _can_add_inventory_item(player, str(item["item_id"]), 1):
        return f"背囊剩余{_inventory_free_slots(player)}格不足，无法购买「{item['name']}」（占{item['slot_size']}格）。可先 /金庸出售 物品名 或 /金庸丢弃 物品名 腾出空间。"
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
        return "当前没有商人在场，不能出售物品。需要在踢门遇到【商人门】或游商后，再使用 /金庸出售 物品名 [数量]。"
    item = _resolve_inventory_item(item_name)
    if item is None:
        return "未找到可出售物品。当前背包物品：" + _inventory_item_text(player)
    quantity = max(1, quantity)
    item_id = str(item["item_id"])
    inventory = player.setdefault("inventory", {})
    owned = int(inventory.get(item_id, 0))
    equipped = _equipped_count(player, item_id) if ("slot" in item or str(item.get("item_type", "")) == "equipment") else 0
    sellable = _sellable_inventory_count(player, item_id)
    if sellable <= 0:
        if equipped > 0:
            return f"「{item['name']}」正在装备中，不能直接出售。请先换下该部位装备，或出售背包中未装备的同名装备。"
        return f"你没有可出售的「{item['name']}」。"
    amount = min(quantity, sellable)
    price_each = _inventory_item_sell_price(item)
    total = price_each * amount
    left = owned - amount
    if left > 0:
        inventory[item_id] = left
    else:
        inventory.pop(item_id, None)
    player["silver"] += total
    return (
        f"你将「{item['name']}」×{amount}摆到柜上，游商验过成色，数出碎银{total}两。\n"
        f"单价：{price_each}两｜当前碎银 {player['silver']}两｜背囊容量 {inventory_used_slots(player)}/{_backpack_capacity(player)}格。"
    )


def buy_backpack(player: dict[str, Any], backpack_name: str = "") -> str:
    _ensure_inventory(player)
    offer = player.get("merchant_offer") or {}
    if offer.get("offer_type") != "backpack" or int(offer.get("floor", -1)) != int(player["floor"]):
        return "当前没有商人背囊报价。需要在踢门遇到【商人门】后，按商人报价使用 /金庸购买 背囊名。"
    target = BACKPACKS.get(str(offer.get("bag_id", "")))
    if target is None:
        equipment_offer = offer.get("equipment")
        player["merchant_offer"] = {"equipment": equipment_offer} if equipment_offer else {}
        return "当前商人背囊报价已失效。"
    if backpack_name and backpack_name not in {str(target["name"]), str(target["bag_id"])}:
        return f"当前商人只出售「{target['name']}」。发送 /金庸购买 {target['name']} 确认购买。"
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
        "/金庸开局 门派 [普通|困难|炼狱]：创建角色\n"
        "/金庸状态：查看当前角色\n"
        "/金庸踢门：开启当前层随机事件门；第7层挑战武神镜像，炼狱可继续挑战真·武神\n"
        "/金庸不挑战：炼狱击败武神镜像后放弃真·武神并结算\n"
        "/金庸下一层：清完3门后触发本门奇遇并上楼\n"
        "/金庸钓鱼 [饵剂]：每层一次，默认普通蚯蚓饵，不消耗碎银\n"
        "/金庸背包：查看背囊容量、物品、待拾取与占格规则\n"
        "/金庸装备 装备名：装备武器、防具或饰品\n"
        "/金庸技能 武学名|自动：设置战斗优先使用的武学\n"
        "/金庸武学：查看可领悟武学、素材和残页\n"
        "/金庸领悟 武学名：消耗残页和武学素材领悟进阶武学或顶级绝学\n"
        "/金庸解锁绝学 绝学名：消耗局外顶级残页或传说残页，解锁局外绝学\n"
        "/金庸绝学：查看局外绝学库、解锁状态与技能详情\n"
        "/金庸合成残页 [数量]：按4张中阶残页合成1张顶级残页\n"
        "/金庸购买 商品名：遇到商人门后，购买当前商人报价的背囊或装备\n"
        "/金庸出售 物品名 [数量]：在商店出售背包占格物品换碎银；已装备的装备不会被出售\n"
        "/金庸局外：查看局外强化等级、炼狱解锁与下一阶消耗\n"
        "/金庸强化 钓鱼|背囊|盘缠|气血|小还丹：消耗武道真髓提升局外属性\n"
        "/金庸小还丹 0|1|2|3：设置新局携带护命小还丹目标数量\n"
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
