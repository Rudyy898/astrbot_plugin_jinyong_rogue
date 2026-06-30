from __future__ import annotations

from collections.abc import AsyncGenerator
from pathlib import Path

from astrbot.api import logger
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.star import Context, Star, StarTools
from astrbot.core import AstrBotConfig

from .engine import fish, format_attrs, help_text, new_player, next_floor, open_door, sect_list_text, status_text
from .game_data import BAITS, DIFFICULTIES, FISHING_SPOTS, SECTS
from .storage import JsonStore


class JinyongRoguePlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig | None = None) -> None:
        super().__init__(context)
        self.config = config or {}
        self.plugin_id = "astrbot_plugin_jinyong_rogue"
        data_dir = Path(StarTools.get_data_dir(self.plugin_id))
        self.store = JsonStore(data_dir / "players.json")

    async def initialize(self) -> None:
        logger.info("[jinyong_rogue] 金庸武侠DND肉鸽踢门团插件已加载")

    def _user_id(self, event: AstrMessageEvent) -> str:
        return str(event.get_sender_id())

    def _nickname(self, event: AstrMessageEvent) -> str:
        return str(event.get_sender_name() or event.get_sender_id())

    def _get_player_or_message(self, event: AstrMessageEvent) -> tuple[dict | None, str | None]:
        player = self.store.get_player(self._user_id(event))
        if player is None:
            return None, "你还没有角色。发送 /jy开局 门派 [普通|困难] 创建角色。"
        return player, None

    def _save(self, event: AstrMessageEvent, player: dict) -> None:
        self.store.put_player(self._user_id(event), player)

    @filter.command("jy帮助", alias={"jy", "金庸帮助", "踢门帮助"})
    async def cmd_help(self, event: AstrMessageEvent) -> AsyncGenerator:
        yield event.plain_result(help_text())

    @filter.command("jy门派", alias={"金庸门派", "踢门门派"})
    async def cmd_sects(self, event: AstrMessageEvent) -> AsyncGenerator:
        lines = [sect_list_text(), "", "门派属性："]
        for name in SECTS:
            sect = SECTS[name]
            lines.append(f"{name}：{format_attrs(name)}｜{sect.ultimate}")
        yield event.plain_result("\n".join(lines))

    @filter.command("jy开局", alias={"金庸开局", "踢门开局"})
    async def cmd_new(self, event: AstrMessageEvent) -> AsyncGenerator:
        parts = event.message_str.strip().split()
        if len(parts) < 2:
            yield event.plain_result("用法：/jy开局 门派 [普通|困难]\n发送 /jy门派 查看可选门派。")
            return
        sect_name = parts[1]
        difficulty = parts[2] if len(parts) >= 3 else "普通"
        if sect_name not in SECTS:
            yield event.plain_result("未知门派。\n" + sect_list_text())
            return
        if difficulty not in DIFFICULTIES:
            yield event.plain_result("未知难度。可选：普通、困难。")
            return
        existing = self.store.get_player(self._user_id(event))
        if existing and not existing.get("frozen"):
            yield event.plain_result("你已有进行中的角色。需要重开请发送 /jy重置 confirm。")
            return
        player = new_player(self._user_id(event), self._nickname(event), sect_name, difficulty)
        self._save(event, player)
        sect = SECTS[sect_name]
        yield event.plain_result(
            f"开局成功：{sect_name}（{sect.camp}）｜难度：{difficulty}\n"
            f"属性：{format_attrs(sect_name)}\n"
            f"初始武学：{'、'.join(sect.skills)}\n"
            "发送 /jy踢门 开启第1层第1个事件门。"
        )

    @filter.command("jy状态", alias={"金庸状态", "踢门状态"})
    async def cmd_status(self, event: AstrMessageEvent) -> AsyncGenerator:
        player, message = self._get_player_or_message(event)
        if player is None:
            yield event.plain_result(message)
            return
        yield event.plain_result(status_text(player))

    @filter.command("jy踢门", alias={"金庸踢门", "踢门"})
    async def cmd_kick(self, event: AstrMessageEvent) -> AsyncGenerator:
        player, message = self._get_player_or_message(event)
        if player is None:
            yield event.plain_result(message)
            return
        text = open_door(player)
        self._save(event, player)
        yield event.plain_result(text)

    @filter.command("jy下一层", alias={"金庸下一层", "踢门下一层"})
    async def cmd_next_floor(self, event: AstrMessageEvent) -> AsyncGenerator:
        player, message = self._get_player_or_message(event)
        if player is None:
            yield event.plain_result(message)
            return
        text = next_floor(player)
        self._save(event, player)
        yield event.plain_result(text)

    @filter.command("jy钓鱼", alias={"金庸钓鱼", "武侠钓鱼"})
    async def cmd_fish(self, event: AstrMessageEvent) -> AsyncGenerator:
        player, message = self._get_player_or_message(event)
        if player is None:
            yield event.plain_result(message)
            return
        parts = event.message_str.strip().split()
        spot = parts[1] if len(parts) >= 2 else "山涧浅滩"
        bait = parts[2] if len(parts) >= 3 else "普通蚯蚓饵"
        if spot == "列表":
            yield event.plain_result(f"钓点：{'、'.join(FISHING_SPOTS)}\n饵剂：{'、'.join(BAITS)}")
            return
        text = fish(player, spot, bait)
        self._save(event, player)
        yield event.plain_result(text)

    @filter.command("jy重置", alias={"金庸重置", "踢门重置"})
    async def cmd_reset(self, event: AstrMessageEvent) -> AsyncGenerator:
        parts = event.message_str.strip().split()
        if len(parts) < 2 or parts[1].lower() != "confirm":
            yield event.plain_result("这会删除当前金庸踢门团角色。确认请发送：/jy重置 confirm")
            return
        deleted = self.store.delete_player(self._user_id(event))
        yield event.plain_result("角色档案已删除，可重新 /jy开局。" if deleted else "当前没有可删除的角色档案。")
