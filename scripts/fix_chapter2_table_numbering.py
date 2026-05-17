from pathlib import Path

from docx import Document


DOCX = Path(__file__).resolve().parents[1] / "02_Chuong_2_ban_bo_sung_phan_tich_rag.docx"

FIXES = [
    ("Các ngưỡng trong Bảng 2.10", "Các ngưỡng trong Bảng 2.11"),
    ("Bảng 2.10. Các ngưỡng tin cậy", "Bảng 2.11. Các ngưỡng tin cậy"),
    ("Bảng 2.10. Các loại sự kiện", "Bảng 2.12. Các loại sự kiện"),
    ("Bảng 2.10 giúp chuẩn hóa", "Bảng 2.12 giúp chuẩn hóa"),
    ("Bảng 2.10. Các event SSE", "Bảng 2.13. Các event SSE"),
    ("Bảng 2.10 liệt kê", "Bảng 2.13 liệt kê"),
    ("Bảng 2.10. Lý do lựa chọn", "Bảng 2.14. Lý do lựa chọn"),
    ("Bảng 2.10. Các trạng thái xử lý", "Bảng 2.15. Các trạng thái xử lý"),
    ("Các trạng thái trong Bảng 2.10", "Các trạng thái trong Bảng 2.15"),
]


def main():
    doc = Document(DOCX)
    for paragraph in doc.paragraphs:
        text = paragraph.text
        new_text = text
        for old, new in FIXES:
            new_text = new_text.replace(old, new)
        if new_text != text:
            paragraph.text = new_text
    doc.save(DOCX)
    print(DOCX)


if __name__ == "__main__":
    main()
