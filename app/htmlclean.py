"""Assignment descriptions arrive as teacher-written HTML; keep a small safe subset and plain text for the AI."""

import html
import re
from html.parser import HTMLParser

ALLOWED = {"p", "br", "ul", "ol", "li", "b", "strong", "i", "em", "u", "a", "h1", "h2", "h3", "h4", "h5",
           "blockquote", "pre", "code", "table", "thead", "tbody", "tr", "td", "th", "hr", "span", "div", "sub", "sup"}
VOID = {"br", "hr"}
DROP_CONTENT = {"script", "style", "iframe", "object", "embed", "noscript", "template", "svg", "math", "head", "title"}
BLOCK = {"p", "div", "li", "tr", "h1", "h2", "h3", "h4", "h5", "blockquote", "pre", "table", "ul", "ol", "br", "hr"}


def _safe_href(href: str) -> str | None:
    href = (href or "").strip()
    return href if re.match(r"^(https?:|mailto:)", href, re.I) else None


class _Cleaner(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out: list[str] = []
        self.text: list[str] = []
        self.skip = 0
        self.open: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag in DROP_CONTENT:
            self.skip += 1
            return
        if self.skip:
            return
        if tag in BLOCK:
            self.text.append("\n")
        if tag == "img":
            alt = dict(attrs).get("alt") or "image"
            self.out.append(f"<em>[{html.escape(alt)}]</em>")
            return
        if tag not in ALLOWED:
            return
        if tag == "a":
            href = _safe_href(dict(attrs).get("href"))
            if href:
                self.out.append(f'<a href="{html.escape(href, quote=True)}" target="_blank" rel="noopener noreferrer">')
            else:
                self.out.append("<a>")
        else:
            self.out.append(f"<{tag}>")
        if tag not in VOID:
            self.open.append(tag)

    def handle_endtag(self, tag):
        if tag in DROP_CONTENT:
            self.skip = max(0, self.skip - 1)
            return
        if self.skip or tag not in ALLOWED or tag in VOID or tag not in self.open:
            return
        while self.open:
            t = self.open.pop()
            self.out.append(f"</{t}>")
            if t == tag:
                break
        if tag in BLOCK:
            self.text.append("\n")

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)

    def handle_data(self, data):
        if self.skip:
            return
        self.out.append(html.escape(data))
        self.text.append(data)

    def result(self) -> tuple[str, str]:
        while self.open:
            self.out.append(f"</{self.open.pop()}>")
        text = re.sub(r"[ \t\r\f\v]+", " ", "".join(self.text))
        text = re.sub(r"\n\s*\n+", "\n\n", text).strip()
        return "".join(self.out).strip(), text


def clean(raw: str | None) -> str:
    """Safe HTML for display."""
    if not raw:
        return ""
    p = _Cleaner()
    p.feed(raw)
    p.close()
    return p.result()[0]


def to_text(raw: str | None) -> str:
    """Plain text (for heuristics and the AI prompt)."""
    if not raw:
        return ""
    p = _Cleaner()
    p.feed(raw)
    p.close()
    return p.result()[1]


def text_to_html(text: str) -> str:
    """Plain-text descriptions (calendar feeds) -> paragraphs, with bare links made clickable."""
    if not text:
        return ""
    out = []
    for para in re.split(r"\n\s*\n", text.strip()):
        esc = html.escape(para).replace("\n", "<br>")
        esc = re.sub(r"(https?://[^\s<]+)", r'<a href="\1" target="_blank" rel="noopener noreferrer">\1</a>', esc)
        out.append(f"<p>{esc}</p>")
    return "".join(out)
