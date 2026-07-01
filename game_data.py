from __future__ import annotations

from dataclasses import dataclass


ABILITY_ROWS = (
    {"ability": "str", "label": "力量", "dnd_label": "Strength"},
    {"ability": "dex", "label": "敏捷", "dnd_label": "Dexterity"},
    {"ability": "con", "label": "体质", "dnd_label": "Constitution"},
    {"ability": "int", "label": "智力", "dnd_label": "Intelligence"},
    {"ability": "wis", "label": "感知", "dnd_label": "Wisdom"},
    {"ability": "cha", "label": "魅力", "dnd_label": "Charisma"},
)

ATTR_LABELS = {row["ability"]: row["label"] for row in ABILITY_ROWS}


@dataclass(frozen=True)
class Sect:
    name: str
    camp: str
    attrs: dict[str, int]
    traits: tuple[str, ...]
    skills: tuple[str, ...]
    ultimate: str

    @property
    def main_attr(self) -> str:
        return max(self.attrs, key=self.attrs.get)


SECT_ROWS = (
    {"sect": "少林", "camp": "名门正派", "str": 1, "dex": 0, "con": 3, "int": 0, "wis": 0, "cha": 0, "initial_skills": ("罗汉拳", "易筋经残篇"), "ultimate": "罗汉伏魔功"},
    {"sect": "武当", "camp": "名门正派", "str": 0, "dex": 0, "con": 0, "int": 3, "wis": 1, "cha": 0, "initial_skills": ("太极拳", "太极剑"), "ultimate": "太极真意"},
    {"sect": "峨眉", "camp": "名门正派", "str": 0, "dex": 1, "con": 0, "int": 0, "wis": 2, "cha": 0, "initial_skills": ("峨眉剑法", "峨嵋九阳功"), "ultimate": "九阳真解"},
    {"sect": "全真", "camp": "名门正派", "str": 0, "dex": 0, "con": 0, "int": 2, "wis": 1, "cha": 0, "initial_skills": ("全真剑法", "先天功"), "ultimate": "天罡北斗阵"},
    {"sect": "华山", "camp": "名门正派", "str": 2, "dex": 2, "con": 0, "int": 0, "wis": 0, "cha": 0, "initial_skills": ("华山长拳", "华山剑法", "养气诀"), "ultimate": "独孤九剑"},
    {"sect": "丐帮", "camp": "江湖大派", "str": 1, "dex": 3, "con": 0, "int": 0, "wis": 0, "cha": 0, "initial_skills": ("降龙十八掌基础式", "打狗棒法"), "ultimate": "降龙十八掌全本"},
    {"sect": "明教", "camp": "江湖大派", "str": 2, "dex": 0, "con": 1, "int": 0, "wis": 0, "cha": 0, "initial_skills": ("乾坤大挪移残篇", "圣火令法"), "ultimate": "九阳圣火"},
    {"sect": "青城", "camp": "江湖大派", "str": 0, "dex": 2, "con": 0, "int": 1, "wis": 0, "cha": 0, "initial_skills": ("青城剑法", "催心掌"), "ultimate": "摧心化骨"},
    {"sect": "雪山派", "camp": "江湖大派", "str": 2, "dex": 0, "con": 1, "int": 0, "wis": 0, "cha": 0, "initial_skills": ("雪山剑法", "寒冰神掌"), "ultimate": "雪山无影剑"},
    {"sect": "大理段氏", "camp": "江湖大派", "str": 0, "dex": 0, "con": 0, "int": 2, "wis": 2, "cha": 0, "initial_skills": ("一阳指初阶", "段家剑法", "段氏吐纳法"), "ultimate": "六脉神剑"},
    {"sect": "逍遥派", "camp": "隐世秘宗", "str": 0, "dex": 2, "con": 0, "int": 2, "wis": 0, "cha": 0, "initial_skills": ("天山折梅手", "北冥吐纳法", "凌波微步初阶"), "ultimate": "北冥神功"},
    {"sect": "金刚宗", "camp": "隐世秘宗", "str": 3, "dex": 0, "con": 2, "int": 0, "wis": 0, "cha": 0, "initial_skills": ("金刚拳初阶", "火焰刀初阶"), "ultimate": "火焰刀全本"},
    {"sect": "桃花岛", "camp": "隐世秘宗", "str": 0, "dex": 1, "con": 0, "int": 3, "wis": 0, "cha": 0, "initial_skills": ("落英神剑掌", "弹指神通"), "ultimate": "奇门五转"},
    {"sect": "日月神教", "camp": "邪派魔教", "str": 2, "dex": 1, "con": 0, "int": 0, "wis": 0, "cha": 0, "initial_skills": ("葵花宝典残篇", "吸星大法"), "ultimate": "葵花宝典"},
    {"sect": "血刀门", "camp": "邪派魔教", "str": 3, "dex": 0, "con": 2, "int": 0, "wis": 0, "cha": 0, "initial_skills": ("血刀刀法初阶", "嗜血心法", "血洗山河"), "ultimate": "血刀经"},
    {"sect": "白驼山庄", "camp": "邪派魔教", "str": 0, "dex": 2, "con": 0, "int": 2, "wis": 0, "cha": 0, "initial_skills": ("白驼蛇毒掌", "蛤蟆功初阶"), "ultimate": "蛤蟆功全本"},
)


SECT_TRAIT_ROWS = (
    {"trait_id": "shaolin_guard", "sect": "少林", "label": "佛门护体", "effect_type": "damage_reduction", "effect_value": 1},
    {"trait_id": "wudang_counter", "sect": "武当", "label": "太极卸力", "effect_type": "incoming_damage_delta", "effect_value": -1},
    {"trait_id": "emei_heal", "sect": "峨眉", "label": "剑气护心", "effect_type": "post_combat_hp_recovery", "effect_value": 2},
    {"trait_id": "quanzhen_focus", "sect": "全真", "label": "先天调息", "effect_type": "encounter_mp_recovery_bonus", "effect_value": 1},
    {"trait_id": "huashan_sword_accuracy", "sect": "华山", "label": "剑类命中+1", "effect_type": "sword_attack_bonus", "effect_value": 1},
    {"trait_id": "gaibang_dodge", "sect": "丐帮", "label": "高闪避", "effect_type": "incoming_damage_delta", "effect_value": -1},
    {"trait_id": "mingjiao_fire", "sect": "明教", "label": "火焰AOE", "effect_type": "damage_type_bonus_percent", "effect_value": 20},
    {"trait_id": "qingcheng_poison", "sect": "青城", "label": "毒伤增幅", "effect_type": "damage_type_bonus_percent", "effect_value": 20},
    {"trait_id": "xueshan_ice", "sect": "雪山派", "label": "冰伤减速", "effect_type": "status_apply", "effect_value": 1},
    {"trait_id": "dali_mp", "sect": "大理段氏", "label": "MP上限+4", "effect_type": "max_mp_bonus", "effect_value": 4},
    {"trait_id": "xiaoyao_tools", "sect": "逍遥派", "label": "机关拆解+2", "effect_type": "trap_check_bonus", "effect_value": 2},
    {"trait_id": "jingang_guard", "sect": "金刚宗", "label": "每回合抵消1d6伤害", "effect_type": "damage_reduction_dice", "effect_value": 6},
    {"trait_id": "taohua_array", "sect": "桃花岛", "label": "阵法控制", "effect_type": "encounter_check_bonus", "effect_value": 1},
    {"trait_id": "riyue_absorb", "sect": "日月神教", "label": "吸真气", "effect_type": "post_combat_mp_recovery", "effect_value": 1},
    {"trait_id": "xuedao_lifesteal", "sect": "血刀门", "label": "暴击吸血100%", "effect_type": "crit_lifesteal_percent", "effect_value": 100},
    {"trait_id": "baituo_poison_resist", "sect": "白驼山庄", "label": "毒抗+30%", "effect_type": "poison_resist_percent", "effect_value": 30},
)


