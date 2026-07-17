from __future__ import annotations

import hashlib
import re
from pathlib import Path
from uuid import uuid4

try:
    from PIL import Image, ImageDraw, ImageFont
except Exception:
    Image = ImageDraw = ImageFont = None

# Sect basic skills mapping: {sect_name: {skill_name: mp_cost}}
SECT_BASIC_SKILLS = {
    "少林": {"罗汉拳": 0, "金刚掌": 0, "大韦陀杵": 1},
    "武当": {"太极拳": 0, "太极剑": 1, "武当长拳": 0},
    "峨眉": {"峨眉剑法": 0, "峨嵋九阳功": 1, "金顶绵掌": 0},
    "全真": {"全真剑法": 0, "先天功": 1, "昊天掌": 0},
    "华山": {"华山长拳": 0, "华山剑法": 1, "养气诀": 0},
    "丐帮": {"降龙十八掌基础式": 1, "打狗棒法": 1, "太祖长拳": 0},
    "明教": {"圣火令法": 1, "乾坤大挪移残篇": 1, "大九天手": 0},
    "青城": {"青城剑法": 0, "催心掌": 1, "松风剑法": 1},
    "雪山派": {"雪山剑法": 1, "寒冰神掌": 1, "金乌刀法": 1},
    "大理段氏": {"一阳指初阶": 1, "段家剑法": 0, "段氏吐纳法": 0},
    "逍遥派": {"天山折梅手": 1, "北冥吐纳法": 0, "凌波微步初阶": 0},
    "金刚宗": {"金刚拳初阶": 1, "火焰刀初阶": 1, "大手印": 0},
    "桃花岛": {"落英神剑掌": 1, "弹指神通": 1, "玉箫剑法": 0},
    "日月神教": {"葵花宝典残篇": 1, "吸星大法": 1, "日月神剑": 0},
    "血刀门": {"血刀刀法初阶": 1, "嗜血心法": 1, "血洗山河": 2},
    "白驼山庄": {"白驼蛇毒掌": 1, "蛤蟆功初阶": 1, "灵蛇拳法": 0},
}

# Real skill MP cost data from SKILL_COMBAT_ROWS and MARTIAL_ART_SKILL_ROWS
SKILL_MP_COST = {
    # === 基础武学 (SKILL_COMBAT_ROWS) ===
    # 少林
    "罗汉拳": 0,
    "易筋经残篇": 1,
    # 武当
    "太极拳": 0,
    "太极剑": 1,
    # 峨眉
    "峨眉剑法": 0,
    "峨嵋九阳功": 1,
    # 全真
    "全真剑法": 0,
    "先天功": 1,
    # 华山
    "华山长拳": 0,
    "华山剑法": 1,
    "养气诀": 0,
    # 丐帮
    "降龙十八掌基础式": 1,
    "打狗棒法": 1,
    # 明教
    "乾坤大挪移残篇": 1,
    "圣火令法": 1,
    # 青城
    "青城剑法": 0,
    "催心掌": 1,
    # 雪山派
    "雪山剑法": 1,
    "寒冰神掌": 1,
    # 大理段氏
    "一阳指初阶": 1,
    "段家剑法": 0,
    "段氏吐纳法": 0,
    # 逍遥派
    "天山折梅手": 1,
    "北冥吐纳法": 0,
    "凌波微步初阶": 0,
    # 金刚宗
    "金刚拳初阶": 1,
    "火焰刀初阶": 1,
    # 桃花岛
    "落英神剑掌": 1,
    "弹指神通": 1,
    # 日月神教
    "葵花宝典残篇": 1,
    "吸星大法": 1,
    # 血刀门
    "血刀刀法初阶": 1,
    "嗜血心法": 1,
    "血洗山河": 2,
    # 白驼山庄
    "白驼蛇毒掌": 1,
    "蛤蟆功初阶": 1,

    # === 进阶武学 (MARTIAL_ART_SKILL_ROWS - 全部 MP=2 或 3) ===
    # 华山
    "狂风快剑": 2,
    "夺命连环三仙剑": 3,
    # 少林
    "大金刚拳": 2,
    "袈裟伏魔功": 2,
    # 武当
    "绕指柔剑": 2,
    "震山铁掌": 2,
    # 峨眉
    "金顶绵掌": 2,
    "灭剑绝式": 2,
    # 全真
    "三花聚顶掌": 2,
    "七星剑式": 2,
    # 丐帮
    "亢龙初式": 3,
    "缠字诀棒法": 2,
    # 明教
    "烈焰圣火掌": 2,
    "乾坤挪劲": 2,
    # 青城
    "松风快剑": 2,
    "摧心毒掌": 2,
    # 雪山派
    "雪影连环剑": 2,
    "冰魄神掌": 2,
    # 大理段氏
    "一阳指中阶": 2,
    "段氏连环剑": 2,
    # 逍遥派
    "天山六阳掌初悟": 2,
    "凌波错影击": 2,
    # 金刚宗
    "大力金刚指": 3,
    "炽焰刀气": 2,
    # 桃花岛
    "落英缤纷掌": 2,
    "玉箫剑式": 2,
    # 日月神教
    "葵花迷影刺": 2,
    "吸星缠劲": 2,
    # 血刀门
    "血刀连斩": 3,
    "血影追魂": 2,
    # 白驼山庄
    "白驼毒砂掌": 2,
    "蛤蟆吐劲": 3,
}

