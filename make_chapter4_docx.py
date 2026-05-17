#!/usr/bin/env python3
"""
Generate 04_Chuong_4.docx from 04_Chuong_4.md.

Images are in sample_images/chapter4/.
Mobile screenshots (portrait) get a light gray background + thin border
  to separate them from the white page (avoids white-on-white blending).
Admin/landscape screenshots scale up to 15cm width, no frame needed.
"""

import struct
from pathlib import Path

from docx.shared import Cm, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

import make_chapter1_docx as base

HERE = Path(__file__).parent
MD_FILE = HERE / "04_Chuong_4.md"
OUT_FILE = HERE / "04_Chuong_4.docx"
IMG_DIR = HERE / "sample_images" / "chapter4"

MAX_WIDTH_CM    = 15.0   # landscape / admin screens
MAX_HEIGHT_CM   = 18.0   # cap portrait so it doesn't fill a whole page
MOBILE_MAX_WIDTH_CM = 8.0  # portrait phone screenshots

# Frame style — matches iOS system background (#F2F2F7), light gray border
FRAME_FILL        = "F2F2F7"
FRAME_BORDER_CLR  = "C0C0C0"
FRAME_BORDER_SZ   = "6"     # eighths of a point → 0.75 pt


def _png_size(path: Path):
    try:
        with path.open("rb") as f:
            sig = f.read(8)
            if sig != b"\x89PNG\r\n\x1a\n":
                return None
            f.read(4)
            chunk_type = f.read(4)
            if chunk_type != b"IHDR":
                return None
            width, height = struct.unpack(">II", f.read(8))
            return width, height
    except Exception:
        return None


def _frame_para(para):
    """Add iOS-gray background + thin border to a paragraph."""
    pPr = para._p.get_or_add_pPr()

    # Clear previous pBdr / shd if any
    for tag in (qn("w:pBdr"), qn("w:shd")):
        for old in pPr.findall(tag):
            pPr.remove(old)

    # Border box
    pBdr = OxmlElement("w:pBdr")
    for side in ["top", "left", "bottom", "right"]:
        el = OxmlElement(f"w:{side}")
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), FRAME_BORDER_SZ)
        el.set(qn("w:space"), "8")
        el.set(qn("w:color"), FRAME_BORDER_CLR)
        pBdr.append(el)
    pPr.append(pBdr)

    # Background fill
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), FRAME_FILL)
    pPr.append(shd)


def chapter4_image_para(doc, filename):
    img_path = IMG_DIR / filename
    if not img_path.exists():
        base.normal_para(doc, f"[Hình: {filename} — không tìm thấy file]")
        return

    size = _png_size(img_path)
    px_w, px_h = size if size else (1, 1)
    aspect = px_w / px_h if px_h else 1.0
    is_portrait = aspect < 1.0

    p = doc.add_paragraph()
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    base._para_fmt(p, before=12, after=0, indent=0)

    if is_portrait:
        # Mobile screenshot: frame + constrained width
        _frame_para(p)
        width_cm = MOBILE_MAX_WIDTH_CM
        height_cm = width_cm / aspect
        if height_cm > MAX_HEIGHT_CM:
            height_cm = MAX_HEIGHT_CM
            width_cm = height_cm * aspect
    else:
        # Landscape/admin: no frame, full width
        width_cm = MAX_WIDTH_CM
        height_cm = width_cm / aspect
        if height_cm > MAX_HEIGHT_CM:
            height_cm = MAX_HEIGHT_CM
            width_cm = height_cm * aspect

    run = p.add_run()
    run.add_picture(str(img_path), width=Cm(width_cm), height=Cm(height_cm))


def main():
    base.MD_FILE = MD_FILE
    base.OUT_FILE = OUT_FILE
    base.IMG_DIR = IMG_DIR
    base.image_para = chapter4_image_para

    lines = MD_FILE.read_text(encoding="utf-8").splitlines()
    doc = base.build_doc(lines)
    doc.save(OUT_FILE)
    print(f"Saved: {OUT_FILE}")


if __name__ == "__main__":
    main()
