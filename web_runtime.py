from __future__ import annotations

from pathlib import Path
from typing import Any

from .engine import (
    apply_pending_meta_rewards,
    _available_combat_skill_names,
    _has_current_merchant,
    buy_merchant_equipment,
    combat_attack,
    combat_defend,
    combat_flee,
    compose_martial_fragments,
    command_hint_text,
    decline_true_wushen,
    difficulty_gate_text,
    discard_item,
    equip_item,
    explore_door,
    fish,
    format_attrs,
    help_text,
    inventory_text,
    item_detail_text,
    leave_merchant,
    learn_martial_skill,
    martial_text,
    merge_meta_progression,
    meta_text,
    new_player,
    next_floor,
    opening_text,
    open_door,
    pickup_item,
    sect_detail_text,
    sect_list_text,
    sell_equipment,
    set_meta_elixir_carry,
    set_active_skill,
    status_text,
    surrender_game,
    trap_block,
    trap_counter,
    trap_dodge,
    unlock_meta_ultimate,
    upgrade_meta_progression,
    ultimate_text,
    use_consumable,
    _ensure_martial_fragments,
    MARTIAL_FRAGMENT_COMPOSE_RATE,
    _martial_cost_text,
    _martial_learn_rows,
    _martial_row_status,
)
from .game_data import BAITS, DIFFICULTIES, EQUIPMENT_BY_ID, FISHING_POOLS, FISH_CONSUMABLES, LEGENDARY_MARTIAL_ART_SKILLS, MEDICINE_CONSUMABLES, SECTS
from .storage import JsonStore
from .ui import infer_scene, render_card_image


COMMAND_ALIASES = {
    "/jy": "help",
    "/金庸": "help",
    "/踢门": "kick",
    "/jy帮助": "help",
    "/金庸帮助": "help",
    "/踢门帮助": "help",
    "/jy门派": "sects",
    "/金庸门派": "sects",
    "/踢门门派": "sects",
    "/jy开局": "new",
    "/金庸开局": "new",
    "/踢门开局": "new",
    "/jy状态": "status",
    "/金庸状态": "status",
    "/踢门状态": "status",
    "/jy踢门": "kick",
    "/金庸踢门": "kick",
    "/jy不挑战": "decline_true_wushen",
    "/金庸不挑战": "decline_true_wushen",
    "/不挑战": "decline_true_wushen",
    "/jy攻击": "attack",
    "/金庸攻击": "attack",
    "/攻击": "attack",
    "/jy逃跑": "flee",
    "/金庸逃跑": "flee",
    "/逃跑": "flee",
    "/jy防御": "defend",
    "/金庸防御": "defend",
    "/防御": "defend",
    "/jy躲避": "trap_dodge",
    "/金庸躲避": "trap_dodge",
    "/躲避": "trap_dodge",
    "/jy躲闪": "trap_dodge",
    "/金庸躲闪": "trap_dodge",
    "/躲闪": "trap_dodge",
    "/jy格挡": "trap_block",
    "/金庸格挡": "trap_block",
    "/格挡": "trap_block",
    "/jy反击": "trap_counter",
    "/金庸反击": "trap_counter",
    "/反击": "trap_counter",
    "/jy探索": "explore",
    "/金庸探索": "explore",
    "/探索门": "explore",
    "/jy查看": "view",
    "/金庸查看": "view",
    "/查看物品": "view",
    "/jy下一层": "next",
    "/金庸下一层": "next",
    "/踢门下一层": "next",
    "/jy钓鱼": "fish",
    "/金庸钓鱼": "fish",
    "/踢门钓鱼": "fish",
    "/jy背包": "inventory",
    "/金庸背包": "inventory",
    "/踢门背包": "inventory",
    "/jy购买": "buy_equipment",
    "/金庸购买": "buy_equipment",
    "/购买装备": "buy_equipment",
    "/jy出售": "sell_equipment",
    "/金庸出售": "sell_equipment",
    "/出售装备": "sell_equipment",
    "/jy离开商人": "leave_merchant",
    "/金庸离开商人": "leave_merchant",
    "/离开商人": "leave_merchant",
    "/jy装备": "equip",
    "/金庸装备": "equip",
    "/踢门装备": "equip",
    "/jy技能": "skill",
    "/金庸技能": "skill",
    "/踢门技能": "skill",
    "/jy武学": "martial",
    "/金庸武学": "martial",
    "/踢门武学": "martial",
    "/jy领悟": "learn_martial",
    "/金庸领悟": "learn_martial",
    "/踢门领悟": "learn_martial",
    "/jy合成残页": "compose_fragments",
    "/金庸合成残页": "compose_fragments",
    "/踢门合成残页": "compose_fragments",
    "/jy解锁绝学": "unlock_ultimate",
    "/金庸解锁绝学": "unlock_ultimate",
    "/踢门解锁绝学": "unlock_ultimate",
    "/jy绝学": "ultimate",
    "/金庸绝学": "ultimate",
    "/踢门绝学": "ultimate",
    "/jy局外": "meta",
    "/金庸局外": "meta",
    "/踢门局外": "meta",
    "/jy小还丹": "elixir_carry",
    "/金庸小还丹": "elixir_carry",
    "/jy强化": "upgrade",
    "/金庸强化": "upgrade",
    "/踢门强化": "upgrade",
    "/jy丢弃": "discard",
    "/金庸丢弃": "discard",
    "/踢门丢弃": "discard",
    "/jy拾取": "pickup",
    "/金庸拾取": "pickup",
    "/踢门拾取": "pickup",
    "/jy使用": "use",
    "/金庸使用": "use",
    "/踢门使用": "use",
    "/jy重置": "reset",
    "/金庸重置": "reset",
    "/踢门重置": "reset",
    "/jy放弃": "surrender",
    "/金庸放弃": "surrender",
    "/踢门放弃": "surrender",
}