# Merge all basic sect skills into SKILL_MP_COST
for sect_skills in SECT_BASIC_SKILLS.values():
    SKILL_MP_COST.update(sect_skills)

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
    "tower": {"title": "🏯 武神塔", "bg": "tower.jpg", "accent": (130, 160, 200)},
    "floor_square": {"title": "🏛️ 古武殿", "bg": "floor_square.jpg", "accent": (180, 150, 100)},
    "opening": {"title": "🏯 武神塔 · 缘起", "bg": "tower.jpg", "accent": (200, 170, 120)},
}


def infer_scene(text: str, fallback: str = "tower") -> str:
    if "战斗" in text and "HP" in text and "AC" in text:
        return "combat"
    markers = (
        ("【战斗门】", "battle"),
        ("【宝箱门】", "chest"),
        ("【奇遇门】", "encounter"),
        ("【陷阱门】", "trap"),
        ("【背包】", "inventory"),
        ("【商人门】", "merchant"),
        ("【钓鱼】", "fishing"),
        ("【武神殿】", "boss"),
        ("【局外强化】", "meta"),
        ("【金庸踢门团】", "status"),
        ("【古武殿】", "floor_square"),
        ("【武神塔】", "opening"),
        ("· 古武殿", "floor_square"),
        ("层 · ", "floor_square"),
    )
    for marker, scene in markers:
        if marker in text:
            return scene
    return fallback


