from __future__ import annotations

import base64
import io
from textwrap import shorten, wrap

from PIL import Image, ImageColor, ImageDraw, ImageFilter, ImageFont

from app.schemas import BrandConfig, FormatType, Slide


DIMENSIONS: dict[FormatType, tuple[int, int]] = {
    "instagram_post": (1080, 1080),
    "instagram_story": (1080, 1920),
    "carousel": (1080, 1350),
}


def render_slide_to_data_url(slide: Slide, brand: BrandConfig, post_format: FormatType) -> tuple[str, int, int]:
    width, height = DIMENSIONS[post_format]
    base = Image.new("RGBA", (width, height), brand.background_color)
    image_layer = _build_image_layer(slide, width, height)
    canvas = Image.alpha_composite(base, image_layer)

    if slide.layout_type == "cover":
        _render_cover(canvas, slide, brand)
    elif slide.layout_type == "insight":
        _render_insight(canvas, slide, brand)
    elif slide.layout_type == "explanation":
        _render_explanation(canvas, slide, brand)
    else:
        _render_cta(canvas, slide, brand)

    output = io.BytesIO()
    canvas.convert("RGB").save(output, format="PNG")
    encoded = base64.b64encode(output.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{encoded}", width, height


def _build_image_layer(slide: Slide, width: int, height: int) -> Image.Image:
    image = _decode_data_url(slide.image_url)
    if image is None:
        return _fallback_art(slide, width, height)

    image = image.convert("RGBA")
    return _fit_image(image, width, height)


def _render_cover(canvas: Image.Image, slide: Slide, brand: BrandConfig) -> None:
    width, height = canvas.size
    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.rectangle((0, int(height * 0.52), width, height), fill=(247, 247, 245, 236))
    draw.rounded_rectangle((70, 70, width - 70, 140), radius=34, fill=(255, 255, 255, 170))
    draw.rounded_rectangle((70, height - 200, width - 70, height - 90), radius=40, fill=_hex_to_rgb(brand.secondary_color) + (232,))
    canvas.alpha_composite(overlay)

    draw = ImageDraw.Draw(canvas)
    title_font = _safe_font(80)
    body_font = _safe_font(32)
    meta_font = _safe_font(26)
    cta_font = _safe_font(28)

    draw.text((98, 92), f"{slide.index:02d}", fill=brand.primary_color, font=meta_font)
    draw.text((98, int(height * 0.58)), _clamp_text(slide.title, 18, 3), fill="#182133", font=title_font, spacing=4)
    draw.text((98, int(height * 0.79)), _clamp_text(slide.body, 31, 3), fill="#4D5D73", font=body_font, spacing=10)
    draw.text((110, height - 165), shorten(slide.cta, width=54, placeholder="..."), fill="#FFFFFF", font=cta_font)


def _render_insight(canvas: Image.Image, slide: Slide, brand: BrandConfig) -> None:
    width, height = canvas.size
    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    if slide.composition == "split":
        draw.rounded_rectangle((60, 60, int(width * 0.46), height - 60), radius=42, fill=(248, 248, 246, 235))
    else:
        draw.rounded_rectangle((60, height - 520, width - 60, height - 60), radius=42, fill=(248, 248, 246, 228))

    draw.rounded_rectangle((width - 260, 78, width - 84, 132), radius=26, fill=_hex_to_rgb(brand.accent_color) + (105,))
    canvas.alpha_composite(overlay)

    draw = ImageDraw.Draw(canvas)
    title_font = _safe_font(66)
    body_font = _safe_font(30)
    meta_font = _safe_font(24)

    x = 98 if slide.composition == "split" else 94
    y = 112 if slide.composition == "split" else height - 470
    draw.text((x, y), _clamp_text(slide.title, 16, 3), fill="#172033", font=title_font, spacing=6)
    draw.text((x, y + 230), _clamp_text(slide.body, 28, 4), fill="#4A5A70", font=body_font, spacing=10)
    draw.text((x, y + 410), f"Takeaway: {shorten(slide.takeaway, width=44, placeholder='...')}", fill=brand.primary_color, font=meta_font)


def _render_explanation(canvas: Image.Image, slide: Slide, brand: BrandConfig) -> None:
    width, height = canvas.size
    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.rounded_rectangle((64, 72, width - 64, height - 72), radius=46, fill=(247, 247, 245, 224))
    draw.rounded_rectangle((92, 260, width - 92, 276), radius=8, fill=(222, 227, 234, 255))
    draw.rounded_rectangle((92, 680, width - 92, 696), radius=8, fill=(222, 227, 234, 255))
    draw.rounded_rectangle((92, 312, 270, 470), radius=32, fill=(255, 255, 255, 170))
    draw.rounded_rectangle((92, 730, width - 92, height - 118), radius=36, fill=(255, 255, 255, 185))
    canvas.alpha_composite(overlay)

    draw = ImageDraw.Draw(canvas)
    title_font = _safe_font(68)
    body_font = _safe_font(30)
    meta_font = _safe_font(24)

    draw.text((102, 108), _clamp_text(slide.title, 17, 2), fill="#162133", font=title_font, spacing=6)
    draw.text((110, 326), _clamp_text(slide.body, 20, 5), fill="#47586D", font=body_font, spacing=10)
    draw.text((110, 764), "What to remember", fill=brand.primary_color, font=meta_font)
    draw.text((110, 810), _clamp_text(slide.takeaway, 34, 3), fill="#203046", font=body_font, spacing=8)


def _render_cta(canvas: Image.Image, slide: Slide, brand: BrandConfig) -> None:
    width, height = canvas.size
    overlay = Image.new("RGBA", canvas.size, (247, 247, 245, 176))
    overlay = overlay.filter(ImageFilter.GaussianBlur(6))
    canvas.alpha_composite(overlay)

    glass = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(glass)
    draw.rounded_rectangle((100, 160, width - 100, height - 160), radius=56, fill=(255, 255, 255, 208))
    draw.rounded_rectangle((146, height - 332, width - 146, height - 228), radius=34, fill=_hex_to_rgb(brand.secondary_color) + (228,))
    canvas.alpha_composite(glass)

    draw = ImageDraw.Draw(canvas)
    title_font = _safe_font(74)
    body_font = _safe_font(30)
    cta_font = _safe_font(30)
    meta_font = _safe_font(24)

    draw.text((144, 214), "Final thought", fill=brand.primary_color, font=meta_font)
    draw.text((144, 286), _clamp_text(slide.title, 16, 3), fill="#162133", font=title_font, spacing=8)
    draw.text((144, 600), _clamp_text(slide.body, 32, 4), fill="#4A5A70", font=body_font, spacing=10)
    draw.text((144, 760), shorten(slide.takeaway, width=52, placeholder="..."), fill=brand.primary_color, font=body_font)
    draw.text((176, height - 305), shorten(slide.cta, width=44, placeholder="..."), fill="#FFFFFF", font=cta_font)


def _decode_data_url(data_url: str | None) -> Image.Image | None:
    if not data_url or "," not in data_url:
        return None
    try:
        encoded = data_url.split(",", 1)[1]
        binary = base64.b64decode(encoded)
        return Image.open(io.BytesIO(binary))
    except Exception:
        return None


def _fit_image(image: Image.Image, width: int, height: int) -> Image.Image:
    ratio = max(width / image.width, height / image.height)
    resized = image.resize((int(image.width * ratio), int(image.height * ratio)))
    left = max((resized.width - width) // 2, 0)
    top = max((resized.height - height) // 2, 0)
    return resized.crop((left, top, left + width, top + height))


def _fallback_art(slide: Slide, width: int, height: int) -> Image.Image:
    canvas = Image.new("RGBA", (width, height), "#F7F7F5")
    draw = ImageDraw.Draw(canvas)
    palettes = {
        "cinematic": ("#F0E5D8", "#D4E0EC"),
        "illustration": ("#F7E9D8", "#DCEAD8"),
        "minimal": ("#F7F5F1", "#E7EEF3"),
        "abstract": ("#E8E4EF", "#E4EBDD"),
    }
    start_hex, end_hex = palettes.get(slide.visual_style, ("#F3EEE7", "#E5EBF1"))
    for y in range(height):
        blend = y / max(height - 1, 1)
        color = _mix_rgb(_hex_to_rgb(start_hex), _hex_to_rgb(end_hex), blend)
        draw.line((0, y, width, y), fill=color)

    draw.ellipse((80, 90, int(width * 0.58), int(height * 0.68)), fill=(255, 255, 255, 120))
    draw.rounded_rectangle((int(width * 0.54), 120, width - 110, int(height * 0.52)), radius=48, fill=(255, 255, 255, 120))
    draw.rounded_rectangle((100, int(height * 0.72), width - 100, int(height * 0.88)), radius=44, fill=(255, 255, 255, 145))
    return canvas


def _clamp_text(text: str, width: int, max_lines: int) -> str:
    lines = wrap(text.strip(), width=width)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = shorten(lines[-1], width=width, placeholder="...")
    return "\n".join(lines)


def _mix_rgb(start: tuple[int, int, int], end: tuple[int, int, int], blend: float) -> tuple[int, int, int]:
    return tuple(int(start[i] + (end[i] - start[i]) * blend) for i in range(3))


def _hex_to_rgb(value: str) -> tuple[int, int, int]:
    return ImageColor.getrgb(value)


def _safe_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for candidate in ("arial.ttf", "DejaVuSans.ttf", "seguiemj.ttf"):
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            continue
    return ImageFont.load_default()
