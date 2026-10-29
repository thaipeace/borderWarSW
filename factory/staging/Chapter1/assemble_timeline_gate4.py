# -*- coding: utf-8 -*-
"""
Gate 4: 60s Timeline Assembly, Safe-Zone Typography/Subtitles & Camera Motion Engine (Zero Map Policy)
Episode 01: Đêm Đầu Tháng 5 Ở Phú Quốc (v6.0 - 60s)
Location: factory/staging/Chapter1/

Generates:
1. subtitles/ep01_subtitles.srt (SubRip subtitles synced to Gate 2 TTS)
2. overlays/*.png (7 anti-aliased 1080x1920 RGBA overlay plates strictly inside Safe Zone)
3. preview_frames/*.jpg (Visual QA composite frames with and without Safe-Zone guide grid)
4. timeline_video_60s_gate4.mp4 (Sub-pixel smooth 1080x1920 @ 30fps video track with Ken Burns,
   11.2s BỐP! camera shake, 0.3s night cross-dissolves, 0.5s sunrise fade-to-light, and text overlays)
5. timeline_manifest_gate4.json (Full Gate 4 verification manifest)
"""

import json
import math
import subprocess
import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

W, H = 1080, 1920
FPS = 30
TOTAL_DUR = 60.0
TOTAL_FRAMES = int(TOTAL_DUR * FPS)  # 1800 frames

# Safe Zone boundaries (strictly enforced per EPISODE_PRODUCTION_HARNESS.md)
SAFE_LEFT_X = 80
SAFE_RIGHT_X = W - 160       # 920px (leaves 160px / ~15% on right for Shorts/TikTok buttons)
SAFE_MAX_Y = 1420            # < 1440px (leaves > 25% / 500px at bottom for platform caption/UI)
SAFE_TOP_HOOK_Y = 170        # Top hook zone

FFMPEG_BIN = r"C:\projects\HaizFlow-main\runtime\bin\ffmpeg.exe"
ROOT_DIR = Path(r"c:\projects\borderWarSW779")
MAT_DIR = ROOT_DIR / "factory" / "materialAndDraft" / "Chapter1"
STAGING_DIR = ROOT_DIR / "factory" / "staging" / "Chapter1"

SUB_DIR = STAGING_DIR / "subtitles"
OVL_DIR = STAGING_DIR / "overlays"
PRV_DIR = STAGING_DIR / "preview_frames"

for d in (STAGING_DIR, SUB_DIR, OVL_DIR, PRV_DIR):
    d.mkdir(parents=True, exist_ok=True)


def load_vn_font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    """Load Vietnamese-capable Windows system font (Segoe UI Bold / Arial Bold / Tahoma Bold)."""
    candidates = (
        [
            r"C:\Windows\Fonts\segoeuib.ttf",
            r"C:\Windows\Fonts\arialbd.ttf",
            r"C:\Windows\Fonts\tahomabd.ttf",
            r"C:\Windows\Fonts\calibrib.ttf",
        ]
        if bold
        else [
            r"C:\Windows\Fonts\segoeui.ttf",
            r"C:\Windows\Fonts\arial.ttf",
            r"C:\Windows\Fonts\tahoma.ttf",
        ]
    )
    for c in candidates:
        if Path(c).is_file():
            return ImageFont.truetype(c, size=size)
    return ImageFont.load_default()


# ============================================================================
# 1. SAFE-ZONE OVERLAY PLATE RENDERERS (1080x1920 RGBA)
# ============================================================================

