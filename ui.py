from __future__ import annotations

import hashlib
import re
from pathlib import Path
from uuid import uuid4


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


def render_card_image(text: str, scene: str, output_dir: Path) -> Path | None:
    try:
        from PIL import Image, ImageDraw, ImageFont
    except Exception:
        return None

    scene = scene if scene in SCENE_META else "tower"
    meta = SCENE_META[scene]
    body, hint = _split_hint(text)
    title = _extract_title(body, str(meta["title"]))
    lines = _plain_body_lines(body)
    bg_path = ASSET_DIR / str(meta["bg"])
    width = 600
    pad = 18
    gap = 7
    title_font = _load_font(ImageFont, 24, bold=True)
    tag_font = _load_font(ImageFont, 13)
    body_font = _load_font(ImageFont, 16)
    hint_font = _load_font(ImageFont, 14)

    draw_probe = ImageDraw.Draw(Image.new("RGB", (width, 20)))
    blocks = []
    for line in lines[:18]:
        wrapped = _wrap_text(draw_probe, line, body_font, width - pad * 2 - 20)
        kind = "major" if any(key in line for key in ("结果：", "获得", "通关奖励", "开局成功", "成功：", "自然20")) else "normal"
        if "d20=" in line or "d100=" in line or "掷骰=" in line:
            kind = "roll"
        blocks.append((kind, wrapped))
    if len(lines) > 18:
        blocks.append(("normal", [f"其余 {len(lines) - 18} 行请用 /金庸状态 或 /金庸背包 查看。"]))

    hint_lines = _wrap_text(draw_probe, hint, hint_font, width - pad * 2 - 20) if hint else []
    line_h = 24
    height = 20 + 36 + 12
    for _, wrapped in blocks:
        height += max(36, 14 + line_h * len(wrapped)) + gap
    if hint_lines:
        height += 14 + 22 * len(hint_lines) + 12
    height = min(max(height + 10, 190), 920)

    base = _load_background(Image, bg_path, width, height)
    overlay = Image.new("RGBA", (width, height), (9, 8, 7, 170))
    base = Image.alpha_composite(base.convert("RGBA"), overlay)
    draw = ImageDraw.Draw(base)

    tone = _hex_to_rgb(str(meta["tone"]))
    draw.rounded_rectangle((8, 8, width - 8, height - 8), radius=14, outline=(232, 210, 158, 108), width=1)
    draw.rectangle((0, 0, width, height), fill=(0, 0, 0, 32))

    x = pad
    y = 16
    draw.text((x, y), title, font=title_font, fill=(255, 226, 164, 255))
    tag = "金庸DND肉鸽"
    tag_w = draw.textlength(tag, font=tag_font)
    draw.text((width - pad - tag_w, y + 8), tag, font=tag_font, fill=(242, 217, 164, 205))
    y += 38
    draw.line((pad, y, width - pad, y), fill=(232, 210, 158, 72), width=1)
    y += 11

    for kind, wrapped in blocks:
        block_h = max(36, 14 + line_h * len(wrapped))
        if y + block_h > height - 22:
            break
        fill = (0, 0, 0, 82)
        outline = (255, 255, 255, 20)
        text_fill = (248, 241, 223, 255)
        if kind == "major":
            fill = (79, 51, 25, 108)
            outline = (255, 217, 147, 76)
            text_fill = (255, 243, 212, 255)
        elif kind == "roll":
            fill = (20, 44, 62, 100)
            outline = (166, 214, 255, 58)
            text_fill = (217, 236, 255, 255)
        draw.rounded_rectangle((pad, y, width - pad, y + block_h), radius=8, fill=fill, outline=outline, width=1)
        ty = y + 7
        for wrapped_line in wrapped:
            draw.text((pad + 10, ty), wrapped_line, font=body_font, fill=text_fill)
            ty += line_h
        y += block_h + gap

    if hint_lines and y < height - 20:
        hint_h = min(14 + 22 * len(hint_lines), height - y - 12)
        draw.rounded_rectangle((pad, y + 3, width - pad, y + 3 + hint_h), radius=8, fill=(*tone, 46), outline=(255, 226, 164, 58), width=1)
        ty = y + 10
        for wrapped_line in hint_lines:
            if ty + 18 > y + 3 + hint_h:
                break
            draw.text((pad + 10, ty), wrapped_line, font=hint_font, fill=(255, 232, 184, 255))
            ty += 22

    output_dir.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha1(f"{scene}\n{text}".encode("utf-8")).hexdigest()[:10]
    output = output_dir / f"jinyong_card_{digest}_{uuid4().hex[:6]}.png"
    base.convert("RGB").save(output, "PNG", optimize=True)
    return output


def _load_background(Image, path: Path, width: int, height: int):
    if path.is_file():
        try:
            img = Image.open(path).convert("RGB")
            src_ratio = img.width / max(1, img.height)
            dst_ratio = width / max(1, height)
            if src_ratio > dst_ratio:
                new_w = int(img.height * dst_ratio)
                left = (img.width - new_w) // 2
                img = img.crop((left, 0, left + new_w, img.height))
            else:
                new_h = int(img.width / dst_ratio)
                top = (img.height - new_h) // 2
                img = img.crop((0, top, img.width, top + new_h))
            return img.resize((width, height), Image.Resampling.LANCZOS).convert("RGBA")
        except Exception:
            pass
    return Image.new("RGBA", (width, height), (28, 24, 20, 255))


def _load_font(ImageFont, size: int, bold: bool = False):
    candidates = [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
        "/Library/Fonts/Arial Unicode.ttf",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
    ]
    for path in candidates:
        if Path(path).is_file():
            try:
                return ImageFont.truetype(path, size=size, index=0)
            except Exception:
                continue
    return ImageFont.load_default()


def _wrap_text(draw, text: str, font, max_width: int) -> list[str]:
    if not text:
        return []
    lines: list[str] = []
    current = ""
    for char in text:
        trial = current + char
        if current and draw.textlength(trial, font=font) > max_width:
            lines.append(current)
            current = char
        else:
            current = trial
    if current:
        lines.append(current)
    return lines


def _hex_to_rgb(value: str) -> tuple[int, int, int]:
    value = value.strip().lstrip("#")
    if len(value) != 6:
        return (111, 134, 167)
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


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


def _plain_body_lines(text: str) -> list[str]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if lines and re.match(r"^【[^】]+】", lines[0]):
        lines[0] = re.sub(r"^【[^】]+】", "", lines[0]).strip()
        if not lines[0]:
            lines = lines[1:]
    return lines or ["暂无内容。"]
