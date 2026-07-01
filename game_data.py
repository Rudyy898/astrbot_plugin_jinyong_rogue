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
    {"key": "starting_medicine", "value": 2},
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
    {"event_id": "chest", "success_silver_dice": "1d19+11", "success_silver_per_floor": 3, "success_medicine": 1, "fumble_damage_dice": "1d6+2"},
    {"event_id": "encounter", "success_materials": 2, "success_mp_recovery": 2},
    {"event_id": "trap", "success_silver": 10, "fail_damage_dice": "1d8+4"},
    {"event_id": "merchant", "base_cost": 20, "success_discount": 10, "min_cost": 8, "buy_medicine": 2, "backpack_discount_percent_success": 10},
)
ENCOUNTER_RULES = {row["event_id"]: row for row in ENCOUNTER_RULE_ROWS}


SECT_ENCOUNTER_RULE_ROWS = (
    {"outcome": "crit", "fragment_tier": "ultimate", "medicine_delta": 1, "materials_delta": 2, "next_door_dc_delta": 0},
    {"outcome": "success", "fragment_tier": "advanced", "medicine_delta": 1, "materials_delta": 0, "next_door_dc_delta": 0},
    {"outcome": "fumble_with_medicine", "fragment_tier": "", "medicine_delta": -1, "materials_delta": 0, "next_door_dc_delta": 0},
    {"outcome": "fumble_without_medicine", "fragment_tier": "", "medicine_delta": 0, "materials_delta": 0, "next_door_dc_delta": 1},
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


ENEMY_ROWS = (
    {"enemy_id": "tower_guard_1", "name": "守塔武师", "floor": 1, "hp": 18, "ac": 12, "attack_bonus": 2, "damage_dice": "1d6+1", "damage_type": "钝击", "desc": "第一层守塔弟子，武艺平平但意志坚定。"},
    {"enemy_id": "tower_guard_2", "name": "护院教头", "floor": 2, "hp": 24, "ac": 13, "attack_bonus": 3, "damage_dice": "1d6+2", "damage_type": "钝击", "desc": "第二层护院教头，一手铁布衫已有小成。"},
    {"enemy_id": "tower_guard_3", "name": "铜人僧", "floor": 3, "hp": 30, "ac": 14, "attack_bonus": 3, "damage_dice": "1d8+2", "damage_type": "钝击", "desc": "第三层金刚铜人，拳拳到肉，刚猛无俦。"},
    {"enemy_id": "tower_guard_4", "name": "飞剑客", "floor": 4, "hp": 28, "ac": 15, "attack_bonus": 4, "damage_dice": "1d6+3", "damage_type": "穿刺", "desc": "第四层飞剑客，出手快如闪电，剑未到气先至。"},
    {"enemy_id": "tower_guard_5", "name": "毒砂掌客", "floor": 5, "hp": 35, "ac": 14, "attack_bonus": 4, "damage_dice": "1d8+2", "damage_type": "毒", "desc": "第五层毒道高手，掌风含毒，触之即伤。"},
    {"enemy_id": "tower_guard_6", "name": "修罗刀使", "floor": 6, "hp": 42, "ac": 16, "attack_bonus": 5, "damage_dice": "1d10+3", "damage_type": "劈砍", "desc": "第六层修罗刀使，刀法狠辣，每一击皆有进无退。"},
)
ENEMIES = {row["enemy_id"]: row for row in ENEMY_ROWS}
ENEMIES_BY_FLOOR = {}
for row in ENEMY_ROWS:
    ENEMIES_BY_FLOOR.setdefault(row["floor"], []).append(row)

BOSS_ROWS = (
    {"boss_id": "wushen_mirror", "name": "武神镜像", "floor": 7, "hp": 70, "ac": 19, "attack_bonus": 7, "damage_dice": "1d12+5", "damage_type": "钝击", "check_dc": 18, "fail_damage_dice": "1d11+11", "ultimate_drop_chance": 10, "desc": "武道极致的投影，集百家武学于一身的终极试炼。"},
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
    {"category": "medicine_consumable", "examples": "金疮药、小还丹", "in_bag": True, "slot_rule": "药品消耗品进入背囊，可用 /金庸使用 药品名"},
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
    {"bait_id": "worm", "name": "普通蚯蚓饵", "price": 0, "loot_roll_bonus": 0, "advantage_rolls": 1, "description": "基础钓饵，不消耗碎银，不提供品质修正。"},
    {"bait_id": "spiced", "name": "秘制香饵", "price": 0, "loot_roll_bonus": 8, "advantage_rolls": 1, "description": "稳定提升鱼获品质，d100鱼获判定获得+8品质修正。"},
    {"bait_id": "dragon_musk", "name": "龙涎香饵", "price": 0, "loot_roll_bonus": 15, "advantage_rolls": 2, "description": "高阶钓饵，d100鱼获判定取优势并获得+15品质修正。"},
)
BAITS = {row["name"]: row for row in BAIT_ROWS}


FISH_CONSUMABLE_ROWS = (
    {"item_id": "river_carp", "name": "青鳞溪鲤", "rarity": "common", "item_type": "fish_consumable", "stack_size": 5, "slot_size": 1, "droppable": True, "usable": True, "effect_type": "hp_recovery", "effect_dice": "1d6", "effect_value": 2, "duration": "instant", "description": "溪水灵气养出的青鳞鲤，肉质温润，食用后回复1d6+2点HP。"},
    {"item_id": "silver_fin_carp", "name": "银鳍灵鲤", "rarity": "uncommon", "item_type": "fish_consumable", "stack_size": 5, "slot_size": 1, "droppable": True, "usable": True, "effect_type": "mp_recovery", "effect_dice": "1d4", "effect_value": 2, "duration": "instant", "description": "银鳍上凝着淡淡月华，入口清凉，食用后回复1d4+2点MP。"},
    {"item_id": "cold_jade_perch", "name": "寒潭玉鲈", "rarity": "rare", "item_type": "fish_consumable", "stack_size": 3, "slot_size": 1, "droppable": True, "usable": True, "effect_type": "temp_hp", "effect_dice": "1d8", "effect_value": 4, "duration": "next_battle", "description": "寒潭深处的玉色灵鱼，鱼肉蕴着护体寒劲，食用后获得1d8+4点临时HP。"},
    {"item_id": "ironbone_catfish", "name": "铁骨鲶", "rarity": "epic", "item_type": "fish_consumable", "stack_size": 2, "slot_size": 1, "droppable": True, "usable": True, "effect_type": "next_d20_bonus", "effect_dice": "", "effect_value": 2, "duration": "next_check", "description": "鱼骨坚如精铁，嚼下后筋骨微热，下一次d20检定获得+2加值。"},
    {"item_id": "dragon_whisker_fish", "name": "龙须金鳞鱼", "rarity": "legendary", "item_type": "fish_consumable", "stack_size": 1, "slot_size": 1, "droppable": True, "usable": True, "effect_type": "hp_recovery", "effect_dice": "2d8", "effect_value": 8, "duration": "instant", "description": "金鳞如火、龙须微动的奇鱼，食用后真气奔涌，回复2d8+8点HP。"},
)
FISH_CONSUMABLES = {row["item_id"]: row for row in FISH_CONSUMABLE_ROWS}
FISH_CONSUMABLES_BY_NAME = {row["name"]: row for row in FISH_CONSUMABLE_ROWS}


MEDICINE_CONSUMABLE_ROWS = (
    {"item_id": "jinchuang_ointment", "name": "金疮药", "rarity": "common", "item_type": "medicine_consumable", "stack_size": 5, "slot_size": 1, "droppable": True, "usable": True, "effect_type": "hp_recovery", "effect_dice": "1d8", "effect_value": 4, "duration": "instant", "description": "江湖行走必备的外伤药，敷上后止血生肌，回复1d8+4点HP。"},
    {"item_id": "shaolin_small_elixir", "name": "小还丹", "rarity": "rare", "item_type": "medicine_consumable", "stack_size": 3, "slot_size": 1, "droppable": True, "usable": True, "effect_type": "hp_recovery", "effect_dice": "2d6", "effect_value": 6, "duration": "instant", "description": "少林密制丹药，丹香沉稳，服下可回护心脉，回复2d6+6点HP。"},
)
MEDICINE_CONSUMABLES = {row["item_id"]: row for row in MEDICINE_CONSUMABLE_ROWS}
MEDICINE_CONSUMABLES_BY_NAME = {row["name"]: row for row in MEDICINE_CONSUMABLE_ROWS}


FISHING_LOOT_ROWS = (
    {"loot_tier": "legendary", "roll_min": 1, "roll_max": 3, "item_id": "dragon_whisker_fish", "quantity": 1},
    {"loot_tier": "epic", "roll_min": 4, "roll_max": 10, "item_id": "ironbone_catfish", "quantity": 1},
    {"loot_tier": "rare", "roll_min": 11, "roll_max": 25, "item_id": "cold_jade_perch", "quantity": 1},
    {"loot_tier": "uncommon", "roll_min": 26, "roll_max": 45, "item_id": "silver_fin_carp", "quantity": 1},
    {"loot_tier": "common", "roll_min": 46, "roll_max": 100, "item_id": "river_carp", "quantity": 1},
)

DOOR_TYPE_HINTS = {
    "battle": {"title": "战", "subtitle": "金戈铁马", "color": "#b84a3a", "flavor": "门后传来兵器交击之声，杀气腾腾..."},
    "chest": {"title": "宝", "subtitle": "奇珍异宝", "color": "#c58a2c", "flavor": "门缝中透出淡淡宝光，似有珍稀之物藏于其内..."},
    "encounter": {"title": "缘", "subtitle": "机缘巧合", "color": "#6f9f7a", "flavor": "门内仙气缭绕，或有高人在此等候..."},
    "trap": {"title": "险", "subtitle": "危机四伏", "color": "#6f986d", "flavor": "此门阴气森森，机关暗伏，步步惊心..."},
    "merchant": {"title": "商", "subtitle": "江湖货郎", "color": "#b77a3d", "flavor": "听到算盘清脆声响，想来是游商在此歇息..."},
}

FLOOR_FLAVOR = {
    1: "初入武道塔，四周青砖古壁，空气中弥漫着淡淡的檀香。",
    2: "拾级而上，风声渐起，远处似有剑鸣铿锵。",
    3: "三层已入云端，脚下云海翻腾，心神为之一振。",
    4: "四层煞气渐浓，石壁之上隐现刀刻剑痕。",
    5: "五层罡风呼啸，真气运转竟有凝滞之感。",
    6: "将近顶层，威压如山，每一步都需运功抵抗。",
    7: "武神殿金光万丈，武神镜像端坐中央，等待挑战者到来。",
}

COMBAT_FLAVOR = {
    "player_hit": [
        "你的招式如行云流水，正中对手！",
        "这一招虚实相生，敌人避无可避！",
        "招式用老，劲力吐透，正中敌身！",
        "你身形一晃，寻得破绽，一击得手！",
    ],
    "player_crit": [
        "自然二十！这一招有如神助，势如雷霆万钧！",
        "破绽！你觑准时机，全力一击，直取要害！",
        "天意如此！这一击竟蕴合天地至理，威力倍增！",
    ],
    "player_miss": [
        "敌人早有防备，侧身避开，你的招式落空。",
        "这招虽快，却被敌人以巧劲卸开。",
        "敌手身法诡异，你的攻击擦身而过！",
    ],
    "enemy_hit": [
        "敌手反击迅猛，你闪避不及，中招！",
        "敌人招式老辣，你护得心门，却仍被余劲所伤。",
        "这一击来得好快！你闷哼一声，连退数步。",
    ],
    "enemy_miss": [
        "你脚下奇门步法施展，堪堪避开这一击。",
        "敌人招式虽猛，却被你以柔劲化解于无形。",
        "早有防备！你横移三尺，避其锋芒。",
    ],
    "victory": [
        "胜了！你长舒一口气，真气运转一周天。",
        "敌手颓然倒地，你立于当场，衣袂飘飘。",
        "此战虽险，却也印证了你的武道进境！",
    ],
}

EVENT_FLAVOR = {
    "chest_open": "你小心翼翼推开宝箱，金光洒落——",
    "chest_trap": "咔嚓！机关触发之声入耳，暗弩激射而出！",
    "merchant_greet": "一位面容清癯的老者抬眼笑道：贵客临门，可有中意之物？",
    "encounter_wise": "一位白发高人缓缓睁眼：孺子可教，且听我道来——",
    "trap_dodge": "机括声响的刹那，你纵身跃起，险之又险避开！",
}

ITEM_DESC = {
    "金疮药": "武林常备伤药，外敷内服，可止血生肌。",
    "小还丹": "少林密制丹药，辅以数十种名贵药材，服用后可回护心脉。",
    "大还丹": "传说中的圣药，生死人肉白骨，乃武林中人梦寐以求之物。",
    "武学素材": "修习进阶武学所需的通用材料，可从战斗、奇遇等事件中获得。",
    "武道真髓": "通关后凝聚的局外修行资源，用于提升局外强化等级。",
    "武学残卷": "通关后获得的残破典籍，可与武道真髓一起投入局外强化。",
    "中阶武学残页": "记录各门派中阶武学心得的残页，可推动门派武学领悟。",
    "顶级绝学残页": "极罕见的绝学残页，记载门派顶级武学的关键心法。",
}

EQUIPMENT_DESC = {
    "精铁长剑": "精铁打造的长剑，虽非神兵，却也锋利耐用。",
    "青竹杖": "以老竹烘制而成，杖身轻韧，适合点穴、格挡与行路。",
    "青钢剑": "掺以玄铁的青钢所铸，剑刃泛着幽蓝冷光。",
    "精铁禅杖": "少林匠坊常见重兵，杖头厚重，挥动时风声沉闷。",
    "朱漆酒葫芦": "丐帮弟子随身酒葫芦，朱漆斑驳，能提气暖身。",
    "软猬内甲仿品": "仿照桃花岛软猬甲所制，虽无反伤奇效，却也能护体防身。",
    "侠士披风": "江湖侠客常披的厚布披风，可挡风沙，也能遮掩身形。",
    "锁子软甲": "细密铁环缀成的贴身软甲，沉稳可靠，防护优于布甲。",
    "虎爪护手": "护手前端嵌有短刃，近身搏杀时尤为凶狠。",
    "银针匣": "峨眉医武常用暗器匣，银针细密，出手隐蔽而精准。",
    "避毒香囊": "囊中药香清冽，可压制毒瘴，也能让兵刃多一分辛辣毒意。",
    "温玉佩": "温润古玉贴身而佩，行气活血，能稍增气血根基。",
    "紫绶剑穗": "名门剑客喜用剑穗，既稳剑势，也便于蓄劲发招。",
    "碧玉箫": "玉质清凉，既可吹奏扰敌，也可作奇门短兵防身。",
    "紫金束带": "以紫金丝线编成，束身聚气，攻守皆有助益。",
    "雪蚕袍": "以极北雪蚕丝织就，轻如鸿毛，刀枪难入。",
    "金丝背心": "金丝密织的贴身背心，护住心脉，尤其擅长保命。",
    "寒铁剑": "寒铁锻成的利剑，剑气清冷，出鞘时寒意逼人。",
    "血纹戒刀": "刀身有暗红血纹，劈斩沉猛，带着血刀门式的狠辣。",
    "玄铁短刃": "玄铁残料打造的短刃，锋芒内敛，适合贴身突袭。",
    "玄铁护腕": "沉重玄铁护腕，既能格挡，也能让出手更具分量。",
    "龙纹令佩": "刻有龙纹的古旧令佩，传闻可镇心神、聚真气。",
    "软金甲": "软金丝编成的护甲，轻薄柔韧，能化开大半冲击。",
    "君子剑": "剑身端正清亮，重在准与稳，适合正面破敌。",
    "淑女剑": "剑形轻灵秀雅，出招迅疾，适合连刺与奇袭。",
    "玄铁重剑仿品": "仿照神雕大侠玄铁重剑形制，入手沉重，威力惊人。",
    "九阳暖玉": "蕴有温热真意的古玉，佩之如怀小日，可护体回阳。",
}