SECT_TRAITS_BY_SECT = {
    row["sect"]: tuple(item["label"] for item in SECT_TRAIT_ROWS if item["sect"] == row["sect"])
    for row in SECT_ROWS
}

SECTS: dict[str, Sect] = {
    row["sect"]: Sect(
        row["sect"],
        row["camp"],
        {ability["ability"]: int(row[ability["ability"]]) for ability in ABILITY_ROWS},
        SECT_TRAITS_BY_SECT[row["sect"]],
        tuple(row["initial_skills"]),
        row["ultimate"],
    )
    for row in SECT_ROWS
}


PLAYER_START_ROWS = (
    {"key": "hp_base", "value": 28},
    {"key": "hp_per_con", "value": 3},
    {"key": "mp_base", "value": 8},
    {"key": "mp_per_int", "value": 1},
    {"key": "silver", "value": 60},
    {"key": "supplies", "value": 2},
)
PLAYER_START = {row["key"]: int(row["value"]) for row in PLAYER_START_ROWS}


DIFFICULTY_ROWS = (
    {"difficulty": "普通", "base_dc": 10, "enemy_bonus": 0, "clear_essence": 2, "clear_scrolls": 5},
    {"difficulty": "困难", "base_dc": 13, "enemy_bonus": 3, "clear_essence": 4, "clear_scrolls": 10},
)
DIFFICULTIES = {row["difficulty"]: row for row in DIFFICULTY_ROWS}


ENCOUNTER_TYPE_ROWS = (
    {"event_id": "battle", "label": "战斗", "weight": 40, "check_attr": "main", "dc_floor_delta": 1},
    {"event_id": "chest", "label": "宝箱", "weight": 20, "check_attr": "main", "dc_floor_delta": 1},
    {"event_id": "encounter", "label": "奇遇", "weight": 15, "check_attr": "main", "dc_floor_delta": 1},
    {"event_id": "trap", "label": "陷阱", "weight": 15, "check_attr": "main", "dc_floor_delta": 1},
    {"event_id": "merchant", "label": "商人", "weight": 10, "check_attr": "cha", "dc_floor_delta": 1},
)
ENCOUNTER_TYPES = {row["event_id"]: row for row in ENCOUNTER_TYPE_ROWS}
ENCOUNTER_TYPES_BY_LABEL = {row["label"]: row for row in ENCOUNTER_TYPE_ROWS}
EVENT_WEIGHTS = tuple((row["event_id"], int(row["weight"])) for row in ENCOUNTER_TYPE_ROWS)


ENCOUNTER_RULE_ROWS = (
    {"event_id": "battle", "enemy_hp_base": 12, "enemy_hp_per_floor": 5, "success_silver_dice": "1d11+7", "success_silver_per_floor": 2, "success_materials": 1, "fail_damage_dice": "1d7+3", "fail_damage_per_floor": 1, "fail_silver_dice": "1d7+1"},
    {"event_id": "chest", "success_silver_dice": "1d19+11", "success_silver_per_floor": 3, "success_supplies": 1, "fumble_damage_dice": "1d6+2"},
    {"event_id": "encounter", "success_materials": 2, "success_mp_recovery": 2},
    {"event_id": "trap", "success_silver": 10, "fail_damage_dice": "1d8+4"},
    {"event_id": "merchant", "base_cost": 20, "success_discount": 10, "min_cost": 8, "buy_supplies": 2, "backpack_discount_percent_success": 10},
)
ENCOUNTER_RULES = {row["event_id"]: row for row in ENCOUNTER_RULE_ROWS}


SECT_ENCOUNTER_RULE_ROWS = (
    {"outcome": "crit", "fragment_tier": "ultimate", "supplies_delta": 1, "materials_delta": 2, "next_door_dc_delta": 0},
    {"outcome": "success", "fragment_tier": "advanced", "supplies_delta": 1, "materials_delta": 0, "next_door_dc_delta": 0},
    {"outcome": "fumble_with_supply", "fragment_tier": "", "supplies_delta": -1, "materials_delta": 0, "next_door_dc_delta": 0},
    {"outcome": "fumble_without_supply", "fragment_tier": "", "supplies_delta": 0, "materials_delta": 0, "next_door_dc_delta": 1},
)
SECT_ENCOUNTER_RULES = {row["outcome"]: row for row in SECT_ENCOUNTER_RULE_ROWS}


ITEM_ROWS = (
    {"item_id": "fragment_advanced", "item_type": "fragment", "tier": "advanced", "name_template": "{sect}中阶武学残页"},
    {"item_id": "fragment_ultimate", "item_type": "fragment", "tier": "ultimate", "name_template": "{sect}顶级绝学残页"},
    {"item_id": "clear_elixir", "item_type": "consumable", "tier": "rare", "name_template": "小还丹"},
)
ITEMS_BY_TIER = {row["tier"]: row for row in ITEM_ROWS if row["item_type"] == "fragment"}


MARTIAL_ART_EFFECT_ROWS = (
    {"effect_id": "huashan_yangqijue_high", "sect": "华山", "skill_name": "养气诀", "tier": "高阶", "upgrade_from_tier": "初阶", "upgrade_to_tier": "高阶", "trigger_timing": "post_combat", "effect_type": "hp_recovery", "effect_value": 6, "stackable": False, "description": "初阶升级后直接高阶；战斗结束脱战调息，固定回复6点HP。"},
)
MARTIAL_ART_EFFECTS = {row["skill_name"]: row for row in MARTIAL_ART_EFFECT_ROWS}


