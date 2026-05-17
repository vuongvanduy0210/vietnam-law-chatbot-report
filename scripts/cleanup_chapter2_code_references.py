from __future__ import annotations

from pathlib import Path

from docx import Document


DOCX = Path("Bao_Cao/02_Chuong_2.docx")


def delete_paragraph(paragraph) -> None:
    element = paragraph._element
    parent = element.getparent()
    if parent is not None:
        parent.remove(element)


def main() -> None:
    doc = Document(DOCX)
    paragraphs = list(doc.paragraphs)

    replacements = {
        90: "2.3.3. Bước 1 — Guardrail (Kiểm soát đầu vào)",
        91: (
            "Guardrail là bước kiểm tra đầu tiên trong Hình 2.4. Mục đích của bước này là xác định câu hỏi "
            "có thuộc phạm vi tư vấn pháp luật hay không, đồng thời loại bỏ các yêu cầu lạc đề hoặc không phù hợp. "
            "Nếu câu hỏi không hợp lệ, hệ thống kết thúc sớm và trả lời từ chối lịch sự, không chạy các bước truy hồi phía sau."
        ),
        115: "2.3.4. Bước 2 — Query Analysis (Phân tích và tái cấu trúc truy vấn)",
        116: (
            "Sau khi qua Guardrail, câu hỏi được chuyển sang bước phân tích truy vấn. Ở bước này, hệ thống không chỉ giữ nguyên "
            "câu hỏi tự nhiên của người dùng, mà rút ra chủ đề pháp lý, lĩnh vực liên quan, các thuật ngữ trọng tâm và hướng tìm kiếm. "
            "Kết quả phân tích giúp bước truy hồi phía sau tìm đúng nhóm văn bản thay vì bị nhiễu bởi cách diễn đạt đời thường."
        ),
        137: (
            "Việc tách nhu cầu tìm kiếm thành hai hướng là một quyết định quan trọng. Với kho tri thức nội bộ, truy vấn cần ngắn gọn "
            "và tập trung vào thuật ngữ pháp lý cốt lõi để tối ưu tìm kiếm ngữ nghĩa. Với nguồn cập nhật bên ngoài, truy vấn cần chứa "
            "nhiều dấu hiệu về văn bản, năm ban hành hoặc quy định mới để tăng khả năng tìm đúng nguồn hiện hành."
        ),
        170: "2.3.6. Bước 4 — Verification (Kiểm chứng chống hallucination)",
        171: (
            "Trong Hình 2.4, bước kiểm chứng nằm ở cuối pipeline và đóng vai trò bảo vệ đầu ra. "
            "Sau khi Agent tạo câu trả lời dựa trên các nguồn đã thu thập, hệ thống rà soát lại xem các kết luận, số điều, mức phạt, "
            "thời hạn hoặc nguồn trích dẫn có xuất hiện trong bằng chứng hay không."
        ),
        172: (
            "Nếu câu trả lời đã có căn cứ, hệ thống giữ nguyên nội dung. Nếu phát hiện đoạn thiếu chứng cứ hoặc suy diễn quá mức, "
            "hệ thống loại bỏ hoặc điều chỉnh phần đó trước khi trả về người dùng. Cách tách bước sinh câu trả lời và bước kiểm chứng "
            "giúp giảm rủi ro hallucination trong miền pháp luật."
        ),
        197: "2.4. Nguồn tri thức của Agent",
        198: (
            "Trong graph ở mục 2.3, Agent chỉ có thể trả lời chính xác nếu có quyền truy cập vào nguồn tri thức đáng tin cậy. "
            "Vì vậy, hệ thống sử dụng hai nhóm nguồn chính: kho pháp luật nội bộ đã được chuẩn hóa và nguồn cập nhật bên ngoài "
            "để đối chiếu tính hiện hành."
        ),
        199: "2.4.1. Tra cứu cơ sở dữ liệu pháp luật nội bộ",
        200: (
            "Nguồn nội bộ cung cấp nguyên văn điều luật, metadata và thông tin đã được chuẩn hóa từ pipeline cập nhật văn bản. "
            "Đây là nguồn phù hợp để tạo câu trả lời có cấu trúc, có trích dẫn và có thể liên kết lại với văn bản gốc."
        ),
        214: "2.4.2. Tìm kiếm nguồn cập nhật bên ngoài",
        294: "Luồng xử lý guided answer gồm ba ý chính:",
        295: (
            "Thứ nhất, hệ thống kết hợp câu hỏi ban đầu với các câu trả lời làm rõ để tạo truy vấn đầy đủ hơn. "
            "Thứ hai, pipeline truy hồi và suy luận được chạy trên ngữ cảnh đã rõ ràng. Thứ ba, câu trả lời vẫn đi qua bước kiểm chứng "
            "trước khi trả về người dùng, giống nguyên tắc chất lượng của luồng chat tự do."
        ),
        360: "2.7.4. Cơ chế hoàn tác để giữ dữ liệu nhất quán",
        361: (
            "Như Hình 2.9 đã thể hiện, sau khi trích xuất xong, hệ thống cần đồng bộ dữ liệu sang nhiều nơi: kho lưu tri thức gốc, "
            "kho vector phục vụ truy hồi và trạng thái task để admin theo dõi. Vấn đề đặt ra là các kho này không tự động nằm trong "
            "một giao dịch duy nhất."
        ),
        364: (
            "Nếu một bước đã ghi dữ liệu thành công nhưng bước sau thất bại, hệ thống có thể rơi vào trạng thái lệch: admin thấy văn bản "
            "đã tồn tại nhưng Agent không tìm được qua vector, hoặc ngược lại. Vì vậy, pipeline cần cơ chế hoàn tác để xóa phần dữ liệu "
            "đã ghi dở và đưa hệ thống về trạng thái an toàn."
        ),
        365: (
            "Cách hiểu đơn giản là: một văn bản chỉ được coi là cập nhật thành công khi toàn bộ các kho liên quan đều đồng bộ. "
            "Nếu không đạt điều kiện này, task chuyển sang thất bại và dữ liệu ghi một phần sẽ được thu hồi."
        ),
        422: (
            "Một vấn đề phổ biến của chatbot dùng LLMs là thời gian chờ lâu. Với Agentic RAG, hệ thống còn phải kiểm tra câu hỏi, "
            "phân tích truy vấn, truy hồi nguồn, đối chiếu thông tin và kiểm chứng câu trả lời. Nếu giao diện chỉ hiển thị một spinner tĩnh, "
            "người dùng khó biết hệ thống còn đang xử lý hay đã gặp lỗi."
        ),
        423: "Đồ án giải quyết bằng streaming kết hợp vùng hiển thị tiến trình:",
        424: "1. Khi người dùng gửi câu hỏi, hệ thống ghi nhận hội thoại và phản hồi trạng thái đã tiếp nhận.",
        425: "2. Trong quá trình xử lý, backend gửi các bước tiến trình dễ hiểu như kiểm tra câu hỏi, tra cứu nguồn và kiểm chứng.",
        427: "4. Khi pipeline hoàn tất, câu trả lời cuối cùng được lưu lại cùng nguồn tham chiếu.",
        444: "1. Admin upload PDF từ màn hình quản trị.",
        445: "2. Backend tạo task xử lý để theo dõi tiến trình.",
        446: "3. Frontend mở kết nối realtime để nhận cập nhật trạng thái.",
        447: "4. Pipeline xử lý tài liệu cập nhật tiến trình theo từng bước.",
        448: "5. Backend gửi event cho đúng người quản trị đang sở hữu task.",
    }

    delete_indices = {
        *range(92, 113),
        *range(117, 137),
        *range(138, 150),
        *range(173, 195),
        *range(201, 209),
        212,
        *range(296, 300),
        *range(366, 376),
        426,
        428,
        449,
    }

    for idx, text in replacements.items():
        paragraphs[idx].text = text

    for idx in sorted(delete_indices, reverse=True):
        delete_paragraph(paragraphs[idx])

    doc.save(DOCX)


if __name__ == "__main__":
    main()
