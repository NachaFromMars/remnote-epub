#!/usr/bin/env python3
"""
RemNote-EPUB v2 — Universal EPUB Builder for RemNote Analysis
Converts RemNote-style markdown → EPUB 3.3 premium
"""

import argparse
import json
import os
import re
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from html import escape

SKILL_DIR = Path(__file__).parent.parent
TEMPLATE_CSS = SKILL_DIR / "templates" / "style.css"


def parse_args():
    p = argparse.ArgumentParser(description="Build EPUB from RemNote markdown")
    p.add_argument("--input", "-i", required=True, help="Input .md file or directory of .xhtml chapters")
    p.add_argument("--output", "-o", required=True, help="Output .epub path")
    p.add_argument("--title", "-t", default="Analysis", help="Book title")
    p.add_argument("--author", "-a", default="Tiểu Tâm", help="Author/analyst")
    p.add_argument("--language", "-l", default="vi", help="Language code")
    p.add_argument("--description", "-d", default="", help="Book description")
    p.add_argument("--css", default=None, help="Custom CSS path (defaults to template)")
    return p.parse_args()


def escape_xml(text):
    """Escape for XHTML content."""
    return escape(text, quote=True)


def md_line_to_html(line):
    """Convert a single RemNote markdown line to HTML."""
    # Bold: **text** → <strong>text</strong>
    line = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', line)
    # RemNote italic: ( __text__ ) → (<em>text</em>)
    line = re.sub(r'\( __([^_]+)__ \)', r'(<em>\1</em>)', line)
    # Markdown italic in parens: (*text*) → (<em>text</em>)
    line = re.sub(r'\(\*([^*]+)\*\)', r'(<em>\1</em>)', line)
    # Standalone italic: *text* → <em>text</em>  
    line = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'<em>\1</em>', line)
    # Arrows
    line = line.replace('→', '&#x2192;').replace('←', '&#x2190;')
    line = line.replace('↔', '&#x2194;')
    # Em dash
    line = line.replace(' — ', ' &#x2014; ').replace('—', '&#x2014;')
    # Ampersand (careful: don't double-escape)
    # Already handled by content
    return line


def split_flashcard(line):
    """Split 'Front :: Back' into (front, back) or None."""
    if '::' in line:
        parts = line.split('::', 1)
        if len(parts) == 2:
            return parts[0].strip(), parts[1].strip()
    return None