MARTIAL_ART_SKILL_ROWS = (
    {"skill_id": "huashan_kuangfeng_kuaijian", "sect": "华山", "name": "狂风快剑", "tier": "进阶", "category": "剑法", "obtain_source": "sect_encounter", "obtain_min_floor": 2, "exclusive_group": "huashan_advanced_sword", "ability": "dex", "attack_segments": 4, "damage_dice_count": 1, "damage_die": 4, "damage_bonus": 1, "damage_type": "劈砍", "mp_cost": 2, "damage_min": 8, "damage_max": 20, "damage_avg": 14.0, "description": "连绵不绝的快攻剑法；造成4段1d4+1劈砍伤害。"},
    {"skill_id": "huashan_duoming_lianhuan_sanxianjian", "sect": "华山", "name": "夺命连环三仙剑", "tier": "进阶", "category": "剑法", "obtain_source": "sect_encounter", "obtain_min_floor": 2, "exclusive_group": "huashan_advanced_sword", "ability": "dex", "attack_segments": 3, "damage_dice_count": 1, "damage_die": 6, "damage_bonus": 2, "damage_type": "穿刺", "mp_cost": 3, "damage_min": 9, "damage_max": 24, "damage_avg": 16.5, "description": "三招连环的华山高阶剑法；造成3段1d6+2穿刺伤害。"},
    {"skill_id": "shaolin_dajingangquan", "sect": "少林", "name": "大金刚拳", "tier": "进阶", "category": "拳掌", "obtain_source": "sect_encounter", "obtain_min_floor": 2, "exclusive_group": "shaolin_advanced", "ability": "str", "attack_segments": 2, "damage_dice_count": 1, "damage_die": 8, "damage_bonus": 2, "damage_type": "钝击", "mp_cost": 2, "damage_min": 6, "damage_max": 20, "damage_avg": 13.0, "description": "刚猛少林拳路；造成2段1d8+2钝击伤害。"},
    {"skill_id": "shaolin_jiashafumogong", "sect": "少林", "name": "袈裟伏魔功", "tier": "进阶", "category": "内功", "obtain_source": "sect_encounter", "obtain_min_floor": 2, "exclusive_group": "shaolin_advanced", "ability": "con", "attack_segments": 2, "damage_dice_count": 1, "damage_die": 6, "damage_bonus": 3, "damage_type": "钝击", "mp_cost": 2, "damage_min": 8, "damage_max": 18, "damage_avg": 13.0, "description": "伏魔内劲护体反震；造成2段1d6+3钝击伤害。"},
    {"skill_id": "wudang_raozhiroujian", "sect": "武当", "name": "绕指柔剑", "tier": "进阶", "category": "剑法", "obtain_source": "sect_encounter", "obtain_min_floor": 2, "exclusive_group": "wudang_advanced", "ability": "int", "attack_segments": 3, "damage_dice_count": 1, "damage_die": 6, "damage_bonus": 1, "damage_type": "劈砍", "mp_cost": 2, "damage_min": 6, "damage_max": 21, "damage_avg": 13.5, "description": "以柔克刚的连环剑势；造成3段1d6+1劈砍伤害。"},
    {"skill_id": "wudang_zhenshantiezhang", "sect": "武当", "name": "震山铁掌", "tier": "进阶", "category": "拳掌", "obtain_source": "sect_encounter", "obtain_min_floor": 2, "exclusive_group": "wudang_advanced", "ability": "wis", "attack_segments": 2, "damage_dice_count": 1, "damage_die": 8, "damage_bonus": 2, "damage_type": "钝击", "mp_cost": 2, "damage_min": 6, "damage_max": 20, "damage_avg": 13.0, "description": "太极劲蓄而后发；造成2段1d8+2钝击伤害。"},
    {"skill_id": "emei_jinding_mianzhang", "sect": "峨眉", "name": "金顶绵掌", "tier": "进阶", "category": "拳掌", "obtain_source": "sect_encounter", "obtain_min_floor": 2, "exclusive_group": "emei_advanced", "ability": "wis", "attack_segments": 2, "damage_dice_count": 1, "damage_die": 8, "damage_bonus": 2, "damage_type": "钝击", "mp_cost": 2, "damage_min": 6, "damage_max": 20, "damage_avg": 13.0, "description": "柔中带刚的峨眉掌法；造成2段1d8+2钝击伤害。"},
    {"skill_id": "emei_miejian_jueshi", "sect": "峨眉", "name": "灭剑绝式", "tier": "进阶", "category": "剑法", "obtain_source": "sect_encounter", "obtain_min_floor": 2, "exclusive_group": "emei_advanced", "ability": "dex", "attack_segments": 3, "damage_dice_count": 1, "damage_die": 6, "damage_bonus": 1, "damage_type": "穿刺", "mp_cost": 2, "damage_min": 6, "damage_max": 21, "damage_avg": 13.5, "description": "峨眉快剑杀招；造成3段1d6+1穿刺伤害。"},
    {"skill_id": "quanzhen_sanhuajudingzhang", "sect": "全真", "name": "三花聚顶掌", "tier": "进阶", "category": "拳掌", "obtain_source": "sect_encounter", "obtain_min_floor": 2, "exclusive_group": "quanzhen_advanced", "ability": "wis", "attack_segments": 2, "damage_dice_count": 1, "damage_die": 8, "damage_bonus": 2, "damage_type": "钝击", "mp_cost": 2, "damage_min": 6, "damage_max": 20, "damage_avg": 13.0, "description": "全真玄门掌力；造成2段1d8+2钝击伤害。"},
    {"skill_id": "quanzhen_qixingjianshi", "sect": "全真", "name": "七星剑式", "tier": "进阶", "category": "剑法", "obtain_source": "sect_encounter", "obtain_min_floor": 2, "exclusive_group": "quanzhen_advanced", "ability": "int", "attack_segments": 3, "damage_dice_count": 1, "damage_die": 6, "damage_bonus": 1, "damage_type": "劈砍", "mp_cost": 2, "damage_min": 6, "damage_max": 21, "damage_avg": 13.5, "description": "七星方位连刺斩击；造成3段1d6+1劈砍伤害。"},
    {"skill_id": "gaibang_kanglong_chushi", "sect": "丐帮", "name": "亢龙初式", "tier": "进阶", "category": "拳掌", "obtain_source": "sect_encounter", "obtain_min_floor": 2, "exclusive_group": "gaibang_advanced", "ability": "str", "attack_segments": 2, "damage_dice_count": 1, "damage_die": 10, "damage_bonus": 2, "damage_type": "钝击", "mp_cost": 3, "damage_min": 6, "damage_max": 24, "damage_avg": 15.0, "description": "降龙掌法中期过渡招；造成2段1d10+2钝击伤害。"},
    {"skill_id": "gaibang_chanzijue_bangfa", "sect": "丐帮", "name": "缠字诀棒法", "tier": "进阶", "category": "棍法", "obtain_source": "sect_encounter", "obtain_min_floor": 2, "exclusive_group": "gaibang_advanced", "ability": "dex", "attack_segments": 3, "damage_dice_count": 1, "damage_die": 6, "damage_bonus": 1, "damage_type": "钝击", "mp_cost": 2, "damage_min": 6, "damage_max": 21, "damage_avg": 13.5, "description": "打狗棒缠拿变化；造成3段1d6+1钝击伤害。"},
    {"skill_id": "mingjiao_lieyan_shenghuozhang", "sect": "明教", "name": "烈焰圣火掌", "tier": "进阶", "category": "拳掌", "obtain_source": "sect_encounter", "obtain_min_floor": 2, "exclusive_group": "mingjiao_advanced", "ability": "str", "attack_segments": 2, "damage_dice_count": 1, "damage_die": 8, "damage_bonus": 2, "damage_type": "灼烧", "mp_cost": 2, "damage_min": 6, "damage_max": 20, "damage_avg": 13.0, "description": "圣火外放灼敌；造成2段1d8+2灼烧伤害。"},
    {"skill_id": "mingjiao_qiankun_nuojin", "sect": "明教", "name": "乾坤挪劲", "tier": "进阶", "category": "内功", "obtain_source": "sect_encounter", "obtain_min_floor": 2, "exclusive_group": "mingjiao_advanced", "ability": "con", "attack_segments": 2, "damage_dice_count": 1, "damage_die": 6, "damage_bonus": 3, "damage_type": "钝击", "mp_cost": 2, "damage_min": 8, "damage_max": 18, "damage_avg": 13.0, "description": "挪移敌劲反击；造成2段1d6+3钝击伤害。"},
    {"skill_id": "qingcheng_songfeng_kuaijian", "sect": "青城", "name": "松风快剑", "tier": "进阶", "category": "剑法", "obtain_source": "sect_encounter", "obtain_min_floor": 2, "exclusive_group": "qingcheng_advanced", "ability": "dex", "attack_segments": 3, "damage_dice_count": 1, "damage_die": 6, "damage_bonus": 1, "damage_type": "穿刺", "mp_cost": 2, "damage_min": 6, "damage_max": 21, "damage_avg": 13.5, "description": "松风观快剑进阶；造成3段1d6+1穿刺伤害。"},
    {"skill_id": "qingcheng_cuixin_duzhang", "sect": "青城", "name": "摧心毒掌", "tier": "进阶", "category": "拳掌", "obtain_source": "sect_encounter", "obtain_min_floor": 2, "exclusive_group": "qingcheng_advanced", "ability": "int", "attack_segments": 2, "damage_dice_count": 1, "damage_die": 8, "damage_bonus": 2, "damage_type": "毒", "mp_cost": 2, "damage_min": 6, "damage_max": 20, "damage_avg": 13.0, "description": "催心掌毒劲进阶；造成2段1d8+2毒伤害。"},
    {"skill_id": "xueshan_xueying_lianhuanjian", "sect": "雪山派", "name": "雪影连环剑", "tier": "进阶", "category": "剑法", "obtain_source": "sect_encounter", "obtain_min_floor": 2, "exclusive_group": "xueshan_advanced", "ability": "str", "attack_segments": 3, "damage_dice_count": 1, "damage_die": 6, "damage_bonus": 1, "damage_type": "寒冰", "mp_cost": 2, "damage_min": 6, "damage_max": 21, "damage_avg": 13.5, "description": "雪山剑势连绵；造成3段1d6+1寒冰伤害。"},
    {"skill_id": "xueshan_bingpo_shenzhang", "sect": "雪山派", "name": "冰魄神掌", "tier": "进阶", "category": "拳掌", "obtain_source": "sect_encounter", "obtain_min_floor": 2, "exclusive_group": "xueshan_advanced", "ability": "con", "attack_segments": 2, "damage_dice_count": 1, "damage_die": 8, "damage_bonus": 2, "damage_type": "寒冰", "mp_cost": 2, "damage_min": 6, "damage_max": 20, "damage_avg": 13.0, "description": "寒劲凝掌；造成2段1d8+2寒冰伤害。"},
    {"skill_id": "dali_yiyangzhi_zhongjie", "sect": "大理段氏", "name": "一阳指中阶", "tier": "进阶", "category": "指法", "obtain_source": "sect_encounter", "obtain_min_floor": 2, "exclusive_group": "dali_advanced", "ability": "wis", "attack_segments": 2, "damage_dice_count": 1, "damage_die": 8, "damage_bonus": 2, "damage_type": "灼烧", "mp_cost": 2, "damage_min": 6, "damage_max": 20, "damage_avg": 13.0, "description": "一阳指力进阶；造成2段1d8+2灼烧伤害。"},
    {"skill_id": "dali_duanshi_lianhuanjian", "sect": "大理段氏", "name": "段氏连环剑", "tier": "进阶", "category": "剑法", "obtain_source": "sect_encounter", "obtain_min_floor": 2, "exclusive_group": "dali_advanced", "ability": "int", "attack_segments": 3, "damage_dice_count": 1, "damage_die": 6, "damage_bonus": 1, "damage_type": "穿刺", "mp_cost": 2, "damage_min": 6, "damage_max": 21, "damage_avg": 13.5, "description": "段家剑式连环递进；造成3段1d6+1穿刺伤害。"},
    {"skill_id": "xiaoyao_tianshan_liuyang_chuwu", "sect": "逍遥派", "name": "天山六阳掌初悟", "tier": "进阶", "category": "拳掌", "obtain_source": "sect_encounter", "obtain_min_floor": 2, "exclusive_group": "xiaoyao_advanced", "ability": "int", "attack_segments": 2, "damage_dice_count": 1, "damage_die": 8, "damage_bonus": 2, "damage_type": "钝击", "mp_cost": 2, "damage_min": 6, "damage_max": 20, "damage_avg": 13.0, "description": "逍遥掌力初成；造成2段1d8+2钝击伤害。"},
    {"skill_id": "xiaoyao_lingbo_cuoyingji", "sect": "逍遥派", "name": "凌波错影击", "tier": "进阶", "category": "身法", "obtain_source": "sect_encounter", "obtain_min_floor": 2, "exclusive_group": "xiaoyao_advanced", "ability": "dex", "attack_segments": 3, "damage_dice_count": 1, "damage_die": 6, "damage_bonus": 1, "damage_type": "钝击", "mp_cost": 2, "damage_min": 6, "damage_max": 21, "damage_avg": 13.5, "description": "凌波身法错位进击；造成3段1d6+1钝击伤害。"},
    {"skill_id": "jingang_dali_jingangzhi", "sect": "金刚宗", "name": "大力金刚指", "tier": "进阶", "category": "指法", "obtain_source": "sect_encounter", "obtain_min_floor": 2, "exclusive_group": "jingang_advanced", "ability": "str", "attack_segments": 2, "damage_dice_count": 1, "damage_die": 10, "damage_bonus": 2, "damage_type": "穿刺", "mp_cost": 3, "damage_min": 6, "damage_max": 24, "damage_avg": 15.0, "description": "金刚指力破甲；造成2段1d10+2穿刺伤害。"},
    {"skill_id": "jingang_chiyan_daoqi", "sect": "金刚宗", "name": "炽焰刀气", "tier": "进阶", "category": "刀法", "obtain_source": "sect_encounter", "obtain_min_floor": 2, "exclusive_group": "jingang_advanced", "ability": "con", "attack_segments": 2, "damage_dice_count": 1, "damage_die": 8, "damage_bonus": 2, "damage_type": "灼烧", "mp_cost": 2, "damage_min": 6, "damage_max": 20, "damage_avg": 13.0, "description": "火焰刀气进阶；造成2段1d8+2灼烧伤害。"},
    {"skill_id": "taohua_luoying_binfenzhang", "sect": "桃花岛", "name": "落英缤纷掌", "tier": "进阶", "category": "拳掌", "obtain_source": "sect_encounter", "obtain_min_floor": 2, "exclusive_group": "taohua_advanced", "ability": "int", "attack_segments": 3, "damage_dice_count": 1, "damage_die": 6, "damage_bonus": 1, "damage_type": "钝击", "mp_cost": 2, "damage_min": 6, "damage_max": 21, "damage_avg": 13.5, "description": "桃花岛掌影纷落；造成3段1d6+1钝击伤害。"},
    {"skill_id": "taohua_yuxiao_jianshi", "sect": "桃花岛", "name": "玉箫剑式", "tier": "进阶", "category": "剑法", "obtain_source": "sect_encounter", "obtain_min_floor": 2, "exclusive_group": "taohua_advanced", "ability": "dex", "attack_segments": 2, "damage_dice_count": 1, "damage_die": 8, "damage_bonus": 2, "damage_type": "穿刺", "mp_cost": 2, "damage_min": 6, "damage_max": 20, "damage_avg": 13.0, "description": "玉箫化剑的轻灵剑招；造成2段1d8+2穿刺伤害。"},
    {"skill_id": "riyue_kuihua_miyingci", "sect": "日月神教", "name": "葵花迷影刺", "tier": "进阶", "category": "身法", "obtain_source": "sect_encounter", "obtain_min_floor": 2, "exclusive_group": "riyue_advanced", "ability": "dex", "attack_segments": 4, "damage_dice_count": 1, "damage_die": 4, "damage_bonus": 1, "damage_type": "穿刺", "mp_cost": 2, "damage_min": 8, "damage_max": 20, "damage_avg": 14.0, "description": "葵花身法迷影连刺；造成4段1d4+1穿刺伤害。"},
    {"skill_id": "riyue_xixing_chanjin", "sect": "日月神教", "name": "吸星缠劲", "tier": "进阶", "category": "内功", "obtain_source": "sect_encounter", "obtain_min_floor": 2, "exclusive_group": "riyue_advanced", "ability": "str", "attack_segments": 2, "damage_dice_count": 1, "damage_die": 8, "damage_bonus": 2, "damage_type": "钝击", "mp_cost": 2, "damage_min": 6, "damage_max": 20, "damage_avg": 13.0, "description": "吸星内劲缠敌；造成2段1d8+2钝击伤害。"},
    {"skill_id": "xuedao_xuedao_lianzhan", "sect": "血刀门", "name": "血刀连斩", "tier": "进阶", "category": "刀法", "obtain_source": "sect_encounter", "obtain_min_floor": 2, "exclusive_group": "xuedao_advanced", "ability": "str", "attack_segments": 3, "damage_dice_count": 1, "damage_die": 6, "damage_bonus": 2, "damage_type": "劈砍", "mp_cost": 3, "damage_min": 9, "damage_max": 24, "damage_avg": 16.5, "description": "血刀门中期主攻刀路；造成3段1d6+2劈砍伤害。"},
    {"skill_id": "xuedao_xueying_zhuihun", "sect": "血刀门", "name": "血影追魂", "tier": "进阶", "category": "身法", "obtain_source": "sect_encounter", "obtain_min_floor": 2, "exclusive_group": "xuedao_advanced", "ability": "dex", "attack_segments": 4, "damage_dice_count": 1, "damage_die": 4, "damage_bonus": 1, "damage_type": "流血", "mp_cost": 2, "damage_min": 8, "damage_max": 20, "damage_avg": 14.0, "description": "血影贴身追击；造成4段1d4+1流血伤害。"},
    {"skill_id": "baituo_baituo_dushazhang", "sect": "白驼山庄", "name": "白驼毒砂掌", "tier": "进阶", "category": "拳掌", "obtain_source": "sect_encounter", "obtain_min_floor": 2, "exclusive_group": "baituo_advanced", "ability": "int", "attack_segments": 2, "damage_dice_count": 1, "damage_die": 8, "damage_bonus": 2, "damage_type": "毒", "mp_cost": 2, "damage_min": 6, "damage_max": 20, "damage_avg": 13.0, "description": "白驼毒掌进阶；造成2段1d8+2毒伤害。"},
    {"skill_id": "baituo_hama_tujin", "sect": "白驼山庄", "name": "蛤蟆吐劲", "tier": "进阶", "category": "内功", "obtain_source": "sect_encounter", "obtain_min_floor": 2, "exclusive_group": "baituo_advanced", "ability": "con", "attack_segments": 2, "damage_dice_count": 1, "damage_die": 10, "damage_bonus": 2, "damage_type": "毒", "mp_cost": 3, "damage_min": 6, "damage_max": 24, "damage_avg": 15.0, "description": "蛤蟆功外放毒劲；造成2段1d10+2毒伤害。"},
)
MARTIAL_ART_SKILLS = {row["skill_id"]: row for row in MARTIAL_ART_SKILL_ROWS}
MARTIAL_ART_SKILLS_BY_NAME = {row["name"]: row for row in MARTIAL_ART_SKILL_ROWS}


