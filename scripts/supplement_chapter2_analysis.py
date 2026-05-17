from __future__ import annotations

import shutil
from pathlib import Path

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from docx.text.paragraph import Paragraph


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "Bao_Cao" / "02_Chuong_2_ban_viet_lai_day_du_theo_mau.docx"
OUT = ROOT / "Bao_Cao" / "02_Chuong_2_ban_bo_sung_phan_tich.docx"


def paragraph_from_element(doc: Document, element) -> Paragraph:
    return Paragraph(element, doc)


def insert_after_element(parent, element, text: str) -> Paragraph:
    new_p = OxmlElement("w:p")
    element.addnext(new_p)
    paragraph = Paragraph(new_p, parent)
    paragraph.text = text
    return paragraph


def insert_after_paragraph(paragraph: Paragraph, text: str) -> Paragraph:
    new_para = insert_after_element(paragraph._parent, paragraph._p, text)
    new_para.style = paragraph.style
    return new_para


def find_paragraph(doc: Document, target: str) -> Paragraph:
    for paragraph in doc.paragraphs:
        if paragraph.text.strip() == target:
            return paragraph
    raise ValueError(f"Không tìm thấy đoạn: {target}")


def add_after_heading(doc: Document, target: str, additions: list[str]) -> None:
    paragraph = find_paragraph(doc, target)
    for text in reversed(additions):
        insert_after_paragraph(paragraph, text)


def add_after_next_table(doc: Document, caption: str, additions: list[str]) -> None:
    caption_paragraph = find_paragraph(doc, caption)
    current = caption_paragraph._p.getnext()
    while current is not None and not isinstance(current, CT_Tbl):
        current = current.getnext()
    if current is None:
        raise ValueError(f"Không tìm thấy bảng sau caption: {caption}")

    anchor = current
    for text in reversed(additions):
        insert_after_element(doc, anchor, text)


def insert_caption_before_next_table_and_explain(doc: Document, anchor_text: str, caption: str, explanation: str) -> None:
    anchor = find_paragraph(doc, anchor_text)
    current = anchor._p.getnext()
    while current is not None and not isinstance(current, CT_Tbl):
        current = current.getnext()
    if current is None:
        raise ValueError("Không tìm thấy bảng trạng thái sau mục 2.3.1")

    # Caption nằm ngay trước bảng, phần phân tích nằm sau bảng.
    caption_p = OxmlElement("w:p")
    current.addprevious(caption_p)
    caption_para = Paragraph(caption_p, doc)
    caption_para.text = caption
    insert_after_element(doc, current, explanation)


