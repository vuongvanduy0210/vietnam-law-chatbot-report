from pathlib import Path

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.text.paragraph import Paragraph


DOCX = Path(__file__).resolve().parents[1] / "02_Chuong_2_ban_bo_sung_phan_tich_rag.docx"


REPLACEMENTS = {
    "Bảng 2.10.": [
        "Trong phần kiểm tra nguồn cập nhật bên ngoài, hệ thống không phụ thuộc vào một kênh tìm kiếm duy nhất. Các nguồn có khả năng cung cấp nội dung đầy đủ được ưu tiên khi cần đối chiếu văn bản pháp luật, trong khi nguồn có phạm vi bao phủ rộng được dùng để phát hiện tin tức pháp lý mới, văn bản thay thế hoặc thông tin hiệu lực được cập nhật gần đây. Cách kết hợp này giúp giảm rủi ro bỏ sót quy định mới nhưng vẫn giữ được khả năng đối chiếu với nội dung cụ thể.",
        "Về mặt xử lý, nguồn bên ngoài được sử dụng như lớp kiểm chứng bổ sung cho kho tri thức nội bộ. Khi câu hỏi liên quan đến mức phạt, thời hạn, hiệu lực hoặc văn bản có khả năng đã được thay thế, hệ thống cần ưu tiên tìm dấu hiệu cập nhật từ nguồn bên ngoài trước khi đưa ra kết luận. Nếu kết quả bên ngoài chỉ cung cấp đoạn trích ngắn, hệ thống không mở rộng nội dung ngoài phần có căn cứ; nếu tìm thấy văn bản đầy đủ hoặc nguồn chính thức, kết quả đó được dùng để đối chiếu với phần truy hồi nội bộ.",
        "Thiết kế này phù hợp với đặc thù dữ liệu pháp luật vì kho nội bộ mạnh ở khả năng lưu trữ có cấu trúc và truy hồi nguyên văn, còn nguồn cập nhật bên ngoài mạnh ở khả năng phản ánh thay đổi mới. Hai nhóm nguồn không thay thế nhau mà bổ sung cho nhau: kho nội bộ tạo nền tảng trích dẫn ổn định, còn nguồn bên ngoài giúp tránh trả lời dựa trên văn bản đã lỗi thời.",
    ],
    "Bảng 2.16.": [
        "Trong Mobile App, mô hình MVI được áp dụng nhất quán cho các màn hình chính nhưng không cần hiểu như một khuôn mẫu cứng. Ở màn hình đăng nhập, State chủ yếu gồm thông tin biểu mẫu, trạng thái đang gửi yêu cầu và lỗi xác thực; Intent tương ứng với các thao tác nhập liệu hoặc nhấn đăng nhập; Effect thường là điều hướng sang màn hình chính hoặc hiển thị thông báo. Với màn hình chat, State phức tạp hơn vì phải chứa danh sách tin nhắn, nội dung nhập, trạng thái streaming, các bước tiến trình và danh sách câu hỏi gợi ý.",
        "Ở các màn hình tra cứu văn bản pháp luật, State tập trung vào danh sách văn bản, bộ lọc, từ khóa tìm kiếm và kết quả tìm kiếm bằng AI. Khi người dùng đổi chủ đề, chọn năm ban hành hoặc mở chi tiết văn bản, các thao tác này được biểu diễn thành Intent để lớp xử lý trung gian gọi API và cập nhật State. Nhờ đó, phần giao diện chỉ cần hiển thị theo State hiện tại mà không phải tự quyết định cách truy vấn dữ liệu.",
        "Đối với luồng tư vấn có hướng dẫn, MVI đặc biệt hữu ích vì người dùng đi qua nhiều trạng thái liên tiếp: nhập câu hỏi ban đầu, nhận câu hỏi làm rõ, chọn phương án bổ sung thông tin và chờ câu trả lời cuối cùng. Việc gom các trạng thái này vào một mô hình dữ liệu thống nhất giúp giao diện xử lý được cả luồng bình thường lẫn lỗi mạng, lỗi xác thực hoặc trường hợp người dùng thay đổi lựa chọn giữa chừng.",
    ],
    "Bảng 2.17.": [
        "Việc sử dụng SSE trong trải nghiệm chat xuất phát từ đặc điểm của pipeline RAG có kiểm chứng. Người dùng không chỉ chờ một mô hình sinh câu trả lời, mà còn chờ các bước kiểm tra câu hỏi, phân tích truy vấn, truy hồi nguồn, tổng hợp và kiểm chứng. Nếu giao diện chỉ hiển thị một trạng thái chờ duy nhất, người dùng khó biết hệ thống còn hoạt động hay đã bị treo.",
        "SSE phù hợp với luồng chat vì đây là kênh truyền một chiều từ server về client. Trong quá trình xử lý, backend chỉ cần đẩy các sự kiện tiến trình và sự kiện hoàn tất; client không cần gửi dữ liệu liên tục ngược lại như các bài toán cộng tác thời gian thực. Cơ chế này đơn giản hơn WebSocket cho trường hợp hỏi đáp, đồng thời vẫn đủ để cập nhật Thinking Panel, trạng thái đang xử lý và câu trả lời cuối cùng.",
        "Ở góc độ trải nghiệm, streaming giúp người dùng thấy rằng hệ thống đang đi qua các bước có kiểm soát thay vì trả lời cảm tính. Các event tiến trình làm giảm cảm giác chờ, còn event hoàn tất bảo đảm câu trả lời chỉ xuất hiện khi đã được lưu và có nguồn tham chiếu. Điều này đặc biệt quan trọng với tư vấn pháp luật, nơi tốc độ cần đi kèm sự minh bạch về quá trình tra cứu.",
    ],
    "Bảng 2.18.": [
        "Mobile App và Admin Web được tách thành hai giao diện vì phục vụ hai nhóm người dùng khác nhau. Mobile App hướng tới người dùng cuối như người dân, sinh viên, doanh nghiệp hoặc cán bộ cần tra cứu nhanh. Trọng tâm của giao diện này là hội thoại với Agent, tư vấn có hướng dẫn, tra cứu thư viện văn bản và trải nghiệm nhận phản hồi theo thời gian thực.",
        "Admin Web lại phục vụ quản trị viên, nên trọng tâm không nằm ở hội thoại mà ở vận hành dữ liệu. Giao diện quản trị cần hỗ trợ tải lên văn bản mới, theo dõi tác vụ xử lý PDF, quan sát thống kê dữ liệu, kiểm tra trạng thái pipeline và xử lý các trường hợp cập nhật lỗi. Vì vậy, các thành phần như dashboard, bảng tác vụ, tiến trình WebSocket và thao tác quản lý văn bản được ưu tiên hơn các thành phần chat.",
        "Sự tách biệt này giúp mỗi frontend được tối ưu theo đúng ngữ cảnh sử dụng. Mobile App cần đơn giản, nhanh và tập trung vào trải nghiệm hỏi đáp; Admin Web cần nhiều thông tin vận hành hơn, cho phép quản trị viên theo dõi trạng thái dữ liệu và phát hiện lỗi trong quá trình cập nhật tri thức. Nhờ đó, hệ thống tránh việc dồn quá nhiều chức năng vào một giao diện duy nhất.",
    ],
}