SKILL_COMBAT_ROWS = (
    {"name": "罗汉拳", "category": "拳掌", "damage_type": "钝击", "attack_segments": 1, "damage_dice_count": 1, "damage_die": 8, "damage_bonus": 2, "mp_cost": 0},
    {"name": "易筋经残篇", "category": "内功", "damage_type": "钝击", "attack_segments": 1, "damage_dice_count": 1, "damage_die": 6, "damage_bonus": 3, "mp_cost": 1},
    {"name": "太极拳", "category": "拳掌", "damage_type": "钝击", "attack_segments": 1, "damage_dice_count": 1, "damage_die": 6, "damage_bonus": 2, "mp_cost": 0},
    {"name": "太极剑", "category": "剑法", "damage_type": "劈砍", "attack_segments": 1, "damage_dice_count": 1, "damage_die": 8, "damage_bonus": 2, "mp_cost": 1},
    {"name": "峨眉剑法", "category": "剑法", "damage_type": "穿刺", "attack_segments": 1, "damage_dice_count": 1, "damage_die": 8, "damage_bonus": 1, "mp_cost": 0},
    {"name": "峨嵋九阳功", "category": "内功", "damage_type": "灼烧", "attack_segments": 1, "damage_dice_count": 1, "damage_die": 6, "damage_bonus": 3, "mp_cost": 1},
    {"name": "全真剑法", "category": "剑法", "damage_type": "劈砍", "attack_segments": 1, "damage_dice_count": 1, "damage_die": 8, "damage_bonus": 1, "mp_cost": 0},
    {"name": "先天功", "category": "内功", "damage_type": "钝击", "attack_segments": 1, "damage_dice_count": 1, "damage_die": 6, "damage_bonus": 3, "mp_cost": 1},
    {"name": "华山长拳", "category": "拳掌", "damage_type": "钝击", "attack_segments": 1, "damage_dice_count": 1, "damage_die": 6, "damage_bonus": 2, "mp_cost": 0},
    {"name": "华山剑法", "category": "剑法", "damage_type": "劈砍", "attack_segments": 1, "damage_dice_count": 1, "damage_die": 8, "damage_bonus": 2, "mp_cost": 1},
    {"name": "养气诀", "category": "内功", "damage_type": "钝击", "attack_segments": 1, "damage_dice_count": 1, "damage_die": 4, "damage_bonus": 2, "mp_cost": 0},
    {"name": "降龙十八掌基础式", "category": "拳掌", "damage_type": "钝击", "attack_segments": 1, "damage_dice_count": 1, "damage_die": 10, "damage_bonus": 2, "mp_cost": 1},
    {"name": "打狗棒法", "category": "棍法", "damage_type": "钝击", "attack_segments": 2, "damage_dice_count": 1, "damage_die": 4, "damage_bonus": 1, "mp_cost": 1},
    {"name": "乾坤大挪移残篇", "category": "内功", "damage_type": "钝击", "attack_segments": 1, "damage_dice_count": 1, "damage_die": 8, "damage_bonus": 2, "mp_cost": 1},
    {"name": "圣火令法", "category": "奇门", "damage_type": "灼烧", "attack_segments": 2, "damage_dice_count": 1, "damage_die": 4, "damage_bonus": 1, "mp_cost": 1},
    {"name": "青城剑法", "category": "剑法", "damage_type": "穿刺", "attack_segments": 1, "damage_dice_count": 1, "damage_die": 8, "damage_bonus": 1, "mp_cost": 0},
    {"name": "催心掌", "category": "拳掌", "damage_type": "毒", "attack_segments": 1, "damage_dice_count": 1, "damage_die": 8, "damage_bonus": 2, "mp_cost": 1},
    {"name": "雪山剑法", "category": "剑法", "damage_type": "寒冰", "attack_segments": 1, "damage_dice_count": 1, "damage_die": 8, "damage_bonus": 2, "mp_cost": 1},
    {"name": "寒冰神掌", "category": "拳掌", "damage_type": "寒冰", "attack_segments": 1, "damage_dice_count": 1, "damage_die": 8, "damage_bonus": 2, "mp_cost": 1},
    {"name": "一阳指初阶", "category": "指法", "damage_type": "灼烧", "attack_segments": 1, "damage_dice_count": 1, "damage_die": 8, "damage_bonus": 2, "mp_cost": 1},
    {"name": "段家剑法", "category": "剑法", "damage_type": "穿刺", "attack_segments": 1, "damage_dice_count": 1, "damage_die": 8, "damage_bonus": 1, "mp_cost": 0},
    {"name": "段氏吐纳法", "category": "内功", "damage_type": "钝击", "attack_segments": 1, "damage_dice_count": 1, "damage_die": 4, "damage_bonus": 3, "mp_cost": 0},
    {"name": "天山折梅手", "category": "拳掌", "damage_type": "钝击", "attack_segments": 2, "damage_dice_count": 1, "damage_die": 4, "damage_bonus": 1, "mp_cost": 1},
    {"name": "北冥吐纳法", "category": "内功", "damage_type": "钝击", "attack_segments": 1, "damage_dice_count": 1, "damage_die": 4, "damage_bonus": 3, "mp_cost": 0},
    {"name": "凌波微步初阶", "category": "身法", "damage_type": "钝击", "attack_segments": 1, "damage_dice_count": 1, "damage_die": 6, "damage_bonus": 2, "mp_cost": 0},
    {"name": "金刚拳初阶", "category": "拳掌", "damage_type": "钝击", "attack_segments": 1, "damage_dice_count": 1, "damage_die": 10, "damage_bonus": 2, "mp_cost": 1},
    {"name": "火焰刀初阶", "category": "刀法", "damage_type": "灼烧", "attack_segments": 1, "damage_dice_count": 1, "damage_die": 10, "damage_bonus": 1, "mp_cost": 1},
    {"name": "落英神剑掌", "category": "拳掌", "damage_type": "钝击", "attack_segments": 2, "damage_dice_count": 1, "damage_die": 4, "damage_bonus": 1, "mp_cost": 1},
    {"name": "弹指神通", "category": "指法", "damage_type": "穿刺", "attack_segments": 1, "damage_dice_count": 1, "damage_die": 8, "damage_bonus": 2, "mp_cost": 1},
    {"name": "葵花宝典残篇", "category": "身法", "damage_type": "穿刺", "attack_segments": 2, "damage_dice_count": 1, "damage_die": 4, "damage_bonus": 2, "mp_cost": 1},
    {"name": "吸星大法", "category": "内功", "damage_type": "钝击", "attack_segments": 1, "damage_dice_count": 1, "damage_die": 8, "damage_bonus": 1, "mp_cost": 1},
    {"name": "血刀刀法初阶", "category": "刀法", "damage_type": "劈砍", "attack_segments": 1, "damage_dice_count": 1, "damage_die": 10, "damage_bonus": 2, "mp_cost": 1},
    {"name": "嗜血心法", "category": "内功", "damage_type": "流血", "attack_segments": 1, "damage_dice_count": 1, "damage_die": 6, "damage_bonus": 3, "mp_cost": 1},
    {"name": "血洗山河", "category": "刀法", "damage_type": "劈砍", "attack_segments": 2, "damage_dice_count": 1, "damage_die": 6, "damage_bonus": 1, "mp_cost": 2},
    {"name": "白驼蛇毒掌", "category": "拳掌", "damage_type": "毒", "attack_segments": 1, "damage_dice_count": 1, "damage_die": 8, "damage_bonus": 2, "mp_cost": 1},
    {"name": "蛤蟆功初阶", "category": "内功", "damage_type": "毒", "attack_segments": 1, "damage_dice_count": 1, "damage_die": 10, "damage_bonus": 1, "mp_cost": 1},
    {"name": "狂风快剑", "category": "剑法", "damage_type": "劈砍", "attack_segments": 4, "damage_dice_count": 1, "damage_die": 4, "damage_bonus": 1, "mp_cost": 2},
    {"name": "夺命连环三仙剑", "category": "剑法", "damage_type": "穿刺", "attack_segments": 3, "damage_dice_count": 1, "damage_die": 6, "damage_bonus": 2, "mp_cost": 3},
)
SKILL_COMBAT_BY_NAME = {row["name"]: row for row in SKILL_COMBAT_ROWS}


