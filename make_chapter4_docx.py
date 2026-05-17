#!/usr/bin/env python3
"""
Generate 04_Chuong_4.docx from 04_Chuong_4.md.

Images are in sample_images/chapter4/.
Mobile screenshots (portrait) are capped at 8cm width to avoid dominating a page.
Admin/landscape screenshots scale up to 15cm width.
"""

import struct
from pathlib import Path

from docx.shared import Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH

import make_chapter1_docx as base

HERE = Path(__file__).parent
MD_FILE = HERE / "04_Chuong_4.md"
OUT_FILE = HERE / "04_Chuong_4.docx"
IMG_DIR = HERE / "sample_images" / "chapter4"

MAX_WIDTH_CM = 15.0    # landscape / admin screens
MAX_HEIGHT_CM = 18.0   # cap so portrait mobile shots don't fill the whole page
MOBILE_MAX_WIDTH_CM = 8.0  # portrait phone screenshots


def _png_size(path: Path):
    try:
        with path.open("rb") as f:
            sig = f.read(8)
            if sig != b"\x89PNG\r\n\x1a\n":
                return None
            f.read(4)  # length
            chunk_type = f.read(4)
            if chunk_type != b"IHDR":
                return None
            width, height = struct.unpack(">II", f.read(8))
            return width, height
    except Exception:
        return None


def chapter4_image_para(doc, filename):
    img_path = IMG_DIR / filename
    if not img_path.exists():
        base.normal_para(doc, f"[Hình: {filename} — không tìm thấy file]")
        return

    p = doc.add_paragraph()
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    base._para_fmt(p, before=12, after=0, indent=0)
    run = p.add_run()

    size = _png_size(img_path)
    if not size:
        run.add_picture(str(img_path), width=Cm(MAX_WIDTH_CM))
        return

    px_w, px_h = size
    aspect = px_w / px_h if px_h else 1.0
    is_portrait = aspect < 1.0  # taller than wide = mobile screenshot

    if is_portrait:
        # Phone screenshot: constrain width to MOBILE_MAX_WIDTH_CM
        width_cm = MOBILE_MAX_WIDTH_CM
        height_cm = width_cm / aspect
        if height_cm > MAX_HEIGHT_CM:
            height_cm = MAX_HEIGHT_CM
            width_cm = height_cm * aspect
    else:
        # Landscape / admin web: use full width
        width_cm = MAX_WIDTH_CM
        height_cm = width_cm / aspect
        if height_cm > MAX_HEIGHT_CM:
            height_cm = MAX_HEIGHT_CM
            width_cm = height_cm * aspect

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
