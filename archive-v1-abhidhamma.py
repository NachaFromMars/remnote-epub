#!/usr/bin/env python3
"""
Abhidhamma Discovery Series — EPUB V3
Clean, iPhone-optimized, no visual noise
"""

import os
import re
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path

TITLE = "Abhidhamma Discovery Series"
AUTHOR = "Tieudzao"
LANG = "vi"
DESCRIPTION = "Khám phá Abhidhamma qua 28 bài viết Discovery — từ Xúc (Phassa) đến Nibbāna."
DATE = "2026-03-31"
BOOK_UUID = str(uuid.uuid4())

BASE_DIR = Path(__file__).parent
CHAPTERS_DIR = BASE_DIR / "chapters"
GLOSSARY_DIR = BASE_DIR / "glossary"
COVER_IMG = BASE_DIR / "images" / "cover.jpg"
OUTPUT = BASE_DIR / "Abhidhamma-Discovery-Series-V3.epub"

CHAPTER_FILES = [
    ("01-Phassa-Xuc.md", "Khoảnh Khắc Bạn Chạm Vào Cốc Nước Nóng"),
    ("02-Vedana-Tho.md", "Tại Sao Cùng 1 Bài Hát — Hôm Nay Thích, Mai Ghét?"),
    ("03-Sanna-Tuong.md", "Bạn Nhận Ra Mẹ Trong Đám Đông Ngàn Người"),
    ("04-Cetana-Tu.md", "Khoảnh Khắc Bạn Quyết Định Nhấc Điện Thoại"),
    ("05-Paramattha-vs-Pannatti.md", "Thế Giới Thật — Có Thật Không?"),
    ("06-4-Paramattha-Dhamma.md", "4 Thứ Duy Nhất Thật Sự Tồn Tại"),
    ("07-Sabbacittasadhaarana-Cetasika.md", "7 Thứ Luôn Có Mặt Mỗi Khi Bạn Biết"),
    ("08-Dosa-Akusala-Cetasika.md", "Cơn Giận Đến Từ Đâu?"),
    ("09-Lobha-TikTok.md", "Tại Sao Cuộn TikTok Không Dừng Được?"),
    ("10-Sobhana-Cetasika.md", "Khoảnh Khắc Giúp Ai Đó Mà Không Nghĩ"),
    ("11-52-Cetasika-Overview.md", "52 Nhân Viên — Bản Đồ Đội Ngũ Tâm"),
    ("12-89-Citta.md", "89 Loại Biết — Tâm Không Chỉ Có 1 Kiểu"),
    ("12A-Kamavacara-Citta.md", "Tâm Dục Giới: 54 Loại Tâm Thường Nhật"),
    ("12B-Mahaggata-Lokuttara-Citta.md", "Tâm Đáo Đại và Siêu Thế"),
    ("13-Citta-Cetasika-Relationship.md", "Khi Citta Gặp Cetasika — Ai Chọn Ai?"),
    ("14-Citta-Khana.md", "0.00003 Giây — Cuộc Đời 1 Sát-na Tâm"),
    ("15-Vithi-Citta.md", "Bạn Thấy 1 Con Chó — Tâm Trải Qua 17 Bước"),
    ("16-Javana-Kamma.md", "7 Sát-na Javana — Nơi Nghiệp Được Tạo"),
    ("17-Manodvara-Vithi.md", "Suy Nghĩ Đến Từ Đâu? — Ý Môn Lộ Trình"),
    ("18-Bhavanga-Patisandhi-Cuti.md", "Khi Bạn Ngủ Say — Bạn Ở Đâu?"),
    ("19-Cuti-Patisandhi-Rebirth.md", "Chết Rồi Thì Sao? — Cơ Chế Tái Sinh"),
    ("20-24-Paccaya-Patthana.md", "24 Sợi Dây Nối Mọi Thứ"),
    ("21-28-Rupa-Mahabhuta.md", "Cơ Thể Bạn — Không Có Gì Cứng Ở Đó"),
    ("22-Paticcasamuppada.md", "Bạn Đang Bị Lập Trình — Bởi Chính Bạn"),
    ("23-Khandha-Ayatana-Dhatu.md", "3 Cách Nhìn Cùng 1 Thứ — Uẩn, Xứ, Giới"),
    ("24-31-Bhumi.md", "31 Cõi — Bạn Có Thể Sinh Ra Ở Đâu?"),
    ("25-Satipatthana.md", "Chánh Niệm Không Phải Để Ý"),
    ("26-Jhana.md", "Thiền Định — Tâm Thay Đổi Khi Nhập Jhāna"),
    ("27-Vipassana-Nana.md", "16 Bước Từ Phàm Đến Thánh"),
    ("28-Magga-Phala-Nibbana.md", "1 Sát-na Thay Đổi Tất Cả"),
]