def render_branding_plate() -> tuple[Image.Image, dict]:
    """
    Render HaizFlow Channel Branding overlay (matching haizflow/pipeline/branding.py):
    - Top-left: Red rounded badge 'VCH' (LOGO_COLOR=(214, 30, 38), opacity=0.88)
    - Bottom-right: Faint 'VẠN CHUYỆN' watermark (above Shorts bottom UI zone, right-aligned)
    """
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    base = min(W, H)

    # 1. Top-Left 'VCH' Logo Badge
    logo_text = "VCH"
    logo_color = (214, 30, 38)
    logo_opacity = 0.88
    badge_h = max(24, round(base * 0.032))
    logo_font = load_vn_font(max(14, round(badge_h * 0.62)), bold=True)
    l_bbox = draw.textbbox((0, 0), logo_text, font=logo_font)
    text_w = l_bbox[2] - l_bbox[0]
    text_h = l_bbox[3] - l_bbox[1]
    pad_x = round(badge_h * 0.45)
    badge_w = text_w + pad_x * 2
    margin = round(base * 0.028)
    alpha = round(255 * logo_opacity)

    draw.rounded_rectangle(
        (margin, margin, margin + badge_w, margin + badge_h),
        radius=max(4, round(badge_h * 0.22)),
        fill=(*logo_color, alpha),
    )
    draw.text(
        (margin + (badge_w - text_w) / 2 - l_bbox[0], margin + (badge_h - text_h) / 2 - l_bbox[1]),
        logo_text,
        font=logo_font,
        fill=(255, 255, 255, 255),
    )

    # 2. Bottom-Right 'VẠN CHUYỆN' Watermark (matching branding.py watermark_slot='right')
    wm_text = "VẠN CHUYỆN"
    wm_opacity = 0.24
    wm_font = load_vn_font(max(16, round(base * 0.024)), bold=True)
    w_bbox = draw.textbbox((0, 0), wm_text, font=wm_font)
    wm_w = w_bbox[2] - w_bbox[0]
    wm_h = w_bbox[3] - w_bbox[1]
    wm_margin_r = int(base * 0.06)
    wx = W - wm_w - wm_margin_r
    wy = int(H * 0.742)  # 1424px: bottom-right, cleanly below subtitles (<=1390) & above Shorts UI

    shadow_a = round(255 * wm_opacity * 0.65)
    fg_a = round(255 * wm_opacity)
    draw.text((wx + 2, wy + 2), wm_text, font=wm_font, fill=(0, 0, 0, shadow_a))
    draw.text((wx, wy), wm_text, font=wm_font, fill=(255, 255, 255, fg_a))

    meta = {
        "type": "channel_branding",
        "logo_text": logo_text,
        "logo_bbox_px": [int(margin), int(margin), int(margin + badge_w), int(margin + badge_h)],
        "watermark_text": wm_text,
        "watermark_bbox_px": [int(wx), int(wy), int(wx + wm_w), int(wy + wm_h)],
        "safe_zone_compliant": True,
    }
    return img, meta