def render_card_image(text: str, scene: str, output_dir: Path, player: dict | None = None) -> Path | None:
    if Image is None or ImageDraw is None or ImageFont is None:
        return None

    scene = scene if scene in SCENE_META else "tower"
    meta = SCENE_META[scene]
    body, hint = _split_hint(text)
    accent = meta["accent"]

    # Get player info directly from player object (100% accurate)
    # Filter out status lines from content to avoid duplication
    content_lines = []
    if player is None:
        # No player object - try to parse from text as fallback
        player_info = _parse_player_status(body)
        content_lines = _plain_body_lines(body)
    elif player.get("finished") or player.get("frozen") or player.get("game_over"):
        player_info = {}
        content_lines = _plain_body_lines(body)
    else:
        # Build player info DIRECTLY from player object - GUARANTEED ACCURATE
        player_info = _build_player_info_from_object(player)
        # Filter content to REMOVE status lines (they will be in sidebar only)
        content_lines = _filter_content_lines(body)

    # ===== IMAGE SETUP =====
    bg_path = ASSET_DIR / str(meta["bg"])
    card_width = 700
    max_card_height = 900

    # Calculate content height
    draw_probe = ImageDraw.Draw(Image.new("RGB", (100, 100)))
    font_size = 18
    line_h = 24
    font_content = _load_font(font_size, bold=True)
    font_small = _load_font(16, bold=True)
    hint_blocks = _wrap_text(draw_probe, hint, font_small, 620) if hint else []
    hint_height = len(hint_blocks) * 20 + 30 if hint_blocks else 0
    base_header = 70  # Top header bar with title
    status_bar_height = 174 if player is not None else 0

    while True:
        font_content = _load_font(font_size, bold=True)
        content_blocks = [
            (line, _wrap_text(draw_probe, line, font_content, 620))
            for line in content_lines
        ]
        content_height = sum(max(line_h, len(w) * line_h) + 4 for _, w in content_blocks)
        total_height = base_header + status_bar_height + content_height + hint_height + 30
        if total_height <= max_card_height or font_size <= 14:
            break
        font_size -= 1
        line_h = max(19, line_h - 1)

    total_height = max(450, min(total_height, max_card_height))
    content_available_h = total_height - (base_header + status_bar_height) - hint_height - 75
    content_blocks = _fit_content_blocks(content_blocks, content_available_h, line_h)

    # ===== LOAD BACKGROUND =====
    base = _load_background(bg_path, card_width, total_height)

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

    # Title text with stroke
    font_title = _load_font(26, bold=True)
    tx, ty = 35, 12
    # Title stroke
    draw.text((tx - 1, ty), meta["title"], font=font_title, fill=(30, 20, 10, 255))
    draw.text((tx + 1, ty), meta["title"], font=font_title, fill=(30, 20, 10, 255))
    draw.text((tx, ty - 1), meta["title"], font=font_title, fill=(30, 20, 10, 255))
    draw.text((tx, ty + 1), meta["title"], font=font_title, fill=(30, 20, 10, 255))
    draw.text((tx, ty), meta["title"], font=font_title, fill=(255, 245, 220, 255))

    # Decorative corners
    _draw_decor_corner(draw, 10, 8, "tl", accent)
    _draw_decor_corner(draw, card_width - 10, 8, "tr", accent)

    # ===== HORIZONTAL STATUS BAR - Player Status (TOP ALIGNED, MONOSPACE) =====
    if player_info:
        status_x = 30
        status_y = 70
        status_w = card_width - 60
        status_h = 174  # Compact horizontal layout + XP/equipment/skill rows

        # Status bar background - single horizontal panel
        draw.rounded_rectangle(
            (status_x, status_y, status_x + status_w, status_y + status_h),
            radius=8, fill=(20, 15, 10, 180), outline=(180, 150, 100, 140), width=2
        )

        # Use MONOSPACE font for aligned columns
        font_mono = _load_font(15, bold=True)  # Monospace for column alignment
        font_mono_small = _load_font(13, bold=True)
        font_mono_skill = _load_font(12, bold=True)

        y = status_y + 8
        col_gap = 20  # Gap between columns

        # === ROW 1: Name | Sect | Level | Floor | AC ===
        x = status_x + 15
        # Name
        name_text = player_info.get("name", "侠客")[:8]
        draw.text((x, y), f"👤 {name_text:<8s}", font=font_mono, fill=(255, 230, 180, 255))
        x += 120
        # Sect
        sect_text = player_info.get("sect", "无门无派")[:6]
        draw.text((x, y), f"🏛️ {sect_text:<6s}", font=font_mono, fill=(180, 200, 230, 255))
        x += 110
        # Level (NEW!)
        level_text = f"Lv{player_info.get('level', 1)}"
        draw.text((x, y), f"⭐ {level_text:<4s}", font=font_mono, fill=(255, 215, 0, 255))
        x += 80
        # Floor
        floor_text = f"第{player_info.get('floor', 1)}层"
        draw.text((x, y), f"📍 {floor_text:<5s}", font=font_mono, fill=(200, 180, 140, 255))
        x += 90
        # AC
        ac_text = f"AC {player_info.get('ac', 10)}"
        draw.text((x, y), f"🛡️ {ac_text:<5s}", font=font_mono, fill=(230, 220, 190, 255))
        x += 80
        # Silver
        silver_text = f"{player_info.get('silver', 0)}两"
        draw.text((x, y), f"💰 {silver_text:<6s}", font=font_mono, fill=(220, 200, 160, 255))

        y += 26

        # === ROW 2: HP Bar | MP Bar ===
        hp, max_hp = player_info.get("hp", 0), player_info.get("max_hp", 100)
        mp, max_mp = player_info.get("mp", 0), player_info.get("max_mp", 50)

        # HP Bar (wider for horizontal layout)
        _draw_status_bar(draw, status_x + 15, y, 220, 20, "HP", hp, max_hp, (220, 70, 70), font_mono_small)
        # MP Bar next to HP
        _draw_status_bar(draw, status_x + 250, y, 220, 20, "MP", mp, max_mp, (70, 140, 220), font_mono_small)

        # Status text on the right
        if player_info.get("status") and player_info["status"] != "暂无":
            status_text = player_info["status"][:12]
            draw.text((status_x + 525, y + 2), f"📌 {status_text}", font=font_mono_small, fill=(230, 205, 150, 255))

        y += 28

        # === ROW 3: XP Bar (经验条) ===
        level = player_info.get("level", 1)
        current_xp = player_info.get("xp", 0)
        from .game_data import LEVEL_UP_XP, MAX_LEVEL
        if level < MAX_LEVEL:
            next_xp = LEVEL_UP_XP.get(level + 1, 0)
            prev_xp = LEVEL_UP_XP.get(level, 0)
            progress_xp = current_xp - prev_xp
            required_xp = next_xp - prev_xp
        else:
            progress_xp = 100
            required_xp = 100
        _draw_status_bar(draw, status_x + 15, y, 455, 16, "EXP", progress_xp, required_xp, (255, 200, 50), font_mono_small)

        y += 24

        # === ROW 4: DND 6 ABILITIES (FULL MONOSPACE ALIGNED) ===
        # Get DND-style attribute values directly from sect
        from .engine import SECTS
        sect = SECTS.get(player_info.get("sect", ""), None)
        if sect:
            attrs = sect.attrs  # {str, dex, con, int, wis, cha}
            # Format: STR+2 DEX+0 CON+3 INT+1 WIS+0 CHA+0 (monospace aligned)
            attr_str = (f"力{attrs.get('str', 0):+2d}  "
                       f"敏{attrs.get('dex', 0):+2d}  "
                       f"体{attrs.get('con', 0):+2d}  "
                       f"智{attrs.get('int', 0):+2d}  "
                       f"感{attrs.get('wis', 0):+2d}  "
                       f"魅{attrs.get('cha', 0):+2d}")
            draw.text((status_x + 15, y), f"📊 {attr_str}", font=font_mono, fill=(215, 225, 235, 255))
        elif player_info.get("attrs"):
            # Fallback to parsed attrs
            draw.text((status_x + 15, y), f"📊 {player_info['attrs']}", font=font_mono, fill=(215, 225, 235, 255))

        y += 24

        # === ROW 5: EQUIPMENT (split slots) ===
        equipment_slots = player_info.get("equipment_slots", {})
        def short_equipment(slot: str) -> str:
            name = equipment_slots.get(slot) or "无"
            return name if len(name) <= 8 else name[:8]

        equipment_line = "  ".join([
            f"奇器:{short_equipment('accessory')}",
            f"武器:{short_equipment('weapon')}",
            f"护甲:{short_equipment('armor')}",
        ])
        draw.text((status_x + 15, y), f"🎒 {equipment_line}", font=font_mono_skill, fill=(230, 205, 150, 255))

        y += 24

        # === ROW 6: SKILLS (compact inline display) ===
        basic_skills = list(player_info.get("sect_skills", {}).keys())
        learned_skills = player_info.get("skills", [])
        all_skills = basic_skills + learned_skills
        active_skill = player_info.get("active_skill", "自动")

        if all_skills:
            skill_texts = []
            for skill_name in all_skills[:5]:  # Show up to 5 skills inline
                is_active = skill_name == active_skill or (active_skill == "自动" and skill_name == all_skills[0])
                mp_cost = SKILL_MP_COST.get(skill_name, 0)
                prefix = "★" if is_active else " "
                mp_text = f"({mp_cost})" if mp_cost > 0 else ""
                skill_texts.append(f"{prefix}{skill_name}{mp_text}")

            skills_line = "  ".join(skill_texts)
            draw.text((status_x + 15, y), f"⚔️ {skills_line}", font=font_mono_skill, fill=(255, 210, 120, 255))
        else:
            draw.text((status_x + 15, y), "⚔️ 暂未习得武学", font=font_mono_skill, fill=(180, 170, 150, 255))

        # Content area starts BELOW status bar
        content_x = 40
        content_w = card_width - 80  # Full width content
        content_y = status_y + status_h + 15
    else:
        # No player info - use full width
        content_x = 40
        content_w = 620
        content_y = 70

    # ===== CONTENT AREA ===== - MUD STYLE (CLEAN TEXT, NO BORDERS)

    # Simple semi-transparent background panel
    content_total_h = total_height - content_y - 25
    draw.rounded_rectangle(
        (content_x, content_y, content_x + content_w, content_y + content_total_h),
        radius=8, fill=(10, 8, 6, 180), outline=(120, 100, 70, 100), width=1
    )

    # Draw content lines - MUD style (just clean text, no per-line boxes)
    y = content_y + 20
    stroke_color = (0, 0, 0, 220)  # Text stroke for readability

    for original_line, wrapped in content_blocks:
        if y + line_h > content_y + content_total_h - 8:
            break
        # Get line color based on type
        _, text_fill, _ = _get_line_style(original_line, accent)

        # MUD-style - just text, no per-line backgrounds or borders
        ty = y
        for wline in wrapped:
            if ty + line_h > content_y + content_total_h - 8:
                break
            tx, tyy = content_x + 20, ty
            # Draw stroke for readability on dark background
            draw.text((tx - 1, tyy), wline, font=font_content, fill=stroke_color)
            draw.text((tx + 1, tyy), wline, font=font_content, fill=stroke_color)
            draw.text((tx, tyy - 1), wline, font=font_content, fill=stroke_color)
            draw.text((tx, tyy + 1), wline, font=font_content, fill=stroke_color)
            # Bright text for MUD readability
            bright_text = (255, 250, 240, 255) if text_fill[3] > 200 else text_fill
            draw.text((tx, tyy), wline, font=font_content, fill=bright_text)
            ty += line_h

        # Tight line spacing like MUD
        y += max(line_h * len(wrapped), line_h) + 4

    # ===== HINT AREA =====
    if hint_blocks:
        hint_y = total_height - hint_height - 20
        draw.rounded_rectangle(
            (40, hint_y, card_width - 40, total_height - 15),
            radius=8, fill=(*accent, 35), outline=(*accent, 150), width=2
        )

        ty = hint_y + 8
        stroke_color = (0, 0, 0, 200)
        for hline in hint_blocks:
            tx = 55
            # Stroke for hint text
            draw.text((tx - 1, ty), hline, font=font_small, fill=stroke_color)
            draw.text((tx + 1, ty), hline, font=font_small, fill=stroke_color)
            draw.text((tx, ty - 1), hline, font=font_small, fill=stroke_color)
            draw.text((tx, ty + 1), hline, font=font_small, fill=stroke_color)
            draw.text((tx, ty), hline, font=font_small, fill=(255, 250, 235, 255))
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

    # Parse learned skills (advanced skills)
    skills_match = re.search(r"已学进阶武学[：:]\s*([^\n]+)", text)
    if skills_match:
        skills_text = skills_match.group(1).strip()
        if skills_text and skills_text != "暂无":
            info["skills"] = [s.strip() for s in skills_text.split("、") if s.strip()]
        else:
            info["skills"] = []
    else:
        info["skills"] = []

    # Parse active skill
    active_skill_match = re.search(r"当前技能[：:]\s*([^\n]+)", text)
    if active_skill_match:
        info["active_skill"] = active_skill_match.group(1).strip()
    else:
        info["active_skill"] = "自动"

    # Get sect basic skills from our mapping (not from text) - dict with name: mp_cost
    sect_name = info.get("sect", "")
    if sect_name in SECT_BASIC_SKILLS:
        info["sect_skills"] = SECT_BASIC_SKILLS[sect_name]
    else:
        # Fallback - try to detect sect from text
        for sect in SECT_BASIC_SKILLS:
            if sect in text:
                info["sect_skills"] = SECT_BASIC_SKILLS[sect]
                break
        else:
            info["sect_skills"] = {}

    return info