GLOSSARY_FILES = [
    ("Glossary-Arc-1-2.md", "Thuật Ngữ — Arc 1 và 2"),
    ("Glossary-Arc-3-4.md", "Thuật Ngữ — Arc 3 và 4"),
    ("Glossary-Arc-5-Master.md", "Thuật Ngữ — Arc 5 và Tổng Hợp"),
]

ARC_INFO = {
    0: ("ARC 1", "Nền Tảng — Tâm Sở và Thực Tại", "Bài 1 – 7"),
    7: ("ARC 2", "Thiện Ác Toàn Cảnh", "Bài 8 – 13"),
    15: ("ARC 3", "Lộ Trình Tâm và Nghiệp", "Bài 14 – 19"),
    21: ("ARC 4", "Sắc Pháp, Duyên Hệ và Vũ Trụ", "Bài 20 – 24"),
    26: ("ARC 5", "Con Đường và Giải Thoát", "Bài 25 – 28"),
}


def esc(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;").replace("'", "&apos;")


def inline(text):
    """Convert inline markdown. __x__ → <em>, **x** → <strong>, *x* → <em>"""
    parts_b = []
    def save_b(m):
        i = len(parts_b); parts_b.append(m.group(1)); return f"\x00B{i}\x00"
    text = re.sub(r'\*\*(.+?)\*\*', save_b, text)
    
    parts_i = []
    def save_i(m):
        i = len(parts_i); parts_i.append(m.group(1)); return f"\x00I{i}\x00"
    text = re.sub(r'__(.+?)__', save_i, text)
    
    parts_si = []
    def save_si(m):
        i = len(parts_si); parts_si.append(m.group(1)); return f"\x00S{i}\x00"
    text = re.sub(r'(?<!\*)\*([^*]+?)\*(?!\*)', save_si, text)
    
    text = esc(text)
    
    for i, p in enumerate(parts_b):
        text = text.replace(f"\x00B{i}\x00", f"<strong>{esc(p)}</strong>")
    for i, p in enumerate(parts_i):
        text = text.replace(f"\x00I{i}\x00", f"<em>{esc(p)}</em>")
    for i, p in enumerate(parts_si):
        text = text.replace(f"\x00S{i}\x00", f"<em>{esc(p)}</em>")
    
    return text


def strip_emoji_from_heading(text):
    """Remove emoji from section headings for cleaner look"""
    # Remove common section emojis
    text = re.sub(r'^[🔑🏷️👁️🧩🧭🧾⚙️🔬🌉💎📚🔗💡🏗️🎯⚖️🧠📖✨🪷☸️⚡🔥🛡️📌🎭🌊💀🏛️🌿🔮🕊️🧪📐🪞🌀🎪]\s*', '', text)
    # Also handle emoji ZWJ sequences that might remain
    text = re.sub(r'^[\U0001F300-\U0001FAFF\U00002702-\U000027B0\U0000FE00-\U0000FE0F\U0000200D]+\s*', '', text)
    return text.strip()


def md_to_html(md_text, chapter_num=None):
    """Convert markdown to clean XHTML body"""
    lines = md_text.split('\n')
    out = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        if not stripped:
            i += 1
            continue
        
        # Headings
        hm = re.match(r'^(#{1,6})\s+(.+)$', stripped)
        if hm:
            lvl = len(hm.group(1))
            title = hm.group(2)
            
            if lvl == 1:
                # Chapter title - keep as is but clean
                clean_title = inline(title)
                out.append(f'<h1>{clean_title}</h1>')
            elif lvl == 2:
                # Section heading - strip emoji, clean typography
                clean = strip_emoji_from_heading(title)
                out.append(f'<h2>{inline(clean)}</h2>')
            else:
                clean = strip_emoji_from_heading(title)
                out.append(f'<h{lvl}>{inline(clean)}</h{lvl}>')
            i += 1
            continue
        
        # Count tabs
        tabs = 0
        t = line
        while t.startswith('\t'):
            tabs += 1
            t = t[1:]
        
        # Bullet list: collect consecutive bullets at same indent
        bm = re.match(r'^(\t*)-\s+(.+)$', line)
        if bm:
            indent = len(bm.group(1))
            items = []
            while i < len(lines):
                bm2 = re.match(r'^(\t*)-\s+(.+)$', lines[i])
                if bm2 and len(bm2.group(1)) == indent:
                    content = inline(bm2.group(2))
                    # Check if callout
                    if content.startswith('💡'):
                        items.append(f'<li class="tip">{content}</li>')
                    else:
                        items.append(f'<li>{content}</li>')
                    i += 1
                else:
                    break
            
            ml = f' style="margin-left:{indent * 1.2}em;"' if indent > 0 else ''
            out.append(f'<ul{ml}>')
            out.extend(items)
            out.append('</ul>')
            continue
        
        # TAB-indented lines → indented paragraph
        if tabs > 0:
            content = inline(stripped)
            ml = tabs * 1.2
            if stripped.startswith('💡'):
                out.append(f'<p class="tip" style="margin-left:{ml}em;">{content}</p>')
            else:
                out.append(f'<p style="margin-left:{ml}em;">{content}</p>')
            i += 1
            continue
        
        # 💡 Callout at root level
        if stripped.startswith('💡'):
            out.append(f'<p class="tip">{inline(stripped)}</p>')
            i += 1
            continue
        
        # Regular prose paragraph — collect lines until blank/heading/bullet/tab
        para = []
        while i < len(lines):
            cur = lines[i]
            cs = cur.strip()
            if not cs:
                break
            if re.match(r'^#{1,6}\s+', cs):
                break
            if re.match(r'^\t*-\s+', cur):
                break
            if cur.startswith('\t'):
                break
            para.append(inline(cs))
            i += 1
        
        if para:
            # Each line becomes its own paragraph for proper spacing
            # But truly short continuation lines should join
            for p in para:
                out.append(f'<p>{p}</p>')
        continue
    
    return '\n'.join(out)


def wrap_xhtml(title, body, css="../Styles/style.css"):
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml"
      xmlns:epub="http://www.idpf.org/2007/ops"
      lang="{LANG}" xml:lang="{LANG}">
<head>
  <meta charset="UTF-8"/>
  <title>{esc(title)}</title>
  <link rel="stylesheet" type="text/css" href="{css}"/>
</head>
<body>
{body}
</body>
</html>'''


def arc_page(label, subtitle, rng):
    body = f'''<div class="arc">
  <p class="arc-sym">☸</p>
  <h1>{esc(label)}</h1>
  <p class="arc-sub">{esc(subtitle)}</p>
  <p class="arc-rng">{esc(rng)}</p>
</div>'''
    return wrap_xhtml(label, body)


# ── CSS: iPhone-first, clean, spacious ──
CSS = r'''@charset "UTF-8";

/* ─── Abhidhamma Discovery Series ─── */
/* iPhone-first · Clean · Spacious · No visual noise */

body {
  font-family: Georgia, "Times New Roman", serif;
  font-size: 1.1em;
  line-height: 1.9;
  margin: 0.8em 1em;
  padding: 0;
  color: #222;
  background: #fff;
  text-align: left;
  -webkit-hyphens: none;
  hyphens: none;
  word-wrap: break-word;
  overflow-wrap: break-word;
}

/* ─── Headings ─── */
h1 {
  font-size: 1.4em;
  font-weight: 700;
  color: #111;
  margin: 1.8em 0 1em 0;
  line-height: 1.35;
  text-align: left;
}

h2 {
  font-size: 1.15em;
  font-weight: 700;
  color: #333;
  margin: 2em 0 0.8em 0;
  padding-top: 0.6em;
  line-height: 1.3;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

h3 {
  font-size: 1.05em;
  font-weight: 600;
  color: #444;
  margin: 1.5em 0 0.6em 0;
}

/* ─── Paragraphs — generous spacing ─── */
p {
  margin: 0.8em 0;
  text-indent: 0;
}

/* ─── Lists — clean bullets ─── */
ul {
  margin: 0.6em 0;
  padding-left: 1.4em;
  list-style-type: disc;
}

li {
  margin-bottom: 0.6em;
  line-height: 1.8;
}

/* ─── Inline ─── */
strong {
  font-weight: 700;
}

em {
  font-style: italic;
  color: #555;
}

/* ─── Tips / Callouts — subtle, no box ─── */
.tip {
  font-style: italic;
  color: #444;
  margin: 1em 0;
  padding: 0;
}

li.tip {
  list-style: none;
  margin-left: -1.4em;
  padding-left: 0;
}

/* ─── Tables ─── */
table {
  border-collapse: collapse;
  margin: 1em 0;
  width: 100%;
  font-size: 0.85em;
}
th, td {
  border: 1px solid #ccc;
  padding: 0.4em 0.5em;
  text-align: left;
  vertical-align: top;
}
th {
  background: #f5f5f5;
  font-weight: 600;
}

/* ─── Separator ─── */
hr {
  border: none;
  text-align: center;
  margin: 2.5em 0;
  height: 1em;
}
hr::after {
  content: "· · ·";
  color: #aaa;
  font-size: 1.2em;
  letter-spacing: 0.5em;
}

/* ─── Cover ─── */
.cover {
  text-align: center;
  padding: 0;
  margin: 0;
}
.cover img {
  max-width: 100%;
  max-height: 100%;
}

/* ─── Title page ─── */
.title-page {
  text-align: center;
  margin-top: 28%;
}
.title-page h1 {
  font-size: 1.7em;
  margin: 0 0 0.3em 0;
  text-align: center;
}
.title-page .sub {
  font-size: 0.95em;
  color: #666;
  font-style: italic;
  margin: 0.5em 0 2.5em 0;
}
.title-page .author {
  font-size: 1.2em;
  color: #333;
  margin: 0;
}
.title-page .year {
  font-size: 0.9em;
  color: #999;
  margin-top: 3em;
}
.title-page .orn {
  font-size: 1.3em;
  color: #b89a5a;
  margin: 1.5em 0;
}

/* ─── Dedication ─── */
.dedication {
  text-align: center;
  margin-top: 28%;
  line-height: 2.2;
}
.dedication .pali {
  font-weight: 600;
  font-size: 1em;
  color: #333;
  margin-bottom: 1.5em;
}

/* ─── Copyright ─── */
.copyright {
  font-size: 0.85em;
  color: #777;
  margin-top: 28%;
  text-align: center;
  line-height: 2;
}

/* ─── Arc divider ─── */
.arc {
  text-align: center;
  margin-top: 32%;
}
.arc .arc-sym {
  font-size: 2em;
  color: #b89a5a;
  margin: 0 0 0.5em 0;
}
.arc h1 {
  font-size: 1.5em;
  text-align: center;
  margin: 0.3em 0;
  border: none;
  padding: 0;
}
.arc .arc-sub {
  font-size: 1em;
  font-style: italic;
  color: #666;
  margin: 0.3em 0;
}
.arc .arc-rng {
  font-size: 0.85em;
  color: #999;
  margin: 0.5em 0 0;
}

/* ─── TOC ─── */
nav ol {
  list-style-type: none;
  padding-left: 0;
}
nav li {
  margin: 0.5em 0;
}
nav a {
  color: #333;
  text-decoration: none;
}
nav .arc-entry {
  font-weight: 700;
  color: #b89a5a;
  margin-top: 1em;
  font-size: 0.9em;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
'''


def build():
    items = []   # (id, fname, title, xhtml, is_arc)
    toc = []     # (title, fname, is_arc)
    idx = 0

    for ci, (mdf, title) in enumerate(CHAPTER_FILES):
        # Arc divider?
        if ci in ARC_INFO:
            al, asub, ar = ARC_INFO[ci]
            af = f"arc-{idx:03d}.xhtml"
            items.append((f"arc{idx}", af, al, arc_page(al, asub, ar), True))
            toc.append((f"{al}: {asub}", af, True))
            idx += 1
        
        md = (CHAPTERS_DIR / mdf).read_text('utf-8')
        body = md_to_html(md, ci+1)
        fid = f"ch{idx}"
        fname = f"ch-{idx:03d}.xhtml"
        xhtml = wrap_xhtml(title, f'<article>\n{body}\n</article>')
        items.append((fid, fname, title, xhtml, False))
        toc.append((f"#{ci+1}  {title}", fname, False))
        idx += 1

    # Glossary arc
    gaf = f"arc-{idx:03d}.xhtml"
    items.append((f"arcg{idx}", gaf, "Thuật Ngữ", arc_page("THUẬT NGỮ", "Pali – Việt Glossary", ""), True))
    toc.append(("Thuật Ngữ", gaf, True))
    idx += 1

    for glf, glt in GLOSSARY_FILES:
        md = (GLOSSARY_DIR / glf).read_text('utf-8')
        body = md_to_html(md)
        fid = f"gl{idx}"
        fname = f"gl-{idx:03d}.xhtml"
        xhtml = wrap_xhtml(glt, f'<article>\n{body}\n</article>')
        items.append((fid, fname, glt, xhtml, False))
        toc.append((glt, fname, False))
        idx += 1

    # Build ZIP
    with zipfile.ZipFile(OUTPUT, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('mimetype', 'application/epub+zip', compress_type=zipfile.ZIP_STORED)

        z.writestr('META-INF/container.xml', '''<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>''')

        with open(COVER_IMG, 'rb') as f:
            z.writestr('OEBPS/Images/cover.jpg', f.read())

        z.writestr('OEBPS/Styles/style.css', CSS)

        # Cover
        z.writestr('OEBPS/Text/cover.xhtml', wrap_xhtml("Bìa", f'''<div class="cover">
  <img src="../Images/cover.jpg" alt="{esc(TITLE)}"/>
</div>'''))

        # Title
        z.writestr('OEBPS/Text/title.xhtml', wrap_xhtml(TITLE, f'''<div class="title-page">
  <p class="orn">☸</p>
  <h1>{esc(TITLE)}</h1>
  <p class="sub">Hành trình khám phá Vi Diệu Pháp qua 28 bài viết</p>
  <p class="orn">᭄</p>
  <p class="author">{esc(AUTHOR)}</p>
  <p class="year">2026</p>
</div>'''))

        # Dedication
        z.writestr('OEBPS/Text/dedication.xhtml', wrap_xhtml("Lời Nguyện", '''<div class="dedication">
  <p class="pali">Namo Tassa Bhagavato Arahato Sammāsambuddhassa</p>
  <p>Dành tặng tất cả những ai đang tìm kiếm<br/>sự thật về tâm —<br/>không qua niềm tin,<br/>mà qua sự quan sát.</p>
</div>'''))

        # Copyright
        z.writestr('OEBPS/Text/copyright.xhtml', wrap_xhtml("Bản Quyền", f'''<div class="copyright">
  <p><strong>{esc(TITLE)}</strong></p>
  <p>Tác giả: {esc(AUTHOR)}</p>
  <p>© 2026 {esc(AUTHOR)}</p>
</div>'''))

        # Chapters
        for fid, fname, title, xhtml, _ in items:
            z.writestr(f'OEBPS/Text/{fname}', xhtml)

        # TOC nav
        toc_li = ['    <li><a href="Text/cover.xhtml">Bìa</a></li>',
                   '    <li><a href="Text/title.xhtml">Trang Tựa</a></li>',
                   '    <li><a href="Text/dedication.xhtml">Lời Nguyện</a></li>']
        for t, f, is_arc in toc:
            cls = ' class="arc-entry"' if is_arc else ''
            toc_li.append(f'    <li{cls}><a href="Text/{f}">{esc(t)}</a></li>')

        z.writestr('OEBPS/toc.xhtml', wrap_xhtml("Mục Lục", f'''<nav epub:type="toc" id="toc">
  <h1>Mục Lục</h1>
  <ol>
{chr(10).join(toc_li)}
  </ol>
</nav>''', css="Styles/style.css"))

        # NCX
        nps = []
        po = 1
        for t, f, _ in toc:
            nps.append(f'    <navPoint id="n{po}" playOrder="{po}"><navLabel><text>{esc(t)}</text></navLabel><content src="Text/{f}"/></navPoint>')
            po += 1
        z.writestr('OEBPS/toc.ncx', f'''<?xml version="1.0" encoding="UTF-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
  <head><meta name="dtb:uid" content="urn:uuid:{BOOK_UUID}"/></head>
  <docTitle><text>{esc(TITLE)}</text></docTitle>
  <navMap>
{chr(10).join(nps)}
  </navMap>
</ncx>''')

        # OPF
        man = ['    <item id="cover-img" href="Images/cover.jpg" media-type="image/jpeg" properties="cover-image"/>',
               '    <item id="css" href="Styles/style.css" media-type="text/css"/>',
               '    <item id="nav" href="toc.xhtml" media-type="application/xhtml+xml" properties="nav"/>',
               '    <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>',
               '    <item id="cover" href="Text/cover.xhtml" media-type="application/xhtml+xml"/>',
               '    <item id="titlep" href="Text/title.xhtml" media-type="application/xhtml+xml"/>',
               '    <item id="dedic" href="Text/dedication.xhtml" media-type="application/xhtml+xml"/>',
               '    <item id="copyr" href="Text/copyright.xhtml" media-type="application/xhtml+xml"/>']
        spine = ['    <itemref idref="cover"/>',
                 '    <itemref idref="titlep"/>',
                 '    <itemref idref="dedic"/>']
        for fid, fname, _, _, _ in items:
            man.append(f'    <item id="{fid}" href="Text/{fname}" media-type="application/xhtml+xml"/>')
            spine.append(f'    <itemref idref="{fid}"/>')
        spine.append('    <itemref idref="copyr"/>')

        now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        z.writestr('OEBPS/content.opf', f'''<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="uid">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="uid">urn:uuid:{BOOK_UUID}</dc:identifier>
    <dc:title>{esc(TITLE)}</dc:title>
    <dc:creator>{esc(AUTHOR)}</dc:creator>
    <dc:language>{LANG}</dc:language>
    <dc:description>{esc(DESCRIPTION)}</dc:description>
    <dc:date>{DATE}</dc:date>
    <meta property="dcterms:modified">{now}</meta>
  </metadata>
  <manifest>
{chr(10).join(man)}
  </manifest>
  <spine toc="ncx">
{chr(10).join(spine)}
  </spine>
</package>''')

    sz = OUTPUT.stat().st_size
    print(f"✅ EPUB V3 built: {OUTPUT.name} ({sz:,} bytes)")


if __name__ == '__main__':
    build()