STATUS_ROWS = (
    {"status_id": "slow", "name": "迟滞", "duration_doors": 1, "dc_delta": -1, "damage_dice": "", "description": "下一次事件门DC-1。"},
    {"status_id": "burn", "name": "灼烧", "duration_doors": 1, "dc_delta": 0, "damage_dice": "1d4", "description": "下次进门前承受1d4伤害。"},
    {"status_id": "poison", "name": "中毒", "duration_doors": 1, "dc_delta": 0, "damage_dice": "1d4", "description": "下次进门前承受1d4毒伤。"},
    {"status_id": "bleed", "name": "流血", "duration_doors": 1, "dc_delta": 0, "damage_dice": "1d4", "description": "下次进门前承受1d4伤害。"},
)
STATUS_EFFECTS = {row["status_id"]: row for row in STATUS_ROWS}


EQUIPMENT_ROWS = (
    {"item_id": "iron_sword", "name": "精铁长剑", "slot": "weapon", "rarity": "common", "stack_size": 1, "slot_size": 1, "attack_bonus": 1, "damage_bonus": 1, "ac_bonus": 0, "max_hp_bonus": 0, "min_floor": 1},
    {"item_id": "bamboo_staff", "name": "青竹杖", "slot": "weapon", "rarity": "common", "stack_size": 1, "slot_size": 1, "attack_bonus": 1, "damage_bonus": 1, "ac_bonus": 0, "max_hp_bonus": 0, "min_floor": 1},
    {"item_id": "greensteel_sword", "name": "青钢剑", "slot": "weapon", "rarity": "common", "stack_size": 1, "slot_size": 1, "attack_bonus": 1, "damage_bonus": 2, "ac_bonus": 0, "max_hp_bonus": 0, "min_floor": 1},
    {"item_id": "iron_staff", "name": "精铁禅杖", "slot": "weapon", "rarity": "common", "stack_size": 1, "slot_size": 2, "attack_bonus": 1, "damage_bonus": 2, "ac_bonus": 0, "max_hp_bonus": 0, "min_floor": 1},
    {"item_id": "beggar_gourd", "name": "朱漆酒葫芦", "slot": "accessory", "rarity": "common", "stack_size": 1, "slot_size": 1, "attack_bonus": 0, "damage_bonus": 0, "ac_bonus": 0, "max_hp_bonus": 2, "min_floor": 1},
    {"item_id": "soft_armor", "name": "软猬内甲仿品", "slot": "armor", "rarity": "uncommon", "stack_size": 1, "slot_size": 2, "attack_bonus": 0, "damage_bonus": 0, "ac_bonus": 1, "max_hp_bonus": 2, "min_floor": 2},
    {"item_id": "hero_cloak", "name": "侠士披风", "slot": "armor", "rarity": "uncommon", "stack_size": 1, "slot_size": 2, "attack_bonus": 0, "damage_bonus": 0, "ac_bonus": 1, "max_hp_bonus": 0, "min_floor": 2},
    {"item_id": "chain_vest", "name": "锁子软甲", "slot": "armor", "rarity": "uncommon", "stack_size": 1, "slot_size": 2, "attack_bonus": 0, "damage_bonus": 0, "ac_bonus": 2, "max_hp_bonus": 0, "min_floor": 2},
    {"item_id": "tiger_claw_gloves", "name": "虎爪护手", "slot": "weapon", "rarity": "uncommon", "stack_size": 1, "slot_size": 1, "attack_bonus": 1, "damage_bonus": 3, "ac_bonus": 0, "max_hp_bonus": 0, "min_floor": 2},
    {"item_id": "silver_needles", "name": "银针匣", "slot": "weapon", "rarity": "uncommon", "stack_size": 1, "slot_size": 1, "attack_bonus": 2, "damage_bonus": 1, "ac_bonus": 0, "max_hp_bonus": 0, "min_floor": 2},
    {"item_id": "poison_sachet", "name": "避毒香囊", "slot": "accessory", "rarity": "uncommon", "stack_size": 1, "slot_size": 1, "attack_bonus": 0, "damage_bonus": 1, "ac_bonus": 0, "max_hp_bonus": 2, "min_floor": 2},
    {"item_id": "jade_pendant", "name": "温玉佩", "slot": "accessory", "rarity": "rare", "stack_size": 1, "slot_size": 1, "attack_bonus": 0, "damage_bonus": 0, "ac_bonus": 0, "max_hp_bonus": 4, "min_floor": 3},
    {"item_id": "sword_tassel", "name": "紫绶剑穗", "slot": "accessory", "rarity": "rare", "stack_size": 1, "slot_size": 1, "attack_bonus": 1, "damage_bonus": 1, "ac_bonus": 0, "max_hp_bonus": 0, "min_floor": 3},
    {"item_id": "jade_flute", "name": "碧玉箫", "slot": "accessory", "rarity": "rare", "stack_size": 1, "slot_size": 1, "attack_bonus": 1, "damage_bonus": 0, "ac_bonus": 1, "max_hp_bonus": 0, "min_floor": 3},
    {"item_id": "purple_gold_belt", "name": "紫金束带", "slot": "accessory", "rarity": "rare", "stack_size": 1, "slot_size": 1, "attack_bonus": 0, "damage_bonus": 1, "ac_bonus": 1, "max_hp_bonus": 2, "min_floor": 3},
    {"item_id": "snow_silk_robe", "name": "雪蚕袍", "slot": "armor", "rarity": "rare", "stack_size": 1, "slot_size": 2, "attack_bonus": 0, "damage_bonus": 0, "ac_bonus": 2, "max_hp_bonus": 2, "min_floor": 4},
    {"item_id": "golden_thread_vest", "name": "金丝背心", "slot": "armor", "rarity": "rare", "stack_size": 1, "slot_size": 2, "attack_bonus": 0, "damage_bonus": 0, "ac_bonus": 1, "max_hp_bonus": 6, "min_floor": 4},
    {"item_id": "cold_iron_sword", "name": "寒铁剑", "slot": "weapon", "rarity": "rare", "stack_size": 1, "slot_size": 1, "attack_bonus": 2, "damage_bonus": 2, "ac_bonus": 0, "max_hp_bonus": 0, "min_floor": 4},
    {"item_id": "blood_blade", "name": "血纹戒刀", "slot": "weapon", "rarity": "rare", "stack_size": 1, "slot_size": 1, "attack_bonus": 1, "damage_bonus": 4, "ac_bonus": 0, "max_hp_bonus": 0, "min_floor": 4},
    {"item_id": "black_iron_blade", "name": "玄铁短刃", "slot": "weapon", "rarity": "epic", "stack_size": 1, "slot_size": 1, "attack_bonus": 2, "damage_bonus": 2, "ac_bonus": 0, "max_hp_bonus": 0, "min_floor": 5},
    {"item_id": "black_iron_gauntlet", "name": "玄铁护腕", "slot": "accessory", "rarity": "epic", "stack_size": 1, "slot_size": 1, "attack_bonus": 1, "damage_bonus": 2, "ac_bonus": 0, "max_hp_bonus": 2, "min_floor": 5},
    {"item_id": "dragon_scale_token", "name": "龙纹令佩", "slot": "accessory", "rarity": "epic", "stack_size": 1, "slot_size": 1, "attack_bonus": 0, "damage_bonus": 1, "ac_bonus": 1, "max_hp_bonus": 4, "min_floor": 5},
    {"item_id": "soft_gold_armor", "name": "软金甲", "slot": "armor", "rarity": "epic", "stack_size": 1, "slot_size": 2, "attack_bonus": 0, "damage_bonus": 0, "ac_bonus": 3, "max_hp_bonus": 4, "min_floor": 5},
    {"item_id": "gentleman_sword", "name": "君子剑", "slot": "weapon", "rarity": "epic", "stack_size": 1, "slot_size": 1, "attack_bonus": 3, "damage_bonus": 2, "ac_bonus": 0, "max_hp_bonus": 0, "min_floor": 5},
    {"item_id": "lady_sword", "name": "淑女剑", "slot": "weapon", "rarity": "epic", "stack_size": 1, "slot_size": 1, "attack_bonus": 2, "damage_bonus": 3, "ac_bonus": 0, "max_hp_bonus": 0, "min_floor": 5},
    {"item_id": "black_iron_heavy_sword", "name": "玄铁重剑仿品", "slot": "weapon", "rarity": "legendary", "stack_size": 1, "slot_size": 2, "attack_bonus": 2, "damage_bonus": 6, "ac_bonus": 0, "max_hp_bonus": 0, "min_floor": 6},
    {"item_id": "nine_sun_jade", "name": "九阳暖玉", "slot": "accessory", "rarity": "legendary", "stack_size": 1, "slot_size": 1, "attack_bonus": 1, "damage_bonus": 1, "ac_bonus": 1, "max_hp_bonus": 8, "min_floor": 6},
)
EQUIPMENT_BY_ID = {row["item_id"]: row for row in EQUIPMENT_ROWS}
EQUIPMENT_BY_NAME = {row["name"]: row for row in EQUIPMENT_ROWS}


