from __future__ import annotations

import hashlib
import re
from pathlib import Path
from uuid import uuid4


ASSET_DIR = Path(__file__).resolve().parent / "assets" / "backgrounds"

SCENE_META = {
    "battle": {"title": "⚔️ 战斗门", "bg": "battle.jpg", "accent": (220, 80, 60)},
    "chest": {"title": "📦 宝箱门", "bg": "chest.jpg", "accent": (230, 170, 50)},
    "encounter": {"title": "🍃 奇遇门", "bg": "encounter.jpg", "accent": (90, 190, 120)},
    "trap": {"title": "⚠️ 陷阱门", "bg": "trap.jpg", "accent": (140, 160, 120)},
    "merchant": {"title": "🏪 商人门", "bg": "merchant.jpg", "accent": (210, 150, 70)},
    "fishing": {"title": "🎣 清溪垂钓", "bg": "fishing.jpg", "accent": (80, 160, 200)},
    "boss": {"title": "👑 武神殿", "bg": "boss.jpg", "accent": (200, 130, 160)},
    "inventory": {"title": "🎒 背囊行囊", "bg": "inventory.jpg", "accent": (180, 140, 90)},
    "meta": {"title": "⭐ 局外修行", "bg": "meta.jpg", "accent": (130, 160, 200)},
    "status": {"title": "👤 侠客状态", "bg": "status.jpg", "accent": (130, 160, 200)},
    "combat": {"title": "⚔️ 刀光剑影", "bg": "battle.jpg", "accent": (220, 70, 70)},
    "tower": {"title": "🏯 武道塔", "bg": "tower.jpg", "accent": (130, 160, 200)},
    "floor_square": {"title": "🏛️ 古武殿", "bg": "floor_square.jpg", "accent": (180, 150, 100)},
    "opening": {"title": "🏯 武道塔 · 缘起", "bg": "tower.jpg", "accent": (200, 170, 120)},
}


