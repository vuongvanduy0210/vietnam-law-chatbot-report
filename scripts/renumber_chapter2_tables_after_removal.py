from pathlib import Path

from docx import Document


DOCX = Path(__file__).resolve().parents[1] / "02_Chuong_2_ban_bo_sung_phan_tich_rag.docx"

REN_NUMBER = {
    "Bảng 2.19": "Bảng 2.15",
    "Bảng 2.15": "Bảng 2.14",
    "Bảng 2.14": "Bảng 2.13",
    "Bảng 2.13": "Bảng 2.12",
    "Bảng 2.12": "Bảng 2.11",
    "Bảng 2.11": "Bảng 2.10",
}


def replace_in_paragraph(paragraph):
    text = paragraph.text
    new_text = text
    for old, new in REN_NUMBER.items():
        new_text = new_text.replace(old, new)
    if new_text != text:
        paragraph.text = new_text


def main():
    doc = Document(DOCX)
    for paragraph in doc.paragraphs:
        replace_in_paragraph(paragraph)
    doc.save(DOCX)
    print(DOCX)


if __name__ == "__main__":
    main()
