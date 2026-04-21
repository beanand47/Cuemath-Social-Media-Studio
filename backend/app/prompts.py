from __future__ import annotations

from textwrap import dedent


SYSTEM_PROMPT = dedent(
    """
    You create simple educational social media content.
    Always return clear, concise, engaging slide copy.
    Return only valid JSON matching the requested schema.
    """
).strip()


def build_generation_prompt(user_prompt: str, selected_format: str, slide_count: int) -> str:
    format_label = {
        "carousel": "carousel",
        "post": "post",
        "story": "story",
    }[selected_format]
    return dedent(
        f"""
        Create a social media post for students and parents.

        Topic:
        {user_prompt}

        Style:
        - simple language (easy for kids)
        - engaging and friendly
        - slightly emotional or relatable
        - include a hook at the beginning
        - include a takeaway or value

        Tone:
        - encouraging
        - clear
        - not robotic

        Format:
        - create content for an Instagram {format_label}
        - return exactly {slide_count} item(s)
        - for carousel, make each slide feel like part of one connected story
        - for post and story, return a single polished creative

        Output:
        - Title (hook)
        - Caption (2-3 lines)

        Return only a valid JSON array in this format:
        [
          {{ "title": "...", "text": "..." }}
        ]
        """
    ).strip()


def build_image_prompt(
    slide_title: str,
    slide_text: str,
    slide_index: int,
    selected_format: str,
) -> str:
    return dedent(
        f"""
        Create a high-quality social media visual.

        Context:
        Slide {slide_index}: {slide_title}
        {slide_text}

        Format:
        {selected_format}

        Style:
        - modern
        - minimal
        - visually engaging
        - platform-appropriate (Instagram style)
        - unique layout for each image

        Make this image visually distinct from the other slides in the same set.
        """
    ).strip()