def main() -> None:
    shutil.copy2(SRC, OUT)
    doc = Document(OUT)

    heading_additions = {
        "2.1.5. Kênh giao tiếp giữa các thành phần": [
            (
                "Sau khi xác định các lớp kiến trúc, cần làm rõ cách các thành phần trao đổi dữ liệu với nhau. "
                "Trong hệ thống này, kênh giao tiếp không chỉ phục vụ truyền dữ liệu mà còn thể hiện ranh giới trách nhiệm "
                "giữa các dịch vụ. Thành phần giao diện chỉ giao tiếp với Main Service, còn RAG Service và các kho dữ liệu "
                "được đặt phía sau lớp điều phối."
            ),
            (
                "Bảng 2.1 tổng hợp các kênh giao tiếp chính, bao gồm hướng kết nối, giao thức sử dụng, cơ chế xác thực "
                "và vai trò của từng kênh. Việc tách rõ các kênh này giúp hệ thống dễ kiểm soát bảo mật hơn, đồng thời "
                "giúp quá trình triển khai và mở rộng từng dịch vụ độc lập hơn."
            ),
        ],
        "2.2.1. Tính chất môi trường của Agent": [
            (
                "Trước khi xây dựng luồng suy luận, cần xác định môi trường hoạt động của tác nhân AI. Đây là bước quan trọng "
                "vì cách tác nhân quan sát dữ liệu, lựa chọn hành động và phản hồi người dùng phụ thuộc trực tiếp vào đặc điểm "
                "của môi trường."
            ),
            (
                "Đối với bài toán tư vấn pháp luật, môi trường không hoàn toàn quan sát được. Tác nhân không đọc toàn bộ kho "
                "văn bản trong một lần, mà chỉ nhìn thấy câu hỏi, một phần lịch sử hội thoại và những nguồn được truy hồi trong "
                "từng lượt xử lý. Do đó, thiết kế Agent phải ưu tiên khả năng tra cứu bổ sung và kiểm chứng thay vì trả lời ngay."
            ),
        ],
        "2.2.2. Đặc tả vai trò và phạm vi Agent": [
            (
                "Sau khi xác định tính chất môi trường, cần giới hạn rõ vai trò của Agent. Trong đồ án này, Agent không đóng "
                "vai trò thay thế luật sư hoặc cơ quan có thẩm quyền, mà là trợ lý hỗ trợ tra cứu, diễn giải và chỉ ra căn cứ "
                "pháp lý liên quan đến câu hỏi của người dùng."
            ),
            (
                "Việc xác định phạm vi giúp hệ thống tránh hai rủi ro: trả lời vượt quá dữ liệu có căn cứ và đưa ra kết luận "
                "mang tính cam kết pháp lý. Vì vậy, các giới hạn trong Bảng 2.3 được dùng như nguyên tắc thiết kế cho toàn bộ "
                "pipeline trả lời."
            ),
        ],
        "2.2.3. Nguồn dữ liệu hỗ trợ Agent và hệ thống": [
            (
                "Nguồn dữ liệu quyết định trực tiếp khả năng trả lời của Agent. Với miền pháp luật, dữ liệu cần vừa có tính "
                "đầy đủ, vừa có khả năng truy ngược về văn bản gốc. Vì vậy, hệ thống không chỉ lưu nội dung điều luật mà còn "
                "lưu metadata, thông tin nguồn và vector phục vụ tìm kiếm ngữ nghĩa."
            ),
            (
                "Các nguồn trong Bảng 2.4 được phân chia theo vai trò: nguồn nội bộ dùng làm căn cứ chính, nguồn bên ngoài dùng "
                "để đối chiếu tính cập nhật, còn dữ liệu hội thoại hỗ trợ hiểu ngữ cảnh người dùng. Cách phân chia này giúp tránh "
                "nhầm lẫn giữa ngữ cảnh hội thoại và căn cứ pháp lý."
            ),
        ],
        "2.5.6. Ngưỡng tin cậy": [
            (
                "Bên cạnh việc xếp hạng kết quả, hệ thống cần xác định ngưỡng tin cậy để quyết định khi nào có thể sử dụng một "
                "đoạn văn bản làm căn cứ. Nếu ngưỡng quá thấp, câu trả lời dễ chứa nguồn không thật sự liên quan; nếu ngưỡng quá cao, "
                "hệ thống có thể bỏ sót căn cứ hữu ích."
            ),
            (
                "Các ngưỡng trong Bảng 2.12 được dùng để phân loại mức độ chắc chắn của kết quả truy hồi. Khi điểm tin cậy thấp, "
                "hệ thống có thể tiếp tục tìm kiếm, hỏi thêm ngữ cảnh hoặc trả lời thận trọng hơn thay vì khẳng định mạnh."
            ),
        ],
        "2.8.2. Các trạng thái trong luồng chat": [
            (
                "Trong luồng chat, trạng thái xử lý cần được truyền về giao diện theo cách có thể hiểu được đối với người dùng. "
                "Các trạng thái này không thay thế câu trả lời cuối cùng, nhưng giúp người dùng biết hệ thống đang kiểm tra câu hỏi, "
                "truy hồi nguồn hay kiểm chứng nội dung."
            ),
        ],
    }

    for target, additions in heading_additions.items():
        add_after_heading(doc, target, additions)

    insert_caption_before_next_table_and_explain(
        doc,
        "Trong một lượt hỏi đáp, hệ thống cần duy trì các thông tin trung gian như câu hỏi hiện tại, ngữ cảnh hội thoại, kết quả phân tích truy vấn, các nguồn đã truy hồi và trạng thái hợp lệ của câu hỏi. Những thông tin này giúp pipeline biết khi nào cần tìm thêm bằng chứng và khi nào có thể chuyển sang kiểm chứng.",
        "Bảng 2.5. Trạng thái trung gian trong luồng RAG có kiểm chứng",
        (
            "Bảng 2.5 cho thấy dữ liệu không đi qua pipeline dưới dạng một chuỗi văn bản đơn lẻ. Mỗi bước đều bổ sung hoặc "
            "cập nhật một phần trạng thái, từ đó bước sau có thể biết câu hỏi đã hợp lệ chưa, nguồn nào đã được truy hồi và "
            "câu trả lời dự thảo có đủ căn cứ để kiểm chứng hay không."
        ),
    )

    after_table_additions = {
        "Bảng 2.6. Dữ liệu đầu vào và đầu ra của bước kiểm soát đầu vào": [
            (
                "Các trường trong bảng làm rõ hai trường hợp xử lý: câu hỏi hợp lệ được chuyển tiếp xuống pipeline, còn câu hỏi "
                "không phù hợp được phản hồi ngay với lý do từ chối. Nhờ vậy, bước kiểm soát đầu vào không chỉ là bộ lọc kỹ thuật "
                "mà còn là cơ chế bảo vệ phạm vi tư vấn của hệ thống."
            ),
        ],
        "Bảng 2.7. Dữ liệu đầu vào và đầu ra của bước phân tích truy vấn": [
            (
                "Kết quả phân tích truy vấn đóng vai trò cầu nối giữa ngôn ngữ tự nhiên của người dùng và yêu cầu truy hồi trong "
                "kho dữ liệu. Nếu bước này hoạt động tốt, câu hỏi phía sau sẽ đúng trọng tâm pháp lý hơn so với việc dùng nguyên "
                "văn câu hỏi ban đầu."
            ),
        ],
        "Bảng 2.8. Dữ liệu đầu vào và đầu ra của bước suy luận": [
            (
                "Bảng 2.8 thể hiện điểm khác biệt giữa suy luận một lần và suy luận có vòng lặp. Đầu ra của bước suy luận có thể "
                "là yêu cầu tra cứu bổ sung hoặc câu trả lời dự thảo, cho phép hệ thống chủ động thu thập thêm nguồn khi bằng chứng "
                "hiện tại chưa đủ."
            ),
        ],
        "Bảng 2.9. Dữ liệu đầu vào và đầu ra của bước kiểm chứng": [
            (
                "Bảng 2.9 cho thấy bước kiểm chứng không tạo nguồn mới mà đối chiếu câu trả lời với các nguồn đã có. Nếu nội dung "
                "phù hợp với bằng chứng, câu trả lời được giữ nguyên; nếu không, hệ thống phải hiệu chỉnh để tránh đưa ra thông tin "
                "thiếu căn cứ."
            ),
        ],
        "Bảng 2.13. Các loại sự kiện trong luồng tư vấn có hướng dẫn": [
            (
                "Bảng 2.13 giúp chuẩn hóa cách frontend hiểu tiến trình xử lý của luồng tư vấn. Mỗi sự kiện không chỉ mang dữ liệu "
                "hiển thị mà còn thể hiện trạng thái nghiệp vụ: đang làm rõ, đang truy hồi, đang tổng hợp hoặc đã hoàn tất."
            ),
        ],
        "Bảng 2.14. Các event SSE của luồng chat": [
            (
                "Bảng 2.14 liệt kê các sự kiện chính được gửi trong quá trình streaming. Việc chuẩn hóa các sự kiện này giúp Mobile "
                "App cập nhật giao diện nhất quán, đồng thời tách rõ phần tiến trình xử lý và phần nội dung trả lời cuối cùng."
            ),
        ],
        "Bảng 2.15. Lý do lựa chọn Kotlin Multiplatform cho Mobile App": [
            (
                "Các tiêu chí trong bảng cho thấy Kotlin Multiplatform được lựa chọn không chỉ để giảm số lượng mã nguồn phải viết, "
                "mà còn để bảo đảm các luồng nghiệp vụ quan trọng như chat, tư vấn có hướng dẫn và xử lý trạng thái hoạt động thống "
                "nhất trên Android và iOS."
            ),
        ],
        "Bảng 2.16. Ánh xạ MVI vào các màn hình chính": [
            (
                "Bảng 2.16 ánh xạ mô hình MVI vào các màn hình chính của ứng dụng. Việc ánh xạ này giúp mỗi màn hình có cùng cách "
                "tổ chức: trạng thái được mô tả rõ, hành động người dùng được gom thành Intent và các phản hồi một lần được tách "
                "khỏi dữ liệu hiển thị lâu dài."
            ),
        ],
        "Bảng 2.17. Lợi ích của SSE trong trải nghiệm người dùng": [
            (
                "Các lợi ích trong bảng cho thấy SSE được dùng chủ yếu để cải thiện trải nghiệm trong các tác vụ có độ trễ cao. "
                "Người dùng không phải chờ một phản hồi duy nhất ở cuối pipeline mà có thể theo dõi tiến trình xử lý ngay khi hệ thống "
                "bắt đầu làm việc."
            ),
        ],
        "Bảng 2.18. So sánh vai trò Mobile App và Admin Web": [
            (
                "Bảng 2.18 nhấn mạnh sự khác nhau giữa hai giao diện. Mobile App tối ưu cho trải nghiệm hỏi đáp của người dùng cuối, "
                "trong khi Admin Web tối ưu cho vận hành dữ liệu. Sự tách biệt này giúp mỗi giao diện tập trung đúng nhu cầu sử dụng."
            ),
        ],
        "Bảng 2.19. Các trạng thái xử lý tài liệu": [
            (
                "Các trạng thái trong Bảng 2.19 giúp quản trị viên biết tác vụ đang ở bước nào và lỗi xảy ra tại đâu nếu quá trình "
                "cập nhật thất bại. Đây là yếu tố quan trọng vì cập nhật văn bản pháp luật là tác vụ dài, có nhiều bước phụ thuộc nhau."
            ),
        ],
    }

    for caption, additions in after_table_additions.items():
        add_after_next_table(doc, caption, additions)

    doc.save(OUT)
    print(OUT)


if __name__ == "__main__":
    main()