def md_to_chapter_xhtml(title, content_lines, chapter_id="chapter"):
    """Convert RemNote markdown lines to XHTML chapter."""
    html_parts = []
    html_parts.append(f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="vi" xml:lang="vi">
<head>
  <title>{escape_xml(title)}</title>
  <link rel="stylesheet" type="text/css" href="../styles/style.css"/>
</head>
<body>
  <section epub:type="chapter" aria-label="{escape_xml(title)}">''')

    for line in content_lines:
        stripped = line.lstrip('\t').strip()
        if not stripped:
            continue

        # Headings
        if stripped.startswith('# ') and not stripped.startswith('## '):
            html_parts.append(f'    <h1>{md_line_to_html(stripped[2:])}</h1>')
        elif stripped.startswith('## '):
            html_parts.append(f'    <h2>{md_line_to_html(stripped[3:])}</h2>')
        elif stripped.startswith('### '):
            html_parts.append(f'    <h3>{md_line_to_html(stripped[4:])}</h3>')
        elif stripped.startswith('#### '):
            html_parts.append(f'    <h4>{md_line_to_html(stripped[5:])}</h4>')
        # Essence box
        elif stripped.startswith('🔑'):
            html_parts.append(f'    <div class="essence-box"><p>{md_line_to_html(stripped)}</p></div>')
        # Misconception
        elif stripped.startswith('⚠️'):
            html_parts.append(f'    <div class="misconception"><p>{md_line_to_html(stripped)}</p></div>')
        # Bridge
        elif stripped.startswith('🌉'):
            html_parts.append(f'    <div class="bridge"><p>{md_line_to_html(stripped)}</p></div>')
        # Flashcard
        elif '::' in stripped and split_flashcard(stripped):
            front, back = split_flashcard(stripped)
            html_parts.append(f'''    <div class="flashcard">
      <p class="front">{md_line_to_html(front)}</p>
      <p class="back">{md_line_to_html(back)}</p>
    </div>''')
        # Regular paragraph
        else:
            html_parts.append(f'    <p>{md_line_to_html(stripped)}</p>')

    html_parts.append('  </section>\n</body>\n</html>')
    return '\n'.join(html_parts)


def split_md_into_sections(md_path):
    """Split a RemNote markdown file into sections by ## headings."""
    with open(md_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    sections = []
    current_title = "Untitled"
    current_lines = []

    for line in lines:
        stripped = line.rstrip('\n')
        # Top-level heading = book title (skip as section)
        if stripped.startswith('# ') and not stripped.startswith('## '):
            if not sections and not current_lines:
                # First # heading = book title, include in first section
                current_lines.append(stripped)
                continue
        # Section break at ##
        if stripped.startswith('## '):
            if current_lines:
                sections.append((current_title, current_lines))
            current_title = stripped[3:].strip()
            current_lines = [stripped]
        else:
            current_lines.append(stripped)

    if current_lines:
        sections.append((current_title, current_lines))

    return sections


def build_epub(args):
    uid = f"urn:uuid:{uuid.uuid4()}"
    modified = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Load CSS
    css_path = args.css or str(TEMPLATE_CSS)
    with open(css_path, 'r') as f:
        css_content = f.read()

    input_path = Path(args.input)

    # If input is a directory of .xhtml files, use directly
    if input_path.is_dir():
        chapters = sorted([f for f in os.listdir(input_path) if f.endswith('.xhtml')])
        chapter_contents = {}
        for ch in chapters:
            with open(input_path / ch, 'r') as f:
                chapter_contents[ch] = f.read()
    else:
        # Parse markdown into sections and convert
        sections = split_md_into_sections(str(input_path))
        chapters = []
        chapter_contents = {}

        for i, (title, lines) in enumerate(sections):
            filename = f"ch{i:02d}-{re.sub(r'[^a-zA-Z0-9]', '-', title.lower())[:30].strip('-')}.xhtml"
            xhtml = md_to_chapter_xhtml(title, lines, f"ch{i:02d}")
            chapters.append(filename)
            chapter_contents[filename] = xhtml

    print(f"Building EPUB: {len(chapters)} chapters")

    # --- OPF ---
    manifest_items = []
    spine_items = []
    for i, ch in enumerate(chapters):
        item_id = f"ch{i:02d}"
        manifest_items.append(f'    <item id="{item_id}" href="text/{ch}" media-type="application/xhtml+xml"/>')
        spine_items.append(f'    <itemref idref="{item_id}"/>')
    manifest_items.append('    <item id="style" href="styles/style.css" media-type="text/css"/>')
    manifest_items.append('    <item id="nav" href="toc.xhtml" media-type="application/xhtml+xml" properties="nav"/>')

    opf = f'''<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="uid" version="3.0">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="uid">{uid}</dc:identifier>
    <dc:title>{escape_xml(args.title)}</dc:title>
    <dc:creator>{escape_xml(args.author)}</dc:creator>
    <dc:language>{args.language}</dc:language>
    <dc:description>{escape_xml(args.description)}</dc:description>
    <meta property="dcterms:modified">{modified}</meta>
  </metadata>
  <manifest>
{chr(10).join(manifest_items)}
  </manifest>
  <spine>
{chr(10).join(spine_items)}
  </spine>
</package>'''

    # --- TOC ---
    toc_li = []
    for ch in chapters:
        # Extract title from filename
        title = ch.replace('.xhtml', '').split('-', 1)[-1].replace('-', ' ').title() if '-' in ch else ch
        toc_li.append(f'        <li><a href="text/{ch}">{escape_xml(title)}</a></li>')

    toc_xhtml = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="{args.language}" xml:lang="{args.language}">
<head><title>Mục Lục</title></head>
<body>
  <nav epub:type="toc">
    <h1>Mục Lục</h1>
    <ol>
{chr(10).join(toc_li)}
    </ol>
  </nav>
</body>
</html>'''

    # --- Container ---
    container = '''<?xml version="1.0" encoding="UTF-8"?>
<container xmlns="urn:oasis:names:tc:opendocument:xmlns:container" version="1.0">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>'''

    # --- Write EPUB ---
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(str(output), 'w') as epub:
        epub.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)
        epub.writestr("META-INF/container.xml", container)
        epub.writestr("OEBPS/content.opf", opf)
        epub.writestr("OEBPS/toc.xhtml", toc_xhtml)
        epub.writestr("OEBPS/styles/style.css", css_content)
        for ch in chapters:
            epub.writestr(f"OEBPS/text/{ch}", chapter_contents[ch])

    size = output.stat().st_size
    print(f"✅ EPUB built: {output}")
    print(f"   Chapters: {len(chapters)}")
    print(f"   Size: {size:,} bytes")


if __name__ == "__main__":
    args = parse_args()
    build_epub(args)