REMOVE_AFTER_CAPTION_PREFIXES = {
    "Bảng 2.16.": ["Bảng 2.16 ánh xạ"],
    "Bảng 2.17.": ["Các lợi ích trong bảng"],
    "Bảng 2.18.": ["Bảng 2.18 nhấn mạnh"],
}


def paragraph_text(element) -> str:
    return "".join(t.text or "" for t in element.iter(qn("w:t"))).strip()


def insert_paragraph_before(doc: Document, element, text: str, style=None) -> Paragraph:
    new_p = OxmlElement("w:p")
    element.addprevious(new_p)
    paragraph = Paragraph(new_p, doc._body)
    if style:
        paragraph.style = style
    paragraph.text = text
    return paragraph


def remove_element(element):
    parent = element.getparent()
    parent.remove(element)


def find_caption_element(doc: Document, caption_prefix: str):
    for element in doc.element.body:
        if element.tag == qn("w:p") and paragraph_text(element).startswith(caption_prefix):
            return element
    raise ValueError(f"Không tìm thấy caption: {caption_prefix}")


def next_nonempty_body_element(body, start_index):
    idx = start_index + 1
    while idx < len(body):
        element = body[idx]
        if element.tag == qn("w:p") and not paragraph_text(element):
            idx += 1
            continue
        return idx, element
    return None, None


def main():
    doc = Document(DOCX)

    for caption_prefix, paragraphs in REPLACEMENTS.items():
        caption_el = find_caption_element(doc, caption_prefix)

        for text in paragraphs:
            insert_paragraph_before(doc, caption_el, text, style="Normal")

        body = doc.element.body
        caption_idx = list(body).index(caption_el)
        table_idx, table_el = next_nonempty_body_element(body, caption_idx)
        if table_el is None or table_el.tag != qn("w:tbl"):
            raise ValueError(f"Không tìm thấy table ngay sau {caption_prefix}")

        remove_element(table_el)
        remove_element(caption_el)

        # Remove direct post-table paragraphs that only refer to the deleted table.
        for prefix in REMOVE_AFTER_CAPTION_PREFIXES.get(caption_prefix, []):
            for element in list(doc.element.body):
                if element.tag == qn("w:p") and paragraph_text(element).startswith(prefix):
                    remove_element(element)
                    break

    doc.save(DOCX)
    print(DOCX)


if __name__ == "__main__":
    main()
