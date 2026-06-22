---
name: remnote-epub
description: "Build premium EPUB from RemNote-style markdown analysis. Converts Essence Lens book analysis, flashcards, glossary song ngữ into beautiful EPUB 3.3. Handles ( __italic__ ), **bold**, TAB hierarchy, essence boxes, flashcards, misconceptions, cross-domain bridges, bilingual glossary. Aliases: epub-remnote, epub remnote, remnote-epub, remnote epub. Auto-trigger when exporting any RemNote analysis to EPUB."
version: 2.0.0
aliases:
  - epub-remnote
  - epub remnote
  - remnote-epub
  - remnote epub
---

# RemNote-EPUB v2 — Premium EPUB Builder for RemNote Analysis

Build premium EPUB 3.3 from RemNote-style markdown analysis files.
Designed for book analysis with Essence Lens, flashcards, bilingual glossary.

**v2.0** — Complete rewrite based on Start with Why analysis template (04/2026).
Replaces v1 (Abhidhamma-only). Now universal for any book/topic analysis.

## Aliases (trigger any of these)
- `epub-remnote`, `epub remnote`, `remnote-epub`, `remnote epub`
- Any EPUB export from RemNote analysis files
- "xuất epub từ remnote", "build epub analysis"

## When to Use
- Converting RemNote markdown analysis → EPUB
- Book analysis with Essence Lens sections
- Any file with: flashcards (::), essence boxes (🔑), glossary entries, ( __italic__ )
- NOT for: novels, raw markdown, non-analysis content (use epub-forge or epub-builder)

## Design Principles (v2)

### Visual Hierarchy
- **Essence boxes** — warm cream background (#f8f5f0), amber left border (#C9A96E)
- **Flashcards** — cool blue background (#f0f4f8), blue left border (#4a90d9)
- **Misconceptions** — rose background (#fdf5f6), crimson left border (#8B1A2F)
- **Cross-domain bridges** — sage background (#f0f7f4), forest left border (#2d6a4f)
- **Insight boxes** — lavender background (#f5f0fa), purple left border (#7b5ea7)
- **Framework steps** — light gray (#fafafa), amber left border (#C9A96E)
- **Glossary entries** — separated by bottom border, structured layout

### Typography
- Georgia / Times New Roman / Noto Serif (safe stack for all e-readers)
- Body: 1em, line-height 1.6, max-width 40em, justified
- h1: 1.8em center, page-break-before
- h2: 1.4em, bottom border
- h3: 1.15em italic

### RemNote → XHTML Conversion Rules
| RemNote | XHTML |
|---------|-------|
| `( __text__ )` | `<em>text</em>` in parens |
| `**text**` | `<strong>text</strong>` |
| `Term :: Definition` | `.flashcard` div with `.front` + `.back` |
| `🔑 Bản chất:` | `.essence-box` div |
| `⚠️ Hiểu lầm:` | `.misconception` div |
| `🌉 Liên kết:` | `.bridge` div |
| TAB indent | Nested structure / margin |
| `# Heading` | `<h1>` (one per file) |
| `## Heading` | `<h2>` |
| `### Heading` | `<h3>` |

### Chapter Structure Template
Standard analysis EPUB has these chapters:
```
ch00-cover.xhtml          — Title, author, subtitle
ch01-core-essence.xhtml   — 🔑 Core Essence (bản chất lõi)
ch02-partN.xhtml          — Analysis parts (1 file per major section)
...
ch08-thinking-framework   — 🧠 Thinking Framework
ch09-assumptions-limits   — ⚠️ Hidden Assumptions & Limits
ch10-cross-domain         — 🌉 Cross-Domain Bridges
ch11-transferable-insights— 💎 Transferable Insights
ch12-glossary             — 📚 Bilingual Essence Glossary
```

### Glossary Entry XHTML Structure
```html
<div class="glossary-entry">
  <h3><strong>Thuật ngữ Việt</strong> (<em>English term</em>)</h3>
  <p class="essence-vi">🔑 <strong>Bản chất (VI):</strong> ...</p>
  <p class="essence-en">🔑 <strong>Essence (EN):</strong> ...</p>
  <p class="misconception">⚠️ ... / ...</p>
  <p class="bridge">🌉 ...</p>
</div>
```

## Build Script

### Usage
```bash
python3 scripts/build-remnote-epub.py \
  --input /path/to/analysis.md \
  --output /path/to/output.epub \
  --title "Book Title — Analysis" \
  --author "Analyst Name"
```

### Or manual build:
1. Parse RemNote markdown → split into chapter XHTML files
2. Apply CSS (see `templates/style.css`)
3. Generate OPF manifest + spine
4. Generate TOC (nav + NCX)
5. Package as EPUB ZIP (mimetype first, uncompressed)

## Files
- `SKILL.md` — this file
- `templates/style.css` — master CSS template
- `templates/cover.xhtml` — cover page template
- `templates/chapter.xhtml` — chapter template
- `templates/glossary.xhtml` — glossary page template
- `scripts/build-remnote-epub.py` — build script
- `scripts/md-to-xhtml.py` — RemNote markdown → XHTML converter

## Color Palette (Tiểu Tâm brand)
- Warm cream: `#f8f5f0` (essence box bg)
- Amber: `#C9A96E` (accent, essence border)
- Deep amber: `#8B6914` (essence strong)
- Cool blue: `#f0f4f8` (flashcard bg)
- Blue accent: `#4a90d9` (flashcard border)
- Blue dark: `#2a5a8a` (flashcard front)
- Crimson: `#8B1A2F` (misconception)
- Rose: `#fdf5f6` (misconception bg)
- Forest: `#2d6a4f` (bridge)
- Sage: `#f0f7f4` (bridge bg)
- Lavender: `#f5f0fa` (insight bg)
- Purple: `#7b5ea7` (insight border)
- Dark: `#2C2C2C` (headings)
- Body: `#1a1a1a` (text)

## EPUB 3.3 Compliance
- mimetype first entry, uncompressed
- Valid XHTML5 + XML namespaces
- `lang` + `xml:lang` on all `<html>`
- Navigation document with `epub:type="toc"`
- NCX backward compat
- `dcterms:modified` meta
- Structural `epub:type` attributes
- `aria-label` on sections
