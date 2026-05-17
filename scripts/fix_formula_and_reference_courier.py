from pathlib import Path

from docx import Document
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor


ROOT = Path(__file__).resolve().parents[2]
TARGETS = [
    ROOT / "Vương Văn Duy_Báo cáo.docx",
    ROOT / "Bao_Cao" / "02_Chuong_2_ban_dinh_dang_theo_mau.docx",
]
BLACK = RGBColor(0, 0, 0)


def set_times(run, size: int) -> None:
    run.font.name = "Times New Roman"
    run.font.size = Pt(size)
    run.font.color.rgb = BLACK
    r_pr = run._element.get_or_add_rPr()
    r_fonts = r_pr.rFonts
    if r_fonts is not None:
        for attr in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
            r_fonts.set(qn(attr), "Times New Roman")


def main() -> None:
    for target in TARGETS:
        if not target.exists():
            continue
        doc = Document(target)
        changed = 0
        for paragraph in doc.paragraphs:
            if "$$" in paragraph.text or "keychain_services" in paragraph.text or "apple_ref" in paragraph.text:
                for run in paragraph.runs:
                    if run.text:
                        set_times(run, 14)
                        changed += 1
        if changed:
            doc.save(target)
        print(target, changed)


if __name__ == "__main__":
    main()
