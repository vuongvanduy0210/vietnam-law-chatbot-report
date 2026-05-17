from pathlib import Path

from docx import Document


DOCX = Path(__file__).resolve().parents[1] / "02_Chuong_2_ban_bo_sung_phan_tich_rag.docx"


def main():
    doc = Document(DOCX)

    # Bảng 2.14 trong file hiện tại là bảng thứ 14 theo thứ tự 0-based index 13.
    # Cột đầu tiên đang chứa tên event SSE, cần khớp với event name trong code.
    table = doc.tables[13]
    replacements = {
        "Sự kiện": "Event",
        "Cập nhật tiến trình": "progress",
        "Hoàn tất": "done",
    }

    for row in table.rows:
        cell = row.cells[0]
        value = cell.text.strip()
        if value in replacements:
            cell.text = replacements[value]

    doc.save(DOCX)
    print(DOCX)


if __name__ == "__main__":
    main()