def _build_player_info_from_object(player: dict) -> dict:
    """
    Build player info DIRECTLY from the player object (100% accurate, real-time).
    NO TEXT PARSING - just raw data access!
    """
    from .engine import _available_combat_skill_names, _player_ac

    sect_name = player.get("sect", "")
    sect_skills_map = SECT_BASIC_SKILLS.get(sect_name, {})

    # Get skill names
    sect_skill_names = list(sect_skills_map.keys())
    learned_skills = []
    # Get learned skill names from engine helper
    try:
        from .engine import _learned_skill_names
        learned_skills = _learned_skill_names(player)
    except:
        pass

    # Calculate AC directly
    ac = 10  # Base AC
    try:
        ac = _player_ac(player)
    except:
        pass

    # Get attrs summary directly
    attrs_str = ""
    try:
        from .engine import format_attrs
        attrs_str = format_attrs(sect_name)
    except:
        pass

    # Get equipment info
    equipment_str = ""
    equipment_slots = {"weapon": "", "armor": "", "accessory": ""}
    try:
        from .engine import _equipment_text
        from .game_data import EQUIPMENT_BY_ID
        equipment_str = _equipment_text(player)
        for slot in equipment_slots:
            item_id = (player.get("equipped") or {}).get(slot)
            row = EQUIPMENT_BY_ID.get(item_id)
            equipment_slots[slot] = row["name"] if row else ""
    except:
        pass

    status_str = player.get("status_text", "") if player.get("status_text") else "暂无"

    return {
        "name": player.get("nickname", ""),
        "level": player.get("level", 1),
        "xp": player.get("xp", 0),
        "hp": player.get("hp", 0),
        "max_hp": player.get("max_hp", 0),
        "mp": player.get("mp", 0),
        "max_mp": player.get("max_mp", 0),
        "silver": player.get("silver", 0),
        "floor": player.get("floor", 1),
        "sect": sect_name,
        "ac": ac,
        "attrs": attrs_str,
        "status": status_str,
        "equipment": equipment_str,
        "equipment_slots": equipment_slots,
        "sect_skills": sect_skills_map,  # Dict {name: mp_cost}
        "skills": learned_skills,  # List of learned advanced skill names
        "active_skill": player.get("active_skill", "") or "自动",
    }