BOSS_ROWS = (
    {"boss_id": "wushen_mirror", "name": "武神镜像", "floor": 7, "hp": 70, "ac": 19, "check_dc": 18, "fail_damage_dice": "1d11+11", "ultimate_drop_chance": 10},
)
BOSSES = {row["boss_id"]: row for row in BOSS_ROWS}


BOSS_CLEAR_REWARD_ROWS = (
    {"difficulty": "普通", "essence": 2, "scrolls": 5, "elixir": 5, "silver": 100},
    {"difficulty": "困难", "essence": 4, "scrolls": 10, "elixir": 5, "silver": 100},
)
BOSS_CLEAR_REWARDS = {row["difficulty"]: row for row in BOSS_CLEAR_REWARD_ROWS}


BACKPACK_ROWS = (
    {"bag_id": "cloth_travel_bundle", "name": "青布行囊", "capacity_slots": 20, "price": 0, "rarity": "common", "description": "开局默认行囊，容量20格。"},
    {"bag_id": "leather_baina_pouch", "name": "牛皮百纳囊", "capacity_slots": 32, "price": 180, "rarity": "uncommon", "description": "江湖游商常备背囊，容量32格。"},
    {"bag_id": "brocade_qiankun_pouch", "name": "锦缎乾坤囊", "capacity_slots": 50, "price": 480, "rarity": "rare", "description": "名门侠士常用背囊，容量50格。"},
    {"bag_id": "qiankun_yiqi_bag", "name": "乾坤一气袋", "capacity_slots": 100, "price": 1200, "rarity": "legendary", "description": "极罕有奇物背囊，容量100格。"},
)
BACKPACKS = {row["bag_id"]: row for row in BACKPACK_ROWS}
BACKPACKS_BY_NAME = {row["name"]: row for row in BACKPACK_ROWS}


