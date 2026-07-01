from __future__ import annotations

import base64
import html
import re
from pathlib import Path


ASSET_DIR = Path(__file__).resolve().parent / "assets" / "backgrounds"

SCENE_META = {
    "battle": {"title": "战斗门", "bg": "battle.jpg", "tone": "#b84a3a"},
    "chest": {"title": "宝箱门", "bg": "chest.jpg", "tone": "#c58a2c"},
    "encounter": {"title": "奇遇门", "bg": "encounter.jpg", "tone": "#6f9f7a"},
    "trap": {"title": "陷阱门", "bg": "trap.jpg", "tone": "#6f986d"},
    "merchant": {"title": "商人门", "bg": "merchant.jpg", "tone": "#b77a3d"},
    "fishing": {"title": "钓鱼", "bg": "fishing.jpg", "tone": "#4f8ea5"},
    "boss": {"title": "武神殿", "bg": "boss.jpg", "tone": "#8d5364"},
    "inventory": {"title": "背包", "bg": "merchant.jpg", "tone": "#9f7a49"},
    "meta": {"title": "局外强化", "bg": "tower.jpg", "tone": "#6f86a7"},
    "status": {"title": "角色状态", "bg": "tower.jpg", "tone": "#6f86a7"},
    "help": {"title": "指令", "bg": "tower.jpg", "tone": "#6f86a7"},
    "tower": {"title": "金庸踢门团", "bg": "tower.jpg", "tone": "#6f86a7"},
}

_BG_CACHE: dict[str, str] = {}


def infer_scene(text: str, fallback: str = "tower") -> str:
    markers = (
        ("【战斗门】", "battle"),
        ("【宝箱门】", "chest"),
        ("【奇遇门】", "encounter"),
        ("【陷阱门】", "trap"),
        ("【商人门】", "merchant"),
        ("【钓鱼】", "fishing"),
        ("【武神殿", "boss"),
        ("【武神殿通关】", "boss"),
        ("【背包】", "inventory"),
        ("【局外强化】", "meta"),
        ("【金庸踢门团】", "status"),
    )
    for marker, scene in markers:
        if marker in text:
            return scene
    return fallback


def render_card(text: str, scene: str = "tower") -> str:
    scene = scene if scene in SCENE_META else "tower"
    meta = SCENE_META[scene]
    body, hint = _split_hint(text)
    title = _extract_title(body, str(meta["title"]))
    bg = _background_data_url(str(meta["bg"]))
    tone = str(meta["tone"])
    body_html = _body_html(body)
    hint_html = f'<div class="hint">{html.escape(hint)}</div>' if hint else ""

    return f"""<render>
<style>
* {{ box-sizing: border-box; }}
body {{
  margin: 0;
  padding: 10px;
  width: 600px;
  background: transparent;
  font-family: "Noto Serif SC", "Noto Sans SC", "PingFang SC", "Microsoft YaHei", serif;
  color: #f8f1df;
}}
.jy-card {{
  position: relative;
  overflow: hidden;
  border-radius: 12px;
  border: 1px solid rgba(232, 210, 158, .42);
  background:
    linear-gradient(180deg, rgba(18, 15, 12, .86), rgba(22, 18, 14, .94)),
    url("{bg}");
  background-size: cover;
  background-position: center;
  box-shadow: 0 10px 26px rgba(0,0,0,.38);
}}
.jy-card::before {{
  content: "";
  position: absolute;
  inset: 0;
  background:
    linear-gradient(90deg, rgba(8,8,7,.82) 0%, rgba(8,8,7,.70) 48%, rgba(8,8,7,.48) 100%),
    radial-gradient(circle at 84% 8%, {tone}66, transparent 38%);
}}
.jy-inner {{
  position: relative;
  z-index: 1;
  padding: 16px 16px 14px;
}}
.jy-head {{
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(232, 210, 158, .28);
}}
.jy-title {{
  margin: 0;
  font-size: 22px;
  line-height: 1.2;
  letter-spacing: 0;
  color: #ffe2a4;
  font-weight: 700;
}}
.jy-tag {{
  flex: 0 0 auto;
  font-size: 12px;
  color: #f2d9a4;
  opacity: .82;
}}
.jy-body {{
  margin-top: 10px;
  display: grid;
  gap: 6px;
  font-size: 15px;
  line-height: 1.52;
}}
.line {{
  padding: 7px 9px;
  border-radius: 8px;
  background: rgba(0,0,0,.26);
  border: 1px solid rgba(255,255,255,.07);
  word-break: break-word;
}}
.line.major {{
  border-color: rgba(255, 217, 147, .30);
  background: rgba(79, 51, 25, .36);
  color: #fff3d4;
}}
.line.roll {{
  font-family: "Noto Sans SC", "PingFang SC", sans-serif;
  color: #d9ecff;
}}
.hint {{
  margin-top: 10px;
  padding: 8px 10px;
  border-radius: 8px;
  background: rgba(255, 226, 164, .13);
  border: 1px solid rgba(255, 226, 164, .22);
  color: #ffe8b8;
  font-size: 13px;
  line-height: 1.45;
  word-break: break-word;
}}
</style>
<div class="jy-card">
  <div class="jy-inner">
    <div class="jy-head">
      <h1 class="jy-title">{html.escape(title)}</h1>
      <div class="jy-tag">金庸DND肉鸽</div>
    </div>
    <div class="jy-body">{body_html}</div>
    {hint_html}
  </div>
</div>
</render>"""


def _background_data_url(filename: str) -> str:
    cached = _BG_CACHE.get(filename)
    if cached:
        return cached
    path = ASSET_DIR / filename
    if not path.is_file():
        return ""
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    data_url = f"data:image/jpeg;base64,{encoded}"
    _BG_CACHE[filename] = data_url
    return data_url


def _split_hint(text: str) -> tuple[str, str]:
    parts = text.rsplit("\n\n下一步可用：", 1)
    if len(parts) == 2:
        return parts[0].strip(), "下一步可用：" + parts[1].strip()
    return text.strip(), ""


def _extract_title(text: str, fallback: str) -> str:
    first = next((line.strip() for line in text.splitlines() if line.strip()), "")
    match = re.match(r"^【([^】]+)】", first)
    if match:
        return match.group(1)
    if first.startswith("开局成功"):
        return "开局成功"
    if first.startswith("可选门派"):
        return "门派选择"
    if first.startswith("用法"):
        return "指令提示"
    return fallback


def _body_html(text: str) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if lines and re.match(r"^【[^】]+】", lines[0]):
        lines[0] = re.sub(r"^【[^】]+】", "", lines[0]).strip()
        if not lines[0]:
            lines = lines[1:]

    html_lines = []
    for line in lines[:18]:
        css = "line"
        if any(key in line for key in ("结果：", "获得", "通关奖励", "开局成功", "成功：", "自然20")):
            css += " major"
        if "d20=" in line or "d100=" in line or "掷骰=" in line:
            css += " roll"
        html_lines.append(f'<div class="{css}">{html.escape(line)}</div>')
    if len(lines) > 18:
        html_lines.append(f'<div class="line">其余 {len(lines) - 18} 行请用 /金庸状态 或 /金庸背包 查看。</div>')
    return "".join(html_lines) or '<div class="line">暂无内容。</div>'