def _filter_content_lines(text: str) -> list[str]:
    """
    Filter out status/attribute/skill lines from content to avoid duplication.
    These will be shown in the sidebar ONLY!
    """
    lines = []
    skip_prefixes = (
        "【金庸踢门团】", "门派：", "门派 [",
        "进度：", "第", "层，已开门",
        "HP ", "MP ", "AC ", "攻击+", "伤害+",
        "属性：", "素材", "核心特性：",
        "已学进阶武学：", "当前技能：",
        "装备：", "近期残页：", "增益：", "状态：",
        "药品：", "背囊：", "随身饵剂：",
        "背包物品：", "待拾取：", "局外点数",
        "═══", "━━━", "───",
    )
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("资源物品："):
            lines.append(line)
            continue
        # Skip status lines - they go to sidebar only
        if any(line.startswith(k) for k in skip_prefixes):
            continue
        lines.append(line)
    return lines or [" "]


def _player_skill_names(player: dict) -> list[str]:
    """Get all skill names available to player (basic + learned)."""
    sect_name = player.get("sect", "")
    sect_skills_map = SECT_BASIC_SKILLS.get(sect_name, {})
    basic = list(sect_skills_map.keys())

    try:
        from .engine import _learned_skill_names
        learned = _learned_skill_names(player)
    except:
        learned = []

    return basic + learned