META_UPGRADE_ROWS = (
    {"upgrade_id": "fishing_preparation", "label": "渔隐行装", "level": 0, "carry_bait_id": "dragon_musk", "carry_bait_qty": 0, "fishing_quality_bonus": 0, "initial_backpack_bonus": 0, "essence_cost": 0, "scroll_cost": 0, "description": "未强化。"},
    {"upgrade_id": "fishing_preparation", "label": "渔隐行装", "level": 1, "carry_bait_id": "dragon_musk", "carry_bait_qty": 1, "fishing_quality_bonus": 10, "initial_backpack_bonus": 0, "essence_cost": 2, "scroll_cost": 5, "description": "出门携带龙涎香饵×1，钓鱼品质修正+10。"},
    {"upgrade_id": "fishing_preparation", "label": "渔隐行装", "level": 2, "carry_bait_id": "dragon_musk", "carry_bait_qty": 3, "fishing_quality_bonus": 30, "initial_backpack_bonus": 0, "essence_cost": 4, "scroll_cost": 10, "description": "出门携带龙涎香饵×3，钓鱼品质修正+30。"},
    {"upgrade_id": "fishing_preparation", "label": "渔隐行装", "level": 3, "carry_bait_id": "dragon_musk", "carry_bait_qty": 5, "fishing_quality_bonus": 50, "initial_backpack_bonus": 0, "essence_cost": 6, "scroll_cost": 15, "description": "出门携带龙涎香饵×5，钓鱼品质修正+50。"},
    {"upgrade_id": "backpack_foundation", "label": "百纳行囊术", "level": 0, "carry_bait_id": "", "carry_bait_qty": 0, "fishing_quality_bonus": 0, "initial_backpack_bonus": 0, "essence_cost": 0, "scroll_cost": 0, "description": "未强化。"},
    {"upgrade_id": "backpack_foundation", "label": "百纳行囊术", "level": 1, "carry_bait_id": "", "carry_bait_qty": 0, "fishing_quality_bonus": 0, "initial_backpack_bonus": 4, "essence_cost": 2, "scroll_cost": 5, "description": "青布行囊初始容量+4格。"},
    {"upgrade_id": "backpack_foundation", "label": "百纳行囊术", "level": 2, "carry_bait_id": "", "carry_bait_qty": 0, "fishing_quality_bonus": 0, "initial_backpack_bonus": 8, "essence_cost": 4, "scroll_cost": 10, "description": "青布行囊初始容量+8格。"},
    {"upgrade_id": "backpack_foundation", "label": "百纳行囊术", "level": 3, "carry_bait_id": "", "carry_bait_qty": 0, "fishing_quality_bonus": 0, "initial_backpack_bonus": 12, "essence_cost": 6, "scroll_cost": 15, "description": "青布行囊初始容量+12格。"},
    {"upgrade_id": "starting_silver", "label": "行侠盘缠", "level": 0, "starting_silver_bonus": 0, "essence_cost": 0, "scroll_cost": 0, "description": "未强化。"},
    {"upgrade_id": "starting_silver", "label": "行侠盘缠", "level": 1, "starting_silver_bonus": 20, "essence_cost": 1, "scroll_cost": 3, "description": "新局开局碎银+20两。"},
    {"upgrade_id": "starting_silver", "label": "行侠盘缠", "level": 2, "starting_silver_bonus": 50, "essence_cost": 3, "scroll_cost": 8, "description": "新局开局碎银+50两。"},
    {"upgrade_id": "starting_silver", "label": "行侠盘缠", "level": 3, "starting_silver_bonus": 90, "essence_cost": 5, "scroll_cost": 12, "description": "新局开局碎银+90两。"},
    {"upgrade_id": "starting_vigor", "label": "护体真气", "level": 0, "max_hp_bonus": 0, "essence_cost": 0, "scroll_cost": 0, "description": "未强化。"},
    {"upgrade_id": "starting_vigor", "label": "护体真气", "level": 1, "max_hp_bonus": 3, "essence_cost": 1, "scroll_cost": 3, "description": "新局开局HP上限+3。"},
    {"upgrade_id": "starting_vigor", "label": "护体真气", "level": 2, "max_hp_bonus": 6, "essence_cost": 3, "scroll_cost": 8, "description": "新局开局HP上限+6。"},
    {"upgrade_id": "starting_vigor", "label": "护体真气", "level": 3, "max_hp_bonus": 10, "essence_cost": 5, "scroll_cost": 12, "description": "新局开局HP上限+10。"},
)
META_UPGRADE_ORDER = ("fishing_preparation", "backpack_foundation", "starting_silver", "starting_vigor")
META_UPGRADES = {
    upgrade_id: {int(row["level"]): row for row in META_UPGRADE_ROWS if row["upgrade_id"] == upgrade_id}
    for upgrade_id in {row["upgrade_id"] for row in META_UPGRADE_ROWS}
}
META_UPGRADE_ALIASES = {
    "钓鱼": "fishing_preparation",
    "渔隐行装": "fishing_preparation",
    "背包": "backpack_foundation",
    "背囊": "backpack_foundation",
    "百纳行囊术": "backpack_foundation",
    "盘缠": "starting_silver",
    "碎银": "starting_silver",
    "行侠盘缠": "starting_silver",
    "气血": "starting_vigor",
    "护体": "starting_vigor",
    "护体真气": "starting_vigor",
}