def infer_scene(text: str, fallback: str = "tower") -> str:
    if "战斗" in text and "HP" in text and "AC" in text:
        return "combat"
    markers = (
        ("【战斗门】", "battle"),
        ("【宝箱门】", "chest"),
        ("【奇遇门】", "encounter"),
        ("【陷阱门】", "trap"),
        ("【商人门】", "merchant"),
        ("【钓鱼】", "fishing"),
        ("【武神殿】", "boss"),
        ("【背包】", "inventory"),
        ("【局外强化】", "meta"),
        ("【金庸踢门团】", "status"),
        ("【古武殿】", "floor_square"),
        ("【武道塔】", "opening"),
        ("· 古武殿", "floor_square"),
        ("层 · ", "floor_square"),
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
    accent = meta["accent"]

    # Parse player status from text for UI rendering
    player_info = _parse_player_status(body)
    content_lines = _plain_body_lines(body)

    # ===== IMAGE SETUP =====
    bg_path = ASSET_DIR / str(meta["bg"])
    card_width = 700
    line_h = 24

    # Calculate content height
    draw_probe = ImageDraw.Draw(Image.new("RGB", (100, 100)))
    font_content = _load_font(ImageFont, 15)
    font_small = _load_font(ImageFont, 13)

    content_blocks = []
    for line in content_lines:
        wrapped = _wrap_text(draw_probe, line, font_content, 420)
        content_blocks.append((line, wrapped))

    hint_blocks = []
    if hint:
        hint_blocks = _wrap_text(draw_probe, hint, font_small, 620)

    # Total height calculation
    content_height = sum(max(28, len(w) * line_h + 10) for _, w in content_blocks)
    hint_height = len(hint_blocks) * 20 + 30 if hint_blocks else 0
    total_height = 130 + content_height + hint_height + 50  # Header + Content + Hint + Footer
    total_height = max(total_height, 420)

    # ===== LOAD BACKGROUND =====
    base = _load_background(Image, bg_path, card_width, total_height)

    # ===== UI LAYERS =====
    overlay = Image.new("RGBA", (card_width, total_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Darken edges (vignette effect) - keep center bright
    for y in range(total_height):
        edge_factor = min(1.0, abs(y - total_height / 2) / (total_height / 2.5))
        alpha = int(60 * edge_factor)
        draw.line((0, y, card_width, y), fill=(0, 0, 0, alpha))

    # ===== TOP HEADER BAR (Game Title) =====
    # Header background gradient
    header_h = 55
    for y in range(header_h):
        alpha = 180 - int(y * 0.5)
        draw.line((0, y, card_width, y), fill=(15, 12, 8, alpha))

    # Header border lines
    draw.line((0, header_h - 1, card_width, header_h - 1), fill=(*accent, 220), width=2)
    draw.line((0, header_h, card_width, header_h), fill=(200, 170, 120, 100), width=1)

    # Title text
    font_title = _load_font(ImageFont, 22, bold=True)
    draw.text((35, 12), meta["title"], font=font_title, fill=(255, 235, 190, 255))

    # Decorative corners
    _draw_decor_corner(draw, 10, 8, "tl", accent)
    _draw_decor_corner(draw, card_width - 10, 8, "tr", accent)

    # ===== LEFT SIDEBAR - Player Status =====
    if player_info:
        sidebar_w = 200
        sidebar_x = 25
        sidebar_y = 70

        # Sidebar background
        draw.rounded_rectangle(
            (sidebar_x, sidebar_y, sidebar_x + sidebar_w, sidebar_y + 290),
            radius=8, fill=(20, 15, 10, 160), outline=(180, 150, 100, 140), width=2
        )

        y = sidebar_y + 10
        font_stat_label = _load_font(ImageFont, 12)
        font_stat_value = _load_font(ImageFont, 14)

        # Player name if available
        if player_info.get("name"):
            draw.text((sidebar_x + 15, y), f"👤 {player_info['name'][:8]}", font=font_stat_value, fill=(255, 230, 180, 255))
            y += 28

        # HP Bar
        hp, max_hp = player_info.get("hp", 0), player_info.get("max_hp", 100)
        _draw_status_bar(draw, sidebar_x + 15, y, 170, 18, "HP", hp, max_hp, (220, 70, 70), font_stat_label)
        y += 28

        # MP Bar
        mp, max_mp = player_info.get("mp", 0), player_info.get("max_mp", 50)
        _draw_status_bar(draw, sidebar_x + 15, y, 170, 18, "MP", mp, max_mp, (70, 140, 220), font_stat_label)
        y += 28

        # Silver
        draw.text((sidebar_x + 15, y), f"💰 碎银: {player_info.get('silver', 0)}两", font=font_stat_label, fill=(220, 200, 160, 255))
        y += 22

        # Floor progress
        draw.text((sidebar_x + 15, y), f"📍 第{player_info.get('floor', 1)}层", font=font_stat_label, fill=(200, 180, 140, 255))
        y += 22

        # Sect if available
        if player_info.get("sect"):
            draw.text((sidebar_x + 15, y), f"🏛️ {player_info['sect'][:6]}", font=font_stat_label, fill=(180, 200, 230, 255))
            y += 22

        if player_info.get("ac") is not None:
            draw.text((sidebar_x + 15, y), f"🛡️ AC: {player_info['ac']}", font=font_stat_label, fill=(230, 220, 190, 255))
            y += 22

        if player_info.get("status"):
            status_text = f"状态: {player_info['status']}"
            for line in _wrap_text(draw, status_text, font_stat_label, 170)[:2]:
                draw.text((sidebar_x + 15, y), line, font=font_stat_label, fill=(230, 205, 150, 255))
                y += 18

        if player_info.get("attrs"):
            y += 4
            draw.text((sidebar_x + 15, y), "属性", font=font_stat_label, fill=(255, 230, 180, 255))
            y += 18
            for line in _wrap_text(draw, player_info["attrs"], font_stat_label, 170)[:3]:
                draw.text((sidebar_x + 15, y), line, font=font_stat_label, fill=(215, 225, 235, 255))
                y += 18

        if player_info.get("equipment"):
            y += 4
            draw.text((sidebar_x + 15, y), "装备", font=font_stat_label, fill=(255, 230, 180, 255))
            y += 18
            for line in _wrap_text(draw, player_info["equipment"], font_stat_label, 170)[:3]:
                draw.text((sidebar_x + 15, y), line, font=font_stat_label, fill=(220, 210, 190, 255))
                y += 18

        # Content area offset
        content_x = 250
        content_w = 430
    else:
        # No player info - use full width
        content_x = 40
        content_w = 620

    # ===== CONTENT AREA =====
    content_y = 70

    # Content panel background
    content_total_h = total_height - content_y - (hint_height + 30 if hint_blocks else 30)
    draw.rounded_rectangle(
        (content_x, content_y, content_x + content_w, content_y + content_total_h),
        radius=10, fill=(10, 8, 6, 110), outline=(160, 130, 90, 120), width=2
    )

    # Inner glow effect
    draw.rounded_rectangle(
        (content_x + 2, content_y + 2, content_x + content_w - 2, content_y + content_total_h - 2),
        radius=9, outline=(*accent, 40), width=1
    )

    # Draw content lines
    y = content_y + 15
    for original_line, wrapped in content_blocks:
        block_h = max(28, len(wrapped) * line_h + 10)

        # Special line styling
        bg_fill, text_fill, border_fill = _get_line_style(original_line, accent)

        # Draw line background
        draw.rounded_rectangle(
            (content_x + 12, y, content_x + content_w - 12, y + block_h),
            radius=6, fill=bg_fill, outline=border_fill, width=1
        )

        # Draw wrapped text
        ty = y + 5
        for wline in wrapped:
            draw.text((content_x + 22, ty), wline, font=font_content, fill=text_fill)
            ty += line_h

        y += block_h + 6

    # ===== HINT AREA =====
    if hint_blocks:
        hint_y = total_height - hint_height - 20
        draw.rounded_rectangle(
            (40, hint_y, card_width - 40, total_height - 15),
            radius=8, fill=(*accent, 35), outline=(*accent, 150), width=2
        )

        ty = hint_y + 8
        for hline in hint_blocks:
            draw.text((55, ty), hline, font=font_small, fill=(255, 245, 220, 255))
            ty += 20

    # ===== OUTER FRAME =====
    draw.rounded_rectangle((4, 4, card_width - 4, total_height - 4),
                           radius=14, outline=(200, 170, 120, 90), width=3)
    draw.rounded_rectangle((1, 1, card_width - 1, total_height - 1),
                           radius=15, outline=(220, 190, 140, 50), width=1)

    # Bottom decoration
    draw.rounded_rectangle((card_width // 2 - 50, total_height - 8, card_width // 2 + 50, total_height - 5),
                           radius=2, fill=(*accent, 180))

    # Compose final image
    final = Image.alpha_composite(base.convert("RGBA"), overlay)

    # Save
    output_dir.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha1(f"{scene}\n{text}".encode("utf-8")).hexdigest()[:10]
    output = output_dir / f"jinyong_card_{digest}_{uuid4().hex[:6]}.png"
    final.convert("RGB").save(output, "PNG", optimize=True)
    return output


def _draw_status_bar(draw, x, y, w, h, label, current, max_val, color, font):
    # Background
    draw.rounded_rectangle((x, y, x + w, y + h), radius=4, fill=(40, 30, 25, 200), outline=(100, 80, 60, 180), width=1)
    # Bar fill
    fill_w = max(2, int((w - 2) * min(1.0, current / max_val)))
    draw.rounded_rectangle((x + 1, y + 1, x + fill_w, y + h - 1), radius=3, fill=(*color, 220))
    # Text
    draw.text((x + 5, y + 2), f"{label}: {current}/{max_val}", font=font, fill=(255, 255, 255, 240))


def _draw_decor_corner(draw, x, y, pos, color):
    if pos in ("tl", "tr"):
        y2 = y + 35 if pos == "tl" else y - 35
        draw.line((x, y, x, y2), fill=(*color, 180), width=2)
        draw.line((x, y, x + (20 if pos == "tl" else -20), y), fill=(*color, 180), width=2)


def _get_line_style(line, accent):
    if any(k in line for k in ("胜利", "获得", "成功", "✓", "开局成功")):
        return (20, 60, 25, 140), (200, 255, 210, 255), (80, 180, 100, 160)
    if any(k in line for k in ("损失", "受到", "伤害", "失败", "✗")):
        return (60, 20, 20, 140), (255, 210, 210, 255), (200, 80, 80, 160)
    if any(k in line for k in ("d20=", "掷骰", "判定", "d100=")):
        return (20, 50, 80, 140), (220, 240, 255, 255), (100, 160, 220, 160)
    if any(k in line for k in ("第", "层", "门派", "武学")):
        return (40, 35, 20, 120), (250, 235, 210, 255), accent + (120,)
    return (5, 3, 2, 80), (248, 241, 223, 255), (180, 160, 130, 80)


def _parse_player_status(text):
    info = {}
    # Parse HP/MP
    hp_match = re.search(r"(?:HP|【气血】)[:：]?\s*(\d+)\/(\d+)", text)
    if hp_match:
        info["hp"], info["max_hp"] = int(hp_match.group(1)), int(hp_match.group(2))
    mp_match = re.search(r"(?:MP|【内力】)[:：]?\s*(\d+)\/(\d+)", text)
    if mp_match:
        info["mp"], info["max_mp"] = int(mp_match.group(1)), int(mp_match.group(2))

    # Parse silver
    silver_match = re.search(r"(?:碎银|【盘缠】)\s*(\d+)", text)
    if silver_match:
        info["silver"] = int(silver_match.group(1))

    # Parse floor
    floor_match = re.search(r"第(\d+)层", text)
    if floor_match:
        info["floor"] = int(floor_match.group(1))

    # Parse sect
    sect_match = re.search(r"(?:门派：|【门派】)([^｜\n（]+)", text)
    if sect_match:
        info["sect"] = sect_match.group(1).strip()

    # Parse armor class
    ac_match = re.search(r"\bAC\s*(\d+)", text)
    if ac_match:
        info["ac"] = int(ac_match.group(1))

    # Parse DND ability summary, status, and equipment from RPG HUD/status pages.
    attrs_match = re.search(r"(?:属性|【属性】)[：:]\s*([^\n║]+)", text)
    if attrs_match:
        info["attrs"] = attrs_match.group(1).strip(" ｜")

    status_match = re.search(r"状态[：:]\s*([^｜\n║]+)", text)
    if status_match:
        info["status"] = status_match.group(1).strip() or "暂无"

    equipment_match = re.search(r"装备[：:]\s*([^\n║]+)", text)
    if equipment_match:
        info["equipment"] = equipment_match.group(1).strip(" ｜")

    # Parse player name
    name_match = re.search(r"【金庸踢门团】\s*([^\n]+)", text)
    if name_match:
        info["name"] = name_match.group(1).strip()
    else:
        panel_name_match = re.search(r"【([^】\n]+)】门派：", text)
        if panel_name_match:
            info["name"] = panel_name_match.group(1).strip()

    return info


def _load_background(Image, path: Path, width: int, height: int):
    bg = Image.new("RGB", (width, height), (28, 23, 20))
    draw = ImageDraw.Draw(bg)
    for y in range(height):
        r = 28 + int(10 * (y / max(1, height)))
        g = 23 + int(8 * (y / max(1, height)))
        b = 20 + int(10 * (y / max(1, height)))
        draw.line((0, y, width, y), fill=(r, g, b))

    if path.is_file():
        try:
            img = Image.open(path).convert("RGB")
            scale = width / max(1, img.width)
            resized_h = max(1, int(img.height * scale))
            img = img.resize((width, resized_h), Image.Resampling.LANCZOS)
            if resized_h > height:
                img = img.crop((0, resized_h - height, width, resized_h))
                resized_h = height
            bg.paste(img, (0, height - resized_h))
            return bg.convert("RGBA")
        except Exception as e:
            print(f"Background load error: {e}")

    return bg.convert("RGBA")


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


def _split_hint(text: str) -> tuple[str, str]:
    parts = text.rsplit("\n\n下一步可用：", 1)
    if len(parts) == 2:
        return parts[0].strip(), "下一步可用：" + parts[1].strip()
    return text.strip(), ""


def _plain_body_lines(text: str) -> list[str]:
    lines = []
    for line in text.splitlines():
        line = line.strip()
        if line and not line.startswith("===") and not line.startswith("───"):
            lines.append(line)
    return lines or [" "]