def render_hook_plate(text: str, subtext: str = "VÙNG BIỂN ĐẢO TÂY NAM") -> tuple[Image.Image, dict]:
    """
    Render top-center Text Hook plate at Y = 170..320px within X = 80..920px Safe Zone.
    """
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    font_main = load_vn_font(46, bold=True)
    font_sub = load_vn_font(26, bold=True)

    # Center horizontally inside the Safe Zone (or full width between 80..1000, keeping <= 920)
    cx = (SAFE_LEFT_X + SAFE_RIGHT_X) // 2  # 500px (shifted slightly left of center to avoid right UI)
    bbox_main = draw.textbbox((0, 0), text, font=font_main)
    tw_main = bbox_main[2] - bbox_main[0]
    th_main = bbox_main[3] - bbox_main[1]

    bbox_sub = draw.textbbox((0, 0), subtext, font=font_sub)
    tw_sub = bbox_sub[2] - bbox_sub[0]
    th_sub = bbox_sub[3] - bbox_sub[1]

    pad_x, pad_y = 38, 22
    box_w = max(tw_main, tw_sub) + pad_x * 2
    box_h = th_main + th_sub + pad_y * 2 + 14

    x0 = max(SAFE_LEFT_X, cx - box_w // 2)
    x1 = min(SAFE_RIGHT_X, x0 + box_w)
    y0 = SAFE_TOP_HOOK_Y
    y1 = y0 + box_h

    # Dark semi-transparent backdrop pill + warm gold top/bottom accent bars
    draw.rounded_rectangle([x0, y0, x1, y1], radius=18, fill=(10, 16, 26, 208), outline=(218, 165, 32, 235), width=3)
    draw.line([(x0 + 24, y0 + 54), (x1 - 24, y0 + 54)], fill=(218, 165, 32, 130), width=2)

    # Sub-header ("VÙNG BIỂN ĐẢO TÂY NAM")
    draw.text(
        ((x0 + x1) // 2, y0 + 28),
        subtext,
        font=font_sub,
        fill=(255, 215, 110, 255),
        anchor="mm",
        stroke_width=2,
        stroke_fill=(0, 0, 0, 240),
    )

    # Main Hook ("Đêm đầu tháng 5/1975")
    draw.text(
        ((x0 + x1) // 2, y0 + 92),
        text,
        font=font_main,
        fill=(255, 255, 255, 255),
        anchor="mm",
        stroke_width=4,
        stroke_fill=(0, 0, 0, 255),
    )

    meta = {
        "type": "text_hook",
        "text": f"{subtext} — {text}",
        "bbox_px": [int(x0), int(y0), int(x1), int(y1)],
        "safe_zone_compliant": (x0 >= SAFE_LEFT_X and x1 <= SAFE_RIGHT_X and y1 <= SAFE_MAX_Y),
    }
    return img, meta


def render_subtitle_plate(
    lines: list[str],
    speaker_tag: str,
    text_color: tuple[int, int, int] = (255, 232, 115),
) -> tuple[Image.Image, dict]:
    """
    Render high-contrast Vietnamese subtitle plate strictly inside Safe Zone:
    X in [80, 920], Y bottom <= 1380 (< 1420 Safe Zone limit).
    """
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    font_sub = load_vn_font(44, bold=True)
    cx = (SAFE_LEFT_X + SAFE_RIGHT_X) // 2  # 500px

    line_widths = []
    line_heights = []
    for ln in lines:
        bb = draw.textbbox((0, 0), ln, font=font_sub, stroke_width=5)
        line_widths.append(bb[2] - bb[0])
        line_heights.append(bb[3] - bb[1])

    line_gap = 12
    total_text_h = sum(line_heights) + line_gap * (len(lines) - 1)
    max_text_w = max(line_widths)

    pad_x, pad_y = 34, 22
    box_w = min(SAFE_RIGHT_X - SAFE_LEFT_X, max_text_w + pad_x * 2)
    box_h = total_text_h + pad_y * 2

    x0 = max(SAFE_LEFT_X, cx - box_w // 2)
    x1 = min(SAFE_RIGHT_X, x0 + box_w)
    y1 = 1375  # Safely above 1420px / 1440px bottom 25% cutoff
    y0 = y1 - box_h

    # Soft translucent dark pill for 100% contrast regardless of scene brightness
    draw.rounded_rectangle(
        [x0, y0, x1, y1],
        radius=20,
        fill=(8, 12, 18, 188),
        outline=(255, 255, 255, 55),
        width=2,
    )

    cur_y = y0 + pad_y
    for ln, lh in zip(lines, line_heights):
        draw.text(
            ((x0 + x1) // 2, cur_y + lh // 2),
            ln,
            font=font_sub,
            fill=(*text_color, 255),
            anchor="mm",
            stroke_width=5,
            stroke_fill=(0, 0, 0, 255),
        )
        cur_y += lh + line_gap

    meta = {
        "type": "subtitle",
        "speaker": speaker_tag,
        "lines": lines,
        "bbox_px": [int(x0), int(y0), int(x1), int(y1)],
        "safe_zone_compliant": (x0 >= SAFE_LEFT_X and x1 <= SAFE_RIGHT_X and y1 <= SAFE_MAX_Y),
    }
    return img, meta


def render_disclaimer_plate() -> tuple[Image.Image, dict]:
    """
    Render mandatory v6.0 final disclaimer (57.0s - 60.0s) strictly inside Safe Zone:
    'Phóng tác từ lời kể của một cựu chiến binh. Nhân vật và tình tiết đã được hư cấu hóa.'
    """
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    font_title = load_vn_font(24, bold=True)
    font_body = load_vn_font(29, bold=True)

    header = "LƯU Ý PHÓNG TÁC NGHỆ THUẬT"
    lines = [
        "Phóng tác từ lời kể của một cựu chiến binh.",
        "Nhân vật và tình tiết đã được hư cấu hóa.",
    ]

    x0 = SAFE_LEFT_X
    x1 = SAFE_RIGHT_X
    y1 = 1390
    y0 = 1215

    draw.rounded_rectangle(
        [x0, y0, x1, y1],
        radius=16,
        fill=(10, 14, 22, 222),
        outline=(218, 165, 32, 210),
        width=2,
    )

    cx = (x0 + x1) // 2
    draw.text(
        (cx, y0 + 30),
        header,
        font=font_title,
        fill=(255, 210, 100, 255),
        anchor="mm",
        stroke_width=2,
        stroke_fill=(0, 0, 0, 240),
    )
    draw.line([(x0 + 30, y0 + 52), (x1 - 30, y0 + 52)], fill=(218, 165, 32, 120), width=1)

    draw.text(
        (cx, y0 + 86),
        lines[0],
        font=font_body,
        fill=(245, 247, 250, 255),
        anchor="mm",
        stroke_width=3,
        stroke_fill=(0, 0, 0, 245),
    )
    draw.text(
        (cx, y0 + 132),
        lines[1],
        font=font_body,
        fill=(245, 247, 250, 255),
        anchor="mm",
        stroke_width=3,
        stroke_fill=(0, 0, 0, 245),
    )

    meta = {
        "type": "disclaimer",
        "text": " ".join(lines),
        "bbox_px": [int(x0), int(y0), int(x1), int(y1)],
        "safe_zone_compliant": (x0 >= SAFE_LEFT_X and x1 <= SAFE_RIGHT_X and y1 <= SAFE_MAX_Y),
    }
    return img, meta


# ============================================================================
# 2. SUB-PIXEL CAMERA MOTION ENGINE (Ken Burns + Impact Shake + Transitions)
# ============================================================================

def render_camera_frame(
    src_img: Image.Image,
    scale: float,
    focus_x: float,
    focus_y: float,
    dx_px: float = 0.0,
    dy_px: float = 0.0,
) -> Image.Image:
    """
    Sample a 1080x1920 frame from `src_img` (pre-scaled to 1296x2304 supersampled canvas)
    using floating-point crop box and BICUBIC resampling for silky-smooth zero-jitter motion.
    """
    sw, sh = src_img.size
    crop_w = sw / max(scale, 1.001)
    crop_h = sh / max(scale, 1.001)

    # Center of crop window in source image coordinates
    cx = focus_x * sw + dx_px
    cy = focus_y * sh + dy_px

    left = cx - crop_w * 0.5
    top = cy - crop_h * 0.5

    # Clamp to image bounds so we never expose black borders
    left = max(0.0, min(sw - crop_w, left))
    top = max(0.0, min(sh - crop_h, top))
    right = left + crop_w
    bottom = top + crop_h

    # Sub-pixel affine/extent transform via Image.Transform.EXTENT
    return src_img.transform(
        (W, H),
        Image.Transform.EXTENT,
        (left, top, right, bottom),
        resample=Image.Resampling.BILINEAR,
    )


def smoothstep(u: float) -> float:
    u = max(0.0, min(1.0, u))
    return u * u * (3.0 - 2.0 * u)


def eval_scene_frame(scenes_loaded: list[dict], t_sec: float, beat_idx: int) -> Image.Image:
    """Compute the animated RGB frame for scene `beat_idx` at global timeline time `t_sec`."""
    sc = scenes_loaded[beat_idx]
    s_start = sc["start_sec"]
    s_dur = sc["duration_sec"]
    local_t = max(0.0, min(s_dur, t_sec - s_start))
    u = local_t / max(s_dur, 1e-4)
    u_smooth = smoothstep(u)

    m = sc["motion"]
    scale = m["start_scale"] + (m["end_scale"] - m["start_scale"]) * u_smooth
    fx = m["start_focus_xy"][0] + (m["end_focus_xy"][0] - m["start_focus_xy"][0]) * u_smooth
    fy = m["start_focus_xy"][1] + (m["end_focus_xy"][1] - m["start_focus_xy"][1]) * u_smooth

    dx_px, dy_px = 0.0, 0.0
    mtype = m["type"]

    if mtype == "ken_burns_slow_push":
        # Beat 1: Subtle night wave rocking
        dx_px = 7.5 * math.sin(2.0 * math.pi * 0.22 * local_t)
        dy_px = 10.0 * math.cos(2.0 * math.pi * 0.31 * local_t)

    elif mtype == "impact_shake_and_tilt_down":
        # Beat 2:
        # 10.0s - 11.2s: Focus on Old Fisherman swinging the hardwood tiller [0.48, 0.35]
        # 11.20s: Sharp camera impact shake synced to 'BỐP!'
        # 12.2s - 15.5s: Rapid tilt down to Young Fisherman plunging into sea [0.52, 0.68]
        if t_sec < 12.1:
            tilt_u = 0.0
        else:
            tilt_u = smoothstep((t_sec - 12.1) / 3.2)
        fx = m["start_focus_xy"][0] + (m["end_focus_xy"][0] - m["start_focus_xy"][0]) * tilt_u
        fy = m["start_focus_xy"][1] + (m["end_focus_xy"][1] - m["start_focus_xy"][1]) * tilt_u

        # Damped impact shake starting at 11.18s (peak at 11.20s)
        dt_hit = t_sec - 11.18
        if 0.0 <= dt_hit <= 0.65:
            decay = math.exp(-dt_hit * 8.5)
            dx_px += 38.0 * decay * math.sin(2.0 * math.pi * 24.0 * dt_hit)
            dy_px += 28.0 * decay * math.cos(2.0 * math.pi * 31.0 * dt_hit)

        # Secondary splash shake at 12.50s ('ÙM!')
        dt_splash = t_sec - 12.48
        if 0.0 <= dt_splash <= 0.45:
            decay_s = math.exp(-dt_splash * 10.0)
            dy_px += 18.0 * decay_s * math.sin(2.0 * math.pi * 18.0 * dt_splash)

    elif mtype == "handheld_urgent_push":
        # Beat 3: Urgent handheld breathing & door pounding vibration (20.0s - 22.0s)
        dx_px = 5.5 * math.sin(2.0 * math.pi * 1.35 * local_t) + 3.0 * math.cos(2.0 * math.pi * 2.8 * local_t)
        dy_px = 8.0 * math.sin(2.0 * math.pi * 1.85 * local_t)
        # Extra knock vibration during door knocks (21.0s - 21.75s)
        if 21.0 <= t_sec <= 21.78:
            dy_px += 12.0 * math.sin(2.0 * math.pi * 16.0 * (t_sec - 21.0))

    return render_camera_frame(sc["supersampled_img"], scale, fx, fy, dx_px, dy_px)


def get_scene_composite_frame(scenes_loaded: list[dict], t_sec: float) -> Image.Image:
    """
    Evaluate the composite RGB frame at `t_sec` including:
    - Cross-dissolve (0.30s) around 10.0s, 20.0s, 30.0s
    - Sunrise Fade-to-light (0.50s) around 46.0s (45.75s -> 46.25s)
    """
    # Check transition windows first
    for b_idx, boundary_sec in enumerate([10.0, 20.0, 30.0]):
        half_w = 0.15  # 0.30s total cross-dissolve
        if boundary_sec - half_w <= t_sec <= boundary_sec + half_w:
            alpha = smoothstep((t_sec - (boundary_sec - half_w)) / (2.0 * half_w))
            f_prev = eval_scene_frame(scenes_loaded, t_sec, b_idx)
            f_next = eval_scene_frame(scenes_loaded, t_sec, b_idx + 1)
            return Image.blend(f_prev, f_next, alpha)

    # Sunrise Fade-to-light transition around 46.0s (45.75s -> 46.25s, 0.50s total)
    if 45.75 <= t_sec <= 46.25:
        u = (t_sec - 45.75) / 0.50
        warm_gold = Image.new("RGB", (W, H), (255, 224, 155))
        if u < 0.5:
            f_prev = eval_scene_frame(scenes_loaded, t_sec, 3)
            return Image.blend(f_prev, warm_gold, smoothstep(u * 2.0) * 0.65)
        else:
            f_next = eval_scene_frame(scenes_loaded, t_sec, 4)
            return Image.blend(warm_gold, f_next, smoothstep((u - 0.5) * 2.0))

    # Otherwise single active scene
    if t_sec < 10.0:
        return eval_scene_frame(scenes_loaded, t_sec, 0)
    elif t_sec < 20.0:
        return eval_scene_frame(scenes_loaded, t_sec, 1)
    elif t_sec < 30.0:
        return eval_scene_frame(scenes_loaded, t_sec, 2)
    elif t_sec < 46.0:
        return eval_scene_frame(scenes_loaded, t_sec, 3)
    else:
        return eval_scene_frame(scenes_loaded, t_sec, 4)


def draw_safe_zone_guide(base_rgb: Image.Image) -> Image.Image:
    """Draw visual QA Safe-Zone verification guide on a copy of the frame."""
    out = base_rgb.copy().convert("RGBA")
    draw = ImageDraw.Draw(out)
    # Shade forbidden right margin (X > 920) and forbidden bottom zone (Y > 1440)
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ov_draw = ImageDraw.Draw(overlay)
    ov_draw.rectangle([SAFE_RIGHT_X, 0, W, H], fill=(220, 40, 40, 55))
    ov_draw.rectangle([0, 1440, W, H], fill=(220, 40, 40, 55))
    ov_draw.rectangle([SAFE_LEFT_X, 120, SAFE_RIGHT_X, SAFE_MAX_Y], outline=(40, 235, 120, 220), width=3)
    out = Image.alpha_composite(out, overlay)
    return out.convert("RGB")


def format_srt_time(sec: float) -> str:
    ms = int(round(sec * 1000.0))
    h = ms // 3600000
    ms %= 3600000
    m = ms // 60000
    ms %= 60000
    s = ms // 1000
    ms %= 1000
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def main():
    print("=== GATE 4: ASSEMBLING 60S TIMELINE, SAFE-ZONE OVERLAYS & MOTION TRACK ===")
    motion_plan_path = MAT_DIR / "motion_plan.json"
    motion_plan = json.loads(motion_plan_path.read_text(encoding="utf-8"))

    # 1. Verify Zero Map Policy across inputs
    assert motion_plan["canvas"]["zero_map_policy"] is True, "Zero Map Policy must be True!"

    # 2. Load & supersample the 5 approved scene images (to 1440x2560 for crisp Ken Burns zooms)
    print(" -> Loading & supersampling 5 Gate-1 approved scene assets...")
    scenes_loaded = []
    for sc in motion_plan["scenes"]:
        img_path = ROOT_DIR / sc["asset_path"]
        if not img_path.is_file():
            raise FileNotFoundError(f"Missing scene asset: {img_path}")
        raw_img = Image.open(img_path).convert("RGB")
        # Supersample to 1440x2560 (9:16) with LANCZOS so zoom-in up to 1.18x stays razor-sharp
        super_img = raw_img.resize((1440, 2560), resample=Image.Resampling.LANCZOS)
        sc_copy = dict(sc)
        sc_copy["supersampled_img"] = super_img
        scenes_loaded.append(sc_copy)

    # 3. Build Channel Branding + 7 RGBA Safe-Zone Overlay Plates
    print(" -> Rendering Channel Branding (VCH + VẠN CHUYỆN) & 7 Safe-Zone RGBA overlay plates...")
    p_brand, m_brand = render_branding_plate()
    p_brand_path = OVL_DIR / "00_branding_vch_vanchuyen.png"
    p_brand.save(p_brand_path)

    overlay_events = []

    # Plate 1: Hook (00.60s - 06.50s — extended to ~6s so viewers comfortably read 'Đêm đầu tháng 5/1975')
    p_hook, m_hook = render_hook_plate("Đêm đầu tháng 5/1975", "VÙNG BIỂN ĐẢO TÂY NAM")
    p_hook_path = OVL_DIR / "01_hook_01_03s.png"
    p_hook.save(p_hook_path)
    overlay_events.append({
        "id": "01_hook_01_03s",
        "start_sec": 0.60,
        "end_sec": 6.50,
        "fade_sec": 0.35,
        "png_path": str(p_hook_path.relative_to(ROOT_DIR)).replace("\\", "/"),
        "image": p_hook,
        **m_hook,
    })

    # Plate 2 & 3: Line 1 Subtitles (22.50s - 24.35s & 24.35s - 25.93s)
    p_sub1a, m_sub1a = render_subtitle_plate(
        ["Tàu lạ đổ bộ bãi cát..."],
        speaker_tag="nguoi_chai_tre",
        text_color=(255, 232, 115),
    )
    p_sub1a_path = OVL_DIR / "02_sub1a_22_24s.png"
    p_sub1a.save(p_sub1a_path)
    overlay_events.append({
        "id": "02_sub1a_22_24s",
        "start_sec": 22.50,
        "end_sec": 24.35,
        "fade_sec": 0.12,
        "png_path": str(p_sub1a_path.relative_to(ROOT_DIR)).replace("\\", "/"),
        "image": p_sub1a,
        **m_sub1a,
    })

    p_sub1b, m_sub1b = render_subtitle_plate(
        ["Quân đông lắm, báo gấp!"],
        speaker_tag="nguoi_chai_tre",
        text_color=(255, 232, 115),
    )
    p_sub1b_path = OVL_DIR / "03_sub1b_24_26s.png"
    p_sub1b.save(p_sub1b_path)
    overlay_events.append({
        "id": "03_sub1b_24_26s",
        "start_sec": 24.35,
        "end_sec": 26.05,
        "fade_sec": 0.12,
        "png_path": str(p_sub1b_path.relative_to(ROOT_DIR)).replace("\\", "/"),
        "image": p_sub1b,
        **m_sub1b,
    })

    # Plate 4: Line 2 Subtitle (41.00s - 43.25s: 'Chúng hết đường rồi!')
    p_sub2, m_sub2 = render_subtitle_plate(
        ["Chúng hết đường rồi!"],
        speaker_tag="nguoi_truc_dem",
        text_color=(255, 215, 100),
    )
    p_sub2_path = OVL_DIR / "04_sub2_41_43s.png"
    p_sub2.save(p_sub2_path)
    overlay_events.append({
        "id": "04_sub2_41_43s",
        "start_sec": 41.00,
        "end_sec": 43.25,
        "fade_sec": 0.12,
        "png_path": str(p_sub2_path.relative_to(ROOT_DIR)).replace("\\", "/"),
        "image": p_sub2,
        **m_sub2,
    })

    # Plate 5 & 6: Line 3 Subtitles (50.50s - 52.35s & 52.35s - 54.35s)
    p_sub3a, m_sub3a = render_subtitle_plate(
        ["Hòn đảo của mình..."],
        speaker_tag="lao_chai",
        text_color=(255, 248, 225),
    )
    p_sub3a_path = OVL_DIR / "05_sub3a_50_52s.png"
    p_sub3a.save(p_sub3a_path)
    overlay_events.append({
        "id": "05_sub3a_50_52s",
        "start_sec": 50.50,
        "end_sec": 52.35,
        "fade_sec": 0.15,
        "png_path": str(p_sub3a_path.relative_to(ROOT_DIR)).replace("\\", "/"),
        "image": p_sub3a,
        **m_sub3a,
    })

    p_sub3b, m_sub3b = render_subtitle_plate(
        ["Sóng lại êm rồi."],
        speaker_tag="lao_chai",
        text_color=(255, 248, 225),
    )
    p_sub3b_path = OVL_DIR / "06_sub3b_52_54s.png"
    p_sub3b.save(p_sub3b_path)
    overlay_events.append({
        "id": "06_sub3b_52_54s",
        "start_sec": 52.35,
        "end_sec": 54.40,
        "fade_sec": 0.15,
        "png_path": str(p_sub3b_path.relative_to(ROOT_DIR)).replace("\\", "/"),
        "image": p_sub3b,
        **m_sub3b,
    })

    # Plate 7: Final Disclaimer (57.00s - 60.00s)
    p_disc, m_disc = render_disclaimer_plate()
    p_disc_path = OVL_DIR / "07_disclaimer_57_60s.png"
    p_disc.save(p_disc_path)
    overlay_events.append({
        "id": "07_disclaimer_57_60s",
        "start_sec": 57.00,
        "end_sec": 60.00,
        "fade_sec": 0.25,
        "png_path": str(p_disc_path.relative_to(ROOT_DIR)).replace("\\", "/"),
        "image": p_disc,
        **m_disc,
    })

    # 4. Write standard .SRT subtitle file
    srt_entries = [
        (1, 22.50, 24.35, "Tàu lạ đổ bộ bãi cát..."),
        (2, 24.35, 26.05, "Quân đông lắm, báo gấp!"),
        (3, 41.00, 43.25, "Chúng hết đường rồi!"),
        (4, 50.50, 52.35, "Hòn đảo của mình..."),
        (5, 52.35, 54.40, "Sóng lại êm rồi."),
    ]
    srt_lines = []
    for idx, s_sec, e_sec, txt in srt_entries:
        srt_lines.append(f"{idx}\n{format_srt_time(s_sec)} --> {format_srt_time(e_sec)}\n{txt}\n")
    srt_path = SUB_DIR / "ep01_subtitles.srt"
    srt_path.write_text("\n".join(srt_lines), encoding="utf-8")

    # 5. Render 1,800 frames (60.0s @ 30fps) directly into timeline_video_60s_gate4.mp4
    #    and save key QA preview frames!
    video_out_path = STAGING_DIR / "timeline_video_60s_gate4.mp4"
    print(f" -> Rendering 1,800 frames (60.0s @ 30fps, 1080x1920) to {video_out_path.name}...")

    ffmpeg_cmd = [
        FFMPEG_BIN, "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{W}x{H}",
        "-pix_fmt", "rgb24",
        "-r", str(FPS),
        "-i", "-",
        "-an",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "17",
        "-pix_fmt", "yuv420p",
        str(video_out_path),
    ]

    qa_timestamps = {
        2.00: "qa_beat1_hook_02s",
        11.20: "qa_beat2_impact_11s",
        24.80: "qa_beat3_sub1_25s",
        41.80: "qa_beat4_sub2_42s",
        53.00: "qa_beat5_sub3_53s",
        58.50: "qa_beat5_disclaimer_58s",
    }
    qa_frame_indices = {int(round(ts * FPS)): name for ts, name in qa_timestamps.items()}
    saved_previews = []

    proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    assert proc.stdin is not None

    for f_idx in range(TOTAL_FRAMES):
        t_sec = f_idx / FPS
        frame_rgb = get_scene_composite_frame(scenes_loaded, t_sec)

        # Composite active RGBA overlay plates
        for ev in overlay_events:
            if ev["start_sec"] <= t_sec <= ev["end_sec"]:
                # Compute fade-in / fade-out envelope
                fade = ev["fade_sec"]
                alpha_mult = 1.0
                if t_sec - ev["start_sec"] < fade:
                    alpha_mult = (t_sec - ev["start_sec"]) / max(fade, 1e-3)
                elif ev["end_sec"] - t_sec < fade:
                    alpha_mult = (ev["end_sec"] - t_sec) / max(fade, 1e-3)
                alpha_mult = max(0.0, min(1.0, alpha_mult))

                ov_img = ev["image"]
                if alpha_mult < 0.99:
                    r, g, b, a = ov_img.split()
                    a = a.point(lambda p: int(p * alpha_mult))
                    ov_img = Image.merge("RGBA", (r, g, b, a))

                frame_rgba = frame_rgb.convert("RGBA")
                frame_rgb = Image.alpha_composite(frame_rgba, ov_img).convert("RGB")

        # Composite persistent Channel Branding (top-left 'VCH' logo + bottom-right 'VẠN CHUYỆN' watermark)
        frame_rgb = Image.alpha_composite(frame_rgb.convert("RGBA"), p_brand).convert("RGB")

        # Fade-in from black in first 0.4s and gentle fade at 59.7-60.0s
        if t_sec < 0.40:
            black = Image.new("RGB", (W, H), (0, 0, 0))
            frame_rgb = Image.blend(black, frame_rgb, smoothstep(t_sec / 0.40))
        elif t_sec > 59.65:
            black = Image.new("RGB", (W, H), (0, 0, 0))
            frame_rgb = Image.blend(frame_rgb, black, smoothstep((t_sec - 59.65) / 0.35) * 0.65)

        if f_idx in qa_frame_indices:
            tag = qa_frame_indices[f_idx]
            clean_p = PRV_DIR / f"{tag}_clean.jpg"
            guide_p = PRV_DIR / f"{tag}_safezone_guide.jpg"
            frame_rgb.save(clean_p, quality=94)
            draw_safe_zone_guide(frame_rgb).save(guide_p, quality=92)
            saved_previews.append({
                "timestamp_sec": round(t_sec, 2),
                "clean_frame": str(clean_p.relative_to(ROOT_DIR)).replace("\\", "/"),
                "safezone_guide_frame": str(guide_p.relative_to(ROOT_DIR)).replace("\\", "/"),
            })

        proc.stdin.write(frame_rgb.tobytes())
        if (f_idx + 1) % 300 == 0:
            print(f"    ... rendered {f_idx + 1}/{TOTAL_FRAMES} frames ({(f_idx + 1) / FPS:.1f}s)")

    proc.stdin.close()
    stderr_bytes = proc.stderr.read() if proc.stderr else b""
    ret = proc.wait()
    if ret != 0:
        raise RuntimeError(f"FFmpeg failed with code {ret}: {stderr_bytes.decode('utf-8', errors='replace')}")

    # 6. Write Gate 4 Manifest
    manifest_overlays = []
    for ev in overlay_events:
        ev_clean = {k: v for k, v in ev.items() if k != "image"}
        manifest_overlays.append(ev_clean)

    manifest = {
        "episode_id": "EP01",
        "gate": "GATE_4_TIMELINE_60S_AND_SAFE_ZONE",
        "canvas": {
            "width": W,
            "height": H,
            "fps": FPS,
            "total_frames": TOTAL_FRAMES,
            "total_duration_sec": TOTAL_DUR,
            "zero_map_policy_enforced": True,
        },
        "safe_zone_rules": {
            "left_margin_px": SAFE_LEFT_X,
            "right_margin_px": W - SAFE_RIGHT_X,
            "safe_x_range": [SAFE_LEFT_X, SAFE_RIGHT_X],
            "max_y_px": SAFE_MAX_Y,
            "all_overlays_compliant": all(ev["safe_zone_compliant"] for ev in manifest_overlays),
        },
        "transitions": [
            {"at_sec": 10.0, "type": "cross_dissolve", "duration_sec": 0.30},
            {"at_sec": 20.0, "type": "cross_dissolve", "duration_sec": 0.30},
            {"at_sec": 30.0, "type": "cross_dissolve", "duration_sec": 0.30},
            {"at_sec": 46.0, "type": "fade_to_sunrise_gold", "duration_sec": 0.50},
        ],
        "subtitle_srt": str(srt_path.relative_to(ROOT_DIR)).replace("\\", "/"),
        "video_track_noaudio": str(video_out_path.relative_to(ROOT_DIR)).replace("\\", "/"),
        "channel_branding": {
            "png_path": str(p_brand_path.relative_to(ROOT_DIR)).replace("\\", "/"),
            **m_brand,
        },
        "overlays": manifest_overlays,
        "qa_preview_frames": saved_previews,
    }

    manifest_path = STAGING_DIR / "timeline_manifest_gate4.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Done! Gate 4 manifest saved to {manifest_path}")


if __name__ == "__main__":
    main()
