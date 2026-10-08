import re

from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe

register = template.Library()

_CODE_BLOCK = re.compile(r"```([\s\S]*?)```")
_INLINE_CODE = re.compile(r"`([^`\n]+)`")
_HEADING = re.compile(r"^(#{1,3}) +(.+?)\s*$", re.MULTILINE)
_BOLD = re.compile(r"\*\*(.+?)\*\*")
_BLOCK_START = re.compile(r"<(h[1-3]|pre)\b|<!--CODE")


@register.filter
def render_post(value):
    """Turn the lightweight post markup into HTML.

    Supports #/##/### headings, **bold**, `inline code` and ``` fenced code blocks.
    All user text is HTML-escaped first, so the result is safe to mark as such.
    """
    text = escape(value or "").replace("\r\n", "\n")

    blocks = []

    def stash(match):
        blocks.append(match.group(1).strip("\n"))
        return f"\n\n<!--CODE{len(blocks) - 1}-->\n\n"

    text = _CODE_BLOCK.sub(stash, text)
    text = _INLINE_CODE.sub(r"<code>\1</code>", text)
    text = _HEADING.sub(
        lambda m: f"\n\n<h{len(m.group(1))}>{m.group(2)}</h{len(m.group(1))}>\n\n", text
    )
    text = _BOLD.sub(r"<strong>\1</strong>", text)

    parts = []
    for chunk in re.split(r"\n{2,}", text):
        chunk = chunk.strip()
        if not chunk:
            continue
        if _BLOCK_START.match(chunk):
            parts.append(chunk)
        else:
            parts.append("<p>" + chunk.replace("\n", "<br>") + "</p>")
    html = "\n".join(parts)

    for index, code in enumerate(blocks):
        html = html.replace(f"<!--CODE{index}-->", f"<pre><code>{code}</code></pre>")
    return mark_safe(html)