INVENTORY_POLICY_ROWS = (
    {"category": "currency", "examples": "碎银", "in_bag": False, "slot_rule": "货币不占背包格"},
    {"category": "progression", "examples": "武学素材、武道真髓、武学残卷、武学残页", "in_bag": False, "slot_rule": "进度资源不占背包格"},
    {"category": "abstract_supply", "examples": "补给、小还丹", "in_bag": False, "slot_rule": "旧规则抽象补给不占背包格"},
    {"category": "fish_consumable", "examples": "鱼获消耗品", "in_bag": True, "slot_rule": "按stack_size堆叠，占用ceil(quantity/stack_size)*slot_size格"},
    {"category": "backpack", "examples": "青布行囊、牛皮百纳囊、锦缎乾坤囊、乾坤一气袋", "in_bag": False, "slot_rule": "已装备背囊不占自身格数"},
)


FISHING_POOL_ROWS = (
    {"pool_id": "floor_stream", "name": "本层山涧鱼池", "tier": "common", "min_floor": 1, "max_floor": 6, "spawn_rule": "default", "spawn_chance_percent": 100, "loot_roll_bonus": 0, "advantage_rolls": 1, "description": "普通楼层默认鱼池。"},
    {"pool_id": "hidden_cold_pool", "name": "隐秘寒潭鱼池", "tier": "advanced", "min_floor": 1, "max_floor": 6, "spawn_rule": "low_chance", "spawn_chance_percent": 12, "loot_roll_bonus": 15, "advantage_rolls": 2, "description": "每层低概率发现的高级鱼池，d100鱼获判定取优势并获得+15品质修正。"},
    {"pool_id": "wushen_dragon_pool", "name": "武神殿门前龙池", "tier": "legendary", "min_floor": 7, "max_floor": 7, "spawn_rule": "guaranteed", "spawn_chance_percent": 100, "loot_roll_bonus": 25, "advantage_rolls": 2, "description": "第7层Boss门口必定出现的高级鱼池，d100鱼获判定取优势并获得+25品质修正。"},
)
FISHING_POOLS = {row["pool_id"]: row for row in FISHING_POOL_ROWS}


BAIT_ROWS = (
    {"bait_id": "worm", "name": "普通蚯蚓饵", "price": 10, "loot_roll_bonus": 0, "advantage_rolls": 1, "description": "基础钓饵，不提供品质修正。"},
    {"bait_id": "spiced", "name": "秘制香饵", "price": 30, "loot_roll_bonus": 8, "advantage_rolls": 1, "description": "稳定提升鱼获品质，d100鱼获判定获得+8品质修正。"},
    {"bait_id": "dragon_musk", "name": "龙涎香饵", "price": 100, "loot_roll_bonus": 15, "advantage_rolls": 2, "description": "高阶钓饵，d100鱼获判定取优势并获得+15品质修正。"},
)
BAITS = {row["name"]: row for row in BAIT_ROWS}


FISH_CONSUMABLE_ROWS = (
    {"item_id": "river_carp", "name": "青鳞溪鲤", "rarity": "common", "item_type": "fish_consumable", "stack_size": 5, "slot_size": 1, "droppable": True, "usable": True, "effect_type": "hp_recovery", "effect_dice": "1d6", "effect_value": 2, "duration": "instant", "description": "食用后回复1d6+2点HP。"},
    {"item_id": "silver_fin_carp", "name": "银鳍灵鲤", "rarity": "uncommon", "item_type": "fish_consumable", "stack_size": 5, "slot_size": 1, "droppable": True, "usable": True, "effect_type": "mp_recovery", "effect_dice": "1d4", "effect_value": 2, "duration": "instant", "description": "食用后回复1d4+2点MP。"},
    {"item_id": "cold_jade_perch", "name": "寒潭玉鲈", "rarity": "rare", "item_type": "fish_consumable", "stack_size": 3, "slot_size": 1, "droppable": True, "usable": True, "effect_type": "temp_hp", "effect_dice": "1d8", "effect_value": 4, "duration": "next_battle", "description": "食用后获得1d8+4点临时HP。"},
    {"item_id": "ironbone_catfish", "name": "铁骨鲶", "rarity": "epic", "item_type": "fish_consumable", "stack_size": 2, "slot_size": 1, "droppable": True, "usable": True, "effect_type": "next_d20_bonus", "effect_dice": "", "effect_value": 2, "duration": "next_check", "description": "食用后下一次d20检定获得+2加值。"},
    {"item_id": "dragon_whisker_fish", "name": "龙须金鳞鱼", "rarity": "legendary", "item_type": "fish_consumable", "stack_size": 1, "slot_size": 1, "droppable": True, "usable": True, "effect_type": "hp_recovery", "effect_dice": "2d8", "effect_value": 8, "duration": "instant", "description": "食用后回复2d8+8点HP。"},
)
FISH_CONSUMABLES = {row["item_id"]: row for row in FISH_CONSUMABLE_ROWS}
FISH_CONSUMABLES_BY_NAME = {row["name"]: row for row in FISH_CONSUMABLE_ROWS}


FISHING_LOOT_ROWS = (
    {"loot_tier": "legendary", "roll_min": 1, "roll_max": 3, "item_id": "dragon_whisker_fish", "quantity": 1},
    {"loot_tier": "epic", "roll_min": 4, "roll_max": 10, "item_id": "ironbone_catfish", "quantity": 1},
    {"loot_tier": "rare", "roll_min": 11, "roll_max": 25, "item_id": "cold_jade_perch", "quantity": 1},
    {"loot_tier": "uncommon", "roll_min": 26, "roll_max": 45, "item_id": "silver_fin_carp", "quantity": 1},
    {"loot_tier": "common", "roll_min": 46, "roll_max": 100, "item_id": "river_carp", "quantity": 1},
)
