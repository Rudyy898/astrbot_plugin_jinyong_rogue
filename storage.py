from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class JsonStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def load_all(self) -> dict[str, Any]:
        if not self.path.exists():
            return {}
        try:
            data = json.loads(self.path.read_text("utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}
        return data if isinstance(data, dict) else {}

    def save_all(self, data: dict[str, Any]) -> None:
        self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def get_player(self, user_id: str) -> dict[str, Any] | None:
        data = self.load_all()
        player = data.get(user_id)
        return player if isinstance(player, dict) else None

    def put_player(self, user_id: str, player: dict[str, Any]) -> None:
        data = self.load_all()
        data[user_id] = player
        self.save_all(data)

    def delete_player(self, user_id: str) -> bool:
        data = self.load_all()
        existed = user_id in data
        data.pop(user_id, None)
        self.save_all(data)
        return existed