class LocalWebGameRuntime:
    """HTTP/Web shell around the same engine functions used by the QQ plugin."""

    def __init__(self, data_dir: Path) -> None:
        self.data_dir = data_dir
        self.store = JsonStore(data_dir / "players.json")
        self.meta_store = JsonStore(data_dir / "meta.json")
        self.card_dir = data_dir / "cards"
        self.card_dir.mkdir(parents=True, exist_ok=True)

    def dispatch(self, user_id: str, nickname: str, raw_text: str) -> dict[str, Any]:
        user_id = str(user_id or "web-tester").strip() or "web-tester"
        nickname = str(nickname or user_id).strip() or user_id
        raw_text = str(raw_text or "").strip()
        if not raw_text:
            return self._response("请输入命令。发送 /金庸帮助 查看指令。", user_id=user_id)

        key = self._command_key(raw_text)
        if key is None:
            return self._response("未识别命令。发送 /金庸帮助 查看指令。", user_id=user_id)

        parts = raw_text.split()
        player = self.store.get_player(user_id)
        text = self._handle_command(key, parts, raw_text, user_id, nickname, player)
        player = self.store.get_player(user_id)
        return self._response(text, player=player, user_id=user_id, suppress_card_player=key in {"meta", "elixir_carry", "upgrade"})

    def _handle_command(
        self,
        key: str,
        parts: list[str],
        raw_text: str,
        user_id: str,
        nickname: str,
        player: dict[str, Any] | None,
    ) -> str:
        if key == "help":
            return help_text()
        if key == "sects":
            if len(parts) >= 2:
                return sect_detail_text(" ".join(parts[1:]), self._current_meta(user_id, player))
            lines = [sect_list_text(), "", "门派属性："]
            for name, sect in SECTS.items():
                lines.append(f"{name}：{format_attrs(name)}｜{sect.ultimate}")
            return "\n".join(lines)
        if key == "new":
            return self._new_game(parts, user_id, nickname, player)
        if key == "reset":
            return self._reset(parts, user_id)
        if key == "meta":
            meta = self._current_meta(user_id, player)
            return meta_text(meta, player)
        if key == "ultimate":
            meta = self._current_meta(user_id, player)
            return ultimate_text(meta)
        if key == "elixir_carry":
            if len(parts) < 2 or parts[1] not in {"0", "1", "2", "3"}:
                return "用法：/金庸小还丹 0｜1｜2｜3\n0=不带；1=默认；2/3需要还丹护命升级上限支持。"
            meta = self._current_meta(user_id, player)
            text, updated_meta = set_meta_elixir_carry(meta, int(parts[1]))
            self.meta_store.put_player(user_id, updated_meta)
            if player:
                player["meta_progression"] = updated_meta
                self._save(user_id, player)
            return text + "\n\n" + meta_text(updated_meta, player)

        player, message = self._get_player_or_message(user_id)
        if player is None:
            return message

        if key == "status":
            return status_text(player)
        if key == "kick":
            return self._kick(parts, user_id, player)
        if key == "decline_true_wushen":
            return self._finish_sensitive(user_id, player, decline_true_wushen(player))
        if key == "next":
            text = next_floor(player)
            self._save(user_id, player)
            return text
        if key == "fish":
            bait = parts[1] if len(parts) >= 2 else "普通蚯蚓饵"
            if bait == "列表":
                return f"鱼池：{'、'.join(row['name'] for row in FISHING_POOLS.values())}\n饵剂：{'、'.join(BAITS)}"
            text = fish(player, bait)
            self._save(user_id, player)
            return text
        if key == "inventory":
            text = inventory_text(player)
            self._save(user_id, player)
            return text
        if key == "buy_equipment":
            if len(parts) < 2:
                return "用法：/金庸购买 商品名\n需要先在商人门看到背囊或装备报价。"
            text = buy_merchant_equipment(player, " ".join(parts[1:]))
            self._save(user_id, player)
            return text
        if key == "sell_equipment":
            if len(parts) < 2:
                return "用法：/金庸出售 物品名 [数量]\n需要在商人或游商处出售；已装备的装备不会被出售。"
            quantity = int(parts[-1]) if len(parts) >= 3 and parts[-1].isdigit() else 1
            name = " ".join(parts[1:-1] if len(parts) >= 3 and parts[-1].isdigit() else parts[1:])
            text = sell_equipment(player, name, quantity)
            self._save(user_id, player)
            return text
        if key == "leave_merchant":
            text = leave_merchant(player)
            self._save(user_id, player)
            return text
        if key == "equip":
            if len(parts) < 2:
                return "用法：/金庸装备 装备名\n发送 /金庸背包 查看装备。"
            text = equip_item(player, " ".join(parts[1:]))
            self._save(user_id, player)
            return text
        if key == "skill":
            return self._skill(parts, user_id, player)
        if key == "martial":
            return martial_text(player)
        if key == "learn_martial":
            text = learn_martial_skill(player, " ".join(parts[1:]) if len(parts) >= 2 else "")
            self._save(user_id, player)
            return text
        if key == "compose_fragments":
            quantity = int(parts[1]) if len(parts) >= 2 and parts[1].isdigit() else 1
            text = compose_martial_fragments(player, quantity)
            self._save(user_id, player)
            return text
        if key == "unlock_ultimate":
            meta = self._current_meta(user_id, player)
            text, updated_meta = unlock_meta_ultimate(meta, " ".join(parts[1:]) if len(parts) >= 2 else "")
            self.meta_store.put_player(user_id, updated_meta)
            player["meta_progression"] = updated_meta
            self._save(user_id, player)
            return text + "\n\n" + ultimate_text(updated_meta)
        if key == "upgrade":
            if len(parts) < 2:
                return "用法：/金庸强化 钓鱼｜背囊｜盘缠｜气血｜小还丹\n发送 /金庸局外 查看强化表。"
            meta = self._current_meta(user_id, player)
            text, updated_meta = upgrade_meta_progression(player, meta, " ".join(parts[1:]))
            self.meta_store.put_player(user_id, updated_meta)
            self._save(user_id, player)
            return text + "\n\n" + meta_text(updated_meta, player)
        if key == "discard":
            if len(parts) < 2:
                return "用法：/金庸丢弃 物品名 [数量]\n发送 /金庸背包 查看当前物品。"
            quantity = int(parts[-1]) if len(parts) >= 3 and parts[-1].isdigit() else 1
            name = " ".join(parts[1:-1] if len(parts) >= 3 and parts[-1].isdigit() else parts[1:])
            text = discard_item(player, name, quantity)
            self._save(user_id, player)
            return text
        if key == "pickup":
            if len(parts) < 2:
                return "用法：/金庸拾取 物品名 [数量]\n发送 /金庸背包 查看待拾取物品。"
            quantity = int(parts[-1]) if len(parts) >= 3 and parts[-1].isdigit() else 1
            name = " ".join(parts[1:-1] if len(parts) >= 3 and parts[-1].isdigit() else parts[1:])
            text = pickup_item(player, name, quantity)
            self._save(user_id, player)
            return text
        if key == "use":
            if len(parts) < 2:
                return "用法：/金庸使用 药品名或鱼获名\n发送 /金庸背包 查看当前药品与鱼获消耗品。"
            text = use_consumable(player, " ".join(parts[1:]))
            self._save(user_id, player)
            return text
        if key == "attack":
            return self._attack(parts, user_id, player)
        if key == "flee":
            return self._finish_sensitive(user_id, player, combat_flee(player))
        if key == "defend":
            if player.get("in_trap"):
                return "你正身处机关陷阱中！请使用 /金庸躲避、/金庸格挡 或 /金庸反击 来应对。"
            if not player.get("in_combat"):
                return "你当前不在战斗中。发送 /金庸踢门 门号 开始冒险。"
            return self._finish_sensitive(user_id, player, combat_defend(player))
        if key == "trap_dodge":
            return self._trap_action(user_id, player, trap_dodge)
        if key == "trap_block":
            return self._trap_action(user_id, player, trap_block)
        if key == "trap_counter":
            return self._trap_action(user_id, player, trap_counter)
        if key == "explore":
            if player.get("in_trap"):
                return "你正身处机关陷阱中！请使用 /金庸躲避、/金庸格挡 或 /金庸反击 来应对。"
            if len(parts) < 2 or not parts[1].isdigit():
                return "用法：/金庸探索 门号\n探索已通关的门，可能有意外收获。"
            text = explore_door(player, int(parts[1]))
            self._save(user_id, player)
            return text
        if key == "view":
            if len(parts) < 2:
                return "用法：/金庸查看 物品名\n查看物品的详细描述和效果。"
            return item_detail_text(" ".join(parts[1:]), player)
        if key == "surrender":
            return self._finish_sensitive(user_id, player, surrender_game(player))

        return f"未实现的本地调试命令：{raw_text}"

    def _new_game(self, parts: list[str], user_id: str, nickname: str, player: dict[str, Any] | None) -> str:
        if len(parts) < 2:
            return "用法：/金庸开局 门派 [普通|困难|炼狱]\n发送 /金庸门派 查看可选门派。"
        sect_name = parts[1]
        difficulty = parts[2] if len(parts) >= 3 else "普通"
        if sect_name not in SECTS:
            return "未知门派。\n" + sect_list_text()
        if difficulty not in DIFFICULTIES:
            return "未知难度。可选：普通、困难、炼狱。"
        if player and not player.get("frozen") and not player.get("game_over"):
            return "你已有进行中的角色。需要重开请发送 /金庸重置 confirm。"
        meta = self.meta_store.get_player(user_id) or {}
        gate_text = difficulty_gate_text(sect_name, difficulty, meta)
        if gate_text:
            return gate_text
        player = new_player(user_id, nickname, sect_name, difficulty, meta)
        self.meta_store.put_player(user_id, player.get("meta_progression") or {})
        self._save(user_id, player)
        return opening_text(player, sect_name)

    def _kick(self, parts: list[str], user_id: str, player: dict[str, Any]) -> str:
        if player.get("in_combat"):
            return "战斗中！请先使用 /金庸攻击 或 /金庸逃跑。"
        if player.get("in_trap"):
            return "你正身处机关陷阱中！请使用 /金庸躲避、/金庸格挡 或 /金庸反击 来应对。"
        door_num = int(parts[1]) if len(parts) >= 2 and parts[1].isdigit() else 0
        text = open_door(player, door_num)
        meta, meta_line = apply_pending_meta_rewards(self.meta_store.get_player(user_id) or {}, player)
        if meta_line:
            self.meta_store.put_player(user_id, meta)
            text += meta_line
        if player.get("game_over") or player.get("finished"):
            meta = player.get("meta_progression")
            if meta:
                self.meta_store.put_player(user_id, meta)
        self._save(user_id, player)
        return text

    def _skill(self, parts: list[str], user_id: str, player: dict[str, Any]) -> str:
        if len(parts) < 2:
            from .engine import _available_combat_skill_names
            from .game_data import MARTIAL_ART_SKILLS_BY_NAME, SKILL_COMBAT_BY_NAME

            available = _available_combat_skill_names(player)
            active = player.get("active_skill") or "自动"
            text_lines = ["【金庸踢门团·技能列表】", f"当前激活：{active}", "", "可用武学：", "────────────────"]
            for skill_name in available:
                marker = "★" if skill_name == active or (active == "自动" and skill_name == available[0]) else " "
                skill = SKILL_COMBAT_BY_NAME.get(skill_name) or MARTIAL_ART_SKILLS_BY_NAME.get(skill_name)
                if skill:
                    mp_text = f"MP{skill['mp_cost']}" if skill["mp_cost"] > 0 else "免费"
                    text_lines.extend([
                        f"{marker} 【{skill_name}】",
                        f"    {skill['category']} · {skill['damage_type']} · {mp_text}",
                        f"    伤害：{skill['attack_segments']}段 × {skill['damage_dice_count']}d{skill['damage_die']}+{skill['damage_bonus']}",
                        "",
                    ])
                else:
                    text_lines.extend([f"{marker} 【{skill_name}】", ""])
            text_lines.extend(["────────────────", "用法：/金庸技能 武学名 切换，/金庸技能 自动 恢复自动"])
            return "\n".join(text_lines)
        text = set_active_skill(player, " ".join(parts[1:]))
        self._save(user_id, player)
        return text

    def _attack(self, parts: list[str], user_id: str, player: dict[str, Any]) -> str:
        if player.get("in_trap"):
            return "你正身处机关陷阱中！请使用 /金庸躲避、/金庸格挡 或 /金庸反击 来应对。"
        if not player.get("in_combat"):
            return "你当前不在战斗中。发送 /金庸踢门 门号 开始冒险。"
        skill_name = " ".join(parts[1:]) if len(parts) >= 2 else ""
        return self._finish_sensitive(user_id, player, combat_attack(player, skill_name))

    def _trap_action(self, user_id: str, player: dict[str, Any], action) -> str:
        if not player.get("in_trap"):
            return "你当前不在陷阱中。"
        text = action(player)
        return self._finish_sensitive(user_id, player, text)

    def _finish_sensitive(self, user_id: str, player: dict[str, Any], text: str) -> str:
        if player.get("game_over") or player.get("finished"):
            meta = player.get("meta_progression")
            if meta:
                self.meta_store.put_player(user_id, meta)
        self._save(user_id, player)
        return text

    def _reset(self, parts: list[str], user_id: str) -> str:
        if len(parts) < 2 or parts[1].lower() != "confirm":
            return "这会删除当前金庸踢门团角色。确认请发送：/金庸重置 confirm"
        deleted = self.store.delete_player(user_id)
        return "角色档案已删除，可重新 /金庸开局。" if deleted else "当前没有可删除的角色档案。"

    def _get_player_or_message(self, user_id: str) -> tuple[dict[str, Any] | None, str]:
        player = self.store.get_player(user_id)
        if player is None:
            return None, "你还没有角色。发送 /金庸开局 门派 [普通|困难|炼狱] 创建角色。"
        return player, ""

    def _current_meta(self, user_id: str, player: dict[str, Any] | None = None) -> dict[str, Any]:
        return merge_meta_progression(self.meta_store.get_player(user_id) or {}, player.get("meta_progression") if player else None)

    def _save(self, user_id: str, player: dict[str, Any]) -> None:
        self.store.put_player(user_id, player)

    def _response(
        self,
        text: str,
        player: dict[str, Any] | None = None,
        user_id: str = "web-tester",
        suppress_card_player: bool = False,
    ) -> dict[str, Any]:
        full_text = f"{text}\n\n{command_hint_text(player)}"
        scene = infer_scene(full_text, "tower")
        render_player = None if suppress_card_player else player
        card_path = render_card_image(full_text, scene, self.card_dir, render_player)
        image_url = f"/cards/{card_path.name}" if card_path else ""
        return {
            "ok": True,
            "userId": user_id,
            "text": full_text,
            "scene": scene,
            "imageUrl": image_url,
            "player": self._player_summary(player, user_id),
        }

    def _command_key(self, text: str) -> str | None:
        first = text.split(None, 1)[0]
        if first in {"/攻击", "/逃跑", "/防御", "/躲避", "/躲闪", "/格挡", "/反击"}:
            return COMMAND_ALIASES.get(first)
        if not (text.startswith("/jy") or text.startswith("/金庸") or text.startswith("/踢门")):
            return None
        return COMMAND_ALIASES.get(first)

    def _player_summary(self, player: dict[str, Any] | None, user_id: str = "web-tester") -> dict[str, Any] | None:
        if not player:
            return None
        return {
            "nickname": player.get("nickname"),
            "sect": player.get("sect"),
            "difficulty": player.get("difficulty"),
            "level": player.get("level"),
            "floor": player.get("floor"),
            "openedDoors": player.get("opened_doors"),
            "hp": player.get("hp"),
            "maxHp": player.get("max_hp"),
            "mp": player.get("mp"),
            "maxMp": player.get("max_mp"),
            "silver": player.get("silver"),
            "reviveElixirs": player.get("revive_elixirs", 0),
            "usableItems": self._usable_item_summary(player),
            "equipmentItems": self._equipment_item_summary(player),
            "merchantItems": self._merchant_item_summary(player),
            "merchantLeaveCommand": "/金庸离开商人" if player.get("merchant_pending_leave") else "",
            "skillItems": self._skill_item_summary(player),
            "learnableSkills": self._learnable_skill_summary(player),
            "metaUnlockItems": self._meta_unlock_item_summary(user_id, player),
            "inCombat": bool(player.get("in_combat")),
            "inTrap": bool(player.get("in_trap")),
            "finished": bool(player.get("finished")),
            "frozen": bool(player.get("frozen")),
            "gameOver": bool(player.get("game_over")),
        }

    def _meta_unlock_item_summary(self, user_id: str, player: dict[str, Any]) -> list[dict[str, str]]:
        meta = self._current_meta(user_id, player)
        unlocked_sects = set(meta.get("unlocked_sect_ultimates", []))
        unlocked_legends = set(meta.get("unlocked_legendary_ultimates", []))
        sect_stock = meta.get("sect_ultimate_fragments", {}) if isinstance(meta.get("sect_ultimate_fragments"), dict) else {}
        items = []
        for sect_name, count in sect_stock.items():
            if int(count) > 0 and sect_name in SECTS and sect_name not in unlocked_sects:
                ultimate = SECTS[sect_name].ultimate
                items.append({"label": ultimate, "command": f"/金庸解锁绝学 {ultimate}"})
        if int(meta.get("legendary_fragments", 0)) > 0:
            for row in LEGENDARY_MARTIAL_ART_SKILLS.values():
                if row["skill_id"] not in unlocked_legends:
                    items.append({"label": row["name"], "command": f"/金庸解锁绝学 {row['name']}"})
        return items

    def _usable_item_summary(self, player: dict[str, Any]) -> list[dict[str, Any]]:
        items = []
        can_sell = _has_current_merchant(player)
        for item_id, count in player.get("inventory", {}).items():
            row = FISH_CONSUMABLES.get(item_id) or MEDICINE_CONSUMABLES.get(item_id)
            if row and int(count) > 0:
                items.append({
                    "id": item_id,
                    "name": row["name"],
                    "quantity": int(count),
                    "sellableQuantity": int(count) if can_sell else 0,
                    "actionLabel": "用",
                    "actionCommand": f"/金庸使用 {row['name']}",
                    "sellCommand": f"/金庸出售 {row['name']} 1" if can_sell else "",
                    "viewCommand": f"/金庸查看 {row['name']}",
                })
        return items

    def _equipment_item_summary(self, player: dict[str, Any]) -> list[dict[str, Any]]:
        items = []
        equipped_ids = set((player.get("equipped") or {}).values())
        can_sell = _has_current_merchant(player)
        for item_id, count in player.get("inventory", {}).items():
            equipment = EQUIPMENT_BY_ID.get(item_id)
            if equipment and int(count) > 0:
                sellable = max(0, int(count) - (1 if item_id in equipped_ids else 0))
                items.append({
                    "id": item_id,
                    "name": equipment["name"],
                    "quantity": int(count),
                    "sellableQuantity": sellable,
                    "active": item_id in equipped_ids,
                    "equipCommand": f"/金庸装备 {equipment['name']}",
                    "sellCommand": f"/金庸出售 {equipment['name']} 1" if can_sell and sellable > 0 else "",
                    "viewCommand": f"/金庸查看 {equipment['name']}",
                })
        return items

    def _skill_item_summary(self, player: dict[str, Any]) -> list[dict[str, Any]]:
        active = player.get("active_skill") or "自动"
        in_combat = bool(player.get("in_combat"))
        items = [{
            "name": "自动",
            "active": active == "自动",
            "selectCommand": "/金庸技能 自动",
            "viewCommand": "",
            "attackCommand": "",
        }]
        for skill_name in _available_combat_skill_names(player):
            items.append({
                "name": skill_name,
                "active": active == skill_name,
                "selectCommand": f"/金庸技能 {skill_name}",
                "viewCommand": f"/金庸查看 {skill_name}",
                "attackCommand": f"/金庸攻击 {skill_name}" if in_combat else "",
            })
        return items

    def _learnable_skill_summary(self, player: dict[str, Any]) -> list[dict[str, Any]]:
        fragments = _ensure_martial_fragments(player)
        items = [{
            "name": "武学总览",
            "status": "查看",
            "cost": "",
            "learnCommand": "/金庸武学",
            "actionLabel": "看",
            "viewCommand": "",
        }]
        items.append({
            "name": "合成顶级残页",
            "status": "可合成" if int(fragments.get("advanced", 0)) >= MARTIAL_FRAGMENT_COMPOSE_RATE else "中阶不足",
            "cost": f"中阶残页x{MARTIAL_FRAGMENT_COMPOSE_RATE}",
            "learnCommand": "/金庸合成残页",
            "actionLabel": "合",
            "viewCommand": "",
        })
        for row in _martial_learn_rows(player):
            status = _martial_row_status(player, row)
            if status == "已学":
                continue
            items.append({
                "name": row["name"],
                "status": status,
                "cost": _martial_cost_text(row),
                "learnCommand": f"/金庸领悟 {row['name']}" if status == "可领悟" else "/金庸武学",
                "actionLabel": "悟",
                "viewCommand": f"/金庸查看 {row['name']}",
            })
        return items

    def _merchant_item_summary(self, player: dict[str, Any]) -> list[dict[str, Any]]:
        offer = player.get("merchant_offer") or {}
        floor = int(player.get("floor", 0))
        items = []
        if offer.get("offer_type") == "backpack" and int(offer.get("floor", -1)) == floor:
            items.append({
                "type": "背囊",
                "name": offer.get("name", "背囊"),
                "price": int(offer.get("price", 0)),
                "command": f"/金庸购买 {offer.get('name', '背囊')}",
                "viewCommand": f"/金庸查看 {offer.get('name', '背囊')}",
            })
        equipment = offer.get("equipment") or {}
        if equipment and int(equipment.get("floor", -1)) == floor:
            row = EQUIPMENT_BY_ID.get(str(equipment.get("item_id", "")))
            slot_labels = {"weapon": "武器", "armor": "防具", "accessory": "饰品"}
            item_type = slot_labels.get(str(row.get("slot"))) if row else "装备"
            items.append({
                "type": item_type or "装备",
                "name": equipment.get("name", "装备"),
                "price": int(equipment.get("price", 0)),
                "command": f"/金庸购买 {equipment.get('name', '装备')}",
                "viewCommand": f"/金庸查看 {equipment.get('name', '装备')}",
            })
        return items
