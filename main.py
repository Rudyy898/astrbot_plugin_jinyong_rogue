from __future__ import annotations

from collections.abc import AsyncGenerator
from pathlib import Path

from astrbot.api import logger
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.message_components import Image
from astrbot.api.star import Context, Star, StarTools
from astrbot.core import AstrBotConfig

from .engine import (
    apply_pending_meta_rewards,
    buy_backpack,
    buy_merchant_equipment,
    combat_attack,
    combat_defend,
    combat_flee,
    command_hint_text,
    discard_item,
    equip_item,
    explore_door,
    fish,
    floor_square_text,
    format_attrs,
    help_text,
    inventory_text,
    item_detail_text,
    meta_text,
    new_player,
    next_floor,
    opening_text,
    open_door,
    pickup_item,
    sect_list_text,
    status_text,
    set_active_skill,
    sell_equipment,
    upgrade_meta_progression,
    use_consumable,
)
from .game_data import BAITS, DIFFICULTIES, FISHING_POOLS, SECTS
from .storage import JsonStore
from .ui import infer_scene, render_card_image


class JinyongRoguePlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig | None = None) -> None:
        super().__init__(context)
        self.config = config or {}
        self.plugin_id = "astrbot_plugin_jinyong_rogue"
        data_dir = Path(StarTools.get_data_dir(self.plugin_id))
        self.store = JsonStore(data_dir / "players.json")
        self.meta_store = JsonStore(data_dir / "meta.json")
        self.card_cache_dir = data_dir / "cards"

    async def initialize(self) -> None:
        self.card_cache_dir.mkdir(parents=True, exist_ok=True)
        logger.info("[jinyong_rogue] 金庸武侠DND肉鸽踢门团插件已加载")

    def _user_id(self, event: AstrMessageEvent) -> str:
        return str(event.get_sender_id())

    def _nickname(self, event: AstrMessageEvent) -> str:
        return str(event.get_sender_name() or event.get_sender_id())

    def _get_player_or_message(self, event: AstrMessageEvent) -> tuple[dict | None, str | None]:
        player = self.store.get_player(self._user_id(event))
        if player is None:
            return None, "你还没有角色。发送 /金庸开局 门派 [普通|困难] 创建角色。"
        return player, None

    def _save(self, event: AstrMessageEvent, player: dict) -> None:
        self.store.put_player(self._user_id(event), player)

    def _with_commands(self, text: str, player: dict | None = None, scene: str = "tower") -> str:
        return f"{text}\n\n{command_hint_text(player)}"

    def _has_floor_context(self, text: str) -> bool:
        markers = ("【第", "【武神殿】", "═══ 三道殿门 ═══", "═══ 可为之事 ═══", "探索完毕，你回到了古殿中央。")
        return any(marker in text for marker in markers)

    def _result(self, event: AstrMessageEvent, text: str, player: dict | None = None, scene: str = "tower"):
        if player is not None and not player.get("in_combat"):
            if scene == "opening":
                full_text = self._with_commands(text, player, scene)
            elif self._has_floor_context(text):
                full_text = self._with_commands(text, player, scene)
            else:
                square_text = floor_square_text(player)
                full_text = text + "\n\n" + "=" * 30 + "\n\n" + self._with_commands(square_text, player, scene)
        else:
            full_text = self._with_commands(text, player, scene)
        card_path = render_card_image(full_text, infer_scene(full_text, scene), self.card_cache_dir)
        if card_path is None:
            return event.plain_result(full_text)
        return event.chain_result([Image.fromFileSystem(str(card_path))])

    def _jy_command_key(self, text: str) -> str | None:
        text = text.strip()
        if not (text.startswith("/jy") or text.startswith("/金庸") or text.startswith("/踢门")):
            return None
        first = text.split(None, 1)[0]
        if first in {"/jy", "/金庸", "/踢门"}:
            return "help"
        mapping = {
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
            "/踢门": "kick",
            "/jy攻击": "attack",
            "/金庸攻击": "attack",
            "/攻击": "attack",
            "/jy逃跑": "flee",
            "/金庸逃跑": "flee",
            "/逃跑": "flee",
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
            "/jy买包": "buy_bag",
            "/金庸买包": "buy_bag",
            "/踢门买包": "buy_bag",
            "/jy购买": "buy_equipment",
            "/金庸购买": "buy_equipment",
            "/购买装备": "buy_equipment",
            "/jy出售": "sell_equipment",
            "/金庸出售": "sell_equipment",
            "/出售装备": "sell_equipment",
            "/jy装备": "equip",
            "/金庸装备": "equip",
            "/踢门装备": "equip",
            "/jy技能": "skill",
            "/金庸技能": "skill",
            "/踢门技能": "skill",
            "/jy局外": "meta",
            "/金庸局外": "meta",
            "/踢门局外": "meta",
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
        }
        return mapping.get(first)

    @filter.event_message_type(filter.EventMessageType.ALL, priority=100)
    async def jy_fallback_route(self, event: AstrMessageEvent) -> AsyncGenerator:
        """兼容 QQ 官方平台 @ 机器人后中文命令不进入 @filter.command 的情况。"""
        key = self._jy_command_key(event.message_str or "")
        if key is None:
            return
        if key == "help":
            yield self._result(event, help_text())
        elif key == "sects":
            lines = [sect_list_text(), "", "门派属性："]
            for name in SECTS:
                sect = SECTS[name]
                lines.append(f"{name}：{format_attrs(name)}｜{sect.ultimate}")
            yield self._result(event, "\n".join(lines))
        elif key == "new":
            async for msg in self.cmd_new(event):
                yield msg
        elif key == "status":
            async for msg in self.cmd_status(event):
                yield msg
        elif key == "kick":
            async for msg in self.cmd_kick(event):
                yield msg
        elif key == "next":
            async for msg in self.cmd_next_floor(event):
                yield msg
        elif key == "fish":
            async for msg in self.cmd_fish(event):
                yield msg
        elif key == "inventory":
            async for msg in self.cmd_inventory(event):
                yield msg
        elif key == "buy_bag":
            async for msg in self.cmd_buy_bag(event):
                yield msg
        elif key == "buy_equipment":
            async for msg in self.cmd_buy_equipment(event):
                yield msg
        elif key == "sell_equipment":
            async for msg in self.cmd_sell_equipment(event):
                yield msg
        elif key == "equip":
            async for msg in self.cmd_equip(event):
                yield msg
        elif key == "skill":
            async for msg in self.cmd_skill(event):
                yield msg
        elif key == "meta":
            async for msg in self.cmd_meta(event):
                yield msg
        elif key == "upgrade":
            async for msg in self.cmd_upgrade(event):
                yield msg
        elif key == "discard":
            async for msg in self.cmd_discard(event):
                yield msg
        elif key == "pickup":
            async for msg in self.cmd_pickup(event):
                yield msg
        elif key == "use":
            async for msg in self.cmd_use(event):
                yield msg
        elif key == "reset":
            async for msg in self.cmd_reset(event):
                yield msg
        elif key == "attack":
            async for msg in self.cmd_attack(event):
                yield msg
        elif key == "flee":
            async for msg in self.cmd_flee(event):
                yield msg
        elif key == "explore":
            async for msg in self.cmd_explore(event):
                yield msg
        elif key == "view":
            async for msg in self.cmd_view_item(event):
                yield msg
        event.stop_event()

    @filter.command("jy帮助", alias={"jy", "金庸帮助", "踢门帮助"})
    async def cmd_help(self, event: AstrMessageEvent) -> AsyncGenerator:
        yield self._result(event, help_text())

    @filter.command("jy门派", alias={"金庸门派", "踢门门派"})
    async def cmd_sects(self, event: AstrMessageEvent) -> AsyncGenerator:
        lines = [sect_list_text(), "", "门派属性："]
        for name in SECTS:
            sect = SECTS[name]
            lines.append(f"{name}：{format_attrs(name)}｜{sect.ultimate}")
        yield self._result(event, "\n".join(lines))

    @filter.command("jy开局", alias={"金庸开局", "踢门开局"})
    async def cmd_new(self, event: AstrMessageEvent) -> AsyncGenerator:
        parts = event.message_str.strip().split()
        if len(parts) < 2:
            yield self._result(event, "用法：/金庸开局 门派 [普通|困难]\n发送 /金庸门派 查看可选门派。")
            return
        sect_name = parts[1]
        difficulty = parts[2] if len(parts) >= 3 else "普通"
        if sect_name not in SECTS:
            yield self._result(event, "未知门派。\n" + sect_list_text())
            return
        if difficulty not in DIFFICULTIES:
            yield self._result(event, "未知难度。可选：普通、困难。")
            return
        existing = self.store.get_player(self._user_id(event))
        if existing and not existing.get("frozen"):
            yield self._result(event, "你已有进行中的角色。需要重开请发送 /金庸重置 confirm。", existing)
            return
        meta = self.meta_store.get_player(self._user_id(event)) or {}
        player = new_player(self._user_id(event), self._nickname(event), sect_name, difficulty, meta)
        self._save(event, player)
        yield self._result(event, opening_text(player, sect_name), player, scene="opening")

    @filter.command("jy状态", alias={"金庸状态", "踢门状态"})
    async def cmd_status(self, event: AstrMessageEvent) -> AsyncGenerator:
        player, message = self._get_player_or_message(event)
        if player is None:
            yield self._result(event, message)
            return
        yield self._result(event, status_text(player), player)

    @filter.command("jy踢门", alias={"金庸踢门", "踢门"})
    async def cmd_kick(self, event: AstrMessageEvent) -> AsyncGenerator:
        player, message = self._get_player_or_message(event)
        if player is None:
            yield self._result(event, message)
            return
        if player.get("in_combat"):
            yield self._result(event, "战斗中！请先使用 /金庸攻击 或 /金庸逃跑。", player)
            return
        parts = event.message_str.strip().split()
        door_num = int(parts[1]) if len(parts) >= 2 and parts[1].isdigit() else 0
        text = open_door(player, door_num)
        meta, meta_line = apply_pending_meta_rewards(self.meta_store.get_player(self._user_id(event)) or {}, player)
        if meta_line:
            self.meta_store.put_player(self._user_id(event), meta)
            text += meta_line
        self._save(event, player)
        yield self._result(event, text, player)

    @filter.command("jy下一层", alias={"金庸下一层", "踢门下一层"})
    async def cmd_next_floor(self, event: AstrMessageEvent) -> AsyncGenerator:
        player, message = self._get_player_or_message(event)
        if player is None:
            yield self._result(event, message)
            return
        text = next_floor(player)
        self._save(event, player)
        yield self._result(event, text, player)

    @filter.command("jy钓鱼", alias={"金庸钓鱼", "武侠钓鱼"})
    async def cmd_fish(self, event: AstrMessageEvent) -> AsyncGenerator:
        player, message = self._get_player_or_message(event)
        if player is None:
            yield self._result(event, message)
            return
        parts = event.message_str.strip().split()
        bait = parts[1] if len(parts) >= 2 else "普通蚯蚓饵"
        if bait == "列表":
            yield self._result(
                event,
                f"鱼池：{'、'.join(row['name'] for row in FISHING_POOLS.values())}\n"
                f"饵剂：{'、'.join(BAITS)}",
                player,
            )
            return
        text = fish(player, bait)
        self._save(event, player)
        yield self._result(event, text, player)

    @filter.command("jy使用", alias={"金庸使用", "使用鱼获", "使用药品"})
    async def cmd_use(self, event: AstrMessageEvent) -> AsyncGenerator:
        player, message = self._get_player_or_message(event)
        if player is None:
            yield self._result(event, message)
            return
        parts = event.message_str.strip().split(maxsplit=1)
        if len(parts) < 2:
            yield self._result(event, "用法：/金庸使用 药品名或鱼获名\n发送 /金庸背包 查看当前药品与鱼获消耗品。", player)
            return
        text = use_consumable(player, parts[1])
        self._save(event, player)
        yield self._result(event, text, player)

    @filter.command("jy背包", alias={"金庸背包", "踢门背包"})
    async def cmd_inventory(self, event: AstrMessageEvent) -> AsyncGenerator:
        player, message = self._get_player_or_message(event)
        if player is None:
            yield self._result(event, message)
            return
        text = inventory_text(player)
        self._save(event, player)
        yield self._result(event, text, player)

    @filter.command("jy买包", alias={"金庸买包", "购买背囊"})
    async def cmd_buy_bag(self, event: AstrMessageEvent) -> AsyncGenerator:
        player, message = self._get_player_or_message(event)
        if player is None:
            yield self._result(event, message)
            return
        parts = event.message_str.strip().split(maxsplit=1)
        text = buy_backpack(player, parts[1] if len(parts) >= 2 else "")
        self._save(event, player)
        yield self._result(event, text, player)

    @filter.command("jy购买", alias={"金庸购买", "购买装备"})
    async def cmd_buy_equipment(self, event: AstrMessageEvent) -> AsyncGenerator:
        player, message = self._get_player_or_message(event)
        if player is None:
            yield self._result(event, message)
            return
        parts = event.message_str.strip().split(maxsplit=1)
        if len(parts) < 2:
            yield self._result(event, "用法：/金庸购买 装备名\n需要先在商人门看到装备报价。", player)
            return
        text = buy_merchant_equipment(player, parts[1])
        self._save(event, player)
        yield self._result(event, text, player)

    @filter.command("jy出售", alias={"金庸出售", "出售装备"})
    async def cmd_sell_equipment(self, event: AstrMessageEvent) -> AsyncGenerator:
        player, message = self._get_player_or_message(event)
        if player is None:
            yield self._result(event, message)
            return
        parts = event.message_str.strip().split()
        if len(parts) < 2:
            yield self._result(event, "用法：/金庸出售 装备名 [数量]\n需要在商人门出售，且只能出售背包中未装备的装备。", player)
            return
        quantity = int(parts[2]) if len(parts) >= 3 and parts[2].isdigit() else 1
        text = sell_equipment(player, parts[1], quantity)
        self._save(event, player)
        yield self._result(event, text, player)

    @filter.command("jy装备", alias={"金庸装备", "装备物品"})
    async def cmd_equip(self, event: AstrMessageEvent) -> AsyncGenerator:
        player, message = self._get_player_or_message(event)
        if player is None:
            yield self._result(event, message)
            return
        parts = event.message_str.strip().split(maxsplit=1)
        if len(parts) < 2:
            yield self._result(event, "用法：/金庸装备 装备名\n发送 /金庸背包 查看装备。", player)
            return
        text = equip_item(player, parts[1])
        self._save(event, player)
        yield self._result(event, text, player)

    @filter.command("jy技能", alias={"金庸技能", "设置技能"})
    async def cmd_skill(self, event: AstrMessageEvent) -> AsyncGenerator:
        player, message = self._get_player_or_message(event)
        if player is None:
            yield self._result(event, message)
            return
        parts = event.message_str.strip().split(maxsplit=1)
        if len(parts) < 2:
            yield self._result(event, "用法：/金庸技能 武学名 或 /金庸技能 自动", player)
            return
        text = set_active_skill(player, parts[1])
        self._save(event, player)
        yield self._result(event, text, player)

    @filter.command("jy局外", alias={"金庸局外", "局外强化"})
    async def cmd_meta(self, event: AstrMessageEvent) -> AsyncGenerator:
        meta = self.meta_store.get_player(self._user_id(event)) or {}
        player = self.store.get_player(self._user_id(event))
        yield self._result(event, meta_text(meta, player), player)

    @filter.command("jy强化", alias={"金庸强化", "局外升级"})
    async def cmd_upgrade(self, event: AstrMessageEvent) -> AsyncGenerator:
        player, message = self._get_player_or_message(event)
        if player is None:
            yield self._result(event, message)
            return
        parts = event.message_str.strip().split(maxsplit=1)
        if len(parts) < 2:
            yield self._result(event, "用法：/金庸强化 钓鱼｜背囊｜盘缠｜气血\n发送 /金庸局外 查看强化表。", player)
            return
        meta = self.meta_store.get_player(self._user_id(event)) or player.get("meta_progression", {})
        text, updated_meta = upgrade_meta_progression(player, meta, parts[1])
        self.meta_store.put_player(self._user_id(event), updated_meta)
        self._save(event, player)
        yield self._result(event, text, player)

    @filter.command("jy丢弃", alias={"金庸丢弃", "丢弃物品"})
    async def cmd_discard(self, event: AstrMessageEvent) -> AsyncGenerator:
        player, message = self._get_player_or_message(event)
        if player is None:
            yield self._result(event, message)
            return
        parts = event.message_str.strip().split()
        if len(parts) < 2:
            yield self._result(event, "用法：/金庸丢弃 物品名 [数量]\n发送 /金庸背包 查看当前物品。", player)
            return
        quantity = int(parts[2]) if len(parts) >= 3 and parts[2].isdigit() else 1
        text = discard_item(player, parts[1], quantity)
        self._save(event, player)
        yield self._result(event, text, player)

    @filter.command("jy拾取", alias={"金庸拾取", "拾取物品"})
    async def cmd_pickup(self, event: AstrMessageEvent) -> AsyncGenerator:
        player, message = self._get_player_or_message(event)
        if player is None:
            yield self._result(event, message)
            return
        parts = event.message_str.strip().split()
        if len(parts) < 2:
            yield self._result(event, "用法：/金庸拾取 物品名 [数量]\n发送 /金庸背包 查看待拾取物品。", player)
            return
        quantity = int(parts[2]) if len(parts) >= 3 and parts[2].isdigit() else 1
        text = pickup_item(player, parts[1], quantity)
        self._save(event, player)
        yield self._result(event, text, player)

    @filter.command("jy攻击", alias={"金庸攻击", "攻击"})
    async def cmd_attack(self, event: AstrMessageEvent) -> AsyncGenerator:
        player, message = self._get_player_or_message(event)
        if player is None:
            yield self._result(event, message)
            return
        if not player.get("in_combat"):
            yield self._result(event, "你当前不在战斗中。发送 /金庸踢门 门号 开始冒险。", player)
            return
        parts = event.message_str.strip().split()
        skill_name = parts[1] if len(parts) >= 2 else ""
        text = combat_attack(player, skill_name)
        self._save(event, player)
        yield self._result(event, text, player)

    @filter.command("jy逃跑", alias={"金庸逃跑", "逃跑"})
    async def cmd_flee(self, event: AstrMessageEvent) -> AsyncGenerator:
        player, message = self._get_player_or_message(event)
        if player is None:
            yield self._result(event, message)
            return
        text = combat_flee(player)
        self._save(event, player)
        yield self._result(event, text, player)

    @filter.command("jy防御", alias={"金庸防御", "防御"})
    async def cmd_defend(self, event: AstrMessageEvent) -> AsyncGenerator:
        player, message = self._get_player_or_message(event)
        if player is None:
            yield self._result(event, message)
            return
        if not player.get("in_combat"):
            yield self._result(event, "你当前不在战斗中。发送 /金庸踢门 门号 开始冒险。", player)
            return
        text = combat_defend(player)
        self._save(event, player)
        yield self._result(event, text, player)

    @filter.command("jy探索", alias={"金庸探索", "探索门"})
    async def cmd_explore(self, event: AstrMessageEvent) -> AsyncGenerator:
        player, message = self._get_player_or_message(event)
        if player is None:
            yield self._result(event, message)
            return
        parts = event.message_str.strip().split()
        if len(parts) < 2 or not parts[1].isdigit():
            yield self._result(event, "用法：/金庸探索 门号\n探索已通关的门，可能有意外收获。", player)
            return
        door_num = int(parts[1])
        text = explore_door(player, door_num)
        self._save(event, player)
        yield self._result(event, text, player)

    @filter.command("jy查看", alias={"金庸查看", "查看物品"})
    async def cmd_view_item(self, event: AstrMessageEvent) -> AsyncGenerator:
        player, message = self._get_player_or_message(event)
        if player is None:
            yield self._result(event, message)
            return
        parts = event.message_str.strip().split(maxsplit=1)
        if len(parts) < 2:
            yield self._result(event, "用法：/金庸查看 物品名\n查看物品的详细描述和效果。", player)
            return
        text = item_detail_text(parts[1], player)
        yield self._result(event, text, player)

    @filter.command("jy重置", alias={"金庸重置", "踢门重置"})
    async def cmd_reset(self, event: AstrMessageEvent) -> AsyncGenerator:
        parts = event.message_str.strip().split()
        if len(parts) < 2 or parts[1].lower() != "confirm":
            player = self.store.get_player(self._user_id(event))
            yield self._result(event, "这会删除当前金庸踢门团角色。确认请发送：/金庸重置 confirm", player)
            return
        deleted = self.store.delete_player(self._user_id(event))
        yield self._result(event, "角色档案已删除，可重新 /金庸开局。" if deleted else "当前没有可删除的角色档案。")