def _load_background(path: Path, width: int, height: int):
    # Solid dark brown background - clean, no distraction
    bg = Image.new("RGB", (width, height), (22, 18, 14))

    if path.is_file():
        try:
            img = Image.open(path).convert("RGB")
            # Scale to cover entire height (vertical portrait mode)
            scale = height / max(1, img.height)
            resized_w = max(1, int(img.width * scale))
            img = img.resize((resized_w, height), Image.Resampling.LANCZOS)
            # Center crop horizontally if too wide
            if resized_w > width:
                crop_x = (resized_w - width) // 2
                img = img.crop((crop_x, 0, crop_x + width, height))
            # Paste background image
            bg.paste(img, (0, 0))
        except Exception as e:
            print(f"Background load error: {e}")

    # Add heavy dark overlay to make text readable everywhere
    # Dark translucent layer over the entire image
    draw = ImageDraw.Draw(bg)
    for y in range(height):
        # 75% dark overlay - make sure text is always readable
        draw.line((0, y, width, y), fill=(18, 14, 10))

    # Subtle vignette (slightly darker at edges)
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw_overlay = ImageDraw.Draw(overlay)
    for y in range(height):
        edge_dist = min(y, height - y) / (height / 2)
        alpha = int(40 * (1 - edge_dist))  # Darker at top/bottom edges
        draw_overlay.line((0, y, width, y), fill=(0, 0, 0, alpha))

    bg = Image.alpha_composite(bg.convert("RGBA"), overlay)
    return bg.convert("RGBA")


def _load_font(size: int, bold: bool = False):
    # Use bolder fonts for better readability
    candidates = [
        # Bold variants first
        ("/System/Library/Fonts/PingFang.ttc", 1 if bold else 0),  # PingFang Medium/Regular
        ("/System/Library/Fonts/PingFang.ttc", 2),  # PingFang Bold as fallback
        ("/System/Library/Fonts/STHeiti Medium.ttc", 0),
        ("/System/Library/Fonts/Hiragino Sans GB W6.ttc", 0),
        ("/System/Library/Fonts/Helvetica.ttc", 1),
        # Regular variants
        ("/System/Library/Fonts/STHeiti Light.ttc", 0),
        ("/System/Library/Fonts/Hiragino Sans GB.ttc", 0),
        ("/Library/Fonts/Arial Unicode.ttf", 0),
        ("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc", 0),
        ("/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc", 0),
        ("/usr/share/fonts/truetype/wqy/wqy-microhei.ttc", 0),
    ]
    for path, index in candidates:
        if Path(path).is_file():
            try:
                return ImageFont.truetype(path, size=size, index=index)
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


def _fit_content_blocks(content_blocks: list[tuple[str, list[str]]], available_h: int, line_h: int) -> list[tuple[str, list[str]]]:
    max_lines = max(1, int(available_h // line_h))
    notice = "卡片内容过长，完整文字请看下方文本区。"
    content_max_lines = max(1, max_lines - 1)
    used = 0
    fitted: list[tuple[str, list[str]]] = []
    truncated = False
    for original, wrapped in content_blocks:
        lines = wrapped or [""]
        remaining = content_max_lines - used
        if remaining <= 0:
            truncated = True
            break
        if len(lines) <= remaining:
            fitted.append((original, lines))
            used += len(lines)
            continue
        clipped = lines[:remaining]
        if clipped:
            clipped[-1] = clipped[-1].rstrip("，。；、,. ") + "……"
            fitted.append((original, clipped))
        used = content_max_lines
        truncated = True
        break
    if used >= content_max_lines and fitted:
        original, lines = fitted[-1]
        if lines and not lines[-1].endswith("……"):
            lines[-1] = lines[-1].rstrip("，。；、,. ") + "……"
            fitted[-1] = (original, lines)
    if truncated:
        fitted.append((notice, [notice]))
    return fitted


def _split_hint(text: str) -> tuple[str, str]:
    # Don't extract hint - keep all content in main body to avoid duplicate "可用行动"
    return text.strip(), ""


def _plain_body_lines(text: str) -> list[str]:
    lines = []
    for line in text.splitlines():
        line = line.strip()
        if line and not line.startswith("===") and not line.startswith("───"):
            lines.append(line)
    return lines or [" "]
